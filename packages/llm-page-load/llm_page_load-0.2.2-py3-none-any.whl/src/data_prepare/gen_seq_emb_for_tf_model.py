import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import json
import numpy as np
from ..utils.video_pre_tools import extract_frames_from_video,get_video_duration_ffmpeg,convert_to_cfr_ffmpeg_cli_realtime_output
from ..utils.frame_ssim_seq_gen_gpu import calculate_temporal_ssim_vectors_gpu
from ..utils.frame_ssim_seq_gen import calculate_temporal_ssim_vectors_mp
import torch
from random import shuffle
from PIL import Image # 用于保存图片
from ..utils.ssim_plot_utils import plot_temporal_ssim_vectors # Added import
import gc
from moviepy import ImageSequenceClip
import time
import argparse # 导入 argparse


def time_str_to_seconds(t_str):
    """支持 mm:ss.xx 或 mm:ss:ff (视为 mm:ss.ff) 格式，返回float秒"""
    if not t_str or not isinstance(t_str, str):
        print(f"警告: 时间字符串为空或非字符串类型: {t_str}")
        return None
    parts = t_str.split(':')
    try:
        if len(parts) == 2:
            # 标准 mm:ss.xx 解析
            m, s = parts
            return int(m) * 60 + float(s)
        elif len(parts) == 3:
            # 特殊解析 mm:ss:ff -> mm:ss.ff
            # parts[0] is minute, parts[1] is second, parts[2] is fraction
            min_part, sec_part, frac_part = parts
            print(f"信息: 输入为3段 '{t_str}', 按 mm:ss:ff -> mm:ss.ff 规则解析: {min_part}:{sec_part}.{frac_part}")
            seconds_with_fraction_str = sec_part + "." + frac_part
            return int(min_part) * 60 + float(seconds_with_fraction_str)
        else:
            print(f"警告: 时间字符串格式无法解析: {t_str} (部分数量: {len(parts)}). 支持 mm:ss.xx 或 mm:ss:ff.")
            return None
    except ValueError as e_main:
        print(f"警告: 转换时间字符串 '{t_str}' 时发生错误: {e_main}")
        return None

def format_time_for_path(time_val):
    """将float时间转换为适合路径的字符串，例如 123.456 -> 123_456s"""
    if time_val is None:
        return "unknown_time"
    return str(time_val).replace('.', '_') + "s"

def save_critical_frames(frames, frame_indices_map, base_save_path, fps, sequence_start_time_sec):
    """
    保存指定时间点及其左右3帧的图片。
    frames: 提取的帧列表 (numpy arrays)
    frame_indices_map: dict, e.g., {"action_time_in_seq": frame_idx_for_action_time, ...}
                       键是描述，值是该事件在frames列表中的索引。
    base_save_path: 保存图片的目录
    fps: 帧率
    sequence_start_time_sec: 当前帧序列在原视频中的开始时间（秒）
    """
    if not frames:
        print("警告: 帧列表为空，无法保存关键帧。")
        return

    os.makedirs(base_save_path, exist_ok=True)
    num_frames_in_sequence = len(frames)

    for event_name, center_frame_idx_in_seq in frame_indices_map.items():
        if center_frame_idx_in_seq is None or not (0 <= center_frame_idx_in_seq < num_frames_in_sequence):
            print(f"警告: 事件 '{event_name}' 的帧索引 {center_frame_idx_in_seq} 无效或越界 (序列长度 {num_frames_in_sequence})，跳过保存其关键帧。")
            continue

        for offset in range(-3, 4): # 提取中心帧及左右各3帧
            current_frame_idx_in_seq = center_frame_idx_in_seq + offset
            if 0 <= current_frame_idx_in_seq < num_frames_in_sequence:
                try:
                    frame_pil = Image.fromarray(frames[current_frame_idx_in_seq])
                    # 帧在原视频中的绝对时间 = sequence_start_time_sec + current_frame_idx_in_seq / fps
                    # 帧相对于事件发生点的偏移 (以帧为单位)
                    # frame_timestamp_in_video = sequence_start_time_sec + (current_frame_idx_in_seq / fps)
                    
                    # 文件名：事件名_偏移量_序列中的帧号.png
                    img_filename = f"{event_name}_offset_{offset:+d}_seqidx_{current_frame_idx_in_seq}.png"
                    img_path = os.path.join(base_save_path, img_filename)
                    frame_pil.save(img_path)
                except Exception as e:
                    print(f"错误: 保存帧图片 {img_filename} 失败: {e}")


def find_json_video_files(data_dir):
    """扫描数据目录，找到所有json文件及其对应的视频文件。"""
    json_video_pairs = []
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        print(f"在目录 {data_dir} 中未找到 JSON 文件。")
        return []
        
    for json_file_name in json_files:
        json_file_path = os.path.join(data_dir, json_file_name)
        video_file_base_name = os.path.splitext(json_file_name)[0]
        
        raw_video_path = None
        possible_video_extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']
        for ext in possible_video_extensions:
            temp_path = os.path.join(data_dir, video_file_base_name + ext)
            if os.path.exists(temp_path):
                raw_video_path = temp_path
                break
        
        if not raw_video_path:
            print(f"警告: 未找到与 {json_file_name} 对应的视频文件。跳过此JSON文件。")
            continue
        json_video_pairs.append((json_file_path, raw_video_path))
    
    return json_video_pairs


