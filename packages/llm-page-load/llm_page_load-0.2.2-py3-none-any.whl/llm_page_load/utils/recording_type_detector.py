"""
录制类型检测模块
用于判断视频是内录（手机屏幕录制）还是外录（外部拍摄）
"""

import json
import os
import re
import time
from typing import Dict, Any
import numpy as np
from PIL import Image

from .llm_narrow_core import load_frame, check_and_resize_saved_image, llm_vision_request_with_retry


def detect_recording_type(segment_dir, llm_client, model="anthropic.claude-3.7-sonnet", frame_dir=None):
    """
    判断录制类型：内录（手机屏幕录制）还是外录（外部拍摄）
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        model: 使用的模型名称
        frame_dir: 帧图片目录路径（可选）
    
    Returns:
        dict: 包含录制类型判断结果的字典
        {
            "recording_type": "internal" | "external",
            "confidence": float,
            "reason": str,
            "frame_path": str
        }
    """
    print("=== 开始判断录制类型 ===")
    
    # 读取action_info.json获取帧数信息
    action_info_path = os.path.join(segment_dir, "action_info.json")
    try:
        with open(action_info_path, "r", encoding="utf-8") as f:
            action_info = json.load(f)
        num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
        action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    except Exception as e:
        print(f"读取action_info.json失败: {e}")
        return {"recording_type": "unknown", "confidence": 0.0, "reason": f"读取配置文件失败: {e}"}
    
    # 选择中间帧进行分析（避免开头和结尾的特殊状态）
    middle_frame_idx = num_frames // 2
    print(f"选择中间帧 {middle_frame_idx} 进行录制类型判断")
    
    # 加载中间帧
    middle_frame = load_frame(segment_dir, middle_frame_idx, frame_dir=frame_dir)
    if middle_frame is None:
        print(f"无法加载中间帧 {middle_frame_idx}")
        return {"recording_type": "unknown", "confidence": 0.0, "reason": "无法加载分析帧"}
    
    # 保存帧为临时图片，先进行预缩放以避免API限制
    temp_dir = os.path.join(segment_dir, "temp_recording_type_check")
    os.makedirs(temp_dir, exist_ok=True)
    frame_path = os.path.join(temp_dir, f"recording_type_check_frame_{middle_frame_idx}.png")
    
    # 预缩放图片以避免API限制
    original_size = middle_frame.size
    max_dimension = 1200  # 限制最大尺寸为1200像素
    
    if original_size[0] > max_dimension or original_size[1] > max_dimension:
        # 计算缩放比例
        scale = min(max_dimension / original_size[0], max_dimension / original_size[1])
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        print(f"预缩放图片: {original_size} -> {new_size} (缩放比例: {scale:.2f})")
        middle_frame = middle_frame.resize(new_size, Image.Resampling.LANCZOS)
    
    middle_frame.save(frame_path)
    
    # 检测和调整保存后的文件大小，使用更小的目标大小避免API限制
    frame_path = check_and_resize_saved_image(frame_path, max_file_size_mb=1.5, min_file_size_mb=0.5)
    
    # 构建录制类型判断的prompt
    recording_type_prompt = (
        f"Please analyze this image to determine if it's from an internal screen recording or external camera recording.\n\n"
        f"## Action Description: {action_desc}\n"
        f"## Frame Number: {middle_frame_idx}\n\n"
        f"## Recording Type Analysis:\n"
        f"Please examine the image carefully and determine if this is:\n"
        f"1. INTERNAL RECORDING (screen recording from phone/device):\n"
        f"   - Clean, crisp screen content\n"
        f"   - Perfect rectangular screen boundaries\n"
        f"   - No camera artifacts (blur, shadows, reflections)\n"
        f"   - No external environment visible\n"
        f"   - No camera UI elements (focus boxes, etc.)\n"
        f"   - Consistent lighting and colors\n"
        f"   - Sharp text and UI elements\n\n"
        f"2. EXTERNAL RECORDING (camera filming a screen):\n"
        f"   - Camera artifacts (blur, shadows, reflections)\n"
        f"   - Visible external environment (desk, hands, etc.)\n"
        f"   - Uneven lighting or shadows\n"
        f"   - Camera UI elements visible\n"
        f"   - Screen edges may be curved or distorted\n"
        f"   - Possible glare or reflections on screen\n"
        f"   - Lower quality or less sharp content\n\n"
        f"## Please answer in JSON format:\n"
        f"{{\n"
        f"    \"recording_type\": \"internal\" or \"external\",\n"
        f"    \"confidence\": 0.0-1.0,\n"
        f"    \"reason\": \"Detailed explanation of your judgment\",\n"
        f"    \"key_features\": [\"List of key visual features that led to your decision\"]\n"
        f"}}"
    )
    
    try:
        messages = [{"role": "user", "content": recording_type_prompt, "image_url": [frame_path]}]
        response = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
        
        # 解析LLM响应
        try:
            # 尝试直接解析JSON
            response_json = json.loads(response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试从markdown代码块中提取
            pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
            match = re.search(pattern, response)
            if match:
                response_json = json.loads(match.group(1))
            else:
                print("无法解析LLM响应，假设为内录")
                response_json = {"recording_type": "internal", "confidence": 0.5, "reason": "无法解析LLM响应"}
        
        recording_type = response_json.get("recording_type", "unknown")
        confidence = response_json.get("confidence", 0.0)
        reason = response_json.get("reason", "无判断理由")
        key_features = response_json.get("key_features", [])
        
        print(f"录制类型判断结果: {recording_type}")
        print(f"置信度: {confidence:.2f}")
        print(f"判断理由: {reason}")
        if key_features:
            print(f"关键特征: {', '.join(key_features)}")
        
        # 清理临时文件
        try:
            os.remove(frame_path)
            os.rmdir(temp_dir)
        except: pass
        
        return {
            "recording_type": recording_type,
            "confidence": confidence,
            "reason": reason,
            "key_features": key_features,
            "frame_path": frame_path,
            "analyzed_frame": middle_frame_idx
        }
        
    except Exception as e:
        print(f"录制类型判断过程中出错: {e}")
        # 清理临时文件
        try:
            os.remove(frame_path)
            os.rmdir(temp_dir)
        except: pass
        
        return {"recording_type": "unknown", "confidence": 0.0, "reason": f"判断过程出错: {e}"}


def should_enable_background_removal(recording_type_result, remove_background_param=False):
    """
    根据录制类型判断是否应该启用背景移除
    
    Args:
        recording_type_result: 录制类型检测结果
        remove_background_param: 用户传入的remove_background参数
    
    Returns:
        bool: 是否应该启用背景移除
    """
    recording_type = recording_type_result.get("recording_type", "unknown")
    confidence = recording_type_result.get("confidence", 0.0)
    
    # 如果用户明确指定了remove_background参数，优先使用用户设置
    if remove_background_param:
        if recording_type == "external" and confidence >= 0.6:
            print(f"检测到外录（置信度: {confidence:.2f}），启用背景移除功能")
            return True
        elif recording_type == "internal" and confidence >= 0.6:
            print(f"检测到内录（置信度: {confidence:.2f}），禁用背景移除功能")
            return False
        else:
            print(f"录制类型不确定（{recording_type}, 置信度: {confidence:.2f}），使用用户设置: {remove_background_param}")
            return remove_background_param
    else:
        # 如果用户没有指定，根据录制类型自动判断
        if recording_type == "external" and confidence >= 0.6:
            print(f"检测到外录（置信度: {confidence:.2f}），自动启用背景移除功能")
            return True
        elif recording_type == "internal" and confidence >= 0.6:
            print(f"检测到内录（置信度: {confidence:.2f}），自动禁用背景移除功能")
            return False
        else:
            print(f"录制类型不确定（{recording_type}, 置信度: {confidence:.2f}），默认禁用背景移除功能")
            return False 