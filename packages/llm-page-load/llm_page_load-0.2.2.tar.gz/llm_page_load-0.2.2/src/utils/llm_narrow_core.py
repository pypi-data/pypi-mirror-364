from .llm_narrow_utils import *
import os
import json
import torch
import pandas as pd
import numpy as np
import arrow
from typing import Dict, Any, List, Sequence, Optional
import concurrent.futures
import cv2
import time
import re
import shutil
import threading
import random
import math
import subprocess
import tempfile
import sys
import os
from PIL import ImageEnhance
import requests
import time
import traceback
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCR
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from ..algorithms.find_page_load_intelligent import find_page_load_intelligent,preprocess_ssim_data
from ..utils.frame_ssim_seq_gen import calculate_temporal_ssim_vectors_mp
from ..utils.extract_phone_screen import extract_phone_screen
# 添加toolchain_llm目录到Python路径，使绝对导入能够正常工作
current_dir = os.path.dirname(os.path.abspath(__file__))
toolchain_llm_dir = os.path.join(current_dir, "..", "toolchain_llm")
toolchain_llm_dir = os.path.abspath(toolchain_llm_dir)

# 将toolchain_llm的父目录添加到sys.path，这样service.ui_detection就能被找到
toolchain_llm_parent = os.path.dirname(toolchain_llm_dir)
if toolchain_llm_parent not in sys.path:
    sys.path.insert(0, toolchain_llm_parent)
    print(f"  [Path] 已添加toolchain_llm父目录到Python路径: {toolchain_llm_parent}")

# 将toolchain_llm目录本身也添加到sys.path，这样tools模块就能被找到
if toolchain_llm_dir not in sys.path:
    sys.path.insert(0, toolchain_llm_dir)
    print(f"  [Path] 已添加toolchain_llm目录到Python路径: {toolchain_llm_dir}")


from ..toolchain_llm.service.ui_detection.img_diff import ImageDiff
from ..toolchain_llm.service.ui_detection.line_feature_diff import line_feature_diff, get_ocr_result
# UI推断相关函数已移动到 llm_ui_infer.py 文件中
from .llm_ui_infer import get_ui_infer_with_retry
from .llm_ui_infer import extract_mask_regions_from_ui_infer
from .llm_ui_infer import create_final_iterative_grid_with_ui_infer
# 添加rembg路径到sys.path
rembg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "3.11", "lib", "python3.11", "site-packages")
if rembg_path not in sys.path:
    sys.path.insert(0, rembg_path)
    print(f"  [Rembg] 已添加rembg路径: {rembg_path}")

# 先导入numpy以避免冲突
try:
    import numpy as np
except ImportError:
    print(f"  [Rembg] 警告: 无法导入numpy")
    np = None

try:
    from rembg import remove
except ImportError as e:
    print(f"  [Rembg] 警告: 无法导入rembg: {e}")
    remove = None

from PIL import Image

def remove_background_with_rembg(image_path, output_path=None):
    """
    使用rembg移除图像背景，提取手机部分
    
    Args:
        image_path: 输入图像路径
        output_path: 输出图像路径，如果为None则自动生成
    
    Returns:
        str: 抠图后的图像路径，如果失败返回None
    """
    try:
        if output_path is None:
            # 生成临时输出路径
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = os.path.dirname(image_path)
            output_path = os.path.join(output_dir, f"{base_name}_removed_bg.png")
        
        print(f"  [Rembg] 正在移除背景: {image_path}")
        
        # 检查rembg是否可用
        if remove is None:
            print(f"  [Rembg] 错误: rembg未安装或无法导入")
            print(f"  [Rembg] 跳过背景移除，直接返回原始图像路径")
            return image_path
        
        # 读取输入图像
        input_image = Image.open(image_path)
        print(f"  [Rembg] 输入图像尺寸: {input_image.size}")
        
        # 使用rembg移除背景，保留透明背景
        output_image = remove(input_image, alpha_matting=True)
        
        # 裁剪透明区域，只保留有内容的部分
        bbox = output_image.getbbox()
        if bbox:
            output_image = output_image.crop(bbox)
            print(f"  [Rembg] 裁剪后尺寸: {output_image.size}")
        
        # 可选：轻微增强亮度
        enhancer = ImageEnhance.Brightness(output_image)
        output_image = enhancer.enhance(1.05)  # 轻微增强亮度
        
        # 保存结果
        output_image.save(output_path)
        print(f"  [Rembg] 背景移除成功: {output_path}")
        print(f"  [Rembg] 输出图像尺寸: {output_image.size}")
        
        return output_path
            
    except Exception as e:
        print(f"  [Rembg] 背景移除异常: {e}")
        return None


try:
    from ..algorithms.find_page_load_intelligent import preprocess_ssim_data, find_page_load_intelligent
except ImportError as e:
    print(f"错误：无法从 'find_page_load_intelligent.py' 导入所需函数: {e}")
    print("请确保find_page_load_intelligent.py在Python的搜索路径中。")
    exit()

def check_and_resize_saved_image(image_path, max_file_size_mb=3.5, min_file_size_mb=2.5):
    """
    检测已保存的图片文件大小，如果超过限制则动态调整并重新保存
    
    Args:
        image_path: 图片文件路径
        max_file_size_mb: 最大文件大小限制（MB）
        min_file_size_mb: 最小文件大小限制（MB）
    
    Returns:
        str: 调整后的图片文件路径（可能是新路径）
    """
    import os
    from PIL import Image
    
    if not os.path.exists(image_path):
        print(f"[文件检测] 文件不存在: {image_path}")
        return image_path
    
    # 检测文件大小
    file_size_bytes = os.path.getsize(image_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    print(f"[文件检测] {os.path.basename(image_path)} 当前大小: {file_size_mb:.2f}MB")
    
    if min_file_size_mb <= file_size_mb <= max_file_size_mb:
        print(f"[文件检测] 文件大小在目标范围内，无需调整")
        return image_path
    
    # 需要调整，加载图片
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size
        print(f"[文件检测] 开始动态调整图片: {original_width}x{original_height}")
        
        # 动态调整循环（最多15次，确保达到目标）
        for attempt in range(15):
            # 每次都重新检测实际文件大小
            current_size_mb = get_file_size_mb(image_path)
            
            print(f"[文件检测] 第{attempt+1}次检查: {img.size[0]}x{img.size[1]}, 实际文件大小: {current_size_mb:.2f}MB")
            
            if min_file_size_mb <= current_size_mb <= max_file_size_mb:
                print(f"[文件检测] 达到目标大小范围[{min_file_size_mb}-{max_file_size_mb}MB]，调整完成")
                break
            
            if current_size_mb > max_file_size_mb:
                # 需要缩小
                size_ratio = current_size_mb / max_file_size_mb
                if size_ratio > 4:
                    scale_factor = 0.5  # 超过4倍，大幅缩小
                elif size_ratio > 2.5:
                    scale_factor = 0.6  # 超过2.5倍，中等缩小
                elif size_ratio > 1.5:
                    scale_factor = 0.75  # 超过1.5倍，适度缩小
                else:
                    scale_factor = 0.9  # 轻微超过，小幅缩小
                
                print(f"[文件检测] 需要缩小，当前{current_size_mb:.2f}MB超过限制{max_file_size_mb}MB（倍数:{size_ratio:.2f})，缩放比例: {scale_factor}")
                
                width, height = img.size
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # 最小尺寸保护
                if new_width < 300 or new_height < 300:
                    print(f"[文件检测] 达到最小尺寸限制300x300，停止调整")
                    break
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img.save(image_path, format='PNG')
                
            elif current_size_mb < min_file_size_mb:
                # 需要放大
                size_ratio = min_file_size_mb / current_size_mb
                if size_ratio > 2.5:
                    scale_factor = 1.5  # 小于40%，大幅放大
                elif size_ratio > 1.5:
                    scale_factor = 1.2  # 小于67%，中等放大
                else:
                    scale_factor = 1.1  # 轻微偏小，小幅放大
                
                print(f"[文件检测] 需要放大，当前{current_size_mb:.2f}MB小于限制{min_file_size_mb}MB（倍数:{size_ratio:.2f})，缩放比例: {scale_factor}")
                
                width, height = img.size
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img.save(image_path, format='PNG')
        
        final_size_mb = get_file_size_mb(image_path)
        print(f"[文件检测] 最终调整结果: {img.size[0]}x{img.size[1]}, {final_size_mb:.2f}MB")
        
        return image_path
        
    except Exception as e:
        print(f"[文件检测] 调整过程中出错: {e}")
        return image_path

def get_file_size_mb(file_path):
    """获取文件大小（MB）"""
    import os
    return os.path.getsize(file_path) / (1024 * 1024)

def llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, max_retries=5, retry_delay=5, model: str = "anthropic.claude-3.7-sonnet", temperature=0.1):
    # 添加线程标识符用于调试
    thread_id = threading.current_thread().ident
    
    # 图片大小超限时的处理函数  
    def handle_image_size_error(messages_to_fix, target_size_mb=3.5):
        """当图片大小超限时，动态检测和缩小图片直到达到目标大小"""
        from PIL import Image
        import base64
        import io
        
        def get_image_size_mb(img_bytes):
            """计算图片的文件大小（MB）"""
            return len(img_bytes) / (1024 * 1024)
        
        modified_messages = []
        for message in messages_to_fix:
            if isinstance(message, dict) and "image_url" in message:
                image_url = message["image_url"]
                
                # 处理base64编码的图片
                if isinstance(image_url, str) and image_url.startswith("data:image"):
                    try:
                        # 解析base64图片
                        header, encoded = image_url.split(',', 1)
                        image_data = base64.b64decode(encoded)
                        original_size_mb = get_image_size_mb(image_data)
                        
                        print(f"[线程{thread_id}] 原始图片大小: {original_size_mb:.2f}MB，目标: {target_size_mb}MB")
                        
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        
                        # 如果已经小于目标大小，直接返回
                        if original_size_mb <= target_size_mb:
                            print(f"[线程{thread_id}] 图片已满足大小要求，无需调整")
                            modified_messages.append(message)
                            continue
                        
                        # 动态调整过程（最多10次）
                        current_image = image
                        current_width, current_height = width, height
                        
                        for attempt in range(10):
                            # 根据当前大小与目标大小的比例计算缩放比例
                            buffer = io.BytesIO()
                            image_format = 'JPEG' if 'jpeg' in header.lower() or 'jpg' in header.lower() else 'PNG'
                            
                            temp_image = current_image
                            if image_format == 'JPEG':
                                temp_image = temp_image.convert('RGB')
                            
                            temp_image.save(buffer, format=image_format, quality=85)
                            current_size_mb = get_image_size_mb(buffer.getvalue())
                            
                            print(f"[线程{thread_id}] 第{attempt+1}次检查: {current_width}x{current_height}, {current_size_mb:.2f}MB")
                            
                            if current_size_mb <= target_size_mb:
                                print(f"[线程{thread_id}] 达到目标大小，调整完成")
                                break
                            
                            # 动态计算缩放比例
                            size_ratio = current_size_mb / target_size_mb
                            if size_ratio > 5:
                                scale_factor = 0.4  # 超过5倍，大幅缩小
                            elif size_ratio > 3:
                                scale_factor = 0.5  # 超过3倍，中等缩小
                            elif size_ratio > 2:
                                scale_factor = 0.7  # 超过2倍，适度缩小
                            else:
                                scale_factor = 0.85  # 轻微超过，小幅缩小
                                
                            print(f"[线程{thread_id}] 当前{current_size_mb:.2f}MB超过目标{target_size_mb}MB（倍数:{size_ratio:.2f})，缩放比例: {scale_factor}")
                            
                            new_width = int(current_width * scale_factor)
                            new_height = int(current_height * scale_factor)
                            
                            # 最小尺寸保护
                            if new_width < 100 or new_height < 100:
                                print(f"[线程{thread_id}] 达到最小尺寸限制，停止调整")
                                break
                                
                            current_image = current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            current_width, current_height = new_width, new_height
                        
                        # 最终编码
                        buffer = io.BytesIO()
                        final_image = current_image
                        if image_format == 'JPEG':
                            final_image = final_image.convert('RGB')
                        
                        final_image.save(buffer, format=image_format, quality=85)
                        buffer.seek(0)
                        
                        final_size_mb = get_image_size_mb(buffer.getvalue())
                        new_encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        new_image_url = f"{header},{new_encoded}"
                        
                        print(f"[线程{thread_id}] 图片从 {width}x{height}({original_size_mb:.2f}MB) 调整至 {current_width}x{current_height}({final_size_mb:.2f}MB)")
                        
                        # 创建新的message
                        new_message = message.copy()
                        new_message["image_url"] = new_image_url
                        modified_messages.append(new_message)
                        
                    except Exception as resize_error:
                        print(f"[线程{thread_id}] 图片缩放失败: {resize_error}")
                        modified_messages.append(message)  # 如果缩放失败，使用原图片
                else:
                    modified_messages.append(message)  # 非base64图片，保持原样
            else:
                modified_messages.append(message)  # 非图片消息，保持原样
        
        return modified_messages
    
    for attempt in range(max_retries):
        try:
            # 修复messages格式，确保符合Friday API要求
            if isinstance(messages, list) and len(messages) > 0:
                for message in messages:
                    if isinstance(message, dict) and "image_url" in message:
                        # 将image_url从顶层移动到content数组中
                        content = message.get("content", "")
                        image_urls = message.pop("image_url", [])
                        
                        # 构建Friday API兼容的格式
                        if isinstance(image_urls, list):
                            # 如果有多个图片，只使用第一个
                            if len(image_urls) > 0:
                                message["image_url"] = image_urls[0]
                        elif isinstance(image_urls, str):
                            message["image_url"] = image_urls
                        
                        # 确保content是字符串
                        if not isinstance(content, str):
                            message["content"] = str(content)
            
            return llm_client.vision_request(messages, model, max_tokens=max_tokens, temperature=temperature)
            
        except Exception as e:
            error_str = str(e)
            
            # 检测是否为图片大小超限错误
            if ("image exceeds" in error_str and "MB maximum" in error_str) or \
               ("图片超过" in error_str and "MB" in error_str) or \
               ("too large" in error_str.lower() and "image" in error_str.lower()) or \
               ("At least one of the image dimensions exceed max allowed size" in error_str) or \
               ("8000 pixels" in error_str):
                
                print(f"[线程{thread_id}] 检测到图片大小超限错误，尝试缩小图片: {error_str}")
                
                # 动态确定目标大小，每次重试逐渐降低目标
                target_sizes = [3.5, 3.0, 2.5, 2.0, 1.5]  # MB
                target_size_mb = target_sizes[min(attempt, len(target_sizes) - 1)]
                
                try:
                    messages = handle_image_size_error(messages, target_size_mb)
                    print(f"[线程{thread_id}] 图片已动态调整，目标大小: {target_size_mb}MB, 重试第 {attempt + 1} 次")
                    continue
                except Exception as resize_error:
                    print(f"[线程{thread_id}] 图片缩放处理失败: {resize_error}")
                    # 如果缩放失败，继续按原逻辑处理
            
            if attempt < max_retries - 1:
                # 添加随机延迟避免并发冲突
                actual_delay = retry_delay + random.uniform(0, 2)
                print(f"[线程{thread_id}] Rate limit exceeded, waiting {actual_delay:.1f} seconds before retry... Error: {e}")
                time.sleep(actual_delay)
                continue
            print(f"[线程{thread_id}] 最终重试失败: {e}")
            raise e



