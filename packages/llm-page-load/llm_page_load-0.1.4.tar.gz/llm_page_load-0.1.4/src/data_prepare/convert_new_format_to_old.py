import os
import json
import argparse
from typing import Dict, List, Any


def convert_new_format_to_old(new_json_path: str, video_path: str) -> str:
    """
    将新格式的JSON转换为旧格式，以便兼容gen_seq_emb_for_tf_model.py
    
    Args:
        new_json_path: 新格式JSON文件路径
        video_path: 对应的视频文件路径
        
    Returns:
        转换后的JSON文件路径
    """
    
    # 读取新格式JSON
    with open(new_json_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    # 获取视频文件名（不含扩展名）作为场景名
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    
    # 构建旧格式的action_list
    action_list = []
    
    for idx, frame_data in enumerate(new_data.get('labeledFrameDataList', [])):
        # 将毫秒转换为秒
        start_time_sec = frame_data.get('startFrameTime', 0) / 1000.0
        end_time_sec = frame_data.get('endFrameTime', 0) / 1000.0
        
        # 计算时间差
        time_diff = end_time_sec - start_time_sec if end_time_sec > start_time_sec else 0
        
        # 构建action_item
        action_item = {
            "timestamp": "",  # 新格式中没有这个信息
            "action_time": f"{int(start_time_sec // 60):02d}:{start_time_sec % 60:05.2f}",
            #"action_desc": f"标注事件 {idx + 1} - {frame_data.get('type', '未知类型')}",
            "action_desc": "",
            "marked_response_time": f"{int(start_time_sec // 60):02d}:{start_time_sec % 60:05.2f}",
            "marked_end_time": f"{int(end_time_sec // 60):02d}:{end_time_sec % 60:05.2f}",
            "marked_loading_event": [
                {
                    "loading_start_time": f"{int(start_time_sec // 60):02d}:{start_time_sec % 60:05.2f}",
                    "loading_end_time": f"{int(end_time_sec // 60):02d}:{end_time_sec % 60:05.2f}"
                }
            ],
            "note": f"从新格式转换 - 类型: {frame_data.get('type', '未知')}",
            "page_name": f"视频{video_basename}",
            "time_diff": time_diff
        }
        
        action_list.append(action_item)
    
    # 构建旧格式的完整JSON结构
    old_format_data = {
        "task_id": new_data.get('videoId', 0),
        "task_info": [
            "",
            str(new_data.get('videoId', '')),
            video_basename
        ],
        "case_name": video_basename,
        "video_action_data": {
            "autotest_info": {
                "case_name": video_basename,
                "ffmpeg_process": False,
                "job_id": new_data.get('videoId', 0),
                "job_type": "VideoAnalysis",
                "network_profile_id": "",
                "scene_name": f"视频分析 - {video_basename}",
                "scrcpy_time_limit": "600",
                "sn": str(new_data.get('videoId', '')),
                "task_id": str(new_data.get('videoId', ''))
            },
            "storage_path": video_path,
            "action_list": action_list
        },
        "note": "从新格式转换",
        "lag_num": 0,
        "data_time_diff_sum": sum(item.get('time_diff', 0) for item in action_list),
        "data_time_diff_num": len([item for item in action_list if item.get('time_diff', 0) > 0]),
        "data_time_diff_avg": sum(item.get('time_diff', 0) for item in action_list) / max(len(action_list), 1),
        "case_loading_time_list": [item.get('time_diff', 0) for item in action_list if item.get('time_diff', 0) > 0]
    }
    
    # 保存转换后的JSON文件到视频所在目录
    video_dir = os.path.dirname(video_path)
    output_json_path = os.path.join(video_dir, f"{video_basename}.json")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(old_format_data, f, indent=4, ensure_ascii=False)
    
    print(f"转换完成: {new_json_path} -> {output_json_path}")
    print(f"  视频文件: {video_path}")
    print(f"  转换了 {len(action_list)} 个action items")
    
    return output_json_path


def process_downloaded_videos_folder(downloaded_videos_dir: str) -> List[str]:
    """
    处理整个downloaded_videos文件夹，转换所有视频的JSON格式
    转换后的JSON文件将保存在对应的视频目录下
    
    Args:
        downloaded_videos_dir: downloaded_videos文件夹路径
        
    Returns:
        转换后的JSON文件路径列表
    """
    converted_files = []
    
    # 遍历所有视频文件夹
    for video_folder in os.listdir(downloaded_videos_dir):
        video_folder_path = os.path.join(downloaded_videos_dir, video_folder)
        
        if not os.path.isdir(video_folder_path):
            continue
            
        # 查找JSON和MP4文件
        json_files = [f for f in os.listdir(video_folder_path) if f.endswith('_info.json')]
        mp4_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]
        
        if not json_files or not mp4_files:
            print(f"警告: {video_folder} 中缺少JSON或MP4文件，跳过")
            continue
            
        # 使用第一个找到的文件（通常只有一个）
        json_file = json_files[0]
        mp4_file = mp4_files[0]
        
        json_path = os.path.join(video_folder_path, json_file)
        mp4_path = os.path.join(video_folder_path, mp4_file)
        
        try:
            converted_json_path = convert_new_format_to_old(json_path, mp4_path)
            converted_files.append(converted_json_path)
        except Exception as e:
            print(f"错误: 转换 {video_folder} 失败: {e}")
    
    return converted_files


def main():
    parser = argparse.ArgumentParser(description="将downloaded_videos的新格式JSON转换为旧格式")
    parser.add_argument("--downloaded_videos_dir", type=str, default="downloaded_videos", 
                       help="downloaded_videos文件夹路径")
    
    args = parser.parse_args()
    
    print(f"开始转换 {args.downloaded_videos_dir} 中的视频数据...")
    print("转换后的JSON文件将保存在对应的视频目录下")
    
    # 处理所有视频
    converted_files = process_downloaded_videos_folder(args.downloaded_videos_dir)
    
    print(f"\n转换完成！共转换了 {len(converted_files)} 个文件")
    print("转换后的JSON文件已保存在对应的视频目录下")
    print("\n现在可以使用以下命令运行gen_seq_emb_for_tf_model.py:")
    print(f"python src/data_prepare/gen_seq_emb_for_tf_model.py --data_dir {args.downloaded_videos_dir} --get_json_video_pairs_func_name v2")


if __name__ == "__main__":
    main() 