def process_single_json_video_pair(json_file_path, raw_video_path, detailed_output_root_dir, offsets, target_fps=30, overwrite_existing_action_items: bool = False, save_all_extracted_frames: bool = False, generate_ssim_sequence: bool = True, save_frames_as_video: bool = False, target_gpu_id: int | None = None):
    """
    处理单个JSON文件及其对应的视频文件。
    提取特征，保存细粒度数据，并返回可供 `convert_to_model_dataset` 使用的数据。
    
    Args:
        json_file_path: JSON文件路径。
        raw_video_path: 原始视频文件路径。
        detailed_output_root_dir: 详细输出的根目录。
        offsets: SSIM计算的偏移量列表。
        target_fps: 目标帧率，默认30fps。
        overwrite_existing_action_items: 是否覆盖已存在的处理结果。
        save_all_extracted_frames: 是否保存所有提取的帧为NumPy数组。
        generate_ssim_sequence: 是否计算和生成SSIM相似度序列。
        save_frames_as_video: 是否将提取的帧保存为视频
        target_gpu_id: 指定GPU ID，传递给SSIM GPU计算函数
    """
    print(f"开始处理 JSON: {os.path.basename(json_file_path)}, 视频: {os.path.basename(raw_video_path)}")
    
    json_filename_no_ext = os.path.splitext(os.path.basename(json_file_path))[0]
    json_specific_output_dir = os.path.join(detailed_output_root_dir, json_filename_no_ext)
    os.makedirs(json_specific_output_dir, exist_ok=True)

    video_file_base_name = os.path.splitext(os.path.basename(raw_video_path))[0]
    data_dir_of_video = os.path.dirname(raw_video_path) 
    output_video_name = video_file_base_name + f'_{target_fps}fps.mp4'
    output_video_path = os.path.join(data_dir_of_video, output_video_name) 

    if not os.path.exists(output_video_path):
        print(f"转换视频 {raw_video_path} 至 {target_fps}fps...")
        # 假设 convert_to_cfr_ffmpeg_cli_realtime_output 成功时返回True或输出路径，失败时返回False或None
        # 在此我们假设它会处理打印错误信息，如果失败，后续的os.path.exists会处理
        convert_to_cfr_ffmpeg_cli_realtime_output(raw_video_path, output_video_path, target_fps=target_fps)
        if not os.path.exists(output_video_path): # 再次检查确保转换成功
             print(f"错误: 转换视频 {raw_video_path} 失败，目标文件 {output_video_path} 未创建。跳过此JSON文件。")
             return []
    else:
        print(f"已存在转换后的视频: {output_video_path}")
    
    current_video_path_for_processing = output_video_path
    if not os.path.exists(current_video_path_for_processing): # 双重检查
        print(f"错误: 目标处理视频 {current_video_path_for_processing} 不存在。")
        return []

    video_duration = get_video_duration_ffmpeg(current_video_path_for_processing)
    if video_duration is None:
        print(f"错误: 无法获取视频 {current_video_path_for_processing} 的时长。")
        return []

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_content = json.load(f)
    except Exception as e:
        print(f"错误：读取或解析JSON文件 {json_file_path} 失败: {e}")
        return []
    #适配不同格式的json文件
    json_content = json_content.get("video_action_data") or json_content
    action_list_original = json_content.get('action_list', [])
    if not action_list_original:
        print(f"警告: {os.path.basename(json_file_path)} 中的 action_list 为空。")

    processed_action_list = []
    for item_orig in action_list_original:
        item = item_orig.copy() 
        valid_item = True
        original_action_time_str = str(item.get('action_time', 'N/A')) # 用于日志

        for key in ["action_time", "marked_response_time", "marked_end_time"]:
            if key in item and item[key] is not None:
                original_time_val_str = str(item[key])
                item[key] = time_str_to_seconds(item[key])
                if item[key] is None: 
                    print(f"警告: action_item (原始action_time: {original_action_time_str}) 的时间字段 '{key}' (原始值: {original_time_val_str}) 转换失败。")
                    valid_item = False
                    break
        
        if not valid_item: continue # 如果核心时间转换失败，跳过这个item

        if "marked_loading_event" in item and isinstance(item["marked_loading_event"], list):
            for ev_idx, ev in enumerate(item["marked_loading_event"]):
                for k_load in ["loading_start_time", "loading_end_time"]:
                    if k_load in ev and ev[k_load] is not None:
                        original_loading_time_str = str(ev[k_load])
                        ev[k_load] = time_str_to_seconds(ev[k_load])
                        if ev[k_load] is None:
                            print(f"警告: action_item (原始action_time: {original_action_time_str}) 的 loading_event {ev_idx} 时间字段 '{k_load}' (原始值: {original_loading_time_str}) 转换失败。")
        
        if not all(k in item and isinstance(item[k], (int, float)) for k in ['marked_response_time', 'marked_end_time', 'action_time']):
            print(f"警告: action_item (原始action_time: {original_action_time_str}) 缺少转换后的有效核心时间戳 (action_time, marked_response_time, marked_end_time)，已跳过。")
            valid_item = False

        if valid_item:
            processed_action_list.append(item)
        
    if not processed_action_list:
        print(f"警告: {os.path.basename(json_file_path)} 中没有有效的 action items (过滤和时间转换后)。")

    sequences_for_this_json = [] 

    for index, action_item in enumerate(processed_action_list):
        action_time = action_item.get('action_time')
        marked_response_time = action_item.get('marked_response_time')
        marked_end_time = action_item.get('marked_end_time')

        # --- Cache Check Logic ---
        dir_name_for_action_item: str
        if action_time is not None:
            dir_name_for_action_item = format_time_for_path(action_time)
        else:
            dir_name_for_action_item = f"action_item_idx_{index}"
        
        action_item_output_dir = os.path.join(json_specific_output_dir, dir_name_for_action_item)
        
        ssim_pt_path = os.path.join(action_item_output_dir, "ssim_sequence.pt")
        action_info_path = os.path.join(action_item_output_dir, "action_info.json")
        # Optional: plot_output_path_check = os.path.join(action_item_output_dir, "ssim_profile_plot.png")

        cached_data_loaded = False
        cached_ssim_vector_results = None
        
        # --- 缓存检查逻辑 ---
        if not overwrite_existing_action_items and \
           os.path.exists(action_item_output_dir) and \
           os.path.exists(ssim_pt_path) and \
           os.path.exists(action_info_path):
            try:
                print(f"  尝试从缓存加载 action (Time: {action_time:.2f}s if available else idx {index}) from {action_item_output_dir}")
                loaded_ssim_tensor = torch.load(ssim_pt_path)
                cached_ssim_vector_results = loaded_ssim_tensor.tolist() # Convert tensor to list of lists

                with open(action_info_path, 'r', encoding='utf-8') as f_info_cached:
                    loaded_action_info = json.load(f_info_cached)
                
                extraction_params_cached = loaded_action_info.get("extraction_parameters", {})
                extract_start_time_sec_cached = extraction_params_cached.get("extract_start_time_sec")
                extract_end_time_sec_cached = extraction_params_cached.get("extract_end_time_sec")
                video_duration_cached = extraction_params_cached.get("video_duration", video_duration) # Use current video_duration as fallback
                fps_cached = extraction_params_cached.get("fps", target_fps) # Use current target_fps as fallback

                if cached_ssim_vector_results and \
                   extract_start_time_sec_cached is not None and \
                   extract_end_time_sec_cached is not None:
                    
                    # 如果只需要SSIM数据（不需要提取帧或生成视频），则直接添加到结果列表并跳过后续步骤
                    if not save_all_extracted_frames and not save_frames_as_video:
                        current_seq_data = {
                            'ssim_vector': cached_ssim_vector_results,
                            'action_item': action_item, # Still use the current action_item from the loop
                            'start_time': extract_start_time_sec_cached,
                            'end_time': extract_end_time_sec_cached,
                            'video_duration': video_duration_cached,
                            "marked_response_time": marked_response_time, # From current action_item
                            "marked_end_time": marked_end_time,         # From current action_item
                            "fps": fps_cached
                        }
                        sequences_for_this_json.append(current_seq_data)
                        print(f"    成功从缓存加载SSIM数据 (Time: {action_time:.2f}s if available else idx {index}). 跳过重新生成。")
                        
                        if loaded_ssim_tensor is not None:
                            del loaded_ssim_tensor # Free up tensor memory if loaded
                        
                        continue # 跳过后续所有步骤
                    else:
                        # 如果需要提取帧或生成视频，则只标记SSIM数据已加载，后续仍需提取帧
                        cached_data_loaded = True
                        print(f"    成功从缓存加载SSIM数据，但仍需提取帧用于保存或生成视频。")
                else:
                    print(f"    缓存文件不完整或数据无效 for action (Time: {action_time:.2f}s if available else idx {index}). 将重新生成。")
            except Exception as e_cache:
                print(f"    从缓存加载 action (Time: {action_time:.2f}s if available else idx {index}) 失败: {e_cache}. 将重新生成。")
        
        # 如果加载了缓存的SSIM数据，但仍需要提取帧，则释放内存
        if cached_data_loaded and loaded_ssim_tensor is not None:
            del loaded_ssim_tensor # Free up tensor memory
            # 不使用continue，继续执行后续提取帧和生成视频的步骤
        # --- End of Cache Check Logic ---

        extract_start_time_sec = min(marked_response_time-5, action_time-5)
        extract_start_time_sec = max(0, extract_start_time_sec)
        extract_end_time_sec = max(marked_response_time+5, action_time+20)

        if index + 1 < len(processed_action_list):
            next_action_item = processed_action_list[index + 1]
            next_action_time = next_action_item.get('action_time')
            if isinstance(next_action_time, (int, float)):
                extract_end_time_sec = min(extract_end_time_sec, next_action_time - 3)
        
        extract_end_time_sec = min(extract_end_time_sec, video_duration)

        if extract_start_time_sec >= extract_end_time_sec:
            print(f"警告: 视频 {os.path.basename(current_video_path_for_processing)} action at {action_time:.2f}s 有效提取区间为零或负，跳过。Start: {extract_start_time_sec:.2f}, End: {extract_end_time_sec:.2f}")
            continue
        
        if not (extract_start_time_sec <= marked_response_time < extract_end_time_sec and \
                extract_start_time_sec <= marked_end_time <= extract_end_time_sec) :
            print(f"提示: 视频 {os.path.basename(current_video_path_for_processing)} action at {action_time:.2f}s 标注时间不在初始提取区间 [{extract_start_time_sec:.2f}s, {extract_end_time_sec:.2f}s] 内。 Resp: {marked_response_time:.2f}, End: {marked_end_time:.2f}。将按计算区间提取。")

        print(f"  处理action {index+1}/{len(processed_action_list)} (Time: {action_time:.2f}s), 提取帧区间: [{extract_start_time_sec:.2f}s, {extract_end_time_sec:.2f}s]")
        frames = extract_frames_from_video(current_video_path_for_processing, extract_start_time_sec, extract_end_time_sec)

        if not frames:
            print(f"  警告: 未能从视频区间提取到帧 for action at {action_time:.2f}s. 跳过此action_item。")
            continue

        num_extracted_frames = len(frames)

        # 处理SSIM数据 - 使用缓存数据或重新计算
        ssim_vector_results = []
        
        # 如果已经从缓存加载了SSIM数据，直接使用
        if cached_data_loaded and cached_ssim_vector_results:
            print(f"    使用缓存的SSIM数据 for action at {action_time:.2f}s...")
            ssim_vector_results = cached_ssim_vector_results
        # 否则，根据需要计算SSIM
        elif generate_ssim_sequence:
            print(f"    计算SSIM for action at {action_time:.2f}s...")
            if torch.cuda.is_available() and False:
                ssim_vector_results = calculate_temporal_ssim_vectors_gpu(frames, offsets, convert_to_gray=True, show_progress=False, target_gpu_id=target_gpu_id)
            else:
                ssim_vector_results = calculate_temporal_ssim_vectors_mp(frames, offsets,num_workers=12,convert_to_gray=True)
            
            if not ssim_vector_results or not isinstance(ssim_vector_results, list) or len(ssim_vector_results) == 0:
                print(f"  警告: 未能计算得到有效SSIM向量 for action at {action_time:.2f}s. 跳过此action_item。SSIM result: {ssim_vector_results}")
                del frames 
                continue
        else:
            print(f"    跳过SSIM计算 for action at {action_time:.2f}s (generate_ssim_sequence=False)")
            # 当不计算SSIM时，创建一个空的占位符，以便后续处理
            # 注意：这将导致SSIM相关步骤（如保存ssim_sequence.pt和绘图）被跳过或简化

        # Determine directory name for the action item - Simplified logic
        # dir_name_for_action_item: str
        # if action_time is not None:
        #     dir_name_for_action_item = format_time_for_path(action_time)
        # else:
        #     dir_name_for_action_item = f"action_item_idx_{index}" # Fallback if no time
        
        # action_item_output_dir = os.path.join(json_specific_output_dir, dir_name_for_action_item)
        os.makedirs(action_item_output_dir, exist_ok=True) # Ensure dir exists if not cached

        # 新增：如果需要，保存所有提取的帧（确保目录存在后）
        if save_all_extracted_frames and frames:
            try:
                # 使用 np.memmap 避免一次性加载所有帧到内存中
                if num_extracted_frames > 0:
                    frame_shape = frames[0].shape
                    print(f"frame_shape: {frame_shape}")
                    dtype = frames[0].dtype
                    print(f"dtype: {dtype}")
                    frames_npy_path = os.path.join(action_item_output_dir, "extracted_frames_sequence.npy")

                    # 1. 创建内存映射文件，在磁盘上分配空间，不占用大量RAM
                    fp = np.memmap(frames_npy_path, dtype=dtype, mode='w+', shape=(num_extracted_frames,) + frame_shape)

                    # 2. 逐帧写入文件
                    for i, frame in enumerate(frames):
                        fp[i] = frame

                    # 3. 确保数据写入磁盘并关闭文件
                    fp.flush()
                    del fp

                    print(f"    所有提取的 {num_extracted_frames} 帧已通过【memmap】高效保存到: {frames_npy_path}")
            except Exception as e_save_npy:
                print(f"    错误: 保存所有提取的帧为 NumPy 数组失败: {e_save_npy}")
        
        # 新增：如果需要，将提取的帧保存为视频
        if save_frames_as_video and frames:
            try:
                if num_extracted_frames > 0:
                    video_output_path = os.path.join(action_item_output_dir, "extracted_frames_video.mp4")
                    
                    # 使用 moviepy 的 ImageSequenceClip 将帧序列转换为视频
                    clip = ImageSequenceClip(frames, fps=target_fps)
                    
                    # 保存视频文件 - 兼容不同版本的MoviePy
                    try:
                        # 尝试使用新版本API (MoviePy 2.x)
                        clip.write_videofile(video_output_path, codec='libx264', audio=False, verbose=False, logger=None)
                    except TypeError:
                        # 如果失败，尝试使用旧版本API (MoviePy 1.x)
                        clip.write_videofile(video_output_path, codec='libx264', audio=False)
                    
                    # 释放资源
                    clip.close()
                    
                    print(f"    所有提取的 {num_extracted_frames} 帧已保存为视频: {video_output_path}")
            except Exception as e_save_video:
                print(f"    错误: 保存帧为视频失败: {e_save_video}")

        action_item_info_to_save = {
            "original_action_item": action_item, 
            "extraction_parameters": {
                "video_path": current_video_path_for_processing,
                "extract_start_time_sec": extract_start_time_sec,
                "extract_end_time_sec": extract_end_time_sec,
                "fps": target_fps,
                "num_extracted_frames": num_extracted_frames,
                "video_duration": video_duration,
                "frame_shape": list(frame_shape) if 'frame_shape' in locals() else None,
                "dtype": str(dtype) if 'dtype' in locals() else None
            }
        }
        action_info_path = os.path.join(action_item_output_dir, "action_info.json")
        try:
            with open(action_info_path, 'w', encoding='utf-8') as f_info:
                json.dump(action_item_info_to_save, f_info, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"    错误: 保存 action_info.json for action at {action_time:.2f}s 失败: {e}")

        # 仅当generate_ssim_sequence=True且有SSIM数据时保存SSIM序列
        ssim_tensor_for_saving = None  # 初始化为None，以便后续逻辑判断
        ssim_pt_path = os.path.join(action_item_output_dir, "ssim_sequence.pt")
        
        if generate_ssim_sequence and ssim_vector_results:
            try:
                # Ensure ssim_vector_results are lists of numbers or handle appropriately
                processed_ssim_for_saving = []
                expected_offsets_len = len(offsets)
                for ssim_list in ssim_vector_results:
                    if isinstance(ssim_list, list):
                        # Replace None with a placeholder like -1.0, ensure correct length
                        current_frame_ssims = [(s if isinstance(s, (int, float)) else -1.0) for s in ssim_list]
                        # Pad or truncate if necessary
                        if len(current_frame_ssims) < expected_offsets_len:
                            current_frame_ssims.extend([-1.0] * (expected_offsets_len - len(current_frame_ssims)))
                        elif len(current_frame_ssims) > expected_offsets_len:
                            current_frame_ssims = current_frame_ssims[:expected_offsets_len]
                        processed_ssim_for_saving.append(current_frame_ssims)
                    else: # If a frame's ssim calculation failed and returned not a list
                        processed_ssim_for_saving.append([-1.0] * expected_offsets_len)
                
                if not processed_ssim_for_saving: # Should not happen if ssim_vector_results check passed
                    print(f"    警告: processed_ssim_for_saving 为空 for action at {action_time:.2f}s, 无法保存SSIM序列。")
                else:
                    ssim_tensor_for_saving = torch.tensor(processed_ssim_for_saving, dtype=torch.float32)
                    torch.save(ssim_tensor_for_saving, ssim_pt_path)
                    print(f"    已保存SSIM序列到: {ssim_pt_path}")
            except Exception as e:
                print(f"    错误: 保存 ssim_sequence.pt for action at {action_time:.2f}s 失败: {e}")
        elif not generate_ssim_sequence:
            print(f"    跳过保存SSIM序列 (generate_ssim_sequence=False)")
            # print(f"    SSIM vector for saving: {ssim_vector_results[:2] if ssim_vector_results else 'None or empty'}")

        critical_frame_indices = {}
        action_frame_idx = int(round((action_time - extract_start_time_sec) * target_fps)) if action_time is not None else None
        resp_frame_idx = int(round((marked_response_time - extract_start_time_sec) * target_fps)) if marked_response_time is not None else None
        end_frame_idx = int(round((marked_end_time - extract_start_time_sec) * target_fps)) if marked_end_time is not None else None
        
        if action_frame_idx is not None and 0 <= action_frame_idx < num_extracted_frames:
            critical_frame_indices["action_time"] = action_frame_idx
        if resp_frame_idx is not None and 0 <= resp_frame_idx < num_extracted_frames:
            critical_frame_indices["response_start_time"] = resp_frame_idx
        if end_frame_idx is not None and 0 <= end_frame_idx < num_extracted_frames:
            critical_frame_indices["load_end_time"] = end_frame_idx
        
        if critical_frame_indices:
            save_critical_frames(frames, critical_frame_indices, action_item_output_dir, target_fps, extract_start_time_sec)
        # else:
            # print(f"    警告: 没有有效的关键帧索引可以用于保存图片 for action at {action_time:.2f}s")

        # --- Call plotting function (仅当generate_ssim_sequence=True时) --- 
        if generate_ssim_sequence and ssim_vector_results:
            event_times_sec_relative = {}
            event_frame_image_paths_for_plot = {}
            event_mapping_for_plot = {
                "action_time": action_time,
                "response_start_time": marked_response_time, # Use the same key as in save_critical_frames
                "load_end_time": marked_end_time         # Use the same key as in save_critical_frames
            }

            for event_key_in_map, event_actual_time_sec in event_mapping_for_plot.items():
                if event_actual_time_sec is not None and extract_start_time_sec is not None:
                    relative_time = event_actual_time_sec - extract_start_time_sec
                    # Only plot if event is within the extracted sequence duration
                    if 0 <= relative_time <= (extract_end_time_sec - extract_start_time_sec):
                        event_times_sec_relative[event_key_in_map] = relative_time
                        
                        # Check if we have a saved central frame for this event
                        # The keys in critical_frame_indices are like "action_time", "response_start_time", "load_end_time"
                        if event_key_in_map in critical_frame_indices:
                            frame_idx_for_event = critical_frame_indices[event_key_in_map]
                            if frame_idx_for_event is not None: # Ensure frame_idx is valid
                                # Construct the image filename for the central frame (offset 0)
                                img_filename_plot = f"{event_key_in_map}_offset_0_seqidx_{frame_idx_for_event}.png"
                                img_full_path_plot = os.path.join(action_item_output_dir, img_filename_plot)
                                if os.path.exists(img_full_path_plot):
                                    event_frame_image_paths_for_plot[event_key_in_map] = img_full_path_plot
                                # else:
                                    # print(f"Debug: Image for plot not found: {img_full_path_plot}")
            
            # Only plot if ssim results are available
            plot_title = f"SSIM: {json_filename_no_ext} - Action Time {action_time:.2f}s"
            plot_output_path = os.path.join(action_item_output_dir, "ssim_profile_plot.png")
            try:
                plot_temporal_ssim_vectors(
                    ssim_vectors=ssim_vector_results,
                    offsets=offsets,
                    x_axis_type="time",
                    fps=target_fps,
                    title=plot_title,
                    output_path=plot_output_path,
                    show_plot=False, # Typically False for batch processing
                    event_times_sec=event_times_sec_relative,
                    event_frame_image_paths=event_frame_image_paths_for_plot
                )
                print(f"    已生成SSIM图表: {plot_output_path}")
            except Exception as e_plot:
                print(f"    错误: 绘制SSIM图表 for action at {action_time:.2f}s 失败: {e_plot}")
        elif not generate_ssim_sequence:
            print(f"    跳过绘制SSIM图表 (generate_ssim_sequence=False)")
        # --- End of plotting call ---

        # 准备当前序列的数据
        current_seq_data = {
            'action_item': action_item, 
            'start_time': extract_start_time_sec, 
            'end_time': extract_end_time_sec,   
            'video_duration': video_duration,
            "marked_response_time": marked_response_time,
            "marked_end_time": marked_end_time,
            "fps": target_fps
        }
        
        # 仅当生成了SSIM数据时才添加SSIM向量
        if generate_ssim_sequence and ssim_vector_results:
            current_seq_data['ssim_vector'] = ssim_vector_results
        else:
            # 如果没有生成SSIM数据，添加一个空列表作为占位符
            # 注意：这可能会导致后续的模型转换步骤（convert_to_model_dataset）失败，
            # 除非该函数也针对generate_ssim_sequence=False的情况进行了修改
            current_seq_data['ssim_vector'] = []
            
        sequences_for_this_json.append(current_seq_data)
        
        del frames
    
    print(f"JSON文件 {os.path.basename(json_file_path)} 处理完毕，初步生成 {len(sequences_for_this_json)} 个序列。")
    return sequences_for_this_json


