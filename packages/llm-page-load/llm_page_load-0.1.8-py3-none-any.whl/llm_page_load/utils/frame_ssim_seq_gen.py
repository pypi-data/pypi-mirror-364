from typing import List, Optional, Sequence, Union, Tuple, Dict
import numpy as np
from skimage.metrics import structural_similarity
from skimage.color import rgb2gray
import multiprocessing
import os # For os.cpu_count()
import matplotlib.pyplot as plt # type: ignore # matplotlib is used in plot_temporal_ssim_vectors
from tqdm import tqdm

# 检查 scikit-image 版本
try:
    from skimage import __version__ as skimage_version
    SKIMAGE_SUPPORTS_CHANNEL_AXIS = tuple(map(int, skimage_version.split('.')[:2])) >= (0, 19)
except ImportError:
    SKIMAGE_SUPPORTS_CHANNEL_AXIS = False

# plot_temporal_ssim_vectors 函数 (保持不变，为了完整性粘贴于此)
# ... (您的 plot_temporal_ssim_vectors 函数代码) ...
# --- 全局变量，用于工作进程 (通过 initializer 设置) ---
_WORKER_FRAMES_SEQ: Optional[Sequence[np.ndarray]] = None
_WORKER_CONVERT_TO_GRAY: bool = False
# _WORKER_ORIGINAL_MAX_VAL_FOR_SCALING: Optional[float] = None # 新的全局变量含义
_WORKER_ORIGINAL_SCALE_FACTOR: Optional[float] = None # 用于存储原始数据的最大值或覆盖值
_WORKER_SKIMAGE_SUPPORTS_CHANNEL_AXIS: bool = False


def _init_worker(
    frames_seq_data: Sequence[np.ndarray],
    convert_to_gray_data: bool,
    # data_range_override_data is now interpreted as original_max_val_for_scaling
    original_max_val_for_scaling_data: Optional[float],
    skimage_supports_channel_axis_data: bool
) -> None:
    """每个工作进程的初始化函数。"""
    global _WORKER_FRAMES_SEQ, _WORKER_CONVERT_TO_GRAY, _WORKER_ORIGINAL_SCALE_FACTOR
    global _WORKER_SKIMAGE_SUPPORTS_CHANNEL_AXIS

    _WORKER_FRAMES_SEQ = frames_seq_data
    _WORKER_CONVERT_TO_GRAY = convert_to_gray_data
    _WORKER_ORIGINAL_SCALE_FACTOR = original_max_val_for_scaling_data # 存储这个值
    _WORKER_SKIMAGE_SUPPORTS_CHANNEL_AXIS = skimage_supports_channel_axis_data

