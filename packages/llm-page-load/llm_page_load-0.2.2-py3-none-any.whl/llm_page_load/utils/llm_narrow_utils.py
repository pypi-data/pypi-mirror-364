import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def load_frame_from_npy(segment_dir, frame_idx):
    """
    从npy文件中加载指定帧的图片
    
    Args:
        segment_dir: 视频片段目录
        frame_idx: 帧索引
    
    Returns:
        PIL.Image: 加载的图片，如果加载失败则返回None
    """
    try:
        npy_path = os.path.join(segment_dir, "extracted_frames_sequence.npy")
        if not os.path.exists(npy_path):
            print(f"警告：未找到frames.npy文件: {npy_path}")
            return None
        
        # 动态读取action_info.json获取帧数、shape和dtype
        action_info_path = os.path.join(segment_dir, "action_info.json")
        if not os.path.exists(action_info_path):
            print(f"警告：未找到action_info.json: {action_info_path}")
            return None
        with open(action_info_path, "r", encoding="utf-8") as f:
            action_info = json.load(f)
        num_frames = action_info["extraction_parameters"].get("num_extracted_frames", 750)
        frame_shape = tuple(action_info["extraction_parameters"].get("frame_shape", [2240, 1080, 3]))
        dtype = action_info["extraction_parameters"].get("dtype", "uint8")
        
        frames_memmap = np.memmap(npy_path, dtype=dtype, mode='r', shape=(num_frames,) + frame_shape)

        if frame_idx >= num_frames:
            print(f"警告：帧索引超出范围: {frame_idx} >= {num_frames}")
            return None

        # 获取当前帧
        frame = frames_memmap[frame_idx]
        
        # 确保数据shape一致
        if frame.shape != frame_shape:
            print(f"警告：帧数据格式不正确，期望shape为{frame_shape}，实际为{frame.shape}")
            return None

        # 将numpy数组转换为PIL图片
        return Image.fromarray(frame)
        
    except Exception as e:
        print(f"加载帧时出错: {e}")
        return None

def load_frame_from_directory(frame_dir, frame_idx):
    """
    从指定目录中加载指定帧的图片
    
    Args:
        frame_dir: 帧图片目录路径
        frame_idx: 帧索引
    
    Returns:
        PIL.Image: 加载的图片，如果加载失败则返回None
    """
    try:
        if not frame_dir or not os.path.exists(frame_dir):
            print(f"警告：帧目录不存在: {frame_dir}")
            return None
        
        # 尝试多种可能的文件名格式
        possible_filenames = [
            f"{frame_idx:04d}.png",
            f"{frame_idx:04d}.jpg",
            f"{frame_idx:04d}.jpeg",
            f"frame_{frame_idx:04d}.png",
            f"frame_{frame_idx:04d}.jpg",
            f"frame_{frame_idx:04d}.jpeg",
            f"{frame_idx}.png",
            f"{frame_idx}.jpg",
            f"{frame_idx}.jpeg",
            f"frame_{frame_idx}.png",
            f"frame_{frame_idx}.jpg",
            f"frame_{frame_idx}.jpeg"
        ]
        
        for filename in possible_filenames:
            frame_path = os.path.join(frame_dir, filename)
            if os.path.exists(frame_path):
                print(f"从目录加载帧 {frame_idx}: {frame_path}")
                return Image.open(frame_path)
        
        print(f"警告：在目录 {frame_dir} 中未找到帧 {frame_idx} 的图片文件")
        return None
        
    except Exception as e:
        print(f"从目录加载帧时出错: {e}")
        return None

def load_frame(segment_dir, frame_idx, frame_dir=None):
    """
    加载指定帧的图片，支持从npy文件或指定目录加载
    
    Args:
        segment_dir: 视频片段目录
        frame_idx: 帧索引
        frame_dir: 帧图片目录路径，如果为None则从npy文件加载
    
    Returns:
        PIL.Image: 加载的图片，如果加载失败则返回None
    """
    if frame_dir is not None:
        return load_frame_from_directory(frame_dir, frame_idx)
    else:
        return load_frame_from_npy(segment_dir, frame_idx)