def get_best_grid_shape(n, min_cols=2, max_cols=3):
    import math
    best_rows, best_cols = n, 1
    min_diff = n
    for cols in range(min_cols, max_cols+1):
        rows = math.ceil(n / cols)
        diff = abs(rows - cols)
        if rows * cols >= n and diff < min_diff:
            best_rows, best_cols = rows, cols
            min_diff = diff
    return best_rows, best_cols

def create_voting_image_grid(segment_dir, candidate_frames, max_single_size=600, label_height=40):
    """
    为voting方法创建紧凑型图片网格：左红框、右蓝框，中间候选帧，画布自适应，无多余空白，图片最大化。
    """
    import math
    from PIL import Image, ImageDraw, ImageFont
    if not candidate_frames:
        return None
        
    # 读取action_info.json获取视频总帧数
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    
    first_frame = load_frame_from_npy(segment_dir, 0)
    last_frame = load_frame_from_npy(segment_dir, num_frames - 1)  # 使用视频的最后一帧
    if first_frame is None or last_frame is None:
        print("无法加载第一帧或最后一帧")
        return None
    total_images = 2 + len(candidate_frames)
    
    rows, cols = get_best_grid_shape(total_images)
    # 计算单张图片最大尺寸（不超过max_single_size）
    cell_width = cell_height = max_single_size
    # 计算画布实际需要的大小
    canvas_width = cols * cell_width
    canvas_height = rows * (cell_height + label_height)
    grid_image = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
    draw = ImageDraw.Draw(grid_image)
    try:
        font = ImageFont.truetype("Arial", 20)
    except:
        font = ImageFont.load_default()
    for i in range(total_images):
        row = i // cols
        col = i % cols
        # 最后一行居中
        if row == rows - 1:
            last_row_count = total_images - (rows - 1) * cols
            offset_x = (canvas_width - last_row_count * cell_width) // 2 if last_row_count < cols else 0
        else:
            offset_x = 0
        x = col * cell_width + offset_x
        y = row * (cell_height + label_height)
        # 选取图片
        if i == 0:
            img = first_frame
            border_color = (255, 0, 0)
            label = "Frame 0 (Start)"
            label_color = (255, 0, 0)
        elif i == total_images - 1:
            img = last_frame
            border_color = (0, 0, 255)
            label = "Last Frame (End)"  # 修改：去掉帧号，只显示描述
            label_color = (0, 0, 255)
        else:
            idx = candidate_frames[i - 1]
            img = load_frame_from_npy(segment_dir, idx)
            border_color = (200, 200, 200)
            label = f"{idx}"
            label_color = (0, 0, 0)
        if img is None:
            continue
        # 保持比例最大化填满cell
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        padding = 4 # 控制图片和边框的间距
        if aspect_ratio > 1:
            new_width = cell_width - padding
            new_height = int(new_width / aspect_ratio)
            if new_height > cell_height - padding:
                new_height = cell_height - padding
                new_width = int(new_height * aspect_ratio)
        else:
            new_height = cell_height - padding
            new_width = int(new_height * aspect_ratio)
            if new_width > cell_width - padding:
                new_width = cell_width - padding
                new_height = int(new_width / aspect_ratio)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        bordered_img = Image.new('RGB', (cell_width, cell_height), border_color)
        paste_x = (cell_width - new_width) // 2
        paste_y = (cell_height - new_height) // 2
        bordered_img.paste(resized_img, (paste_x, paste_y))
        grid_image.paste(bordered_img, (x, y))
        # 标签
        if label:
            text_width = draw.textlength(label, font=font)
            text_x = x + (cell_width - text_width) // 2
            text_y = y + cell_height + 5
            draw.text((text_x, text_y), label, fill=label_color, font=font)
    # 顶部说明
    title = "Page Loading Analysis Grid"
    title_width = draw.textlength(title, font=font)
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 10), title, fill=(0, 0, 0), font=font)
    
    return grid_image



# UI推断相关函数已移动到 llm_ui_infer.py 文件中
from .llm_ui_infer import get_ui_infer_with_retry

from .llm_ui_infer import extract_mask_regions_from_ui_infer


def merge_overlapping_regions(mask_regions, image_width, image_height):
    """
    合并重叠的遮蔽区域
    
    Args:
        mask_regions: 遮蔽区域列表
        image_width: 图像宽度
        image_height: 图像高度
    
    Returns:
        list: 合并后的遮蔽区域列表
    """
    if not mask_regions:
        return []
    
    # 按照顶部位置排序
    sorted_regions = sorted(mask_regions, key=lambda r: r['coordinates'][1])
    merged = []
    
    for current_region in sorted_regions:
        current_coords = current_region['coordinates']
        x1, y1, x2, y2 = current_coords
        
        # 检查是否与已有区域重叠
        merged_with_existing = False
        for i, existing_region in enumerate(merged):
            existing_coords = existing_region['coordinates']
            ex1, ey1, ex2, ey2 = existing_coords
            
            # 检查是否有重叠或相邻
            if (x1 <= ex2 + 10 and x2 >= ex1 - 10 and 
                y1 <= ey2 + 10 and y2 >= ey1 - 10):
                
                # 合并区域
                new_x1 = min(x1, ex1)
                new_y1 = min(y1, ey1)
                new_x2 = max(x2, ex2)
                new_y2 = max(y2, ey2)
                
                # 更新现有区域
                merged[i]['coordinates'] = [new_x1, new_y1, new_x2, new_y2]
                merged[i]['class_name'] = f"merged_{existing_region['class_name']}_{current_region['class_name']}"
                merged[i]['mask_reason'] = f"合并区域: {existing_region['mask_reason']} + {current_region['mask_reason']}"
                
                print(f"    [Merge] Merged regions: {existing_coords} + {current_coords} = {[new_x1, new_y1, new_x2, new_y2]}")
                merged_with_existing = True
                break
        
        if not merged_with_existing:
            merged.append(current_region)
    
    return merged


def draw_ui_inferences_on_image(image, recognize_results, mask_regions=None):
    """
    Draw UI inference results on a PIL image.
    
    Args:
        image: PIL Image object
        recognize_results: UI inference recognition results list
        mask_regions: List of mask regions (deprecated, kept for compatibility)
    """
    from PIL import ImageDraw, ImageFont
    import random
    
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        try:
            font = ImageFont.load_default(size=12)
        except:
            font = ImageFont.load_default()

    unique_labels = list(set([r.get('cls_name', 'N/A') for r in recognize_results]))
    colors = {label: (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)) for label in unique_labels}

    # Create a set of mask region coordinates for faster lookup
    mask_coords = set()
    if mask_regions:
        print(f"  [Debug] Processing {len(mask_regions)} mask regions:")
        for i, region in enumerate(mask_regions):
            coords = region['coordinates']
            print(f"    Region {i+1}: {coords} (type: {type(coords)})")
            
            # Note: Coordinates can be in list or tuple format
            if isinstance(coords, (list, tuple)) and len(coords) == 4:
                mask_coords.add(tuple(coords))
            elif isinstance(coords, dict):
                mask_coords.add((coords['left'], coords['top'], coords['right'], coords['bottom']))
        print(f"  [Debug] Created mask_coords set with {len(mask_coords)} regions: {mask_coords}")

    print(f"  [Debug] Drawing {len(recognize_results)} UI components:")
    
    for i, recognition in enumerate(recognize_results):
        box = recognition.get('elem_det_region')
        label = recognition.get('cls_name', 'N/A')
        
        # Check if box exists and is in the correct format
        if not box or len(box) != 4:
            print(f"    [Skip] Component {i+1}: '{label}' invalid box data {box}")
            continue
        
        print(f"    Component {i+1}: {label} at {box}")
        
        # Check if the current box is a mask region
        box_tuple = tuple(box)
        is_mask_region = box_tuple in mask_coords
        
        print(f"      Checking if {box_tuple} in mask_coords...")
        
        # If direct match fails, try fuzzy match with a small tolerance
        if not is_mask_region and mask_regions:
            for mask_coords_tuple in mask_coords:
                mx1, my1, mx2, my2 = mask_coords_tuple
                if (abs(box[0] - mx1) <= 5 and abs(box[1] - my1) <= 5 and 
                    abs(box[2] - mx2) <= 5 and abs(box[3] - my2) <= 5):
                    print(f"      Found fuzzy match: {box_tuple} ~= {mask_coords_tuple}")
                    is_mask_region = True
                    break
        
        if is_mask_region:
            # Mask regions are marked with green thick frames
            color = (0, 255, 0)  # Green
            width = 8  # Thicker frame
            
            print(f"    [Green] Drawing green box for {label} at {box}")
            
            draw.rectangle([box[0], box[1], box[2], box[3]], outline=color, width=width)
            
            # Add label indicating this is a scrolling region
            text_position = (box[0] + 5, box[1] + 5)
            draw.text(text_position, f"{label} (Scrolling region)", fill=color, font=font)
        else:
            # Other UI components are marked with random colors
            color = colors.get(label, (255, 0, 0))
            
            draw.rectangle([box[0], box[1], box[2], box[3]], outline=color, width=3)
            
            text_position = (box[0] + 5, box[1] + 5)
            draw.text(text_position, label, fill=color, font=font)
        
    return image