def _get_processed_frame_for_worker(idx: int) -> Tuple[np.ndarray, float, bool]: # 返回处理后的帧, data_range (将是1.0), is_color
    """
    由工作进程调用，获取并按需处理帧。
    所有输出帧都将被缩放到 [0,1]范围，并转换为 np.float32 类型。
    data_range 将始终为 1.0。
    """
    assert _WORKER_FRAMES_SEQ is not None, f"Worker {os.getpid()}: _WORKER_FRAMES_SEQ 未初始化!"
    original_frame: np.ndarray = _WORKER_FRAMES_SEQ[idx]

    processed_frame: np.ndarray
    is_color_after_processing: bool

    # 1. 确定原始数据的最大理论值 (用于缩放)
    # original_max_val_for_scaling: float
    # if _WORKER_ORIGINAL_SCALE_FACTOR is not None:
    #     original_max_val_for_scaling = _WORKER_ORIGINAL_SCALE_FACTOR
    # else: # 推断
    #     if original_frame.dtype == np.uint8:
    #         original_max_val_for_scaling = 255.0
    #     elif np.issubdtype(original_frame.dtype, np.integer):
    #         original_max_val_for_scaling = float(np.iinfo(original_frame.dtype).max)
    #     elif np.issubdtype(original_frame.dtype, np.floating):
    #         # 对于浮点数，如果没有override，我们假设它已经是[0,1]或者用户应该提供override
    #         # 为了与GPU版本在未知浮点范围时的行为（默认1.0并警告）保持部分一致，这里也设为1.0
    #         # 但更好的做法是要求用户为非标准浮点范围提供override
    #         min_val_check, max_val_check = original_frame.min(), original_frame.max()
    #         if min_val_check >= -1e-5 and max_val_check <= 1.0 + 1e-5:
    #              original_max_val_for_scaling = 1.0
    #         elif min_val_check >= -1e-5 and max_val_check <= 255.0 + 1e-5 and max_val_check > 1.0 + 1e-5 : # 近似 [0,255] 的浮点数
    #              original_max_val_for_scaling = 255.0
    #         else:
    #              # print(f"警告 (Worker {os.getpid()}): 帧 {idx} 是浮点类型，但其范围 [{min_val_check:.2f}, {max_val_check:.2f}] 未知。"
    #              #      "假设其最大值为 1.0 进行缩放。为确保准确性，请考虑使用 data_range_override。")
    #              original_max_val_for_scaling = 1.0 # 与GPU版本一致的默认行为
    #     else:
    #         raise TypeError(f"帧 {idx} 的数据类型 {original_frame.dtype} 不支持自动推断缩放因子。请使用 data_range_override。")

    # 2. 类型转换和灰度转换
    #    目标：processed_frame 为 np.float32 类型
    current_frame_for_processing = original_frame.copy()

    if _WORKER_CONVERT_TO_GRAY:
        if current_frame_for_processing.ndim == 3 and current_frame_for_processing.shape[-1] in (3, 4):
            # rgb2gray 输出 float64 [0,1]
            processed_frame = rgb2gray(current_frame_for_processing).astype(np.float32)
        elif current_frame_for_processing.ndim == 2:
            # 已经是灰度图，但需要确保是 float32 [0,1]
            # 首先确定原始最大值（如果不是从rgb2gray来的）
            scale_factor_gray: float
            if _WORKER_ORIGINAL_SCALE_FACTOR is not None:
                 scale_factor_gray = _WORKER_ORIGINAL_SCALE_FACTOR
            elif np.issubdtype(current_frame_for_processing.dtype, np.integer):
                 scale_factor_gray = float(np.iinfo(current_frame_for_processing.dtype).max)
            elif np.issubdtype(current_frame_for_processing.dtype, np.floating): # 已经是浮点灰度
                min_v, max_v = current_frame_for_processing.min(), current_frame_for_processing.max()
                if min_v >= -1e-5 and max_v <= 1.0 + 1e-5:
                    scale_factor_gray = 1.0
                elif min_v >= -1e-5 and max_v <= 255.0 + 1e-5 and max_v > 1.0 + 1e-5:
                    scale_factor_gray = 255.0
                else: # 未知范围的浮点灰度图
                    # print(f"警告 (Worker {os.getpid()}): 帧 {idx} 是浮点灰度图，但范围 [{min_v:.2f}, {max_v:.2f}] 未知。"
                    #       "假设其最大值为 1.0 进行缩放。请考虑使用 data_range_override。")
                    scale_factor_gray = 1.0 # 默认
            else: # 其他类型
                 scale_factor_gray = 1.0 # 无法推断，默认1.0
            
            if scale_factor_gray <= 1e-6: scale_factor_gray = 1.0 #避免除零

            processed_frame = (current_frame_for_processing.astype(np.float32) / scale_factor_gray)

        else: # 不支持的维度进行灰度转换
            raise ValueError(f"帧 {idx} (形状 {current_frame_for_processing.shape}) 不支持灰度转换。")
        is_color_after_processing = False
    else: # 不进行灰度转换 (保持彩色或原始灰度)
        # 确定原始最大值
        scale_factor_color_or_original_gray: float
        if _WORKER_ORIGINAL_SCALE_FACTOR is not None:
            scale_factor_color_or_original_gray = _WORKER_ORIGINAL_SCALE_FACTOR
        elif original_frame.dtype == np.uint8: # uint8 -> 255
            scale_factor_color_or_original_gray = 255.0
        elif np.issubdtype(original_frame.dtype, np.integer): # e.g. uint16
            scale_factor_color_or_original_gray = float(np.iinfo(original_frame.dtype).max)
        elif np.issubdtype(original_frame.dtype, np.floating):
            min_v, max_v = original_frame.min(), original_frame.max()
            if min_v >= -1e-5 and max_v <= 1.0 + 1e-5: # approx [0,1]
                scale_factor_color_or_original_gray = 1.0
            elif min_v >= -1e-5 and max_v <= 255.0 + 1e-5 and max_v > 1.0 + 1e-5: # approx [0,255] float
                scale_factor_color_or_original_gray = 255.0
            else: # unknown float scale
                # print(f"警告 (Worker {os.getpid()}): 帧 {idx} 是浮点类型，不转灰度，但范围 [{min_v:.2f}, {max_v:.2f}] 未知。"
                #       "假设其最大值为 1.0 进行缩放。请考虑使用 data_range_override。")
                scale_factor_color_or_original_gray = 1.0 # Default assumption
        else:
            raise TypeError(f"帧 {idx} 数据类型 {original_frame.dtype} 不支持自动推断缩放因子。")

        if scale_factor_color_or_original_gray <= 1e-6: scale_factor_color_or_original_gray = 1.0

        processed_frame = (current_frame_for_processing.astype(np.float32) / scale_factor_color_or_original_gray)
        is_color_after_processing = processed_frame.ndim == 3 and processed_frame.shape[-1] in (3,4)


    # 3. 裁剪到 [0,1]
    processed_frame = np.clip(processed_frame, 0.0, 1.0)

    # 4. data_range 对于处理后的帧始终为 1.0
    final_data_range_for_ssim = 1.0

    return processed_frame, final_data_range_for_ssim, is_color_after_processing


