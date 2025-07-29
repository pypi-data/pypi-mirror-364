# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch # 您之前的代码中包含了torch，这里保留

# _plot_analysis_final 函数定义 (与之前版本相同，此处为简洁省略，实际使用时请包含)
def _plot_analysis_final(raw_ssim, smoothed_ssim, slopes, start_frame, end_frame, activity_thresh_val, active_frames):
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        print("警告：未能设置中文字体，图表标签可能显示不正常。")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    fig.suptitle("页面加载时间分析结果 (最终优化版)", fontsize=16)
    frames = np.arange(len(raw_ssim)); ax1.plot(frames, raw_ssim, label='原始SSIM', alpha=0.4, color='gray', linestyle=':'); ax1.plot(frames, smoothed_ssim, label='平滑后SSIM', color='blue')
    if len(active_frames) > 0: ax1.plot(active_frames, smoothed_ssim[active_frames], 'x', color='purple', markersize=6, label='活动点')
    ax1.set_ylabel('SSIM 得分'); ax1.grid(True, linestyle='--', alpha=0.6); ax2.plot(frames, slopes, label='斜率 (变化率)', color='green')
    ax2.axhline(activity_thresh_val, color='orange', linestyle='--', label=f'活动阈值 ({activity_thresh_val:.3f})'); ax2.axhline(-activity_thresh_val, color='orange', linestyle='--')
    ax2.set_xlabel('帧号 (Frames)'); ax2.set_ylabel('斜率'); ax2.grid(True, linestyle='--', alpha=0.6)
    if start_frame != -1: ax1.axvline(start_frame, color='green', linestyle='-', linewidth=2, label=f'加载开始 @ {start_frame}'); ax2.axvline(start_frame, color='green', linestyle='-', linewidth=2)
    if end_frame != -1: ax1.axvline(end_frame, color='red', linestyle='-', linewidth=2, label=f'加载结束 @ {end_frame}'); ax2.axvline(end_frame, color='red', linestyle='-', linewidth=2)
    ax1.legend(loc='best'); ax2.legend(loc='best'); plt.tight_layout(rect=[0, 0, 1, 0.96]); plt.show()


