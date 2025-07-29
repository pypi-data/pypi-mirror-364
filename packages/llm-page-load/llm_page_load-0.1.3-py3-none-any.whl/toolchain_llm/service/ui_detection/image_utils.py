import os
import cv2
import numpy
import time
import signal
import threading
import numpy as np
import urllib.request


def clear_temp():
    try:
        from datetime import datetime, timedelta
        base_dir = os.path.dirname(os.path.realpath(__file__))
        temp_dir = os.path.join(base_dir, 'temp')
        # 指定要清理的目录路径
        directory_to_clean = temp_dir
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)
        for filename in os.listdir(directory_to_clean):
            # 获取文件的完整路径
            file_path = os.path.join(directory_to_clean, filename)

            # 确保是文件而不是文件夹
            if os.path.isfile(file_path) and filename != '.gitkeep':
                # 获取文件的创建时间
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))

                # 如果文件的创建时间在一天前，则删除该文件
                if file_creation_time < one_day_ago:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
    except Exception as e:
        print(repr(e))


def image_preprocess(image_url):
    image_name = image_url.split('/')[-1]
    base_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(base_dir, 'temp')
    local_path = os.path.join(temp_dir, image_name)
    if 'http' in image_url:
        download_image(image_url, local_path)
    else:
        local_path = image_url
    return local_path, image_name


def download_image(url, filename):
    with urllib.request.urlopen(url) as response:
        with open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)


def merge_rectangle_contours(rectangle_contours):
    merged_contours = [rectangle_contours[0]] if len(rectangle_contours) > 0 else []
    for rec in rectangle_contours[1:]:
        for i in range(len(merged_contours)):
            x_min = rec[0][0]
            y_min = rec[0][1]
            x_max = rec[2][0]
            y_max = rec[2][1]
            merged_x_min = merged_contours[i][0][0]
            merged_y_min = merged_contours[i][0][1]
            merged_x_max = merged_contours[i][2][0]
            merged_y_max = merged_contours[i][2][1]
            if x_min >= merged_x_min and y_min >= merged_y_min and x_max <= merged_x_max and y_max <= merged_y_max:
                break
            else:
                if i == len(merged_contours)-1:
                    merged_contours.append(rec)
    # print(len(rectangle_contours), len(merged_contours))
    return merged_contours


def contour_area_filter(binary, contours, thresh=1800):
    rectangle_contours =[]
    h, w = binary.shape
    for contour in contours:
        if thresh < cv2.contourArea(contour) < 0.2*h*w:
            rectangle_contours.append(contour)
    return rectangle_contours


def get_roi_image(img, rectangle_contour, gray=True):
    if gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if (len(img.shape) > 2) else img
    roi_image = img[rectangle_contour[0][1]:rectangle_contour[2][1],
                rectangle_contour[0][0]:rectangle_contour[1][0]]
    return roi_image


def get_rectangle_contours(binary, area_thresh=1800, area_counter=100):
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rectangle_contours = []
    for counter in contours:
        x, y, w, h = cv2.boundingRect(counter)
        cnt = numpy.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
        rectangle_contours.append(cnt)
    rectangle_contours = sorted(rectangle_contours, key=cv2.contourArea, reverse=True)[:area_counter]
    rectangle_contours = contour_area_filter(binary, rectangle_contours, area_thresh)
    rectangle_contours = merge_rectangle_contours(rectangle_contours)
    return rectangle_contours


def get_center_pos(contour):
    x = int((contour[0][0]+contour[1][0])/2)
    y = int((contour[1][1]+contour[2][1])/2)
    return x, y


def get_label_pos(contour):
    ret = get_center_pos(contour)
    center = [ret[0], ret[1]]
    x = int((int((center[0]+contour[2][0])/2)+contour[2][0])/2)
    y = int((int((center[1]+contour[2][1])/2)+contour[2][1])/2)
    return x, y


def region_to_rect(regions, type="x_y"):
    """
    convert (x,y,w,h) to ((x1,y1),(x2,y3),(x3,y3),(x4,y4))
    """
    rects = []
    for region in regions:
        x = region[0]
        y = region[1]
        w = region[2] if type == 'w_h' else region[2] - x
        h = region[3] if type == 'w_h' else region[3] - y
        rects.append([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])
    return rects


