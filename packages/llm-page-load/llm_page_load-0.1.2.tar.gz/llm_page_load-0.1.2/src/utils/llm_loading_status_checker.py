import os
import json
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ui_infer_with_retry(horus_client, image, cls_thresh=0, max_retries=3, retry_delay=2, frame_info=""):
    """
    从ui_infer方法复制的UI推理函数，用于获取页面元素信息
    """
    for attempt in range(max_retries):
        try:
            recognize_results = horus_client.recognize(image)
            if recognize_results and len(recognize_results) > 0:
                return recognize_results
            else:
                logger.warning(f"UI inference returned empty results (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            logger.error(f"UI inference error (attempt {attempt + 1}/{max_retries}): {str(e)}")
        
        if attempt < max_retries - 1:
            import time
            time.sleep(retry_delay)
    
    return []

def extract_mask_regions_from_ui_infer(recognize_results, target_classes=None, image_width=None, width_threshold=0.7, image_height=None):
    """
    从ui_infer方法复制的区域提取函数
    """
    mask_regions = []
    
    if not recognize_results:
        return mask_regions
    
    for result in recognize_results:
        try:
            # 检查是否有必要的字段
            if not all(key in result for key in ['bbox', 'class_name', 'confidence']):
                continue
            
            class_name = result['class_name']
            confidence = result['confidence']
            bbox = result['bbox']
            
            # 如果指定了目标类别，只处理这些类别
            if target_classes and class_name not in target_classes:
                continue
            
            # 检查置信度
            if confidence < 0.5:  # 可以调整这个阈值
                continue
            
            # 解析边界框
            if isinstance(bbox, list) and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
            else:
                continue
            
            # 计算区域宽度和高度
            region_width = x2 - x1
            region_height = y2 - y1
            
            # 如果指定了图像宽度，检查区域宽度是否超过阈值
            if image_width and region_width / image_width > width_threshold:
                continue
            
            # 如果指定了图像高度，检查区域高度
            if image_height and region_height / image_height > 0.8:
                continue
            
            mask_regions.append({
                'bbox': [x1, y1, x2, y2],
                'class_name': class_name,
                'confidence': confidence
            })
            
        except Exception as e:
            logger.error(f"Error processing UI inference result: {str(e)}")
            continue
    
    return mask_regions

def merge_overlapping_regions(mask_regions, image_width, image_height):
    """
    从ui_infer方法复制的区域合并函数
    """
    if not mask_regions:
        return []
    
    # 按置信度排序
    sorted_regions = sorted(mask_regions, key=lambda x: x['confidence'], reverse=True)
    merged_regions = []
    
    for region in sorted_regions:
        bbox = region['bbox']
        x1, y1, x2, y2 = bbox
        
        # 检查是否与已合并的区域重叠
        should_merge = True
        for merged_region in merged_regions:
            merged_bbox = merged_region['bbox']
            mx1, my1, mx2, my2 = merged_bbox
            
            # 计算重叠区域
            overlap_x1 = max(x1, mx1)
            overlap_y1 = max(y1, my1)
            overlap_x2 = min(x2, mx2)
            overlap_y2 = min(y2, my2)
            
            if overlap_x1 < overlap_x2 and overlap_y1 < overlap_y2:
                # 有重叠，计算重叠比例
                overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
                region_area = (x2 - x1) * (y2 - y1)
                merged_area = (mx2 - mx1) * (my2 - my1)
                
                # 如果重叠比例超过50%，则跳过这个区域
                if overlap_area / min(region_area, merged_area) > 0.5:
                    should_merge = False
                    break
        
        if should_merge:
            merged_regions.append(region)
    
    return merged_regions

def create_loading_status_prompt(image_path: str, frame_idx: int, ui_infer_results: List[Dict]) -> str:
    """
    创建用于判断加载状态的英文prompt
    """
    # 分析UI推理结果
    ui_elements = []
    loading_indicators = []
    
    for result in ui_infer_results:
        class_name = result.get('class_name', '')
        confidence = result.get('confidence', 0)
        
        # 识别可能的加载指示器
        if any(keyword in class_name.lower() for keyword in ['loading', 'spinner', 'progress', 'wait']):
            loading_indicators.append(f"{class_name} (confidence: {confidence:.2f})")
        
        ui_elements.append(f"{class_name} (confidence: {confidence:.2f})")
    
    prompt = f"""Please analyze the loading status of this webpage frame (frame {frame_idx}).

Image Path: {image_path}

UI Elements Detected:
{chr(10).join(ui_elements) if ui_elements else "No UI elements detected"}

Loading Indicators Found:
{chr(10).join(loading_indicators) if loading_indicators else "No loading indicators detected"}

Please determine if the page is still loading or has finished loading. Consider the following factors:

1. **Visual Loading Indicators**: Look for spinners, progress bars, loading text, or animated elements
2. **Content Completeness**: Check if all expected content is visible and properly rendered
3. **UI Element States**: Analyze if buttons, forms, or interactive elements appear fully functional
4. **Layout Stability**: Determine if the page layout appears stable and complete

Based on your analysis, please respond with one of the following:

**STILL_LOADING** - if the page appears to be in a loading state with visible loading indicators or incomplete content
**FINISHED_LOADING** - if the page appears to be fully loaded with no loading indicators and complete content

Please provide your reasoning in a brief explanation after your classification.

Response format:
STATUS: [STILL_LOADING/FINISHED_LOADING]
REASONING: [Your explanation]"""

    return prompt

def check_frame_loading_status_with_ui_infer(
    frame_path: str, 
    frame_idx: int, 
    horus_client, 
    llm_client,
    ui_infer_max_retries: int = 3,
    ui_infer_retry_delay: int = 2,
    target_classes: Optional[List[str]] = None,
    model: str = "anthropic.claude-3.7-sonnet"
) -> Dict[str, Any]:
    """
    使用UI推理和LLM分析来检查帧的加载状态
    
    Args:
        frame_path: 帧图像路径
        frame_idx: 帧索引
        horus_client: Horus客户端
        llm_client: LLM客户端
        ui_infer_max_retries: UI推理重试次数
        ui_infer_retry_delay: UI推理重试延迟
        target_classes: 目标UI元素类别
        model: LLM模型名称
    
    Returns:
        包含加载状态分析结果的字典
    """
    try:
        # 读取图像
        image = cv2.imread(frame_path)
        if image is None:
            logger.error(f"Failed to read image: {frame_path}")
            return {
                'status': 'ERROR',
                'reasoning': f'Failed to read image: {frame_path}',
                'frame_idx': frame_idx,
                'ui_elements': [],
                'loading_indicators': []
            }
        
        image_height, image_width = image.shape[:2]
        
        # 获取UI推理结果
        ui_infer_results = get_ui_infer_with_retry(
            horus_client, 
            image, 
            max_retries=ui_infer_max_retries, 
            retry_delay=ui_infer_retry_delay,
            frame_info=f"frame_{frame_idx}"
        )
        
        # 提取和过滤UI元素
        mask_regions = extract_mask_regions_from_ui_infer(
            ui_infer_results,
            target_classes=target_classes,
            image_width=image_width,
            image_height=image_height
        )
        
        # 合并重叠区域
        final_regions = merge_overlapping_regions(mask_regions, image_width, image_height)
        
        # 创建prompt
        prompt = create_loading_status_prompt(frame_path, frame_idx, final_regions)
        
        # 调用LLM进行分析
        from .llm_narrow_core import llm_vision_request_with_retry
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": cv2.imencode('.jpg', image)[1].tobytes().decode('latin1')
                        }
                    }
                ]
            }
        ]
        
        response = llm_vision_request_with_retry(
            llm_client,
            messages,
            max_tokens=512,
            model=model,
            temperature=0.1
        )
        
        # 解析响应
        status = 'UNKNOWN'
        reasoning = 'No response from LLM'
        
        if response:
            response_text = response.strip()
            
            # 提取状态和推理
            if 'STATUS:' in response_text:
                status_line = response_text.split('STATUS:')[1].split('\n')[0].strip()
                if 'STILL_LOADING' in status_line:
                    status = 'STILL_LOADING'
                elif 'FINISHED_LOADING' in status_line:
                    status = 'FINISHED_LOADING'
            
            if 'REASONING:' in response_text:
                reasoning_line = response_text.split('REASONING:')[1].strip()
                reasoning = reasoning_line
        
        # 提取UI元素信息
        ui_elements = [region['class_name'] for region in final_regions]
        loading_indicators = [
            region['class_name'] for region in final_regions 
            if any(keyword in region['class_name'].lower() for keyword in ['loading', 'spinner', 'progress', 'wait'])
        ]
        
        return {
            'status': status,
            'reasoning': reasoning,
            'frame_idx': frame_idx,
            'ui_elements': ui_elements,
            'loading_indicators': loading_indicators,
            'total_ui_elements': len(final_regions),
            'ui_infer_results': final_regions
        }
        
    except Exception as e:
        logger.error(f"Error checking loading status for frame {frame_idx}: {str(e)}")
        return {
            'status': 'ERROR',
            'reasoning': f'Error: {str(e)}',
            'frame_idx': frame_idx,
            'ui_elements': [],
            'loading_indicators': []
        }

