import cv2
import numpy as np
import os
import math

def get_line_intersection(line1, line2):
    """计算两条无限延长线的交点。"""
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    
    ix = x1 + t * (x2 - x1)
    iy = y1 + t * (y2 - y1)
    
    return (int(ix), int(iy))

def extract_phone_screen(image_path, output_path="output.jpg", debug=False):
    """
    一个能同时处理有无遮挡情况的、鲁棒的手机屏幕提取函数。
    它聚焦于识别蓝色背景的边缘，并复原被遮挡的手机轮廓。

    :param image_path: 输入图片的路径
    :param output_path: 处理后图片的保存路径
    :param debug: 是否启用调试模式
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误: 无法读取图片 {image_path}")
        return

    # 1. 识别蓝色背景
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    background_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 如果启用了调试模式，则准备调试图像
    if debug:
        debug_image = image.copy()
        blue_overlay = np.zeros_like(image, np.uint8)
        blue_overlay[background_mask == 255] = (255, 100, 0) # BGR for a shade of Blue
        cv2.addWeighted(blue_overlay, 0.4, debug_image, 0.6, 0, debug_image)

    # 2. 在背景的边缘上寻找直线
    edges = cv2.Canny(background_mask, 50, 150)
    
    h, w = image.shape[:2]
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=w/8, maxLineGap=w/15)

    if lines is None:
        print("错误: 未能在背景边缘上检测到足够长的直线。")
        return

    # 3. 直线过滤与分类
    horizontal_lines = []
    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if debug:
            # 在调试图上用黄色画出所有检测到的直线
            cv2.line(debug_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
        angle = abs(math.degrees(math.atan2(y2 - y1, x2 - x1)))
        if angle < 45 or angle > 135:
            horizontal_lines.append(line[0])
        elif 45 <= angle <= 135:
            vertical_lines.append(line[0])

    if not horizontal_lines or not vertical_lines:
        print("错误：未能稳健地识别出手机的横向和纵向边缘。")
        return

    # 4. 智能筛选四条边界线
    top_candidates = [l for l in horizontal_lines if ((l[1] + l[3]) / 2) < h / 2]
    top_edge = min(top_candidates, key=lambda line: (line[1] + line[3]) / 2) if top_candidates else min(horizontal_lines, key=lambda line: (line[1] + line[3]) / 2)
    
    bottom_candidates = [l for l in horizontal_lines if ((l[1] + l[3]) / 2) > h / 2]
    bottom_edge = max(bottom_candidates, key=lambda line: (line[1] + line[3]) / 2) if bottom_candidates else max(horizontal_lines, key=lambda line: (line[1] + line[3]) / 2)
    
    left_candidates = [l for l in vertical_lines if ((l[0] + l[2]) / 2) < w / 2]
    left_edge = min(left_candidates, key=lambda line: (line[0] + line[2]) / 2) if left_candidates else min(vertical_lines, key=lambda line: (line[0] + line[2]) / 2)
    
    right_candidates = [l for l in vertical_lines if ((l[0] + l[2]) / 2) > w / 2]
    right_edge = max(right_candidates, key=lambda line: (line[0] + line[2]) / 2) if right_candidates else max(vertical_lines, key=lambda line: (line[0] + line[2]) / 2)
    
    if debug:
        # 在调试图上用白色画出选定的4条边界线
        for line_coords in [top_edge, bottom_edge, left_edge, right_edge]:
            cv2.line(debug_image, (line_coords[0], line_coords[1]), (line_coords[2], line_coords[3]), (255, 255, 255), 3)

    # 5. 计算边界线的交点以获得角点
    tl = get_line_intersection(top_edge, left_edge)
    tr = get_line_intersection(top_edge, right_edge)
    bl = get_line_intersection(bottom_edge, left_edge)
    br = get_line_intersection(bottom_edge, right_edge)

    if any(p is None for p in [tl, tr, bl, br]):
         print("警告: 无法计算所有四个角点。")
         return
    else:
        screen_contour = np.array([tl, tr, br, bl], dtype="int32")

    if debug:
        # 在调试图上用绿色画出最终的屏幕轮廓并保存
        cv2.drawContours(debug_image, [screen_contour], -1, (0, 255, 0), 3)
        debug_output_path = os.path.splitext(output_path)[0] + "_debug.jpg"
        cv2.imwrite(debug_output_path, debug_image)
        print(f"调试图像已保存到 {debug_output_path}")

    # 6. 精确排序与裁剪
    pts = screen_contour.reshape(4, 2)
    rect_pts = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect_pts[0] = pts[np.argmin(s)]  # Top-left
    rect_pts[2] = pts[np.argmax(s)]  # Bottom-right

    diff = np.diff(pts, axis=1)
    rect_pts[1] = pts[np.argmin(diff)]  # Top-right
    rect_pts[3] = pts[np.argmax(diff)]  # Bottom-left
    
    src_pts = rect_pts.astype("float32")

    (tl, tr, br, bl) = src_pts
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst_pts = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    cv2.imwrite(output_path, warped)
    print(f"处理完成，结果已保存到 {output_path}")

if __name__ == '__main__':
    # 控制是否生成调试图像
    DEBUG_MODE = True

    # 同时处理有手和无手两种情况，以验证方案的鲁棒性
    test_cases = {
        'frame_0148.jpeg': 'screen_output_0148.jpg',  # 无手
        'frame_0025.jpeg': 'screen_output_0025.jpg',
        'frame_0090.jpeg': 'screen_output_0090.jpg'
    }

    for input_file, output_file in test_cases.items():
        input_path = os.path.join('data', input_file)
        print(f"\n--- 正在处理: {input_path} ---")
        extract_phone_screen(input_path, output_file, debug=DEBUG_MODE)
        