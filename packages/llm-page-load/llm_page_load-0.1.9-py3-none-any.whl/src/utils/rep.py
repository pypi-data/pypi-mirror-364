from .llm_narrow_utils import *
from .llm_narrow_llm import *
from .llm_narrow_eval import *
import os
import json
import torch
import pandas as pd
import numpy as np
import cv2
import time
import re
from src.toolchain_llm.service.ui_detection.img_diff import ImageDiff
from src.toolchain_llm.service.ui_detection.line_feature_diff import line_feature_diff, get_ocr_result

try:
    from src.algorithms.find_page_load_intelligent import preprocess_ssim_data, find_page_load_intelligent
except ImportError as e:
    print(f"错误：无法从 'find_page_load_intelligent.py' 导入所需函数: {e}")
    print("请确保find_page_load_intelligent.py在Python的搜索路径中。")
    exit()

def llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, max_retries=5, retry_delay=5, model: str = "anthropic.claude-3.7-sonnet", temperature=0.1):
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
            if attempt < max_retries - 1:
                print(f"Rate limit exceeded, waiting {retry_delay} seconds before retry... Error: {e}")
                time.sleep(retry_delay)
                continue
            raise e

def llm_narrow_from_action_info(
    segment_dir,
    llm_client,
    window=3,
    do_evaluation=False,
    prompt_start="请分析当前帧是否是页面加载的【开始】帧。请结合图片内容和帧号，给出你的判断和理由。",
    prompt_end="请分析当前帧是否是页面加载的【结束】帧。请结合图片内容和帧号，给出你的判断和理由。"
):
    """
    使用LLM对SSIM算法检测到的页面加载时间进行精确判断
    """
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 获取操作描述
    action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    
    # 2. 加载和处理SSIM数据
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    if not os.path.exists(ssim_pt_path):
        raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_dir}")
    
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    
    # 3. 预处理SSIM数据
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    if not cleaned_ssim_data:
        raise ValueError("预处理后的SSIM数据为空")
    
    # 4. 计算平滑SSIM和斜率
    fps = action_info["extraction_parameters"]["fps"]
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    # 5. 获取开始帧的候选帧
    start_candidates, start_point_map = get_candidate_frames_for_start(cleaned_ssim_data, smoothed_ssim, slopes, 0.004, segment_dir)
    
    # 保存开始帧候选帧图片
    save_candidate_frames(segment_dir, start_candidates, "start_candidate_frames", "start")
    
    # 6. 处理开始帧
    refined_start = None
    llm_results_start = None
    
    # 加载所有候选帧图片
    start_images = []
    for idx in start_candidates:
        img = load_frame_from_npy(segment_dir, idx)
        if img is not None:
            start_images.append((idx, None, img))
    
    if start_images:
        refined_start, llm_results_start = llm_refine_event_frames_batch(
            llm_client, start_images, "response_start_time", prompt_start, 
            action_desc=action_desc, ssim_sequence=cleaned_ssim_data
        )
        if refined_start is not None and refined_start in start_point_map:
            refined_start = start_point_map[refined_start]
    
    # 7. 只有在找到开始帧后，才处理结束帧
    refined_end = None
    llm_results_end = None
    if refined_start is not None:
        # 获取结束帧的候选帧
        end_candidates = get_candidate_frames_for_end(
            cleaned_ssim_data, smoothed_ssim, slopes, refined_start, 0.004, 0.995
        )

        # 保存结束帧候选帧图片
        save_candidate_frames(segment_dir, end_candidates, "end_candidate_frames", "end")
        
        # 加载所有结束帧候选帧图片
        end_images = []
        for idx in end_candidates:
            img = load_frame_from_npy(segment_dir, idx)
            if img is not None:
                end_images.append((idx, None, img))
        
        if end_images:
            refined_end, llm_results_end = llm_refine_event_frames_batch(
                llm_client, end_images, "load_end_time", prompt_end,
                action_desc=action_desc, ssim_sequence=cleaned_ssim_data
            )
    
    # 8. 输出结果
    result_entry = {
        "segment_dir": segment_dir,
        "llm_refined_start_frame": refined_start,
        "llm_refined_end_frame": refined_end,
        "start_candidate_indices": start_candidates,
        "end_candidate_indices": end_candidates,
        "llm_results_start": llm_results_start,
        "llm_results_end": llm_results_end
    }
    
    if do_evaluation:
        evaluate_llm_narrow_results([result_entry])
    
    return result_entry

def llm_narrow_from_action_info_grid(
    segment_dir,
    llm_client,
    do_evaluation=False,
    activity_threshold=-0.0004,
    merge_window=3,
    start_threshold=-0.0001,
    end_threshold=-0.0001,
    ssim_threshold=0.995,
    model="gpt-4-vision-preview"
):
    """
    使用图片网格的版本，将所有候选帧拼接成一张图片进行判断
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        start_threshold: 开始点阈值，默认-0.0001
        end_threshold: 结束点阈值，默认-0.0001
        ssim_threshold: SSIM阈值，默认0.995
        model: 使用的模型名称，默认"gpt-4-vision-preview"
    """
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 获取操作描述
    action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    
    # 2. 加载和处理SSIM数据
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    if not os.path.exists(ssim_pt_path):
        raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_dir}")
    
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    
    # 3. 预处理SSIM数据
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    if not cleaned_ssim_data:
        raise ValueError("预处理后的SSIM数据为空")
    
    # 4. 计算平滑SSIM和斜率
    fps = action_info["extraction_parameters"]["fps"]
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    # 5. 获取开始帧的候选帧
    start_candidates, start_point_map = get_candidate_frames_for_start(
        cleaned_ssim_data, smoothed_ssim, slopes, 
        activity_threshold=activity_threshold,
        merge_window=merge_window,
        start_threshold=start_threshold
    )
    
    # 保存开始帧候选帧图片
    save_candidate_frames(segment_dir, start_candidates, "start_candidate_frames", "start")
    
    # 6. 加载所有开始帧候选帧图片
    start_images = []
    for idx in start_candidates:
        img = load_frame_from_npy(segment_dir, idx)
        if img is not None:
            start_images.append((idx, None, img))
    
    # 7. 创建开始帧网格图片
    start_grid = create_image_grid(start_images)
    
    # 保存开始帧网格图片
    if start_grid:
        grid_output_dir = os.path.join(segment_dir, "grid_images")
        os.makedirs(grid_output_dir, exist_ok=True)
        start_grid_path = os.path.join(grid_output_dir, "start_grid.png")
        start_grid.save(start_grid_path)
        print(f"已保存开始帧网格图片到: {start_grid_path}")
    
    # 8. 构建开始帧提示词
    start_prompt = (
        f"You are a helpful assistant that can help me analyze the page loading process after executing the operation. "
        f"Below is a grid of frames from a video showing the page loading process. "
        f"The frames are arranged from left to right, top to bottom.\n\n"
        f"## Context:\n"
        f"1. Action being performed: {action_desc}\n"
        f"2. Event type: response_start_time\n\n"
        f"## Definition of start frame:\n"
        f"1. The start frame is the first frame where the page shows loading actions after clicking\n"
        f"2. Loading actions include: button turning gray, page color changes, animations appearing, appearing some loading texts (e.g., 'loading', '正在加载中')\n"
        f"3. Loading is a process,you should choose the first pic from these pics,which shows the start of loading\n"
        f"4. There is a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
        f"## Task:\n"
        f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
        f"Pay special attention to:\n"
        f"- Small changes in UI elements\n"
        f"- Slight color variations\n"
        f"- Initial signs of loading indicators\n"
        f"- Any movement or animation starting to appear\n\n"
        f"Then, identify which frame shows the start of page loading.(start of change)\n"
        f"Please answer in JSON format:\n"
        f"{{\n"
        f"    \"frame_analysis\": [\n"
        f"        {{\"position\": 1, \"description\": \"Detailed description of subtle changes in first frame\"}},\n"
        f"        {{\"position\": 2, \"description\": \"Detailed description of subtle changes in second frame\"}},\n"
        f"        // ... continue for all frames\n"
        f"    ],\n"
        f"    \"target_position\": <position_number>,\n"
        f"    \"reason\": \"Detailed explanation of why this frame is the start frame,and why the others are not.\"\n"
        f"}}"
    )
    
    # 9. 处理开始帧
    refined_start = None
    llm_results_start = None
    position_to_start_frame_map = {i+1:idx for i,idx in enumerate(start_candidates)}
    print(start_candidates)
    print(position_to_start_frame_map)
    if start_grid:
        refined_start, llm_results_start = llm_refine_event_frames_grid(
            llm_client, [(0, None, start_grid)], "response_start_time", start_prompt,
            position_to_start_frame_map, model=model
        )
        if refined_start is not None and refined_start in start_point_map:
            refined_start = start_point_map[refined_start]
    
    # 10. 只有在找到开始帧后，才处理结束帧
    refined_end = None
    llm_results_end = None
    if refined_start is not None:
        # 获取结束帧的候选帧
        end_candidates = get_candidate_frames_for_end(
            cleaned_ssim_data, smoothed_ssim, slopes, refined_start,
            activity_threshold=activity_threshold,
            merge_window=merge_window,
            end_threshold=end_threshold
        )

        # 保存结束帧候选帧图片
        save_candidate_frames(segment_dir, end_candidates, "end_candidate_frames", "end")
        position_to_end_frame_map = {i+1:idx for i,idx in enumerate(end_candidates)}
        print(end_candidates)
        print(position_to_end_frame_map)
        
        # 加载所有结束帧候选帧图片
        end_images = []
        for idx in end_candidates:
            img = load_frame_from_npy(segment_dir, idx)
            if img is not None:
                end_images.append((idx, None, img))
        
        # 创建结束帧网格图片
        end_grid = create_image_grid(end_images)
        
        # 保存结束帧网格图片
        if end_grid:
            grid_output_dir = os.path.join(segment_dir, "grid_images")
            os.makedirs(grid_output_dir, exist_ok=True)
            end_grid_path = os.path.join(grid_output_dir, "end_grid.png")
            end_grid.save(end_grid_path)
            print(f"已保存结束帧网格图片到: {end_grid_path}")
        
        # 构建结束帧提示词
        end_prompt = (
            f"You are a helpful assistant that can help me analyze the page loading process after executing the operation. "
            f"Below is a grid of frames from a video showing the page loading process. "
            f"The frames are arranged from left to right, top to bottom.\n\n"
            f"## Context:\n"
            f"1. Action being performed: {action_desc}\n"
            f"2. Event type: load_end_time\n"
            f"3. Grid layout: Red border = Frame 0 (start), Blue border = Last frame (end), Gray borders = Candidate frames\n\n"
            f"## Definition of end frame:\n"
            f"1. The first end frame is the first frame where the page is fully loaded after the operation\n"
            f"2. The page must be completely loaded with no white spaces or loading indicators\n"
            f"3. The page must have changed from the previous page to the desired page after the operation\n"
            f"## Task:\n"
            f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
            f"  ##Pay special attention to:\n"
            f"- Small changes in UI elements\n"
            f"- Slight color variations\n"
            f"- Loading indicators disappearing\n"
            f"- White spaces or loading elements being filled\n\n"
            f"- ##Ignorging:\n"
            f"- Any banner movement or animation changing or advertisement image changing\n"
            f"- Minor non-content visual changes\n"
            f"- Floating elements such as floating buttons which may be testing components\n"
            f"- There may be a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
            f"- Scrolling of small texts\n"
            f"Then, identify which frame shows the end of page loading.(end of change,first frame after all changes)\n"
            f"## IMPORTANT: You must choose from the candidate frames (gray borders) only. Do NOT select the start frame (red border) or the end frame (blue border) - they are only for reference.\n"
            f"Please answer in JSON format:\n"
            f"{{\n"
            f"    \"frame_analysis\": [\n"
            f"        {{\"position\": 1, \"description\": \"Detailed description of subtle changes in first frame\"}},\n"
            f"        {{\"position\": 2, \"description\": \"Detailed description of subtle changes in second frame\"}},\n"
            f"        // ... continue for all frames\n"
            f"    ],\n"
            f"    \"target_position\": <position_number>,\n"
            f"    \"reason\": \"Detailed explanation of why this frame is the end frame,and why the others are not.\"\n"
            f"}}"
        )
        
        if end_grid:
            refined_end, llm_results_end = llm_refine_event_frames_grid(
                llm_client, [(0, None, end_grid)], "load_end_time", end_prompt,
                position_to_end_frame_map, model=model
            )
    
    # 11. 输出结果
    result_entry = {
        "segment_dir": segment_dir,
        "llm_refined_start_frame": refined_start,
        "llm_refined_end_frame": refined_end,
        "start_candidate_indices": start_candidates,
        "end_candidate_indices": end_candidates,
        "llm_results_start": llm_results_start,
        "llm_results_end": llm_results_end
    }
    
    if do_evaluation:
        evaluate_llm_narrow_results([result_entry])
    
    return result_entry

