"""
UI-Infer 相关的函数集合
从 llm_narrow_core.py 中分离出来，用于专门处理UI推断相关的功能
"""

import json
import os
import re
import time
import traceback
import threading
import math
import shutil
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import torch
import pandas as pd
from paddleocr import PaddleOCR

# 避免循环导入，在函数内部导入所需的函数


def get_ui_infer_with_retry(horus_client, image, cls_thresh=0, max_retries=3, retry_delay=2, frame_info=""):
    """
    带重试机制的UI推断请求
    
    Args:
        horus_client: UI推断客户端
        image: 图像数据 (BGR格式的numpy数组)
        cls_thresh: 分类阈值，默认0
        max_retries: 最大重试次数，默认3次
        retry_delay: 重试间隔（秒），默认2秒
        frame_info: 帧信息字符串，用于日志标识，如"frame 123"
    
    Returns:
        dict: UI推断结果，失败时返回包含错误信息的字典
    """
    import time
    
    frame_label = f" {frame_info}" if frame_info else ""
    
    for attempt in range(max_retries + 1):  # +1 因为第一次不算重试
        try:
            if attempt == 0:
                print(f"  [UI-Infer{frame_label}] 发送UI推断请求...")
            else:
                print(f"  [UI-Infer{frame_label}] 重试第 {attempt} 次...")
                
            result = horus_client.get_ui_infer(image=image, cls_thresh=cls_thresh)
            
            # 检查结果是否有效
            if result and isinstance(result, dict):
                if result.get('code') == 0:
                    if attempt == 0:
                        print(f"  [UI-Infer{frame_label}] 请求成功")
                    else:
                        print(f"  [UI-Infer{frame_label}] 重试第 {attempt} 次成功")
                    return result
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"  [UI-Infer{frame_label}] 服务返回错误: code={result.get('code')}, msg={error_msg}")
            else:
                print(f"  [UI-Infer{frame_label}] 返回无效结果: {type(result)} - {result}")
                
        except ConnectionError as e:
            print(f"  [UI-Infer{frame_label}] 网络连接错误: {str(e)}")
        except TimeoutError as e:
            print(f"  [UI-Infer{frame_label}] 请求超时: {str(e)}")
        except Exception as e:
            print(f"  [UI-Infer{frame_label}] 请求异常: {type(e).__name__} - {str(e)}")
        
        # 如果不是最后一次尝试，等待后重试
        if attempt < max_retries:
            wait_time = retry_delay * (attempt + 1)  # 递增延迟：2s, 4s, 6s...
            print(f"  [UI-Infer{frame_label}] {wait_time}秒后重试...")
            time.sleep(wait_time)
        else:
            print(f"  [UI-Infer{frame_label}] 已达到最大重试次数 {max_retries}，放弃请求")
    
    # 所有重试都失败，返回错误结果
    return {
        'code': -1,
        'msg': f'UI推断请求失败，已重试{max_retries}次',
        'data': {},
        'retry_info': {
            'max_retries': max_retries,
            'total_attempts': max_retries + 1,
            'frame_info': frame_info
        }
    }


