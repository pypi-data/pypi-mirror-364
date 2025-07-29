#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超高效的OCR开始帧检测测试
"""

import os
import sys
import re
import cv2
import numpy as np
import time
import gc
import json
import threading
import datetime
import uuid
import requests
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
# from paddleocr import PaddleOCR  # 注释掉本地PaddleOCR

# 修复tqdm的AttributeError问题
import warnings
warnings.filterwarnings("ignore", message=".*'tqdm' object has no attribute 'pos'.*")

# 添加ground truth计算相关的辅助函数
def parse_case_key_for_gt(case_key: str) -> tuple:
    """
    解析case_key，提取视频名和时间信息
    格式: "2025-07-03_1751514078822,VID_20250703_113456/1_15s"
    """
    try:
        # 分割视频名和时间
        video_part, time_part = case_key.split('/')
        
        # 解析时间部分 "1_37s" -> 1.37
        time_str = time_part.replace('s', '')
        if '_' in time_str:
            # 处理 "1_37s" 格式，转换为 1.37
            action_time_str, decimal_str = time_str.split('_')
            action_time = float(action_time_str) + float(decimal_str) / 100.0
        else:
            action_time = float(time_str)
            
        return video_part, action_time
    except Exception as e:
        print(f"解析case_key失败: {case_key}, 错误: {e}")
        return None, None

def find_action_info_file_for_gt(video_name: str, action_time: float, processed_dir: str) -> str:
    """
    在processed目录中查找对应的action_info.json文件
    支持两种数据格式：
    1. downloaded_videos_processed (新格式)
    2. all_marked_data_processed_action_items (旧格式)
    """
    # 时间字符串生成方式修正，避免四舍五入
    def get_time_str(action_time):
        int_part = int(action_time)
        decimal_part = int(round((action_time - int_part) * 100))
        return f"{int_part}_{decimal_part}s"

    # 首先在downloaded_videos_processed中查找
    if os.path.exists(processed_dir):
        # 查找匹配的视频目录
        for item in os.listdir(processed_dir):
            item_path = os.path.join(processed_dir, item)
            if not os.path.isdir(item_path):
                continue
                
            # 检查是否是目标视频（精确匹配）
            if video_name == item:
                # 查找对应时间点的action_info.json
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if not os.path.isdir(subitem_path):
                        continue
                        
                    # 检查时间是否匹配
                    time_str = get_time_str(action_time)
                    if time_str in subitem:
                        action_info_path = os.path.join(subitem_path, "action_info.json")
                        if os.path.exists(action_info_path):
                            return action_info_path
    
    # 如果没找到，在all_marked_data_processed_action_items中查找
    old_format_dir = "all_marked_data_processed_action_items"
    if os.path.exists(old_format_dir):
        # 查找匹配的视频目录
        for item in os.listdir(old_format_dir):
            item_path = os.path.join(old_format_dir, item)
            if not os.path.isdir(item_path):
                continue
                
            # 检查是否是目标视频（精确匹配）
            if video_name == item:
                # 查找对应时间点的action_info.json
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if not os.path.isdir(subitem_path):
                        continue
                        
                    # 检查时间是否匹配
                    time_str = get_time_str(action_time)
                    if time_str in subitem:
                        action_info_path = os.path.join(subitem_path, "action_info.json")
                        if os.path.exists(action_info_path):
                            return action_info_path
    
    return None

def calculate_ground_truth_start_frame_for_gt(action_info_path: str) -> int:
    """
    从action_info.json计算开始帧的ground truth帧索引
    对于开始帧检测，我们需要找到动作开始的时间点
    """
    try:
        with open(action_info_path, 'r', encoding='utf-8') as f:
            action_info = json.load(f)
        
        # 提取关键信息
        original_action = action_info.get('original_action_item', {})
        extraction_params = action_info.get('extraction_parameters', {})
        
        # 尝试多种时间字段，优先级：action_time > marked_start_time > marked_response_time
        action_time = original_action.get('action_time')
        marked_start_time = original_action.get('marked_start_time')
        marked_response_time = original_action.get('marked_response_time')
        
        extract_start_time_sec = extraction_params.get('extract_start_time_sec')
        fps = extraction_params.get('fps', 30)
        
        # 选择合适的时间作为开始时间
        start_time = None
        if action_time is not None:
            start_time = action_time
        elif marked_start_time is not None:
            start_time = marked_start_time
        elif marked_response_time is not None:
            start_time = marked_response_time
        
        if start_time is None or extract_start_time_sec is None:
            print(f"缺少必要的时间信息: action_time={action_time}, marked_start_time={marked_start_time}, marked_response_time={marked_response_time}, extract_start_time_sec={extract_start_time_sec}")
            return None
        
        # 计算开始帧的ground truth帧索引
        gt_start_frame = int(round((start_time - extract_start_time_sec) * fps))
        
        # 确保帧索引不为负数
        if gt_start_frame < 0:
            print(f"警告: 计算的帧索引为负数 ({gt_start_frame})，设置为0")
            gt_start_frame = 0
        
        return gt_start_frame
        
    except Exception as e:
        print(f"计算开始帧ground truth失败: {e}")
        return None

# 线程安全的计数器
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    def get_value(self):
        with self._lock:
            return self._value
    
    def set_value(self, value):
        with self._lock:
            self._value = value

# 实时结果保存器
class RealTimeResultSaver:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.results_file = os.path.join(output_dir, "results.json")
        self.log_file = os.path.join(output_dir, "real_time_log.txt")
        self.results_buffer = []  # 结果缓冲区
        self.buffer_size = 10     # 缓冲区大小
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化结果文件
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump({"results": [], "summary": {}}, f, indent=2, ensure_ascii=False)
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"=== 实时日志 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    def save_result(self, result):
        """保存单个结果"""
        # 添加新结果到缓冲区（不包含frame_texts，避免文件过大）
        result_copy = result.copy()
        if "frame_texts" in result_copy:
            del result_copy["frame_texts"]  # 从主结果中移除详细文本
        
        self.results_buffer.append(result_copy)
        
        # 当缓冲区满时，批量写入文件
        if len(self.results_buffer) >= self.buffer_size:
            self._flush_results_buffer()
        
        # 单独保存帧文本信息到测例目录
        if "frame_texts" in result and result["frame_texts"]:
            self.save_frame_texts_to_case_dir(result["case_key"], result["frame_texts"])
    
    def _flush_results_buffer(self):
        """刷新结果缓冲区到文件"""
        if not self.results_buffer:
            return
            
        # 读取现有结果
        with open(self.results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 添加缓冲区中的结果
        data["results"].extend(self.results_buffer)
        
        # 写回文件
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 清空缓冲区
        self.results_buffer.clear()
    
    def save_frame_texts_to_case_dir(self, case_key, frame_texts):
        """保存单个case的帧文本信息到测例目录"""
        # 创建测例目录
        case_dir = os.path.join(self.output_dir, "case_details", case_key.replace("/", "_"))
        os.makedirs(case_dir, exist_ok=True)
        
        # 保存帧文本文件
        frame_texts_file = os.path.join(case_dir, "frame_texts.json")
        case_summary = {
            "case_key": case_key,
            "total_frames": len(frame_texts),
            "frames_with_coordinates": sum(1 for f in frame_texts if f.get("has_coordinates", False)),
            "frames_with_errors": sum(1 for f in frame_texts if "error" in f),
            "processing_timestamp": datetime.datetime.now().isoformat(),
            "frame_details": frame_texts
        }
        
        with open(frame_texts_file, "w", encoding="utf-8") as f:
            json.dump(case_summary, f, indent=2, ensure_ascii=False)
        
        # 创建简化的统计文件
        stats_file = os.path.join(case_dir, "stats.txt")
        with open(stats_file, "w", encoding="utf-8") as f:
            f.write(f"=== {case_key} 统计信息 ===\n")
            f.write(f"总帧数: {len(frame_texts)}\n")
            f.write(f"包含坐标的帧数: {case_summary['frames_with_coordinates']}\n")
            f.write(f"有错误的帧数: {case_summary['frames_with_errors']}\n")
            f.write(f"坐标检测成功率: {case_summary['frames_with_coordinates']/len(frame_texts)*100:.1f}%\n")
            f.write(f"处理时间: {case_summary['processing_timestamp']}\n")
            
            # 显示前几帧的文本示例
            f.write(f"\n=== 前5帧文本示例 ===\n")
            for i, frame_text in enumerate(frame_texts[:5]):
                f.write(f"帧 {frame_text['frame_number']} (时间戳: {frame_text['timestamp']:.2f}s):\n")
                f.write(f"  OCR文本: {frame_text['ocr_texts']}\n")
                f.write(f"  有坐标: {frame_text['has_coordinates']}\n")
                if frame_text['coordinate_texts']:
                    f.write(f"  坐标文本: {frame_text['coordinate_texts']}\n")
                if 'error' in frame_text:
                    f.write(f"  错误: {frame_text['error']}\n")
                f.write("\n")
    
    def update_summary(self, summary):
        """更新统计摘要"""
        # 先刷新缓冲区
        self._flush_results_buffer()
        
        with open(self.results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data["summary"] = summary
        
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def save_config(self, config):
        """保存配置"""
        config_file = os.path.join(self.output_dir, "config.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def finalize(self):
        """完成时刷新所有缓冲区"""
        self._flush_results_buffer()

def create_experiment_output_dir():
    """创建实验输出目录"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"experiment_ocr_start_frame_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def check_words(text):
    """使用用户提供的正则表达式检查坐标信息（开始帧检测，严格版本）"""
    # 严格版本：必须是X:或Y:，且后面跟非零数字
    pattern = re.compile(r'(?i)\b[XY]:\s*-?(?!0\.?0*$)\d+\.?\d*\b')
    
    # 使用search而不是fullmatch，因为文本可能包含多个坐标
    match = pattern.search(text)
    return match is not None

