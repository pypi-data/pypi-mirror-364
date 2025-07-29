import os
import json
import torch
import numpy as np
from pathlib import Path

# 尝试从 find_page_load_intelligent.py 导入所需函数
# 假设 evaluate_load_time_accuracy.py 与 find_page_load_intelligent.py 在同一目录下，
# 或者 find_page_load_intelligent.py 在Python的搜索路径中。
try:
    from ..algorithms.find_page_load_intelligent import preprocess_ssim_data, find_page_load_intelligent, find_page_load_simple_ssim_threshold
except ImportError as e:
    print(f"错误：无法从 'find_page_load_intelligent.py' 导入一个或多个所需函数: {e}")
    print("请确保两个脚本在同一目录下，或者 find_page_load_intelligent.py 在 PYTHONPATH 中，")
    print("并且 find_page_load_simple_ssim_threshold 函数已在该文件中定义。")
    exit()

def _classify_and_append_result(
    result_entry: dict, 
    gt_start_frame: int, 
    gt_end_frame: int, 
    pred_start_frame: int, 
    pred_end_frame: int,
    perfect_matches_list: list, 
    close_matches_list: list, 
    mid_matches_list: list,
    other_cases_list: list
):
    """Helper function to classify and append results based on prediction accuracy."""
    if pred_start_frame == -1 and pred_end_frame == -1: # Algorithm did not detect
        result_entry["diff_start"] = None
        result_entry["diff_end"] = None
        other_cases_list.append(result_entry)
        print(f"    算法未检测到加载过程。真实起止: ({gt_start_frame}, {gt_end_frame})")
        return "no_detection"

    diff_start = abs(pred_start_frame - gt_start_frame)
    diff_end = abs(pred_end_frame - gt_end_frame)
    result_entry["diff_start"] = diff_start
    result_entry["diff_end"] = diff_end

    print(f"    真实起止: ({gt_start_frame}, {gt_end_frame}), 预测起止: ({pred_start_frame}, {pred_end_frame}), 差异: ({diff_start}, {diff_end})")

    if diff_start == 0 and diff_end == 0:
        perfect_matches_list.append(result_entry)
        print("    分类: 精确匹配")
        return "perfect"
    elif diff_end < 10:
        close_matches_list.append(result_entry)
        print("    分类: 接近匹配 (结束帧差异 < 10)")
        return "close"
    elif 10 <= diff_end < 20:
        mid_matches_list.append(result_entry)
        print("    分类: 10≤结束帧差异<20")
        return "mid"
    else:
        other_cases_list.append(result_entry)
        print("    分类: 其他情况")
        return "other"