def find_page_load_intelligent(
    ssim_sequence,
    smooth_window=9,
    activity_threshold=0.004,
    cluster_separation_threshold=150,
    start_search_window_duration=10,
    fps=30,
    plot_results=True
):
    print("--- 开始分析 ---")
    if not isinstance(ssim_sequence, (list, np.ndarray)) or len(ssim_sequence) < smooth_window:
        print("错误: SSIM序列数据不足或格式不正确。")
        return -1, -1

    ssim_series = pd.Series(ssim_sequence)
    smoothed_ssim = ssim_series.rolling(window=smooth_window, min_periods=1).mean().to_numpy()
    slopes = np.diff(smoothed_ssim, prepend=smoothed_ssim[0])
    active_frames = np.where(np.abs(slopes) > activity_threshold)[0]

    if len(active_frames) < 1:
        print("未检测到任何显著活动。")
        if plot_results:
            _plot_analysis_final(ssim_sequence, smoothed_ssim, slopes, -1, -1, activity_threshold, [])
        return -1, -1

    # 2. 智能识别 Start Frame
    first_active_frame = active_frames[0]
    
    search_window_end = first_active_frame + int(start_search_window_duration * fps)
    search_window_end = min(search_window_end, len(smoothed_ssim))
    search_window = smoothed_ssim[first_active_frame:search_window_end]
    
    calculated_start_frame = first_active_frame # 默认值
    if len(search_window) > 0:
        min_ssim_index_in_window = np.argmin(search_window)
        min_ssim_global_index = first_active_frame + min_ssim_index_in_window
        
        temp_start_frame = -1
        # 从最低点向左回溯到斜率不再显著为负的点
        for i in range(min_ssim_global_index, 0, -1): 
            if slopes[i] >= -activity_threshold: # 不再是明显下降趋势
                # 如果i是平稳区的最后一个点，那么i+1是下降的开始
                if i + 1 < len(slopes) and slopes[i+1] < -activity_threshold:
                     temp_start_frame = i + 1
                else: # 可能i就是下降开始前的那个点，或者整个序列都很平缓
                     temp_start_frame = i # 作为一个备选，确保有值
                break
        else: # 如果循环正常结束（没有break），说明一直到最开头斜率都是负的或等于0
            temp_start_frame = 0 # 最极端情况，从第0帧开始
        
        if temp_start_frame != -1:
            calculated_start_frame = temp_start_frame
            
    print(f"智能识别到主要加载事件的起点位于第 {calculated_start_frame} 帧。")

    # 3. 寻找 End Frame (使用全局最大间隙逻辑)
    calculated_end_frame = -1 # 初始化
    relevant_active_frames = active_frames[active_frames >= calculated_start_frame]

    if len(relevant_active_frames) > 1:
        gaps = np.diff(relevant_active_frames)
        max_gap_index_in_gaps = np.argmax(gaps) # 这是gaps数组的索引
        max_gap_value = gaps[max_gap_index_in_gaps]
        
        if max_gap_value > cluster_separation_threshold:
            # end_frame是最大间隙开始前的那个活动点
            # relevant_active_frames[max_gap_index_in_gaps] 是最大间隙左边的点
            calculated_end_frame = relevant_active_frames[max_gap_index_in_gaps]
            print(f"在第 {calculated_end_frame} 帧后发现一个长达 {max_gap_value} 帧的全局最大静默期，判定加载结束。")
        else:
            calculated_end_frame = relevant_active_frames[-1]
            print(f"所有活动被视为一个连续事件（最大内部间隙 {max_gap_value} 帧），判定加载结束于最后一次活动。")
    elif len(relevant_active_frames) == 1: # 只有一个相关活动点（通常是start_frame本身）
        calculated_end_frame = relevant_active_frames[0]
    else: # relevant_active_frames 为空
        calculated_end_frame = calculated_start_frame # 如果开始后无活动，结束点就是开始点

    # --- 新增：确保返回的是Python原生的int类型 ---
    final_start_frame = int(calculated_start_frame) if calculated_start_frame != -1 else -1
    final_end_frame = int(calculated_end_frame) if calculated_end_frame != -1 else -1
    # --- 修改结束 ---

    if plot_results:
        # 确保传递给绘图函数的是最终确定的整数值
        _plot_analysis_final(ssim_sequence, smoothed_ssim, slopes, final_start_frame, final_end_frame, activity_threshold, active_frames)

    return final_start_frame, final_end_frame

# preprocess_ssim_data 函数定义 (与之前版本相同，此处为简洁省略，实际使用时请包含)
def preprocess_ssim_data(raw_data_list: list) -> list:
    cleaned_data = []
    if not raw_data_list: print("警告：传入的原始数据列表为空."); return cleaned_data
    print("开始进行数据预处理...")
    for i, original_item in enumerate(raw_data_list):
        item_to_process = original_item
        if isinstance(item_to_process, (list, tuple)): item_to_process = item_to_process[0]
        if i == 0:
            is_first_frame_special_case = False
            if item_to_process is None: print("信息：检测到第一个SSIM值为None对象，将其处理为1.0。"); cleaned_data.append(1.0); is_first_frame_special_case = True
            elif isinstance(item_to_process, str) and item_to_process.strip().lower() == 'none': print("信息：检测到第一个SSIM值为'None'字符串，将其处理为1.0。"); cleaned_data.append(1.0); is_first_frame_special_case = True
            else:
                try:
                    numeric_val = float(item_to_process)
                    if numeric_val == -1.0: print(f"信息：检测到第一个SSIM值为-1.0，将其处理为1.0。"); cleaned_data.append(1.0); is_first_frame_special_case = True
                except (ValueError, TypeError): pass
            if is_first_frame_special_case: continue
        try:
            numeric_val = float(item_to_process)
            if np.isnan(numeric_val): print(f"⚠️ 警告：跳过索引为 {i} 的NaN值。")
            else: cleaned_data.append(numeric_val)
        except (ValueError, TypeError): print(f"⚠️ 警告：跳过索引为 {i} 的无效数据: '{original_item}'")
    print(f"数据预处理完成，共获得 {len(cleaned_data)} 条有效数据。"); return cleaned_data