# 添加HTTP OCR服务调用函数
def call_ocr_service(image, url="http://10.164.6.121:8417/paddelocr"):
    """
    调用HTTP OCR服务
    
    Args:
        image: OpenCV图像数组
        url: OCR服务URL
        
    Returns:
        list: 识别的文本列表
    """
    try:
        # 将OpenCV的BGR格式转换为RGB格式
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 编码为JPEG格式
        _, buffer = cv2.imencode('.jpg', image_rgb)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 准备请求数据
        data = {'image': img_base64}
        
        # 发送请求
        response = requests.post(url, data=data, timeout=30)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # 提取文本
                texts = []
                for item in result.get('results', []):
                    text = item.get('text', '')
                    if text.strip():  # 只添加非空文本
                        texts.append(text)
                return texts
            else:
                print(f"OCR服务返回错误: {result.get('error')}")
                return []
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"调用OCR服务出错: {e}")
        return []

def llm_narrow_start_frame_ocr_ultra_fast(
    video_path: str, 
    llm_client=None,  # 添加LLM客户端参数
    do_evaluation: bool = False,
    max_frames: int = None,
    skip_frames: int = 1,  # 更激进的跳帧
    scale_factor: float = 0.25,  # 更小的缩放
    early_stop: bool = True,  # 找到第一个坐标就停止
    save_frame_texts: bool = True,  # 是否保存每帧文本
    ui_infer_config: dict = None  # UI infer配置参数
):
    """
    超高效的OCR开始帧检测方法
    使用激进的内存优化策略
    支持设备类型检测：安卓设备使用OCR方案，其他设备使用UI infer方案
    
    Args:
        video_path: 视频文件路径
        llm_client: LLM客户端实例（用于UI infer方案）
        do_evaluation: 是否进行评估输出
        max_frames: 最大处理帧数，None表示处理所有帧
        skip_frames: 跳帧数，3表示每3帧处理1帧
        scale_factor: 图片缩放因子，0.25表示缩小到原来的1/4
        early_stop: 是否找到第一个坐标就停止
        save_frame_texts: 是否保存每帧提取的文本
        ui_infer_config: UI infer配置参数
    
    Returns:
        dict: 包含检测结果的字典
    """
    
    # 导入设备类型检测函数
    from .llm_narrow_core import detect_android_by_first_frame, llm_narrow_start_frame_with_ui_infer
    
    print(f"=== 开始帧检测: {os.path.basename(video_path)} ===")
    
    # 1. 首先检测设备类型
    print("正在检测设备类型...")
    is_android = detect_android_by_first_frame(video_path)
    
    if is_android:
        print("检测到安卓设备，使用OCR方案")
        return _llm_narrow_start_frame_ocr_ultra_fast_android(
            video_path, do_evaluation, max_frames, skip_frames, 
            scale_factor, early_stop, save_frame_texts
        )
    else:
        print("检测到非安卓设备，使用UI Infer方案")
        if llm_client is None:
            return {
                'success': False,
                'error': '非安卓设备需要LLM客户端，但未提供',
                'start_frame': None,
                'candidates': []
            }
        
        # 使用UI infer方案
        ui_config = ui_infer_config or {}
        return llm_narrow_start_frame_with_ui_infer(
            video_path=video_path,
            llm_client=llm_client,
            do_evaluation=do_evaluation,
            activity_threshold=ui_config.get('activity_threshold', -0.001),
            merge_window=ui_config.get('merge_window', 3),
            start_threshold=ui_config.get('start_threshold', -0.0001),
            end_threshold=ui_config.get('end_threshold', -0.00003),
            ssim_threshold=ui_config.get('ssim_threshold', 0.995),
            model=ui_config.get('model', "anthropic.claude-3.7-sonnet"),
            max_voting_rounds=ui_config.get('max_voting_rounds', 10),
            temperature=ui_config.get('temperature', 0.1),
            remove_background=ui_config.get('remove_background', False),
            enable_diff=ui_config.get('enable_diff', False),
            ui_infer_max_retries=ui_config.get('ui_infer_max_retries', 3),
            ui_infer_retry_delay=ui_config.get('ui_infer_retry_delay', 2)
        )