def draw_contours(img, contours, color=(255, 145, 30), type='x_y'):
    if len(contours) > 0:
        contours = region_to_rect(contours, type=type) if len(numpy.array(contours[0]).shape) == 1 else contours
        contours = numpy.array(contours)
        _, w, _ = img.shape
        cv2.drawContours(img, contours, -1, color, w // 200)


def compute_iou(rect1, rect2):
    """
    computing IoU
    :param rec1: [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
    :param rec2: [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
    :return: scala value of IoU
    """
    rec1 = [rect1[0][1], rect1[0][0], rect1[2][1], rect1[2][0]]
    rec2 = [rect2[0][1], rect2[0][0], rect2[2][1], rect2[2][0]]
    # computing area of each rectangles
    S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
    S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

    # computing the sum_area
    sum_area = S_rec1 + S_rec2

    # find the each edge of intersect rectangle
    left_line = max(rec1[1], rec2[1])
    right_line = min(rec1[3], rec2[3])
    top_line = max(rec1[0], rec2[0])
    bottom_line = min(rec1[2], rec2[2])

    # judge if there is an intersect
    if left_line >= right_line or top_line >= bottom_line:
        return 0
    else:
        intersect = (right_line - left_line) * (bottom_line - top_line)
        return (intersect / (sum_area - intersect))*1.0


def cosine_similarity(x, y, norm=False):
    """ 计算两个向量x和y的余弦相似度 """
    assert len(x) == len(y), "len(x) != len(y)"
    zero_list = [0] * len(x)
    if x == zero_list or y == zero_list:
        return float(1) if x == y else float(0)
    res = numpy.array([[x[i] * y[i], x[i] * x[i], y[i] * y[i]] for i in range(len(x))])
    cos = sum(res[:, 0]) / (numpy.sqrt(sum(res[:, 1])) * numpy.sqrt(sum(res[:, 2])))
    return 0.5 * cos + 0.5 if norm else cos  # 归一化到[0, 1]区间内


def set_timeout(num):
    """
    signal works in main thread
    """
    def wrap(func):
        def handle(signum, frame):
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                r = func(*args, **kwargs)
                signal.alarm(0)
                return r
            except RuntimeError as e:
                pass

        return to_do

    return wrap


def m_diff(e, f, i=0, j=0, equal_obj=object()):
    N, M, L, Z = len(e), len(f), len(e) + len(f), 2 * min(len(e), len(f)) + 2
    if N > 0 and M > 0:
        w, g, p = N - M, [0] * Z, [0] * Z
        for h in range(0, (L // 2 + (L % 2 != 0)) + 1):
            for r in range(0, 2):
                c, d, o, m = (g, p, 1, 1) if r == 0 else (p, g, 0, -1)
                for k in range(-(h - 2 * max(0, h - M)), h - 2 * max(0, h - N) + 1, 2):
                    a = c[(k + 1) % Z] if (k == -h or k != h and c[(k - 1) % Z] < c[(k + 1) % Z]) else c[(k - 1) % Z] + 1
                    b = a - k
                    s, t = a, b
                    while a < N and b < M and equal_obj.equal(e[(1 - o) * N + m * a + (o - 1)], f[(1 - o) * M + m * b + (o - 1)]):
                        a, b = a + 1, b + 1
                    c[k % Z], z = a, -(k - w)
                    if L % 2 == o and -(h - o) <= z <= h - o and c[k % Z] + d[z % Z] >= N:
                        D, x, y, u, v = (2 * h - 1, s, t, a, b) if o == 1 else (2 * h, N - a, M - b, N - s, M - t)
                        if D > 1 or (x != u and y != v):
                            return m_diff(e[0:x], f[0:y], i, j, equal_obj) + m_diff(e[u:N], f[v:M], i + u, j + v, equal_obj)
                        elif M > N:
                            return m_diff([], f[N:M], i + N, j + N, equal_obj)
                        elif M < N:
                            return m_diff(e[M:N], [], i + M, j + M, equal_obj)
                        else:
                            return []
    elif N > 0:
        return [{"operation": "delete", "position_old": i + n} for n in range(0, N)]
    else:
        return [{"operation": "insert", "position_old": i, "position_new": j + n} for n in range(0, M)]


def calculate_time(f):
    def wrapper(*args, **kwargs):
        t_start = time.time()
        ret = f(*args, **kwargs)
        t_end = time.time()
        print(f.__name__ + ":" + str(round((t_end - t_start) * 1000, 2)) + "ms")
        return ret
    return wrapper


def get_image_gray(img_file, offset_y_percent=0.078, area=None):
    img = cv2.imread(img_file) if isinstance(img_file, str) else img_file
    if img is None:
        return None
    h, w, _ = img.shape
    if area:
        x1, y1, x2, y2 = area
        img = img[max(0, y1):min(h, y2), max(0, x1):min(w, x2), :]
    if area is None and offset_y_percent > 0:
        img = img[int(w * offset_y_percent):, :, :]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray


def get_image_list(img_gray):
    i = 0
    img_list = []
    if img_gray is None:
        return img_list
    h, w = img_gray.shape
    img_gray = img_gray[:, :w - 80]
    stride = int(w * 0.03)
    while i < h:
        img_list.append(img_gray[i:i + stride, :])
        i = i + stride
    return img_list


def alpha_channel_merge(foreground_image_path, background_image_path):
    foreground = cv2.imread(foreground_image_path, cv2.IMREAD_UNCHANGED)
    background = cv2.imread(background_image_path, cv2.IMREAD_UNCHANGED)
    alpha_background = background[:, :, 3] / 255.0
    alpha_foreground = foreground[:, :, 3] / 255.0
    for color in range(0, 3):
        background[:, :, color] = alpha_foreground * foreground[:, :, color] + \
            alpha_background * background[:, :, color] * (1 - alpha_foreground)
    background[:, :, 3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255
    cv2.imwrite(background_image_path, background)


def has_part_page_on_loading(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return False
    h, w, _ = img.shape
    # RGB三个通道的值相加
    data = np.dot(img, np.ones((3, 1), dtype=int))
    # 200 x img_w：为一个检测区块
    t = 200
    h_start = 0
    h_end = 0
    total_part_count = 0
    loading_part_count = 0
    concat_empty_part = 0
    while h_end < h:
        h_end = min(h_start + t, h)
        # 常见未加载场景的底色范围是：220-255，所以RGB的值加起来最小值是660
        c = np.sum(data[h_start:h_end, :, :] > 660)
        p = c / ((h_end - h_start) * w)
        total_part_count += 1
        h_start = h_end
        if p == 1:
            loading_part_count += 1
        else:
            concat_empty_part = max(loading_part_count, concat_empty_part)
            loading_part_count = 0

    p = concat_empty_part / total_part_count
    # 连续空白区块占总页面的30%以上，算未加载完成
    return p > 0.3

class TaskThread(threading.Thread):
    def __init__(self, func, args=()):
        super(TaskThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None