def save_candidate_frames(segment_dir, frame_indices, output_dir="candidate_frames", prefix="frame"):
    """
    保存候选帧图片到指定目录
    
    Args:
        segment_dir: 视频片段目录
        frame_indices: 帧索引列表
        output_dir: 输出目录
        prefix: 文件名前缀
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个候选帧
    for idx in frame_indices:
        img = load_frame_from_npy(segment_dir, idx)
        if img:
            # 构建输出文件名
            output_path = os.path.join(output_dir, f"{prefix}_{idx:04d}.png")
            img.save(output_path)
            print(f"已保存帧 {idx} 到 {output_path}")

def create_image_grid(images, grid_size=None, target_size=(2048, 2048), enhance_images=False):
    """
    将所有图片拼接成一个网格，保持图片原始比例
    
    Args:
        images: 图片列表，每个元素是(idx, path, PIL.Image)
        grid_size: 网格大小，如果为None则自动计算
        target_size: 目标图片大小
        enhance_images: 是否增强图像，默认False
    
    Returns:
        PIL.Image: 拼接后的图片
    """
    if not images:
        return None
        
    # 如果没有指定grid_size，自动计算
    if grid_size is None:
        num_images = len(images)
        cols = min(3, num_images)  # 最多3列，让图片更大更清晰
        rows = (num_images + cols - 1) // cols
        grid_size = (rows, cols)
    
    # 设置间隔和边框
    padding = 40  # 图片之间的间隔
    border = 3    # 图片边框宽度
    
    # 计算每个单元格的大小（考虑间隔和边框）
    cell_width = (target_size[0] - (grid_size[1] - 1) * padding) // grid_size[1]
    cell_height = (target_size[1] - (grid_size[0] - 1) * padding) // grid_size[0]
    
    # 创建空白画布（白色背景）
    grid_image = Image.new('RGB', target_size, (255, 255, 255))
    
    # 创建边框颜色（浅灰色）
    border_color = (200, 200, 200)
    
    for idx, (frame_idx, _, img) in enumerate(images):
        if idx >= grid_size[0] * grid_size[1]:
            break
            
        # 如果启用图像增强，只进行rembg抠图，不进行RealESRGAN增强
        if enhance_images:
            print(f"  [Grid-Background-Removal] 开始移除网格图片 {frame_idx} 的背景")
            
            # 创建临时目录用于图像处理
            import os
            temp_dir = os.path.join("temp_rembg_grid")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 保存原始图像
            original_path = os.path.join(temp_dir, f"grid_frame_{frame_idx}_original.png")
            img.save(original_path)
            
            # 使用rembg移除背景，提取手机部分
            print(f"  [Grid-Background-Removal] 使用rembg移除背景")
            from src.utils.llm_narrow_core import remove_background_with_rembg
            removed_bg_path = remove_background_with_rembg(original_path)
            
            if removed_bg_path != original_path and os.path.exists(removed_bg_path):
                # 加载抠图后的图像
                removed_bg_img = Image.open(removed_bg_path)
                print(f"  [Grid-Background-Removal] 背景移除成功，新尺寸: {removed_bg_img.size}")
                img = removed_bg_img
            else:
                print(f"  [Grid-Background-Removal] rembg抠图失败或跳过，使用原始图像")
            
        # 计算位置（考虑间隔）
        row = idx // grid_size[1]
        col = idx % grid_size[1]
        x = col * (cell_width + padding)
        y = row * (cell_height + padding)
        
        # 计算保持原始比例的图片大小
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        
        # 计算在单元格内保持比例的最大尺寸
        if aspect_ratio > 1:  # 宽图
            new_width = cell_width - 2*border
            new_height = int(new_width / aspect_ratio)
        else:  # 高图
            new_height = cell_height - 2*border
            new_width = int(new_height * aspect_ratio)
        
        # 调整图片大小，使用高质量的LANCZOS重采样
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建带边框的图片（居中放置）
        bordered_img = Image.new('RGB', (cell_width, cell_height), border_color)
        paste_x = (cell_width - new_width) // 2
        paste_y = (cell_height - new_height) // 2
        bordered_img.paste(img, (paste_x, paste_y))
        
        # 粘贴图片
        grid_image.paste(bordered_img, (x, y))
    
    # 在图片顶部添加说明文字
    draw = ImageDraw.Draw(grid_image)
    # 动态设置字体大小，随cell高度自适应
    font_size = max(16, int(cell_height * 0.09))  # 9%高度，最小16
    try:
        font = ImageFont.truetype("Arial", font_size)
    except:
        font = ImageFont.load_default()
    # 添加说明文字
    text = f"Total frames: {len(images)}"
    text_width = draw.textlength(text, font=font)
    text_x = (target_size[0] - text_width) // 2
    draw.text((text_x, 20), text, fill=(0, 0, 0), font=font)
    

    
    return grid_image

def get_candidate_frames_for_start(ssim_sequence, smoothed_ssim, slopes, activity_threshold=-0.001, merge_window=3, start_threshold=-0.0001):
    """
    获取开始帧的候选帧
    1. 找出所有活动点（斜率小于activity_threshold的点）
    2. 递归合并merge_window帧之内的活动点，只保留最早的点
    3. 对每个活动点，向左找到第一个不明显下降的点作为开始点
    4. 如果多个活动点对应同一个开始点，只保留第一个活动点
    
    Args:
        ssim_sequence: 原始SSIM序列
        smoothed_ssim: 平滑后的SSIM序列
        slopes: SSIM序列的斜率
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        start_threshold: 开始点阈值，默认-0.0001
    
    Returns:
        tuple: (候选帧列表, 开始点字典) 候选帧是活动点，开始点字典记录每个活动点对应的开始点
    """
    # 1. 找出所有活动点
    activity_points = []
    for i in range(len(slopes)-1):
        if slopes[i] < activity_threshold:
            activity_points.append(i)
    
    # 2. 递归合并活动点
    def merge_nearby_points(points, window=merge_window):
        if not points:
            return []
        
        points = sorted(points)
        merged = []
        current_group = [points[0]]
        
        for i in range(1, len(points)):
            if points[i] - current_group[-1] <= window:
                current_group.append(points[i])
            else:
                merged.append(current_group[0])
                current_group = [points[i]]
        
        if current_group:
            merged.append(current_group[0])
        
        return merged
    
    merged_activity_points = merge_nearby_points(activity_points)
    print("\n合并后的活动点列表:", merged_activity_points)
    
    # 3. 对每个活动点，向左找到第一个不明显下降的点作为开始点
    start_points = {}
    for activity_point in merged_activity_points:
        start_point = activity_point
        while start_point > 0:
            if slopes[start_point] >= start_threshold:
                break
            start_point -= 1
        
        if start_point not in start_points or activity_point < start_points[start_point]:
            start_points[start_point] = activity_point
    
    # 4. 整理结果
    valley_frames = []
    start_point_map = {}
    for start_point, activity_point in sorted(start_points.items()):
        valley_frames.append(activity_point)
        start_point_map[activity_point] = start_point
    
    return valley_frames, start_point_map

def get_candidate_frames_for_end(ssim_sequence, smoothed_ssim, slopes, start_frame, activity_threshold=-0.001, merge_window=3, end_threshold=-0.00003):
    """
    获取结束帧的候选帧
    1. 找出开始帧之后的所有活动点（斜率小于activity_threshold的点）
    2. 递归合并merge_window帧之内的活动点，只保留最后的点
    3. 对每个活动点，向右找到第一个不明显下降的点作为结束点
    4. 如果多个活动点对应同一个结束点，只保留最后一个结束点
    
    Args:
        ssim_sequence: 原始SSIM序列
        smoothed_ssim: 平滑后的SSIM序列
        slopes: SSIM序列的斜率
        start_frame: 开始帧
        activity_threshold: 活动阈值，默认-0.001
        merge_window: 合并窗口大小，默认3
        end_threshold: 结束点阈值，默认-0.0001
    
    Returns:
        list: 候选帧列表（结束点）
    """
    # 1. 找出开始帧之后的所有活动点
    activity_points = []
    for i in range(start_frame + 1, len(slopes)-1):
        if slopes[i] < activity_threshold:
            activity_points.append(i)
    
    print("\n初始活动点列表:", activity_points)
    
    # 2. 递归合并活动点
    def merge_nearby_points(points, window=merge_window):
        if not points:
            return []
        
        points = sorted(points)
        merged = []
        current_group = [points[0]]
        
        for i in range(1, len(points)):
            if points[i] - current_group[-1] <= window:
                current_group.append(points[i])
            else:
                merged.append(current_group[-1])
                current_group = [points[i]]
        
        if current_group:
            merged.append(current_group[-1])
        
        return merged
    
    merged_activity_points = merge_nearby_points(activity_points)
    print("\n合并后的活动点列表:", merged_activity_points)
    
    # 3. 对每个活动点，向右找到第一个不明显下降的点作为结束点
    end_points = set()
    for activity_point in merged_activity_points:
        end_point = activity_point
        while end_point < len(slopes) - 1:
            if slopes[end_point] >= end_threshold:
                break
            end_point += 1
        
        end_points.add(end_point)
    
    # 4. 整理结果
    candidate_frames = sorted(list(end_points))
    print("\n最终选定的候选帧:", candidate_frames)
    
    return candidate_frames

def estimate_tokens(text: str) -> int:
    """粗略估计文本的token数量"""
    # 英文单词平均4个字符，中文平均2个字符
    # 这是一个非常粗略的估计，后续修改
    return len(text) // 2 