def create_voting_image_grid_with_ui_infer(segment_dir, candidate_frames, horus_client, max_single_size=2400, label_height=50, ui_infer_max_retries=3, ui_infer_retry_delay=2, grid_cache=None, processed_frames_cache=None, remove_background=False, enable_global_screen_rect=False, frame_dir=None, start_frame_mode=False):
    """
    Create a compact image grid for voting: each image retains its original size, and the canvas size is dynamically calculated.
    Each image is accompanied by UI-infer component recognition results and automatically masks regions wider than 70%.
    Supports UI inference request retry mechanism for improved stability.
    Supports grid cache and processed frames cache for efficiency.
    Supports background removal and difference detection features.
    Supports global screen region uniform cropping feature.
    
    Args:
        start_frame_mode: If True, adds first frame (frame 0) as reference with red border.
                         If False, adds last frame as reference with blue border (default behavior).
    """
    from PIL import Image, ImageDraw, ImageFont

    if not candidate_frames:
        return None
        
    # Initialize cache
    if grid_cache is None:
        grid_cache = {}
    if processed_frames_cache is None:
        processed_frames_cache = {}
    
    # Check grid cache
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    
    cache_key = (tuple(sorted(candidate_frames)), num_frames, max_single_size, label_height, remove_background, enable_global_screen_rect, frame_dir, start_frame_mode)
    if cache_key in grid_cache:
        print(f"  [Grid-Cache] Using cached grid, candidate frames: {candidate_frames}")
        return grid_cache[cache_key]
        
    print(f"  [Grid-Cache] Cache miss, generating new grid, candidate frames: {candidate_frames}")
    
    # Global screen region detection
    global_screen_rect = None
    if enable_global_screen_rect:
        print(f"  [Global-Screen] Enabling global screen region detection")
        try:
            from toolchain_llm.service.ui_detection.img_diff import get_global_screen_rect
            if start_frame_mode:
                all_frames = [0] + list(candidate_frames)  # First frame + candidate frames
            else:
                all_frames = list(candidate_frames) + [num_frames - 1]  # Candidate frames + last frame
            global_screen_rect = get_global_screen_rect(segment_dir, all_frames)
            print(f"  [Global-Screen] Detected global screen region: {global_screen_rect}")
        except Exception as e:
            print(f"  [Global-Screen] Global screen region detection failed: {e}")
            enable_global_screen_rect = False
    
    memoized_frames = {}
    def get_frame_with_ui_infer(frame_idx):
        # First check global cache
        if frame_idx in processed_frames_cache:
            print(f"  [Frame-Cache] Using cached processed frame: {frame_idx}")
            return processed_frames_cache[frame_idx]
        
        print(f"  [Frame-Cache] Cache miss, processing new frame: {frame_idx}")

        img_pil = load_frame(segment_dir, frame_idx, frame_dir)
        if img_pil is None:
            return None
        
        # If background removal is enabled
        if remove_background:
            print(f"  [Background-Removal] Starting to remove background from frame {frame_idx}")
            
            # Create temporary directory for image processing
            temp_dir = os.path.join(segment_dir, "temp_rembg")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save original image
            original_path = os.path.join(temp_dir, f"frame_{frame_idx}_original.png")
            img_pil.save(original_path)
            
            # Use rembg to remove background, extract phone part
            print(f"  [Background-Removal] Using rembg to remove background")
            removed_bg_path = remove_background_with_rembg(original_path)
            
            if removed_bg_path and os.path.exists(removed_bg_path):
                # Load the cropped image
                removed_bg_img = Image.open(removed_bg_path)
                print(f"  [Background-Removal] Background removal successful, new size: {removed_bg_img.size}")
                img_pil = removed_bg_img
            else:
                print(f"  [Background-Removal] rembg cropping failed, using original image")
        
        # Create RGB version for UI inference (UI inference requires RGB format)
        img_np = np.array(img_pil.convert('RGB'))
        img_np_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        ui_infer_result = get_ui_infer_with_retry(horus_client, img_np_bgr, cls_thresh=0, max_retries=ui_infer_max_retries, retry_delay=ui_infer_retry_delay, frame_info=f"frame {frame_idx}")
        
        # Keep the original image's transparent background
        processed_img = img_pil
        if ui_infer_result.get('code') == 0:
            recognize_results = ui_infer_result.get('data', {}).get('recognize_results', [])
            if recognize_results:
                print(f"  [UI-Infer] Found {len(recognize_results)} components for frame {frame_idx}.")
                # Add debug output to display the structure of the first component
                if recognize_results:
                    first_result = recognize_results[0]
                    print(f"  [Debug] Sample component structure: {list(first_result.keys())}")
                    print(f"  [Debug] Sample component: {first_result}")
                
                    # Get image width and height for filtering
                    image_width, image_height = img_pil.size
                    
                    # Filter out UI components to mask
                    wide_regions = extract_mask_regions_from_ui_infer(
                        recognize_results, 
                        target_classes=['banner', 'advertisement', 'popup', 'ad', 'carousel', 'slider'],
                        image_width=image_width, 
                        image_height=image_height,
                        width_threshold=0.7  # Back to 70%
                    )
                    
                    print(f"  [UI-Infer] Frame {frame_idx}: Found {len(wide_regions)} components to mask.")
                    
                    # Physically mask these regions
                    processed_img = img_pil.copy()
                    if wide_regions:
                        from PIL import ImageDraw
                        draw = ImageDraw.Draw(processed_img)
                        for region in wide_regions:
                            coords = region['coordinates']
                            if isinstance(coords, list) and len(coords) == 4:
                                x1, y1, x2, y2 = coords
                            else:
                                x1, y1, x2, y2 = coords.get('left', 0), coords.get('top', 0), coords.get('right', 0), coords.get('bottom', 0)
                            
                            # Mask this region with black
                            draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
                            print(f"    [Mask] Physically masked region at ({x1}, {y1}, {x2}, {y2})")
                    
                    # No longer draw UI component boxes, just use the masked image
                    # processed_img = draw_ui_inferences_on_image(processed_img, recognize_results, mask_regions=None)
            else:
                print(f"  [UI-Infer] No components found for frame {frame_idx}.")
        else:
            print(f"  [UI-Infer] Failed for frame {frame_idx}. Code: {ui_infer_result.get('code')}, Msg: {ui_infer_result.get('msg')}")
        
        # Apply global screen region cropping
        if enable_global_screen_rect and global_screen_rect is not None:
            try:
                print(f"  [Global-Screen] Applying global screen region cropping to frame {frame_idx}: {global_screen_rect}")
                # Convert to numpy array for cropping
                img_np = np.array(processed_img.convert('RGB'))
                x1, y1, x2, y2 = global_screen_rect
                # Ensure coordinates are within image range
                h, w = img_np.shape[:2]
                x1 = max(0, min(x1, w))
                y1 = max(0, min(y1, h))
                x2 = max(x1, min(x2, w))
                y2 = max(y1, min(y2, h))
                
                if x2 > x1 and y2 > y1:
                    cropped_np = img_np[y1:y2, x1:x2]
                    processed_img = Image.fromarray(cropped_np)
                    print(f"  [Global-Screen] Frame {frame_idx} cropped, new size: {processed_img.size}")
                else:
                    print(f"  [Global-Screen] Frame {frame_idx} cropping region invalid, keeping original size")
            except Exception as e:
                print(f"  [Global-Screen] Frame {frame_idx} cropping failed: {e}")
        
        # Cache processed frame
        processed_frames_cache[frame_idx] = processed_img
        return processed_img

    # Adopt the excellent layout strategy from the final grid
    total_images = len(candidate_frames) + 1  # Candidate frames + reference frame
    
    # Pre-load all images to get original sizes (adopt final strategy)
    print("  [Voting] Pre-loading all images to get sizes...")
    all_images = []
    all_labels = []
    all_colors = []
    
    # For start frame mode, add first frame as reference (red border)
    # For end frame mode, add reference frame at the end
    if start_frame_mode:
        # Add first frame as reference
        first_img = get_frame_with_ui_infer(0)
        if first_img is not None:
            all_images.append(first_img)
            all_labels.append("Frame 0 (Start)")
            all_colors.append((255, 0, 0))  # Red border
    
    # Load candidate frames
    for frame_idx in candidate_frames:
        img = get_frame_with_ui_infer(frame_idx)
        if img is not None:
            all_images.append(img)
            all_labels.append(f"{frame_idx}")
            all_colors.append((200, 200, 200))
    
    # For end frame mode, add last frame as reference (blue border)
    if not start_frame_mode:
        last_img = get_frame_with_ui_infer(num_frames - 1)
        if last_img is not None:
            all_images.append(last_img)
            all_labels.append("Last Frame (End)")
            all_colors.append((0, 0, 255))  # Blue border
    
    if not all_images:
        print("No available images")
        return None
    
    total_images = len(all_images)
    rows = min(2, total_images)  # Max 2 rows
    cols = math.ceil(total_images / rows)  # Calculate cols based on rows
    
    # Use the adjusted size of the first image as the baseline (adopt final strategy)
    base_width, base_height = all_images[0].size
    margin = 12  # Increase image margin  
    padding = 4   # Keep inner padding
    label_height = 50  # Further increase label height to accommodate larger font
    
    # Dynamically calculate canvas size to optimize space usage (adopt final strategy)
    canvas_width = cols * (base_width + margin + padding * 2) + margin
    canvas_height = rows * (base_height + label_height + margin + padding * 2) + margin + 60  # Increase to 60px for larger titles
    
    grid_image = Image.new('RGB', (canvas_width, canvas_height), (240, 240, 240))
    draw = ImageDraw.Draw(grid_image)
    
    try:
        font = ImageFont.truetype("Arial", 50)  # Further increase frame number font
        title_font = ImageFont.truetype("Arial", 54)  # Further increase title font
    except:
        try:
            font = ImageFont.load_default(size=50)
            title_font = ImageFont.load_default(size=54)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
    
    # Adopt the fine layout strategy from the final grid to draw each image
    if start_frame_mode:
        title = "Start Frame Analysis Grid (with UI Detections)"
        subtitle = f"Red: Reference Frame 0, Gray: Candidates ({len(candidate_frames)}), Total: {total_images}"
    else:
        title = "Page Loading Analysis Grid (with UI Detections)"
        subtitle = f"Voting candidates: {len(candidate_frames)}, Total frames: {total_images}"
    
    title_width = draw.textlength(title, font=title_font)
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 5), title, fill=(0, 0, 0), font=title_font)
    
    subtitle_width = draw.textlength(subtitle, font=font)
    subtitle_x = (canvas_width - subtitle_width) // 2
    draw.text((subtitle_x, 25), subtitle, fill=(100, 100, 100), font=font)
    
    # Draw each image (adopt final strategy)
    for i in range(total_images):
        row = i // cols
        col = i % cols
        
        # Calculate image position, including padding
        x = col * (base_width + margin + padding * 2) + margin + padding
        y = row * (base_height + label_height + margin + padding * 2) + 60 + padding  # Leave space for larger title
        
        img = all_images[i]
        label = all_labels[i]
        border_color = all_colors[i]
        label_color = all_colors[i] if all_colors[i] != (200, 200, 200) else (0, 0, 0)  # Black text for gray border
        
        print(f"  [Voting] Drawing image {i+1}/{total_images}: {label} at ({x}, {y}) adjusted size({img.size[0]}x{img.size[1]})")
        
        # Add white background and border
        bg_x, bg_y = x - padding, y - padding
        bg_width, bg_height = img.size[0] + padding * 2, img.size[1] + padding * 2
        draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], fill=(255, 255, 255), outline=border_color, width=3)
        
        # Paste the resized image
        grid_image.paste(img, (x, y))
        
        # Draw label (directly display frame number, no box)
        if label:
            text_width = draw.textlength(label, font=font)
            text_x = x + (img.size[0] - text_width) // 2
            text_y = y + img.size[1] + 5  # Reduce gap with image
            
            # Directly draw black text, no background box
            draw.text((text_x, text_y), label, fill=(0, 0, 0), font=font)
    

    

    
    # Cache the generated grid
    grid_cache[cache_key] = grid_image
    print(f"  [Grid-Cache] Grid cached, candidate frames: {candidate_frames}")
    
    return grid_image
    
    return grid_image


