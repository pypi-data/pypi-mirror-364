import copy

import cv2
from service.ui_detection.hash_similar import HashSimilar
from service.ui_detection.image_utils import image_preprocess, clear_temp
from utils import logger
from tools.s3 import MssHHelper
import os
import requests
import json
from service.lang_chain_utils.lion_client import client_prod as lion


similar_thresh_lion = float(lion.config.get(f'{lion.app_name}.video_performance_similar', '0.965'))


def get_start_index(data, longest_sub_sequence=True, similar_thresh=0):
    thresh = similar_thresh if similar_thresh else similar_thresh_lion
    print(thresh)
    if longest_sub_sequence:
        max_length = 0
        current_length = 1
        start_index = 0
        # 遍历数据列表
        for i in range(1, len(data)):
            # 如果当前值与前一个值相同，增加当前序列的长度
            if abs(data[i] - data[i - 1]) < 0.01:
                current_length += 1
            else:
                # 如果当前值与前一个值不同，比较当前序列长度与最大长度
                if current_length > max_length:
                    max_length = current_length
                    start_index = i - current_length
                # 重置当前序列的长度
                current_length = 1
        # 检查最后一个序列
        if current_length > max_length:
            start_index = len(data) - current_length
    else:
        start_index = 0
        for i in range(1, len(data)):
            if data[i] > thresh:
                start_index = start_index + 1
                break
            start_index = start_index + 1
    return start_index


def filtered_similar(img1, img2, ignore_list):
    hash_similar = HashSimilar()
    h, w, _ = img1.shape
    img_1 = copy.deepcopy(img1)
    img_2 = copy.deepcopy(img2)
    for rect in ignore_list:
        x1, y1, x2, y2 = rect
        x1, y1, x2, y2 = int(x1*w), int(y1*h), int(x2*w), int(y2*h)
        img_1[y1:y2, x1:x2] = img_2[y1:y2, x1:x2]
    score = hash_similar.get_similar_score(img_1, img_2, offset_y_percent=0.5)
    return score


def video_call_back(task_id, resp, callback_URL):
    if task_id == 1000:
        print(resp)
    else:
        url = callback_URL
        resp['task_id'] = task_id
        json_data = json.dumps(resp)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json_data, headers=headers)
        print(response.text)
        logger.info(f'[video performance][task id:{task_id}][{resp}][{response.text}]')


def fine_tuning(frame_index, frames, ignore_list, fps):
    tuning_index = frame_index
    tuning_range = int(fps/2)
    start_index = 0 if frame_index - tuning_range <= 0 else frame_index-tuning_range
    end_index = len(frames)-2 if frame_index + tuning_range >= len(frames)-2 else frame_index + tuning_range
    for i in range(start_index, end_index):
        score = filtered_similar(frames[i], frames[frame_index], ignore_list)
        if 1 - score < 0.01:
            tuning_index = i
            break
    return tuning_index


def video_load_duration(video_url, start_time, task_id, callback_URL, ignore_list=[], similar_thresh=0.0):
    video_path, video_name = image_preprocess(video_url)
    image_name = video_name.replace('.mp4', '.png')
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    count = 0
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No more frames to read.")
            break
        count = count + 1
        frames.append(frame)
    cap.release()
    stable_frame = frames[-2]
    score_list = []
    index_list = []
    k = 10 if fps < 100 else 15
    fps_step = int(fps/50*k)
    for i, f in enumerate(frames):
        if i % int(fps / fps_step) == 0:
            score = filtered_similar(f, stable_frame, ignore_list)
            if score > 0.6:
                score_list.append(score)
                index_list.append(i)

    start_index = get_start_index(score_list, False, similar_thresh)
    index = start_index + 1 if len(index_list) > start_index + 1 else len(index_list)-1
    frame_index = index_list[index]
    tuning_index = fine_tuning(frame_index, frames, ignore_list, fps)
    end_time = tuning_index/fps
    img = frames[tuning_index]
    h, w, _ = img.shape
    for rect in ignore_list:
        x1, y1, x2, y2 = rect
        cv2.rectangle(img, (int(x1*w), int(y1*h)), (int(x2*w), int(y2*h)), (255, 0, 0), 3)
    client_s3 = MssHHelper()
    s3_path_name = f'resource/{image_name}'
    base_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(base_dir, 'temp')
    local_path = os.path.join(temp_dir, f'{image_name}')
    h, w, _ = img.shape
    cv2.imwrite(local_path, img)
    image_url = client_s3.save_to_mss(local_path, s3_path_name)
    video_call_back(task_id, {'duration': round(end_time-start_time, 2), 'image': image_url}, callback_URL)
    clear_temp()


if __name__ == '__main__':
    video_url = 'https://msstest.sankuai.com/s3plus-oriolefe/performance-test/xiaomi15-dd-app-sy-0-6.67.402.mp4'
    # video_url = 'https://msstest.sankuai.com/s3plus-oriolefe/performance-test/xiaomi15-xx-app-sx-0-6.67.402.mp4'
    video_url = 'https://msstest.sankuai.com/s3plus-oriolefe/performance-test/xiaomi15-dd-app-gwc-0-6.67.402.mp4'
    ignore_list = []
    print(video_load_duration(video_url, 0.0, 1000, 'http://qa.mall.test.sankuai.com/api/oriole/lvc/callback',
                              ignore_list=ignore_list, similar_thresh=0.82))