def _calculate_single_ssim_task(task_args: Tuple[int, int, int, Optional[int]]) -> Tuple[int, int, Optional[float]]:
    """工作函数，为单对帧计算SSIM。"""
    t_idx, prev_idx, offset_val, win_size_val = task_args
    
    try:
        # _get_processed_frame_for_worker 现在返回 (frame_arr, data_range=1.0, is_color)
        frame_t_arr, dr_t, is_color_t = _get_processed_frame_for_worker(t_idx)
        frame_prev_arr, dr_prev, _ = _get_processed_frame_for_worker(prev_idx) # is_color_prev not directly used for params

        # dr_t 和 dr_prev 现在应该总是1.0，所以不需要检查它们是否一致

        effective_win_size = win_size_val
        # win_size 校验 (应在主函数中进行更严格的校验，这里仅作运行时保护)
        if win_size_val is not None:
            if win_size_val <= 0 or win_size_val % 2 == 0:
                 # print(f"警告 (Worker {os.getpid()}): 无效的 win_size ({win_size_val})。将尝试让 skimage 处理或使用默认值。")
                 effective_win_size = None # 或者可以返回None，但主函数应先校验
            else:
                min_dim_t = min(frame_t_arr.shape[0], frame_t_arr.shape[1])
                min_dim_prev = min(frame_prev_arr.shape[0], frame_prev_arr.shape[1])
                min_overall_dim = min(min_dim_t, min_dim_prev)
                if win_size_val > min_overall_dim:
                    # print(f"警告 (Worker {os.getpid()}): win_size ({win_size_val}) 大于图像最小维度 ({min_overall_dim})。将使用 skimage 默认窗口。")
                    effective_win_size = None # 让 skimage 决定，或如果其默认值不合适则可能报错
        
        ssim_params: Dict[str, Union[int, float, bool, None, str]] = {
            'win_size': effective_win_size,
            'data_range': dr_t, # 这将是 1.0
            'gaussian_weights': True,
            # 'sigma': 1.5, # 可以考虑固定sigma，但需要与piqa行为对比
            # 'use_sample_covariance': False, # skimage 默认
            # 'K1': 0.01, 'K2': 0.03 # skimage 默认
        }

        if is_color_t: # is_color_t 来自处理后的 frame_t_arr
            if _WORKER_SKIMAGE_SUPPORTS_CHANNEL_AXIS:
                ssim_params['channel_axis'] = -1
            else:
                ssim_params['multichannel'] = True # type: ignore
        
        # 确保输入是 float32 (虽然 _get_processed_frame_for_worker 应该已经处理了)
        # skimage 的 SSIM 对 float32 和 float64 的处理可能略有不同，但通常兼容
        # frame_t_arr = frame_t_arr.astype(np.float32, copy=False) # copy=False 如果已经是float32
        # frame_prev_arr = frame_prev_arr.astype(np.float32, copy=False)

        score = structural_similarity(frame_t_arr, frame_prev_arr, **ssim_params) # type: ignore
        
        # SSIM理论上在[-1,1]，但由于数值精度可能略超出，统一钳位
        score = np.clip(score, -1.0, 1.0)

        return (t_idx, offset_val, score)

    except Exception as e:
        # print(f"错误 (Worker {os.getpid()}): 计算帧 {t_idx} 与帧 {prev_idx} (偏移 {offset_val}) 的 SSIM 时: {e}")
        # import traceback
        # traceback.print_exc()
        return (t_idx, offset_val, None)


