import cv2
import numpy as np
from scipy.stats import pearsonr

def cal_image_similarity(image1, image2):
    """从 结构 / 颜色 计算两张图像的整体相似度

    Args:
        image1 (opencv image): 图1
        image2 (_type_): 图2

    Returns:
        structural_similarity: 结构相似性
        color_similarity: 颜色相似性
    """
    structural_similarity = get_similar_score(image1, image2)
    color_similarity = compare_images_withRGBHist(image1, image2)
    return structural_similarity, color_similarity

# color_histogram similarity
def calculate_histogram(image, bins=256):
    """计算RGB直方图"""
    hist = [cv2.calcHist([image], [i], None, [bins], [0, 256]) for i in range(3)]
    hist = np.concatenate(hist)
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def compare_images_withRGBHist(image1_pth, image2_pth):
    """比较两张图片"""
    # 读取图片
    image1 = cv2.imread(image1_pth) if isinstance(image1_pth, str) else image1_pth
    image2 = cv2.imread(image2_pth) if isinstance(image2_pth, str) else image2_pth
    # 调整图片大小
    image1 = cv2.resize(image1, (256, 256))
    image2 = cv2.resize(image2, (256, 256))
    # 计算RGB直方图
    hist1 = calculate_histogram(image1)
    hist2 = calculate_histogram(image2)
    # 计算颜色相似度
    similarity, _ = pearsonr(hist1, hist2)
    similarity = (similarity + 1) / 2  # 将-1到1映射到0到1
    return similarity

# hash similarity
def get_similar_score(image1, image2, offset_y_percent=0.078, area=None):
    img1 = get_image_gray(image1, offset_y_percent, area)
    img2 = get_image_gray(image2, offset_y_percent, area)
    hash1 = perception_hash(img1)
    hash2 = perception_hash(img2)
    return 1-hamming_dist(hash1, hash2)*1.0 / (64*64)

def get_image_gray(img_file, offset_y_percent=0.078, area=None):
    img = cv2.imread(img_file) if isinstance(img_file, str) else img_file
    h, w, _ = img.shape
    if area:
        x1, y1, x2, y2 = area
        img = img[max(0, y1):min(h, y2), max(0, x1):min(w, x2), :]
    if area is None and offset_y_percent > 0:
        img = img[int(w * offset_y_percent):, :, :]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

def perception_hash(img_gray, precision=64):
    img_scale = cv2.resize(img_gray, (precision, precision))
    img_list = img_scale.flatten()
    avg = sum(img_list)*1./len(img_list)
    avg_list = ['0' if i < avg else '1' for i in img_list]
    return [int(''.join(avg_list[x:x+4]), 2) for x in range(0, precision*precision)]

def hamming_dist(s1, s2):
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])