def analyze_segment_loading_status(
    segment_dir: str,
    horus_client,
    llm_client,
    target_classes: Optional[List[str]] = None,
    model: str = "anthropic.claude-3.7-sonnet"
) -> Dict[str, Any]:
    """
    分析整个视频片段的加载状态
    
    Args:
        segment_dir: 视频片段目录
        horus_client: Horus客户端
        llm_client: LLM客户端
        target_classes: 目标UI元素类别
        model: LLM模型名称
    
    Returns:
        包含分析结果的字典
    """
    # 查找最后一帧
    frames_dir = os.path.join(segment_dir, 'frames')
    if not os.path.exists(frames_dir):
        logger.error(f"Frames directory not found: {frames_dir}")
        return {'error': 'Frames directory not found'}
    
    # 获取所有帧文件
    frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.jpg') or f.endswith('.png')]
    if not frame_files:
        logger.error(f"No frame files found in: {frames_dir}")
        return {'error': 'No frame files found'}
    
    # 按帧号排序
    frame_files.sort(key=lambda x: int(x.split('.')[0]))
    
    # 获取最后一帧
    last_frame_file = frame_files[-1]
    last_frame_idx = int(last_frame_file.split('.')[0])
    last_frame_path = os.path.join(frames_dir, last_frame_file)
    
    logger.info(f"Analyzing loading status for last frame: {last_frame_path} (frame {last_frame_idx})")
    
    # 分析最后一帧的加载状态
    result = check_frame_loading_status_with_ui_infer(
        last_frame_path,
        last_frame_idx,
        horus_client,
        llm_client,
        target_classes=target_classes,
        model=model
    )
    
    # 添加额外信息
    result['segment_dir'] = segment_dir
    result['total_frames'] = len(frame_files)
    result['last_frame_file'] = last_frame_file
    
    return result

if __name__ == "__main__":
    # 示例用法
    print("Loading status checker module loaded successfully!")
    print("Use check_frame_loading_status_with_ui_infer() or analyze_segment_loading_status() functions.") 