def _llm_narrow_start_frame_ocr_ultra_fast_android(
    video_path: str, 
    do_evaluation: bool = False,
    max_frames: int = None,
    skip_frames: int = 1,  # 更激进的跳帧
    scale_factor: float = 0.25,  # 更小的缩放
    early_stop: bool = True,  # 找到第一个坐标就停止
    save_frame_texts: bool = True  # 是否保存每帧文本
):
    """
    安卓设备的OCR开始帧检测方法（原有逻辑）
    """
    
    # 初始化PaddleOCR，使用更轻量的配置
    # ocr = PaddleOCR( # 注释掉本地PaddleOCR
    #     use_doc_orientation_classify=False, 
    #     use_doc_unwarping=False, 
    #     use_textline_orientation=False
    # )
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'success': False,
            'error': f'无法打开视频文件: {video_path}',
            'start_frame': None,
            'candidates': [],
            'frame_texts': []
        }
    
    # 获取视频信息
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if do_evaluation:
        print(f"视频信息:")
        print(f"  总帧数: {total_frames}")
        print(f"  FPS: {fps:.2f}")
        print(f"  分辨率: {width}x{height}")
        print(f"  跳帧数: {skip_frames}")
        print(f"  缩放因子: {scale_factor}")
        print(f"  早期停止: {early_stop}")
        if max_frames:
            print(f"  最大处理帧数: {max_frames}")
    
    candidates = []
    frame_count = 0
    processed_frames = 0
    start_time = time.time()
    
    # 记录每帧提取的文本
    frame_texts = []
    
    # 直接在内存中处理帧，不保存临时文件
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 检查是否达到最大帧数限制
        if max_frames and processed_frames >= max_frames:
            break
        
        # 跳帧处理
        if frame_count % skip_frames != 0:
            frame_count += 1
            continue
        
        processed_frames += 1
        
        if do_evaluation and processed_frames % 5 == 0:
            elapsed_time = time.time() - start_time
            fps_processed = processed_frames / elapsed_time if elapsed_time > 0 else 0
            print(f"处理帧 {processed_frames}: 帧号 {frame_count}, 处理速度: {fps_processed:.1f} fps")
        
        try:
            # 图片缩放以减少内存使用和提高处理速度
            if scale_factor != 1.0:
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # 将OpenCV的BGR格式转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if do_evaluation:
                print(f"  帧 {frame_count} - 开始OCR识别...")
                print(f"  图片尺寸: {frame_rgb.shape}")
                print(f"  图片数据类型: {frame_rgb.dtype}")
            
            # 调用HTTP OCR服务
            try:
                rec_texts = call_ocr_service(frame, url="http://10.164.6.121:8417/paddelocr")
                if do_evaluation:
                    print(f"  帧 {frame_count} - OCR识别完成")
                    print(f"  提取的文本: {rec_texts}")
            except Exception as ocr_error:
                if do_evaluation:
                    print(f"  帧 {frame_count} - OCR识别失败: {ocr_error}")
                    print(f"  OCR错误类型: {type(ocr_error).__name__}")
                    import traceback
                    traceback.print_exc()
                raise ocr_error
            
            # 记录每帧的文本信息
            frame_text_info = {
                'frame_number': frame_count,
                'frame_index': processed_frames - 1,
                'timestamp': frame_count / fps if fps > 0 else 0,
                'ocr_texts': rec_texts,
                'has_coordinates': False,
                'coordinate_texts': []
            }
            
            # 判断是否存在点击坐标
            has_coordinates = False
            coordinate_texts = []
            for text in rec_texts:
                if check_words(text):
                    has_coordinates = True
                    coordinate_texts.append(text)
                    break
            
            frame_text_info['has_coordinates'] = has_coordinates
            frame_text_info['coordinate_texts'] = coordinate_texts
            
            # 保存帧文本信息
            if save_frame_texts:
                frame_texts.append(frame_text_info)
            
            if has_coordinates:
                candidates.append({
                    'frame_number': frame_count,
                    'frame_index': processed_frames - 1,
                    'timestamp': frame_count / fps if fps > 0 else 0,
                    'ocr_texts': rec_texts,
                    'coordinate_texts': coordinate_texts
                })
                
                if do_evaluation:
                    print(f"  检测到坐标信息: {coordinate_texts}")
                    print(f"  所有OCR文本: {rec_texts}")
                    print(f"  时间戳: {frame_count / fps:.2f}s")
                
                # 早期停止：找到第一个坐标就停止
                if early_stop:
                    break
        
        except Exception as e:
            if do_evaluation:
                import traceback
                print(f"  处理帧 {frame_count} 时出错: {e}")
                print(f"  错误类型: {type(e).__name__}")
                print(f"  错误详情:")
                traceback.print_exc()
            
            # 记录错误帧信息
            if save_frame_texts:
                frame_texts.append({
                    'frame_number': frame_count,
                    'frame_index': processed_frames - 1,
                    'timestamp': frame_count / fps if fps > 0 else 0,
                    'ocr_texts': [],
                    'has_coordinates': False,
                    'coordinate_texts': [],
                    'error': str(e)
                })
        
        # 强制垃圾回收，释放内存
        if processed_frames % 10 == 0:
            gc.collect()
        
        frame_count += 1
    
    # 释放视频资源
    cap.release()
    
    # 选择第一个检测到坐标的帧作为开始帧
    start_frame = candidates[0] if candidates else None
    
    total_time = time.time() - start_time
    
    result = {
        'success': True,
        'start_frame': start_frame,
        'candidates': candidates,
        'total_frames': total_frames,
        'processed_frames': processed_frames,
        'processing_time': total_time,
        'fps_processed': processed_frames / total_time if total_time > 0 else 0,
        'video_info': {
            'fps': fps,
            'width': width,
            'height': height,
            'duration': total_frames / fps if fps > 0 else 0
        },
        'frame_texts': frame_texts if save_frame_texts else [],
        'method_used': 'ocr_ultra_fast_android'
    }
    
    # 评估模式输出
    if do_evaluation:
        print(f"\n=== 检测结果 ===")
        print(f"视频总帧数: {total_frames}")
        print(f"实际处理帧数: {processed_frames}")
        print(f"处理总时间: {total_time:.2f} 秒")
        print(f"处理速度: {processed_frames / total_time:.1f} fps")
        print(f"检测到坐标的帧数: {len(candidates)}")
        print(f"记录帧文本数: {len(frame_texts)}")
        
        if start_frame:
            print(f"\n开始帧:")
            print(f"  帧号: {start_frame['frame_number']}")
            print(f"  时间戳: {start_frame['timestamp']:.2f}s")
            print(f"  坐标文本: {start_frame['coordinate_texts']}")
            print(f"  所有OCR文本: {start_frame['ocr_texts']}")
        else:
            print("未检测到包含坐标信息的帧")
    
    return result