def extract_mask_regions_from_ui_infer(recognize_results, target_classes=None, image_width=None, width_threshold=0.7, image_height=None):
    """
    从UI推断结果中提取需要遮蔽的区域
    
    Args:
        recognize_results: UI推断识别结果列表
        target_classes: 需要遮蔽的类别名称列表，如['banner', 'advertisement', 'popup']。
                       如果为None，则遮蔽所有检测到的区域
        image_width: 图像宽度，用于计算宽度阈值
        width_threshold: 宽度阈值比例，默认0.7表示70%
        image_height: 图像高度，用于位置判断
    
    Returns:
        list: 遮蔽区域列表，格式为 [{'coordinates': {'top': y1, 'left': x1, 'bottom': y2, 'right': x2}}, ...]
    """
    if not recognize_results:
        return []
    
    # 扩展需要遮蔽的类别，但排除重要的导航元素
    always_mask_classes = [
        'banner', 'advertisement', 'popup', 'ad', 'carousel', 'slider',
        'header', 'toolbar', 'topbar', 'statusbar',  # 移除 'nav', 'navigation' 避免误遮蔽重要导航
        'loading', 'spinner', 'progress', 'alert', 'notification',
        'floating', 'overlay', 'modal', 'dialog', 'toast'
    ]
    
    mask_regions = []
    
    for recognition in recognize_results:
        cls_name = recognition.get('cls_name', '').lower()
        box = recognition.get('elem_det_region')  # [x1, y1, x2, y2]
        
        # 检查box是否存在且格式正确
        if not box or len(box) != 4:
            print(f"  [Skip] Component '{cls_name}': 无效的边界框数据 {box}")
            continue
        
        # 计算UI组件的尺寸
        ui_width = box[2] - box[0]
        ui_height = box[3] - box[1]
        
        # 计算宽度比例和高度比例
        width_ratio = ui_width / image_width if image_width else 0
        height_ratio = ui_height / image_height if image_height else 0
        
        print(f"  [Check] Component '{cls_name}': width={ui_width}px ({width_ratio:.1%}), height={ui_height}px ({height_ratio:.1%})")
        
        should_mask = False
        mask_reason = ""
        
        # 计算UI组件在图像中的相对位置
        relative_y_position = (box[1] + box[3]) / 2 / image_height if image_height else 0  # 中心点位置
        is_bottom_area = relative_y_position > 0.7  # 底部30%区域
        
        # 判断是否需要遮蔽的条件
        if cls_name in always_mask_classes:
            should_mask = True
            mask_reason = f"类别匹配 '{cls_name}'"
        elif width_ratio >= width_threshold:
            # 底部区域的宽UI组件更保守处理，避免误遮蔽导航栏
            if is_bottom_area and width_ratio < 0.9:  # 底部区域需要90%以上宽度才遮蔽
                should_mask = False
                mask_reason = f"底部区域宽度 {width_ratio:.1%} < 90%，保留重要导航"
            else:
                should_mask = True
                mask_reason = f"宽度比例 {width_ratio:.1%} >= {width_threshold:.1%}"
        elif height_ratio >= 0.8:  # 高度比例大于80%的竖向组件
            should_mask = True
            mask_reason = f"高度比例 {height_ratio:.1%} >= 80%"
        elif width_ratio >= 0.5 and not is_bottom_area:  # 激进模式但排除底部区域
            should_mask = True
            mask_reason = f"宽度比例 {width_ratio:.1%} >= 50% (激进模式，非底部)"
        elif height_ratio >= 0.6 and not is_bottom_area:  # 激进模式但排除底部区域
            should_mask = True
            mask_reason = f"高度比例 {height_ratio:.1%} >= 60% (激进模式，非底部)"
        
        if should_mask:
            print(f"  [Mask] Including region '{cls_name}': {mask_reason}")
            
            # 智能边缘扩展：根据UI组件位置和类型使用不同的扩展策略
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            
            # 计算UI组件在图像中的相对位置
            relative_y_position = y1 / image_height if image_height else 0
            
            # 动态边缘扩展阈值 - 大幅增大以确保完全遮蔽
            if relative_y_position <= 0.15:  # 顶部15%区域（状态栏、导航栏区域）
                top_threshold = 350  # 大幅增大顶部扩展阈值，确保完全遮蔽
                side_threshold = 100
            elif relative_y_position <= 0.3:  # 上部30%区域（标题栏、工具栏区域）
                top_threshold = 280  # 大幅增大上部区域阈值
                side_threshold = 90
            elif relative_y_position <= 0.5:  # 中上部50%区域
                top_threshold = 180  # 增大中上部阈值
                side_threshold = 80
            else:  # 中下部区域
                top_threshold = 120  # 增大中下部阈值
                side_threshold = 70
            
            print(f"    [Smart-Extend] Position analysis: y={y1}px ({relative_y_position:.1%}) -> thresholds: top={top_threshold}px, side={side_threshold}px")
            
            # 智能扩展到顶部边缘：根据位置使用不同阈值
            if y1 <= top_threshold:
                original_y1 = y1
                y1 = 0
                print(f"    [Smart-Extend] Extended to top edge: {original_y1} -> {y1} (threshold={top_threshold}px)")
            
            # 智能扩展到底部边缘  
            if (image_height - y2) <= side_threshold:
                original_y2 = y2
                y2 = image_height
                print(f"    [Smart-Extend] Extended to bottom edge: {original_y2} -> {y2} (threshold={side_threshold}px)")
            
            # 智能扩展到左边缘
            if x1 <= side_threshold:
                original_x1 = x1
                x1 = 0
                print(f"    [Smart-Extend] Extended to left edge: {original_x1} -> {x1} (threshold={side_threshold}px)")
            
            # 智能扩展到右边缘
            if (image_width - x2) <= side_threshold:
                original_x2 = x2
                x2 = image_width
                print(f"    [Smart-Extend] Extended to right edge: {original_x2} -> {x2} (threshold={side_threshold}px)")
            
            # 特殊类型的UI组件使用更激进的扩展策略
            if cls_name in ['statusbar', 'navbar', 'header', 'topbar', 'banner']:
                if y1 > 0 and y1 <= 250:  # 增大强制扩展范围，确保状态栏完全遮蔽
                    print(f"    [Aggressive-Extend] {cls_name} component forced to top edge: {y1} -> 0")
                    y1 = 0
            
            # 添加更多padding确保完全遮蔽
            padding = 5
            expanded_box = [
                max(0, int(x1 - padding)),  # x1
                max(0, int(y1 - padding)),  # y1
                min(image_width, int(x2 + padding)),  # x2
                min(image_height, int(y2 + padding))  # y2
            ]
            
            mask_region = {
                'coordinates': expanded_box,
                'class_name': recognition.get('cls_name', 'unknown'),
                'confidence': recognition.get('confidence', 0.0),
                'width': ui_width,
                'height': ui_height,
                'width_ratio': width_ratio,
                'height_ratio': height_ratio,
                'mask_reason': mask_reason
            }
            
            mask_regions.append(mask_region)
            print(f"  [Mask] Added region: coords={mask_region['coordinates']} class={mask_region['class_name']} reason={mask_reason}")
        else:
            print(f"  [Skip] Component '{cls_name}': 不符合遮蔽条件")
    
    # 合并重叠的遮蔽区域以优化遮蔽效果
    if len(mask_regions) > 1:
        print(f"  [Merge] Processing {len(mask_regions)} mask regions for overlaps...")
        mask_regions = merge_overlapping_regions(mask_regions, image_width, image_height)
        print(f"  [Merge] Merged to {len(mask_regions)} regions")
    
    # 检查总遮蔽面积，如果超过50%则取消遮蔽（可能是识别错误）
    if mask_regions and image_width and image_height:
        total_image_area = image_width * image_height
        total_mask_area = 0
        
        for region in mask_regions:
            coords = region['coordinates']
            if len(coords) == 4:
                x1, y1, x2, y2 = coords
                region_area = (x2 - x1) * (y2 - y1)
                total_mask_area += region_area
        
        mask_coverage_ratio = total_mask_area / total_image_area
        print(f"  [Coverage-Check] 总遮蔽面积: {total_mask_area}px², 图片总面积: {total_image_area}px², 覆盖率: {mask_coverage_ratio:.1%}")
        
        if mask_coverage_ratio > 0.5:  # 超过50%
            print(f"  [Coverage-Check] 警告：遮蔽覆盖率过高 ({mask_coverage_ratio:.1%} > 50%)，可能是识别错误，取消所有遮蔽")
            return []  # 返回空列表，取消所有遮蔽
        else:
            print(f"  [Coverage-Check] 遮蔽覆盖率正常 ({mask_coverage_ratio:.1%} ≤ 50%)，保持遮蔽")
    
    return mask_regions


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

