import os
import json
import requests
import time # Added time import for retries
from tqdm import tqdm # Added tqdm import
from concurrent.futures import ThreadPoolExecutor, as_completed

# output_dir is defined in if __name__ == "__main__" block,
# will be passed as an argument to main.

def download_video(storage_path, target_path, task_info_str="Unknown task", max_retries=3, initial_retry_delay=5):
    """
    Downloads a video file from a URL (storage_path) to target_path with retries.
    Skips if the target file already exists.
    Assumes storage_path is always a URL.
    """
    # Common pre-check: if target already exists, skip.
    if os.path.exists(target_path):
        print(f"视频已存在: {target_path} (任务: {task_info_str})，跳过下载。")
        return storage_path, target_path, "skipped_exists"

    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)

    last_exception = None

    for attempt in range(max_retries):
        try:
            print(f"开始从 URL 下载 (尝试 {attempt + 1}/{max_retries}): {storage_path} -> {target_path} (任务: {task_info_str})")
            response = requests.get(storage_path, stream=True, timeout=300) 
            response.raise_for_status()  
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: 
                        f.write(chunk)
            print(f"URL 下载成功: {target_path} (任务: {task_info_str})")
            return storage_path, target_path, "success"

        except requests.exceptions.RequestException as e_req:
            last_exception = e_req
            print(f"URL 下载尝试 {attempt + 1} 失败 (任务: {task_info_str}). 网络错误: {e_req}")
            # If it's the last attempt, don't sleep, just fall through to error return
            if attempt < max_retries - 1:
                retry_delay = initial_retry_delay * (2 ** attempt) # Exponential backoff
                print(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print(f"所有 {max_retries} 次下载尝试均失败 (任务: {task_info_str}).")
        except Exception as e_general: # Catch other potential errors during file writing etc.
            last_exception = e_general
            print(f"下载或写入文件尝试 {attempt + 1} 发生一般错误 (任务: {task_info_str}). 错误: {e_general}")
            # If it's the last attempt, don't sleep
            if attempt < max_retries - 1:
                retry_delay = initial_retry_delay * (2 ** attempt)
                print(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print(f"所有 {max_retries} 次下载/写入尝试均失败 (任务: {task_info_str}).")
    
    # If all retries failed, handle cleanup and return error status
    error_type = "error_network" if isinstance(last_exception, requests.exceptions.RequestException) else "error_general"
    error_message = str(last_exception) if last_exception else "Unknown error after retries"
    print(f"最终下载失败: {storage_path} -> {target_path} (任务: {task_info_str}). 错误: {error_message}")
    
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
            print(f"已删除部分下载的文件 (重试全部失败后): {target_path}")
        except OSError as e_del:
            print(f"删除部分下载的文件失败 (重试全部失败后) {target_path}: {e_del}")
            
    return storage_path, target_path, f"{error_type}: {error_message}"

def main(target_json_file, output_dir_base):
    futures = []
    max_workers = os.cpu_count() or 4  # Use CPU count or default to 4 workers
    print(f"使用 {max_workers} 个线程进行下载...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with open(target_json_file, "r") as f:
            data = json.load(f)
            for item_idx, item in enumerate(data):
                task_info = item.get("task_info", [f"item_idx_{item_idx}"]) # Provide default if missing
                item_dir_name = "-".join(map(str, task_info)) # Ensure all parts are strings
                # note = item.get("note")
                # if note is not None:
                #     print(f"任务 '{item_dir_name}' 包含备注，跳过处理。")
                #     continue
                
                video_action_data = item.get("video_action_data")
                if not video_action_data:
                    print(f"任务 '{item_dir_name}' 缺少 'video_action_data'，跳过。")
                    continue
                    
                storage_path = video_action_data.get("storage_path")
                if not storage_path:
                    print(f"任务 '{item_dir_name}' 缺少 'storage_path' (URL)，跳过视频下载。")
                    # Still save JSON if other info is present, but don't submit download task
                
                item_target_path_base = os.path.join(output_dir_base, item_dir_name)
                if not os.path.exists(item_target_path_base):
                    try:
                        os.makedirs(item_target_path_base)
                        print(f"为任务 '{item_dir_name}' 创建目录: {item_target_path_base}")
                    except OSError as e:
                        print(f"创建目录失败 {item_target_path_base} (任务: {item_dir_name}). 错误: {e} 跳过此任务。")
                        continue
                
                json_data_path = os.path.join(item_target_path_base, "info.json")
                try:
                    with open(json_data_path, "w") as f_json:
                        json.dump(item, f_json, ensure_ascii=False, indent=4)
                    # print(f"JSON信息已保存到: {json_data_path} (任务: {item_dir_name})") # Reduced verbosity for cleaner progress
                except Exception as e_json:
                    print(f"保存JSON失败 {json_data_path} (任务: {item_dir_name}). 错误: {e_json}")

                if storage_path: 
                    target_video_path = os.path.join(item_target_path_base, "video.mp4")
                    futures.append(executor.submit(download_video, storage_path, target_video_path, item_dir_name))
                # else: # Already handled above
                    # print(f"任务 '{item_dir_name}' 无视频路径，不执行下载。")

            if not futures:
                print("没有需要下载的视频任务。")
                return # Exit early if no futures
                
            print(f"\n所有 {len(futures)} 个下载任务已提交。开始处理...")
            # Wrap as_completed with tqdm for progress bar
            for future in tqdm(as_completed(futures), total=len(futures), desc="视频下载进度"):
                src, dst, status = future.result()
                # Optional: Log detailed status for each completed task if needed, 
                # but tqdm handles the overall progress display.
                if status != "success" and status != "skipped_exists":
                     # Error messages are already printed within download_video, 
                     # so we might not need to print them again here unless for specific summary.
                     # For now, rely on download_video for detailed error prints.
                     pass # print(f"任务 {src} -> {dst} 状态: {status}")
                 
    print("\n所有任务处理完毕。")
    
def change_json_file_and_video_name(dir_path):
    dir_list = os.listdir(dir_path)
    for dir_name in dir_list:
        sub_dir_path = os.path.join(dir_path, dir_name)
        print(sub_dir_path)
        if os.path.isdir(sub_dir_path):
            json_path = os.path.join(sub_dir_path, "info.json")
            video_path = os.path.join(sub_dir_path, "video.mp4")
            
            # 检查文件是否存在，存在才重命名
            if os.path.exists(json_path):
                os.rename(json_path, os.path.join(sub_dir_path, dir_name + ".json"))
            else:
                print(f"警告：文件不存在 {json_path}")
                
            if os.path.exists(video_path):
                os.rename(video_path, os.path.join(sub_dir_path, dir_name + ".mp4"))
            else:
                print(f"警告：文件不存在 {video_path}")

if __name__ == "__main__":
    target_json_file = "data/marked_data_300_page_process_1.json"
    output_dir = "all_marked_data"
    # main(target_json_file, output_dir)
    change_json_file_and_video_name(output_dir)