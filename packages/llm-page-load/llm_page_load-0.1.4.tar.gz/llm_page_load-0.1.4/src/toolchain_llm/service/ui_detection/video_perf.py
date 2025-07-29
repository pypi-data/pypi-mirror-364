import json

import cv2
import copy
from service.ui_detection.horus_ocr import ClientHorus
from service.ui_detection.hash_similar import HashSimilar
from service.ui_detection.image_utils import image_preprocess, clear_temp
from tools.s3 import MssHHelper
from service.GPT import gpt_v, llmcore_completion
from service.ui_detection.image_utils import draw_contours
import time
import os
import requests
import numpy as np
import gc


def filtered_similar(img1, img2, ignore_list=[]):
    hash_similar = HashSimilar()
    h, w, _ = img1.shape
    img_1 = copy.deepcopy(img1)
    img_2 = copy.deepcopy(img2)
    for rect in ignore_list:
        x1, y1, x2, y2 = rect
        x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
        img_1[y1:y2, x1:x2] = img_2[y1:y2, x1:x2]
    score = hash_similar.get_similar_score(img_1, img_2, offset_y_percent=0.2)
    return score


def remove_close_numbers(numbers, frames_count):
    result = []
    for i in range(len(numbers)):
        if not result or abs(numbers[i] - result[-1]) >= frames_count:
            result.append(numbers[i])
    return result


def cut_video_to_frames(video_path, time_points=None, cut=0.0):
    """
    按指定时间点将视频分割成帧列表，如果 time_points 为空，则返回整段视频的所有帧
    :param video_path: 输入视频的路径
    :param time_points: 时间点列表，单位为秒，例如 [10, 20]。如果为空，则返回整段视频
    :return: 一个包含多个帧列表的列表，每个子列表对应一个视频片段的帧
    """
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        return []

    # 获取视频的帧率和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames / fps  # 视频总时长（秒）
    total_duration = total_duration - cut
    # 处理 time_points
    if time_points is None or len(time_points) == 0:
        time_points = [0, total_duration]  # 只有一个片段，覆盖整个视频
    else:
        time_points = sorted(time_points)
        if time_points[0] != 0:
            time_points.insert(0, 0)  # 添加起始时间点
        total_duration = min(total_duration, time_points[-1] + 15)
        time_points.append(total_duration)  # 添加视频总时长作为最后一个时间点
    # 初始化结果列表
    segments = []
    # 遍历时间点，分割视频
    for i in range(len(time_points) - 1):
        start_time = time_points[i]
        end_time = time_points[i + 1]
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        # 跳到起始帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        # 初始化当前片段的帧列表
        segment_frames = []
        # 读取帧
        cap_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_frame > end_frame:
                break
            segment_frames.append(frame)
            cap_count = cap_count + 1
            if cap_count % 20 == 0:
                del frame
                gc.collect()
        # 将当前片段的帧列表添加到结果中
        segments.append(segment_frames)

    cap.release()
    del cap
    return fps, segments


def video_preprocess(video_url, action_list, cut=0.0):
    action_info_list = []
    video_path, video_name = image_preprocess(video_url)
    image_name = video_name.replace('.mp4', '.png')
    action_time_list = []
    if len(action_list) == 0:
        return []
    for i in range(0, len(action_list)):
        action_info = {}
        action_time = action_list[i]['action_time']
        if i > 0:
            offset_t = 0.5
            action_info['action_time'] = offset_t
            action_time_list.append(action_time - offset_t)
            action_info['offset_time'] = action_time - offset_t
        else:
            action_info['action_time'] = action_time
            action_info['offset_time'] = 0.0
        action_info['action_desc'] = action_list[i]['action_desc']
        action_info['image_name'] = image_name.replace('.png', f'_{i}.png')
        action_info_list.append(action_info)
    fps, frames = cut_video_to_frames(video_path, time_points=action_time_list, cut=cut)
    for i in range(0, len(action_info_list)):
        action_info_list[i]['frames'] = frames[i]
    return fps, action_info_list


def find_response_index(frames, action_index, end_index):
    """找到页面首次响应的帧索引"""
    response_index = action_index + 1
    for i in range(action_index, end_index - 1):
        score = filtered_similar(frames[i], frames[i + 1])
        if score < 0.9:
            response_index = i
            break
    return response_index


def calculate_frame_scores(frames, start_index, end_index):
    """计算帧之间的相似度分数"""
    score_list = []
    for i in range(start_index, end_index - 1):
        score = filtered_similar(frames[i], frames[i + 1])
        score_list.append(score)
    return score_list