def calculate_temporal_ssim_vectors_mp(
    frames: Sequence[np.ndarray],
    offsets: List[int],
    convert_to_gray: bool = False,
    win_size: Optional[int] = 7, # skimage的SSIM可以接受None作为win_size
    data_range_override: Optional[float] = None, # 现在表示原始数据的最大值，用于缩放
    num_workers: Optional[int] = None
) -> List[List[Optional[float]]]:
    if not frames:
        print("输入帧序列为空。")
        return []
    if not isinstance(frames[0], np.ndarray): # 基本检查
        raise TypeError("输入帧序列中的元素必须是 NumPy 数组。")

    if not offsets:
        print("警告: 未提供 offsets 列表。将为每帧返回空的 SSIM 向量。")
        return [[] for _ in frames] # 为每个输入帧返回一个空列表
    
    # 过滤无效offsets，并排序去重
    valid_offsets = sorted(list(set(o for o in offsets if o > 0)))
    if not valid_offsets:
        if offsets: # 如果原始列表不为空但全无效
             print("警告: offsets 列表中所有值均为非正数或无效，过滤后没有有效的 offsets。")
        # 返回与GPU版本一致的结构：一个包含num_frames个空列表的列表，因为没有有效的offset维度
        return [[] for _ in frames]


    if any(o <=0 for o in offsets) and valid_offsets:
         print("警告: offsets 列表中包含非正数值，这些值将被忽略。")

    # win_size 校验
    if win_size is not None and (win_size <= 0 or win_size % 2 == 0):
        raise ValueError(f"win_size ({win_size}) 必须是正奇数。如果想使用scikit-image的默认窗口，请传入 None。")


    sorted_unique_offsets = valid_offsets # 重命名以明确
    num_frames_total = len(frames)
    offset_to_index_map = {offset_val: i for i, offset_val in enumerate(sorted_unique_offsets)}
    
    tasks_to_process: List[Tuple[int, int, int, Optional[int]]] = []
    # 初始化all_ssim_vectors，使其维度与(num_frames, num_valid_offsets)一致
    all_ssim_vectors: List[List[Optional[float]]] = [[None for _ in sorted_unique_offsets] for _ in range(num_frames_total)]


    for t in range(num_frames_total):
        for offset_val in sorted_unique_offsets:
            prev_frame_idx = t - offset_val
            if prev_frame_idx >= 0:
                tasks_to_process.append((t, prev_frame_idx, offset_val, win_size))

    if not tasks_to_process:
        print("根据 offsets，没有有效的帧对可以进行比较。")
        return all_ssim_vectors # 返回已初始化的 None 填充列表

    # --- 推断/设置 original_max_val_for_scaling ---
    # 这个值将传递给工作进程的初始化函数
    # _WORKER_ORIGINAL_SCALE_FACTOR 将基于此设置
    effective_original_max_val: Optional[float]
    if data_range_override is not None:
        if data_range_override <= 0:
            raise ValueError("data_range_override (用于表示原始数据最大值) 必须是正数。")
        effective_original_max_val = data_range_override
        # print(f"使用 data_range_override: {effective_original_max_val} 作为原始数据缩放基准。")
    else: # 推断
        first_frame = frames[0]
        if first_frame.dtype == np.uint8:
            effective_original_max_val = 255.0
        elif np.issubdtype(first_frame.dtype, np.integer): # e.g. uint16
            effective_original_max_val = float(np.iinfo(first_frame.dtype).max)
        elif np.issubdtype(first_frame.dtype, np.floating):
            min_val, max_val = first_frame.min(), first_frame.max()
            if min_val >= -1e-5 and max_val <= 1.0 + 1e-5:
                effective_original_max_val = 1.0
            elif min_val >= -1e-5 and max_val <= 255.0 + 1e-5 and max_val > 1.0 + 1e-5 :
                effective_original_max_val = 255.0
            else:
                # print(f"警告: 无法从第一个浮点帧 (范围 [{min_val:.2f}, {max_val:.2f}]) 安全推断其原始比例。"
                #       "假设其最大值为 1.0 进行缩放。为确保准确性，请明确使用 data_range_override。")
                effective_original_max_val = 1.0 # 与GPU版本一致的默认行为
        else:
            raise TypeError(
                f"主函数错误: 帧的数据类型 {first_frame.dtype} 不支持自动推断原始数据最大值。"
                "请使用 'data_range_override' 参数。"
            )
        # print(f"从帧数据推断的原始数据缩放基准为: {effective_original_max_val}")


    skimage_supports_channel_axis_main = SKIMAGE_SUPPORTS_CHANNEL_AXIS # 使用全局检查的结果

    cpu_cores = os.cpu_count() or 1
    actual_num_workers: int
    if num_workers is None or num_workers <= 0:
        if cpu_cores <= 2: actual_num_workers = 1 # 对于1或2核，只用1个worker
        elif cpu_cores <= 4: actual_num_workers = cpu_cores - 1
        elif cpu_cores <= 16: actual_num_workers = cpu_cores - 2 # 稍微多留一些给系统
        else: actual_num_workers = min(cpu_cores - 2, 32) # 上限，并为超多核机器留余地
        actual_num_workers = max(1, actual_num_workers)
        # print(f"num_workers 未指定或无效，自动调整为: {actual_num_workers} (可用CPU核心数: {cpu_cores})")
    else:
        actual_num_workers = num_workers
        if actual_num_workers > cpu_cores:
             print(f"警告: 请求的 num_workers ({actual_num_workers}) 大于CPU核心数 ({cpu_cores})，可能导致性能不佳或不稳定。")
    actual_num_workers = max(1, actual_num_workers) # 确保至少为1
    
    # print(f"准备使用 {actual_num_workers} 个工作进程处理 {len(tasks_to_process)} 个SSIM比较任务...")

    initargs_tuple = (
        frames,
        convert_to_gray,
        effective_original_max_val, # 这是新的含义
        skimage_supports_channel_axis_main
    )
    
    context_method = "spawn" if os.name == 'nt' else "fork" # forkserver 也可以考虑
    # context_method = "spawn" # 在某些情况下，spawn 更稳定，但可能稍慢
    try:
        ctx = multiprocessing.get_context(context_method)
    except ValueError:
        print(f"警告: multiprocessing context '{context_method}' 初始化失败，尝试默认上下文。")
        ctx = multiprocessing # type: ignore

    results_collector: List[Tuple[int, int, Optional[float]]] = []
    try:
        with ctx.Pool(
            processes=actual_num_workers,
            initializer=_init_worker,
            initargs=initargs_tuple
        ) as pool:
            with tqdm(total=len(tasks_to_process), desc="Calculating SSIM (CPU)", unit="pair") as pbar:
                for result_tuple in pool.imap_unordered(_calculate_single_ssim_task, tasks_to_process):
                    results_collector.append(result_tuple)
                    pbar.update(1)
    except Exception as e_pool:
        print(f"多进程池执行过程中发生严重错误: {e_pool}")
        import traceback
        traceback.print_exc()
        # 根据错误严重性，可能需要返回部分结果或重新抛出异常
        # 这里我们继续尝试填充已收集的结果

    for t_idx, offset_val, score in results_collector:
        if offset_val in offset_to_index_map: # 确保 offset_val 是我们期望的有效offset
            result_offset_idx = offset_to_index_map[offset_val]
            # 确保 t_idx 和 result_offset_idx 没有越界 (理论上不应发生，如果tasks_to_process正确)
            if 0 <= t_idx < num_frames_total and 0 <= result_offset_idx < len(sorted_unique_offsets):
                 all_ssim_vectors[t_idx][result_offset_idx] = score
            # else:
                # print(f"警告: 无效的索引 t_idx={t_idx} 或 result_offset_idx={result_offset_idx} (来自 offset_val={offset_val})")
        # else:
            # print(f"警告: 从工作进程收到未知偏移量 {offset_val} (帧 {t_idx}) 的结果，将被忽略。")
            
    return all_ssim_vectors