# 继续添加其他函数
def create_voting_image_grid_with_ui_infer(segment_dir, candidate_frames, horus_client, max_single_size=2400, label_height=50, ui_infer_max_retries=3, ui_infer_retry_delay=2, grid_cache=None, processed_frames_cache=None, remove_background=False, enable_diff=False, enable_global_screen_rect=False):
    """
    Create a compact image grid for voting: each image retains its original size, and the canvas size is dynamically calculated.
    Each image is accompanied by UI-infer component recognition results and automatically masks regions wider than 70%.
    Supports UI inference request retry mechanism for improved stability.
    Supports grid cache and processed frames cache for efficiency.
    Supports background removal and difference detection features.
    Supports global screen region uniform cropping feature.
    """
    from PIL import Image, ImageDraw, ImageFont
    import math
    
    # 避免循环导入，在函数内部导入所需的函数
    from .llm_narrow_core import (
        check_and_resize_saved_image,
        llm_vision_request_with_retry,
        remove_background_with_rembg
    )

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
    
    cache_key = (tuple(sorted(candidate_frames)), num_frames, max_single_size, label_height, remove_background, enable_diff, enable_global_screen_rect)
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

        img_pil = load_frame(segment_dir, frame_idx, None)
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
    total_images = len(candidate_frames) + 1  # Candidate frames + last frame
    
    # Pre-load all images to get original sizes (adopt final strategy)
    print("  [Voting] Pre-loading all images to get sizes...")
    all_images = []
    all_labels = []
    all_colors = []
    
    # If diff is enabled, need to get the last frame as the reference frame
    reference_frame = None
    print(f"  [Voting-Diff-Init] enable_diff parameter: {enable_diff}")
    if enable_diff:
        print(f"  [Voting-Diff-Init] Loading reference frame {num_frames - 1}")
        reference_frame = get_frame_with_ui_infer(num_frames - 1)
        if reference_frame is None:
            print("  [Voting-Diff-Error] Failed to load reference frame, disabling diff feature")
            enable_diff = False
        else:
            print(f"  [Voting-Diff-Init] Reference frame loaded successfully, size: {reference_frame.size}")
    else:
        print("  [Voting-Diff-Init] Diff feature not enabled")
    
    # Load candidate frames
    for frame_idx in candidate_frames:
        img = get_frame_with_ui_infer(frame_idx)
        if img is not None:
            # If diff is enabled, generate diff image
            if enable_diff and reference_frame is not None:
                print(f"  [Diff-Debug] Starting to generate diff image for frame {frame_idx}")
                print(f"  [Diff-Debug] Current image size: {img.size}")
                print(f"  [Diff-Debug] Reference image size: {reference_frame.size}")
                
                try:
                    
                    # Create temporary directory for diff processing
                    temp_dir = os.path.join(segment_dir, "temp_diff")
                    os.makedirs(temp_dir, exist_ok=True)
                    print(f"  [Diff-Debug] Created temporary directory: {temp_dir}")
                    
                    # Save current frame and reference frame
                    current_path = os.path.join(temp_dir, f"frame_{frame_idx}.png")
                    reference_path = os.path.join(temp_dir, f"reference_{num_frames-1}.png")
                    
                    print(f"  [Diff-Debug] Saving current frame to: {current_path}")
                    img.save(current_path)
                    print(f"  [Diff-Debug] Saving reference frame to: {reference_path}")
                    reference_frame.save(reference_path)
                    
                    # Verify if files are saved successfully
                    if os.path.exists(current_path) and os.path.exists(reference_path):
                        print(f"  [Diff-Debug] Files saved successfully, size: {os.path.getsize(current_path)} bytes, {os.path.getsize(reference_path)} bytes")
                    else:
                        print(f"  [Diff-Debug] Error: Failed to save files")
                        continue
                    
                    # Convert to OpenCV format
                    print(f"  [Diff-Debug] Loading OpenCV images...")
                    img1 = cv2.imread(current_path)
                    img2 = cv2.imread(reference_path)
                    
                    if img1 is not None and img2 is not None:
                        print(f"  [Diff-Debug] OpenCV images loaded successfully, size: {img1.shape}, {img2.shape}")
                        
                        # Get OCR result
                        print(f"  [Diff-Debug] Getting OCR result...")
                        from toolchain_llm.service.ui_detection.img_diff import get_ocr_result, ImageDiff
                        ocr_result = get_ocr_result(img1, img2)
                        print(f"  [Diff-Debug] OCR result type: {type(ocr_result)}")
                        
                        # Create ImageDiff object and generate diff image
                        print(f"  [Diff-Debug] Creating ImageDiff object...")
                        img_diff_obj = ImageDiff(img1, img2, ocr_result, struct_score_thresh=0.99)
                        print(f"  [Diff-Debug] Generating diff image...")
                        diff_img, diff_points_count = img_diff_obj.image_diff()
                            
                        if diff_img is not None:
                            print(f"  [Diff-Debug] Diff image generated successfully, type: {type(diff_img)}, size: {diff_img.shape}")
                            # Convert back to PIL format
                            diff_img_rgb = cv2.cvtColor(diff_img, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(diff_img_rgb)
                            print(f"  [Diff-Success] Frame {frame_idx} diff image generated successfully, replaced original image")
                            
                            # Save diff image for debugging
                            diff_save_path = os.path.join(temp_dir, f"diff_{frame_idx}.png")
                            img.save(diff_save_path)
                            print(f"  [Diff-Debug] Diff image saved to: {diff_save_path}")
                        else:
                            print(f"  [Diff-Error] Frame {frame_idx} image_diff() returned None, using original image")
                    else:
                        print(f"  [Diff-Error] Failed to load OpenCV images: img1={img1 is not None}, img2={img2 is not None}")
                        
                except ImportError as e:
                    print(f"  [Diff-Error] Import error: {e}")
                    print(f"  [Diff-Error] Failed to import diff related modules, disabling diff feature")
                    enable_diff = False
                except Exception as e:
                    print(f"  [Diff-Error] Frame {frame_idx} diff processing error: {type(e).__name__}: {e}")
                    print(f"  [Diff-Error] Full error info:")
                    traceback.print_exc()
                    print(f"  [Diff-Error] Using original image")
            
            all_images.append(img)
            all_labels.append(f"{frame_idx}")
            all_colors.append((200, 200, 200))
    
    # Load last frame
    img = get_frame_with_ui_infer(num_frames - 1)
    if img is not None:
        all_images.append(img)
        all_labels.append("Last Frame (End)")
        all_colors.append((0, 0, 255))
    
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
    title = "Page Loading Analysis Grid (with UI Detections)"
    if enable_diff:
        title += " + Diff Analysis"
    title_width = draw.textlength(title, font=title_font)
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 5), title, fill=(0, 0, 0), font=title_font)
    
    subtitle = f"Voting candidates: {len(candidate_frames)}, Total frames: {total_images}"
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
    
    # Clean up temporary diff files
    if enable_diff:
        try:
            temp_dir = os.path.join(segment_dir, "temp_diff")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"  [Diff-Cleanup] Cleaned up temporary diff directory: {temp_dir}")
        except Exception as e:
            print(f"  [Diff-Cleanup] Failed to clean up temporary files: {e}")
    
    return grid_image 