def detect_jank_frames(score_list, frames_per_100ms, response_index, action_index):
    """检测卡顿帧"""
    jank_frames = []
    for i in range(response_index - action_index, len(score_list)):
        if i + frames_per_100ms < len(score_list) and \
                any(score_frame < 0.999 for score_frame in score_list[i + frames_per_100ms:i + frames_per_100ms+1]):
            if all(x == 1.0 for x in score_list[i:i + frames_per_100ms]):
                jank_frames.append(i + action_index)
    return jank_frames


def visualize_frame_sequence(frames, jank_frame_idx, image_name, window_size=3):
    """可视化卡顿帧前后的连续帧，并将它们拼接成一张图保存"""
    start_idx = max(jank_frame_idx, 0)
    end_idx = min(jank_frame_idx + window_size + 2, len(frames))

    # 获取单帧的尺寸
    frame_height, frame_width = frames[0].shape[:2]
    frame_height = int(frame_height / 2)
    frame_width = int(frame_width / 2)
    # 创建一个大图来容纳所有帧
    total_frames = end_idx - start_idx
    combined_image = np.zeros((frame_height, frame_width * total_frames, 3), dtype=np.uint8)
    for i, frame_idx in enumerate(range(start_idx, end_idx)):
        frame = frames[frame_idx]
        frame = cv2.resize(frame, (frame_width, frame_height))
        # 添加帧信息
        text = f'Frame {frame_idx}'
        if frame_idx == jank_frame_idx:
            text += ' (Jank)'
            frame = cv2.rectangle(frame, (0, 0),
                                  (frame.shape[1] - 1, frame.shape[0] - 1),
                                  (0, 0, 255), 2)

        # 添加相似度分数信息
        if frame_idx < len(frames) - 1:
            score = filtered_similar(frames[frame_idx], frames[frame_idx + 1])
            score_text = f'Score: {score:.3f}'
            cv2.putText(frame, score_text, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

        cv2.putText(frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        # 将当前帧放入大图中
        combined_image[:, i * frame_width:(i + 1) * frame_width] = frame

    # 保存拼接后的图片
    client_s3 = MssHHelper()
    s3_path_name = f'resource/{image_name}'
    base_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(base_dir, 'temp')
    local_path = os.path.join(temp_dir, f'{image_name}')
    cv2.imwrite(local_path, combined_image)
    image_url = client_s3.save_to_mss(local_path, s3_path_name)
    return image_url


def get_end_index(frames, fps, start_index, cut=0.0):
    cut_index = int(cut * fps) if cut else 1
    t_frame = frames[-cut_index]
    result = ClientHorus().get_ui_infer(t_frame)
    rect_list = []
    end_index = len(frames) - cut_index
    for rect in result['data']['recognize_results']:
        if rect['elem_det_type'] == 'image':
            x1, y1, x2, y2 = rect['elem_det_region']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            rect_list.append([x1, y1, x2, y2])
    for i in range(len(frames) - cut_index, start_index, -2):
        score = filtered_similar(frames[i], t_frame, rect_list)
        if score < 0.9:
            end_index = i - 1
            break
    return end_index


def video_call_back(task_id, resp, callback_URL):
    if task_id == 1000:
        print(resp)
    else:
        url = callback_URL
        resp['task_id'] = task_id
        json_data = json.dumps(resp)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json_data, headers=headers)


def video_perf(video_path, action_list=[], cut=0.0, task_id=1000, call_back_url=None):
    # 预处理视频
    fps, action_info_list = video_preprocess(video_path, action_list, cut=cut)
    # 计算100ms内的帧数
    frames_per_100ms = int(100 * (fps / 1000)) + 1
    result = {'fps': fps, 'result': []}
    for action_info in action_info_list:
        action_result = {}
        frames = action_info['frames']
        action_time = action_info['action_time']
        image_name = action_info['image_name']
        offset_time = action_info['offset_time']
        action_desc = action_info['action_desc']
        prompt = f"""
        通过App操作描述，推理页面是否会产生跳转/滑屏动作,返回json
        ===动作描述===
        {action_desc}
        ===结果===
        result - true/false
        reason - reason here
        """
        action_pred = llmcore_completion([{"role": "system", "content": prompt}], business="video_perf",
                                         response_format={"type": "json_object"}, model='gpt-4.1')
        if json.loads(action_pred)['result']:
            # 计算关键时间点
            action_index = int(fps * action_time)
            # 找到响应帧
            response_index = find_response_index(frames, action_index, len(frames))
            action_result['response_time'] = round(response_index/fps+offset_time, 2)
            end_index = get_end_index(frames, fps, response_index)
            action_result['end_time'] = round(end_index/fps+offset_time, 2)
            # 计算帧分数
            score_list = calculate_frame_scores(frames, action_index, end_index)

            # 检测卡顿帧
            jank_frames = detect_jank_frames(score_list, frames_per_100ms, response_index, action_index)
        else:
            action_result['response_time'] = 0.0
            action_result['end_time'] = 0.0
            jank_frames = []
            # 可视化每个卡顿帧
        action_result['action_time'] = action_time + offset_time
        action_result['action_desc'] = action_desc
        jank_list = []
        jank_frames = remove_close_numbers(jank_frames, frames_per_100ms*2)
        for jank_frame_idx in jank_frames:
            image_url = visualize_frame_sequence(frames, jank_frame_idx,
                                                 image_name.replace('.png', f"_{jank_frame_idx}.png"),
                                                 window_size=frames_per_100ms)
            prompt = """
            以下是App卡顿时的截图，根据图像的内容推理卡顿的可能原因，不超过10个字
            ===示例1===
            页面在转场过程中，可能是机器性能问题
            ===示例2===
            页面加载中，可能是网络问题
            """
            # desc = gpt_v(frames[jank_frame_idx+1], prompt, business='video_perf', temperature=0.3)
            desc = ""
            jank_list.append({
                "frame_idx": jank_frame_idx,
                "time_range": [round(jank_frame_idx/fps+offset_time, 2),
                               round((jank_frame_idx+frames_per_100ms)/fps+offset_time, 2)],
                "image_url": image_url,
                "desc": desc
            })
        action_result['jank_list'] = jank_list
        result['result'].append(action_result)
    clear_temp()
    if call_back_url:
        video_call_back(task_id, result, call_back_url)
    return result


if __name__ == '__main__':
    import os

    action_info_list = []
    video_list = []
    result_list = []
    
    def list_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == 'action_info.json':
                    action_info_list.append(os.path.join(root, file))
                if file == 'extracted_frames_video.mp4':
                    video_list.append((os.path.join(root, file)))

    # Load existing results if available
    results_dir = 'service/ui_detection/results'
    existing_results = {}
    if os.path.exists('service/ui_detection/results/results.json'):
        try:
            with open('service/ui_detection/results/results.json', 'r', encoding='utf-8') as f:
                existing_results = {result['video_url']: result for result in json.load(f)}
                print(len(existing_results))
        except Exception as e:
            print(f"Error loading existing results: {str(e)}")

    # 示例用法
    directory_path = "/Users/jinhailiang/Downloads/videos/"
    list_files(directory_path)
    
    for i, action_info_path in enumerate(action_info_list):
        with open(action_info_path, "r", encoding="utf-8") as file:
            action_info = json.load(file)
        
        video_url = video_list[i].replace("/Users/jinhailiang/Downloads/", "")
        
        # Skip if video already processed
        if video_url in existing_results:
            print(f"Skipping already processed video: {video_url}")
            result_list.append(existing_results[video_url])
            continue
            
        action_time = action_info['original_action_item']['action_time']
        action_desc = action_info['original_action_item']['action_desc']
        marked_response_time = action_info['original_action_item']['marked_response_time']
        marked_end_time = action_info['original_action_item']['marked_end_time']
        extract_start_time_sec = action_info['extraction_parameters']['extract_start_time_sec']
        action_time_sec = action_time - extract_start_time_sec
        
        req_data = {
            'video_url': video_list[i],
            "cut": 0.0,
            "action_list": [
                {
                    "action_time": action_time_sec,
                    "action_desc": action_desc
                }
            ]
        }
        
        result = video_perf(req_data['video_url'], action_list=req_data['action_list'], cut=req_data['cut'], task_id=1000,
                            call_back_url="")
        result['video_url'] = video_url
        result['marked_response_time'] = marked_response_time - extract_start_time_sec
        result['marked_end_time'] = marked_end_time - extract_start_time_sec
        result['resp_fp20'] = 1 if abs(result['marked_end_time']-result['result'][0]['end_time']) < 0.67 else 0
        result_list.append(result)

    print(result_list)

    # Save results
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    with open('service/ui_detection/results/results.json', 'w', encoding='utf-8') as f:
        json.dump(result_list, f, ensure_ascii=False, indent=4)