def convert_to_model_dataset(raw_train_data_single_video, offsets, fps=30):
    labels_map = { "O": 0,  "LOADING": 1 }
    op_type_mapping = { "default": 0 }
    dataset = []
    
    if not raw_train_data_single_video or len(raw_train_data_single_video) != 1:
        print("错误: convert_to_model_dataset 期望 raw_train_data_single_video 是包含单个视频条目的列表。")
        return []

    video_item = raw_train_data_single_video[0]
    video_path_for_logging = video_item.get('video_path', 'N/A_video') 
    seq_list = video_item.get('seq_raw_data', [])

    for seq_idx, seq_data in enumerate(seq_list): 
        ssim_vector_raw = seq_data.get('ssim_vector')
        action_item = seq_data.get('action_item', {})
        action_name_for_log = action_item.get('action_name', f'Seq_{seq_idx}')
        log_prefix = f"Video '{os.path.basename(video_path_for_logging)}', Action '{action_name_for_log}' (SeqIdx {seq_idx}):"

        if not ssim_vector_raw or not isinstance(ssim_vector_raw, list):
            print(f"{log_prefix} SSIM向量为空或格式不正确，已跳过。SSIM: {ssim_vector_raw}")
            continue
        
        seq_len = len(ssim_vector_raw)
        if seq_len == 0:
            print(f"{log_prefix} SSIM向量长度为0，已跳过。")
            continue

        processed_ssim_vector = []
        expected_num_offsets = len(offsets)
        for frame_ssims_idx, frame_ssims in enumerate(ssim_vector_raw):
            if isinstance(frame_ssims, list): 
                processed_frame_ssims = [val if isinstance(val, (int,float)) and val is not None else -1.0 for val in frame_ssims] 
                if len(processed_frame_ssims) != expected_num_offsets:
                    processed_frame_ssims.extend([-1.0] * (expected_num_offsets - len(processed_frame_ssims)))
                processed_frame_ssims = processed_frame_ssims[:expected_num_offsets] 
                processed_ssim_vector.append(processed_frame_ssims)
            else:
                processed_ssim_vector.append([-1.0] * expected_num_offsets) 
        
        if not processed_ssim_vector: # Should not happen if ssim_vector_raw had content
            print(f"{log_prefix} processed_ssim_vector为空，跳过。")
            continue
            
        try:
            ssim_tensor = torch.tensor(processed_ssim_vector, dtype=torch.float32)
        except Exception as e:
            print(f"{log_prefix} 转换 processed_ssim_vector 到张量失败: {e}。processed_ssim_vector (first 2): {processed_ssim_vector[:2]}... 跳过此序列。")
            continue

        op_type_str = action_item.get('op_type', 'default') 
        op_type_id = op_type_mapping.get(op_type_str, op_type_mapping['default']) 
        op_type_tensor = torch.tensor(op_type_id, dtype=torch.long)

        op_frame_flag = torch.zeros(seq_len, 1, dtype=torch.float32) 
        action_time = action_item.get('action_time')
        start_time_seq = seq_data.get('start_time')  
        current_fps_of_seq = seq_data.get('fps', fps) 

        if action_time is not None and start_time_seq is not None:
            op_idx_float = (action_time - start_time_seq) * current_fps_of_seq
            op_idx = int(round(op_idx_float))
            if 0 <= op_idx < seq_len:
                op_frame_flag[op_idx, 0] = 1.0
        
        labels = torch.full((seq_len,), labels_map["O"], dtype=torch.long)
        marked_response_time = seq_data.get('marked_response_time')
        marked_end_time = seq_data.get('marked_end_time')

        if all(isinstance(t, (int, float)) for t in [marked_response_time, marked_end_time, start_time_seq]):
            resp_idx_float = (marked_response_time - start_time_seq) * current_fps_of_seq
            load_end_idx_float = (marked_end_time - start_time_seq) * current_fps_of_seq

            resp_idx = max(0, min(int(round(resp_idx_float)), seq_len - 1))
            load_end_idx = max(0, min(int(round(load_end_idx_float)), seq_len - 1))

            if resp_idx <= load_end_idx : 
                labels[resp_idx] = labels_map["LOADING"]
                labels[load_end_idx] = labels_map["LOADING"]
                
                # 确保resp_idx + 1 不超过 load_end_idx -1 (即它们之间至少有一个元素)
                if resp_idx + 1 <= load_end_idx -1 : 
                    labels[resp_idx + 1 : load_end_idx] = labels_map["LOADING"]
                else:
                    print(f"{log_prefix} marked_response_time ({marked_response_time:.2f}s from seq_start {start_time_seq:.2f}s -> frame {resp_idx}) 晚于 marked_end_time ({marked_end_time:.2f}s from seq_start {start_time_seq:.2f}s -> frame {load_end_idx}). 标签可能不正确。")

            dataset.append({
                "ssim_features": ssim_tensor,    
                "op_type": op_type_tensor,       
                "op_frame_flag": op_frame_flag,  
                "labels": labels                 
            })
    return dataset

