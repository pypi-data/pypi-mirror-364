import torch
import torch.nn.functional as F # Still potentially useful, though not directly for SSIM via piqa
import numpy as np
from typing import List, Optional, Sequence, Tuple, Dict, Union
from tqdm import tqdm
import math
import os # 用于测试代码中的环境变量

# Try to import piqa
try:
    import piqa
    from piqa.ssim import SSIM as SSIM_piqa_class # Specific import for clarity
    PIQA_AVAILABLE = True
except ImportError:
    PIQA_AVAILABLE = False
    print("警告: piqa 库未找到。GPU SSIM 计算将不可用。")
    print("请尝试使用 'pip install piqa' 安装它。")
    # Define a placeholder if piqa is not available
    class SSIM_piqa_class: # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("piqa 未安装，无法创建 SSIM 实例。")
        def __call__(self, *args, **kwargs):
            raise ImportError("piqa 未安装，无法计算 SSIM。")

# _create_gaussian_window_2d_pytorch function is removed as it's not used for piqa-based SSIM.

def _preprocess_frames_for_gpu(
    frames_np: Sequence[np.ndarray],
    convert_to_gray: bool,
    original_max_val_for_scaling: float, # NEW: Explicit original max value for scaling
    data_range_target: float,            # Target range, typically 1.0 for piqa
    device: torch.device,
    target_dtype: torch.dtype = torch.float32
) -> List[torch.Tensor]:
    """
    Preprocesses NumPy frames to PyTorch tensors for GPU.
    Scales frames from their original range (defined by original_max_val_for_scaling)
    to the data_range_target (typically [0,1] for PiQA).
    """
    processed_frames_torch: List[torch.Tensor] = []
    
    for frame_np in tqdm(frames_np, desc="Preprocessing frames for GPU", leave=False): # leave=False for cleaner nested tqdm
        if not isinstance(frame_np, np.ndarray):
            raise TypeError(f"输入帧必须是 NumPy 数组，但得到 {type(frame_np)}")
        
        img_tensor = torch.from_numpy(frame_np.copy()).to(device)

        if img_tensor.ndim == 2: # H, W
            img_tensor = img_tensor.unsqueeze(0) # 1, H, W
        elif img_tensor.ndim == 3: # H, W, C
            img_tensor = img_tensor.permute(2, 0, 1) # C, H, W
        else:
            raise ValueError(f"不支持的帧维度: {img_tensor.ndim} (形状: {img_tensor.shape})")

        # Always convert to target_dtype (float32 by default) for consistent processing
        if img_tensor.dtype != target_dtype:
            img_tensor = img_tensor.to(target_dtype)

        if convert_to_gray and img_tensor.shape[0] > 1: # Check if not already single channel
            if img_tensor.shape[0] == 3: # RGB
                weights = torch.tensor([0.299, 0.587, 0.114], dtype=target_dtype, device=device).view(3, 1, 1)
                img_tensor = (img_tensor * weights).sum(dim=0, keepdim=True)
            elif img_tensor.shape[0] == 4: # RGBA
                weights = torch.tensor([0.299, 0.587, 0.114], dtype=target_dtype, device=device).view(3, 1, 1)
                img_tensor = (img_tensor[:3] * weights).sum(dim=0, keepdim=True) # Use only RGB
            else: # Other channel counts (e.g., 2) are not standard for this grayscale conversion
                # If it was, e.g., 2 channels, this would error. Better to be explicit.
                if img_tensor.shape[0] != 1: # Re-check if it's not already grayscale
                    raise ValueError(f"不支持的彩色通道数进行灰度转换: {img_tensor.shape[0]}。期望3 (RGB) 或 4 (RGBA)。")
        
        # --- MODIFIED SCALING LOGIC ---
        # Scale the tensor to the target data range [0, data_range_target]
        # using the provided original_max_val_for_scaling.
        if original_max_val_for_scaling <= 1e-6: 
            if data_range_target == 0.0:
                 img_tensor = torch.zeros_like(img_tensor)
            else:
                # If original scale is effectively zero, assume input tensor is also likely zero.
                # For safety, output scaled tensor as 0.
                # This avoids potential division by zero if img_tensor had non-zero values but scale was misreported as 0.
                img_tensor = torch.zeros_like(img_tensor)
                # print(f"警告: original_max_val_for_scaling ({original_max_val_for_scaling}) 非常小或为零。输出将为零。")
        else:
            img_tensor = (img_tensor / original_max_val_for_scaling) * data_range_target
        
        img_tensor = torch.clamp(img_tensor, 0.0, data_range_target)
        processed_frames_torch.append(img_tensor)
        
    return processed_frames_torch