def llm_narrow_from_action_info_grid_voting_iterative_ui_infer(
    segment_dir,
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
    check_last_frame_loading=False,
    ui_infer_max_retries=3,
    ui_infer_retry_delay=2,
    frame_dir=None
):
    """
    基于grid with voting的迭代细化函数, 并在拼图前进行UI组件识别
    投票选出答案后，逐步缩小搜索范围，最终得到精确答案
    支持根据UI推断结果自动遮蔽指定区域
    
    Args:
        segment_dir: 视频片段目录
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
        check_last_frame_loading: 是否预先判断结尾帧是否加载完成，默认False
        ui_infer_max_retries: UI推断最大重试次数，默认3次
        ui_infer_retry_delay: UI推断重试间隔（秒），默认2秒
        frame_dir: 帧图片目录路径，如果为None则从npy文件加载，否则从指定目录加载
    
    Returns:
        dict: 包含最终结果、遮蔽信息和所有迭代过程的详细信息
    """
    import math
    from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
    from .llm_narrow_utils import load_frame
    
    print(f"开始迭代细化voting方法处理 (带UI-Infer): {segment_dir}")
    
    # 导入录制类型检测模块
    from .recording_type_detector import detect_recording_type, should_enable_background_removal
    
    # 检测录制类型并决定是否启用背景移除
    print("=== 开始录制类型检测 ===")
    recording_type_result = detect_recording_type(segment_dir, llm_client, model, frame_dir=frame_dir)
    
    # 根据录制类型判断是否启用背景移除
    actual_remove_background = should_enable_background_removal(recording_type_result, remove_background)
    
    # 将录制类型检测结果保存到结果中
    recording_type_info = {
        "recording_type": recording_type_result.get("recording_type", "unknown"),
        "confidence": recording_type_result.get("confidence", 0.0),
        "reason": recording_type_result.get("reason", "无判断理由"),
        "key_features": recording_type_result.get("key_features", []),
        "analyzed_frame": recording_type_result.get("analyzed_frame", -1),
        "actual_remove_background": actual_remove_background,
        "user_remove_background_param": remove_background
    }
    
    print(f"=== 录制类型检测完成 ===")
    print(f"录制类型: {recording_type_info['recording_type']}")
    print(f"置信度: {recording_type_info['confidence']:.2f}")
    print(f"背景移除: {'启用' if actual_remove_background else '禁用'}")
    
    # 1. 读取 action_info.json 和初始化
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    fps = action_info["extraction_parameters"]["fps"]
    
    # 1.5. 如果启用了结尾帧加载检查，先判断结尾帧是否加载完成
    if check_last_frame_loading:
        print("=== 开始预先检查结尾帧是否加载完成 ===")
        last_frame_idx = num_frames - 1
        
        # 加载结尾帧
        last_frame = load_frame(segment_dir, last_frame_idx, frame_dir)
        if last_frame is None:
            print(f"警告: 无法加载结尾帧 {last_frame_idx}")
        else:
            # 保存结尾帧为临时图片，先进行预缩放以避免API限制
            temp_dir = os.path.join(segment_dir, "temp_last_frame_check")
            os.makedirs(temp_dir, exist_ok=True)
            last_frame_path = os.path.join(temp_dir, f"last_frame_{last_frame_idx}.png")
            
            # 预缩放图片以避免API限制
            original_size = last_frame.size
            max_dimension = 1200  # 限制最大尺寸为1200像素
            
            if original_size[0] > max_dimension or original_size[1] > max_dimension:
                # 计算缩放比例
                scale = min(max_dimension / original_size[0], max_dimension / original_size[1])
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                print(f"预缩放结尾帧图片: {original_size} -> {new_size} (缩放比例: {scale:.2f})")
                last_frame = last_frame.resize(new_size, Image.Resampling.LANCZOS)
            
            last_frame.save(last_frame_path)
            
            # 检测和调整保存后的文件大小，使用更小的目标大小避免API限制
            last_frame_path = check_and_resize_saved_image(last_frame_path, max_file_size_mb=1.5, min_file_size_mb=0.5)
            
            # 构建结尾帧加载检查的prompt
                        # 构建严格的结尾帧加载检查的prompt
            last_frame_prompt = (
                f"You are a strict page loading completion analyzer. Your task is to determine if this webpage frame shows a COMPLETELY loaded page with ALL necessary UI elements present and functional.\n\n"
                f"## Action Description: {action_desc}\n"
                f"## Current Frame Number: {last_frame_idx}\n\n"
                f"## STRICT LOADING COMPLETION CRITERIA:\n"
                f"A page is ONLY considered fully loaded when ALL of the following conditions are met:\n\n"
                f"1. **NO Loading Indicators**: No spinners, progress bars, loading text, or animated loading elements visible\n"
                f"2. **Complete Navigation**: All navigation elements (tabs, menus, buttons) are visible and properly styled\n"
                f"3. **Full Content Display**: All expected content areas are populated with actual content (not placeholders)\n"
                f"4. **Image Completion**: All images are fully loaded with no broken image icons or placeholders\n"
                f"5. **Layout Stability**: Page layout is stable and matches the expected final state\n"
                f"6. **Interactive Elements**: All buttons, links, and interactive elements are properly rendered\n"
                f"7. **Text Rendering**: All text content is properly formatted and readable\n"
                f"8. **No Empty Areas**: No large blank/white areas where content should be visible\n"
                f"9. **Consistent Styling**: All elements have consistent and complete styling\n"
                f"10. **Functional Appearance**: The page appears ready for user interaction\n\n"
                f"## CRITICAL ANALYSIS POINTS:\n"
                f"- Look for ANY signs of incomplete loading\n"
                f"- Check if ALL expected UI components are present\n"
                f"- Verify that no content areas are empty or showing placeholders\n"
                f"- Ensure navigation elements are fully functional\n"
                f"- Confirm that images and media are completely loaded\n"
                f"- Check for any loading-related text or indicators\n\n"
                f"## Please analyze this frame and provide your assessment:\n\n"
                f"Please answer in JSON format:\n"
                f"{{\n"
                f"    \"is_fully_loaded\": true/false,\n"
                f"    \"visible_content\": \"Description of what content is visible\",\n"
                f"    \"loading_issues\": \"Description of loading problems (if any)\",\n"
                f"    \"missing_elements\": \"List any critical elements that appear to be missing or incomplete\",\n"
                f"    \"reason\": \"Detailed reasoning for the judgment\",\n"
                f"    \"confidence\": \"High/Medium/Low - confidence in this assessment\"\n"
                f"}}\n\n"
                f"## IMPORTANT NOTES:\n"
                f"- Be EXTREMELY strict in your assessment\n"
                f"- If there is ANY doubt about complete loading, mark as false\n"
                f"- Only mark as true if you are completely confident the page is fully loaded\n"
                f"- Consider the context of the action being performed when determining what elements should be present"
            )
            
            try:
                messages = [{"role": "user", "content": last_frame_prompt, "image_url": [last_frame_path]}]
                last_frame_response = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
                
                # 解析LLM响应
                try:
                    # 尝试直接解析JSON
                    response_json = json.loads(last_frame_response)
                except json.JSONDecodeError:
                    # 如果直接解析失败，尝试从markdown代码块中提取
                    pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                    match = re.search(pattern, last_frame_response)
                    if match:
                        response_json = json.loads(match.group(1))
                    else:
                        print("无法解析LLM响应，假设结尾帧未加载完成")
                        response_json = {"is_fully_loaded": False}
                
                is_fully_loaded = response_json.get("is_fully_loaded", False)
                
                if not is_fully_loaded:
                    print(f"结尾帧 {last_frame_idx} 未完全加载，直接返回结尾帧作为结束帧")
                    print(f"LLM判断理由: {response_json.get('reason', '无')}")
                    print(f"可见内容: {response_json.get('visible_content', '无描述')}")
                    
                    # 清理临时文件
                    try:
                        os.remove(last_frame_path)
                        os.rmdir(temp_dir)
                    except: pass
                    
                    return {
                        "segment_dir": segment_dir,
                        "final_end_frame": last_frame_idx,
                        "iteration_results": [],
                        "last_frame_check_result": {
                            "is_fully_loaded": True,
                            "llm_response": last_frame_response,
                            "visible_content": response_json.get("visible_content", "无描述"),
                            "reason": response_json.get("reason", "无")
                        },
                        "early_return_reason": "结尾帧已完全加载"
                    }
                else:
                    print(f"结尾帧 {last_frame_idx} 完全加载，继续正常流程")
                    print(f"LLM判断理由: {response_json.get('reason', '无')}")
                    if response_json.get("loading_issues"):
                        print(f"加载问题: {response_json.get('loading_issues')}")
                
                # 清理临时文件
                try:
                    os.remove(last_frame_path)
                    os.rmdir(temp_dir)
                except: pass
                
            except Exception as e:
                print(f"结尾帧加载检查过程中出错: {e}")
                print("继续正常流程")
        
        print("=== 结尾帧加载检查完成 ===")
    
    experiment_dir = os.path.join(segment_dir, f"experiment_iterative_voting_ui_infer_{int(time.time())}_{threading.current_thread().ident}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    horus_client = ClientHorus()
    
    # 全局缓存：缓存生成的拼图和处理过的帧
    grid_cache = {}  # 缓存拼图: key=candidate_frames_tuple, value=grid_image
    processed_frames_cache = {}  # 缓存处理过的帧: key=frame_idx, value=processed_image
    
    # 统一的prompt模板
    base_prompt = (
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
    

    
    base_prompt += (
        f"Please answer in JSON format:\n"
        f"{{\n"
        f"    \"frame_analysis\": [\n"
        f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame by ##Pay atttention to and #Ignoring\"}},\n"
        f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame by ##Pay atttention to and #Ignoring\"}},\n"
        f"        // ... continue for all frames\n"
        f"    ],\n"
        f"    \"target_frame\": <frame_number>,\n"
        f"    \"reason\": \"Detailed explanation of why this frame is the end frame,and why the others are not.\"\n"
        f"}}"
    )

    # 2. 获取初始候选帧
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    if not os.path.exists(ssim_pt_path):
        raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_dir}")
    
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    end_candidates = get_candidate_frames_for_end(
        cleaned_ssim_data, smoothed_ssim, slopes, start_frame,
        activity_threshold=activity_threshold,
        merge_window=merge_window,
        end_threshold=end_threshold
    )
    
    # 3. 使用相似度方法过滤候选帧
    def filter_candidates_by_similarity(candidates, last_frame_idx):
        if not candidates: return candidates
        last_frame = load_frame(segment_dir, last_frame_idx, frame_dir)
        if last_frame is None: return candidates
        
        filtered_candidates = []
        found_perfect_similarity = False
        for candidate_idx in candidates:
            if found_perfect_similarity: continue
            candidate_frame = load_frame(segment_dir, candidate_idx, frame_dir)
            if candidate_frame is None: continue
            
            temp_dir = os.path.join(segment_dir, "temp_similarity")
            os.makedirs(temp_dir, exist_ok=True)
            candidate_path = os.path.join(temp_dir, f"candidate_{candidate_idx}.png")
            last_path = os.path.join(temp_dir, f"last_{last_frame_idx}.png")
            candidate_frame.save(candidate_path)
            last_frame.save(last_path)
            
            img1 = cv2.imread(candidate_path)
            img2 = cv2.imread(last_path)
            
            try:
                ocr_result = get_ocr_result(img1, img2)
                img_diff_obj = ImageDiff(img1, img2, ocr_result, struct_score_thresh=0.99)
                score = img_diff_obj.get_similar_score([])
                if score == 1.0:
                    filtered_candidates.append(candidate_idx)
                    found_perfect_similarity = True
                else:
                    filtered_candidates.append(candidate_idx)
            except Exception:
                filtered_candidates.append(candidate_idx)
            
            try:
                os.remove(candidate_path)
                os.remove(last_path)
            except: pass
        try: os.rmdir(temp_dir)
        except: pass
        return filtered_candidates
    
    filtered_end_candidates = filter_candidates_by_similarity(end_candidates, num_frames - 1)
    if not filtered_end_candidates:
        filtered_end_candidates = end_candidates

    # 3.5. 候选帧数量控制机制
    # 如果候选帧大于7张，计算使候选帧数量≤7所需的最小合并窗口
    max_candidates = 7
    target_candidates = 7
    
    print(f"初始候选帧数量: {len(filtered_end_candidates)}")
    
    if len(filtered_end_candidates) > max_candidates:
        print(f"候选帧数量 {len(filtered_end_candidates)} > {max_candidates}，计算所需的最小合并窗口")
        
        # 计算候选帧之间的最小间距
        sorted_candidates = sorted(filtered_end_candidates)
        min_gaps = []
        for i in range(len(sorted_candidates) - 1):
            gap = sorted_candidates[i + 1] - sorted_candidates[i]
            min_gaps.append(gap)
        
        if min_gaps:
            min_gaps.sort()
            # 计算需要合并多少对相邻候选帧来达到目标数量
            pairs_to_merge = len(filtered_end_candidates) - target_candidates
            
            # 选择最小的gaps作为合并窗口的参考
            if pairs_to_merge > 0 and pairs_to_merge <= len(min_gaps):
                # 使用第pairs_to_merge小的gap作为合并窗口
                required_merge_window = min_gaps[pairs_to_merge - 1] + 1
                # 确保合并窗口至少比原始窗口大
                required_merge_window = max(required_merge_window, merge_window + 2)
            else:
                # 如果需要合并的对数太多，使用较大的合并窗口
                avg_gap = sum(min_gaps) // len(min_gaps) if min_gaps else merge_window + 2
                required_merge_window = max(avg_gap, merge_window + 2)
            
            print(f"候选帧间距分析: {min_gaps[:10]}{'...' if len(min_gaps) > 10 else ''}")
            print(f"计算得出所需合并窗口: {required_merge_window}")
            
            # 直接对现有的候选帧按照合并窗口进行采样
            def merge_candidates_by_window(candidates, merge_window):
                """按照合并窗口对候选帧进行采样"""
                if not candidates:
                    return candidates
                
                sorted_candidates = sorted(candidates)
                merged = []
                current_group = [sorted_candidates[0]]
                
                for i in range(1, len(sorted_candidates)):
                    if sorted_candidates[i] - current_group[-1] <= merge_window:
                        current_group.append(sorted_candidates[i])
                    else:
                        # 选择组中的最后一个（最新的）帧
                        merged.append(current_group[-1])
                        current_group = [sorted_candidates[i]]
                
                if current_group:
                    merged.append(current_group[-1])
                
                return merged
            
            new_filtered_candidates = merge_candidates_by_window(filtered_end_candidates, required_merge_window)
            
            if new_filtered_candidates and len(new_filtered_candidates) <= target_candidates:
                filtered_end_candidates = new_filtered_candidates
                current_merge_window = required_merge_window
                print(f"使用合并窗口 {required_merge_window} 对现有候选帧进行采样后，候选帧数量: {len(filtered_end_candidates)}")
            else:
                print(f"警告: 使用合并窗口 {required_merge_window} 采样后仍有 {len(new_filtered_candidates) if new_filtered_candidates else 0} 个候选帧，保持原始候选帧")
                current_merge_window = merge_window
        else:
            print("无法计算候选帧间距，保持原始候选帧")
            current_merge_window = merge_window
    else:
        current_merge_window = merge_window
    
    print(f"最终候选帧数量: {len(filtered_end_candidates)}，使用的合并窗口: {current_merge_window}")



    # 5. 开始迭代细化过程
    iteration_results = []
    current_candidates = filtered_end_candidates.copy()
    current_window_size = 200
    min_window_size = 10
    iteration_count = 0
    max_iterations = 10
    while current_window_size >= min_window_size and iteration_count < max_iterations:
        iteration_count += 1
        print(f"\n=== 第{iteration_count}次迭代 (UI-Infer)，窗口大小: {current_window_size} ===")
        
        iteration_dir = os.path.join(experiment_dir, f"iteration_{iteration_count:03d}")
        os.makedirs(iteration_dir, exist_ok=True)
        
        current_best_frame = None
        response = None
        voting_results = None
        all_voting_details = None

        # Helper function to parse LLM response
        def parse_llm_response(response_text, valid_candidates):
            try:
                # First try to parse the whole string as JSON
                resp_json = json.loads(response_text)
                target_frame = resp_json.get("target_frame")
                if target_frame in valid_candidates:
                    return target_frame
            except json.JSONDecodeError:
                # If that fails, try to extract from markdown code block
                pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                match = re.search(pattern, response_text)
                if match:
                    try:
                        resp_json = json.loads(match.group(1))
                        target_frame = resp_json.get("target_frame")
                        if target_frame in valid_candidates:
                            return target_frame
                    except json.JSONDecodeError:
                        return None
            return None

        if iteration_count == 1:
            print("  第一次迭代，使用voting方法...")
            
            # 检查候选帧数量，如果只有一个候选帧，直接选择它
            if len(current_candidates) == 1:
                current_best_frame = current_candidates[0]
                print(f"  只有一个候选帧 {current_best_frame}，直接选择")
                response = f"只有一个候选帧，直接选择: {current_best_frame}"
                voting_results = {current_best_frame: 1}
                all_voting_details = [{"round": 1, "selected_frame": current_best_frame, "llm_results": response, "method": "direct_selection"}]
            else:
                voting_results = {}
                all_voting_details = []
                
                for round_num in range(1, max_voting_rounds + 1):
                    print(f"    第{round_num}轮投票...")
                    end_grid = create_voting_image_grid_with_ui_infer(segment_dir, current_candidates, horus_client, max_single_size=1000, label_height=80, ui_infer_max_retries=ui_infer_max_retries, ui_infer_retry_delay=ui_infer_retry_delay, grid_cache=grid_cache, processed_frames_cache=processed_frames_cache, remove_background=actual_remove_background, frame_dir=frame_dir)
                    
                    if not end_grid:
                        print("    没有可用的候选图片, 无法创建网格")
                        break
                
                grid_path = os.path.join(iteration_dir, f"grid_round_{round_num}.png")
                end_grid.save(grid_path)
                
                # 检测和调整保存后的文件大小
                grid_path = check_and_resize_saved_image(grid_path, max_file_size_mb=3.5)
                
                end_prompt = base_prompt

                try:
                    messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                    response = llm_vision_request_with_retry(llm_client, messages, max_tokens=4096, model=model)
                    
                    refined_end_frame = parse_llm_response(response, current_candidates)
                     
                    if refined_end_frame is not None:
                        voting_results[refined_end_frame] = voting_results.get(refined_end_frame, 0) + 1
                        all_voting_details.append({"round": round_num, "selected_frame": refined_end_frame, "llm_results": response})
                        
                        # 判断是否可以结束投票
                        should_break = False
                        if voting_results[refined_end_frame] >= 2:
                                print(f"    第{round_num}轮: 帧 {refined_end_frame} 获得 {voting_results[refined_end_frame]} 票，投票结束")
                                should_break = True
                        
                        if should_break:
                            break
                    else:
                        all_voting_details.append({"round": round_num, "selected_frame": None, "llm_results": response, "error": "Invalid response or frame selection"})
                         
                except Exception as e:
                    print(f"    第{round_num}轮投票过程中出错: {e}")
                    all_voting_details.append({"round": round_num, "selected_frame": None, "error": str(e)})
            
            # 投票结束后，确定获胜的帧
            if voting_results:
                # 找到得票最多的帧
                current_best_frame = max(voting_results.items(), key=lambda x: x[1])[0]
                print(f"  投票结束，获胜帧: {current_best_frame} (得票: {voting_results[current_best_frame]})")
                
                # 生成投票汇总响应，用于保存迭代结果
                response = f"投票轮次完成。最终获胜帧: {current_best_frame}，得票数: {voting_results[current_best_frame]}。详细投票结果: {dict(voting_results)}"
            else:
                current_best_frame = None
                print("  投票结束，没有有效结果")
                response = "投票轮次完成，但没有获得有效的投票结果。"

        else: # Subsequent iterations
            print("  后续迭代，使用单次LLM推理...")
            end_grid = create_voting_image_grid_with_ui_infer(segment_dir, current_candidates, horus_client, max_single_size=1000, label_height=80, ui_infer_max_retries=ui_infer_max_retries, ui_infer_retry_delay=ui_infer_retry_delay, grid_cache=grid_cache, processed_frames_cache=processed_frames_cache, remove_background=actual_remove_background, frame_dir=frame_dir)
            if not end_grid:
                print("    无法创建网格图片")
                break
            
            grid_path = os.path.join(iteration_dir, f"grid_single.png")
            end_grid.save(grid_path)
            
            # 检测和调整保存后的文件大小
            grid_path = check_and_resize_saved_image(grid_path, max_file_size_mb=3.5)
            
            end_prompt = base_prompt
            
            try:
                messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                response = llm_vision_request_with_retry(llm_client, messages, max_tokens=2048, model=model)
                current_best_frame = parse_llm_response(response, current_candidates)
            except Exception as e:
                print(f"  LLM推理过程中出错: {e}")

            if current_best_frame is None:
                if current_candidates:
                    current_best_frame = current_candidates[len(current_candidates)//2]
                    print("  LLM未返回有效结果，使用候选帧中间值")
                else:
                    break

                # 保存迭代结果
        iteration_result = {
            "iteration": iteration_count,
            "candidates": current_candidates.copy(),
            "best_frame": current_best_frame,
            "method": "voting" if iteration_count == 1 else "single",
            "llm_response": response if 'response' in locals() else None,
            "voting_results": voting_results,
            "voting_details": all_voting_details if all_voting_details else None,
            "window_size": current_window_size
        }
        iteration_results.append(iteration_result)
        
        # 保存当前迭代结果到JSON文件
        with open(os.path.join(iteration_dir, "iteration_result.json"), "w", encoding="utf-8") as f:
            json.dump(iteration_result, f, indent=4, ensure_ascii=False)
        
        print(f"第{iteration_count}次迭代完成，选中帧: {current_best_frame}")
        print(f"当前候选帧范围: {current_candidates[0]}-{current_candidates[-1]} (共{len(current_candidates)}帧)")
        
        # 第二次迭代后的退出机制
        if iteration_count >= 2:
            # 当候选帧数量降到很少时停止
            if current_window_size <= min_window_size:
                print(f"  窗口大小已达到最小值 {min_window_size}，停止迭代")
                break
        
        
        # 根据当前最佳帧缩小候选范围，重新按窗口获取候选帧
        if current_best_frame is not None:
            # 以current_best_frame为中心，定义新的搜索范围
            new_left = max(0, current_best_frame - current_window_size // 2)
            new_right = min(num_frames - 1, current_best_frame + current_window_size // 2)
            
            print(f"  以帧{current_best_frame}为中心，在范围[{new_left}, {new_right}]中重新获取候选帧...")
            
            current_candidates = None
            # 如果窗口内没有找到候选帧，就在窗口范围内按间隔采样
            if not current_candidates:
                print(f"  窗口内未找到SSIM候选帧，按间隔采样...")
                step = max(1, current_window_size // 4)  # 在窗口内采样5个左右的帧
                current_candidates = list(range(new_left, new_right + 1, step))
                # 删除以下行：
                # current_candidates = [c for c in current_candidates if c >= action_frame]
            
            print(f"  窗口内新候选帧: {current_candidates} (共{len(current_candidates)}帧)")
            
            # 缩小窗口大小
            current_window_size = max(min_window_size, current_window_size // 2)
        else:
            print("当前迭代未找到有效的最佳帧，停止迭代")
            break
    
    # 6. 最终投票：将所有迭代的最佳帧进行投票
    print(f"\n=== 最终投票阶段 ===")
    
    # 收集所有迭代的最佳帧
    all_best_frames = [result["best_frame"] for result in iteration_results if result["best_frame"] is not None]
    
    if not all_best_frames:
        print("没有找到任何有效的最佳帧")
        return {
            "segment_dir": segment_dir,
            "final_end_frame": None,
            "iteration_results": iteration_results,
            "error": "没有找到任何有效的最佳帧"
        }
    
    # 添加尾帧
    final_candidates = all_best_frames + [num_frames - 1]
    final_candidates = list(set(final_candidates))  # 去重
    final_candidates.sort()
    
    print(f"最终候选帧: {final_candidates}")
    
    # 创建最终网格
    final_grid = create_final_iterative_grid_with_ui_infer(segment_dir, final_candidates, iteration_results, horus_client, ui_infer_max_retries, ui_infer_retry_delay, grid_cache, processed_frames_cache, remove_background=actual_remove_background, frame_dir=frame_dir)
    
    # 初始化最终结果变量
    final_end_frame = None
    final_voting_results = None
    final_voting_details = None
    final_llm_response = None

    # 如果只有一个唯一的候选帧（除了最后的参考帧），就直接选它
    if len(final_candidates) <= 2:
        candidate_frame = -1
        for frame in final_candidates:
            if frame != num_frames - 1:
                candidate_frame = frame
                break
        
        if candidate_frame != -1:
            final_end_frame = candidate_frame
            final_llm_response = None
            print(f"最终候选帧只有一个有效选项 {final_end_frame}，直接采纳为最终结果。")
        elif final_candidates:
            final_end_frame = final_candidates[0]
            final_llm_response = None
            print(f"最终候选帧只有最后一帧 {final_end_frame}，直接采纳为最终结果。")
        else:
             final_end_frame = all_best_frames[-1] if all_best_frames else None
             final_llm_response = None
    elif final_grid:
        final_voting_results = {}
        final_voting_details = []
        final_llm_response = None
        
        final_grid_path = os.path.join(experiment_dir, f"final_grid_{threading.current_thread().ident}.png")
        final_grid.save(final_grid_path)
        
        # 检测和调整保存后的文件大小
        final_grid_path = check_and_resize_saved_image(final_grid_path, max_file_size_mb=3.5)
        
        final_prompt = base_prompt
        
        for round_num in range(1, max_voting_rounds + 1):
            print(f"  最终投票第{round_num}轮...")
            try:
                messages = [{"role": "user", "content": final_prompt, "image_url": [final_grid_path]}]
                final_response = llm_vision_request_with_retry(
                    llm_client,
                    messages,
                    max_tokens=2048,
                    model=model
                )
                
                selected_frame = None
                max_retries_for_position = 3
                retry_count = 0
                
                while retry_count < max_retries_for_position:
                    try:
                        resp_json = json.loads(final_response)
                        if "target_frame" in resp_json:
                            target_frame = resp_json["target_frame"]
                            # 验证选择的是否为候选帧（不是参考帧）
                            if target_frame in all_best_frames:
                                selected_frame = target_frame
                                print(f"    第{round_num}轮选择帧: {selected_frame}")
                                break
                            else:
                                print(f"    第{round_num}轮选择了无效帧 {target_frame}（不是候选帧），重试...")
                                retry_count += 1
                                if retry_count < max_retries_for_position:
                                    messages = [{"role": "user", "content": final_prompt, "image_url": [final_grid_path]}]
                                    final_response = llm_vision_request_with_retry(llm_client, messages, max_tokens=2048, model=model)
                                    continue
                                else:
                                    print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                    selected_frame = None
                                    break
                    except:
                        pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                        match = re.search(pattern, final_response)
                        if match:
                            try:
                                resp_json = json.loads(match.group(1))
                                if "target_frame" in resp_json:
                                    target_frame = resp_json["target_frame"]
                                    if target_frame in all_best_frames:
                                        selected_frame = target_frame
                                        print(f"    第{round_num}轮选择帧: {selected_frame}")
                                        break
                                    else:
                                        print(f"    第{round_num}轮选择了无效帧 {target_frame}（不是候选帧），重试...")
                                        retry_count += 1
                                        if retry_count < max_retries_for_position:
                                            messages = [{"role": "user", "content": final_prompt, "image_url": [final_grid_path]}]
                                            final_response = llm_vision_request_with_retry(llm_client, messages, max_tokens=2048, model=model)
                                            continue
                                        else:
                                            print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                            selected_frame = None
                                            break
                            except:
                                print(f"    第{round_num}轮解析JSON失败")
                                break
                        else:
                            print(f"    第{round_num}轮LLM未返回有效结果")
                            break

                if selected_frame is not None:
                    if selected_frame not in final_voting_results:
                        final_voting_results[selected_frame] = 0
                    final_voting_results[selected_frame] += 1
                    
                    voting_detail = {
                        "round": round_num,
                        "selected_frame": selected_frame,
                        "llm_results": final_response,
                        "current_vote_count": final_voting_results[selected_frame],
                        "retry_count": retry_count
                    }
                    final_voting_details.append(voting_detail)
                    
                    if final_voting_results[selected_frame] >= 2:
                        print(f"    帧 {selected_frame} 获得了 {final_voting_results[selected_frame]} 票，达到投票要求")
                        final_llm_response = final_response
                        break
                else:
                    final_voting_details.append({"round": round_num, "selected_frame": None, "llm_results": final_response, "error": "LLM未返回有效结果"})
                
            except Exception as e:
                final_voting_details.append({"round": round_num, "selected_frame": None, "llm_results": None, "error": str(e)})
                print(f"  最终投票第{round_num}轮出错: {e}")
        
        if final_voting_results:
            final_end_frame = max(final_voting_results.items(), key=lambda x: x[1])[0]
            max_votes = final_voting_results[final_end_frame]
            print(f"\n最终投票结果: {final_voting_results}")
            print(f"最终选择帧: {final_end_frame} (获得 {max_votes} 票)")
            
            # 找到最终选择帧对应的LLM响应
            for detail in final_voting_details:
                if detail["selected_frame"] == final_end_frame:
                    final_llm_response = detail["llm_results"]
                    break
            
            if final_llm_response:
                print(f"最终选择帧 {final_end_frame} 对应的LLM响应已找到")
            else:
                print(f"警告：未找到最终选择帧 {final_end_frame} 对应的LLM响应")
        else:
            print("最终投票未获得任何有效结果，使用候选帧中间值")
            if all_best_frames:
                final_end_frame = all_best_frames[len(all_best_frames)//2]
                print(f"使用候选帧中间值作为最终结果: {final_end_frame}")
                final_llm_response = None
            else:
                print("没有候选帧可用")
                final_end_frame = None
                final_llm_response = None

        if final_end_frame is None:
            final_end_frame = all_best_frames[len(all_best_frames)//2] if all_best_frames else None

        # 生成最终结果
        result = {
            "segment_dir": segment_dir,
            "final_end_frame": final_end_frame,
            "final_llm_response": final_llm_response if 'final_llm_response' in locals() else None,
            "iteration_results": iteration_results,
            "final_candidates": final_candidates,
            "final_voting_results": final_voting_results if 'final_voting_results' in locals() else {},
            "final_voting_details": final_voting_details if 'final_voting_details' in locals() else [],
            "experiment_dir": experiment_dir,
            "recording_type_info": recording_type_info if 'recording_type_info' in locals() else {},
            "evaluation": {}
        }
        
        # 保存最终结果到JSON文件
        with open(os.path.join(experiment_dir, "final_result.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        if do_evaluation:
            print("\n=== 开始评估 ===")
            action_info_path = os.path.join(segment_dir, "action_info.json")
            with open(action_info_path, "r", encoding="utf-8") as f:
                action_info = json.load(f)
            
            marked_end_time = action_info["original_action_item"]["marked_end_time"]
            extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
            fps = action_info["extraction_parameters"]["fps"]
            gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
            gt_end_frame = max(0, gt_end_frame)
            
            if final_end_frame is not None:
                diff_end = abs(final_end_frame - gt_end_frame)
                evaluation_result = {
                    "gt_end_frame": gt_end_frame,
                    "pred_end_frame": final_end_frame,
                    "diff_end": diff_end,
                    "accuracy": "perfect" if diff_end == 0 else "close" if diff_end < 10 else "mid" if diff_end < 20 else "other"
                }
                result["evaluation"] = evaluation_result
                print(f"评估完成: {evaluation_result}")
            else:
                print("没有找到预测结果，跳过评估")

        return result

    


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
    直接使用文件夹中的图片，不创建任何视频文件
    模仿 llm_narrow_from_action_info_grid_voting_iterative_ui_infer 的完整流程
    """
    import math
    import time
    import threading
    from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
    from .llm_narrow_utils import load_frame
    
    print(f"开始UI infer开始帧检测（图片文件夹）: {frame_dir}")
    
    # 1. 创建临时段目录结构，模拟 segment_dir
    import tempfile
    import os
    import shutil
    
    temp_segment_dir = tempfile.mkdtemp(prefix="start_frame_segment_")
    print(f"临时段目录: {temp_segment_dir}")
    
    try:
        # 2. 获取图片文件列表
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
        
        # 3. 创建action_info.json文件（模拟）
        action_info = {
            "original_action_item": {
                "action_desc": "开始帧检测",
                "action_time": 0.0,
                "marked_start_time": 0.0,
                "marked_end_time": len(frame_files) / fps if fps > 0 else 0.0
            },
            "extraction_parameters": {
                "num_extracted_frames": len(frame_files),
                "fps": fps,
                "extract_start_time_sec": 0.0
            }
        }
        
        action_info_path = os.path.join(temp_segment_dir, "action_info.json")
        with open(action_info_path, "w", encoding="utf-8") as f:
            json.dump(action_info, f, indent=2, ensure_ascii=False)
        
        print(f"开始迭代细化voting方法处理 (带UI-Infer): {temp_segment_dir}")
        
        # 4. 导入录制类型检测模块并进行检测
        from .recording_type_detector import detect_recording_type, should_enable_background_removal
        
        print("=== 开始录制类型检测 ===")
        recording_type_result = detect_recording_type(temp_segment_dir, llm_client, model, frame_dir=frame_dir)
        
        # 根据录制类型判断是否启用背景移除
        actual_remove_background = should_enable_background_removal(recording_type_result, remove_background)
        
        # 将录制类型检测结果保存到结果中
        recording_type_info = {
            "recording_type": recording_type_result.get("recording_type", "unknown"),
            "confidence": recording_type_result.get("confidence", 0.0),
            "reason": recording_type_result.get("reason", "无判断理由"),
            "key_features": recording_type_result.get("key_features", []),
            "analyzed_frame": recording_type_result.get("analyzed_frame", -1),
            "actual_remove_background": actual_remove_background,
            "user_remove_background_param": remove_background
        }
        
        print(f"=== 录制类型检测完成 ===")
        print(f"录制类型: {recording_type_info['recording_type']}")
        print(f"置信度: {recording_type_info['confidence']:.2f}")
        print(f"背景移除: {'启用' if actual_remove_background else '禁用'}")
        
        # 5. 创建实验目录
        experiment_dir = os.path.join(temp_segment_dir, f"experiment_iterative_voting_ui_infer_{int(time.time())}_{threading.current_thread().ident}")
        os.makedirs(experiment_dir, exist_ok=True)
        
        horus_client = ClientHorus()
        
        # 全局缓存：缓存生成的拼图和处理过的帧
        grid_cache = {}  # 缓存拼图: key=candidate_frames_tuple, value=grid_image
        processed_frames_cache = {}  # 缓存处理过的帧: key=frame_idx, value=processed_image
        
        # 6. 统一的prompt模板（专门用于开始帧检测）
        base_prompt = (
            f"You are a helpful assistant and an expert in start frame analysis. Your task is to identify the FIRST frame in the grid that shows the initial visible change after a user operation (e.g., click, tap, scroll) on a web or app page.\n\n"
            f"Below is a grid of frames from a video showing the page loading or transition process. The frames are arranged from left to right, top to bottom.\n\n"
            f"## Frame Types in Grid:\n"
            f"1. **Reference Frame (Red Border)**: Frame 0 - the initial state before any user operation\n"
            f"2. **Candidate Frames (Gray Borders)**: Numbered frames - potential start frames after the operation\n\n"
            f"## Context:\n"
            f"- The user has just performed an operation (e.g., click, tap, scroll).\n"
            f"- Each frame is a snapshot of the page after the operation.\n"
            f"- Your goal is to find the first frame where the page starts to change in response to the operation.\n"
            f"- Compare each candidate frame with the red-bordered reference frame (Frame 0) to detect changes.\n\n"
            f"## Definition of start frame:\n"
            f"1. The start frame is the FIRST frame that shows any visible change or reaction after the user operation compared to Frame 0.\n"
            f"2. Changes may include: button color change, loading indicator appearing, page content starting to update, new UI elements appearing, animations starting, etc.\n"
            f"3. Ignore minor flickers, background animation, or non-essential UI changes that are not related to the main operation.\n"
            f"4. The change should be a direct result of the user action, not random or unrelated animation.\n\n"
            f"## Task:\n"
            f"- Compare each candidate frame (gray borders) with the reference Frame 0 (red border).\n"
            f"- Carefully analyze each candidate frame and describe the changes you observe compared to Frame 0.\n"
            f"- Pay special attention to:\n"
            f"  - Button or UI element color/state changes\n"
            f"  - Loading indicators or spinners appearing\n"
            f"  - New content or images starting to load\n"
            f"  - Any visible feedback that the operation has triggered a response\n"
            f"- Ignore:\n"
            f"  - Minor background animation\n"
            f"  - Floating system buttons or overlays not related to the operation\n"
            f"  - Small text scrolling or ticker effects\n\n"
            f"## IMPORTANT:\n"
            f"- You must choose ONLY from the candidate frames (gray borders). Do NOT select the reference frame (red border).\n"
            f"- Be precise: select the earliest candidate frame that shows a clear, operation-related change compared to Frame 0.\n"
            f"- If no candidate frame shows visible changes, select the earliest candidate frame.\n\n"
        )
        
        base_prompt += (
            f"Please answer in JSON format:\n"
            f"{{\n"
            f"    \"frame_analysis\": [\n"
            f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame by ##Pay atttention to and #Ignoring\"}},\n"
            f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame by ##Pay atttention to and #Ignoring\"}},\n"
            f"        // ... continue for all frames\n"
            f"    ],\n"
            f"    \"target_frame\": <frame_number>,\n"
            f"    \"reason\": \"Detailed explanation of why this frame is the start frame,and why the others are not.\"\n"
            f"}}"
        )

        # 7. 获取初始候选帧（使用类似 get_candidate_frames_for_start 的方法）
        # 对于开始帧检测，我们需要找到波动点，然后找它们前面的稳定点作为候选帧
        
        print("计算帧间SSIM数据用于候选帧选择...")
        
        # 计算帧间SSIM数据
        import cv2
        from skimage.metrics import structural_similarity as ssim
        import pandas as pd
        
        ssim_pt_path = os.path.join(frame_dir, "ssim_sequence.pt")
        if not os.path.exists(ssim_pt_path):
            raise FileNotFoundError(f"ssim_sequence.pt not found in {frame_dir}")
        
        raw_ssim_data_tensor = torch.load(ssim_pt_path)
        raw_ssim_data_list = raw_ssim_data_tensor.tolist()
        cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
        
        # 计算平滑SSIM和斜率
        ssim_series = pd.Series(cleaned_ssim_data)
        smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
        slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])

        from .llm_narrow_utils import get_candidate_frames_for_start
        
        try:
            # 找到开始帧候选帧（波动点前面的稳定点）
            candidate_frames, start_point_map = get_candidate_frames_for_start(
                cleaned_ssim_data, smoothed_ssim, slopes, 
                activity_threshold=activity_threshold,
                merge_window=merge_window,
                start_threshold=start_threshold
            )
            
            print(f"基于SSIM分析的候选帧: {candidate_frames}")
            print(f"候选帧映射: {start_point_map}")
            
        except Exception as e:
            print(f"使用get_candidate_frames_for_start时出错: {e}")
            # 降级到简单策略
            candidate_frames = []
            early_frames_count = min(len(frame_files) // 3, 15)
            step = max(1, early_frames_count // 8)
            for i in range(0, early_frames_count, step):
                candidate_frames.append(i)
            
            # 确保包含第0帧
            if 0 not in candidate_frames:
                candidate_frames.insert(0, 0)
            
            candidate_frames = sorted(list(set(candidate_frames)))
        
        # 确保至少有5个候选帧
        if len(candidate_frames) < 5:
            for i in range(min(5, len(frame_files))):
                if i not in candidate_frames:
                    candidate_frames.append(i)
        
        candidate_frames = sorted(candidate_frames)
        
        print(f"开始帧检测初始候选帧: {candidate_frames}")

        # 7.5. 使用相似度方法过滤候选帧（与第一帧比较）
        def filter_candidates_by_similarity_start(candidates, first_frame_idx=0):
            """过滤候选帧，与第一帧进行相似度比较"""
            if not candidates: return candidates
            
            # 加载第一帧作为参考
            first_frame = load_frame(temp_segment_dir, first_frame_idx, frame_dir)
            if first_frame is None: 
                print("无法加载第一帧，跳过相似度过滤")
                return candidates
            
            filtered_candidates = []
            found_perfect_similarity = False
            
            for candidate_idx in candidates:
                if found_perfect_similarity: continue
                candidate_frame = load_frame(temp_segment_dir, candidate_idx, frame_dir)
                if candidate_frame is None: continue
                
                temp_dir = os.path.join(temp_segment_dir, "temp_similarity_start")
                os.makedirs(temp_dir, exist_ok=True)
                candidate_path = os.path.join(temp_dir, f"candidate_{candidate_idx}.png")
                first_path = os.path.join(temp_dir, f"first_{first_frame_idx}.png")
                candidate_frame.save(candidate_path)
                first_frame.save(first_path)
                
                img1 = cv2.imread(candidate_path)
                img2 = cv2.imread(first_path)
                
                try:
                    from ..toolchain_llm.service.ui_detection.line_feature_diff import get_ocr_result
                    from ..toolchain_llm.service.ui_detection.img_diff import ImageDiff
                    
                    ocr_result = get_ocr_result(img1, img2)
                    img_diff_obj = ImageDiff(img1, img2, ocr_result, struct_score_thresh=0.99)
                    score = img_diff_obj.get_similar_score([])
                    if score == 1.0:
                        filtered_candidates.append(candidate_idx)
                        found_perfect_similarity = True
                    else:
                        filtered_candidates.append(candidate_idx)
                except Exception as e:
                    print(f"相似度比较出错 (帧{candidate_idx}): {e}")
                    filtered_candidates.append(candidate_idx)
                
                try:
                    os.remove(candidate_path)
                    os.remove(first_path)
                except: pass
            
            try: os.rmdir(temp_dir)
            except: pass
            
            return filtered_candidates
        
        filtered_start_candidates = filter_candidates_by_similarity_start(candidate_frames, 0)
        if not filtered_start_candidates:
            filtered_start_candidates = candidate_frames
            print("相似度过滤后无候选帧，使用原始候选帧")
        else:
            print(f"相似度过滤后候选帧: {filtered_start_candidates}")

        # 7.6. 候选帧数量控制机制
        max_candidates = 7
        target_candidates = 7
        
        print(f"初始候选帧数量: {len(filtered_start_candidates)}")
        
        if len(filtered_start_candidates) > max_candidates:
            print(f"候选帧数量 {len(filtered_start_candidates)} > {max_candidates}，计算所需的最小合并窗口")
            
            # 计算候选帧之间的最小间距
            sorted_candidates = sorted(filtered_start_candidates)
            min_gaps = []
            for i in range(len(sorted_candidates) - 1):
                gap = sorted_candidates[i + 1] - sorted_candidates[i]
                min_gaps.append(gap)
            
            if min_gaps:
                min_gaps.sort()
                # 计算需要合并多少对相邻候选帧来达到目标数量
                pairs_to_merge = len(filtered_start_candidates) - target_candidates
                
                # 选择最小的gaps作为合并窗口的参考
                if pairs_to_merge > 0 and pairs_to_merge <= len(min_gaps):
                    # 使用第pairs_to_merge小的gap作为合并窗口
                    required_merge_window = min_gaps[pairs_to_merge - 1] + 1
                    # 确保合并窗口至少比原始窗口大
                    required_merge_window = max(required_merge_window, merge_window + 2)
                else:
                    # 如果需要合并的对数太多，使用较大的合并窗口
                    avg_gap = sum(min_gaps) // len(min_gaps) if min_gaps else merge_window + 2
                    required_merge_window = max(avg_gap, merge_window + 2)
                
                print(f"候选帧间距分析: {min_gaps[:10]}{'...' if len(min_gaps) > 10 else ''}")
                print(f"计算得出所需合并窗口: {required_merge_window}")
                
                # 直接对现有的候选帧按照合并窗口进行采样
                def merge_candidates_by_window_start(candidates, merge_window):
                    """按照合并窗口对候选帧进行采样（开始帧检测版本）"""
                    if not candidates:
                        return candidates
                    
                    sorted_candidates = sorted(candidates)
                    merged = []
                    current_group = [sorted_candidates[0]]
                    
                    for i in range(1, len(sorted_candidates)):
                        if sorted_candidates[i] - current_group[-1] <= merge_window:
                            current_group.append(sorted_candidates[i])
                        else:
                            # 对于开始帧检测，选择组中的第一个（最早的）帧
                            merged.append(current_group[0])
                            current_group = [sorted_candidates[i]]
                    
                    if current_group:
                        merged.append(current_group[0])
                    
                    return merged
                
                new_filtered_candidates = merge_candidates_by_window_start(filtered_start_candidates, required_merge_window)
                
                if new_filtered_candidates and len(new_filtered_candidates) <= target_candidates:
                    filtered_start_candidates = new_filtered_candidates
                    current_merge_window = required_merge_window
                    print(f"使用合并窗口 {required_merge_window} 对现有候选帧进行采样后，候选帧数量: {len(filtered_start_candidates)}")
                else:
                    print(f"警告: 使用合并窗口 {required_merge_window} 采样后仍有 {len(new_filtered_candidates) if new_filtered_candidates else 0} 个候选帧，保持原始候选帧")
                    current_merge_window = merge_window
            else:
                print("无法计算候选帧间距，保持原始候选帧")
                current_merge_window = merge_window
        else:
            current_merge_window = merge_window
        
        print(f"最终候选帧数量: {len(filtered_start_candidates)}，使用的合并窗口: {current_merge_window}")
        
        # 更新候选帧为过滤后的结果
        candidate_frames = filtered_start_candidates

        # 8. 开始迭代细化过程
        iteration_results = []
        current_candidates = candidate_frames.copy()
        current_window_size = 200
        min_window_size = 10
        iteration_count = 0
        max_iterations = 10
        
        while current_window_size >= min_window_size and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n=== 第{iteration_count}次迭代 (UI-Infer)，窗口大小: {current_window_size} ===")
            
            iteration_dir = os.path.join(experiment_dir, f"iteration_{iteration_count:03d}")
            os.makedirs(iteration_dir, exist_ok=True)
            
            current_best_frame = None
            response = None
            
            # Helper function to parse LLM response
            def parse_llm_response(response_text, valid_candidates):
                try:
                    # First try to parse the whole string as JSON
                    resp_json = json.loads(response_text)
                    target_frame = resp_json.get("target_frame")
                    if target_frame in valid_candidates:
                        return target_frame
                except json.JSONDecodeError:
                    # If that fails, try to extract from markdown code block
                    pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                    match = re.search(pattern, response_text)
                    if match:
                        try:
                            resp_json = json.loads(match.group(1))
                            target_frame = resp_json.get("target_frame")
                            if target_frame in valid_candidates:
                                return target_frame
                        except json.JSONDecodeError:
                            return None
                return None

            # 生成拼图并调用LLM
            print(f"  使用候选帧: {current_candidates}")
            start_grid = create_voting_image_grid_with_ui_infer(
                temp_segment_dir, 
                current_candidates, 
                horus_client, 
                max_single_size=1000, 
                label_height=80, 
                ui_infer_max_retries=ui_infer_max_retries, 
                ui_infer_retry_delay=ui_infer_retry_delay, 
                grid_cache=grid_cache, 
                processed_frames_cache=processed_frames_cache, 
                remove_background=actual_remove_background, 
                frame_dir=frame_dir,
                start_frame_mode=True
            )
            
            if not start_grid:
                print("    无法创建网格图片")
                break
            
            grid_path = os.path.join(iteration_dir, f"grid_start_frame.png")
            start_grid.save(grid_path)
            
            # 检测和调整保存后的文件大小
            grid_path = check_and_resize_saved_image(grid_path, max_file_size_mb=3.5)
            
            try:
                messages = [{"role": "user", "content": base_prompt, "image_url": [grid_path]}]
                response = llm_vision_request_with_retry(llm_client, messages, max_tokens=2048, model=model, temperature=temperature)
                current_best_frame = parse_llm_response(response, current_candidates)
            except Exception as e:
                print(f"  LLM推理过程中出错: {e}")

            if current_best_frame is None:
                if current_candidates:
                    current_best_frame = current_candidates[0]  # 对于开始帧，选择最早的候选帧
                    print("  LLM未返回有效结果，使用最早候选帧")
                else:
                    break

            # 保存迭代结果
            iteration_result = {
                "iteration": iteration_count,
                "window_size": current_window_size,
                "candidates": current_candidates.copy(),
                "best_frame": current_best_frame,
                "grid_path": grid_path,
                "llm_response": response
            }
            iteration_results.append(iteration_result)
            
            print(f"  第{iteration_count}次迭代结果: 最佳帧 = {current_best_frame}")
            
            # 如果只剩下少数候选帧或者已经收敛，停止迭代
            if len(current_candidates) <= 3:
                print(f"  候选帧数量较少({len(current_candidates)})，停止迭代")
                break
            
            # 缩小搜索范围：围绕当前最佳帧创建新的候选帧窗口
            current_window_size = max(min_window_size, current_window_size // 2)
            
            # 为开始帧检测创建新的候选帧窗口
            window_start = max(0, current_best_frame - current_window_size // 2)
            window_end = min(len(frame_files) - 1, current_best_frame + current_window_size // 2)
            
            # 在窗口内生成新的候选帧
            new_candidates = []
            window_frames = list(range(window_start, window_end + 1))
            
            # 添加关键帧
            new_candidates.append(current_best_frame)
            
            # 添加窗口内的其他帧
            step = max(1, len(window_frames) // 8)
            for i in range(0, len(window_frames), step):
                frame_idx = window_frames[i]
                if frame_idx not in new_candidates:
                    new_candidates.append(frame_idx)
            
            # 确保至少有3个候选帧
            while len(new_candidates) < 3 and window_end < len(frame_files) - 1:
                window_end += 1
                if window_end not in new_candidates:
                    new_candidates.append(window_end)
            
            current_candidates = sorted(new_candidates)
            
            print(f"  下一轮候选帧: {current_candidates}")

        # 9. 构建最终结果
        final_start_frame = current_best_frame if current_best_frame is not None else (candidate_frames[0] if candidate_frames else 0)
        
        result = {
            "success": True,
            "start_frame": {
                'frame_number': final_start_frame,
                'timestamp': final_start_frame / fps if fps > 0 else 0,
                'method': 'ui_infer_iterative_start_frame'
            },
            "total_frames": len(frame_files),
            "candidates": candidate_frames,
            "iteration_results": iteration_results,
            "recording_type_info": recording_type_info,
            "final_iteration_count": iteration_count,
            "method_used": "ui_infer_iterative_start_frame_from_frames"
        }
        
        if do_evaluation:
            print(f"\n=== UI Infer开始帧检测结果（图片文件夹） ===")
            print(f"总帧数: {len(frame_files)}")
            print(f"录制类型: {recording_type_info['recording_type']} (置信度: {recording_type_info['confidence']:.2f})")
            print(f"背景移除: {'启用' if actual_remove_background else '禁用'}")
            print(f"初始候选帧: {candidate_frames}")
            print(f"迭代次数: {iteration_count}")
            print(f"最终开始帧: {final_start_frame}")
            print(f"时间戳: {final_start_frame / fps:.2f}s")
        
        return result
        
    except Exception as e:
        print(f"UI infer开始帧检测（图片文件夹）出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'UI infer开始帧检测出错: {str(e)}',
            'start_frame': None,
            'candidates': []
        }
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_segment_dir)
            print(f"已清理临时目录: {temp_segment_dir}")
        except Exception as e:
            print(f"清理临时目录失败: {e}")

def detect_android_by_first_frame(video_path, ocr_url="http://10.164.6.121:8417/paddelocr"):
    """
    通过第一帧OCR检测判断是否为安卓设备
    
    Args:
        video_path: 视频文件路径
        ocr_url: OCR服务URL
    
    Returns:
        bool: True表示安卓设备，False表示其他设备
    """
    import cv2
    import base64
    import requests
    
    def check_words(text):
        """检查文本中是否包含坐标信息"""
        import re
        pattern = re.compile(r'(?i)[xy][^a-z]*[1-9]\d*\.?\d*')
        match = pattern.search(text)
        return match is not None
    
    def call_ocr_service(image, url):
        """调用OCR服务"""
        try:
            # 将OpenCV的BGR格式转换为RGB格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 编码为JPEG格式
            _, buffer = cv2.imencode('.jpg', image_rgb)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 准备请求数据
            data = {'image': img_base64}
            
            # 发送请求
            response = requests.post(url, data=data, timeout=10)
            
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
    
    try:
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            return False
        
        # 读取第一帧
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("无法读取视频第一帧")
            return False
        
        # 调用OCR服务
        texts = call_ocr_service(frame, ocr_url)
        
        # 检查是否包含坐标信息
        for text in texts:
            if check_words(text):
                print(f"检测到坐标信息: {text}，判定为安卓设备")
                return True
        
        print("未检测到坐标信息，判定为非安卓设备")
        return False
        
    except Exception as e:
        print(f"检测设备类型时出错: {e}")
        return False  # 出错时默认为非安卓设备
    

def find_page_load_llm_comprehensive(frame_dir: str, fps: int):
    """
    融合多种算法的页面加载检测方法
    包括：
    1. 设备类型检测（安卓vs非安卓）
    2. 开始帧检测：OCR方案 + UI infer方案
    3. 结束帧检测：LLM narrow方案 + SSIM算法备用
    4. 智能结果融合
    
    参数:
        frame_dir: 包含图片帧的本地目录路径
        fps: 帧率
        
    返回:
        tuple: (开始帧, 结束帧)
    """
    import json
    import cv2
    import os
    import torch
    import pandas as pd
    import time
    import glob
    
    logger.info(f"[find_page_load_llm_comprehensive] 开始综合页面加载检测，帧目录: {frame_dir}, fps: {fps}")
    
    # 确保toolchain环境变量已设置（但不切换工作目录）
    if 'TOOLCHAIN_ROOT' in os.environ:
        logger.info(f"[find_page_load_llm_comprehensive] toolchain环境已设置: {os.environ['TOOLCHAIN_ROOT']}")
    else:
        logger.warning("[find_page_load_llm_comprehensive] toolchain环境变量未设置，可能影响LLM功能")
    
    # 1. 检查帧目录并获取帧信息
    expanded_frame_dir = os.path.expanduser(frame_dir)
    if not os.path.exists(expanded_frame_dir):
        logger.error(f"[find_page_load_llm_comprehensive] 帧目录不存在: {expanded_frame_dir}")
        return 0, 0
    
    # 获取所有帧文件
    frame_files = sorted(glob.glob(os.path.join(expanded_frame_dir, "frame_*.jpeg")))
    if not frame_files:
        logger.error(f"[find_page_load_llm_comprehensive] 未找到帧文件: {expanded_frame_dir}")
        return 0, 0
    
    num_frames = len(frame_files)
    logger.info(f"[find_page_load_llm_comprehensive] 找到 {num_frames} 个帧文件")
    
    # 读取第一帧获取尺寸信息
    first_frame = cv2.imread(frame_files[0])
    if first_frame is None:
        logger.error(f"[find_page_load_llm_comprehensive] 无法读取第一帧: {frame_files[0]}")
        return 0, 0
    
    frame_height, frame_width = first_frame.shape[:2]
    
    # 2. 创建固定的实验目录（不使用临时目录）
    experiment_base_dir = os.path.expanduser("~/llm_page_load_experiments")
    os.makedirs(experiment_base_dir, exist_ok=True)
    
    # 使用时间戳创建唯一的实验目录
    experiment_id = f"experiment_{int(time.time())}_{num_frames}frames"
    experiment_dir = os.path.join(experiment_base_dir, experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)
    
    logger.info(f"[find_page_load_llm_comprehensive] 使用实验目录: {experiment_dir}")
    
    # 执行检测算法
    return process_detection_algorithms(expanded_frame_dir, experiment_dir, num_frames, fps, frame_height, frame_width, frames=None)

def process_detection_algorithms(expanded_frame_dir, experiment_dir, num_frames, fps, frame_height, frame_width, frames=None):
    """处理检测算法的核心逻辑"""
    import json
    import cv2
    import os
    import torch
    import pandas as pd
    import time
    import glob
    
    logger.info(f"[process_detection_algorithms] 开始处理检测算法，帧目录: {expanded_frame_dir}, fps: {fps}")
    
    try:
        # 复制帧文件到实验目录（保持原有命名）
        import shutil
        frame_files = sorted(glob.glob(os.path.join(expanded_frame_dir, "frame_*.jpeg")))
        for frame_file in frame_files:
            frame_name = os.path.basename(frame_file)
            dest_path = os.path.join(experiment_dir, frame_name)
            shutil.copy2(frame_file, dest_path)
        
        # 3. 创建action_info.json文件
        action_info = {
            "original_action_item": {
                "action_desc": "页面加载检测",
                "action_time": 0.0,
                "marked_start_time": 0.0,
                "marked_end_time": num_frames / fps if fps > 0 else 0.0
            },
            "extraction_parameters": {
                "num_extracted_frames": num_frames,
                "fps": fps,
                "extract_start_time_sec": 0.0,
                "width": frame_width,
                "height": frame_height,
                "frame_shape": [frame_height, frame_width, 3],
                "dtype": "uint8"
            }
        }
        
        action_info_path = os.path.join(experiment_dir, "action_info.json")
        with open(action_info_path, "w", encoding="utf-8") as f:
            json.dump(action_info, f, indent=2, ensure_ascii=False)
        
        # 4. 计算并保存SSIM向量
        try:
            # 需要加载帧来计算SSIM
            frames = []
            for frame_file in frame_files:
                frame = cv2.imread(frame_file)
                if frame is not None:
                    frames.append(frame)
            
            if len(frames) != num_frames:
                logger.warning(f"[process_detection_algorithms] 部分帧加载失败，预期: {num_frames}, 实际: {len(frames)}")
           
            if len(frames) > 1:  # 至少需要2帧才能计算SSIM
                offsets = [1]
                ssim_vectors = calculate_temporal_ssim_vectors_mp(frames, offsets, convert_to_gray=True)
                
                # 检查ssim_vectors是否有效，并清理None值
                if ssim_vectors is not None and len(ssim_vectors) > 0:
                    # 将None值替换为0.0
                    cleaned_ssim_vectors = []
                    for frame_vector in ssim_vectors:
                        if isinstance(frame_vector, list):
                            cleaned_frame_vector = [0.0 if val is None else val for val in frame_vector]
                            cleaned_ssim_vectors.append(cleaned_frame_vector)
                        else:
                            cleaned_ssim_vectors.append([0.0])  # 备用默认值
                    
                    try:
                        ssim_tensor = torch.tensor(cleaned_ssim_vectors, dtype=torch.float32)
                        ssim_path = os.path.join(experiment_dir, "ssim_sequence.pt")
                        torch.save(ssim_tensor, ssim_path)
                        logger.info(f"[process_detection_algorithms] SSIM向量已保存: {ssim_path}")
                    except Exception as tensor_error:
                        logger.error(f"[process_detection_algorithms] SSIM张量创建失败: {tensor_error}")
                else:
                    logger.warning("[process_detection_algorithms] SSIM计算返回空结果")
            else:
                logger.warning("[process_detection_algorithms] 帧数不足，跳过SSIM计算")
        except Exception as e:
            logger.error(f"[process_detection_algorithms] SSIM计算失败: {e}")
        
        # 5. 开始帧检测 - 使用llm_narrow_start_frame_ocr_ultra_fast_from_frames（内部会自动判断设备类型）
        start_frame = None
        try:
            logger.info("[process_detection_algorithms] 开始开始帧检测...")
            
            # 导入必要模块
            from .test_ocr_ultra_fast import llm_narrow_start_frame_ocr_ultra_fast_from_frames
            from .llm_tools import LLMClient
            
            # 初始化LLM客户端
            llm_client = None
            try:
                llm_client = LLMClient()
                logger.info("[process_detection_algorithms] LLM客户端初始化成功")
            except Exception as e:
                logger.warning(f"[process_detection_algorithms] LLM客户端初始化失败: {e}")
            
            # 配置UI infer参数
            ui_infer_config = {
                "activity_threshold": -0.001,
                "merge_window": 3,
                "start_threshold": -0.0001,
                "end_threshold": -0.00003,
                "ssim_threshold": 0.995,
                "model": "anthropic.claude-3.7-sonnet",
                "max_voting_rounds": 10,
                "temperature": 0.1,
                "remove_background": True,
                "enable_diff": False,
                "ui_infer_max_retries": 3,
                "ui_infer_retry_delay": 2
            }
            
            # 直接调用开始帧检测算法（内部会自动判断设备类型）
            
            start_result = llm_narrow_start_frame_ocr_ultra_fast_from_frames(
                frame_dir=experiment_dir,
                llm_client=llm_client,
                do_evaluation=False,
                max_frames=num_frames,
                skip_frames=1,
                scale_factor=1,
                early_stop=True,
                save_frame_texts=True,
                ui_infer_config=ui_infer_config,
                fps=fps
            )
            # 修正：确保start_frame为int类型
            
            if isinstance(start_result, dict):
                start_frame = start_result.get("start_frame", 0)
            else:
                start_frame = start_result
            if isinstance(start_frame, dict):
                start_frame = start_frame.get("frame_index", 0)
            else:
                start_frame = start_frame
            logger.info(f"[process_detection_algorithms] 开始帧检测结果: {start_frame}")
            
        except ImportError as e:
            logger.error(f"[process_detection_algorithms] 导入模块失败: {e}")
        except Exception as e:
            logger.error(f"[process_detection_algorithms] 开始帧检测失败: {e}")
            
        # 6. 结束帧检测 - 使用LLM narrow方法
        end_frame = None
        logger.info("[process_detection_algorithms] 开始结束帧检测...")
        # 导入LLM narrow结束帧检测模块
        
        if llm_client is not None:
            # 调用LLM narrow结束帧检测算法
            end_result = llm_narrow_from_action_info_grid_voting_iterative_ui_infer(
                segment_dir=experiment_dir,
                llm_client=llm_client,
                do_evaluation=False,
                activity_threshold=-0.001,
                merge_window=3,
                start_threshold=-0.0001,
                end_threshold=-0.00003,
                ssim_threshold=0.995,
                model="anthropic.claude-3.7-sonnet",
                max_voting_rounds=10,
                temperature=0.1,
                remove_background=True,
                check_last_frame_loading=True,
                ui_infer_max_retries=3,
                ui_infer_retry_delay=2,
                frame_dir=experiment_dir  # 传递帧图片目录
            )
            end_frame = end_result.get("final_end_frame")
            logger.info(f"[process_detection_algorithms] 结束帧检测结果: {end_frame}")
        else:
            logger.warning("[process_detection_algorithms] LLM客户端不可用，跳过LLM narrow结束帧检测")
        
        
        # 7. 备用SSIM算法
        if start_frame is None or end_frame is None:
            logger.info("[process_detection_algorithms] 使用SSIM备用算法")
            try:
                if not frames:  # 如果之前没有加载帧，现在加载
                    frames = []
                    for frame_file in frame_files:
                        frame = cv2.imread(frame_file)
                        if frame is not None:
                            frames.append(frame)
                
                if len(frames) > 1:
                    offsets = [1] 
                    ssim_vectors = calculate_temporal_ssim_vectors_mp(frames, offsets, convert_to_gray=True)
                    
                    if ssim_vectors is not None and len(ssim_vectors) > 0:
                        # 清理None值
                        cleaned_ssim_vectors = []
                        for frame_vector in ssim_vectors:
                            if isinstance(frame_vector, list):
                                cleaned_frame_vector = [0.0 if val is None else val for val in frame_vector]
                                cleaned_ssim_vectors.append(cleaned_frame_vector)
                            else:
                                cleaned_ssim_vectors.append([0.0])
                        
                        clean_ssim_vectors = preprocess_ssim_data(cleaned_ssim_vectors)
                        ssim_start_frame, ssim_end_frame = find_page_load_intelligent(clean_ssim_vectors, fps=fps, plot_results=False)
                        
                        if start_frame is None:
                            start_frame = ssim_start_frame
                            logger.info(f"[process_detection_algorithms] 使用SSIM开始帧: {start_frame}")
                            
                        if end_frame is None:
                            end_frame = ssim_end_frame
                            logger.info(f"[process_detection_algorithms] 使用SSIM结束帧: {end_frame}")
                    else:
                        logger.warning("[process_detection_algorithms] SSIM备用算法计算失败")
                else:
                    logger.warning("[process_detection_algorithms] 帧数不足，跳过SSIM备用算法")
                    
            except Exception as e:
                logger.error(f"[process_detection_algorithms] SSIM备用算法失败: {e}")
        
        # 8. 结果验证和默认值
        if start_frame is None:
            start_frame = 0
            logger.warning("[process_detection_algorithms] 开始帧检测失败，使用默认值0")
            
        if end_frame is None:
            end_frame = num_frames - 1
            logger.warning(f"[process_detection_algorithms] 结束帧检测失败，使用默认值{num_frames - 1}")
        
        # 9. 结果范围检查
        # 修正：确保start_frame为int类型
        if isinstance(start_frame, dict):
            start_frame = start_frame.get("start_frame", 0)
        if not isinstance(start_frame, int):
            start_frame = 0
        start_frame = max(0, min(start_frame, num_frames - 1))
        end_frame = max(start_frame, min(end_frame, num_frames - 1))
        
        # 10. 输出最终结果
        logger.info(f"[process_detection_algorithms] 最终结果 - 开始帧: {start_frame}, 结束帧: {end_frame}")
        return start_frame, end_frame
        
    finally:
        # 清理实验目录（可选，用于节省磁盘空间）
        try:
            import shutil
            shutil.rmtree(experiment_dir)
            logger.info(f"[process_detection_algorithms] 已清理实验目录: {experiment_dir}")
        except Exception as e:
            logger.warning(f"[process_detection_algorithms] 清理实验目录失败: {e}")
            # 清理失败不影响主要功能，继续执行



def load_frames_as_numpy_sequence(local_task_dir: str, total_frames: int) -> Sequence[np.ndarray]:
    """
    从指定本地目录按顺序加载图片帧为 numpy.ndarray 序列。
    
    参数:
        local_task_dir (str): 包含图片帧的本地目录路径 (例如 '~/downloaded_frames/task_id/')。
        total_frames (int): 需要加载的总帧数 (例如，图片名为 frame_0.jpeg, ..., frame_{total_frames-1}.jpeg)。
        
    返回:
        Sequence[np.ndarray]: 成功加载的图片帧的 numpy.ndarray 列表。
                              如果某帧无法加载，则该帧不会包含在返回的序列中，并会记录警告。
    """
    loaded_frames: List[np.ndarray] = []
    # local_task_dir 可能包含 '~', 需要展开
    expanded_dir = os.path.expanduser(local_task_dir)
    
    logger.info(f"[Loader] 开始从目录 {expanded_dir} 加载 {total_frames} 帧图像...")
    
    for i in range(total_frames):  # 索引范围 0 ~ total_frames-1
        frame_filename = f"frame_{i}.jpeg"
        frame_path = os.path.join(expanded_dir, frame_filename)
        
        if not os.path.exists(frame_path):
            logger.warning(f"[Loader] 帧图像文件不存在，跳过: {frame_path}")
            continue
            
        try:
            # cv2.imread 默认以 BGR 格式加载图像
            img_array = cv2.imread(frame_path)
            if img_array is not None:
                loaded_frames.append(img_array)
                logger.debug(f"[Loader] 帧图像加载成功: {frame_path}, 形状: {img_array.shape}")
            else:
                logger.warning(f"[Loader] cv2.imread 返回 None，无法加载帧图像: {frame_path}")
        except Exception as e:
            logger.error(f"[Loader] 加载帧图像时发生异常: {frame_path}，错误: {e}", exc_info=True)
            
    logger.info(f"[Loader] 图像加载完成。成功加载 {len(loaded_frames)} / {total_frames} 帧。")
    return loaded_frames

def cleanup_downloaded_frames(local_task_dir: str):
    """
    清理（删除）指定的本地任务帧目录。

    参数:
        local_task_dir (str): 要删除的目录路径。
    """
    # 确保路径是展开的，以防包含 '~'
    expanded_dir = os.path.expanduser(local_task_dir)
    
    if not expanded_dir or expanded_dir == os.path.expanduser("~"): # 防止意外删除主目录
        logger.warning(f"[Cleaner] 无效的清理目录或尝试清理根用户目录: {expanded_dir}，跳过清理。")
        return

    if os.path.exists(expanded_dir):
        try:
            shutil.rmtree(expanded_dir)
            logger.info(f"[Cleaner] 已成功删除目录: {expanded_dir}")
        except OSError as e:
            logger.error(f"[Cleaner] 删除目录时发生错误: {expanded_dir}，错误: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"[Cleaner] 删除目录时发生未知错误: {expanded_dir}，错误: {e}", exc_info=True)
    else:
        logger.info(f"[Cleaner] 目录不存在，无需清理: {expanded_dir}")

def calculate_action_start_frame(video_create_timestamp: int, action_event_info: Dict[str, Any], fps: int, duration_seconds: float) -> Optional[int]:
    """
    根据视频创建时间戳和第一个操作事件的系统时间计算操作发生的帧。

    参数:
        video_create_timestamp (int): 视频创建的Unix时间戳 (秒)。
        action_event_info (Dict[str, Any]): 包含事件列表的字典。
        fps (int): 视频的帧率。

    返回:
        Optional[int]: 计算得到的操作起始帧号。如果无法计算，则默认为None。
    """
    if not action_event_info or not isinstance(action_event_info, dict) or \
       "events" not in action_event_info or not isinstance(action_event_info["events"], list) or \
       not action_event_info["events"]:
        logger.warning(f"[FrameCalc] 无效或空的 action_event_info['events']，无法计算操作起始帧。返回默认帧 None。 Info: {action_event_info}")
        return None

    try:
        first_event = action_event_info["events"][0]
        if not isinstance(first_event, dict) or "system_time" not in first_event:
            logger.warning(f"[FrameCalc] 第一个事件格式无效或缺少 'system_time'。事件: {first_event}。将返回 None.")
            return None
        
        first_event_system_time_str = first_event["system_time"]
        
        video_creation_datetime_utc = arrow.get(video_create_timestamp) # Video CREATION time in UTC
        
        # Calculate actual video START time by subtracting duration from creation time
        video_actual_start_datetime_utc = video_creation_datetime_utc.shift(seconds=-duration_seconds)
        
        first_event_datetime_gmt8 = arrow.get(first_event_system_time_str, tzinfo='+08:00') # Event time in GMT+8
        
        logger.info(f"[FrameCalc] 视频创建时间 (UTC): {video_creation_datetime_utc}, 视频时长: {duration_seconds:.3f}s")
        logger.info(f"[FrameCalc] 计算得到的视频实际开始时间 (UTC): {video_actual_start_datetime_utc}")
        logger.info(f"[FrameCalc] 第一个事件的原始时间 (GMT+8): {first_event_datetime_gmt8} (字符串: '{first_event_system_time_str}')")

        # Calculate the time difference in seconds: (Event Time) - (Video Actual Start Time)
        # Both times must be in the same reference (e.g., UTC timestamps) for direct subtraction.
        time_difference_seconds = first_event_datetime_gmt8.timestamp() - video_actual_start_datetime_utc.timestamp()
        
        logger.info(f"[FrameCalc] 第一个事件与视频实际开始的时间差: {time_difference_seconds:.3f} 秒")

        if time_difference_seconds < 0:
            logger.warning(f"[FrameCalc] 第一个事件时间 ({first_event_datetime_gmt8}) 早于计算出的视频实际开始时间 ({video_actual_start_datetime_utc})。事件可能无效或时间戳不准确。将返回 None。")
            return None # Return None if event is before video start
            
        action_frame = round(time_difference_seconds * fps)
        logger.info(f"[FrameCalc] 计算得到的操作起始帧: {action_frame} (基于 {time_difference_seconds:.3f}s * {fps}fps)")
        
        return max(0, action_frame) # Ensure frame number is not negative

    except arrow.parser.ParserError as e:
        logger.error(f"[FrameCalc] 解析时间戳时出错: video_create_timestamp='{video_create_timestamp}', first_event_system_time='{first_event_system_time_str if 'first_event_system_time_str' in locals() else '未提取'}'. 错误: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"[FrameCalc] 计算操作起始帧时发生未知错误: {e}", exc_info=True)
        return None