def get_json_video_path_pairs_v1(data_dir):
    json_video_file_pairs = find_json_video_files(data_dir)
    return json_video_file_pairs

def get_json_video_path_pairs_v2(data_dir):
    """
    获取JSON和视频文件路径对 - 支持两种数据结构：
    1. 旧格式：每个文件夹包含 {场景名}.json 和 {场景名}.mp4
    2. 转换后的新格式：每个文件夹包含 {视频名}.json 和对应的视频文件
    """
    json_video_file_pairs = []
    dir_list = os.listdir(data_dir)
    
    for dir_name in dir_list:
        dir_path = os.path.join(data_dir, dir_name)
        if not os.path.isdir(dir_path):
            continue
            
        # 跳过以 _info 结尾的目录（这些是信息目录，不是视频目录）
        if dir_name.endswith('_info'):
            continue
            
        # 方法1：尝试旧格式 - {场景名}.json 和 {场景名}.mp4
        json_path_old = os.path.join(dir_path, f"{dir_name}.json")
        video_path_old = os.path.join(dir_path, f"{dir_name}.mp4")
        
        if os.path.exists(json_path_old) and os.path.exists(video_path_old):
            json_video_file_pairs.append((json_path_old, video_path_old))
            continue
            
        # 方法2：尝试转换后的新格式 - 查找转换后的JSON文件（不含_info后缀）
        json_files = [f for f in os.listdir(dir_path) 
                     if f.endswith('.json') and not f.endswith('_info.json')]
        mp4_files = [f for f in os.listdir(dir_path) if f.endswith('.mp4')]
        
        if json_files and mp4_files:
            # 优先选择转换后的JSON文件（不含_info后缀）
            # 如果有多个JSON文件，选择第一个非_info的
            json_path = os.path.join(dir_path, json_files[0])
            video_path = os.path.join(dir_path, mp4_files[0])
            json_video_file_pairs.append((json_path, video_path))
    
    return json_video_file_pairs

    