def create_final_iterative_grid_with_ui_infer(segment_dir, final_candidates, iteration_results, horus_client, ui_infer_max_retries=3, ui_infer_retry_delay=2, grid_cache=None, processed_frames_cache=None, remove_background=False, enable_diff=False, enable_global_screen_rect=False, frame_dir=None):
    """
    Create a grid for the final voting, showing the iterative process and results, with UI-infer component recognition results.
    Supports UI inference request retry mechanism for improved stability.
    Supports grid cache and processed frames cache for efficiency.
    Supports background removal and difference detection features.
    Supports global screen region uniform cropping feature.
    """
    from PIL import Image, ImageDraw, ImageFont
    import math

    if not final_candidates:
        return None
    
    # Initialize cache
    if grid_cache is None:
        grid_cache = {}
    if processed_frames_cache is None:
        processed_frames_cache = {}
    
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    
    # Check final grid cache (includes iteration results cache key)
    cache_key = (tuple(sorted(final_candidates)), num_frames, str(iteration_results), remove_background, enable_diff, enable_global_screen_rect, frame_dir)
    if cache_key in grid_cache:
        print(f"  [Final-Grid-Cache] Using cached final grid, candidate frames: {final_candidates}")
        return grid_cache[cache_key]
        
    print(f"  [Final-Grid-Cache] Cache miss, generating new final grid, candidate frames: {final_candidates}")
    
    # Global screen region detection
    global_screen_rect = None
    if enable_global_screen_rect:
        print(f"  [Global-Screen] Enabling global screen region detection")
        try:
            from toolchain_llm.service.ui_detection.img_diff import get_global_screen_rect
            all_frames = list(final_candidates) + [num_frames - 1]  # Candidate frames + last frame
            global_screen_rect = get_global_screen_rect(segment_dir, all_frames)
            print(f"  [Global-Screen] Detected global screen region: {global_screen_rect}")
        except Exception as e:
            print(f"  [Global-Screen] Global screen region detection failed: {e}")
            enable_global_screen_rect = False
    
    # 避免循环导入，在函数内部导入所需的函数
    from .llm_narrow_core import (
        check_and_resize_saved_image,
        llm_vision_request_with_retry,
        remove_background_with_rembg
    )
    from .llm_narrow_utils import load_frame
    
    def get_frame_with_ui_infer(frame_idx):
        import cv2
        
        # First check global cache
        if frame_idx in processed_frames_cache:
            print(f"  [Final-Frame-Cache] Using cached processed frame: {frame_idx}")
            return processed_frames_cache[frame_idx]
        
        print(f"  [Final-Frame-Cache] Cache miss, processing new frame: {frame_idx}")

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

        ui_infer_result = get_ui_infer_with_retry(horus_client, img_np_bgr, cls_thresh=0, max_retries=ui_infer_max_retries, retry_delay=ui_infer_retry_delay, frame_info=f"final frame {frame_idx}")
        
        # Keep the original image's transparent background
        processed_img = img_pil
        if ui_infer_result.get('code') == 0:
            recognize_results = ui_infer_result.get('data', {}).get('recognize_results', [])
            if recognize_results:
                print(f"  [UI-Infer] Found {len(recognize_results)} components for final frame {frame_idx}.")
                # Add debug output to display the structure of the first component
                if recognize_results:
                    first_result = recognize_results[0]
                    print(f"  [Debug] Final frame sample component structure: {list(first_result.keys())}")
                    print(f"  [Debug] Final frame sample component: {first_result}")
                
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
                
                print(f"  [UI-Infer] Final frame {frame_idx}: Found {len(wide_regions)} components to mask.")
                
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
                        print(f"    [Final] Physically masked region at ({x1}, {y1}, {x2}, {y2})")
                
                # No longer draw UI component boxes, just use the masked image
                # processed_img = draw_ui_inferences_on_image(processed_img, recognize_results, mask_regions=None)
            else:
                print(f"  [UI-Infer] No components found for final frame {frame_idx}.")
        else:
            print(f"  [UI-Infer] Failed for final frame {frame_idx}. Code: {ui_infer_result.get('code')}, Msg: {ui_infer_result.get('msg')}")
        
        # Apply global screen region cropping
        if enable_global_screen_rect and global_screen_rect is not None:
            try:
                print(f"  [Global-Screen] Applying global screen region cropping to final frame {frame_idx}: {global_screen_rect}")
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
                    print(f"  [Global-Screen] Final frame {frame_idx} cropped, new size: {processed_img.size}")
                else:
                    print(f"  [Global-Screen] Final frame {frame_idx} cropping region invalid, keeping original size")
            except Exception as e:
                print(f"  [Global-Screen] Final frame {frame_idx} cropping failed: {e}")
        
        # Cache processed frame
        processed_frames_cache[frame_idx] = processed_img
        return processed_img

    # Pre-load all images to get original sizes
    print("  [Final] Pre-loading all images to get sizes...")
    all_images = []
    all_labels = []
    all_colors = []
    
    # If diff is enabled, need to get the last frame as the reference frame
    reference_frame = None
    print(f"  [Final-Diff-Init] enable_diff parameter: {enable_diff}")
    if enable_diff:
        print(f"  [Final-Diff-Init] Loading reference frame {num_frames - 1}")
        reference_frame = get_frame_with_ui_infer(num_frames - 1)
        if reference_frame is None:
            print("  [Final-Diff-Error] Failed to load reference frame, disabling diff feature")
            enable_diff = False
        else:
            print(f"  [Final-Diff-Init] Reference frame loaded successfully, size: {reference_frame.size}")
    else:
        print("  [Final-Diff-Init] Diff feature not enabled")
    
    for frame_idx in final_candidates:
        img = get_frame_with_ui_infer(frame_idx)
        if img is not None:
            # If diff is enabled, generate diff image
            if enable_diff and frame_idx != num_frames - 1 and reference_frame is not None:
                print(f"  [Final-Diff-Debug] Starting to generate diff image for frame {frame_idx}")
                print(f"  [Final-Diff-Debug] Current image size: {img.size}")
                print(f"  [Final-Diff-Debug] Reference image size: {reference_frame.size}")
                
                try:
                    
                    # Create temporary directory for diff processing
                    temp_dir = os.path.join(segment_dir, "temp_diff")
                    os.makedirs(temp_dir, exist_ok=True)
                    print(f"  [Final-Diff-Debug] Created temporary directory: {temp_dir}")
                    
                    # Save current frame and reference frame
                    current_path = os.path.join(temp_dir, f"final_frame_{frame_idx}.png")
                    reference_path = os.path.join(temp_dir, f"final_reference_{num_frames-1}.png")
                    
                    print(f"  [Final-Diff-Debug] Saving current frame to: {current_path}")
                    img.save(current_path)
                    print(f"  [Final-Diff-Debug] Saving reference frame to: {reference_path}")
                    reference_frame.save(reference_path)
                    
                    # Verify if files are saved successfully
                    if os.path.exists(current_path) and os.path.exists(reference_path):
                        print(f"  [Final-Diff-Debug] Files saved successfully, size: {os.path.getsize(current_path)} bytes, {os.path.getsize(reference_path)} bytes")
                    else:
                        print(f"  [Final-Diff-Debug] Error: Failed to save files")
                        continue
                    
                    # Convert to OpenCV format
                    print(f"  [Final-Diff-Debug] Loading OpenCV images...")
                    img1 = cv2.imread(current_path)
                    img2 = cv2.imread(reference_path)
                    
                    if img1 is not None and img2 is not None:
                        print(f"  [Final-Diff-Debug] OpenCV images loaded successfully, size: {img1.shape}, {img2.shape}")
                        
                        # Get OCR result
                        print(f"  [Final-Diff-Debug] Getting OCR result...")
                        ocr_result = get_ocr_result(img1, img2)
                        print(f"  [Final-Diff-Debug] OCR result type: {type(ocr_result)}")
                        
                        # Create ImageDiff object and generate diff image
                        print(f"  [Final-Diff-Debug] Creating ImageDiff object...")
                        img_diff_obj = ImageDiff(img1, img2, ocr_result, struct_score_thresh=0.99)
                        print(f"  [Final-Diff-Debug] Generating diff image...")
                        diff_img, diff_points_count = img_diff_obj.image_diff()
                        
                        if diff_img is not None:
                            print(f"  [Final-Diff-Debug] Diff image generated successfully, type: {type(diff_img)}, size: {diff_img.shape}")
                            # Convert back to PIL format
                            diff_img_rgb = cv2.cvtColor(diff_img, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(diff_img_rgb)
                            print(f"  [Final-Diff-Success] Frame {frame_idx} diff image generated successfully, replaced original image")
                            
                            # Save diff image for debugging
                            diff_save_path = os.path.join(temp_dir, f"final_diff_{frame_idx}.png")
                            img.save(diff_save_path)
                            print(f"  [Final-Diff-Debug] Diff image saved to: {diff_save_path}")
                        else:
                            print(f"  [Final-Diff-Error] Frame {frame_idx} image_diff() returned None, using original image")
                    else:
                        print(f"  [Final-Diff-Error] Failed to load OpenCV images: img1={img1 is not None}, img2={img2 is not None}")
                        
                except ImportError as e:
                    print(f"  [Final-Diff-Error] Import error: {e}")
                    print(f"  [Final-Diff-Error] Failed to import diff related modules, disabling diff feature")
                    enable_diff = False
                except Exception as e:
                    print(f"  [Final-Diff-Error] Frame {frame_idx} diff processing error: {type(e).__name__}: {e}")
                    print(f"  [Final-Diff-Error] Full error info:")
                    traceback.print_exc()
                    print(f"  [Final-Diff-Error] Using original image")
            
            all_images.append(img)
            
            if frame_idx == num_frames - 1:
                all_labels.append("Last Frame (End)")
                all_colors.append((0, 0, 255))
            else:
                is_iteration_result = any(result["best_frame"] == frame_idx for result in iteration_results)
                if is_iteration_result:
                    all_labels.append(f"{frame_idx} (Iter. Result)")
                    all_colors.append((0, 128, 0))
                else:
                    all_labels.append(f"{frame_idx}")
                    all_colors.append((128, 128, 128))
    
    if not all_images:
        print("No available images")
        return None
    
    total_images = len(all_images)
    rows = min(2, total_images)  # Max 2 rows
    cols = math.ceil(total_images / rows)  # Calculate cols based on rows
    
    # Use the adjusted size of the first image as the baseline
    base_width, base_height = all_images[0].size
    margin = 12  # Increase image margin  
    padding = 4   # Keep inner padding
    label_height = 50  # Further increase label height to accommodate larger font
    
    # Dynamically calculate canvas size to optimize space usage
    canvas_width = cols * (base_width + margin + padding * 2) + margin
    canvas_height = rows * (base_height + label_height + margin + padding * 2) + margin + 80  # 增加到80px for larger titles
    
    grid_image = Image.new('RGB', (canvas_width, canvas_height), (240, 240, 240))  # 使用灰色背景
    draw = ImageDraw.Draw(grid_image)
    
    try:
        font = ImageFont.truetype("Arial", 50)  # 进一步增大帧号字体
        title_font = ImageFont.truetype("Arial", 54)  # 进一步增大标题字体
    except:
        try:
            font = ImageFont.load_default(size=50)
            title_font = ImageFont.load_default(size=54)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
    
    title = "Final Iterative Voting Results (with UI Detections)"
    if enable_diff:
        title += " + Diff Analysis"
    title_width = draw.textlength(title, font=title_font)
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 8), title, fill=(0, 0, 0), font=title_font)
    
    subtitle = f"Total iterations: {len(iteration_results)}, Final candidates: {len(final_candidates)}"
    subtitle_width = draw.textlength(subtitle, font=font)
    subtitle_x = (canvas_width - subtitle_width) // 2
    draw.text((subtitle_x, 32), subtitle, fill=(100, 100, 100), font=font)
    
    # 绘制每张图片（保持原始尺寸）
    for i in range(total_images):
        row = i // cols
        col = i % cols
        
        # 计算图片位置，包含padding
        x = col * (base_width + margin + padding * 2) + margin + padding
        y = row * (base_height + label_height + margin + padding * 2) + 80 + padding  # 为更大的标题留出的空间
        
        img = all_images[i]
        label = all_labels[i]
        border_color = all_colors[i]
        label_color = all_colors[i] if all_colors[i] != (128, 128, 128) else (0, 0, 0)  # 灰色边框用黑色文字
        
        print(f"  [Final] 绘制图片 {i+1}/{total_images}: {label} at ({x}, {y}) 调整后尺寸({img.size[0]}x{img.size[1]})")
        
        # 添加白色背景和边框
        bg_x, bg_y = x - padding, y - padding
        bg_width, bg_height = img.size[0] + padding * 2, img.size[1] + padding * 2
        draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], fill=(255, 255, 255), outline=border_color, width=2)
        
        # 粘贴调整尺寸后的图片
        grid_image.paste(img, (x, y))
        
        # 绘制标签（直接显示帧号，不带框）
        if label:
            text_width = draw.textlength(label, font=font)
            text_x = x + (img.size[0] - text_width) // 2
            text_y = y + img.size[1] + 8  # 减少与图片的间距
            
            # 直接绘制黑色文字，不添加背景框
            draw.text((text_x, text_y), label, fill=(0, 0, 0), font=font)
    
    
    
    # 缓存生成的最终拼图
    grid_cache[cache_key] = grid_image
    print(f"  [Final-Grid-Cache] 已缓存最终拼图，候选帧: {final_candidates}")
    
    # 清理临时diff文件
    if enable_diff:
        try:
            temp_dir = os.path.join(segment_dir, "temp_diff")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"  [Final-Diff-Cleanup] 已清理临时diff目录: {temp_dir}")
        except Exception as e:
            print(f"  [Final-Diff-Cleanup] 清理临时文件失败: {e}")
    
    return grid_image 