def llm_narrow_end_frame_step(segment_dir: str, llm_client, do_evaluation: bool = False, activity_threshold: float = -0.001,model: str = "anthropic.claude-3.7-sonnet"):
    """
    使用二分法查找页面加载结束帧。
    左边界初始是action_time，右边界初始是最后一帧。
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        model: 使用的模型名称，默认"anthropic.claude-3.7-sonnet"
    
    Returns:
        tuple: (end_frame, llm_results, image_path_list, messages)
    """
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 2. 获取最后一帧作为参考
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
    if last_frame is None:
        raise ValueError("无法加载最后一帧")
    
    # 3. 获取起始帧（action_time对应的帧）
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    fps = action_info["extraction_parameters"]["fps"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    # 4. 创建实验文件夹
    experiment_dir = os.path.join(segment_dir, f"experiment_binary_{int(time.time())}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # 5. 初始化二分查找的边界
    left = start_frame
    right = num_frames - 1
    step_count = 0
    last_fully_loaded_frame = None
    last_fully_loaded_resp = None
    last_fully_loaded_images = None
    
    # 保存初始信息
    with open(os.path.join(experiment_dir, "binary_search_info.json"), "w", encoding="utf-8") as f:
        json.dump({
            "start_frame": start_frame,
            "end_frame": num_frames - 1,
            "fps": fps,
            "activity_threshold": activity_threshold,
            "model": model
        }, f, indent=4, ensure_ascii=False)
    
    while left <= right:
        time.sleep(10)
        step_count += 1
        # 计算中间帧
        mid = (left + right) // 2
        current_frame = load_frame_from_npy(segment_dir, mid)
        if current_frame is None:
            raise ValueError(f"无法加载帧 {mid}")
        
        # 为每一步创建子文件夹
        step_dir = os.path.join(experiment_dir, f"step_{step_count:03d}")
        os.makedirs(step_dir, exist_ok=True)
        
        # 保存当前帧、参考帧和差异图
        current_path = os.path.join(step_dir, f"current_{mid}.png")
        ref_path = os.path.join(step_dir, f"ref_{num_frames-1}.png")
        diff_path = os.path.join(step_dir, f"diff_{mid}.png")
        
        current_frame.save(current_path)
        last_frame.save(ref_path)
        img1 = cv2.imread(current_path)
        img2 = cv2.imread(ref_path)
        diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
        if isinstance(diff_image_url_or_np, np.ndarray):
            cv2.imwrite(diff_path, diff_image_url_or_np)
        elif isinstance(diff_image_url_or_np, str):
            with open(os.path.join(step_dir, "diff_image_url.txt"), "w") as f:
                f.write(diff_image_url_or_np)
        
        # 保存当前步骤的信息
        step_info = {
            "frame_index": mid,
            "left_boundary": left,
            "right_boundary": right,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(os.path.join(step_dir, "step_info.json"), "w", encoding="utf-8") as f:
            json.dump(step_info, f, indent=4, ensure_ascii=False)
        
        image_path_list = [current_path, ref_path, diff_path]
        action_desc = action_info["original_action_item"]["action_desc"]
        
        # 构建提示词
        user_prompt = (
            f"You are a helpful assistant tasked with analyzing whether a webpage has fully loaded after a user action.\n"
            f"## Context:\n"
            f"- Action performed: {action_desc}\n"
            f"- Current frame index: {mid}\n"
            f"- You are given three images:\n"
            f"    1. The current frame to evaluate\n"
            f"    2. A reference frame showing the expected loaded state\n"
            f"    3. A difference image highlighting changes (with red boxes marking differences)\n"
            f"\n"
            f"## Task:\n"
            f"Determine whether the current frame represents a fully loaded page.\n"
            f"- If the page is **not** fully loaded, suggest looking to the **right** (i.e., later frames)\n"
            f"- If the page **is** fully loaded, suggest looking to the **left** (i.e., earlier frames to find the start)\n"
            f"\n"
            f"## Notes:\n"
            f"- Ensure that **all required page components** (e.g., text, buttons, main layout, Overall framework, key UI Components) are present.\n"
            f"- **Ignore non-essential differences**, such as:\n"
            f"  - Animations\n"
            f"  - Banner or ad rotations\n"
            f"  - Minor non-content visual changes\n"
            f"  - Floating elements such as floating buttons which may be testing components\n"
            f"\n"
            f"Please respond strictly in the following JSON format:\n"
            f"{{\n"
            f"  \"is_fully_loaded\": true/false,\n"
            f"  \"direction\": \"left\"/\"right\",\n"
            f"  \"reason\": \"Your detailed reasoning here. Be specific about what elements are present or missing, and why.\"\n"
            f"}}"
        )
        messages = []
        messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
        resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=2048, model=model)
        
        # 保存LLM响应
        with open(os.path.join(step_dir, "llm_response.json"), "w", encoding="utf-8") as f:
            json.dump({"response": resp}, f, indent=4, ensure_ascii=False)
        
        try:
            resp_json = json.loads(resp)
        except:
            pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
            match = re.search(pattern, resp)
            if match:
                resp_json = json.loads(match.group(1))
            else:
                raise ValueError(f"无法解析LLM响应: {resp}")
        
        if resp_json.get("is_fully_loaded", False):
            # 记录最后一个完全加载的帧
            last_fully_loaded_frame = mid
            last_fully_loaded_resp = resp
            last_fully_loaded_images = image_path_list
            right = mid - 1  # 继续向左搜索，寻找第一个完全加载的帧
        else:
            left = mid + 1  # 向右搜索，寻找完全加载的帧
    
    # 二分查找结束后，使用最后一个完全加载的帧
    if last_fully_loaded_frame is not None:
        if do_evaluation:
            # 获取ground truth帧号
            marked_end_time = action_info["original_action_item"]["marked_end_time"]
            gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
            gt_end_frame = max(0, gt_end_frame)
            
            # 构建评估结果
            result_entry = {
                "segment_dir": segment_dir,
                "llm_refined_start_frame": start_frame,
                "llm_refined_end_frame": last_fully_loaded_frame,
                "llm_results_end": last_fully_loaded_resp
            }
            
            # 执行评估
            evaluate_llm_narrow_results([result_entry])
        
        return last_fully_loaded_frame, last_fully_loaded_resp, last_fully_loaded_images, messages
    
    # 如果没有找到完全加载的帧，返回最后一个检查的帧
    if do_evaluation:
        marked_end_time = action_info["original_action_item"]["marked_end_time"]
        gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
        gt_end_frame = max(0, gt_end_frame)
        
        result_entry = {
            "segment_dir": segment_dir,
            "llm_refined_start_frame": start_frame,
            "llm_refined_end_frame": mid,
            "llm_results_end": resp
        }
        
        evaluate_llm_narrow_results([result_entry])
    
    return mid, resp, image_path_list, messages

def llm_narrow_end_frame_ssim(
    segment_dir: str, 
    llm_client,
    activity_threshold: float = -0.001,
    merge_window: int = 3,
    end_threshold: float = -0.0001,
    ssim_threshold: float = 0.995,
    model: str = "anthropic.claude-3.7-sonnet",
    do_evaluation: bool = False
):
    """
    Narrow down the end frame using candidate frames and comparison with the last frame.
    This method moves between candidate frames.
    
    Args:
        segment_dir: Directory containing the video segment
        llm_client: LLM client instance
        activity_threshold: Threshold for activity detection
        merge_window: Window size for merging nearby points
        end_threshold: Threshold for end point detection
        ssim_threshold: SSIM threshold for stability
        model: Model name to use
        do_evaluation: Whether to perform evaluation against ground truth
    
    Returns:
        tuple: (end_frame, llm_results, image_path_list, messages)
    """
    # 1. Load action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 2. Get the last frame as reference
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
    if last_frame is None:
        raise ValueError("Failed to load the last frame")
    
    # 3. Get SSIM data
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    
    # Get start frame from action_time
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    fps = action_info["extraction_parameters"]["fps"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    # Get candidate frames
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    end_candidates = get_candidate_frames_for_end(
        cleaned_ssim_data, smoothed_ssim, slopes, start_frame,
        activity_threshold=activity_threshold,
        merge_window=merge_window,
        end_threshold=end_threshold
    )
    
    if not end_candidates:
        raise ValueError("No end frame candidates found")
    
    # 创建实验文件夹
    experiment_dir = os.path.join(segment_dir, f"experiment_ssim_{int(time.time())}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # 保存候选帧信息
    with open(os.path.join(experiment_dir, "candidates_info.json"), "w", encoding="utf-8") as f:
        json.dump({
            "start_frame": start_frame,
            "end_candidates": end_candidates,
            "activity_threshold": activity_threshold,
            "merge_window": merge_window,
            "end_threshold": end_threshold,
            "ssim_threshold": ssim_threshold,
            "model": model
        }, f, indent=4, ensure_ascii=False)
    
    current_frame_idx = end_candidates[0]
    current_candidate_index = 0
    last_direction = None
    messages = []
    step_count = 0
    while True:
        step_count += 1
        current_frame = load_frame_from_npy(segment_dir, current_frame_idx)
        if current_frame is None:
            raise ValueError(f"Failed to load frame {current_frame_idx}")
        
        # 为每一步创建子文件夹
        step_dir = os.path.join(experiment_dir, f"step_{step_count:03d}")
        os.makedirs(step_dir, exist_ok=True)
        
        # 保存当前帧、参考帧和差异图
        current_path = os.path.join(step_dir, f"current_{current_frame_idx}.png")
        ref_path = os.path.join(step_dir, f"ref_{num_frames-1}.png")
        diff_path = os.path.join(step_dir, f"diff_{current_frame_idx}.png")
        
        current_frame.save(current_path)
        last_frame.save(ref_path)
        img1 = cv2.imread(current_path)
        img2 = cv2.imread(ref_path)
        diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
        if isinstance(diff_image_url_or_np, np.ndarray):
            cv2.imwrite(diff_path, diff_image_url_or_np)
        elif isinstance(diff_image_url_or_np, str):
            with open(os.path.join(step_dir, "diff_image_url.txt"), "w") as f:
                f.write(diff_image_url_or_np)
        
        # 保存当前步骤的信息
        step_info = {
            "frame_index": current_frame_idx,
            "candidate_index": current_candidate_index,
            "direction": last_direction,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(os.path.join(step_dir, "step_info.json"), "w", encoding="utf-8") as f:
            json.dump(step_info, f, indent=4, ensure_ascii=False)
        
        image_path_list = [current_path, ref_path, diff_path]
        action_desc = action_info["original_action_item"]["action_desc"]
        user_prompt = (
            f"You are a helpful assistant that can help me analyze the page loading process after executing the operation. "
            f"## Context:\n"
            f"Action being performed: {action_desc}\n"
            f"current frame index: {current_frame_idx}\n"
            f"The three pictures are the picture to be judged, the loading status (reference), and the difference between the two pictures\n"
            f"Determine whether the current frame image is the first frame after loading. If not (if it is not loaded, you need to look to the right, or if it is loaded but not the first frame, you need to look to the left)\n"
            f"You must make sure that this frame is the first frame after loading. It cannot be the frame that has not been loaded or has been loaded for a while. So you need to see the left and right of this frame before drawing a conclusion.\n"
            f"You must make sure that all the needed components are loaded. If there is some difference,you need to explain why\n"
            f"Please answer strictly according to the following JSON format:\n"
            f"{{\n"
            f"  \"is_fully_loaded\": true/false,\n"
            f"  \"direction\": \"left\"/\"right\"/\"found\",\n"
            f"  \"reason\": \"Your detailed judgment reason\"\n"
            f"}}"
        )
        messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
        resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
        messages.append({"role": "assistant", "content": resp})
        
        # 保存LLM响应
        with open(os.path.join(step_dir, "llm_response.json"), "w", encoding="utf-8") as f:
            json.dump({"response": resp}, f, indent=4, ensure_ascii=False)
        
        try:
            resp_json = json.loads(resp)
        except:
            pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
            match = re.search(pattern, resp)
            if match:
                resp_json = json.loads(match.group(1))
            else:
                raise ValueError(f"Failed to parse LLM response: {resp}")
        
        if resp_json.get("is_fully_loaded", False):
            if do_evaluation:
                # 获取ground truth帧号
                marked_end_time = action_info["original_action_item"]["marked_end_time"]
                gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
                gt_end_frame = max(0, gt_end_frame)
                
                # 构建评估结果
                result_entry = {
                    "segment_dir": segment_dir,
                    "llm_refined_start_frame": start_frame,
                    "llm_refined_end_frame": current_frame_idx,
                    "end_candidate_indices": end_candidates,
                    "llm_results_end": resp
                }
                
                # 执行评估
                evaluate_llm_narrow_results([result_entry])
            
            return current_frame_idx, resp, image_path_list, messages
        direction = resp_json.get("direction")
        if direction == "found":
            if do_evaluation:
                # 获取ground truth帧号
                marked_end_time = action_info["original_action_item"]["marked_end_time"]
                gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
                gt_end_frame = max(0, gt_end_frame)
                
                # 构建评估结果
                result_entry = {
                    "segment_dir": segment_dir,
                    "llm_refined_start_frame": start_frame,
                    "llm_refined_end_frame": current_frame_idx,
                    "end_candidate_indices": end_candidates,
                    "llm_results_end": resp
                }
                
                # 执行评估
                evaluate_llm_narrow_results([result_entry])
            
            return current_frame_idx, resp, image_path_list, messages
        if direction == "left":
            if current_candidate_index > 0:
                current_candidate_index -= 1
                current_frame_idx = end_candidates[current_candidate_index]
        elif direction == "right":
            if current_candidate_index < len(end_candidates) - 1:
                current_candidate_index += 1
                current_frame_idx = end_candidates[current_candidate_index]
        else:
            raise ValueError(f"Invalid direction: {direction}")
        last_direction = direction

def llm_narrow_end_frame_step_with_recheck(segment_dir: str, llm_client, do_evaluation: bool = False, activity_threshold: float = -0.001, model: str = "gemini-2.5-pro-preview-03-25"):
    """
    使用二分法查找页面加载结束帧，并带有recheck机制。
    在step method得到结果后，检查左边第10帧和右边第10帧的加载状态来验证结果。
    每次recheck都新建独立的experiment子文件夹。
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        model: 使用的模型名称，默认"gemini-2.5-pro-preview-03-25"
    
    Returns:
        tuple: (end_frame, llm_results, image_path_list, messages)
    """
    import time
    import os
    import json
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 2. 获取基本信息
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    fps = action_info["extraction_parameters"]["fps"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    recheck_count = 0
    max_rechecks = 3  # 最大recheck次数
    last_left_bound = None
    last_right_bound = None
    final_result = None
    
    while recheck_count < max_rechecks:
        recheck_count += 1
        print(f"第{recheck_count}次step method + recheck")
        # 每次recheck新建独立experiment子文件夹
        experiment_dir = os.path.join(segment_dir, f"experiment_binary_recheck_{int(time.time())}_recheck{recheck_count}")
        os.makedirs(experiment_dir, exist_ok=True)
        
        # 确定当前搜索范围
        if recheck_count == 1:
            current_left = start_frame
            current_right = num_frames - 1
        else:
            current_left = last_left_bound
            current_right = last_right_bound
        
        def check_frame_loading_status(frame_idx):
            if frame_idx < 0 or frame_idx >= num_frames:
                return False
            current_frame = load_frame_from_npy(segment_dir, frame_idx)
            if current_frame is None:
                return False
            last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
            if last_frame is None:
                return False
            current_path = os.path.join(experiment_dir, f"check_current_{frame_idx}.png")
            ref_path = os.path.join(experiment_dir, f"check_ref_{num_frames-1}.png")
            diff_path = os.path.join(experiment_dir, f"check_diff_{frame_idx}.png")
            current_frame.save(current_path)
            last_frame.save(ref_path)
            img1 = cv2.imread(current_path)
            img2 = cv2.imread(ref_path)
            diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
            if isinstance(diff_image_url_or_np, np.ndarray):
                cv2.imwrite(diff_path, diff_image_url_or_np)
            elif isinstance(diff_image_url_or_np, str):
                with open(os.path.join(experiment_dir, f"check_diff_url_{frame_idx}.txt"), "w") as f:
                    f.write(diff_image_url_or_np)
            # 先用get_ocr_result获取ocr_result
            ocr_result = get_ocr_result(img1, img2)
            img_diff_obj = ImageDiff(img1, img2, ocr_result)
            score = img_diff_obj.get_similar_score([])
            if score == 1.0:
                return True
            # 否则送LLM
            image_path_list = [current_path, ref_path, diff_path]
            action_desc = action_info["original_action_item"]["action_desc"]
            user_prompt = (
                f"You are a helpful assistant tasked with analyzing whether a webpage has fully loaded after a user action.\n"
                f"## Context:\n"
                f"- Action performed: {action_desc}\n"
                f"- Current frame index: {frame_idx}\n"
                f"- You are given three images:\n"
                f"    1. The current frame to evaluate\n"
                f"    2. A reference frame showing the expected loaded state\n"
                f"    3. A difference image highlighting changes (with red boxes marking differences)\n"
                f"\n"
                f"## Task:\n"
                f"Determine whether the current frame represents a fully loaded page.\n"
                f"- If the page is **not** fully loaded, suggest looking to the **right** (i.e., later frames)\n"
                f"- If the page **is** fully loaded, suggest looking to the **left** (i.e., earlier frames to find the start)\n"
                f"\n"
                f"## Notes:\n"
                f"- Ensure that **all required page components** (e.g., text, buttons, main layout, Overall framework, key UI Components) are present.\n"
                f"- **Ignore non-essential differences**, such as:\n"
                f"  - Animations\n"
                f"  - Banner or ad rotations\n"
                f"  - Minor non-content visual changes\n"
                f"  - Floating elements such as floating buttons which may be testing components\n"
                f"\n"
                f"Please respond strictly in the following JSON format:\n"
                f"{{\n"
                f"  \"is_fully_loaded\": true/false,\n"
                f"  \"direction\": \"left\"/\"right\",\n"
                f"  \"reason\": \"Your detailed reasoning here. Be specific about what elements are present or missing, and why.\"\n"
                f"}}"
            )
            messages = []
            messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
            resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
            try:
                resp_json = json.loads(resp)
            except:
                import re
                pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                match = re.search(pattern, resp)
                if match:
                    resp_json = json.loads(match.group(1))
                else:
                    raise ValueError(f"无法解析LLM响应: {resp}")
            return resp_json.get("is_fully_loaded", False)
        
        def run_step_method_in_range(left_bound, right_bound):
            left = left_bound
            right = right_bound
            step_count = 0
            last_fully_loaded_frame = None
            while left <= right:
                time.sleep(10)
                step_count += 1
                mid = (left + right) // 2
                current_frame = load_frame_from_npy(segment_dir, mid)
                if current_frame is None:
                    raise ValueError(f"无法加载帧 {mid}")
                step_dir = os.path.join(experiment_dir, f"step_{step_count:03d}")
                os.makedirs(step_dir, exist_ok=True)
                current_path = os.path.join(step_dir, f"current_{mid}.png")
                ref_path = os.path.join(step_dir, f"ref_{num_frames-1}.png")
                diff_path = os.path.join(step_dir, f"diff_{mid}.png")
                current_frame.save(current_path)
                last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
                last_frame.save(ref_path)
                img1 = cv2.imread(current_path)
                img2 = cv2.imread(ref_path)
                diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
                if isinstance(diff_image_url_or_np, np.ndarray):
                    cv2.imwrite(diff_path, diff_image_url_or_np)
                elif isinstance(diff_image_url_or_np, str):
                    with open(os.path.join(step_dir, "diff_image_url.txt"), "w") as f:
                        f.write(diff_image_url_or_np)
                # 先用get_ocr_result获取ocr_result
                ocr_result = get_ocr_result(img1, img2)
                img_diff_obj = ImageDiff(img1, img2, ocr_result)
                score = img_diff_obj.get_similar_score([])
                if score == 1.0:
                    last_fully_loaded_frame = mid
                    right = mid - 1
                    continue
                # 否则送LLM
                image_path_list = [current_path, ref_path, diff_path]
                action_desc = action_info["original_action_item"]["action_desc"]
                user_prompt = (
                    f"You are a helpful assistant tasked with analyzing whether a webpage has fully loaded after a user action.\n"
                    f"## Context:\n"
                    f"- Action performed: {action_desc}\n"
                    f"- Current frame index: {mid}\n"
                    f"- You are given three images:\n"
                    f"    1. The current frame to evaluate\n"
                    f"    2. A reference frame showing the expected loaded state\n"
                    f"    3. A difference image highlighting changes (with red boxes marking differences)\n"
                    f"\n"
                    f"## Task:\n"
                    f"Determine whether the current frame represents a fully loaded page.\n"
                    f"- If the page is **not** fully loaded, suggest looking to the **right** (i.e., later frames)\n"
                    f"- If the page **is** fully loaded, suggest looking to the **left** (i.e., earlier frames to find the start)\n"
                    f"\n"
                    f"## Notes:\n"
                    f"- Ensure that **all required page components** (e.g., text, buttons, main layout, Overall framework, key UI Components) are present.\n"
                    f"- **Ignore non-essential differences**, such as:\n"
                    f"  - Animations\n"
                    f"  - Banner or ad rotations\n"
                    f"  - Minor non-content visual changes\n"
                    f"  - Floating elements such as floating buttons which may be testing components\n"
                    f"\n"
                    f"Please respond strictly in the following JSON format:\n"
                    f"{{\n"
                    f"  \"is_fully_loaded\": true/false,\n"
                    f"  \"direction\": \"left\"/\"right\",\n"
                    f"  \"reason\": \"Your detailed reasoning here. Be specific about what elements are present or missing, and why.\"\n"
                    f"}}"
                )
                messages = []
                messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
                resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
                with open(os.path.join(step_dir, "llm_response.json"), "w", encoding="utf-8") as f:
                    json.dump({"response": resp}, f, indent=4, ensure_ascii=False)
                try:
                    resp_json = json.loads(resp)
                except:
                    import re
                    pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                    match = re.search(pattern, resp)
                    if match:
                        resp_json = json.loads(match.group(1))
                    else:
                        raise ValueError(f"无法解析LLM响应: {resp}")
                if resp_json.get("is_fully_loaded", False):
                    last_fully_loaded_frame = mid
                    right = mid - 1
                else:
                    left = mid + 1
            return last_fully_loaded_frame if last_fully_loaded_frame is not None else mid
        
        # 运行step method
        result_frame = run_step_method_in_range(current_left, current_right)
        
        if result_frame is None:
            print(f"Step method未找到结果，返回最后一帧")
            result_frame = num_frames - 1
        
        # 检查左边第10帧和右边第10帧
        left_check_frame = max(0, result_frame - 10)
        right_check_frame = min(num_frames - 1, result_frame + 10)
        
        print(f"检查帧 {result_frame}，左边第10帧: {left_check_frame}，右边第10帧: {right_check_frame}")
        
        # 检查左边帧
        left_loaded = check_frame_loading_status(left_check_frame)
        print(f"左边帧 {left_check_frame} 加载状态: {left_loaded}")
        
        # 检查右边帧
        right_loaded = check_frame_loading_status(right_check_frame)
        print(f"右边帧 {right_check_frame} 加载状态: {right_loaded}")
        
        # 根据recheck结果决定下一步
        if not left_loaded and right_loaded:
            # 情况1：左边没加载完，右边加载完，答案正确
            print(f"Recheck通过：左边未加载完成，右边已加载完成")
            final_result = result_frame
            break
        elif left_loaded and right_loaded:
            # 情况2：左边加载完，右边加载完，答案可能不正确，正确答案可能在左边
            print(f"Recheck失败：两边都已加载完成，在左边重新搜索")
            last_left_bound = start_frame
            last_right_bound = result_frame - 1
            continue
        elif left_loaded and not right_loaded:
            # 情况3：左边加载完，右边没加载完，重新recheck
            print(f"Recheck失败：左边已加载完成，右边未加载完成，重新recheck")
            last_left_bound = left_check_frame
            last_right_bound = right_check_frame
            continue
        else:  # not left_loaded and not right_loaded
            # 情况4：左边没加载完，右边没加载完，答案可能不正确，正确答案可能在右边
            print(f"Recheck失败：两边都未加载完成，在右边重新搜索")
            last_left_bound = result_frame + 1
            last_right_bound = num_frames - 1
            continue
    else:
        # 达到最大recheck次数，返回最后一次的结果
        print(f"达到最大recheck次数({max_rechecks})，返回最后一次结果")
        final_result = result_frame
    
    # 保存最终结果信息
    with open(os.path.join(experiment_dir, "final_result.json"), "w", encoding="utf-8") as f:
        json.dump({
            "final_end_frame": final_result,
            "recheck_count": recheck_count,
            "start_frame": start_frame,
            "end_frame": num_frames - 1,
            "fps": fps,
            "activity_threshold": activity_threshold,
            "model": model
        }, f, indent=4, ensure_ascii=False)
    
    if do_evaluation:
        marked_end_time = action_info["original_action_item"]["marked_end_time"]
        gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
        gt_end_frame = max(0, gt_end_frame)
        result_entry = {
            "segment_dir": segment_dir,
            "llm_refined_start_frame": start_frame,
            "llm_refined_end_frame": final_result,
            "llm_results_end": f"Recheck method with {recheck_count} iterations"
        }
        evaluate_llm_narrow_results([result_entry])
    
    return final_result, f"Recheck method with {recheck_count} iterations", [], []

def llm_narrow_end_frame_step_with_recheck_ocr(segment_dir: str, llm_client, do_evaluation: bool = False, activity_threshold: float = -0.001, model: str = "gemini-2.5-pro-preview-03-25", ocr_filter_score: float = 0.6):
    """
    使用二分法查找页面加载结束帧，并带有recheck机制和OCR文字识别功能。
    在step method得到结果后，检查左边第10帧和右边第10帧的加载状态来验证结果。
    同时使用OCR识别文字内容，帮助判断页面是否完全加载。
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        model: 使用的模型名称，默认"gemini-2.5-pro-preview-03-25"
        ocr_filter_score: OCR置信度过滤阈值，默认0.6
    
    Returns:
        tuple: (end_frame, llm_results, image_path_list, messages)
    """
    # 导入OCR相关模块
    from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
    
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 2. 获取基本信息
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    fps = action_info["extraction_parameters"]["fps"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    # 3. 创建实验文件夹
    experiment_dir = os.path.join(segment_dir, f"experiment_binary_recheck_ocr_{int(time.time())}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # 4. 初始化OCR客户端
    ocr_client = ClientHorus()
    
    def get_ocr_text_content(image_path):
        """
        获取图片的OCR文字内容
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: OCR识别的文字内容
        """
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                return ""
            
            # 调用OCR
            ocr_result = ocr_client.get_ocr(img, ocr_filter_score=ocr_filter_score)
            
            if ocr_result['code'] == 0:
                # 提取所有文字内容
                text_list = []
                for roi_text in ocr_result['data']['roi_text']:
                    text_list.append(roi_text['text'])
                return " ".join(text_list)
            else:
                return ""
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return ""
    
    def check_frame_loading_status_with_ocr(frame_idx):
        """
        检查指定帧的加载状态，包含OCR文字识别
        
        Args:
            frame_idx: 要检查的帧索引
            
        Returns:
            bool: True表示已加载完成，False表示未加载完成
        """
        if frame_idx < 0 or frame_idx >= num_frames:
            return False
            
        current_frame = load_frame_from_npy(segment_dir, frame_idx)
        if current_frame is None:
            return False
            
        last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
        if last_frame is None:
            return False
        
        # 保存当前帧、参考帧和差异图
        current_path = os.path.join(experiment_dir, f"check_current_{frame_idx}.png")
        ref_path = os.path.join(experiment_dir, f"check_ref_{num_frames-1}.png")
        diff_path = os.path.join(experiment_dir, f"check_diff_{frame_idx}.png")
        
        current_frame.save(current_path)
        last_frame.save(ref_path)
        
        # 生成差异图
        img1 = cv2.imread(current_path)
        img2 = cv2.imread(ref_path)
        diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
        if isinstance(diff_image_url_or_np, np.ndarray):
            cv2.imwrite(diff_path, diff_image_url_or_np)
        elif isinstance(diff_image_url_or_np, str):
            with open(os.path.join(experiment_dir, f"check_diff_url_{frame_idx}.txt"), "w") as f:
                f.write(diff_image_url_or_np)
        
        # 获取OCR文字内容
        current_ocr_text = get_ocr_text_content(current_path)
        ref_ocr_text = get_ocr_text_content(ref_path)
        
        # 保存OCR结果
        ocr_info = {
            "current_frame_ocr": current_ocr_text,
            "reference_frame_ocr": ref_ocr_text,
            "ocr_filter_score": ocr_filter_score
        }
        with open(os.path.join(experiment_dir, f"check_ocr_{frame_idx}.json"), "w", encoding="utf-8") as f:
            json.dump(ocr_info, f, indent=4, ensure_ascii=False)
        
        image_path_list = [current_path, ref_path, diff_path]
        action_desc = action_info["original_action_item"]["action_desc"]
        
        # 构建包含OCR信息的提示词
        user_prompt = (
            f"You are a helpful assistant tasked with analyzing whether a webpage has fully loaded after a user action.\n"
            f"## Context:\n"
            f"- Action performed: {action_desc}\n"
            f"- Current frame index: {frame_idx}\n"
            f"- You are given three images:\n"
            f"    1. The current frame to evaluate\n"
            f"    2. A reference frame showing the expected loaded state\n"
            f"    3. A difference image highlighting changes (with red boxes marking differences)\n"
            f"\n"
            f"## OCR Text Content:\n"
            f"- Current frame OCR text: \"{current_ocr_text}\"\n"
            f"- Reference frame OCR text: \"{ref_ocr_text}\"\n"
            f"\n"
            f"## Task:\n"
            f"Determine whether the current frame represents a fully loaded page.\n"
            f"\n"
            f"## Important Guidelines for Text Content Analysis:\n"
            f"1. **Focus on text differences ONLY in areas marked with red boxes in the diff image**\n"
            f"2. **Ignore text differences in non-critical UI areas** (e.g., banners, ads, floating elements)\n"
            f"3. **Key UI text content should match** between current and reference frames\n"
            f"4. **Non-essential text differences should be ignored** (e.g., timestamps, dynamic content)\n"
            f"5. **Consider OCR accuracy** - minor OCR errors should not affect the judgment\n"
            f"\n"
            f"## Notes:\n"
            f"- Ensure that **all required page components** (e.g., text, buttons, main layout, Overall framework, key UI Components) are present.\n"
            f"- **Ignore non-essential differences**, such as:\n"
            f"  - Animations\n"
            f"  - Banner or ad rotations\n"
            f"  - Minor non-content visual changes\n"
            f"  - Floating elements such as floating buttons which may be testing components\n"
            f"  - Text differences in non-critical areas (unless marked in diff image)\n"
            f"\n"
            f"Please respond strictly in the following JSON format:\n"
            f"{{\n"
            f"  \"is_fully_loaded\": true/false,\n"
            f"  \"text_analysis\": \"Your analysis of text content differences, focusing on critical UI elements\",\n"
            f"  \"reason\": \"Your detailed reasoning here. Be specific about what elements are present or missing, and why.\"\n"
            f"}}"
        )
        
        messages = []
        messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
        resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
        
        try:
            resp_json = json.loads(resp)
        except:
            pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
            match = re.search(pattern, resp)
            if match:
                resp_json = json.loads(match.group(1))
            else:
                raise ValueError(f"无法解析LLM响应: {resp}")
        
        return resp_json.get("is_fully_loaded", False)
    
    def run_step_method_in_range_with_ocr(left_bound, right_bound):
        """
        在指定范围内运行step method，包含OCR功能
        
        Args:
            left_bound: 左边界
            right_bound: 右边界
            
        Returns:
            int: 找到的结束帧
        """
        left = left_bound
        right = right_bound
        step_count = 0
        last_fully_loaded_frame = None
        
        while left <= right:
            time.sleep(10)  # 避免API限制
            step_count += 1
            mid = (left + right) // 2
            current_frame = load_frame_from_npy(segment_dir, mid)
            if current_frame is None:
                raise ValueError(f"无法加载帧 {mid}")
            
            # 为每一步创建子文件夹
            step_dir = os.path.join(experiment_dir, f"step_{step_count:03d}")
            os.makedirs(step_dir, exist_ok=True)
            
            # 保存当前帧、参考帧和差异图
            current_path = os.path.join(step_dir, f"current_{mid}.png")
            ref_path = os.path.join(step_dir, f"ref_{num_frames-1}.png")
            diff_path = os.path.join(step_dir, f"diff_{mid}.png")
            
            current_frame.save(current_path)
            last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
            last_frame.save(ref_path)
            
            img1 = cv2.imread(current_path)
            img2 = cv2.imread(ref_path)
            diff_result, diff_image_url_or_np = line_feature_diff(img1, img2, business=None)
            if isinstance(diff_image_url_or_np, np.ndarray):
                cv2.imwrite(diff_path, diff_image_url_or_np)
            elif isinstance(diff_image_url_or_np, str):
                with open(os.path.join(step_dir, "diff_image_url.txt"), "w") as f:
                    f.write(diff_image_url_or_np)
            
            # 获取OCR文字内容
            current_ocr_text = get_ocr_text_content(current_path)
            ref_ocr_text = get_ocr_text_content(ref_path)
            
            # 保存OCR结果
            ocr_info = {
                "current_frame_ocr": current_ocr_text,
                "reference_frame_ocr": ref_ocr_text,
                "ocr_filter_score": ocr_filter_score
            }
            with open(os.path.join(step_dir, "ocr_info.json"), "w", encoding="utf-8") as f:
                json.dump(ocr_info, f, indent=4, ensure_ascii=False)
            
            image_path_list = [current_path, ref_path, diff_path]
            action_desc = action_info["original_action_item"]["action_desc"]
            
            user_prompt = (
                f"You are a helpful assistant tasked with analyzing whether a webpage has fully loaded after a user action.\n"
                f"## Context:\n"
                f"- Action performed: {action_desc}\n"
                f"- Current frame index: {mid}\n"
                f"- You are given three images:\n"
                f"    1. The current frame to evaluate\n"
                f"    2. A reference frame showing the expected loaded state\n"
                f"    3. A difference image highlighting changes (with red boxes marking differences)\n"
                f"\n"
                f"## OCR Text Content:\n"
                f"- Current frame OCR text: \"{current_ocr_text}\"\n"
                f"- Reference frame OCR text: \"{ref_ocr_text}\"\n"
                f"\n"
                f"## Task:\n"
                f"Determine whether the current frame represents a fully loaded page.\n"
                f"\n"
                f"## Important Guidelines for Text Content Analysis:\n"
                f"1. **Focus on text differences ONLY in areas marked with red boxes in the diff image**\n"
                f"2. **Ignore text differences in non-critical UI areas** (e.g., banners, ads, floating elements)\n"
                f"3. **Key UI text content should match** between current and reference frames\n"
                f"4. **Non-essential text differences should be ignored** (e.g., timestamps, dynamic content)\n"
                f"5. **Consider OCR accuracy** - minor OCR errors should not affect the judgment\n"
                f"\n"
                f"## Notes:\n"
                f"- Ensure that **all required page components** (e.g., text, buttons, main layout, Overall framework, key UI Components) are present.\n"
                f"- **Ignore non-essential differences**, such as:\n"
                f"  - Animations\n"
                f"  - Banner or ad rotations\n"
                f"  - Minor non-content visual changes\n"
                f"  - Floating elements such as floating buttons which may be testing components\n"
                f"  - Text differences in non-critical areas (unless marked in diff image)\n"
                f"\n"
                f"Please respond strictly in the following JSON format:\n"
                f"{{\n"
                f"  \"is_fully_loaded\": true/false,\n"
                f"  \"direction\": \"left\"/\"right\",\n"
                f"  \"text_analysis\": \"Your analysis of text content differences, focusing on critical UI elements\",\n"
                f"  \"reason\": \"Your detailed reasoning here. Be specific about what elements are present or missing, and why.\"\n"
                f"}}"
            )
            
            messages = []
            messages.append({"role": "user", "content": user_prompt, "image_url": image_path_list})
            resp = llm_vision_request_with_retry(llm_client, messages, max_tokens=1024, model=model)
            
            # 保存LLM响应
            with open(os.path.join(step_dir, "llm_response.json"), "w", encoding="utf-8") as f:
                json.dump({"response": resp}, f, indent=4, ensure_ascii=False)
            
            try:
                resp_json = json.loads(resp)
            except:
                import re
                pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                match = re.search(pattern, resp)
                if match:
                    resp_json = json.loads(match.group(1))
                else:
                    raise ValueError(f"无法解析LLM响应: {resp}")
            
            if resp_json.get("is_fully_loaded", False):
                last_fully_loaded_frame = mid
                right = mid - 1
            else:
                left = mid + 1
        
        return last_fully_loaded_frame if last_fully_loaded_frame is not None else mid
    
    # 主循环：运行step method并进行recheck
    recheck_count = 0
    max_rechecks = 3  # 最大recheck次数
    
    while recheck_count < max_rechecks:
        recheck_count += 1
        print(f"第{recheck_count}次step method + recheck (with OCR)")
        
        # 确定当前搜索范围
        if recheck_count == 1:
            # 第一次：从action_time到最后一帧
            current_left = start_frame
            current_right = num_frames - 1
        else:
            # 后续：根据上次recheck结果调整范围
            current_left = last_left_bound
            current_right = last_right_bound
        
        # 运行step method (包含OCR)
        result_frame = run_step_method_in_range_with_ocr(current_left, current_right)
        
        if result_frame is None:
            print(f"Step method未找到结果，返回最后一帧")
            result_frame = num_frames - 1
        
        # 检查左边第10帧和右边第10帧 (包含OCR)
        left_check_frame = max(0, result_frame - 10)
        right_check_frame = min(num_frames - 1, result_frame + 10)
        
        print(f"检查帧 {result_frame}，左边第10帧: {left_check_frame}，右边第10帧: {right_check_frame}")
        
        # 检查左边帧 (包含OCR)
        left_loaded = check_frame_loading_status_with_ocr(left_check_frame)
        print(f"左边帧 {left_check_frame} 加载状态: {left_loaded}")
        
        # 检查右边帧 (包含OCR)
        right_loaded = check_frame_loading_status_with_ocr(right_check_frame)
        print(f"右边帧 {right_check_frame} 加载状态: {right_loaded}")
        
        # 根据recheck结果决定下一步
        if not left_loaded and right_loaded:
            # 情况1：左边没加载完，右边加载完，答案正确
            print(f"Recheck通过：左边未加载完成，右边已加载完成")
            final_result = result_frame
            break
        elif left_loaded and right_loaded:
            # 情况2：左边加载完，右边加载完，答案可能不正确，正确答案可能在左边
            print(f"Recheck失败：两边都已加载完成，在左边重新搜索")
            last_left_bound = start_frame
            last_right_bound = result_frame - 1
            continue
        elif left_loaded and not right_loaded:
            # 情况3：左边加载完，右边没加载完，重新recheck
            print(f"Recheck失败：左边已加载完成，右边未加载完成，重新recheck")
            last_left_bound = left_check_frame
            last_right_bound = right_check_frame
            continue
        else:  # not left_loaded and not right_loaded
            # 情况4：左边没加载完，右边没加载完，答案可能不正确，正确答案可能在右边
            print(f"Recheck失败：两边都未加载完成，在右边重新搜索")
            last_left_bound = result_frame + 1
            last_right_bound = num_frames - 1
            continue
    else:
        # 达到最大recheck次数，返回最后一次的结果
        print(f"达到最大recheck次数({max_rechecks})，返回最后一次结果")
        final_result = result_frame
    
    # 保存最终结果信息
    with open(os.path.join(experiment_dir, "final_result.json"), "w", encoding="utf-8") as f:
        json.dump({
            "final_end_frame": final_result,
            "recheck_count": recheck_count,
            "start_frame": start_frame,
            "end_frame": num_frames - 1,
            "fps": fps,
            "activity_threshold": activity_threshold,
            "model": model,
            "ocr_filter_score": ocr_filter_score
        }, f, indent=4, ensure_ascii=False)
    
    if do_evaluation:
        # 获取ground truth帧号
        marked_end_time = action_info["original_action_item"]["marked_end_time"]
        gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
        gt_end_frame = max(0, gt_end_frame)
        
        # 构建评估结果
        result_entry = {
            "segment_dir": segment_dir,
            "llm_refined_start_frame": start_frame,
            "llm_refined_end_frame": final_result,
            "llm_results_end": f"Recheck method with OCR ({recheck_count} iterations)"
        }
        
        # 执行评估
        evaluate_llm_narrow_results([result_entry])
    
    return final_result, f"Recheck method with OCR ({recheck_count} iterations)", [], []

def llm_narrow_from_action_info_grid_voting(
    segment_dir,
    llm_client,
    do_evaluation=False,
    activity_threshold=-0.001,
    merge_window=3,
    start_threshold=-0.0001,
    end_threshold=-0.0001,
    ssim_threshold=0.995,
    model="anthropic.claude-3.7-sonnet",
    max_voting_rounds=10
):
    """
    使用voting机制的图片网格版本，会多次运行直到有帧被选中两次，并使用相似度过滤候选帧
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        start_threshold: 开始点阈值，默认-0.0001
        end_threshold: 结束点阈值，默认-0.0001
        ssim_threshold: SSIM阈值，默认0.995
        model: 使用的模型名称，默认"anthropic.claude-3.7-sonnet"
        max_voting_rounds: 最大投票轮数，默认5
    """
    print(f"开始voting方法处理: {segment_dir}")
    
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 获取操作描述
    action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    
    # 2. 加载和处理SSIM数据
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    if not os.path.exists(ssim_pt_path):
        raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_dir}")
    
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    
    # 3. 预处理SSIM数据
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    if not cleaned_ssim_data:
        raise ValueError("预处理后的SSIM数据为空")
    
    # 4. 计算平滑SSIM和斜率
    fps = action_info["extraction_parameters"]["fps"]
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    refined_start = None
    
    # 如果没有找到开始帧，使用action_time
    if refined_start is None:
        action_time = action_info["original_action_item"]["action_time"]
        extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
        refined_start = round((action_time - extract_start_time_sec) * fps)
        refined_start = max(0, refined_start)
        print(f"使用action_time作为开始帧: {refined_start}")
    
    # 7. 获取结束帧候选帧并进行相似度过滤
    print(f"开始获取结束帧候选帧，开始帧: {refined_start}")
    end_candidates = get_candidate_frames_for_end(
        cleaned_ssim_data, smoothed_ssim, slopes, refined_start,
        activity_threshold=activity_threshold,
        merge_window=merge_window,
        end_threshold=end_threshold
    )
    
    print(f"原始结束帧候选帧数量: {len(end_candidates)}")
    
    # 7.5. 使用action time筛选候选帧，去掉小于action time帧的候选帧
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    action_frame = round((action_time - extract_start_time_sec) * fps)
    action_frame = max(0, action_frame)
    
    # 筛选候选帧，只保留大于等于action_frame的候选帧
    end_candidates = [c for c in end_candidates if c >= action_frame]
    print(f"Action time帧: {action_frame}")
    print(f"Action time筛选后的候选帧数量: {len(end_candidates)}")
    
    if not end_candidates:
        print("警告: Action time筛选后没有剩余候选帧")
        # 如果没有候选帧，返回None
        result_entry = {
            "segment_dir": segment_dir,
            "llm_refined_start_frame": refined_start,
            "llm_refined_end_frame": None,
            "start_candidate_indices": refined_start,
            "end_candidate_indices": [],
            "filtered_end_candidates": [],
            "llm_results_start": refined_start,
            "voting_results": {},
            "all_voting_details": [],
            "voting_rounds_completed": 0
        }
        
        if do_evaluation:
            from .llm_narrow_eval import evaluate_llm_narrow_results
            evaluate_llm_narrow_results([result_entry])
        
        print(f"voting方法处理完成: {segment_dir}")
        return result_entry
    
    # 8. 使用相似度方法过滤候选帧 (参考step_with_recheck的逻辑)
    def filter_candidates_by_similarity(candidates, last_frame_idx):
        """使用相似度过滤候选帧，去掉从左到右第一个相似度为1.0的帧后面的所有候选帧"""
        if not candidates:
            return candidates
            
        # 加载最后一帧作为参考
        last_frame = load_frame_from_npy(segment_dir, last_frame_idx)
        if last_frame is None:
            print(f"无法加载最后一帧: {last_frame_idx}")
            return candidates
        
        filtered_candidates = []
        found_perfect_similarity = False
        
        for candidate_idx in candidates:
            if found_perfect_similarity:
                print(f"  跳过候选帧 {candidate_idx} (已找到相似度1.0的帧)")
                continue
                
            # 加载候选帧
            candidate_frame = load_frame_from_npy(segment_dir, candidate_idx)
            if candidate_frame is None:
                print(f"  无法加载候选帧: {candidate_idx}")
                continue
            
            # 保存临时图片用于相似度计算
            temp_dir = os.path.join(segment_dir, "temp_similarity")
            os.makedirs(temp_dir, exist_ok=True)
            
            candidate_path = os.path.join(temp_dir, f"candidate_{candidate_idx}.png")
            last_path = os.path.join(temp_dir, f"last_{last_frame_idx}.png")
            
            candidate_frame.save(candidate_path)
            last_frame.save(last_path)
            
            # 计算相似度
            img1 = cv2.imread(candidate_path)
            img2 = cv2.imread(last_path)
            
            try:
                ocr_result = get_ocr_result(img1, img2)
                img_diff_obj = ImageDiff(img1, img2, ocr_result,struct_score_thresh=0.99)
                score = img_diff_obj.get_similar_score([])
                
                print(f"  候选帧 {candidate_idx} 与最后一帧的相似度: {score}")
                
                if score == 1.0:
                    print(f"  找到相似度1.0的帧: {candidate_idx}，将过滤后续所有候选帧")
                    filtered_candidates.append(candidate_idx)
                    found_perfect_similarity = True
                else:
                    filtered_candidates.append(candidate_idx)
                    
            except Exception as e:
                print(f"  计算候选帧 {candidate_idx} 相似度时出错: {e}")
                filtered_candidates.append(candidate_idx)  # 出错时仍保留候选帧
            
            # 清理临时文件
            try:
                os.remove(candidate_path)
                os.remove(last_path)
            except:
                pass
        
        # 清理临时目录
        try:
            os.rmdir(temp_dir)
        except:
            pass
            
        return filtered_candidates
    
    # 过滤候选帧
    filtered_end_candidates = filter_candidates_by_similarity(end_candidates, num_frames - 1)
    print(f"相似度过滤后的结束帧候选帧数量: {len(filtered_end_candidates)}")
    
    if not filtered_end_candidates:
        print("警告: 相似度过滤后没有剩余候选帧，使用原始候选帧")
        filtered_end_candidates = end_candidates
    
    # 9. 开始voting过程
    print(f"开始voting过程，最多{max_voting_rounds}轮")
    
    voting_results = {}  # {frame_idx: count}
    all_voting_details = []  # 保存所有投票详情
    
    for round_num in range(1, max_voting_rounds + 1):
        print(f"\n--- 第{round_num}轮投票 ---")
        
        # 创建网格图片
        end_images = []
        for idx in filtered_end_candidates:
            img = load_frame_from_npy(segment_dir, idx)
            if img is not None:
                end_images.append((idx, None, img))
        
        if not end_images:
            print("没有可用的结束帧候选图片")
            break
            
        # 使用新的voting拼图函数
        end_grid = create_voting_image_grid(segment_dir, filtered_end_candidates)
        # 修复位置映射：第一帧是位置1，候选帧从位置2开始，最后一帧在最后
        position_to_end_frame_map = {i+2:idx for i,idx in enumerate(filtered_end_candidates)}  # 候选帧从位置2开始
        
        if not end_grid:
            print("无法创建网格图片")
            break
        
        # 保存网格图片
        grid_output_dir = os.path.join(segment_dir, "grid_images_voting")
        os.makedirs(grid_output_dir, exist_ok=True)
        end_grid_path = os.path.join(grid_output_dir, f"end_grid_round_{round_num}.png")
        end_grid.save(end_grid_path)
        
        # 构建提示词
        end_prompt = (
            f"You are a helpful assistant that can help me analyze the page loading process after executing the operation. "
            f"Below is a grid of frames from a video showing the page loading process. "
            f"The frames are arranged from left to right, top to bottom.\n\n"
            f"## Context:\n"
            f"1. Action being performed: {action_desc}\n"
            f"2. Event type: load_end_time\n"
            f"3. Grid layout: Red border = Frame 0 (start), Blue border = Last frame (end), Gray borders = Candidate frames\n\n"
            f"## Definition of end frame:\n"
            f"1. The first end frame is the first frame where the page is fully loaded after the operation\n"
            f"2. The page must be completely loaded with no white spaces or loading indicators\n"
            f"3. The page must have changed from the previous page to the desired page after the operation\n"
            f"## Task:\n"
            f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
            f"  ##Pay special attention to:\n"
            f"- Small changes in UI elements\n"
            f"- Slight color variations\n"
            f"- Loading indicators disappearing\n"
            f"- White spaces or loading elements being filled\n\n"
            f"- ##Ignorging:\n"
            f"- Any banner movement or animation changing or advertisement image changing\n"
            f"- Minor non-content visual changes\n"
            f"- Floating elements such as floating buttons which may be testing components\n"
            f"- There may be a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
            f"- Scrolling of small texts\n"
            f"Then, identify which frame shows the end of page loading.(end of change,first frame after all changes)\n"
            f"## IMPORTANT: You must choose from the candidate frames (gray borders) only. Do NOT select the start frame (red border) or the end frame (blue border) - they are only for reference.\n"
            f"Please answer in JSON format:\n"
            f"{{\n"
            f"    \"frame_analysis\": [\n"
            f"        {{\"position\": 1, \"description\": \"Detailed description of subtle changes in first frame\"}},\n"
            f"        {{\"position\": 2, \"description\": \"Detailed description of subtle changes in second frame\"}},\n"
            f"        // ... continue for all frames\n"
            f"    ],\n"
            f"    \"target_position\": <position_number>,\n"
            f"    \"reason\": \"Detailed explanation of why this frame is the end frame,and why the others are not.\"\n"
            f"}}"
        )
        llm_client = LLMClient()
        # LLM推理 - 使用llm_vision_request_with_retry
        try:
            # 保存网格图片到临时文件
            temp_grid_path = os.path.join(segment_dir, f"temp_grid_round_{round_num}.png")
            end_grid.save(temp_grid_path)
            
            # 构建正确的消息格式
            messages = [{"role": "user", "content": end_prompt, "image_url": [temp_grid_path]}]
            
            # 使用llm_vision_request_with_retry
            response = llm_vision_request_with_retry(
                llm_client,
                messages, 
                max_tokens=2048,
                model=model
            )
            
            # 解析响应
            refined_end_position = None
            max_retries_for_position = 3  # 最大重试次数
            retry_count = 0
            
            while retry_count < max_retries_for_position:
                try:
                    resp_json = json.loads(response)
                    if "target_position" in resp_json:
                        target_pos = resp_json["target_position"]
                        if target_pos in position_to_end_frame_map:
                            refined_end_position = position_to_end_frame_map[target_pos]
                            # 验证选择的是否为候选帧（不是参考帧）
                            if refined_end_position in filtered_end_candidates:
                                print(f"    第{round_num}轮选择帧: {refined_end_position}")
                                break
                            else:
                                print(f"    第{round_num}轮选择了无效帧 {refined_end_position}（不是候选帧），重试...")
                                retry_count += 1
                                if retry_count < max_retries_for_position:
                                    # 重新请求
                                    messages = [{"role": "user", "content": end_prompt, "image_url": [temp_grid_path]}]
                                    response = llm_vision_request_with_retry(
                                        llm_client,
                                        messages,
                                        max_tokens=2048,
                                        model=model
                                    )
                                    continue
                                else:
                                    print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                    refined_end_position = None
                                    break
                except:
                    pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                    match = re.search(pattern, response)
                    if match:
                        resp_json = json.loads(match.group(1))
                        if "target_position" in resp_json:
                            target_pos = resp_json["target_position"]
                            if target_pos in position_to_end_frame_map:
                                refined_end_position = position_to_end_frame_map[target_pos]
                                # 验证选择的是否为候选帧（不是参考帧）
                                if refined_end_position in filtered_end_candidates:
                                    print(f"    第{round_num}轮选择帧: {refined_end_position}")
                                    break
                                else:
                                    print(f"    第{round_num}轮选择了无效帧 {refined_end_position}（不是候选帧），重试...")
                                    retry_count += 1
                                    if retry_count < max_retries_for_position:
                                        # 重新请求
                                        messages = [{"role": "user", "content": end_prompt, "image_url": [temp_grid_path]}]
                                        response = llm_vision_request_with_retry(
                                            llm_client,
                                            messages,
                                            max_tokens=2048,
                                            model=model
                                        )
                                        continue
                                    else:
                                        print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                        refined_end_position = None
                                        break
                    else:
                        print(f"    第{round_num}轮LLM未返回有效结果")
                        break
            
            if refined_end_position is not None:
                refined_end_frame = refined_end_position
                print(f"第{round_num}轮选择帧: {refined_end_frame}")
                
                # 记录投票
                if refined_end_frame not in voting_results:
                    voting_results[refined_end_frame] = 0
                voting_results[refined_end_frame] += 1
                
                # 保存投票详情
                voting_detail = {
                    "round": round_num,
                    "selected_frame": refined_end_frame,
                    "llm_results": response,
                    "current_vote_count": voting_results[refined_end_frame],
                    "retry_count": retry_count
                }
                all_voting_details.append(voting_detail)
                
                # 检查是否有帧获得了2票或以上
                if voting_results[refined_end_frame] >= 2:
                    print(f"帧 {refined_end_frame} 获得了 {voting_results[refined_end_frame]} 票，达到投票要求")
                    break
            else:
                print(f"第{round_num}轮LLM未返回有效结果")
                all_voting_details.append({
                    "round": round_num,
                    "selected_frame": None,
                    "llm_results": response,
                    "error": "LLM未返回有效结果"
                })
                
        except Exception as e:
            print(f"第{round_num}轮投票过程中出错: {e}")
            all_voting_details.append({
                "round": round_num,
                "selected_frame": None,
                "llm_results": None,
                "error": str(e)
            })
            
            # 清理临时文件
            if 'temp_grid_path' in locals() and os.path.exists(temp_grid_path):
                os.remove(temp_grid_path)
        
        # 等待一段时间再进行下一轮投票
        if round_num < max_voting_rounds:
            print(f"等待10秒后进行下一轮投票...")
            time.sleep(5)
    
    # 10. 确定最终结果
    final_end_frame = None
    if voting_results:
        # 选择票数最多的帧
        final_end_frame = max(voting_results.items(), key=lambda x: x[1])[0]
        max_votes = voting_results[final_end_frame]
        print(f"\n投票结果: {voting_results}")
        print(f"最终选择帧: {final_end_frame} (获得 {max_votes} 票)")
        
        # 找到最终选择帧对应的LLM响应
        final_llm_response = None
        for detail in all_voting_details:
            if detail["selected_frame"] == final_end_frame:
                final_llm_response = detail["llm_results"]
                break
        
        if final_llm_response:
            print(f"最终选择帧 {final_end_frame} 对应的LLM响应已找到")
        else:
            print(f"警告：未找到最终选择帧 {final_end_frame} 对应的LLM响应")
    else:
        print("最终投票未获得任何有效结果，使用候选帧中间值")
        if all_voting_details:
            final_end_frame = max(voting_results.items(), key=lambda x: x[1])[0]
            max_votes = voting_results[final_end_frame]
            print(f"最终选择帧: {final_end_frame} (获得 {max_votes} 票)")
            final_llm_response = None
        else:
            print("没有候选帧可用")
            final_end_frame = None
            final_llm_response = None
    
    # 11. 输出结果
    result_entry = {
        "segment_dir": segment_dir,
        "llm_refined_start_frame": refined_start,
        "llm_refined_end_frame": final_end_frame,
        "start_candidate_indices": refined_start,
        "end_candidate_indices": end_candidates,
        "filtered_end_candidates": filtered_end_candidates,
        "llm_results_start": refined_start,
        "voting_results": voting_results,
        "all_voting_details": all_voting_details,
        "voting_rounds_completed": len(all_voting_details)
    }
    
    if do_evaluation:
        from .llm_narrow_eval import evaluate_llm_narrow_results
        evaluate_llm_narrow_results([result_entry])
    
    print(f"voting方法处理完成: {segment_dir}")
    return result_entry

def get_best_grid_shape(n, min_cols=2, max_cols=5):
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
            label = f"Frame {idx}"
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

def llm_narrow_from_action_info_grid_voting_iterative(
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
    temperature=0.1
):
    """
    基于grid with voting的迭代细化函数
    投票选出答案后，逐步缩小搜索范围，最终得到精确答案
    
    Args:
        segment_dir: 视频片段目录
        llm_client: LLM客户端实例
        do_evaluation: 是否进行详细评估
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        start_threshold: 开始点阈值，默认-0.0001
        end_threshold: 结束点阈值，默认-0.0001
        ssim_threshold: SSIM阈值，默认0.995
        model: 使用的模型名称，默认"anthropic.claude-3.7-sonnet"
        max_voting_rounds: 最大投票轮数，默认10
    
    Returns:
        dict: 包含最终结果和所有迭代过程的详细信息
    """
    import time
    import math
    
    print(f"开始迭代细化voting方法处理: {segment_dir}")
    
    # 1. 读取 action_info.json
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    
    # 获取基本信息
    action_desc = action_info.get("original_action_item", {}).get("action_desc", "")
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    fps = action_info["extraction_parameters"]["fps"]
    
    # 2. 创建实验文件夹
    experiment_dir = os.path.join(segment_dir, f"experiment_iterative_voting_{int(time.time())}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # 3. 获取初始候选帧（使用原有的voting逻辑）
    action_time = action_info["original_action_item"]["action_time"]
    extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
    start_frame = round((action_time - extract_start_time_sec) * fps)
    start_frame = max(0, start_frame)
    
    # 加载SSIM数据
    ssim_pt_path = os.path.join(segment_dir, "ssim_sequence.pt")
    if not os.path.exists(ssim_pt_path):
        raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_dir}")
    
    raw_ssim_data_tensor = torch.load(ssim_pt_path)
    raw_ssim_data_list = raw_ssim_data_tensor.tolist()
    cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
    
    # 计算平滑SSIM和斜率
    ssim_series = pd.Series(cleaned_ssim_data)
    smoothed_ssim = ssim_series.rolling(window=9, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    
    # 获取结束帧候选帧
    end_candidates = get_candidate_frames_for_end(
        cleaned_ssim_data, smoothed_ssim, slopes, start_frame,
        activity_threshold=activity_threshold,
        merge_window=merge_window,
        end_threshold=end_threshold
    )
    
    # 使用action time筛选候选帧
    action_frame = round((action_time - extract_start_time_sec) * fps)
    action_frame = max(0, action_frame)
    end_candidates = [c for c in end_candidates if c >= action_frame]
    
    if not end_candidates:
        print("警告: 没有找到候选帧")
        return {
            "segment_dir": segment_dir,
            "final_end_frame": None,
            "iteration_results": [],
            "error": "没有找到候选帧"
        }
    
    # 4. 使用相似度方法过滤候选帧 (参考step_with_recheck的逻辑)
    def filter_candidates_by_similarity(candidates, last_frame_idx):
        """使用相似度过滤候选帧，去掉从左到右第一个相似度为1.0的帧后面的所有候选帧"""
        if not candidates:
            return candidates
            
        # 加载最后一帧作为参考
        last_frame = load_frame_from_npy(segment_dir, last_frame_idx)
        if last_frame is None:
            print(f"无法加载最后一帧: {last_frame_idx}")
            return candidates
        
        filtered_candidates = []
        found_perfect_similarity = False
        
        for candidate_idx in candidates:
            if found_perfect_similarity:
                print(f"  跳过候选帧 {candidate_idx} (已找到相似度1.0的帧)")
                continue
                
            # 加载候选帧
            candidate_frame = load_frame_from_npy(segment_dir, candidate_idx)
            if candidate_frame is None:
                print(f"  无法加载候选帧: {candidate_idx}")
                continue
            
            # 保存临时图片用于相似度计算
            temp_dir = os.path.join(segment_dir, "temp_similarity")
            os.makedirs(temp_dir, exist_ok=True)
            
            candidate_path = os.path.join(temp_dir, f"candidate_{candidate_idx}.png")
            last_path = os.path.join(temp_dir, f"last_{last_frame_idx}.png")
            
            candidate_frame.save(candidate_path)
            last_frame.save(last_path)
            
            # 计算相似度
            img1 = cv2.imread(candidate_path)
            img2 = cv2.imread(last_path)
            
            try:
                ocr_result = get_ocr_result(img1, img2)
                img_diff_obj = ImageDiff(img1, img2, ocr_result, struct_score_thresh=0.99)
                score = img_diff_obj.get_similar_score([])
                
                print(f"  候选帧 {candidate_idx} 与最后一帧的相似度: {score}")
                
                if score == 1.0:
                    print(f"  找到相似度1.0的帧: {candidate_idx}，将过滤后续所有候选帧")
                    filtered_candidates.append(candidate_idx)
                    found_perfect_similarity = True
                else:
                    filtered_candidates.append(candidate_idx)
                    
            except Exception as e:
                print(f"  计算候选帧 {candidate_idx} 相似度时出错: {e}")
                filtered_candidates.append(candidate_idx)  # 出错时仍保留候选帧
            
            # 清理临时文件
            try:
                os.remove(candidate_path)
                os.remove(last_path)
            except:
                pass
        
        # 清理临时目录
        try:
            os.rmdir(temp_dir)
        except:
            pass
            
        return filtered_candidates
    
    # 过滤候选帧
    filtered_end_candidates = filter_candidates_by_similarity(end_candidates, num_frames - 1)
    print(f"相似度过滤后的结束帧候选帧数量: {len(filtered_end_candidates)}")
    
    if not filtered_end_candidates:
        print("警告: 相似度过滤后没有剩余候选帧，使用原始候选帧")
        filtered_end_candidates = end_candidates
    
    # 5. 开始迭代细化过程
    iteration_results = []  # 记录每次迭代的结果
    current_candidates = filtered_end_candidates.copy()
    current_window_size = 200  # 初始窗口大小
    min_window_size = 10  # 最小窗口大小
    
    iteration_count = 0
    max_iterations = 10  # 最大迭代次数
    
    while current_window_size >= min_window_size and iteration_count < max_iterations:
        iteration_count += 1
        print(f"\n=== 第{iteration_count}次迭代，窗口大小: {current_window_size} ===")
        
        # 创建当前迭代的文件夹
        iteration_dir = os.path.join(experiment_dir, f"iteration_{iteration_count:03d}")
        os.makedirs(iteration_dir, exist_ok=True)
        
        # 5.1 选择当前最佳帧（第一次使用voting，后续直接选择）
        if iteration_count == 1:
            # 第一次迭代：使用voting方法
            print("  第一次迭代，使用voting方法...")
            voting_results = {}
            all_voting_details = []
            
            for round_num in range(1, max_voting_rounds + 1):
                print(f"    第{round_num}轮投票...")
                
                # 创建网格图片
                end_images = []
                for idx in current_candidates:
                    img = load_frame_from_npy(segment_dir, idx)
                    if img is not None:
                        end_images.append((idx, None, img))
                
                if not end_images:
                    print("    没有可用的候选图片")
                    break
                    
                # 创建voting网格
                end_grid = create_voting_image_grid(segment_dir, current_candidates)
                
                if not end_grid:
                    print("    无法创建网格图片")
                    break
                
                # 保存网格图片
                grid_path = os.path.join(iteration_dir, f"grid_round_{round_num}.png")
                end_grid.save(grid_path)
                
                        # 构建提示词
                end_prompt = (
                    f"You are a helpful assistant that can help me analyze the page loading process after executing the operation. "
                    f"Below is a grid of frames from a video showing the page loading process. "
                    f"The frames are arranged from left to right, top to bottom.\n\n"
                    f"## Context:\n"
                    f"1. Action being performed: {action_desc}\n"
                    f"2. Event type: load_end_time\n"
                    f"3. Grid layout: Red border = Frame 0 (start), Blue border = Last frame (end), Gray borders = Candidate frames\n"
                    f"## Definition of end frame:\n"
                    f"1. The first end frame is the first frame where the page is fully loaded after the operation\n"
                    f"2. The page must be completely loaded with no white spaces or loading indicators\n"
                    f"3. Loading popups and dialogs must have disappeared\n"
                    f"4. If the interface before and after loading looks similar, the loading completion time must be later - do not choose frames from before loading\n"
                    f"5. The page must have changed from the previous page to the desired page after the operation\n"
                    f"## Task:\n"
                    f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
                    f"  ##Pay special attention to:\n"
                    f"- Small changes in UI elements,important clickable elements must be visible\n"
                    f"- Slight color variations\n"
                    f"- White spaces or loading elements being filled\n"
                    f"- Placeholder must be filled\n"
                    f"- Popups and dialogs must have disappeared\n"
                    f"- ##Ignore:\n"
                    f"- Banner images and videos changing/moving after loaded on the page are not important,but image loading is important.In other words,image or videos must have contents,but don't care about the content changing\n"
                    f"- Character color/texts changing/moving is not important after loaded.In other words,character color/texts must have contents,but don't care about the content changing\n"
                    f"- There may be a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
                    f"Then, identify which frame shows the end of page loading.(end of change,first frame after all changes)\n"
                    f"## IMPORTANT: You must choose from the candidate frames (gray borders) only. Do NOT select the start frame (red border) or the end frame (blue border) - they are only for reference.\n"
                    f"Please answer in JSON format:\n"
                    f"{{\n"
                    f"    \"frame_analysis\": [\n"
                    f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame\"}},\n"
                    f"        {{\"frame_number\": <frame_number>, \"description\": \"Detailed description of subtle changes in this frame\"}},\n"
                    f"        // ... continue for all frames\n"
                    f"    ],\n"
                    f"    \"target_frame\": <frame_number>,\n"
                    f"    \"reason\": \"Detailed explanation of why this frame is the end frame,and why the others are not.\"\n"
                    f"}}"
                )
                
                # LLM推理
                try:
                    messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                    response = llm_vision_request_with_retry(
                        llm_client,
                        messages,
                        max_tokens=2048,
                        model=model
                    )
                    print(response)
                    # 解析响应
                    refined_end_frame = None
                    max_retries_for_position = 10  # 最大重试次数
                    retry_count = 0
                    
                    while retry_count < max_retries_for_position:
                        try:
                            resp_json = json.loads(response)
                            if "target_frame" in resp_json:
                                target_frame = resp_json["target_frame"]
                                # 验证选择的是否为候选帧（不是参考帧）
                                if target_frame in current_candidates:
                                    refined_end_frame = target_frame
                                    print(f"    第{round_num}轮选择帧: {refined_end_frame}")
                                    break
                                else:
                                    print(f"    第{round_num}轮选择了无效帧 {target_frame}（不是候选帧），重试...")
                                    retry_count += 1
                                    if retry_count < max_retries_for_position:
                                        # 重新请求
                                        messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                                        response = llm_vision_request_with_retry(
                                            llm_client,
                                            messages,
                                            max_tokens=2048,
                                            model=model
                                        )
                                        continue
                                    else:
                                        print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                        refined_end_frame = None
                                        break
                        except:
                            pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                            match = re.search(pattern, response)
                            if match:
                                resp_json = json.loads(match.group(1))
                                if "target_frame" in resp_json:
                                    target_frame = resp_json["target_frame"]
                                    # 验证选择的是否为候选帧（不是参考帧）
                                    if target_frame in current_candidates:
                                        refined_end_frame = target_frame
                                        print(f"    第{round_num}轮选择帧: {refined_end_frame}")
                                        break
                                    else:
                                        print(f"    第{round_num}轮选择了无效帧 {target_frame}（不是候选帧），重试...")
                                        retry_count += 1
                                        if retry_count < max_retries_for_position:
                                            # 重新请求
                                            messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                                            response = llm_vision_request_with_retry(
                                                llm_client,
                                                messages,
                                                max_tokens=2048,
                                                model=model
                                            )
                                            continue
                                        else:
                                            print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                            refined_end_frame = None
                                            break
                    if refined_end_frame is not None:
                        print(f"    第{round_num}轮选择帧: {refined_end_frame}")
                        
                        # 记录投票
                        if refined_end_frame not in voting_results:
                            voting_results[refined_end_frame] = 0
                        voting_results[refined_end_frame] += 1
                        
                        # 保存投票详情
                        voting_detail = {
                            "round": round_num,
                            "selected_frame": refined_end_frame,
                            "llm_results": response,
                            "current_vote_count": voting_results[refined_end_frame],
                            "retry_count": retry_count
                        }
                        all_voting_details.append(voting_detail)
                        
                        # 检查是否有帧获得了2票或以上
                        if voting_results[refined_end_frame] >= 2:
                            print(f"    帧 {refined_end_frame} 获得了 {voting_results[refined_end_frame]} 票，达到投票要求")
                            break
                    else:
                        print(f"    第{round_num}轮LLM未返回有效结果")
                        
                except Exception as e:
                    print(f"    第{round_num}轮投票过程中出错: {e}")
            
            # 确定当前迭代的最佳帧
            current_best_frame = None
            if voting_results:
                # 找到票数最多的帧
                current_best_frame = max(voting_results.items(), key=lambda x: x[1])[0]
                max_votes = voting_results[current_best_frame]
                print(f"  当前迭代最佳帧: {current_best_frame} (获得 {max_votes} 票)")
                
                # 添加调试信息
                print(f"  投票结果详情: {voting_results}")
                print(f"  所有投票详情: {all_voting_details}")
                
                # 验证投票结果的一致性
                for detail in all_voting_details:
                    if detail["selected_frame"] != current_best_frame:
                        print(f"  警告：投票详情中的帧 {detail['selected_frame']} 与最佳帧 {current_best_frame} 不一致")
            else:
                print("  未获得任何有效投票结果")
                # 如果没有投票结果，使用候选帧的中间值
                if current_candidates:
                    current_best_frame = current_candidates[len(current_candidates)//2]
                    print(f"  使用候选帧中间值作为最佳帧: {current_best_frame}")
                else:
                    break
                
        else:
            # 后续迭代：直接选择最佳帧
            print("  后续迭代，直接选择最佳帧...")
            
            # 创建网格图片
            end_images = []
            if iteration_count == 1:
                # 第一次：首帧+候选帧+尾帧
                for idx in current_candidates:
                    img = load_frame_from_npy(segment_dir, idx)
                    if img is not None:
                        end_images.append((idx, None, img))
                end_grid = create_voting_image_grid(segment_dir, current_candidates)
            else:
                # 后续迭代：只保留候选帧和最后一帧
                # 先生成候选帧图片
                for idx in current_candidates:
                    img = load_frame_from_npy(segment_dir, idx)
                    if img is not None:
                        end_images.append((idx, None, img))
                # 加载最后一帧
                action_info_path = os.path.join(segment_dir, "action_info.json")
                with open(action_info_path, "r", encoding="utf-8") as f:
                    action_info = json.load(f)
                num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
                last_frame = load_frame_from_npy(segment_dir, num_frames - 1)
                if last_frame is not None:
                    end_images.append((num_frames - 1, None, last_frame))
                # 生成自定义网格（不含首帧）
                from PIL import Image, ImageDraw, ImageFont
                import math
                total_images = len(end_images)
                cols = min(5, total_images)
                rows = math.ceil(total_images / cols)
                cell_width = cell_height = 400
                label_height = 50
                canvas_width = cols * cell_width
                canvas_height = rows * (cell_height + label_height) + 60
                grid_image = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
                draw = ImageDraw.Draw(grid_image)
                try:
                    font = ImageFont.truetype("Arial", 16)
                except:
                    font = ImageFont.load_default()
                for i, (idx, _, img) in enumerate(end_images):
                    row = i // cols
                    col = i % cols
                    x = col * cell_width
                    y = row * (cell_height + label_height) + 40
                    # 边框颜色和标签
                    if idx == num_frames - 1:
                        border_color = (0, 0, 255)
                        label = f"Frame {num_frames - 1} (End)"
                        label_color = (0, 0, 255)
                    else:
                        border_color = (128, 128, 128)
                        label = f"Frame {idx}"
                        label_color = (0, 0, 0)
                    # 调整图片大小
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height
                    if aspect_ratio > 1:
                        new_width = cell_width - 6
                        new_height = int(new_width / aspect_ratio)
                        if new_height > cell_height - 6:
                            new_height = cell_height - 6
                            new_width = int(new_height * aspect_ratio)
                    else:
                        new_height = cell_height - 6
                        new_width = int(new_height * aspect_ratio)
                        if new_width > cell_width - 6:
                            new_width = cell_width - 6
                            new_height = int(new_width / aspect_ratio)
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    bordered_img = Image.new('RGB', (cell_width, cell_height), border_color)
                    paste_x = (cell_width - new_width) // 2
                    paste_y = (cell_height - new_height) // 2
                    bordered_img.paste(resized_img, (paste_x, paste_y))
                    grid_image.paste(bordered_img, (x, y))
                    # 标签
                    text_width = draw.textlength(label, font=font)
                    text_x = x + (cell_width - text_width) // 2
                    text_y = y + cell_height + 5
                    draw.text((text_x, text_y), label, fill=label_color, font=font)
                end_grid = grid_image
            
            if not end_grid:
                print("  无法创建网格图片")
                break
            # 保存网格图片
            grid_path = os.path.join(iteration_dir, "grid_single.png")
            end_grid.save(grid_path)
            
        # 构建提示词（使用相同的prompt）
        end_prompt = (
            f"You are a helpful assistant that can help me analyze the page loading process. "
            f"Below is a grid of frames from a video showing the page loading process. "
            f"The frames are arranged from left to right, top to bottom.\n\n"
            f"## Context:\n"
            f"1. Event type: load_end_time\n"
            f"2. Grid layout:  Blue border = Last frame (end), Green border = Iteration result, Gray borders = Other candidate frames.The frame index is under each frame\n"
            f"3. we are focusing on a narrower range for precise detection\n"
            f"4. Available candidate frame numbers: {current_candidates}\n\n"
            f"## Definition of end frame:\n"
            f"1. The first end frame is the first frame where the page is fully loaded after the operation\n"
            f"2. The page must be completely loaded with no white spaces or loading indicators\n"
            f"3. Loading popups and dialogs must have disappeared\n"
            f"4. If the interface before and after loading looks similar, the loading completion time must be later - do not choose frames from before loading\n"
            f"5. The page must have changed from the previous page to the desired page after the operation\n"
            f"## Task:\n"
            f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
            f"  ##Pay special attention to:\n"
            f"- Small changes in UI elements,and which UI elements doesn't appear\n"
            f"- Slight color variations\n"
            f"- Loading indicators disappearing\n"
            f"- White spaces or loading elements being filled\n"
            f"- Loading popups and dialogs disappearing\n\n"
            f"- ##Ignorging:\n"
            f"- Any banner movement or animation changing or advertisement image changing\n"
            f"- Minor non-content visual changes\n"
            f"- Floating elements such as floating buttons which may be testing components\n"
            f"- There may be a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
            f"- Scrolling of small texts\n"
            f"Then, identify which frame shows the end of page loading.(end of change,first frame after all changes)\n"
            f"## IMPORTANT: You must choose from the candidate frames (gray borders) only. Do NOT select the end frame (blue border, last frame) - it is only for reference.\n"
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
        
        # LLM推理
        try:
            messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
            response = llm_vision_request_with_retry(
                llm_client,
                messages,
                max_tokens=2048,
                model=model
            )
            print(response)
            # 解析响应
            current_best_frame = None
            max_retries_for_position = 3  # 最大重试次数
            retry_count = 0
            
            while retry_count < max_retries_for_position:
                try:
                    resp_json = json.loads(response)
                    if "target_frame" in resp_json:
                        target_frame = resp_json["target_frame"]
                        # 验证选择的是否为候选帧（不是参考帧）
                        if target_frame in current_candidates:
                            current_best_frame = target_frame
                            print(f"  当前迭代最佳帧: {current_best_frame}")
                            break
                        else:
                            print(f"  当前迭代选择了无效帧 {target_frame}（不是候选帧），重试...")
                            retry_count += 1
                            if retry_count < max_retries_for_position:
                                # 重新请求
                                messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                                response = llm_vision_request_with_retry(
                                    llm_client,
                                    messages,
                                    max_tokens=2048,
                                    model=model
                                )
                                continue
                            else:
                                print(f"  当前迭代重试{max_retries_for_position}次后仍选择无效帧")
                                current_best_frame = None
                                break
                except:
                    pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                    match = re.search(pattern, response)
                    if match:
                        resp_json = json.loads(match.group(1))
                        if "target_frame" in resp_json:
                            target_frame = resp_json["target_frame"]
                            # 验证选择的是否为候选帧（不是参考帧）
                            if target_frame in current_candidates:
                                current_best_frame = target_frame
                                print(f"  当前迭代最佳帧: {current_best_frame}")
                                break
                            else:
                                print(f"  当前迭代选择了无效帧 {target_frame}（不是候选帧），重试...")
                                retry_count += 1
                                if retry_count < max_retries_for_position:
                                    # 重新请求
                                    messages = [{"role": "user", "content": end_prompt, "image_url": [grid_path]}]
                                    response = llm_vision_request_with_retry(
                                        llm_client,
                                        messages,
                                        max_tokens=2048,
                                        model=model
                                    )
                                    continue
                                else:
                                    print(f"  当前迭代重试{max_retries_for_position}次后仍选择无效帧")
                                    current_best_frame = None
                                    break
                    else:
                        print(f"  第{round_num}轮LLM未返回有效结果")
                        break
            
            if current_best_frame is not None:
                print(f"  当前迭代最佳帧: {current_best_frame}")
            else:
                print("  LLM未返回有效结果")
                print(f"  LLM响应: {response[:200]}...")  # 打印前200个字符用于调试
                
                # 检查是否是选择了无效位置
                try:
                    resp_json = json.loads(response)
                    if "target_frame" in resp_json:
                        target_frame = resp_json["target_frame"]
                        print(f"  LLM选择了帧号 {target_frame}，但有效帧号范围是: {current_candidates}")
                except:
                    pass
                
                # 如果没有有效结果，使用候选帧的中间值
                if current_candidates:
                    current_best_frame = current_candidates[len(current_candidates)//2]
                    print(f"  使用候选帧中间值作为最佳帧: {current_best_frame}")
                else:
                    break
                
        except Exception as e:
            print(f"  LLM推理过程中出错: {e}")
            # 出错时使用候选帧的中间值
            if current_candidates:
                current_best_frame = current_candidates[len(current_candidates)//2]
                print(f"  出错时使用候选帧中间值作为最佳帧: {current_best_frame}")
            else:
                break
        
        # 5.2 记录当前迭代结果
        print(f"  准备记录迭代结果，当前最佳帧: {current_best_frame}")
        iteration_result = {
            "iteration": iteration_count,
            "window_size": current_window_size,
            "candidates": current_candidates,
            "best_frame": current_best_frame,
            "method": "voting" if iteration_count == 1 else "single",
            "llm_response": response if 'response' in locals() else None,
            "voting_results": voting_results if iteration_count == 1 else None,
            "all_voting_details": all_voting_details if iteration_count == 1 else None
        }
        iteration_results.append(iteration_result)
        print(f"  迭代结果已记录，最佳帧: {iteration_result['best_frame']}")
        
        # 保存当前迭代结果
        with open(os.path.join(iteration_dir, "iteration_result.json"), "w", encoding="utf-8") as f:
            json.dump(iteration_result, f, indent=4, ensure_ascii=False)
        
        # 5.3 生成新的候选帧范围
        if current_window_size <= min_window_size:
            print(f"  窗口大小已达到最小值 {min_window_size}，停止迭代")
            break
        
        # 计算新的候选帧范围
        half_window = current_window_size // 2
        new_start = max(0, current_best_frame - half_window)
        new_end = min(num_frames - 1, current_best_frame + half_window)
        
        # 生成新的候选帧列表（每5帧一个）
        new_candidates = []
        for i in range(new_start, new_end + 1, current_window_size//5):
            if i not in new_candidates:
                new_candidates.append(i)
        
        # 确保包含当前最佳帧
        if current_best_frame not in new_candidates:
            new_candidates.append(current_best_frame)
            new_candidates.sort()
        
        print(f"  新候选帧范围: {new_start} - {new_end}，候选帧数量: {len(new_candidates)}")
        
        # 更新候选帧和窗口大小
        current_candidates = new_candidates
        current_window_size = half_window
        
        # 等待一段时间再进行下一次迭代
        if iteration_count < max_iterations:
            print(f"  等待5秒后进行下一次迭代...")
            time.sleep(5)
    
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
    final_grid = create_final_iterative_grid(segment_dir, final_candidates, iteration_results)
    
    # 初始化最终结果变量
    final_end_frame = None
    final_voting_results = None
    final_voting_details = None
    final_llm_response = None  # 确保在所有情况下都有定义

    # 如果只有一个唯一的候选帧（除了最后的参考帧），就直接选它
    if len(final_candidates) <= 2:
        candidate_frame = -1
        for frame in final_candidates:
            if frame != num_frames - 1:
                candidate_frame = frame
                break
        
        if candidate_frame != -1:
            final_end_frame = candidate_frame
            final_llm_response = None  # 直接选择时没有LLM响应
            print(f"最终候选帧只有一个有效选项 {final_end_frame}，直接采纳为最终结果。")
        elif final_candidates:
            final_end_frame = final_candidates[0]
            final_llm_response = None  # 直接选择时没有LLM响应
            print(f"最终候选帧只有最后一帧 {final_end_frame}，直接采纳为最终结果。")
        else: # Should not happen given previous checks, but for safety
             final_end_frame = all_best_frames[-1] if all_best_frames else None
             final_llm_response = None  # 直接选择时没有LLM响应
    elif final_grid:
        final_voting_results = {}
        final_voting_details = []
        final_llm_response = None  # 初始化变量
        
        final_grid_path = os.path.join(experiment_dir, "final_grid.png")
        final_grid.save(final_grid_path)
        
        position_to_frame_map = {i + 1: frame for i, frame in enumerate(final_candidates)}
        final_prompt = (
            f"You are a helpful assistant that can help me analyze the page loading process. "
            f"Below is a grid of frames from a video showing the page loading process. "
            f"The frames are arranged from left to right, top to bottom.\n\n"
            f"## Context:\n"
            f"1. Event type: load_end_time\n"
            f"2. Grid layout:  Blue border = Last frame (end), Green border = Iteration result, Gray borders = Other candidate frames\n"
            f"3. we are focusing on a narrower range for precise detection\n"
            f"4. Available candidate frame numbers: {all_best_frames}\n\n"
            f"## Definition of end frame:\n"
            f"1. The first end frame is the first frame where the page is fully loaded after the operation\n"
            f"2. The page must be completely loaded with no white spaces or loading indicators\n"
            f"3. Loading popups and dialogs must have disappeared\n"
            f"4. If the interface before and after loading looks similar, the loading completion time must be later - do not choose frames from before loading\n"
            f"5. The page must have changed from the previous page to the desired page after the operation\n"
            f"## Task:\n"
            f"First, carefully analyze each frame in the grid (from left to right, top to bottom) and describe the subtle changes you observe between consecutive frames.\n"
            f"  ##Pay special attention to:\n"
            f"- Small changes in UI elements,and which UI elements doesn't appear\n"
            f"- Slight color variations\n"
            f"- Loading indicators disappearing\n"
            f"- White spaces or loading elements being filled\n"
            f"- Loading popups and dialogs disappearing\n\n"
            f"- ##Ignorging:\n"
            f"- Any banner movement or animation changing or advertisement image changing\n"
            f"- Minor non-content visual changes\n"
            f"- Floating elements such as floating buttons which may be testing components\n"
            f"- There may be a gray double circle in the lower middle of the page (system button) - please ignore it\n\n"
            f"- Scrolling of small texts\n"
            f"Then, identify which frame shows the end of page loading.(end of change,first frame after all changes)\n"
            f"## IMPORTANT: You must choose from the candidate frames (gray borders) only. Do NOT select the end frame (blue border, last frame) - it is only for reference.\n"
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
                print(final_response)
                selected_frame = None
                max_retries_for_position = 3  # 最大重试次数
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
                                    # 重新请求
                                    messages = [{"role": "user", "content": final_prompt, "image_url": [final_grid_path]}]
                                    final_response = llm_vision_request_with_retry(
                                        llm_client,
                                        messages,
                                        max_tokens=2048,
                                        model=model
                                    )
                                    continue
                                else:
                                    print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                    selected_frame = None
                                    break
                    except:
                        pattern = r"```(?:json\s*)?\n([\s\S]+?)\n```"
                        match = re.search(pattern, final_response)
                        if match:
                            resp_json = json.loads(match.group(1))
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
                                        # 重新请求
                                        messages = [{"role": "user", "content": final_prompt, "image_url": [final_grid_path]}]
                                        final_response = llm_vision_request_with_retry(
                                            llm_client,
                                            messages,
                                            max_tokens=2048,
                                            model=model
                                        )
                                        continue
                                    else:
                                        print(f"    第{round_num}轮重试{max_retries_for_position}次后仍选择无效帧")
                                        selected_frame = None
                                        break
                    else:
                        print(f"    第{round_num}轮LLM未返回有效结果")
                        break

                if selected_frame is not None:
                    print(f"    第{round_num}轮选择帧: {selected_frame}")
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
                        break
                else:
                    print(f"    第{round_num}轮LLM未返回有效结果")
                    print(f"    LLM响应: {final_response[:200]}...")  # 打印前200个字符用于调试
                    
                    # 检查是否是选择了无效位置
                    try:
                        resp_json = json.loads(final_response)
                        if "target_frame" in resp_json:
                            target_frame = resp_json["target_frame"]
                            print(f"    LLM选择了帧号 {target_frame}，但有效帧号范围是: {all_best_frames}")
                    except:
                        pass
                    
                    final_voting_details.append({"round": round_num, "selected_frame": None, "llm_results": final_response, "error": "LLM未返回有效结果"})

            except Exception as e:
                print(f"  最终投票第{round_num}轮过程中出错: {e}")
                final_voting_details.append({"round": round_num, "selected_frame": None, "llm_results": None, "error": str(e)})

            if round_num < max_voting_rounds:
                print(f"  等待5秒后进行下一轮投票...")
                time.sleep(5)

        if final_voting_results:
            final_end_frame = max(final_voting_results.items(), key=lambda x: x[1])[0]
            max_votes = final_voting_results[final_end_frame]
            print(f"\n最终投票结果: {final_voting_results}")
            print(f"最终选择帧: {final_end_frame} (获得 {max_votes} 票)")
            
            # 找到最终选择帧对应的LLM响应
            final_llm_response = None
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
    
    else:
        print("无法创建最终网格")
        if all_best_frames:
            final_end_frame = all_best_frames[len(all_best_frames)//2]
            print(f"使用候选帧中间值作为最终结果: {final_end_frame}")
            final_llm_response = None
        else:
            print("没有候选帧可用")
            final_end_frame = None
            final_llm_response = None

    # 7. 保存最终结果
    final_result = {
        "segment_dir": segment_dir,
        "final_end_frame": final_end_frame,
        "final_llm_response": final_llm_response,
        "iteration_results": iteration_results,
        "final_candidates": final_candidates,
        "final_voting_results": final_voting_results,
        "final_voting_details": final_voting_details,
        "experiment_dir": experiment_dir
    }
    
    with open(os.path.join(experiment_dir, "final_result.json"), "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=4, ensure_ascii=False)
    
    # 8. 评估（如果需要）
    if do_evaluation:
        marked_end_time = action_info["original_action_item"]["marked_end_time"]
        gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
        gt_end_frame = max(0, gt_end_frame)
        
        result_entry = {
            "segment_dir": segment_dir,
            "llm_refined_start_frame": start_frame,
            "llm_refined_end_frame": final_end_frame,
            "llm_results_end": f"Iterative voting method with {len(iteration_results)} iterations"
        }
        
        evaluate_llm_narrow_results([result_entry])
    
    print(f"迭代细化voting方法处理完成: {segment_dir}")
    return final_result

def create_final_iterative_grid(segment_dir, final_candidates, iteration_results):
    """
    为最终投票创建网格，显示迭代过程和结果
    """
    from PIL import Image, ImageDraw, ImageFont
    import math
    
    if not final_candidates:
        return None
    
    # 读取action_info.json获取视频总帧数
    action_info_path = os.path.join(segment_dir, "action_info.json")
    with open(action_info_path, "r", encoding="utf-8") as f:
        action_info = json.load(f)
    num_frames = action_info["extraction_parameters"]["num_extracted_frames"]
    
    # 计算网格布局
    total_images = len(final_candidates)
    cols = min(5, total_images)
    rows = math.ceil(total_images / cols)
    
    # 设置图片尺寸
    cell_width = cell_height = 400
    label_height = 50
    canvas_width = cols * cell_width
    canvas_height = rows * (cell_height + label_height) + 100  # 额外空间用于标题和说明
    
    grid_image = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
    draw = ImageDraw.Draw(grid_image)
    
    try:
        font = ImageFont.truetype("Arial", 16)
        title_font = ImageFont.truetype("Arial", 20)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # 绘制标题
    title = "Final Iterative Voting Results"
    title_width = draw.textlength(title, font=title_font)
    title_x = (canvas_width - title_width) // 2
    draw.text((title_x, 10), title, fill=(0, 0, 0), font=title_font)
    
    # 绘制说明
    subtitle = f"Total iterations: {len(iteration_results)}, Final candidates: {len(final_candidates)}"
    subtitle_width = draw.textlength(subtitle, font=font)
    subtitle_x = (canvas_width - subtitle_width) // 2
    draw.text((subtitle_x, 40), subtitle, fill=(100, 100, 100), font=font)
    
    # 绘制每一帧
    for i, frame_idx in enumerate(final_candidates):
        row = i // cols
        col = i % cols
        
        x = col * cell_width
        y = row * (cell_height + label_height) + 80  # 为标题留出空间
        
        # 加载图片
        img = load_frame_from_npy(segment_dir, frame_idx)
        if img is None:
            continue
        
        # 确定边框颜色和标签
        if frame_idx == num_frames - 1:
            border_color = (0, 0, 255)  # 蓝色：尾帧
            label = ""  # 去掉尾帧的标号
            label_color = (0, 0, 255)
        else:
            # 检查是否是迭代结果
            is_iteration_result = any(result["best_frame"] == frame_idx for result in iteration_results)
            if is_iteration_result:
                border_color = (0, 128, 0)  # 绿色：迭代结果
                label = f"Frame {frame_idx} (Iteration Result)"
                label_color = (0, 128, 0)
            else:
                border_color = (128, 128, 128)  # 灰色：其他
                label = f"Frame {frame_idx}"
                label_color = (0, 0, 0)
        
        # 调整图片大小
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        
        if aspect_ratio > 1:
            new_width = cell_width - 6
            new_height = int(new_width / aspect_ratio)
            if new_height > cell_height - 6:
                new_height = cell_height - 6
                new_width = int(new_height * aspect_ratio)
        else:
            new_height = cell_height - 6
            new_width = int(new_height * aspect_ratio)
            if new_width > cell_width - 6:
                new_width = cell_width - 6
                new_height = int(new_width / aspect_ratio)
        
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        bordered_img = Image.new('RGB', (cell_width, cell_height), border_color)
        paste_x = (cell_width - new_width) // 2
        paste_y = (cell_height - new_height) // 2
        bordered_img.paste(resized_img, (paste_x, paste_y))
        grid_image.paste(bordered_img, (x, y))
        
        # 绘制标签
        if label:
            text_width = draw.textlength(label, font=font)
            text_x = x + (cell_width - text_width) // 2
            text_y = y + cell_height + 5
            draw.text((text_x, text_y), label, fill=label_color, font=font)
    
    return grid_image