def calculate_accuracy(dataset_root_path: str):
    """
    评估页面加载时间识别算法在指定数据集上的准确率。

    Args:
        dataset_root_path: 数据集的根目录路径 (例如 "processed_action_items/")
    """
    # Results for the 'intelligent' algorithm
    perfect_matches_intelligent = []
    close_matches_intelligent = []
    mid_matches_intelligent = []
    other_cases_intelligent = []

    # Results for the 'simple_ssim_threshold' algorithm
    perfect_matches_simple = []
    close_matches_simple = []
    mid_matches_simple = []
    other_cases_simple = []
    
    error_log = []

    root_path = Path(dataset_root_path)

    # 遍历一级子目录 (视频ID)
    for video_id_path in root_path.iterdir():
        if not video_id_path.is_dir():
            continue
        
        video_id = video_id_path.name
        print(f"\n正在处理视频ID: {video_id}")

        # 遍历二级子目录 (视频片段ID)
        for segment_id_path in video_id_path.iterdir():
            if not segment_id_path.is_dir():
                continue
            
            segment_id = segment_id_path.name
            print(f"  正在处理视频片段: {segment_id}")
            
            # 初始化当前片段的错误标记
            current_segment_error = False

            try:
                # 1. 加载 action_info.json
                action_info_path = segment_id_path / "action_info.json"
                if not action_info_path.exists():
                    raise FileNotFoundError(f"action_info.json not found in {segment_id_path}")
                
                with open(action_info_path, "r", encoding="utf-8") as f:
                    action_info = json.load(f)

                # 提取所需信息
                marked_response_time = action_info["original_action_item"]["marked_response_time"]
                marked_end_time = action_info["original_action_item"]["marked_end_time"]
                extract_start_time_sec = action_info["extraction_parameters"]["extract_start_time_sec"]
                fps = action_info["extraction_parameters"]["fps"]

                # 2. 计算真实的开始帧和结束帧 (相对于视频片段)
                gt_start_frame = round((marked_response_time - extract_start_time_sec) * fps)
                gt_end_frame = round((marked_end_time - extract_start_time_sec) * fps)
                
                gt_start_frame = max(0, gt_start_frame)
                gt_end_frame = max(0, gt_end_frame)

                # 3. 加载 ssim_sequence.pt
                ssim_pt_path = segment_id_path / "ssim_sequence.pt"
                if not ssim_pt_path.exists():
                    raise FileNotFoundError(f"ssim_sequence.pt not found in {segment_id_path}")
                
                raw_ssim_data_tensor = torch.load(ssim_pt_path)
                raw_ssim_data_list = raw_ssim_data_tensor.tolist()

                # 4. 预处理SSIM数据
                cleaned_ssim_data = preprocess_ssim_data(raw_ssim_data_list)
                
                if not cleaned_ssim_data:
                    # 如果预处理后数据为空，两个算法都无法运行
                    raise ValueError("预处理后的SSIM数据为空，跳过此片段")

                # ---评估算法1: find_page_load_intelligent ---
                print("    评估算法: find_page_load_intelligent")
                try:
                    pred_start_intelligent, pred_end_intelligent = find_page_load_intelligent(
                        ssim_sequence=cleaned_ssim_data,
                        fps=fps,
                        plot_results=False
                    )
                    result_entry_intelligent = {
                        "video_id": video_id, "segment_id": segment_id,
                        "gt_start_frame": gt_start_frame, "gt_end_frame": gt_end_frame,
                        "pred_start_frame": pred_start_intelligent, "pred_end_frame": pred_end_intelligent,
                        "algorithm": "intelligent",
                        "action_info_path": str(action_info_path.relative_to(root_path)),
                        "ssim_pt_path": str(ssim_pt_path.relative_to(root_path))
                    }
                    _classify_and_append_result(
                        result_entry_intelligent, gt_start_frame, gt_end_frame,
                        pred_start_intelligent, pred_end_intelligent,
                        perfect_matches_intelligent, close_matches_intelligent, mid_matches_intelligent, other_cases_intelligent
                    )
                except Exception as e_alg1:
                    print(f"    错误 (find_page_load_intelligent 执行失败): {e_alg1}")
                    error_log.append({
                        "video_id": video_id, "segment_id": segment_id, 
                        "algorithm": "intelligent", "error_type": type(e_alg1).__name__, "message": str(e_alg1)
                    })
                    # 即使一个算法失败，也尝试另一个

                # ---评估算法2: find_page_load_simple_ssim_threshold ---
                print("    评估算法: find_page_load_simple_ssim_threshold")
                try:
                    # 注意：此算法可能需要不同的参数或预处理，此处假设它使用与intelligent相同的cleaned_ssim_data
                    # 并且其默认参数是合适的。如果它也需要fps，需要传递
                    # 根据 find_page_load_simple_ssim_threshold 的定义，它不需要fps
                    pred_start_simple, pred_end_simple = find_page_load_simple_ssim_threshold(
                        ssim_sequence=cleaned_ssim_data,
                        # smooth_window=3, # 使用默认值
                        # ssim_drop_threshold=0.95, # 使用默认值
                        plot_results=False
                    )
                    result_entry_simple = {
                        "video_id": video_id, "segment_id": segment_id,
                        "gt_start_frame": gt_start_frame, "gt_end_frame": gt_end_frame,
                        "pred_start_frame": pred_start_simple, "pred_end_frame": pred_end_simple,
                        "algorithm": "simple_ssim_threshold",
                        "action_info_path": str(action_info_path.relative_to(root_path)),
                        "ssim_pt_path": str(ssim_pt_path.relative_to(root_path))
                    }
                    _classify_and_append_result(
                        result_entry_simple, gt_start_frame, gt_end_frame,
                        pred_start_simple, pred_end_simple,
                        perfect_matches_simple, close_matches_simple, mid_matches_simple, other_cases_simple
                    )
                except Exception as e_alg2:
                    print(f"    错误 (find_page_load_simple_ssim_threshold 执行失败): {e_alg2}")
                    error_log.append({
                        "video_id": video_id, "segment_id": segment_id,
                        "algorithm": "simple_ssim_threshold", "error_type": type(e_alg2).__name__, "message": str(e_alg2)
                    })

            except FileNotFoundError as e_file:
                print(f"    错误 (文件预处理阶段 - 文件未找到): {e_file}")
                error_log.append({"video_id": video_id, "segment_id": segment_id, "error_type": "FileNotFoundError", "message": str(e_file), "stage": "preprocessing"})
                current_segment_error = True
            except json.JSONDecodeError as e_json:
                print(f"    错误 (文件预处理阶段 - JSON解析错误): {e_json} in file {action_info_path}")
                error_log.append({"video_id": video_id, "segment_id": segment_id, "file": str(action_info_path.relative_to(root_path)), "error_type": "JSONDecodeError", "message": str(e_json), "stage": "preprocessing"})
                current_segment_error = True
            except KeyError as e_key:
                print(f"    错误 (文件预处理阶段 - JSON中缺少键): {e_key} in file {action_info_path}")
                error_log.append({"video_id": video_id, "segment_id": segment_id, "file": str(action_info_path.relative_to(root_path)), "error_type": "KeyError", "message": f"Missing key: {str(e_key)}", "stage": "preprocessing"})
                current_segment_error = True
            except ValueError as e_val: # 包括 cleaned_ssim_data 为空的情况
                print(f"    错误 (文件预处理阶段 - 值错误或SSIM数据预处理失败): {e_val}")
                error_log.append({"video_id": video_id, "segment_id": segment_id, "error_type": "ValueError", "message": str(e_val), "stage": "preprocessing"})
                current_segment_error = True
            except Exception as e_gen: # 捕获预处理阶段的其他未知错误
                print(f"    文件预处理阶段发生未知错误: {e_gen}")
                error_log.append({
                    "video_id": video_id, "segment_id": segment_id, 
                    "error_type": type(e_gen).__name__, "message": str(e_gen), "stage": "preprocessing"
                })
                current_segment_error = True
            
            if current_segment_error:
                print(f"    由于预处理错误，跳过对片段 {segment_id} 的算法评估。")
                continue # 跳到下一个segment_id

    # 保存结果
    output_dir = Path("evaluation_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存 'intelligent' 算法结果
    with open(output_dir / "perfect_matches_intelligent.json", "w", encoding="utf-8") as f:
        json.dump(perfect_matches_intelligent, f, indent=4, ensure_ascii=False)
    with open(output_dir / "close_matches_intelligent.json", "w", encoding="utf-8") as f:
        json.dump(close_matches_intelligent, f, indent=4, ensure_ascii=False)
    with open(output_dir / "mid_matches_intelligent.json", "w", encoding="utf-8") as f:
        json.dump(mid_matches_intelligent, f, indent=4, ensure_ascii=False)
    with open(output_dir / "other_cases_intelligent.json", "w", encoding="utf-8") as f:
        json.dump(other_cases_intelligent, f, indent=4, ensure_ascii=False)

    # 保存 'simple_ssim_threshold' 算法结果
    with open(output_dir / "perfect_matches_simple.json", "w", encoding="utf-8") as f:
        json.dump(perfect_matches_simple, f, indent=4, ensure_ascii=False)
    with open(output_dir / "close_matches_simple.json", "w", encoding="utf-8") as f:
        json.dump(close_matches_simple, f, indent=4, ensure_ascii=False)
    with open(output_dir / "mid_matches_simple.json", "w", encoding="utf-8") as f:
        json.dump(mid_matches_simple, f, indent=4, ensure_ascii=False)
    with open(output_dir / "other_cases_simple.json", "w", encoding="utf-8") as f:
        json.dump(other_cases_simple, f, indent=4, ensure_ascii=False)
    
    with open(output_dir / "error_log.json", "w", encoding="utf-8") as f:
        json.dump(error_log, f, indent=4, ensure_ascii=False)

    print("\n--- 评估结果统计 ---")
    
    def print_algorithm_stats(algo_name, perfect_list, close_list, mid_list, other_list):
        total_processed = len(perfect_list) + len(close_list) + len(mid_list) + len(other_list)
        print(f"\n算法: {algo_name}")
        if total_processed > 0:
            print(f"  总共成功处理视频片段数 (此算法): {total_processed}")
            print(f"    - 精确匹配: {len(perfect_list)} ({(len(perfect_list)/total_processed)*100:.2f}%)")
            print(f"    - 接近匹配 (结束帧差异 < 10): {len(close_list)} ({(len(close_list)/total_processed)*100:.2f}%)")
            print(f"    - 10≤结束帧差异<20: {len(mid_list)} ({(len(mid_list)/total_processed)*100:.2f}%)")
            print(f"    - 其他情况: {len(other_list)} ({(len(other_list)/total_processed)*100:.2f}%)")
            # (精确 + 接近 + mid) / 总数
            overall_accuracy_flexible = (len(perfect_list) + len(close_list) + len(mid_list)) / total_processed * 100
            print(f"    - 综合准确率 (精确+接近+10~20): {overall_accuracy_flexible:.2f}%")
        else:
            print("  没有成功处理任何视频片段 (此算法)。")

    print_algorithm_stats("find_page_load_intelligent", perfect_matches_intelligent, close_matches_intelligent, mid_matches_intelligent, other_cases_intelligent)
    print_algorithm_stats("find_page_load_simple_ssim_threshold", perfect_matches_simple, close_matches_simple, mid_matches_simple, other_cases_simple)

    print(f"\n处理过程中记录的错误总数: {len(error_log)}")
    print(f"结果已保存到 '{output_dir.resolve()}' 目录下。")

if __name__ == '__main__':
    # 注意：请将此路径替换为您的实际数据集路径
    # dataset_path = "processed_action_items/" # 示例路径
    dataset_path = "downloaded_videos_processed" # 使用用户提供的绝对路径
    
    # 确保路径存在
    if not Path(dataset_path).exists():
        print(f"错误：数据集路径 '{dataset_path}' 不存在。请检查路径。")
    else:
        print(f"开始评估数据集: {dataset_path}")
        calculate_accuracy(dataset_path)
        print("\n评估完成。")