def find_video_files(base_dir: str):
    """查找目录中的视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    video_files = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))
    
    return video_files

def scan_and_select_cases_from_directory(dataset_root_path):
    """
    扫描dataset_root_path目录，让用户选择要运行的case
    
    Args:
        dataset_root_path: 数据集根目录路径
        
    Returns:
        list: 选中的测试用例列表，格式为 ["case_name/segment_name", ...]
    """
    print(f"\n正在扫描目录: {dataset_root_path}")
    
    if not os.path.exists(dataset_root_path):
        print(f"错误：目录 {dataset_root_path} 不存在")
        return []
    
    # 获取所有case目录
    case_dirs = []
    for item in os.listdir(dataset_root_path):
        item_path = os.path.join(dataset_root_path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            case_dirs.append(item)
    
    case_dirs.sort()
    
    if not case_dirs:
        print("未找到任何case目录")
        return []
    
    print(f"\n找到 {len(case_dirs)} 个case目录:")
    for i, case_dir in enumerate(case_dirs, 1):
        print(f"{i:2d}. {case_dir}")
    
    # 让用户选择case
    while True:
        try:
            selection = input(f"\n请选择case编号 (1-{len(case_dirs)}) 或输入'all'选择所有case: ").strip().lower()
            
            if selection == 'all':
                selected_case_dirs = case_dirs
                break
            else:
                case_idx = int(selection) - 1
                if 0 <= case_idx < len(case_dirs):
                    selected_case_dirs = [case_dirs[case_idx]]
                    break
                else:
                    print(f"无效选择，请输入1-{len(case_dirs)}之间的数字")
        except ValueError:
            print("输入无效，请输入数字或'all'")
    
    # 对于选中的每个case，获取其segment
    all_test_cases = []
    for case_dir in selected_case_dirs:
        case_path = os.path.join(dataset_root_path, case_dir)
        
        # 获取该case下的所有segment
        segments = []
        for item in os.listdir(case_path):
            item_path = os.path.join(case_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                segments.append(item)
        
        segments.sort()
        
        if not segments:
            print(f"警告：case {case_dir} 下没有找到segment")
            continue
        
        print(f"\ncase {case_dir} 中找到 {len(segments)} 个segment:")
        for i, segment in enumerate(segments, 1):
            print(f"  {i:2d}. {segment}")
        
        # 如果只有一个case被选中，让用户选择segment
        if len(selected_case_dirs) == 1:
            while True:
                try:
                    seg_selection = input(f"请选择segment编号 (1-{len(segments)}) 或输入'all'选择所有segment: ").strip().lower()
                    
                    if seg_selection == 'all':
                        selected_segments = segments
                        break
                    else:
                        seg_idx = int(seg_selection) - 1
                        if 0 <= seg_idx < len(segments):
                            selected_segments = [segments[seg_idx]]
                            break
                        else:
                            print(f"无效选择，请输入1-{len(segments)}之间的数字")
                except ValueError:
                    print("输入无效，请输入数字或'all'")
        else:
            # 多个case时，默认选择所有segment
            selected_segments = segments
        
        # 添加到测试用例列表
        for segment in selected_segments:
            test_case_path = f"{case_dir}/{segment}"
            all_test_cases.append(test_case_path)
    
    return all_test_cases

def process_single_test_case_ocr(args):
    """
    处理单个测试用例的函数，用于并发执行OCR开始帧检测
    
    Args:
        args: 包含测试用例信息和结果保存器的元组
        
    Returns:
        dict: 处理结果
    """
    test_case, dataset_root_path, case_index, total_cases, result_saver, ocr_config, llm_client = args
    
    # 为每个线程生成唯一标识符
    thread_id = threading.current_thread().ident
    unique_id = f"{thread_id}_{uuid.uuid4().hex[:8]}"
    
    case_key = test_case["case_key"]
    gt_start_frame = test_case.get("gt_start_frame", None)
    
    message = f"[线程{unique_id}] 处理第 {case_index}/{total_cases} 个测试用例: {case_key}"
    print(message)
    result_saver.log_message(message)
    
    if gt_start_frame is not None:
        message = f"[线程{unique_id}] Ground Truth开始帧: {gt_start_frame}"
        print(message)
        result_saver.log_message(message)
    
    # 构建segment_dir路径
    if os.path.isabs(case_key) or case_key.startswith(dataset_root_path):
        segment_dir = case_key
    else:
        segment_dir = os.path.join(dataset_root_path, case_key)
    
    if not os.path.exists(segment_dir):
        message = f"[线程{unique_id}] 警告: 目录不存在 {segment_dir}"
        print(message)
        result_saver.log_message(message)
        
        result = {
            "case_key": case_key,
            "gt_start_frame": gt_start_frame,
            "pred_start_frame": None,
            "diff": None,
            "match_type": "failed",
            "error": "目录不存在",
            "timestamp": datetime.datetime.now().isoformat(),
            "thread_id": unique_id,
            "method_used": "ocr_ultra_fast"
        }
        result_saver.save_result(result)
        return result
    
    try:
        # 查找视频文件
        video_files = find_video_files(segment_dir)
        if not video_files:
            message = f"[线程{unique_id}] 警告: 目录中没有找到视频文件"
            print(message)
            result_saver.log_message(message)
            
            result = {
                "case_key": case_key,
                "gt_start_frame": gt_start_frame,
                "pred_start_frame": None,
                "diff": None,
                "match_type": "failed",
                "error": "没有找到视频文件",
                "timestamp": datetime.datetime.now().isoformat(),
                "thread_id": unique_id,
                "method_used": "ocr_ultra_fast"
            }
            result_saver.save_result(result)
            return result
        
        # 使用第一个视频文件
        video_path = video_files[0]
        message = f"[线程{unique_id}] 使用视频文件: {os.path.basename(video_path)}"
        print(message)
        result_saver.log_message(message)
        
        # 调用OCR开始帧检测函数
        ocr_result = llm_narrow_start_frame_ocr_ultra_fast(
            video_path=video_path,
            llm_client=llm_client,  # 传递LLM客户端
            do_evaluation=ocr_config.get("show_realtime_output", False),  # 根据配置决定是否显示实时输出
            max_frames=ocr_config.get("max_frames", 10000),
            skip_frames=ocr_config.get("skip_frames", 1),
            scale_factor=ocr_config.get("scale_factor", 0.25),
            early_stop=ocr_config.get("early_stop", True),
            save_frame_texts=ocr_config.get("save_frame_texts", True), # 传递save_frame_texts参数
            ui_infer_config=ocr_config.get("ui_infer_config") # 传递UI infer配置
        )
        
        if not ocr_result["success"]:
            message = f"[线程{unique_id}] OCR检测失败: {ocr_result.get('error', '未知错误')}"
            print(message)
            result_saver.log_message(message)
            
            result = {
                "case_key": case_key,
                "gt_start_frame": gt_start_frame,
                "pred_start_frame": None,
                "diff": None,
                "match_type": "failed",
                "error": ocr_result.get('error', 'OCR检测失败'),
                "timestamp": datetime.datetime.now().isoformat(),
                "thread_id": unique_id,
                "method_used": "ocr_ultra_fast"
            }
            result_saver.save_result(result)
            return result
        
        # 获取预测的开始帧
        start_frame_info = ocr_result.get("start_frame")
        if start_frame_info is None:
            message = f"[线程{unique_id}] 未检测到开始帧"
            print(message)
            result_saver.log_message(message)
            
            result = {
                "case_key": case_key,
                "gt_start_frame": gt_start_frame,
                "pred_start_frame": None,
                "diff": None,
                "match_type": "failed",
                "error": "未检测到开始帧",
                "timestamp": datetime.datetime.now().isoformat(),
                "thread_id": unique_id,
                "method_used": "ocr_ultra_fast"
            }
            result_saver.save_result(result)
            return result
        
        pred_start_frame = start_frame_info["frame_number"]
        
        # 计算差异（如果有ground truth）
        if gt_start_frame is not None:
            diff = abs(pred_start_frame - gt_start_frame)
            
            # 判断匹配类型
            if diff == 0:
                match_type = "perfect"
            elif diff <= 5:
                match_type = "close"
            elif diff <= 20:
                match_type = "mid"
            else:
                match_type = "other"
        else:
            diff = None
            match_type = "no_gt"
        
        message = f"[线程{unique_id}] 预测开始帧: {pred_start_frame}"
        print(message)
        result_saver.log_message(message)
        
        if diff is not None:
            message = f"[线程{unique_id}] 差异: {diff}"
            print(message)
            result_saver.log_message(message)
        
        message = f"[线程{unique_id}] 匹配类型: {match_type}"
        print(message)
        result_saver.log_message(message)
        
        result = {
            "case_key": case_key,
            "gt_start_frame": gt_start_frame,
            "pred_start_frame": pred_start_frame,
            "diff": diff,
            "match_type": match_type,
            "error": None,
            "timestamp": datetime.datetime.now().isoformat(),
            "thread_id": unique_id,
            "method_used": "ocr_ultra_fast",
            "ocr_config": ocr_config,
            "video_file": os.path.basename(video_path),
            "processing_time": ocr_result.get("processing_time", 0),
            "processed_frames": ocr_result.get("processed_frames", 0),
            "total_frames": ocr_result.get("total_frames", 0),
            "candidates_count": len(ocr_result.get("candidates", [])),
            "frame_texts": ocr_result.get("frame_texts", []) # 添加frame_texts到结果中
        }
        result_saver.save_result(result)
        return result
        
    except Exception as e:
        message = f"[线程{unique_id}] 错误: 处理测试用例时出错: {e}"
        print(message)
        result_saver.log_message(message)
        
        result = {
            "case_key": case_key,
            "gt_start_frame": gt_start_frame,
            "pred_start_frame": None,
            "diff": None,
            "match_type": "failed",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat(),
            "thread_id": unique_id,
            "method_used": "ocr_ultra_fast"
        }
        result_saver.save_result(result)
        return result


def test_ocr_basic():
    """测试OCR基本功能"""
    print("=== 测试OCR基本功能 ===")
    
    # 创建一个简单的测试图片
    import numpy as np
    
    # 创建一个白色背景的图片
    test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
    
    # 在图片上添加一些文字（模拟）
    cv2.putText(test_image, "X:123 Y:456", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # 保存测试图片
    cv2.imwrite("test_ocr_image.png", test_image)
    print("创建测试图片: test_ocr_image.png")
    
    try:
        print("开始OCR测试...")
        texts = call_ocr_service(test_image, url="http://10.164.6.121:8417/paddelocr")
        print(f"OCR测试成功，识别到 {len(texts)} 个文本")
        print(f"识别的文本: {texts}")
        
        return True
    except Exception as e:
        print(f"OCR测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== 超高效OCR开始帧检测测试 ===")
    print("💡 优化策略:")
    print("  - 内存中直接处理，不保存临时文件")
    print("  - 激进的跳帧处理（每3帧处理1帧）")
    print("  - 大幅缩小图片尺寸（缩小到1/4）")
    print("  - 早期停止（找到第一个坐标就停止）")
    print("  - 强制垃圾回收释放内存")
    print("  - 轻量级OCR配置")
    print("  - 支持批量测试和ground truth计算")
    print("  - 新增设备类型检测：安卓设备使用OCR，其他设备使用UI Infer")
    print()
    
    # 直接测试temp/test_task_001目录
    test_frame_dir = "temp/test_task_001"
    
    if not os.path.exists(test_frame_dir):
        print(f"错误: 测试目录不存在: {test_frame_dir}")
        return
    
    print(f"开始测试目录: {test_frame_dir}")
    
    # 初始化LLM客户端（用于UI infer方案）
    llm_client = None
    try:
        import boto3
        llm_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("LLM客户端初始化成功")
    except Exception as e:
        print(f"LLM客户端初始化失败: {e}")
        print("将无法处理非安卓设备的视频")
    
    # 配置参数
    ocr_config = {
        "max_frames": 10000,      # 最大处理帧数
        "skip_frames": 1,       # 跳帧数
        "scale_factor": 0.7,   # 缩放因子
        "early_stop": True,      # 早期停止
        "save_frame_texts": True, # 保存每帧文本
        "show_realtime_output": True, # 显示实时输出
        "ui_infer_config": { # 新增UI infer配置
            "activity_threshold": -0.001,
            "merge_window": 3,
            "start_threshold": -0.0001,
            "end_threshold": -0.00003,
            "ssim_threshold": 0.995,
            "model": "anthropic.claude-3.7-sonnet",
            "max_voting_rounds": 10,
            "temperature": 0.1,
            "remove_background": False,
            "enable_diff": False,
            "ui_infer_max_retries": 3,
            "ui_infer_retry_delay": 2
        }
    }
    
    print("配置参数:")
    for key, value in ocr_config.items():
        print(f"  - {key}: {value}")
    
    # 直接进行测试
    print(f"\n开始测试 {test_frame_dir}...")
    
    # 1. 先检测设备类型
    print("\n=== 设备类型检测 ===")
    is_android = detect_android_by_first_frame_from_frames(test_frame_dir)
    print(f"设备类型检测结果: {'安卓设备' if is_android else '非安卓设备'}")
    
    # 2. 根据设备类型选择检测方法
    if is_android:
        print("\n=== 使用OCR方法检测开始帧 ===")
        result = _llm_narrow_start_frame_ocr_ultra_fast_android_from_frames(
            frame_dir=test_frame_dir,
            do_evaluation=True,
            max_frames=300,
            skip_frames=1,
            scale_factor=1.0,
            early_stop=True,
            save_frame_texts=True,
            fps=30.0
        )
    else:
        print("\n=== 使用UI Infer方法检测开始帧 ===")
        result = llm_narrow_start_frame_ocr_ultra_fast_from_frames(
            frame_dir=test_frame_dir,
            llm_client=llm_client,
            do_evaluation=True,
            max_frames=300,
            skip_frames=1,
            scale_factor=1.0,
            early_stop=True,
            save_frame_texts=True,
            ui_infer_config=ocr_config["ui_infer_config"],
            fps=30.0
        )
    
    # 3. 输出结果
    print("\n=== 测试结果 ===")
    if result["success"]:
        print(f"检测成功!")
        print(f"开始帧: {result['start_frame']}")
        if 'frame_texts' in result and result['frame_texts']:
            print(f"处理帧数: {len(result['frame_texts'])}")
    else:
        print(f"检测失败: {result['error']}")
    
    print("\n测试完成!")

def test_ground_truth_calculation():
    """测试ground truth计算功能"""
    print("=== 测试Ground Truth计算功能 ===")
    
    # 测试解析case_key
    test_case_key = "2025-07-03_1751514078822,VID_20250703_113456/1_15s"
    video_name, action_time = parse_case_key_for_gt(test_case_key)
    print(f"解析case_key: {test_case_key}")
    print(f"  视频名: {video_name}")
    print(f"  时间: {action_time}")
    
    # 测试查找action_info文件
    if video_name and action_time is not None:
        action_info_path = find_action_info_file_for_gt(video_name, action_time, "downloaded_videos_processed")
        print(f"找到action_info文件: {action_info_path}")
        
        if action_info_path:
            # 测试计算ground truth
            gt_start_frame = calculate_ground_truth_start_frame_for_gt(action_info_path)
            print(f"计算得到的ground truth开始帧: {gt_start_frame}")
        else:
            print("未找到对应的action_info文件")
    
    print("Ground Truth计算功能测试完成")

# 如果需要单独测试ground truth计算功能，可以取消下面的注释
# if __name__ == "__main__":
#     test_ground_truth_calculation() 

def llm_narrow_start_frame_ocr_ultra_fast_from_frames(
    frame_dir: str, 
    llm_client=None,
    do_evaluation: bool = False,
    max_frames: int = None,
    skip_frames: int = 1,
    scale_factor: float = 0.25,
    early_stop: bool = True,
    save_frame_texts: bool = True,
    ui_infer_config: dict = None,
    fps: float = 30.0  # 默认帧率
):
    """
    从图片文件夹进行超高效的OCR开始帧检测方法
    支持设备类型检测：安卓设备使用OCR方案，其他设备使用UI infer方案
    
    Args:
        frame_dir: 图片文件夹路径
        llm_client: LLM客户端实例（用于UI infer方案）
        do_evaluation: 是否进行评估输出
        max_frames: 最大处理帧数，None表示处理所有帧
        skip_frames: 跳帧数，1表示每帧都处理
        scale_factor: 图片缩放因子，0.25表示缩小到原来的1/4
        early_stop: 是否找到第一个坐标就停止
        save_frame_texts: 是否保存每帧提取的文本
        ui_infer_config: UI infer配置参数
        fps: 帧率，用于计算时间戳
    
    Returns:
        dict: 包含检测结果的字典
    """
    
    # 导入设备类型检测函数
    from .llm_narrow_core import detect_android_by_first_frame, llm_narrow_start_frame_with_ui_infer_from_frames
    
    print(f"=== 开始帧检测（图片文件夹）: {os.path.basename(frame_dir)} ===")
    
    # 1. 首先检测设备类型（使用第一帧）
    print("正在检测设备类型...")
    is_android = detect_android_by_first_frame_from_frames(frame_dir)
    is_android = True
    if is_android:
        print("检测到安卓设备，使用OCR方案")
        return _llm_narrow_start_frame_ocr_ultra_fast_android_from_frames(
            frame_dir, do_evaluation, max_frames, skip_frames, 
            scale_factor, early_stop, save_frame_texts, fps
        )
    else:
        print("检测到非安卓设备，使用UI Infer方案")
        if llm_client is None:
            return {
                'success': False,
                'error': '非安卓设备需要LLM客户端，但未提供',
                'start_frame': None,
                'candidates': []
            }
        
        # 使用UI infer方案
        ui_config = ui_infer_config or {}
        return llm_narrow_start_frame_with_ui_infer_from_frames(
            frame_dir=frame_dir,  # 传递图片文件夹路径
            llm_client=llm_client,
            do_evaluation=do_evaluation,
            activity_threshold=ui_config.get('activity_threshold', -0.001),
            merge_window=ui_config.get('merge_window', 3),
            start_threshold=ui_config.get('start_threshold', -0.0001),
            end_threshold=ui_config.get('end_threshold', -0.00003),
            ssim_threshold=ui_config.get('ssim_threshold', 0.995),
            model=ui_config.get('model', "anthropic.claude-3.7-sonnet"),
            max_voting_rounds=ui_config.get('max_voting_rounds', 10),
            temperature=ui_config.get('temperature', 0.1),
            remove_background=ui_config.get('remove_background', False),
            enable_diff=ui_config.get('enable_diff', False),
            ui_infer_max_retries=ui_config.get('ui_infer_max_retries', 3),
            ui_infer_retry_delay=ui_config.get('ui_infer_retry_delay', 2),
            fps=fps
        )

def detect_android_by_first_frame_from_frames(frame_dir: str, ocr_url: str = "http://10.164.6.121:8417/paddelocr") -> bool:
    """
    通过第一帧OCR检测判断是否为安卓设备（从图片文件夹）
    """
    import cv2
    import base64
    import requests
    
    def check_words(text):
        """检查文本中是否包含坐标信息（第一帧检测，宽松版本）"""
        import re
        # 宽松版本：有关键字且有数字，但不要求冒号
        pattern = re.compile(r'(?i)\b(Xv|Yv|dY|dX|X|Y)\b[^a-z]*\d+\.?\d*')
        match = pattern.search(text)
        if match:
            print(f"匹配到坐标信息: '{text}' -> {match.group()}")
        return match is not None
    
    def call_ocr_service(image, url):
        """调用OCR服务"""
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', image_rgb)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            data = {'image': img_base64}
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    texts = []
                    for item in result.get('results', []):
                        text = item.get('text', '')
                        if text.strip():
                            texts.append(text)
                    return texts
                else:
                    print(f"OCR服务返回错误: {result.get('error')}")
                    return []
            else:
                print(f"HTTP请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"调用OCR服务出错: {e}")
            return []
    
    try:
        # 查找第一帧图片文件
        first_frame_path = None
        possible_filenames = [
            "frame_0.jpeg", "frame_0.jpg", "frame_0.png",
            "0.jpeg", "0.jpg", "0.png",
            "0000.jpeg", "0000.jpg", "0000.png"
        ]
        
        for filename in possible_filenames:
            test_path = os.path.join(frame_dir, filename)
            if os.path.exists(test_path):
                first_frame_path = test_path
                break
        
        if first_frame_path is None:
            print(f"在目录 {frame_dir} 中未找到第一帧图片文件")
            return False
        
        # 读取第一帧
        frame = cv2.imread(first_frame_path)
        if frame is None:
            print(f"无法读取第一帧图片: {first_frame_path}")
            return False
        
        # 先进行背景扣除
        print(f"开始对第一帧进行背景扣除: {first_frame_path}")
        try:
            # 使用rembg进行背景扣除
            from src.utils.llm_narrow_core import remove_background_with_rembg
            from PIL import Image
            
            # 直接在原文件夹下保存临时文件
            temp_frame_path = os.path.join(frame_dir, "temp_first_frame.png")
            
            # 保存原始帧为PNG格式（rembg需要）
            cv2.imwrite(temp_frame_path, frame)
            
            # 使用rembg进行背景扣除，输出文件也会在原文件夹下
            removed_bg_path = remove_background_with_rembg(temp_frame_path)
            
            if removed_bg_path and os.path.exists(removed_bg_path):
                # 读取扣除背景后的帧
                frame = cv2.imread(removed_bg_path)
                if frame is not None:
                    print(f"rembg背景扣除完成，新尺寸: {frame.shape}")
                else:
                    print(f"rembg背景扣除后无法读取图片，使用原始图片")
                    frame = cv2.imread(first_frame_path)
            else:
                print(f"rembg背景扣除失败，使用原始图片")
                frame = cv2.imread(first_frame_path)
            
            # 清理临时文件
            try:
                if os.path.exists(temp_frame_path):
                    os.remove(temp_frame_path)
            except:
                pass
                
        except ImportError as e:
            print(f"无法导入rembg模块: {e}，跳过背景扣除")
        except Exception as e:
            print(f"背景扣除失败: {e}，使用原始图片")
            frame = cv2.imread(first_frame_path)
        
        # 调用OCR服务
        texts = call_ocr_service(frame, ocr_url)
        
        # 打印所有识别的文本
        print(f"第一帧OCR识别结果:")
        print(f"识别到的所有文本: {texts}")
        
        # 保存抠出来的图片用于查看
        debug_image_path = os.path.join(frame_dir, "debug_first_frame_cropped.jpeg")
        cv2.imwrite(debug_image_path, frame)
        print(f"抠出来的图片已保存到: {debug_image_path}")
        
        # 检查是否包含坐标信息
        for text in texts:
            if check_words(text):
                print(f"检测到坐标信息: {text}，判定为安卓设备")
                return True
        
        print("未检测到坐标信息，判定为非安卓设备")
        return False
        
    except Exception as e:
        print(f"检测设备类型时出错: {e}")
        return False

def _llm_narrow_start_frame_ocr_ultra_fast_android_from_frames(
    frame_dir: str, 
    do_evaluation: bool = False,
    max_frames: int = None,
    skip_frames: int = 1,
    scale_factor: float = 1.0,
    early_stop: bool = True,
    save_frame_texts: bool = True,
    fps: float = 30.0
):
    """
    安卓设备的OCR开始帧检测方法（从图片文件夹）
    """
    
    # 获取所有帧文件
    frame_files = []
    import re
    def natural_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]
    frame_files = sorted([f for f in os.listdir(frame_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))], key=natural_key)
    frame_files = [os.path.join(frame_dir, f) for f in frame_files]
    
    if not frame_files:
        return {
            'success': False,
            'error': f'在目录中未找到图片文件: {frame_dir}',
            'start_frame': None,
            'candidates': [],
            'frame_texts': []
        }
    
    # 获取视频信息（从第一帧推断）
    first_frame = cv2.imread(frame_files[0])
    if first_frame is None:
        return {
            'success': False,
            'error': f'无法读取第一帧图片: {frame_files[0]}',
            'start_frame': None,
            'candidates': [],
            'frame_texts': []
        }
    
    total_frames = len(frame_files)
    height, width = first_frame.shape[:2]
    
    if do_evaluation:
        print(f"图片文件夹信息:")
        print(f"  总帧数: {total_frames}")
        print(f"  FPS: {fps:.2f}")
        print(f"  分辨率: {width}x{height}")
        print(f"  跳帧数: {skip_frames}")
        print(f"  缩放因子: {scale_factor}")
        print(f"  早期停止: {early_stop}")
        if max_frames:
            print(f"  最大处理帧数: {max_frames}")
    
    candidates = []
    processed_frames = 0
    start_time = time.time()
    
    # 记录每帧提取的文本
    frame_texts = []
    
    # 处理每一帧
    for frame_idx, frame_path in enumerate(frame_files):
        # 检查是否达到最大帧数限制
        if max_frames and processed_frames >= max_frames:
            break
        
        processed_frames += 1
        frame_index = processed_frames - 1
        basename = os.path.splitext(os.path.basename(frame_path))[0]
        
        if do_evaluation and processed_frames % 5 == 0:
            elapsed_time = time.time() - start_time
            fps_processed = processed_frames / elapsed_time if elapsed_time > 0 else 0
            print(f"处理帧 {processed_frames}: 帧号 {frame_index}, 处理速度: {fps_processed:.1f} fps")
        
        try:
            # 读取图片
            frame = cv2.imread(frame_path)
            if frame is None:
                if do_evaluation:
                    print(f"  帧 {frame_index} - 无法读取图片: {frame_path}")
                continue
            
            # 先进行背景扣除
            if do_evaluation:
                print(f"  帧 {frame_index} - 开始背景扣除...")
            
            try:
                # 使用rembg进行背景扣除
                from src.utils.llm_narrow_core import remove_background_with_rembg
                from PIL import Image
                
                # 直接在原文件夹下保存临时文件，命名用原始文件名
                temp_frame_path = os.path.join(frame_dir, f"temp_{basename}.png")
                
                # 保存原始帧为PNG格式（rembg需要）
                cv2.imwrite(temp_frame_path, frame)
                
                # 使用rembg进行背景扣除，输出文件也会在原文件夹下
                removed_bg_path = remove_background_with_rembg(temp_frame_path)
                
                if removed_bg_path and os.path.exists(removed_bg_path):
                    # 读取扣除背景后的帧
                    frame = cv2.imread(removed_bg_path)
                    if frame is not None:
                        if do_evaluation:
                            print(f"  帧 {frame_index} - rembg背景扣除完成，新尺寸: {frame.shape}")
                        # 对移除背景后的图片做大小调整
                        from src.utils.llm_narrow_core import check_and_resize_saved_image
                        enhanced_path = check_and_resize_saved_image(removed_bg_path, max_file_size_mb=3.5, min_file_size_mb=2.5)
                        if enhanced_path and os.path.exists(enhanced_path):
                            from PIL import Image
                            enhanced_pil = Image.open(enhanced_path)
                            print(enhanced_path)
                            enhanced_frame = cv2.cvtColor(np.array(enhanced_pil), cv2.COLOR_RGB2BGR)
                            if enhanced_frame is not None:
                                frame = enhanced_frame
                                if do_evaluation:
                                    print(f"  帧 {frame_index} - 移除背景后图片大小调整完成: {enhanced_pil.size}")
                            else:
                                if do_evaluation:
                                    print(f"  帧 {frame_index} - 移除背景后图片大小调整后无法读取，使用原始尺寸")
                        else:
                            if do_evaluation:
                                print(f"  帧 {frame_index} - 移除背景后图片大小调整失败，使用原始尺寸")
                    else:
                        if do_evaluation:
                            print(f"  帧 {frame_index} - rembg背景扣除后无法读取图片，使用原始图片")
                        frame = cv2.imread(frame_path)
                else:
                    if do_evaluation:
                        print(f"  帧 {frame_index} - rembg背景扣除失败，使用原始图片")
                    frame = cv2.imread(frame_path)
                # 清理临时文件
                try:
                    if os.path.exists(temp_frame_path):
                        os.remove(temp_frame_path)
                except:
                    pass
                    
            except ImportError as e:
                if do_evaluation:
                    print(f"  帧 {frame_index} - 无法导入rembg模块: {e}，跳过背景扣除")
            except Exception as e:
                if do_evaluation:
                    print(f"  帧 {frame_index} - 背景扣除失败: {e}，使用原始图片")
                frame = cv2.imread(frame_path)
            
            # 图片缩放以减少内存使用和提高处理速度（在放大之后进行）
            # 已去除scale_factor缩小图片的代码，保证用的就是check_and_resize后的图片
            
            if do_evaluation:
                print(f"  帧 {frame_index} - 开始OCR识别...")
                print(f"  图片尺寸: {frame.shape}")
                print(f"  图片数据类型: {frame.dtype}")
            
            # 调用HTTP OCR服务
            try:
                rec_texts = call_ocr_service(frame, url="http://10.164.6.121:8417/paddelocr")
                if do_evaluation:
                    print(f"  帧 {frame_index} - OCR识别完成")
                    print(f"  提取的文本: {rec_texts}")
            except Exception as ocr_error:
                if do_evaluation:
                    print(f"  帧 {frame_index} - OCR识别失败: {ocr_error}")
                    print(f"  OCR错误类型: {type(ocr_error).__name__}")
                    import traceback
                    traceback.print_exc()
                raise ocr_error
            
            # 记录每帧的文本信息
            frame_text_info = {
                'frame_number': frame_index,
                'frame_index': frame_index,
                'frame_file': os.path.basename(frame_path),
                'timestamp': frame_index / fps if fps > 0 else 0,
                'ocr_texts': rec_texts,
                'has_coordinates': False,
                'coordinate_texts': []
            }
            
            # 判断是否存在点击坐标
            has_coordinates = False
            coordinate_texts = []
            for text in rec_texts:
                if check_words(text):
                    has_coordinates = True
                    coordinate_texts.append(text)
                    break
            
            if has_coordinates:
                candidates.append({
                    'frame_path': frame_path,
                    'frame_index': frame_index,
                    'frame_file': os.path.basename(frame_path),
                    'ocr_texts': rec_texts,
                    'coordinate_texts': coordinate_texts
                })
                
                frame_text_info['has_coordinates'] = True
                frame_text_info['coordinate_texts'] = coordinate_texts
                
                if do_evaluation:
                    print(f"  检测到坐标信息: {coordinate_texts}")
                    print(f"  所有OCR文本: {rec_texts}")
                
                # 如果启用早期停止，找到第一个坐标就停止
                if early_stop:
                    if do_evaluation:
                        print(f"  启用早期停止，找到第一个坐标帧，停止处理")
                    break
            
            frame_texts.append(frame_text_info)
            
        except Exception as e:
            if do_evaluation:
                print(f"  处理帧 {frame_path} 时出错: {e}")
    
    # 选择第一个检测到坐标的帧作为开始帧
    start_frame = candidates[0] if candidates else None
    
    result = {
        'success': True,
        'start_frame': start_frame,
        'candidates': candidates,
        'total_frames': total_frames,
        'processed_frames': processed_frames,
        'frame_texts': frame_texts if save_frame_texts else [],
        'method_used': 'ocr_ultra_fast_from_frames'
    }
    
    # 评估模式输出
    if do_evaluation:
        print(f"\n=== 检测结果 ===")
        print(f"总帧数: {total_frames}")
        print(f"处理帧数: {processed_frames}")
        print(f"检测到坐标的帧数: {len(candidates)}")
        
        if start_frame:
            print(f"\n开始帧: {os.path.basename(start_frame['frame_path'])}")
            print(f"帧索引: {start_frame['frame_index']}")
            print(f"坐标文本: {start_frame['coordinate_texts']}")
            print(f"所有OCR文本: {start_frame['ocr_texts']}")
        else:
            print("未检测到包含坐标信息的帧")
    
    return result

def llm_narrow_start_frame_with_ui_infer(
    video_path: str,
    llm_client,
    do_evaluation=False,
    activity_threshold=-0.001,
    merge_window=3,
    start_threshold=-0.0001,
    end_threshold=-0.00003,
    ssim_threshold=0.995,
    model="anthropic.claude-3.7-sonnet",
    max_voting_rounds=10,
    temperature=0.1,
    remove_background=False,
    enable_diff=False,
    ui_infer_max_retries=3,
    ui_infer_retry_delay=2
):
    """
    基于UI infer的开始帧检测方法
    使用LLM+拼图+投票的方式找到操作开始的第一帧
    
    Args:
        video_path: 视频文件路径
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        start_threshold: 开始点阈值，默认-0.0001
        end_threshold: 结束点阈值，默认-0.00003
        ssim_threshold: SSIM阈值，默认0.995
        model: 使用的模型名称，默认"anthropic.claude-3.7-sonnet"
        max_voting_rounds: 最大投票轮数，默认10
        temperature: 温度参数，默认0.1
        remove_background: 是否去除背景，默认False
        enable_diff: 是否启用差异检测，默认False
        ui_infer_max_retries: UI推断最大重试次数，默认3次
        ui_infer_retry_delay: UI推断重试间隔（秒），默认2秒
    
    Returns:
        dict: 包含检测结果的字典
    """
    import math
    from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
    
    print(f"开始UI infer开始帧检测: {video_path}")
    
    # 创建临时目录用于处理视频帧
    import tempfile
    import cv2
    import os
    
    temp_dir = tempfile.mkdtemp(prefix="start_frame_ui_infer_")
    print(f"临时目录: {temp_dir}")
    
    try:
        # 1. 提取视频帧到临时目录
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {
                'success': False,
                'error': f'无法打开视频文件: {video_path}',
                'start_frame': None,
                'candidates': []
            }
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if do_evaluation:
            print(f"视频信息:")
            print(f"  总帧数: {total_frames}")
            print(f"  FPS: {fps:.2f}")
            print(f"  分辨率: {width}x{height}")
        
        # 提取帧到临时目录
        frame_count = 0
        extracted_frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 保存帧为PNG文件
            frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
            cv2.imwrite(frame_path, frame)
            extracted_frames.append(frame_path)
            frame_count += 1
            
            # 限制处理的帧数，避免处理过多帧
            if frame_count >= 100:  # 最多处理100帧
                break
        
        cap.release()
        
        if not extracted_frames:
            return {
                'success': False,
                'error': '无法提取视频帧',
                'start_frame': None,
                'candidates': []
            }
        
        print(f"成功提取 {len(extracted_frames)} 帧")
        
        # 2. 创建action_info.json文件（模拟）
        action_info = {
            "original_action_item": {
                "action_desc": "开始帧检测",
                "action_time": 0.0,
                "marked_start_time": 0.0,
                "marked_end_time": len(extracted_frames) / fps if fps > 0 else 0.0
            },
            "extraction_parameters": {
                "num_extracted_frames": len(extracted_frames),
                "fps": fps,
                "extract_start_time_sec": 0.0,
                "width": width,
                "height": height
            }
        }
        
        action_info_path = os.path.join(temp_dir, "action_info.json")
        with open(action_info_path, "w", encoding="utf-8") as f:
            json.dump(action_info, f, indent=2, ensure_ascii=False)
        
        # 3. 初始化Horus客户端
        horus_client = ClientHorus()
        
        # 4. 生成候选帧（从0开始，不筛除开始帧之前的帧）
        # 使用活动检测来找到可能的开始帧
        from src.algorithms.find_page_load_intelligent import preprocess_ssim_data, find_page_load_intelligent
        
        # 计算帧间差异
        ssim_data = []
        for i in range(len(extracted_frames) - 1):
            try:
                img1 = cv2.imread(extracted_frames[i])
                img2 = cv2.imread(extracted_frames[i + 1])
                
                if img1 is not None and img2 is not None:
                    # 计算SSIM
                    from skimage.metrics import structural_similarity as ssim
                    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                    
                    # 确保两个图像尺寸相同
                    if gray1.shape != gray2.shape:
                        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
                    
                    ssim_score = ssim(gray1, gray2)
                    ssim_data.append(ssim_score)
                else:
                    ssim_data.append(1.0)  # 如果无法读取图像，假设相似
            except Exception as e:
                print(f"计算帧 {i} 和 {i+1} 的SSIM时出错: {e}")
                ssim_data.append(1.0)
        
        # 找到活动点（SSIM变化较大的地方）
        activity_points = []
        for i in range(len(ssim_data)):
            if i > 0:
                # 计算SSIM变化
                ssim_change = abs(ssim_data[i] - ssim_data[i-1])
                if ssim_change > activity_threshold:
                    activity_points.append(i)
        
        # 生成候选帧（包括活动点和一些均匀分布的帧）
        candidate_frames = set()
        
        # 添加活动点
        for point in activity_points:
            candidate_frames.add(point)
        
        # 添加均匀分布的帧（确保覆盖整个视频）
        step = max(1, len(extracted_frames) // 10)  # 最多10个均匀分布的帧
        for i in range(0, len(extracted_frames), step):
            candidate_frames.add(i)
        
        # 确保至少有5个候选帧
        if len(candidate_frames) < 5:
            for i in range(min(5, len(extracted_frames))):
                candidate_frames.add(i)
        
        candidate_frames = sorted(list(candidate_frames))
        
        if do_evaluation:
            print(f"候选帧: {candidate_frames}")
            print(f"活动点: {activity_points}")
        
        # 5. 创建拼图并进行UI infer
        grid_image_path = create_voting_image_grid_with_ui_infer(
            temp_dir, 
            candidate_frames, 
            horus_client,
            max_single_size=1200,  # 使用较小的尺寸
            label_height=40,
            ui_infer_max_retries=ui_infer_max_retries,
            ui_infer_retry_delay=ui_infer_retry_delay,
            remove_background=remove_background,
            enable_diff=enable_diff
        )
        
        if grid_image_path is None:
            return {
                'success': False,
                'error': '无法创建拼图',
                'start_frame': None,
                'candidates': []
            }
        
        # 6. 构建开始帧检测的prompt
        start_frame_prompt = (
            "You are a helpful assistant and an expert in start frame analysis. Your task is to identify the FIRST frame in the grid that shows the initial visible change after a user operation (e.g., click, tap, scroll) on a web or app page.\n\n"
            "Below is a grid of frames from a video showing the page loading or transition process. The frames are arranged from left to right, top to bottom.\n\n"
            "## Context:\n"
            "- The user has just performed an operation (e.g., click, tap, scroll).\n"
            "- Each frame is a snapshot of the page after the operation.\n"
            "- Your goal is to find the first frame where the page starts to change in response to the operation.\n\n"
            "## Definition of start frame:\n"
            "1. The start frame is the FIRST frame that shows any visible change or reaction after the user operation.\n"
            "2. Changes may include: button color change, loading indicator appearing, page content starting to update, new UI elements appearing, animations starting, etc.\n"
            "3. Ignore minor flickers, background animation, or non-essential UI changes that are not related to the main operation.\n"
            "4. The change should be a direct result of the user action, not random or unrelated animation.\n\n"
            "## Task:\n"
            "- Carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
            "- Pay special attention to:\n"
            "  - Button or UI element color/state changes\n"
            "  - Loading indicators or spinners appearing\n"
            "  - New content or images starting to load\n"
            "  - Any visible feedback that the operation has triggered a response\n"
            "- Ignore:\n"
            "  - Minor background animation\n"
            "  - Floating system buttons or overlays not related to the operation\n"
            "  - Small text scrolling or ticker effects\n\n"
            "## IMPORTANT:\n"
            "- You must choose ONLY from the candidate frames (gray borders). Do NOT select any reference or non-candidate frames.\n"
            "- Be precise: select the earliest frame that shows a clear, operation-related change.\n\n"
            "## Please answer in JSON format:\n"
            "{\n"
            "    \"frame_analysis\": [\n"
            "        {\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame\"},\n"
            "        {\"frame_number\": <frame_number>, \"description\": \"...\"},\n"
            "        // ... continue for all frames\n"
            "    ],\n"
            "    \"target_frame\": <frame_number>,\n"
            "    \"reason\": \"Detailed explanation of why this frame is the start frame, and why the others are not.\"\n"
            "}\n"
        )

        # 7. 调用LLM进行判断
        try:
            messages = [{"role": "user", "content": start_frame_prompt, "image_url": [grid_image_path]}]
            llm_response = llm_vision_request_with_retry(
                llm_client, 
                messages, 
                max_tokens=1024, 
                model=model,
                temperature=temperature
            )
            
            if do_evaluation:
                print(f"LLM响应: {llm_response}")
            
            # 8. 解析LLM响应
            try:
                # 尝试直接解析JSON
                response_json = json.loads(llm_response)
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试从markdown代码块中提取
                pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                match = re.search(pattern, llm_response)
                if match:
                    response_json = json.loads(match.group(1))
                else:
                    # 如果还是无法解析，使用默认值
                    print("无法解析LLM响应，使用默认值")
                    response_json = {"target_frame": candidate_frames[0] if candidate_frames else 0}
            
            target_frame = response_json.get("target_frame", 0)
            reason = response_json.get("reason", "无理由")
            confidence = response_json.get("confidence", 0.5)
            
            # 确保target_frame在候选帧范围内
            if target_frame not in candidate_frames:
                print(f"警告: LLM返回的帧号 {target_frame} 不在候选帧中，使用第一个候选帧")
                target_frame = candidate_frames[0] if candidate_frames else 0
            
            # 9. 构建结果
            result = {
                'success': True,
                'start_frame': {
                    'frame_number': target_frame,
                    'timestamp': target_frame / fps if fps > 0 else 0,
                    'reason': reason,
                    'confidence': confidence
                },
                'candidates': [
                    {
                        'frame_number': frame_idx,
                        'timestamp': frame_idx / fps if fps > 0 else 0,
                        'is_activity_point': frame_idx in activity_points
                    }
                    for frame_idx in candidate_frames
                ],
                'total_frames': len(extracted_frames),
                'activity_points': activity_points,
                'llm_response': llm_response,
                'method_used': 'ui_infer_start_frame'
            }
            
            if do_evaluation:
                print(f"\n=== UI Infer开始帧检测结果 ===")
                print(f"总帧数: {len(extracted_frames)}")
                print(f"候选帧数: {len(candidate_frames)}")
                print(f"活动点: {activity_points}")
                print(f"预测开始帧: {target_frame}")
                print(f"时间戳: {target_frame / fps:.2f}s")
                print(f"理由: {reason}")
                print(f"置信度: {confidence}")
            
            return result
            
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return {
                'success': False,
                'error': f'LLM调用失败: {e}',
                'start_frame': None,
                'candidates': []
            }
    
    finally:
        # 清理临时目录
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"已清理临时目录: {temp_dir}")
        except Exception as e:
            print(f"清理临时目录失败: {e}")


    


def llm_narrow_start_frame_with_ui_infer_from_frames(
    frame_dir: str,
    llm_client,
    do_evaluation=False,
    activity_threshold=-0.001,
    merge_window=3,
    start_threshold=-0.0001,
    end_threshold=-0.00003,
    ssim_threshold=0.995,
    model="anthropic.claude-3.7-sonnet",
    max_voting_rounds=10,
    temperature=0.1,
    remove_background=False,
    enable_diff=False,
    ui_infer_max_retries=3,
    ui_infer_retry_delay=2,
    fps=30.0
):
    """
    基于UI infer的开始帧检测方法（从图片文件夹）
    这是llm_narrow_start_frame_with_ui_infer的适配器版本，用于处理图片文件夹
    """
    import cv2
    import tempfile
    import os
    
    print(f"开始UI infer开始帧检测（图片文件夹）: {frame_dir}")
    
    # 创建临时视频文件
    temp_video_path = os.path.join(tempfile.gettempdir(), f"temp_video_{os.getpid()}.mp4")
    
    try:
        # 从图片文件夹创建视频文件
        frame_files = []
        for filename in sorted(os.listdir(frame_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                frame_files.append(os.path.join(frame_dir, filename))
        
        if not frame_files:
            return {
                'success': False,
                'error': f'在目录中未找到图片文件: {frame_dir}',
                'start_frame': None,
                'candidates': []
            }
        
        # 读取第一帧获取尺寸信息
        first_frame = cv2.imread(frame_files[0])
        if first_frame is None:
            return {
                'success': False,
                'error': f'无法读取第一帧图片: {frame_files[0]}',
                'start_frame': None,
                'candidates': []
            }
        
        height, width = first_frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        
        # 写入所有帧
        for frame_path in frame_files:
            frame = cv2.imread(frame_path)
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        # 调用原有的视频版本函数
        result = llm_narrow_start_frame_with_ui_infer(
            video_path=temp_video_path,
            llm_client=llm_client,
            do_evaluation=do_evaluation,
            activity_threshold=activity_threshold,
            merge_window=merge_window,
            start_threshold=start_threshold,
            end_threshold=end_threshold,
            ssim_threshold=ssim_threshold,
            model=model,
            max_voting_rounds=max_voting_rounds,
            temperature=temperature,
            remove_background=remove_background,
            enable_diff=enable_diff,
            ui_infer_max_retries=ui_infer_max_retries,
            ui_infer_retry_delay=ui_infer_retry_delay
        )
        
        return result
        
    except Exception as e:
        print(f"UI infer开始帧检测（图片文件夹）出错: {e}")
        return {
            'success': False,
            'error': f'UI infer开始帧检测出错: {str(e)}',
            'start_frame': None,
            'candidates': []
        }
    finally:
        # 清理临时视频文件
        if os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except:
                pass