def main_refactored(data_dir: str, 
                    overwrite_action_items: bool = False, 
                    save_all_extracted_frames: bool = False, 
                    generate_ssim_sequence: bool = True, 
                    save_frames_as_video: bool = False,
                    get_json_video_pairs_func_name:str="v1",
                    custom_detailed_output_dir: str | None = None,
                    target_gpu_id: int | None = None):
    """
    重构的主函数，用于处理标注数据并生成模型训练所需的数据集。
    
    Args:
        data_dir: 包含JSON和视频文件的根目录。
        overwrite_action_items: 是否覆盖已存在的action_items处理结果。
        save_all_extracted_frames: 是否将提取的所有帧保存为NumPy数组。
        generate_ssim_sequence: 是否计算和生成SSIM相似度序列。
        save_frames_as_video: 是否将提取的帧保存为视频
        get_json_video_pairs_func_name: 获取json和视频路径的函数名
        custom_detailed_output_dir: 用户自定义的详细输出根目录路径。
        target_gpu_id: 指定GPU ID，传递给SSIM GPU计算函数
    """
    # data_dir = "all_marked_data" # 从参数获取，不再硬编码
    data_dir_basename = os.path.basename(data_dir.rstrip('/\\')) # 正确的路径处理

    if custom_detailed_output_dir:
        detailed_output_dir = custom_detailed_output_dir
    else:
        detailed_output_dir = f"{data_dir_basename}_processed_action_items"
    
    if os.path.exists(detailed_output_dir):
        print(f"细粒度输出目录 {detailed_output_dir} 已存在。如果您希望清空，请手动删除或取消下面shutil.rmtree的注释。")
        # print(f"正在清空已存在的细粒度输出目录: {detailed_output_dir}")
        # shutil.rmtree(detailed_output_dir) 
    os.makedirs(detailed_output_dir, exist_ok=True)

    offsets = [1 ,10, 30, 60, 90,150] 
    # offsets = [1] 
    target_fps = 30

    get_json_video_pairs_func = {
        "v1": get_json_video_path_pairs_v1,
        "v2": get_json_video_path_pairs_v2
    }
    json_video_file_pairs = get_json_video_pairs_func[get_json_video_pairs_func_name](data_dir)
    if not json_video_file_pairs:
        print("未找到任何 JSON-视频 对进行处理。")
        return

    all_model_samples = []
    global_uid_counter = 0 

    for json_path, video_path in json_video_file_pairs:
        sequences_from_single_json = process_single_json_video_pair(
            json_path, 
            video_path, 
            detailed_output_dir, 
            offsets, 
            target_fps=target_fps,
            overwrite_existing_action_items=overwrite_action_items,
            save_all_extracted_frames=save_all_extracted_frames,
            generate_ssim_sequence=generate_ssim_sequence,
            save_frames_as_video=save_frames_as_video,
            target_gpu_id=target_gpu_id
        )

        if sequences_from_single_json:
            raw_data_for_conversion = [{
                'video_path': video_path, 
                'seq_raw_data': sequences_from_single_json 
            }]
            
            model_dataset_for_this_json = convert_to_model_dataset(
                raw_data_for_conversion, 
                offsets, 
                fps=target_fps
            )
            
            for sample_idx, sample in enumerate(model_dataset_for_this_json):
                # 使用更稳定的ID，例如基于json文件名和序列索引
                base_json_name = os.path.splitext(os.path.basename(json_path))[0]
                sample['id'] = f"{base_json_name}_seq{global_uid_counter}" # 使用全局计数器保证唯一性
                all_model_samples.append(sample)
                global_uid_counter += 1
            
            print(f"JSON {os.path.basename(json_path)} 处理完毕，转换得到 {len(model_dataset_for_this_json)} 个模型样本。累计总样本: {len(all_model_samples)}")
        else:
            print(f"JSON文件 {os.path.basename(json_path)} 未生成任何有效序列数据用于模型转换。")
        
        gc.collect()

    print(f"\n所有JSON文件处理完毕。总共生成 {len(all_model_samples)} 个模型训练样本。")

    if not all_model_samples:
        print("没有生成任何模型样本，无法继续。")
        return

    shuffle(all_model_samples)
    split_idx = int(len(all_model_samples) * 0.9)
    train_set = all_model_samples[:split_idx]
    test_set = all_model_samples[split_idx:]

    if not train_set and not test_set and all_model_samples: # 理论上如果all_model_samples有数据，这里不会都为空
         print("警告：有模型样本但训练集和测试集均为空，检查分割逻辑。")
    elif not train_set and not test_set and not all_model_samples:
        print("训练集和测试集均为空，因为没有生成样本。")
        return
    
    # 动态生成文件名，基于关键参数
    param_str = f"fps{target_fps}_offsets{len(offsets)}"
    if generate_ssim_sequence:
        param_str += "_ssim"
    
    current_date = time.strftime("%Y%m%d")
    # 此处直接使用上面已经定义的 data_dir_basename
    output_train_file = f"{data_dir_basename}_train_data_{param_str}_{current_date}.pt"
    output_test_file = f"{data_dir_basename}_test_data_{param_str}_{current_date}.pt"
    
    torch.save(train_set, output_train_file)
    torch.save(test_set, output_test_file)
    print(f"重构后的训练集已保存到 {output_train_file}，样本数: {len(train_set)}")
    print(f"重构后的测试集已保存到 {output_test_file}，样本数: {len(test_set)}")

    if train_set:
         print("\n部分训练样本示例:")
         for i, item in enumerate(train_set[:2]):
            print(f"  样本 {item['id']}: ssim_features.shape={item['ssim_features'].shape}, op_type={item['op_type'].item()}, op_frame_flag.sum={item['op_frame_flag'].sum().item()}, labels分布={torch.bincount(item['labels'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理视频标注数据并生成模型训练集。")
    parser.add_argument("--data_dir", type=str, default="all_marked_data", help="包含JSON和视频文件的根目录。")
    parser.add_argument("--overwrite_action_items", type=bool, default=False, help="是否覆盖已存在的处理结果。")
    parser.add_argument("--save_all_extracted_frames", type=bool, default=True, help="是否将提取的帧保存为NumPy数组。")
    parser.add_argument("--generate_ssim_sequence", type=bool, default=True, help="是否计算SSIM相似度序列。")
    parser.add_argument("--save_frames_as_video", type=bool, default=True, help="是否将提取的帧保存为视频。")
    parser.add_argument("--get_json_video_pairs_func_name", type=str, default="v2", choices=["v1", "v2"], help="获取json和视频路径对的函数版本。")
    parser.add_argument("--detailed_output_dir", type=str, default=None, help="自定义详细输出的根目录路径。如果未指定，将基于data_dir名称在当前目录创建。")
    parser.add_argument("--gpu_id", type=int, default=None, help="指定使用的GPU ID (例如 0, 1, ...)。如果未指定，则由PyTorch自动选择或基于device_str参数。")

    args = parser.parse_args()

    main_refactored(
        data_dir=args.data_dir,
        overwrite_action_items=args.overwrite_action_items,
        save_all_extracted_frames=args.save_all_extracted_frames,
        generate_ssim_sequence=args.generate_ssim_sequence,
        save_frames_as_video=args.save_frames_as_video,
        get_json_video_pairs_func_name=args.get_json_video_pairs_func_name,
        custom_detailed_output_dir=args.detailed_output_dir,
        target_gpu_id=args.gpu_id
    )