# ==============================================================================
# ============ 新增：纯串行(单进程)SSIM计算函数 ===================================
# ==============================================================================
def calculate_temporal_ssim_vectors_serial(
    frames: Sequence[np.ndarray],
    offsets: List[int],
    convert_to_gray: bool = False,
    win_size: Optional[int] = 7,
    data_range_override: Optional[float] = None
) -> List[List[Optional[float]]]:
    """
    一个纯串行(单线程)的函数，用于在CPU上计算时域SSIM向量。
    它的参数和返回类型与 _mp 版本兼容。
    """
    # 1. --- 输入校验和任务准备 (与 _mp 版本逻辑相同) ---
    if not frames:
        print("输入帧序列为空。")
        return []
    if not offsets:
        return [[] for _ in frames]
    
    valid_offsets = sorted(list(set(o for o in offsets if o > 0)))
    if not valid_offsets:
        return [[] for _ in frames]
    
    if win_size is not None and (win_size <= 0 or win_size % 2 == 0):
        raise ValueError(f"win_size ({win_size}) 必须是正奇数。")

    num_frames_total = len(frames)
    offset_to_index_map = {offset_val: i for i, offset_val in enumerate(valid_offsets)}
    all_ssim_vectors: List[List[Optional[float]]] = [[None for _ in valid_offsets] for _ in range(num_frames_total)]

    tasks_to_process: List[Tuple[int, int, int, Optional[int]]] = []
    for t in range(num_frames_total):
        for offset_val in valid_offsets:
            prev_frame_idx = t - offset_val
            if prev_frame_idx >= 0:
                tasks_to_process.append((t, prev_frame_idx, offset_val, win_size))

    if not tasks_to_process:
        return all_ssim_vectors

    # 2. --- 准备帧处理逻辑 (串行版本) ---
    
    # 确定缩放因子 (与 _mp 版本逻辑相同)
    effective_original_max_val: float
    if data_range_override is not None:
        effective_original_max_val = data_range_override
    else:
        first_frame = frames[0]
        if first_frame.dtype == np.uint8:
            effective_original_max_val = 255.0
        elif np.issubdtype(first_frame.dtype, np.integer):
            effective_original_max_val = float(np.iinfo(first_frame.dtype).max)
        else:
            effective_original_max_val = 1.0  # 浮点数默认

    # 帧处理缓存，避免重复转换
    processed_frames_cache: Dict[int, Tuple[np.ndarray, bool]] = {}

    def get_processed_frame(idx: int) -> Tuple[np.ndarray, bool]:
        """在串行模式下获取并处理帧的内部函数"""
        if idx in processed_frames_cache:
            return processed_frames_cache[idx]

        original_frame = frames[idx]
        
        # 核心处理逻辑 (模拟 _get_processed_frame_for_worker)
        if convert_to_gray:
            if original_frame.ndim == 3:
                processed_frame = rgb2gray(original_frame).astype(np.float32)
            else: # 已经是灰度图，只需归一化
                processed_frame = (original_frame.astype(np.float32) / effective_original_max_val)
            is_color = False
        else: # 保持彩色或原始灰度，但需要归一化
            processed_frame = (original_frame.astype(np.float32) / effective_original_max_val)
            is_color = processed_frame.ndim == 3 and processed_frame.shape[-1] in (3,4)

        processed_frame = np.clip(processed_frame, 0.0, 1.0)
        
        result = (processed_frame, is_color)
        processed_frames_cache[idx] = result
        return result

    # 3. --- 主计算循环 (串行) ---
    print("以串行模式安全计算SSIM...")
    for t_idx, prev_idx, offset_val, win_size_val in tqdm(tasks_to_process, desc="Calculating SSIM (Serial)"):
        try:
            frame_t_arr, is_color_t = get_processed_frame(t_idx)
            frame_prev_arr, _ = get_processed_frame(prev_idx)
            
            ssim_params: Dict[str, Union[int, float, bool, None, str]] = {
                'win_size': win_size_val,
                'data_range': 1.0,  # 因为已经归一化到[0,1]
                'gaussian_weights': True
            }

            if is_color_t:
                if SKIMAGE_SUPPORTS_CHANNEL_AXIS:
                    ssim_params['channel_axis'] = -1
                else:
                    ssim_params['multichannel'] = True # type: ignore
            
            score = structural_similarity(frame_t_arr, frame_prev_arr, **ssim_params) # type: ignore
            
            result_offset_idx = offset_to_index_map[offset_val]
            all_ssim_vectors[t_idx][result_offset_idx] = np.clip(score, -1.0, 1.0)

        except Exception as e:
            print(f"串行计算SSIM时出错: {e} (帧 {t_idx} vs {prev_idx})")
            # 保持为 None
            
    return all_ssim_vectors