from src.toolchain_llm.service.ui_detection import image_utils
from src.toolchain_llm.service.ui_detection.image_utils import *
from src.toolchain_llm.service.ui_detection.horus_ocr import ClientHorus
from src.toolchain_llm.service.ui_detection.hash_similar import HashSimilar
import re
import cv2
import numpy as np


def auto_detect_screen_rect(img):
    # 简单自动检测最大矩形轮廓作为屏幕区域
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    best_rect = (0, 0, img.shape[1], img.shape[0])
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > max_area and w > img.shape[1] // 2 and h > img.shape[0] // 2:
            max_area = area
            best_rect = (x, y, x + w, y + h)
    return best_rect

def get_global_screen_rect(segment_dir, frame_indices, sample_count=5):
    """
    分析多个帧的屏幕区域，找到统一的裁剪区域
    
    Args:
        segment_dir: 视频片段目录
        frame_indices: 要分析的帧索引列表
        sample_count: 采样帧数量，默认5帧
    
    Returns:
        tuple: (x1, y1, x2, y2) 统一的屏幕区域坐标
    """
    from utils.llm_narrow_core import load_frame_from_npy
    
    # 采样帧进行分析
    sample_frames = []
    step = max(1, len(frame_indices) // sample_count)
    for i in range(0, len(frame_indices), step):
        if len(sample_frames) >= sample_count:
            break
        frame_idx = frame_indices[i]
        img = load_frame_from_npy(segment_dir, frame_idx)
        if img is not None:
            # 转换为OpenCV格式
            img_np = np.array(img.convert('RGB'))
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            sample_frames.append(img_cv)
    
    if not sample_frames:
        print(f"[Global-Screen] 没有可用的采样帧")
        return (0, 0, 1000, 1000)  # 默认区域
    
    print(f"[Global-Screen] 分析 {len(sample_frames)} 个采样帧的屏幕区域")
    
    # 检测每个帧的屏幕区域
    screen_rects = []
    for i, img in enumerate(sample_frames):
        rect = auto_detect_screen_rect(img)
        screen_rects.append(rect)
        print(f"[Global-Screen] 帧 {i}: 检测到屏幕区域 {rect}")
    
    # 计算统一的屏幕区域（取交集或使用最常见的区域）
    if len(screen_rects) == 1:
        global_rect = screen_rects[0]
    else:
        # 计算所有区域的重叠部分
        x1_max = max(rect[0] for rect in screen_rects)
        y1_max = max(rect[1] for rect in screen_rects)
        x2_min = min(rect[2] for rect in screen_rects)
        y2_min = min(rect[3] for rect in screen_rects)
        
        # 如果重叠区域太小，使用面积最大的区域
        overlap_area = (x2_min - x1_max) * (y2_min - y1_max)
        max_area_rect = max(screen_rects, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
        max_area = (max_area_rect[2] - max_area_rect[0]) * (max_area_rect[3] - max_area_rect[1])
        
        if overlap_area > max_area * 0.5:  # 重叠区域大于最大区域的50%
            global_rect = (x1_max, y1_max, x2_min, y2_min)
            print(f"[Global-Screen] 使用重叠区域: {global_rect}")
        else:
            global_rect = max_area_rect
            print(f"[Global-Screen] 重叠区域太小，使用最大区域: {global_rect}")
    
    print(f"[Global-Screen] 最终统一屏幕区域: {global_rect}")
    return global_rect

def crop_and_resize_to_screen(img, screen_rect, target_size):
    x1, y1, x2, y2 = screen_rect
    cropped = img[y1:y2, x1:x2]
    resized = cv2.resize(cropped, target_size)
    return resized


class LineFeatureEqual(object):
    def __init__(self):
        self.thresh = 0.75

    def equal(self, a, b):
        if get_hash_score(a, b) > self.thresh:
            return True
        else:
            return False


def get_hash_score(hash1, hash2, precision=8):
    score = 1 - HashSimilar.hamming_dist(hash1, hash2) * 1.0 / (precision * precision)
    return score


def get_line_list(op_list):
    line1_list = []
    line2_list = []
    for op in op_list:
        if op["operation"] == "insert":
            line1_list.append(op["position_new"])
        if op["operation"] == "delete":
            line2_list.append(op["position_old"])
    return line1_list, line2_list


def get_line_feature(image, precision=8):
    line_feature = []
    for y in range(image.shape[0]):
        img = cv2.resize(image[y], (precision, precision))
        img_list = img.flatten()
        avg = np.mean(img_list)
        avg_list = ["0" if i < avg else "1" for i in img_list]
        line_feature.append([int(''.join(avg_list[x:x+4]), 2) for x in range(0, precision*precision)])
    return line_feature


def get_image_feature(img1, img2):
    h1, w = img1.shape
    img1 = img1[:, :w-80]
    img2 = img2[:, :w-80]
    img1_feature = get_line_feature(img1)
    img2_feature = get_line_feature(img2)
    return img1_feature, img2_feature


def line_filter(line_list):
    i = 0
    w = 3
    line = []
    while i < len(line_list)-w-1:
        f = line_list[i:i+w]
        s = 0
        for j in range(w-1):
            s = s + f[j+1] - f[j]
        if s - w <= 6:
            for l in f:
                if l not in line:
                    line.append(l)
        i = i + 1
    return line


def get_image(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 1.0)
    h, w = img.shape
    scale = 850/w
    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
    return img, scale


def get_pixel(img, x, y):
    h, w = img.shape
    p = 0
    if y < h:
        p = img[y][x]
    return p


def process_ch_text(text):
    """
    只保留中文，字母和数字
    :param text:
    :return:
    """
    cop = re.compile("(\\\\\d+|u\d+|\^|\\\\\"20c)|[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    text = cop.sub('', text)
    return text


class ImageDiff(object):

    def __init__(self, img1, img2, ocr_result, ocr_score_thresh=0.98, struct_score_thresh=0.8,
                 ignore_bottom=True):
        self.img1 = img1
        self.img2 = img2
        self.ocr_result = ocr_result
        self.attention = []
        self.ocr_score = 0
        self.ocr_score_thresh = ocr_score_thresh
        self.struct_score_thresh = struct_score_thresh
        self.ignore_bottom = ignore_bottom

    @staticmethod
    def _point_in_crops(point, crop, img_h, img_w):
        """
        判断一个点是否在图片中指定区域内
        @param point 点，例如：[x, y]
        @param crop 区域，例如：{"x1":0.62, "y1": 0.323, "x2":0.701, "y2":0.43}, 数值是对应高宽的比值
        @param img_h 图片的高
        @param img_w 图片的宽
        @return True-点在区域中，False-不在
        """
        crop_left_up = (max(0, int(float(crop['x1']) * img_w) - 10), max(0, int(float(crop['y1']) * img_h) - 10))
        crop_right_down = (int(float(crop['x2']) * img_w) + 10, int(float(crop['y2']) * img_h) + 10)
        return crop_right_down[0] >= point[0] >= crop_left_up[0] and crop_right_down[1] >= point[1] >= \
                            crop_left_up[1]

    @staticmethod
    def text_in_crop(text_rect, crop, img_h, img_w, thresh=0.8):
        """
        根据文本区域与crop相交面积与文本区域的比例 >= thresh， 判断文本是否在指定区域内。
        @param text_rect，例如：[[x1, y1], [x2, y1], [x2 y2], [x1, y2]]
        @param crop 区域，例如：{"x1":0.62, "y1": 0.323, "x2":0.701, "y2":0.43}, 数值是对应高宽的比值
        @param img_h 图片的高
        @param img_w 图片的宽
        @param thresh 阈值
        @return True-大部分的文本处于区域内
        """
        crop_x1 = max(0, int(float(crop['x1']) * img_w))
        crop_y1 = max(0, int(float(crop['y1']) * img_h))
        crop_x2 = int(float(crop['x2']) * img_w)
        crop_y2 = int(float(crop['y2']) * img_h)

        rec1 = [int(text_rect[0][0]), int(text_rect[0][1]), int(text_rect[2][0]), int(text_rect[2][1])]
        rec2 = [crop_x1, crop_y1, crop_x2, crop_y2]
        # computing area of each rectangles
        s_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
        s_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

        # computing the sum_area
        sum_area = s_rec1 + s_rec2

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
            return (intersect / s_rec1) * 1.0

    @staticmethod
    def get_mask_with_crop(h, w, img_show, points, scheme_crops):
        if not scheme_crops or len(scheme_crops) <= 0:
            return points

        # 给屏蔽区域和识别区域画不同颜色的框
        for crop in scheme_crops:
            crop_left_up = (int(float(crop['x1']) * w), int(float(crop['y1']) * h))
            crop_right_down = (int(float(crop['x2']) * w), int(float(crop['y2']) * h))
            color = (255, 255, 51) if crop['type'] == 'ignore' else (255, 0, 255)
            cv2.rectangle(img_show, crop_left_up, crop_right_down, color, 5)

        # 获取绘制区域
        target_crops = [scheme_crop for scheme_crop in scheme_crops if scheme_crop['type'] == 'target']
        ignore_crops = [scheme_crop for scheme_crop in scheme_crops if scheme_crop['type'] == 'ignore']

        filter_points = []
        # 未设置识别区域时，默认所有点都在识别区域
        in_target_crop = True
        # 未设置忽略区域时，默认所有点都不在忽略区域
        in_ignore_crop = False
        for point in points:
            if len(target_crops) > 0:
                in_target_crop = False
                for crop in target_crops:
                    if ImageDiff._point_in_crops(point, crop, h, w):
                        in_target_crop = True
                        break
            if len(ignore_crops) > 0:
                in_ignore_crop = False
                for crop in ignore_crops:
                    if ImageDiff._point_in_crops(point, crop, h, w):
                        in_ignore_crop = True
                        break
            # 只有当前点在识别区域，且不在忽略区域时，才需要绘制
            if in_target_crop and not in_ignore_crop:
                filter_points.append(point)

        return filter_points

    @staticmethod
    def draw_diff_on_image(filter_points, img_show):
        mask = img_show.copy()
        draw_board = np.zeros((img_show.shape[0], img_show.shape[1]), dtype=np.uint8) + 255
        for point in filter_points:
            cv2.circle(draw_board, (point[0], point[1]), 1, (0, 0, 0), -1)
        contours = get_rectangle_contours(draw_board, area_thresh=30, area_counter=500)
        for counter in contours:
            x, y, w, h = cv2.boundingRect(counter)
            cnt = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            cv2.fillConvexPoly(mask, np.array(cnt), (101, 67, 254))
        alpha = 0.6
        beta = 1 - alpha
        gamma = 0
        img_weighted_show = cv2.addWeighted(img_show, alpha, mask, beta, gamma)
        return img_weighted_show

    @staticmethod
    def draw_diff_on_first_image(filter_points, img1_original, diff_color=(0, 255, 0)):
        """
        将差异部分直接绘制在第一幅图上，使用指定的颜色
        
        @param filter_points: 差异点列表
        @param img1_original: 原始的第一幅图像（BGR格式）
        @param diff_color: 差异区域的颜色，默认为绿色 (0, 255, 0)
        @return: 绘制了差异区域的第一幅图像
        """
        # 创建第一幅图像的副本
        img1_with_diff = img1_original.copy()
        
        if len(filter_points) == 0:
            return img1_with_diff
            
        # 创建绘制板，用于找到连续的差异区域
        draw_board = np.zeros((img1_with_diff.shape[0], img1_with_diff.shape[1]), dtype=np.uint8) + 255
        
        # 在绘制板上标记差异点
        for point in filter_points:
            cv2.circle(draw_board, (point[0], point[1]), 1, (0, 0, 0), -1)
        
        # 获取矩形轮廓
        contours = get_rectangle_contours(draw_board, area_thresh=30, area_counter=500)
        
        # 在每个轮廓区域绘制差异颜色
        for counter in contours:
            x, y, w, h = cv2.boundingRect(counter)
            cnt = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            # 使用半透明效果绘制差异区域
            mask = np.zeros(img1_with_diff.shape[:2], dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.array(cnt), 255)
            
            # 创建颜色遮罩
            color_mask = np.zeros_like(img1_with_diff)
            color_mask[mask > 0] = diff_color
            
            # 混合原图和颜色遮罩
            alpha = 0.7  # 透明度
            img1_with_diff = cv2.addWeighted(img1_with_diff, 1-alpha, color_mask, alpha, 0)
        
        return img1_with_diff

    def calculate_attention(self, line, h, show_scale):
        line_attention = []
        score_list = self.attention
        print(f'[Attention-Debug] 开始注意力计算，输入行数: {len(line)}, score_list长度: {len(score_list) if score_list else 0}')
        
        # text attention
        if self.ocr_result and len(score_list) > 0:
            _rects = self.ocr_result.get('diff_rects')
            scale = self.ocr_result.get('scale')
            ocr_diff_rects = _rects if _rects else []
            print(f'[Attention-Debug] OCR差异矩形数: {len(ocr_diff_rects)}')
            for ocr_diff_rect in ocr_diff_rects:
                y_start = int(ocr_diff_rect[0][1]/scale)
                y_end = int(ocr_diff_rect[2][1]/scale)
                for i in range(y_start, y_end, 1):
                    opt_i = int(len(score_list)*i/(h/show_scale))
                    if 0 <= opt_i < len(score_list):
                        score_list[opt_i] -= 0.001
        
        # line attention - 放宽条件，不使用score_list过滤
        if len(score_list) > 0:
            print(f'[Attention-Debug] 使用score_list过滤，阈值: 0.98')
            for l in line:
                i = int((len(score_list) * (l-1) / h))
                i = 0 if i < 0 else i
                if i < len(score_list):
                    score = score_list[i] if i < len(score_list) else 1.0
                    if score < 0.98:
                        line_attention.append(l)
                    else:
                        print(f'[Attention-Debug] 行 {l} 被过滤，score: {score}')
        else:
            print(f'[Attention-Debug] score_list为空，保留所有行')
            line_attention = line
        
        print(f'[Attention-Debug] 注意力计算完成，输出行数: {len(line_attention)}')
        return line_attention
    def align_image_to_reference(self,img_ref, img_to_align):
        # 灰度化
        gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY) if len(img_ref.shape) == 3 else img_ref
        gray_align = cv2.cvtColor(img_to_align, cv2.COLOR_BGR2GRAY) if len(img_to_align.shape) == 3 else img_to_align

        # SIFT特征
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(gray_ref, None)
        kp2, des2 = sift.detectAndCompute(gray_align, None)
        if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
            print('[Align] 特征点不足，跳过对齐')
            return img_to_align

        # FLANN匹配
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        if len(good) < 10:
            print('[Align] 匹配点不足，跳过对齐')
            return img_to_align

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if H is None:
            print('[Align] 单应性矩阵失败，跳过对齐')
            return img_to_align

        h, w = gray_ref.shape
        aligned = cv2.warpPerspective(img_to_align, H, (w, h))
        print('[Align] 对齐成功')
        return aligned
    def filter_small_diff_points(self, points, min_area=100, h=None, w=None):
        # 生成二值图
        if not points:
            return []
        if h is None or w is None:
            h = max(p[1] for p in points) + 1
            w = max(p[0] for p in points) + 1
        mask = np.zeros((h, w), dtype=np.uint8)
        for x, y in points:
            mask[y, x] = 255
        # 连通域分析
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        filtered = []
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                ys, xs = np.where(labels == i)
                filtered.extend(list(zip(xs, ys)))
        return filtered
    def image_diff(self, scheme_crops=[]):
        points = []
        print(f'[Diff-Debug] 开始image_diff，img1.shape={self.img1.shape}, img2.shape={self.img2.shape}')
        img1, _ = get_image(self.img1)
        img2, show_scale = get_image(self.img2)
        print(f'[Diff-Debug] 获取图像后: img1.shape={img1.shape}, img2.shape={img2.shape}, show_scale={show_scale}')
        # 自动检测屏幕内容区域
        rect1 = auto_detect_screen_rect(self.img1)
        rect2 = auto_detect_screen_rect(self.img2)
        print(f'[Diff-Debug] 检测到屏幕区域: img1={rect1}, img2={rect2}')
        # 统一resize到内容区最大尺寸
        target_w = max(rect1[2]-rect1[0], rect2[2]-rect2[0])
        target_h = max(rect1[3]-rect1[1], rect2[3]-rect2[1])
        img1_screen = crop_and_resize_to_screen(self.img1, rect1, (target_w, target_h))
        img2_screen = crop_and_resize_to_screen(self.img2, rect2, (target_w, target_h))
        # 后续diff用内容区
        img1, _ = get_image(img1_screen)
        img2, show_scale = get_image(img2_screen)
        print(f'[Diff-Debug] 内容区对齐后: img1.shape={img1.shape}, img2.shape={img2.shape}')
        img2 = self.align_image_to_reference(img1, img2)
        print(f'[Diff-Debug] 对齐后: img1.shape={img1.shape}, img2.shape={img2.shape}')
        if img1.shape != img2.shape:
            print(f'[Diff-Debug] 图像尺寸不匹配，将img2调整为img1的尺寸')
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            print(f'[Diff-Debug] 调整后: img1.shape={img1.shape}, img2.shape={img2.shape}')
        img1_feature, img2_feature = get_image_feature(img1, img2)
        line1, line2 = get_line_list(m_diff(img1_feature, img2_feature, equal_obj=LineFeatureEqual()))
        print(f'[Diff-Debug] 行特征检测: line1={len(line1)}, line2={len(line2)}')
        if len(self.img1.shape) == 3:
            img_show = self.img1.copy()
        else:
            img_show = cv2.cvtColor(self.img1, cv2.COLOR_GRAY2BGR)
        if len(img_show.shape) == 3:
            h, w = img_show.shape[:2]
        else:
            h, w = img_show.shape
        print(f'[Diff-Debug] 显示图像尺寸: h={h}, w={w}')
        line = line1 + line2
        line = line_filter(line)
        print(f'[Diff-Debug] 过滤后行数: {len(line)}')
        print(f'[Diff-Debug] 跳过注意力计算，直接使用所有行: {len(line)}')
        margin = 40  # 区域过滤
        step = 2
        points_found = 0
        print(f'[Diff-Debug] 仅在内容区域做diff: margin={margin}, step={step}')
        for y in range(margin, h-margin, step):
            for x in range(margin, w-margin, step):
                p1 = int(get_pixel(img1, x, y))
                p2 = int(get_pixel(img2, x, y))
                diff = abs(p1 - p2)
                if diff >= 15:
                    points.append([x, y])
                    points_found += 1
                    if points_found <= 5:
                        print(f'[Diff-Debug] 找到差异点: ({x}, {y}), p1={p1}, p2={p2}, diff={diff}')
        print(f'[Diff-Debug] 像素比较完成，找到差异点: {len(points)}')
        # 保存面积过滤前的diff点分布
        if points:
            mask_debug = np.zeros((h, w), dtype=np.uint8)
            for x, y in points:
                mask_debug[y, x] = 255
            cv2.imwrite('diff_points_mask.png', mask_debug)
            print(f'[Diff-Debug] 已保存diff点分布图: diff_points_mask.png')
            # 形态学膨胀，连接稀疏diff点
            kernel = np.ones((7, 21), np.uint8)  # 横向膨胀更强，参数可调
            mask_dilated = cv2.dilate(mask_debug, kernel, iterations=1)
            cv2.imwrite('diff_points_mask_dilated.png', mask_dilated)
            print(f'[Diff-Debug] 已保存膨胀后diff点分布图: diff_points_mask_dilated.png')
            ys, xs = np.where(mask_dilated > 0)
            dilated_points = list(zip(xs, ys))
            points = self.filter_small_diff_points(dilated_points, min_area=200, h=h, w=w)
            print(f'[Diff-Debug] 膨胀+面积过滤后点数: {len(points)}')
        else:
            print(f'[Diff-Debug] 没有diff点可保存')
            points = []

        filter_points = ImageDiff.get_mask_with_crop(h, w, img_show, points, scheme_crops)
        print(f'[Diff-Debug] mask过滤后点数: {len(filter_points)}')
        if len(filter_points) > 0:
            print(f'[Diff-Debug] 开始绘制diff，点数: {len(filter_points)}')
            img_show = ImageDiff.draw_diff_on_image(filter_points, img_show)
            print(f'[Diff-Debug] diff绘制完成')
        else:
            print(f'[Diff-Debug] 没有差异点需要绘制')
        try:
            cv2.imwrite('debug_img1_gray.png', img1)
            cv2.imwrite('debug_img2_gray.png', img2)
            cv2.imwrite('debug_img_show_final.png', img_show)
            if img1.shape == img2.shape:
                absdiff = cv2.absdiff(img1, img2)
                cv2.imwrite('debug_absdiff.png', absdiff)
                print(f'[Diff-Debug] 保存调试图像完成')
        except Exception as e:
            print(f'[Diff-Debug] 保存调试图像失败: {e}')
        return img_show, len(filter_points)

    def _align_images(self, img1, img2):
        """
        使用特征匹配和单应性变换对齐两幅图像
        
        Args:
            img1: 参考图像（第一帧）
            img2: 需要对齐的图像（第二帧）
            
        Returns:
            对齐后的img2，如果对齐失败返回None
        """
        try:
            # 转换为灰度图像进行特征检测
            if len(img1.shape) == 3:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            else:
                gray1 = img1.copy()
                
            if len(img2.shape) == 3:
                gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            else:
                gray2 = img2.copy()
            
            # 使用SIFT特征检测器
            sift = cv2.SIFT_create()
            
            # 检测关键点和描述符
            kp1, des1 = sift.detectAndCompute(gray1, None)
            kp2, des2 = sift.detectAndCompute(gray2, None)
            
            print(f'[Align-Debug] 检测到特征点: img1={len(kp1)}, img2={len(kp2)}')
            
            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                print(f'[Align-Debug] 特征点不足，跳过对齐')
                return None
            
            # 使用FLANN匹配器
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            matches = flann.knnMatch(des1, des2, k=2)
            
            # 应用Lowe's ratio test筛选好的匹配
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)
            
            print(f'[Align-Debug] 好的匹配点数量: {len(good_matches)}')
            
            if len(good_matches) < 10:
                print(f'[Align-Debug] 好的匹配点不足，跳过对齐')
                return None
            
            # 提取匹配点的坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # 计算单应性矩阵
            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            
            if H is None:
                print(f'[Align-Debug] 无法计算单应性矩阵，跳过对齐')
                return None
            
            # 应用变换
            h, w = gray1.shape
            aligned_img2 = cv2.warpPerspective(img2, H, (w, h))
            
            print(f'[Align-Debug] 图像对齐成功')
            return aligned_img2
            
        except Exception as e:
            print(f'[Align-Debug] 图像对齐异常: {e}')
            return None

    def image_diff_on_first_image(self, scheme_crops=[], diff_color=(0, 255, 0)):
        """
        将两幅图片的差异部分直接绘制在第一幅图上，使用指定的颜色
        
        @param scheme_crops: 区域裁剪配置
        @param diff_color: 差异区域的颜色，默认为绿色 (0, 255, 0)
        @return: (绘制了差异区域的第一幅图像, 差异点数量)
        """
        points = []
        
        # 获取原始图像用于显示（保持彩色）
        if len(self.img1.shape) == 3:
            img1_original = self.img1.copy()
        else:
            img1_original = cv2.cvtColor(self.img1, cv2.COLOR_GRAY2BGR)
        if len(self.img2.shape) == 3:
            img2_original = self.img2.copy()
        else:
            img2_original = cv2.cvtColor(self.img2, cv2.COLOR_GRAY2BGR)
        
        # 获取灰度图像用于特征提取，确保使用相同的缩放比例
        img1, scale1 = get_image(self.img1)
        img2, scale2 = get_image(self.img2)
        if scale1 != scale2:
            print(f'[Diff-Debug] 缩放比例不同，重新缩放: scale1={scale1}, scale2={scale2}')
            h1, w1 = img1.shape
            img2 = cv2.resize(img2, (w1, h1))
            show_scale = scale1
        else:
            show_scale = scale1
        
        # 获取特征
        img1_feature, img2_feature = get_image_feature(img1, img2)
        line1, line2 = get_line_list(m_diff(img1_feature, img2_feature, equal_obj=LineFeatureEqual()))
        print('line1:', len(line1), 'line2:', len(line2))
        line = line1 + line2
        line = line_filter(line)
        print('line after filter:', len(line))
        
        # 注意力计算
        line = self.calculate_attention(line, img1.shape[0], show_scale)
        
        # 确定底部边界
        if self.ignore_bottom:
            bottom_y = img1.shape[0] - (abs(img2.shape[0]-img1.shape[0])+100)
        else:
            bottom_y = img1.shape[0]
        
        # 检测差异点（主逻辑，像素阈值调低）
        for y in range(int(img1.shape[0] * 0.1), int(bottom_y)):
            if y in line:
                for x in range(img1.shape[1] - 80):
                    p1 = int(get_pixel(img1, x, y))
                    p2 = int(get_pixel(img2, x, y))
                    if abs(p1 - p2) >= 10:
                        points.append([x, y])
        
        # 如果主逻辑没找到任何点，备用全图像素diff
        if len(points) == 0:
            print('[Diff-Debug] 行特征检测未找到差异，使用备用像素比较方法')
            for y in range(0, img1.shape[0], 2):
                for x in range(0, img1.shape[1], 2):
                    p1 = int(get_pixel(img1, x, y))
                    p2 = int(get_pixel(img2, x, y))
                    if abs(p1 - p2) >= 5:
                        points.append([x, y])
        
        print('points before mask:', len(points))
        
        # 应用区域遮罩
        filter_points = ImageDiff.get_mask_with_crop(img1.shape[0], img1.shape[1], img1_original, points, scheme_crops)
        print('filter_points after mask:', len(filter_points))
        
        # 在第一幅图上绘制差异
        if len(filter_points) > 0:
            img1_with_diff = ImageDiff.draw_diff_on_first_image(filter_points, img1_original, diff_color)
        else:
            img1_with_diff = img1_original
        
        # 保存调试信息
        try:
            if img1.shape == img2.shape:
                cv2.imwrite('debug_absdiff.png', cv2.absdiff(img1, img2))
                diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16))
                print('像素diff均值:', diff.mean(), '最大:', diff.max())
            else:
                print(f'[Diff-Debug] 图像尺寸不匹配，跳过absdiff: img1.shape={img1.shape}, img2.shape={img2.shape}')
        except Exception as e:
            print(f'[Diff-Debug] 保存调试信息失败: {e}')
        print('img1.shape:', img1.shape, 'img2.shape:', img2.shape)
        cv2.imwrite('debug_img1.png', img1)
        cv2.imwrite('debug_img2.png', img2)
        return img1_with_diff, len(filter_points)

    @staticmethod
    def _filter_ignore_text(ocr_res, text_crops, img_shape):
        if not text_crops or len(text_crops) <= 0:
            filter_roi_text = ocr_res['roi_text']
        else:
            roi_text_list = ocr_res['roi_text']
            scale = ocr_res['scale']
            filter_roi_text = []
            target_crops = [crop for crop in text_crops if crop['type'] == 'target']
            ignore_crops = [crop for crop in text_crops if crop['type'] == 'ignore']
            in_ignore_area = False
            in_target_area = True
            for roi_text in roi_text_list:
                # 屏蔽区域内忽略
                rect = roi_text['rect']
                rect = ClientHorus.fix_text_rect(rect, scale)
                if len(ignore_crops) > 0:
                    in_ignore_area = False
                    for crop in ignore_crops:
                        if ImageDiff.text_in_crop(rect, crop, img_shape[0], img_shape[1]):
                            in_ignore_area = True
                            break
                if len(target_crops) > 0:
                    in_target_area = False
                    for crop in target_crops:
                        if ImageDiff.text_in_crop(rect, crop, img_shape[0], img_shape[1]):
                            in_target_area = True
                            break
                if in_target_area and not in_ignore_area:
                    filter_roi_text.append(roi_text)

        new_roi_text = []
        for roi_text in filter_roi_text:
            # 过滤掉 超短字符且score值较低
            if len(roi_text['text']) >= 5 or roi_text['score'] >= 0.8:
                new_roi_text.append(roi_text)
        return new_roi_text

    def _ocr_result_distance(self, text_l, text_s, img_shape_l):
        result_diff = []
        result_same = []
        rects = []
        rects_len_diff = []
        h_l = img_shape_l[0]
        for index_l, l in enumerate(text_l):
            l['text'] = process_ch_text(l['text'])
            if l['text'] == '':
                continue
            for index_s, s in enumerate(text_s):
                s['text'] = process_ch_text(s['text'])
                if (l['text'] in s['text'] or s['text'] in l['text']) \
                        and cosine_similarity([l['pos'][0], l['pos'][1]], [s['pos'][0], s['pos'][1]]) > 0.99 \
                        and abs(l['pos'][1] - s['pos'][1]) < int(0.15 * h_l) and s['text'] != '':
                    if len(s['text']) != len(l['text']):
                        # 文本长度存在差异的部分，由后续的行特征元素比较阶段确认
                        rects_len_diff.append(l['rect'])
                    else:
                        result_same.append(s['text'])
                    break
            else:
                result_diff.append(l['text'])
                rects.append(l['rect'])

        if len(text_l) > 0:
            # 针对长图，对score增加一定惩罚系数
            score = round(1.0 - (len(result_diff) / len(text_l)) * (max(h_l, 3000) / 3000), 2)
            if score >= 1:
                rects = rects + rects_len_diff
                # 存在文本缩短使用"in"的方式未检出情况，对此进行修正
                content_l = process_ch_text("".join([text['text'] for text in text_l]))
                size_l = len(content_l)
                content_s = process_ch_text("".join([text['text'] for text in text_s]))
                size_s = len(content_s)
                if abs(size_l - size_s) > 3 or (self.ocr_score_thresh == 1 and size_l != size_s):
                    score = score - round((abs(size_l - size_s) * 1.0) / (400 * max(h_l, 3000) / 3000), 2)
        else:
            # 此时，ocr语义不作为场景结果判断的依据
            score = -1
        return score, rects

    def get_text_distance(self, text_crops=[]):
        image1_result = self.ocr_result['image1_ocr_result']
        image2_result = self.ocr_result['image2_ocr_result']
        r_h1 = len(image1_result['roi_text'])
        r_h2 = len(image2_result['roi_text'])
        img1 = self.img1
        img2 = self.img2
        if r_h1 > r_h2:
            result_l = image1_result
            result_s = image2_result
            img_shape_l = img1.shape
            img_shape_s = img2.shape
        else:
            result_l = image2_result
            result_s = image1_result
            img_shape_l = img2.shape
            img_shape_s = img1.shape
        # ignore text filter
        roi_text_l = self._filter_ignore_text(result_l, text_crops, img_shape_l)
        roi_text_s = self._filter_ignore_text(result_s, text_crops, img_shape_s)
        return self._ocr_result_distance(roi_text_l, roi_text_s, img_shape_l)

    @staticmethod
    def _get_attention(img1, img2):
        img1_list = image_utils.get_image_list(img1)
        img2_list = image_utils.get_image_list(img2)
        l = min(len(img1_list), len(img2_list))
        score_list = []
        for i in range(0, l, 1):
            try:
                start = i - 5 if i - 5 >= 0 else 0
                end = min(i + 5, len(img2_list))  # 确保不超出列表范围
                if start < end:  # 确保有有效的切片
                    img_stack = np.vstack(img2_list[start:end])
                    res = cv2.matchTemplate(img1_list[i], img_stack, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    score_list.append(max_val)
                else:
                    score_list.append(0)
            except Exception as e:
                score_list.append(0)
        return score_list

    def get_similar_score(self, scheme_crops):
        # ocr diff in sub thread
        ocr_score, ocr_rects = self.get_text_distance(scheme_crops)
        self.ocr_result['diff_rects'] = ocr_rects
        img1 = image_utils.get_image_gray(self.img1)
        img2 = image_utils.get_image_gray(self.img2)
        std1 = np.std(img1)
        std2 = np.std(img2)
        img1_list = image_utils.get_image_list(img1)
        img2_list = image_utils.get_image_list(img2)
        l = min(len(img1_list), len(img2_list))
        self.attention = self._get_attention(img1, img2)
        score_list = self.attention.copy()
        score_list.sort()
        print(f"[DEBUG] OCR语义相似度 ocr_score: {ocr_score}")
        print(f"[DEBUG] 行特征相似度 score_list(结构分数): {score_list}")
        
        # 修复IndexError：检查score_list是否为空或太小
        if len(score_list) > 0:
            print(f"[DEBUG] 行特征相似度1位数: {score_list[int(len(score_list) * 0.01) - 1]}")
            print(f"[DEBUG] 行特征相似度5分位: {score_list[int(len(score_list) * 0.05) - 1]}")
        
        # 检查是否有任何行的相似度小于0.98
        if len(score_list) > 0 and min(score_list) < 0.95:
            print(f"[DEBUG] 发现相似度小于0.95的行，最小相似度: {min(score_list)}")
            return 0.2
        
        if len(ocr_rects) > 0 or ocr_score > 0:
            self.ocr_score = ocr_score
            if ocr_score < 0.2 or (len(score_list) > 0 and max(score_list) < 0.2):
                return 0.2
            elif (ocr_score >= self.ocr_score_thresh
                  and len(score_list) > 0 and score_list[int(len(score_list) * 0.01) - 1] > self.struct_score_thresh):
                # 从语义+行特征满足一定阈值
                return 1.0
            else:
                return 0.8
        # ocr_result may get error
        else:
            if (len(score_list) > 0 and score_list[int(len(score_list) * 0.01) - 1] < self.struct_score_thresh) \
                    or max(len(img1_list), len(img2_list)) - l > int(0.5*l) \
                    or abs(std1-std2) > 35:
                return 0.2
            elif len(score_list) > 0 and min(score_list) > 0.99:
                return 1.0
            else:
                return 0.8

    def get_similar_score_info(self, scheme_crops):
        score = self.get_similar_score(scheme_crops)
        score_list = self.attention.copy()
        score_list_h = [score for score in score_list if score > 0.98]
        struct_score = {
            'text': self.ocr_score,
            'attention': round(len(score_list_h) / len(score_list), 2) if len(score_list) > 0 else 0.0
        }
        return struct_score, score


if __name__ == "__main__":
    print(re.match(r'[\u4e00-\u9fa5]+', '美团u'))