def find_page_load_simple_ssim_threshold(
    ssim_sequence, # 已预处理的SSIM数字列表
    smooth_window=7,
    ssim_drop_threshold=0.992,
    apply_smoothing=True, # <--- 新增参数，默认为True
    plot_results=True
):
    """
    一个基于SSIM绝对值阈值的简单加载时间检测算法。
    - apply_smoothing: 控制是否对输入序列进行平滑处理。
    - 开始帧：从头开始，第一个处理后SSIM值低于ssim_drop_threshold的点。
    - 结束帧：从尾部开始，第一个（反向）处理后SSIM值低于ssim_drop_threshold的点。
    """
    title_suffix = f"(简单SSIM阈值算法 - 平滑:{'开' if apply_smoothing else '关'})"
    print(f"--- 开始分析 {title_suffix} ---")

    if not ssim_sequence or len(ssim_sequence) == 0:
        print(f"{title_suffix}：错误: SSIM序列数据为空。")
        return -1, -1
        
    data_to_analyze = None # 将用于分析的数据（平滑或原始）
    
    if apply_smoothing:
        if len(ssim_sequence) < 1: # rolling至少需要1个元素 (min_periods=1)
            print(f"{title_suffix}：错误: 应用平滑时，SSIM序列数据过短。")
            return -1, -1
        print(f"应用平滑处理，窗口大小: {smooth_window}")
        ssim_series = pd.Series(ssim_sequence)
        # 确保数据是数字类型，以防万一（理论上preprocess_ssim_data已处理）
        if not pd.api.types.is_numeric_dtype(ssim_series):
            try: ssim_series = ssim_series.astype(float)
            except ValueError:
                print(f"{title_suffix}：错误: SSIM序列包含无法转换为数字的值（在平滑前）。")
                return -1,-1
        data_to_analyze = ssim_series.rolling(window=smooth_window, min_periods=1).mean().to_numpy()
    else:
        print("未应用平滑处理，使用原始（已清洗）数据进行分析。")
        try:
            # 确保是numpy array
            data_to_analyze = np.array(ssim_sequence, dtype=float)
        except ValueError:
            print(f"{title_suffix}：错误: SSIM序列包含无法转换为数字的值。")
            return -1, -1
            
    # 为了绘图和某些可能的调试，我们基于实际分析的数据计算斜率
    slopes = np.diff(data_to_analyze, prepend=data_to_analyze[0])

    start_frame = -1
    end_frame = -1

    # 2. 寻找开始帧
    for i in range(len(data_to_analyze)):
        if data_to_analyze[i] < ssim_drop_threshold:
            start_frame = i
            print(f"{title_suffix}：找到加载开始于第 {start_frame} 帧 (SSIM {data_to_analyze[i]:.3f} < {ssim_drop_threshold:.3f})。")
            break
    
    # 3. 寻找结束帧
    if start_frame != -1:
        search_start_index_for_end = start_frame
        for i in range(len(data_to_analyze) - 1, search_start_index_for_end - 1, -1):
            if data_to_analyze[i] < ssim_drop_threshold:
                end_frame = i
                print(f"{title_suffix}：找到加载结束于第 {end_frame} 帧 (SSIM {data_to_analyze[i]:.3f} < {ssim_drop_threshold:.3f})。")
                break
    
    # 4. 处理边界情况
    if start_frame == -1:
        end_frame = -1
        print(f"{title_suffix}：未检测到SSIM低于阈值的活动。")
    elif end_frame == -1:
        end_frame = start_frame
        print(f"{title_suffix}：未找到明确结束点或活动仅一帧，将结束点设为开始点 {end_frame}。")

    final_start_frame = int(start_frame) if start_frame != -1 else -1
    final_end_frame = int(end_frame) if end_frame != -1 else -1
    
    if plot_results:
        active_frames_for_plot = np.where(data_to_analyze < ssim_drop_threshold)[0]
        _plot_analysis_generic(
            title_suffix, ssim_sequence, data_to_analyze, slopes, 
            final_start_frame, final_end_frame, 
            ssim_drop_threshold, "ssim", 
            active_frames_for_plot
        )

    return final_start_frame, final_end_frame