def calculate_temporal_ssim_vectors_gpu(
    frames_np_sequence: Sequence[np.ndarray],
    offsets: List[int],
    convert_to_gray: bool = False,
    win_size: int = 7,
    data_range_override: Optional[float] = None, # 恢复的参数
    nonnegative_ssim_opt: bool = True,          # 恢复的参数
    batch_size: int = 16,                       # 恢复的参数
    device_str: Optional[str] = None, 
    show_progress: bool = True, 
    target_gpu_id: Optional[int] = None 
) -> List[List[Union[float, None]]]:
    if not PIQA_AVAILABLE:
        print("错误: piqa 库未安装。无法执行 GPU SSIM 计算。")
        if not frames_np_sequence or not offsets:
             return []
        num_frames_fallback = len(frames_np_sequence)
        sorted_unique_offsets_fallback = sorted(list(set(o for o in offsets if o > 0))) if offsets else []
        return [[None for _ in sorted_unique_offsets_fallback] for _ in range(num_frames_fallback)]

    if not frames_np_sequence:
        print("输入帧序列为空。")
        return []
    if not offsets:
        print("警告: 未提供 offsets 列表。将为每帧返回空的 SSIM 向量。")
        return [[] for _ in frames_np_sequence]
    
    valid_offsets = sorted(list(set(o for o in offsets if o > 0)))
    if not valid_offsets:
        # If original offsets list was not empty but all were invalid
        if offsets: 
            print("警告: offsets 列表中所有值均为非正数或无效，过滤后没有有效的 offsets。")
        raise ValueError("所有提供的 offsets 必须是正整数。过滤后没有有效的 offsets。")

    if any(o <=0 for o in offsets) and valid_offsets: # Check original list for user message only if some valid ones exist
         print("警告: offsets 列表中包含非正数值，这些值将被忽略。")

    if win_size % 2 == 0 or win_size <=0 : # win_size must be positive odd
        raise ValueError(f"win_size ({win_size}) 必须是正奇数。")

    # --- 设备选择逻辑 --- 
    if target_gpu_id is not None and torch.cuda.is_available():
        if 0 <= target_gpu_id < torch.cuda.device_count():
            device = torch.device(f"cuda:{target_gpu_id}")
        else:
            print(f"警告: 指定的 GPU ID {target_gpu_id} 无效 (可用数量: {torch.cuda.device_count()}). 将尝试使用 cuda:0.")
            if torch.cuda.device_count() > 0:
                device = torch.device("cuda:0")
            else: # Should not happen if torch.cuda.is_available() was true and count is 0
                print("警告: CUDA 声称可用但未检测到设备，回退到 CPU.")
                device = torch.device("cpu")
    elif device_str: # 如果用户明确指定了 device_str，则优先使用
        device = torch.device(device_str)
    else: # 默认行为
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 双重检查CUDA可用性与最终设备
    if not torch.cuda.is_available() and device.type == 'cuda':
        print("警告: 请求使用 CUDA 但最终不可用，将回退到 CPU。")
        device = torch.device("cpu")
    # --- 设备选择逻辑结束 ---
    print(f"使用设备: {device}")

    original_data_max_value: float
    first_frame_sample = frames_np_sequence[0]
    if not isinstance(first_frame_sample, np.ndarray): # Basic check for first frame
        raise TypeError(f"输入帧序列中的元素必须是 NumPy 数组，但第一个元素是 {type(first_frame_sample)}")


    if data_range_override is not None:
        if data_range_override <= 0:
            raise ValueError("data_range_override 必须是正数。")
        original_data_max_value = data_range_override
        print(f"使用 data_range_override: {original_data_max_value} 作为原始数据缩放基准进行预处理。")
    else: 
        if first_frame_sample.dtype == np.uint8:
            original_data_max_value = 255.0
            # print(f"从 uint8 帧推断原始数据缩放基准为: {original_data_max_value}")
        elif np.issubdtype(first_frame_sample.dtype, np.floating):
            min_val_check, max_val_check = first_frame_sample.min(), first_frame_sample.max()
            if min_val_check >= -1e-5 and max_val_check <= 1.0 + 1e-5: 
                original_data_max_value = 1.0
            elif min_val_check >= -1e-5 and max_val_check <= 255.0 + 1e-5 and max_val_check > 1.0 + 1e-5: # Ensure it's not mistaken for [0,1]
                 original_data_max_value = 255.0
            else: 
                print(f"警告: 无法从第一个浮点帧 (范围 [{min_val_check:.2f}, {max_val_check:.2f}]) 安全推断其原始比例。"
                      "假设其原始比例最大值为 1.0 进行预处理以适配 PiQA。"
                      "如果输入是例如 [-1,1] 或其他非标准范围的浮点数，或其最大值不是1.0或255.0，"
                      "强烈建议使用 data_range_override 参数指定其真实的最大值（例如，如果数据是[0,1000]，则data_range_override=1000.0）。")
                original_data_max_value = 1.0 
            # print(f"从浮点帧 (范围 [{first_frame_sample.min():.2f}, {first_frame_sample.max():.2f}]) 推断/默认原始数据缩放基准为: {original_data_max_value}")
        elif np.issubdtype(first_frame_sample.dtype, np.integer): # Other integer types like uint16
             # For other integer types, using their max value is safer if data_range_override is not given
             iinfo = np.iinfo(first_frame_sample.dtype)
             original_data_max_value = float(iinfo.max)
             print(f"从整数类型 {first_frame_sample.dtype} 帧推断原始数据缩放基准为: {original_data_max_value}。"
                   " 如果此推断不准确，请使用 data_range_override。")
        else:
            raise TypeError(f"不支持的帧数据类型 {first_frame_sample.dtype} 用于自动推断原始数据比例。"
                            "请使用 data_range_override。")
    
    piqa_input_target_range = 1.0
    # print(f"帧将被预处理到目标范围 [0, {piqa_input_target_range}] (使用 original_max_val_for_scaling={original_data_max_value}) 以适配 PiQA。")

    try:
        processed_frames_torch = _preprocess_frames_for_gpu(
            frames_np_sequence,
            convert_to_gray,
            original_max_val_for_scaling=original_data_max_value, 
            data_range_target=piqa_input_target_range,          
            device=device
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"帧预处理失败: {e}")
        return [[None for _ in valid_offsets] for _ in range(len(frames_np_sequence))]

    num_frames = len(processed_frames_torch)
    if num_frames == 0: 
        print("预处理后没有帧。")
        return []
        
    num_channels = processed_frames_torch[0].shape[0]
    
    try:
        # PiQA's SSIM value_range defaults to 1.0, which matches our preprocessed data.
        ssim_metric = SSIM_piqa_class(
            n_channels=num_channels,
            window_size=win_size, 
            reduction='none' 
        ).to(device)
    except Exception as e:
        print(f"初始化 PiQA SSIM 模块失败: {e}")
        return [[None for _ in valid_offsets] for _ in range(len(frames_np_sequence))]

    offset_to_index_map = {offset_val: i for i, offset_val in enumerate(valid_offsets)}
    all_ssim_vectors: List[List[Optional[float]]] = [[None for _ in valid_offsets] for _ in range(num_frames)]

    tasks: List[Dict[str, int]] = []
    for t in range(num_frames):
        for offset_val in valid_offsets: 
            prev_frame_idx = t - offset_val
            if prev_frame_idx >= 0:
                tasks.append({'t_idx': t, 'prev_idx': prev_frame_idx, 'offset_val': offset_val})

    if not tasks:
        print("根据 offsets，没有有效的帧对可以进行比较。")
        return all_ssim_vectors

    num_batches = math.ceil(len(tasks) / batch_size)
    task_iterator = tqdm(range(num_batches), desc="Calculating SSIM with PiQA (GPU batches)", disable=not show_progress, leave=True)

    for i in task_iterator:
        batch_tasks = tasks[i * batch_size : (i + 1) * batch_size]
        if not batch_tasks:
            continue

        img1_batch_list: List[torch.Tensor] = []
        img2_batch_list: List[torch.Tensor] = []
        for task_info in batch_tasks:
            img1_batch_list.append(processed_frames_torch[task_info['t_idx']])
            img2_batch_list.append(processed_frames_torch[task_info['prev_idx']])
        
        try:
            img1_batch_tensor = torch.stack(img1_batch_list)
            img2_batch_tensor = torch.stack(img2_batch_list)

            ssim_scores_batch = ssim_metric(img1_batch_tensor, img2_batch_tensor) 

            # --- MODIFICATION START ---
            # Clamp to theoretical SSIM range first to handle potential numerical outputs 
            # slightly outside [-1,1] from piqa for identical/near-identical images.
            ssim_scores_batch = torch.clamp(ssim_scores_batch, -1.0, 1.0)
            # --- MODIFICATION END ---

            if nonnegative_ssim_opt:
                # This will further clamp the lower bound to 0.0 if it was negative.
                # The upper bound is already handled by the previous clamp.
                ssim_scores_batch = torch.clamp(ssim_scores_batch, min=0.0) # or torch.clamp(ssim_scores_batch, 0.0, 1.0)

            for task_idx, ssim_score_tensor in enumerate(ssim_scores_batch):
                original_task_info = batch_tasks[task_idx]
                ssim_val = ssim_score_tensor.item()
                t_original_idx = original_task_info['t_idx']
                offset_original_val = original_task_info['offset_val']
                result_offset_map_idx = offset_to_index_map[offset_original_val]
                all_ssim_vectors[t_original_idx][result_offset_map_idx] = ssim_val
        
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"GPU 内存不足 (Batch {i+1}/{num_batches})。尝试减小 batch_size。错误: {e}")
            elif "Kernel size can't be greater than actual input size" in str(e) or \
                 "Expected kernel_size to be less than or equal to input size" in str(e) or \
                 "Defaulting to non-separable Conv2d" in str(e): 
                print(f"警告/错误: 批次 {i+1}/{num_batches} 中的一个或多个帧对的 win_size ({win_size}) 可能对于图像尺寸而言过大。错误: {e}")
            else:
                print(f"计算批次 {i+1}/{num_batches} 时发生运行时错误: {e}")
            for task_info in batch_tasks:
                t_original_idx = task_info['t_idx']
                offset_original_val = task_info['offset_val']
                if offset_original_val in offset_to_index_map: # Ensure offset is valid before indexing
                    result_offset_map_idx = offset_to_index_map[offset_original_val]
                    all_ssim_vectors[t_original_idx][result_offset_map_idx] = None
            continue 
        except Exception as e:
            print(f"计算批次 {i+1}/{num_batches} 时发生未知错误: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for unknown errors
            for task_info in batch_tasks: 
                t_original_idx = task_info['t_idx']
                offset_original_val = task_info['offset_val']
                if offset_original_val in offset_to_index_map:
                    result_offset_map_idx = offset_to_index_map[offset_original_val]
                    all_ssim_vectors[t_original_idx][result_offset_map_idx] = None
            continue
            
    # --- 手动释放显存 ---
    try:
        if 'processed_frames_torch' in locals() and processed_frames_torch is not None:
            del processed_frames_torch
        if 'ssim_metric' in locals() and ssim_metric is not None:
            del ssim_metric
        # 批处理张量通常在循环作用域内，但为确保清理，可以添加（尽管可能不是严格必要）
        if 'img1_batch_tensor' in locals() and img1_batch_tensor is not None:
            del img1_batch_tensor
        if 'img2_batch_tensor' in locals() and img2_batch_tensor is not None:
            del img2_batch_tensor
        
        if device.type == 'cuda':
            # print(f"调试: 清理前的CUDA内存: Allocated={torch.cuda.memory_allocated(device)/1024**2:.2f} MB, Reserved={torch.cuda.memory_reserved(device)/1024**2:.2f} MB")
            torch.cuda.empty_cache()
            # print(f"调试: 清理后的CUDA内存: Allocated={torch.cuda.memory_allocated(device)/1024**2:.2f} MB, Reserved={torch.cuda.memory_reserved(device)/1024**2:.2f} MB")
    except NameError: # 如果变量在某些执行路径中未定义（例如，由于早期返回）
        pass # 静默处理，因为我们的目标是清理已定义的变量
    except Exception as e_cleanup:
        print(f"警告: 在清理GPU内存时发生错误: {e_cleanup}")

    return all_ssim_vectors

# --- Test Code ---
if __name__ == '__main__':
    # Set environment variable to bypass GPU checks if running in CI or non-GPU env for basic logic tests
    # In a real scenario, you'd want PIQA_AVAILABLE to be true for GPU tests.
    RUN_CPU_FALLBACK_TESTS = os.getenv("CI_CPU_TEST") == "true"
    
    if not PIQA_AVAILABLE and not RUN_CPU_FALLBACK_TESTS:
        print("由于 piqa 不可用，并且未设置 CI_CPU_TEST=true，测试将不运行 GPU SSIM 计算。")
    else:
        if PIQA_AVAILABLE:
            print(f"PiQA version: {piqa.__version__}")
            print(f"PyTorch version: {torch.__version__}")
            print(f"CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                cuda_version_str = torch.version.cuda if hasattr(torch.version, 'cuda') else "N/A"
                print(f"CUDA version: {cuda_version_str}") 
                print(f"Device name: {torch.cuda.get_device_name(0)}")
        else: # PIQA_AVAILABLE is False, but RUN_CPU_FALLBACK_TESTS is True
            print("PiQA 不可用，测试将仅检查函数的非 PIQA 逻辑部分（如参数处理和返回结构）。")


        num_test_frames = 20
        height, width = 64, 64
        test_offsets = [1, 3, 0, -2, 3] # Include invalid and duplicate offsets
        piqa_default_win_size = 11 # Default for piqa if not specified, but we specify it.

        # --- Test 0: Identical frames to test SSIM=1.0 and clamping ---
        print("\n--- Test 0: Identical frames (expect SSIM close to 1.0) ---")
        # Create identical frames
        identical_frame_np = np.random.rand(height, width).astype(np.float32) * 0.8 # Values between 0 and 0.8
        test_frames_identical = [identical_frame_np.copy() for _ in range(num_test_frames)]
        
        ssim_vectors_identical = calculate_temporal_ssim_vectors_gpu(
            test_frames_identical,
            offsets=[1], # Compare adjacent identical frames
            convert_to_gray=True, # Ensure single channel for simplicity if original has more
            win_size=7,
            data_range_override=1.0, # Max value of original data is 1.0 (or less, but scaling by 1.0 is fine)
            batch_size=16,
            nonnegative_ssim_opt=False, # Test without the non-negative clamp first
            show_progress=True
        )
        if PIQA_AVAILABLE: # Only assert values if piqa ran
            all_ones = True
            has_results = False
            for i, row in enumerate(ssim_vectors_identical):
                if i == 0 and row[0] is None: continue # First frame has no prior for offset 1
                has_results = True
                for val in row:
                    if val is not None:
                        if not (0.999 <= val <= 1.000): # Allow for tiny float inaccuracies but clamp ensures <= 1.0
                            all_ones = False
                            print(f"  Unexpected SSIM for identical frames: {val}")
                        assert val <= 1.0, f"SSIM value {val} exceeded 1.0 after clamping!"
            if has_results:
                 print(f"结果: Identical frames test {'produced values very close to or equal to 1.0' if all_ones else 'produced some unexpected values (see above)'}.")
            else:
                 print("结果: Identical frames test did not produce comparable results.")
        else:
            print("结果: Identical frames test (PIQA not available, structure check only).")


        print("\n--- Test 1: Grayscale float frames, original range [0,1] ---")
        test_frames_gray_float_0_1 = [(np.random.rand(height, width).astype(np.float32)) for _ in range(num_test_frames)]
        ssim_vectors_gpu_gray = calculate_temporal_ssim_vectors_gpu(
            test_frames_gray_float_0_1,
            offsets=test_offsets,
            convert_to_gray=True, 
            win_size=7, 
            data_range_override=1.0, 
            batch_size=16,
            nonnegative_ssim_opt=True,
            show_progress=False
        )
        # Check structure: number of valid offsets should be 2 (1, 3) after filtering and unique
        expected_num_offsets = len(sorted(list(set(o for o in test_offsets if o > 0))))
        if ssim_vectors_gpu_gray and ssim_vectors_gpu_gray[0] is not None:
             assert len(ssim_vectors_gpu_gray[0]) == expected_num_offsets, f"Test 1: Expected {expected_num_offsets} offset results, got {len(ssim_vectors_gpu_gray[0])}"

        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_gpu_gray for val in row):
            print("结果: Grayscale float [0,1] test produced some results.")
        elif not PIQA_AVAILABLE:
            print("结果: Grayscale float [0,1] test (PIQA not available, structure check only).")
        else:
            print("结果: Grayscale float [0,1] test did NOT produce results or all were None.")


        print("\n--- Test 2: Color uint8 frames, original range [0,255] (convert to gray) ---")
        test_frames_color_uint8 = [np.random.randint(0, 256, (height, width, 3), dtype=np.uint8) for _ in range(num_test_frames)]
        ssim_vectors_gpu_color_to_gray = calculate_temporal_ssim_vectors_gpu(
            test_frames_color_uint8,
            offsets=test_offsets,
            convert_to_gray=True,
            win_size=piqa_default_win_size, # Using 11
            data_range_override=None, 
            batch_size=8,
            show_progress=False
        )
        if ssim_vectors_gpu_color_to_gray and ssim_vectors_gpu_color_to_gray[0] is not None:
             assert len(ssim_vectors_gpu_color_to_gray[0]) == expected_num_offsets
        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_gpu_color_to_gray for val in row):
            print("结果: Color uint8 to gray test produced some results.")
        elif not PIQA_AVAILABLE:
            print("结果: Color uint8 to gray test (PIQA not available, structure check only).")
        else:
            print("结果: Color uint8 to gray test did NOT produce results or all were None.")


        print("\n--- Test 3: Color uint8 frames, original range [0,255] (as color) ---")
        ssim_vectors_gpu_color_as_color = calculate_temporal_ssim_vectors_gpu(
            test_frames_color_uint8, 
            offsets=test_offsets,
            convert_to_gray=False, 
            win_size=piqa_default_win_size,
            data_range_override=255.0, 
            batch_size=8,
            show_progress=False
        )
        if ssim_vectors_gpu_color_as_color and ssim_vectors_gpu_color_as_color[0] is not None:
            assert len(ssim_vectors_gpu_color_as_color[0]) == expected_num_offsets
        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_gpu_color_as_color for val in row):
            print("结果: Color uint8 as color test produced some results.")
        elif not PIQA_AVAILABLE:
            print("结果: Color uint8 as color test (PIQA not available, structure check only).")
        else:
            print("结果: Color uint8 as color test did NOT produce results or all were None.")

        print("\n--- Test 4: Float frames, original range [0,1000] (convert to gray) ---")
        test_frames_float_0_1000 = [(np.random.rand(height, width).astype(np.float32) * 1000.0) for _ in range(num_test_frames)]
        ssim_vectors_float_custom_range = calculate_temporal_ssim_vectors_gpu(
            test_frames_float_0_1000,
            offsets=[1], 
            convert_to_gray=True,
            win_size=5,
            data_range_override=1000.0, 
            batch_size=16,
            show_progress=False
        )
        if ssim_vectors_float_custom_range and ssim_vectors_float_custom_range[0] is not None:
            assert len(ssim_vectors_float_custom_range[0]) == 1
        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_float_custom_range for val in row):
            print("结果: Float [0,1000] with data_range_override=1000.0 test produced some results.")
        elif not PIQA_AVAILABLE:
             print("结果: Float [0,1000] test (PIQA not available, structure check only).")
        else:
            print("结果: Float [0,1000] with data_range_override=1000.0 test did NOT produce results or all were None.")


        print("\n--- Test 5: Small window size (e.g., 3) for robustness ---")
        ssim_vectors_small_win = calculate_temporal_ssim_vectors_gpu(
            test_frames_gray_float_0_1, 
            offsets=[1],
            convert_to_gray=True,
            win_size=3, 
            data_range_override=1.0, 
            batch_size=16,
            show_progress=False
        )
        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_small_win for val in row):
            print("结果: Small window size test produced some results.")
        elif not PIQA_AVAILABLE:
             print("结果: Small window size test (PIQA not available, structure check only).")
        else:
            print("结果: Small window size test did NOT produce results or all were None.")
        
        print("\n--- Test 6: Edge case - very small images vs. window size ---")
        small_height, small_width = 5, 5 
        test_frames_tiny_gray = [(np.random.rand(small_height, small_width).astype(np.float32)) for _ in range(5)]
        ssim_vectors_tiny_img = calculate_temporal_ssim_vectors_gpu(
            test_frames_tiny_gray,
            offsets=[1],
            convert_to_gray=True,
            win_size=7, 
            data_range_override=1.0,
            batch_size=4,
            show_progress=False
        )
        if PIQA_AVAILABLE:
            if all(val is None for row in ssim_vectors_tiny_img for val in row if row): 
                 print(f"结果: Tiny image test (win_size > dim) resulted in None values as expected, or ran without crashing.")
            elif not ssim_vectors_tiny_img or not ssim_vectors_tiny_img[0] or not any(r for r in ssim_vectors_tiny_img if r is not None and r[0] is not None) : # No tasks or no results
                 print(f"结果: Tiny image test (win_size > dim) produced no results or tasks, as expected or handled.")
            else:
                 print(f"结果: Tiny image test (win_size > dim) produced some results (unexpected): {ssim_vectors_tiny_img[0]}")
        else:
            print("结果: Tiny image test (PIQA not available, structure check only).")


        print("\n--- Test 7: No valid positive offsets ---")
        try:
            ssim_no_valid_offset = calculate_temporal_ssim_vectors_gpu(
                test_frames_gray_float_0_1,
                offsets=[0, -1, -5], 
                convert_to_gray=True,
                win_size=7,
                data_range_override=1.0,
                show_progress=False
            )
            print(f"结果: No valid positive offsets test DID NOT raise ValueError as expected.")
        except ValueError as e:
            print(f"结果: No valid positive offsets test correctly raised ValueError: {e}")
        
        print("\n--- Test 8: Empty offsets list ---")
        ssim_empty_offset = calculate_temporal_ssim_vectors_gpu(
            test_frames_gray_float_0_1,
            offsets=[], 
            convert_to_gray=True,
            win_size=7,
            data_range_override=1.0,
            show_progress=False
        )
        if all(not r for r in ssim_empty_offset): 
            print(f"结果: Empty offsets list test correctly returned list of empty lists.")
        else:
            print(f"结果: Empty offsets list test failed: {ssim_empty_offset}")
        
        print("\n--- Test 9: uint16 frames ---")
        test_frames_uint16 = [(np.random.randint(0, 2**16, (height, width), dtype=np.uint16)) for _ in range(num_test_frames)]
        ssim_vectors_uint16 = calculate_temporal_ssim_vectors_gpu(
            test_frames_uint16,
            offsets=[1],
            convert_to_gray=True, # Already grayscale, but this ensures single channel handling
            win_size=7,
            data_range_override=None, # Infer original scale (65535.0 from uint16)
            batch_size=8,
            show_progress=False
        )
        if PIQA_AVAILABLE and any(val is not None for row in ssim_vectors_uint16 for val in row):
            print("结果: uint16 frames test produced some results.")
        elif not PIQA_AVAILABLE:
            print("结果: uint16 frames test (PIQA not available, structure check only).")
        else:
            print("结果: uint16 frames test did NOT produce results or all were None.")


        print("\nAll tests completed.")