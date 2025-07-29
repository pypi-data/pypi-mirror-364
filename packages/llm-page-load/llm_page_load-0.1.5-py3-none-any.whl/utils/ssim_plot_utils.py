import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List, Optional, Tuple, Dict
import os

def plot_temporal_ssim_vectors(
    ssim_vectors: List[List[Optional[float]]],
    offsets: List[int], # 注意：这里的offsets应该是排序且去重后的，与all_ssim_vectors的维度对应
    x_axis_type: str = "index",
    fps: Optional[float] = None,
    title: Optional[str] = None,
    ylabel: str = "SSIM Score",
    figure_size: Tuple[float, float] = (15, 8), # Increased height for images
    output_path: Optional[str] = None,
    legend_loc: str = "lower left",
    y_lim_padding: float = 0.05,
    show_plot: bool = False,
    event_times_sec: Optional[Dict[str, float]] = None, # Times relative to sequence start
    event_frame_image_paths: Optional[Dict[str, str]] = None # Paths to central frame images
) -> None:
    if not ssim_vectors:
        print("SSIM 向量列表为空，无法绘制图表。")
        return

    num_dimensions = 0
    # 尝试从第一个非空向量确定维度
    for vec in ssim_vectors:
        if vec and isinstance(vec, list): # 确保 vec 是列表且非空
            num_dimensions = len(vec)
            break
    
    if num_dimensions == 0 and ssim_vectors: # 如果所有内部列表都为空或 ssim_vectors 本身结构不对
        # 检查是否 ssim_vectors 是空的列表的列表，例如 [[]]
        if all(isinstance(v, list) and not v for v in ssim_vectors):
             print("SSIM 向量数据全部为空列表 (例如 [[] for _ in range(N)])，无法确定维度来绘制。")
        else:
             print("SSIM 向量数据无效或无法确定维度，无法绘制。")
        return
    elif not ssim_vectors: # 再次检查，以防万一
        return


    # 处理图例标签的 offsets
    # 这里的 offsets 参数应与 ssim_vectors[0] 的长度匹配
    effective_offsets_labels: List[str]
    if not offsets: # offsets 为空或 None
        if num_dimensions > 0:
            print("警告: offsets 列表为空，但 SSIM 向量有数据。将使用通用图例标签。")
            effective_offsets_labels = [f"Offset Index {i+1}" for i in range(num_dimensions)]
        else: # num_dimensions 也是0
            effective_offsets_labels = []
    elif len(offsets) != num_dimensions:
        print(f"警告: 提供的 offsets 数量 ({len(offsets)}) 与 SSIM 向量维度 ({num_dimensions}) 不匹配。图例可能不正确。将尝试使用提供的 offsets 生成标签。")
        effective_offsets_labels = [f"SSIM (t, t-{offset})" if isinstance(offset, int) else f"Offset {idx+1}" for idx, offset in enumerate(offsets[:num_dimensions])]
        if num_dimensions > len(offsets):
            for i in range(len(offsets), num_dimensions):
                effective_offsets_labels.append(f"Offset Index {i+1}")
    else: # offsets数量与维度匹配
        effective_offsets_labels = [f"SSIM (t, t-{offset})" for offset in offsets]


    num_frames_plot = len(ssim_vectors)
    x_values: np.ndarray
    actual_xlabel: str
    effective_x_axis_type = x_axis_type.lower() 

    if effective_x_axis_type == "time":
        if fps is None or fps <= 0:
            print("警告: x_axis_type 设置为 'time'，但未提供有效 FPS 或 FPS 无效。将默认使用帧索引作为X轴。")
            x_values = np.arange(num_frames_plot)
            actual_xlabel = "Frame Index (t)"
            effective_x_axis_type = "index" 
        else:
            x_values = np.arange(num_frames_plot) / fps
            actual_xlabel = "Time (seconds)"
    elif effective_x_axis_type == "index":
        x_values = np.arange(num_frames_plot)
        actual_xlabel = "Frame Index (t)"
    else:
        print(f"警告: 无效的 x_axis_type '{x_axis_type}'。将默认使用帧索引作为X轴。")
        x_values = np.arange(num_frames_plot)
        actual_xlabel = "Frame Index (t)"
        effective_x_axis_type = "index" 

    fig, ax_main = plt.subplots(figsize=figure_size)

    min_ssim_val = 1.1 
    max_ssim_val = -1.1 
    has_valid_data_points = False

    if num_dimensions > 0:
        for i in range(num_dimensions):
            current_ssim_series_list = []
            for vec_idx, vec in enumerate(ssim_vectors):
                if vec and i < len(vec) and vec[i] is not None:
                    current_ssim_series_list.append(vec[i])
                    has_valid_data_points = True 
                else: # vec is None, or shorter than i, or vec[i] is None
                    current_ssim_series_list.append(np.nan)
            
            current_ssim_series = np.array(current_ssim_series_list, dtype=float)
            
            if not np.all(np.isnan(current_ssim_series)):
                min_ssim_val = min(min_ssim_val, np.nanmin(current_ssim_series))
                max_ssim_val = max(max_ssim_val, np.nanmax(current_ssim_series))
            
            label = effective_offsets_labels[i] if i < len(effective_offsets_labels) else f"Dim {i+1}"
            ax_main.plot(x_values, current_ssim_series, marker='.', markersize=4, linestyle='-', label=label, alpha=0.8)
    else: # num_dimensions is 0, implies ssim_vectors was like [[]] or all Nones
        print("没有有效的SSIM数据维度可以绘制。")

    # Plot vertical lines for events
    event_colors = {
        "action_time": "red",
        "marked_response_time": "green",
        "marked_end_time": "blue",
        "response_start_time": "green", # Alias for legend consistency
        "load_end_time": "blue" # Alias for legend consistency
    }
    if event_times_sec:
        for event_name, time_val_sec in event_times_sec.items():
            x_coord_event = None
            if effective_x_axis_type == "time":
                x_coord_event = time_val_sec
            elif fps and fps > 0: # index type
                x_coord_event = time_val_sec * fps 
                if not (0 <= x_coord_event < num_frames_plot):
                    print(f"警告: 事件 '{event_name}' 的计算帧索引 {x_coord_event} 超出范围 [0, {num_frames_plot-1}]。时间: {time_val_sec:.2f}s")
                    continue
            else: # Cannot determine x_coord for index type without fps
                print(f"警告: 无法为事件 '{event_name}' 确定x坐标 (x_axis_type='index' 但fps无效)。")
                continue
            
            clean_event_name = event_name.replace('_', ' ').title()
            color = event_colors.get(event_name, "purple")
            ax_main.axvline(x=x_coord_event, color=color, linestyle='--', linewidth=1.2,
                            label=f"{clean_event_name} ({time_val_sec:.2f}s)")

    if title is None: 
        if effective_x_axis_type == "time" and fps is not None and fps > 0:
            plt.title(f"Temporal SSIM Scores vs. Time (Source FPS: {fps:.2f})")
        else:
            plt.title("Temporal SSIM Scores vs. Frame Index")
    else: 
        plt.title(title)

    ax_main.set_xlabel(actual_xlabel)
    ax_main.set_ylabel(ylabel)

    if has_valid_data_points: # Changed from has_valid_data
        y_range = max_ssim_val - min_ssim_val
        y_padding_val = y_range * y_lim_padding if y_range > 1e-6 else 0.05 
        
        y_lower = min_ssim_val - y_padding_val
        y_upper = max_ssim_val + y_padding_val

        y_lower_clamped = max(-1.05, y_lower) 
        y_upper_clamped = min(1.05, y_upper)

        if y_lower_clamped >= y_upper_clamped: # Fallback if range is problematic
            y_lower_clamped = -0.1 if min_ssim_val < 0 else 0.0 # Adjust based on typical SSIM
            y_upper_clamped = 1.05
            if min_ssim_val < -0.05: # If there are actual negative values
                 y_lower_clamped = -1.05

        ax_main.set_ylim(y_lower_clamped, y_upper_clamped)
    else: 
        ax_main.set_ylim(-0.05, 1.05) 

    if effective_x_axis_type == "time" and x_values.size > 0 and x_values.max() > 10 : 
        ax_main.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10, prune='both'))


    if num_dimensions > 0 and has_valid_data_points: 
        ax_main.legend(loc=legend_loc)
    ax_main.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout() 

    # Display critical frame images using inset axes at the bottom
    num_images_to_show = 0
    if event_frame_image_paths:
        valid_images = {k:p for k,p in event_frame_image_paths.items() if p and os.path.exists(p)}
        num_images_to_show = len(valid_images)
        
        if num_images_to_show > 0:
            img_height_fig_fraction = 0.15 # Fraction of figure height for each image row
            img_aspect_ratio = 16/9 # Assume typical video frame aspect ratio
            total_img_strip_height = img_height_fig_fraction
            
            # Adjust main plot to make space at the bottom
            fig.subplots_adjust(bottom=total_img_strip_height + 0.08) # Add some padding

            img_width_fig_fraction = (img_height_fig_fraction / img_aspect_ratio) * (figure_size[1]/figure_size[0]) 
            # Calculate width based on aspect ratio and figure aspect ratio
            # Or a simpler way: distribute available width
            total_available_width_fraction = 0.9 # Use 90% of figure width for images
            spacing_fraction = 0.02
            img_width_fig_fraction = (total_available_width_fraction - (num_images_to_show -1)*spacing_fraction) / num_images_to_show
            img_height_fig_fraction = img_width_fig_fraction * img_aspect_ratio * (figure_size[0]/figure_size[1]) # re-calc height to maintain aspect
            if img_height_fig_fraction > 0.15: # Cap height
                img_height_fig_fraction = 0.15
                img_width_fig_fraction = (img_height_fig_fraction / img_aspect_ratio) * (figure_size[1]/figure_size[0])

            current_x_pos = (1.0 - (num_images_to_show * img_width_fig_fraction + (num_images_to_show - 1) * spacing_fraction)) / 2.0 # Center the strip
            img_bottom_fig_fraction = 0.02

            sorted_event_keys = sorted(valid_images.keys(), key=lambda k: list(event_frame_image_paths.keys()).index(k)) # Keep original order if possible

            for i, event_key in enumerate(sorted_event_keys):
                img_path = valid_images[event_key]
                try:
                    img = plt.imread(img_path)
                    ax_inset = fig.add_axes([current_x_pos, img_bottom_fig_fraction, img_width_fig_fraction, img_height_fig_fraction])
                    ax_inset.imshow(img)
                    ax_inset.set_title(event_key.replace('_', ' ').title(), fontsize=7)
                    ax_inset.axis('off')
                    current_x_pos += (img_width_fig_fraction + spacing_fraction)
                except Exception as e_img:
                    print(f"错误: 加载或显示图片 {img_path} 失败: {e_img}")
    
    if num_images_to_show == 0:
        plt.tight_layout()

    if output_path:
        try:
            plt.savefig(output_path, dpi=150) 
            print(f"图表已保存到: {output_path}")
        except Exception as e:
            print(f"保存图表到 '{output_path}' 时出错: {e}")

    if show_plot:
        plt.show()
    
    plt.close(fig)