def _plot_analysis_generic(
    title_suffix, raw_ssim, smoothed_ssim, slopes, 
    start_frame, end_frame, 
    slope_thresh_val, active_frames_for_plot
):
    """
    一个通用的内部辅助函数，用于绘制和分析结果。
    """
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        print("警告：未能设置中文字体，图表标签可能显示不正常。")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    fig.suptitle(f"页面加载时间分析结果 {title_suffix}", fontsize=16)
    frames = np.arange(len(raw_ssim))

    ax1.plot(frames, raw_ssim, label='原始SSIM', alpha=0.4, color='gray', linestyle=':')
    ax1.plot(frames, smoothed_ssim, label='平滑后SSIM', color='blue')
    if len(active_frames_for_plot) > 0:
        ax1.plot(active_frames_for_plot, smoothed_ssim[active_frames_for_plot], 'x', color='purple', markersize=6, label='活动点 (基于当前阈值)')
    ax1.set_ylabel('SSIM 得分')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2.plot(frames, slopes, label='斜率 (变化率)', color='green')
    ax2.axhline(slope_thresh_val, color='orange', linestyle='--', label=f'斜率阈值 ({slope_thresh_val:.3f})')
    ax2.axhline(-slope_thresh_val, color='orange', linestyle='--')
    ax2.set_xlabel('帧号 (Frames)')
    ax2.set_ylabel('斜率')
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    if start_frame != -1:
        ax1.axvline(start_frame, color='green', linestyle='-', linewidth=2, label=f'加载开始 @ {start_frame}')
        ax2.axvline(start_frame, color='green', linestyle='-', linewidth=2)
    if end_frame != -1:
        ax1.axvline(end_frame, color='red', linestyle='-', linewidth=2, label=f'加载结束 @ {end_frame}')
        ax2.axvline(end_frame, color='red', linestyle='-', linewidth=2)

    ax1.legend(loc='best')
    ax2.legend(loc='best')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

# --- 主程序入口 (与之前版本相同，此处为简洁省略，实际使用时请包含) ---
if __name__ == '__main__':
    print("-" * 30)
    ssim_pt_path = "processed_action_items/12/226_72s/ssim_sequence.pt" # 示例路径
    raw_ssim_data = []
    try:
        print(f"正在从 PyTorch 文件加载数据: {ssim_pt_path}"); loaded_ssim_tensor = torch.load(ssim_pt_path)
        raw_ssim_data = loaded_ssim_tensor.tolist(); print("数据加载成功。")
    except FileNotFoundError: print(f"❌ 错误：找不到文件 '{ssim_pt_path}'。")
    except Exception as e: print(f"❌ 错误：加载文件时发生未知错误: {e}")
    cleaned_data = preprocess_ssim_data(raw_ssim_data)
    if cleaned_data:
        START_FRAME, END_FRAME = find_page_load_intelligent(
            ssim_sequence=cleaned_data, smooth_window=3, activity_threshold=0.015,
            cluster_separation_threshold=45, start_search_window_duration=7, fps=30)
        print("-" * 30)
        if START_FRAME != -1 and END_FRAME != -1:
            load_duration = END_FRAME - START_FRAME; load_duration_seconds = load_duration / 30
            print(f"✅ 检测完成 (最终优化版): \n   - 页面加载开始于第 {START_FRAME} 帧。\n   - 页面加载结束于第 {END_FRAME} 帧。\n   - 加载持续时间: {load_duration} 帧 (约 {load_duration_seconds:.2f} 秒)。")
        else: print("❌ 未能检测到完整的加载过程。")
    else: print("错误：经过预处理后，没有有效的SSIM数据可供分析。")