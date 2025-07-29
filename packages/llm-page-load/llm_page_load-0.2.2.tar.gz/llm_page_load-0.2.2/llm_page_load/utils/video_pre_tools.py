import os
import subprocess
import shutil
import numpy as np
from moviepy import VideoFileClip
import imageio
from typing import List, Optional, Union # 导入所需的类型

# Pillow is often a dependency for MoviePy for certain operations or warnings,
# ensure it's available or handle potential warnings if not strictly needed for this.
try:
    from PIL import Image # Check if Pillow is available
except ImportError:
    print("Pillow (PIL) not found. Some MoviePy functionalities might be limited or show warnings.")


def get_video_duration_ffmpeg(video_path: str) -> Optional[float]:
    """使用 ffprobe 获取视频时长 (秒)"""
    if shutil.which("ffprobe") is None:
        print("警告：找不到 ffprobe。无法获取视频时长。")
        return None
    if not os.path.exists(video_path):
        print(f"警告：文件 '{video_path}' 不存在。无法获取视频时长。")
        return None

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if process.returncode == 0 and process.stdout.strip():
            return float(process.stdout.strip())
        else:
            print(f"获取视频时长失败。ffprobe stderr: {process.stderr.strip()}")
            return None
    except Exception as e:
        print(f"执行 ffprobe 获取时长时出错: {e}")
        return None


def cut_video_segment_ffmpeg_cli(
    input_video_path: str,
    output_video_path: str,
    start_time: Union[float, str], # 秒数或 "HH:MM:SS.xxx" 格式
    end_time: Union[float, str],   # 秒数或 "HH:MM:SS.xxx" 格式
    re_encode: bool = False,       # False 表示流复制 (快速但不精确到帧，不改编码), True 表示重新编码 (慢但精确，可改编码)
    # --- 重新编码参数 (仅当 re_encode=True 时有效) ---
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    crf: Optional[int] = 23,        # Constant Rate Factor, 仅用于某些视频编码器如 libx264
    video_bitrate: Optional[str] = None, # 例如 "2000k", 如果设置则可能覆盖CRF效果
    preset: str = "medium",         # FFmpeg 编码预设
    audio_bitrate: Optional[str] = "128k",
    # --- 通用参数 ---
    threads: Optional[int] = None,
    overwrite: bool = True,
    realtime_output: bool = True # 是否实时输出 FFmpeg 日志到终端
) -> bool:
    """
    使用 FFmpeg 命令行切割视频的特定片段。

    参数:
    - input_video_path (str): 输入视频文件路径。
    - output_video_path (str): 输出子视频文件路径。
    - start_time (Union[float, str]): 切割开始时间 (秒或 "HH:MM:SS.xxx")。
    - end_time (Union[float, str]): 切割结束时间 (秒或 "HH:MM:SS.xxx")。
    - re_encode (bool): 
        - False (默认): 使用流复制 (`-c copy`)。速度极快，不改变编码。
                         切割点可能不完全精确到帧 (通常在最近的关键帧)。
        - True: 对选定片段进行重新编码。速度较慢，但切割点更精确，
                并且可以改变视频/音频的编码参数。
    - video_codec (str): (re_encode=True 时) 视频编码器。
    - audio_codec (str): (re_encode=True 时) 音频编码器。
    - crf (Optional[int]): (re_encode=True 时) CRF值，用于如 libx264。
    - video_bitrate (Optional[str]): (re_encode=True 时) 视频目标比特率，如 "2M"。
    - preset (str): (re_encode=True 时) FFmpeg 编码预设。
    - audio_bitrate (Optional[str]): (re_encode=True 时) 音频比特率。
    - threads (Optional[int]): FFmpeg 使用的线程数。
    - overwrite (bool): 是否覆盖已存在的输出文件。
    - realtime_output (bool): 是否将 FFmpeg 的日志实时输出到终端。

    返回:
    - bool: 如果操作成功则返回 True，否则返回 False。
    """

    if shutil.which("ffmpeg") is None:
        print("错误：找不到 FFmpeg。请确保 FFmpeg 已安装并在系统的 PATH 环境变量中。")
        return False

    if not os.path.exists(input_video_path):
        print(f"错误：输入文件 '{input_video_path}' 未找到。")
        return False

    # 将时间转换为秒 (如果它们已经是字符串格式如 HH:MM:SS，FFmpeg可以直接处理)
    # 为了计算 duration，我们最好还是都转成 float
    def time_to_seconds(t: Union[float, str]) -> float:
        if isinstance(t, str):
            try:
                parts = t.split(':')
                sec = 0.0
                if len(parts) == 3: # HH:MM:SS.ms
                    sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2: # MM:SS.ms
                    sec = int(parts[0]) * 60 + float(parts[1])
                elif len(parts) == 1: # SS.ms
                    sec = float(parts[0])
                else:
                    raise ValueError("时间格式无效")
                return sec
            except ValueError:
                print(f"警告：无法解析时间字符串 '{t}'，假设它已经是秒数。")
                # 尝试直接转为 float，如果失败则会抛出异常由调用者处理或进一步检查
                return float(t) # 这可能再次引发 ValueError
        return float(t)

    try:
        start_s = time_to_seconds(start_time)
        end_s = time_to_seconds(end_time)
    except ValueError as e:
        print(f"错误：无效的时间参数格式 - {e}")
        return False
        
    if start_s < 0:
        print("警告：开始时间小于0，将从0开始。")
        start_s = 0.0
    
    duration_s = end_s - start_s
    if duration_s <= 0:
        print(f"错误：计算得到的持续时间 ({duration_s}s) 无效。结束时间必须大于开始时间。")
        return False

    # (可选) 检查时间是否超出视频总长，尽管 FFmpeg 通常能处理
    video_actual_duration = get_video_duration_ffmpeg(input_video_path)
    if video_actual_duration is not None:
        if start_s >= video_actual_duration:
            print(f"错误：开始时间 ({start_s}s) 超出或等于视频总时长 ({video_actual_duration}s)。")
            return False
        if end_s > video_actual_duration:
            print(f"警告：结束时间 ({end_s}s) 超出视频总时长 ({video_actual_duration}s)。将切割到视频末尾。")
            duration_s = video_actual_duration - start_s
            if duration_s <=0:
                 print(f"错误：调整后的持续时间 ({duration_s}s) 无效。")
                 return False


    # 创建输出目录 (如果不存在)
    output_dir = os.path.dirname(output_video_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"错误：无法创建输出目录 '{output_dir}': {e}")
            return False
            
    if os.path.exists(output_video_path) and not overwrite:
        print(f"错误：输出文件 '{output_video_path}' 已存在，并且 overwrite 设置为 False。")
        return False

    command: List[str] = ["ffmpeg"]
    if overwrite:
        command.extend(["-y"])
    else:
        command.extend(["-n"])

    # 对于快速切割，-ss 通常放在 -i 之前
    # 对于重新编码时更精确的定位（但可能较慢的查找），-ss 可以放在 -i 之后
    # 为了速度，这里我们主要将 -ss 放在前面
    command.extend(["-ss", str(start_s)])
    command.extend(["-i", input_video_path])
    command.extend(["-t", str(duration_s)]) # 使用计算出的持续时间

    if re_encode:
        print(f"模式：重新编码片段从 {start_s:.2f}s，持续 {duration_s:.2f}s")
        command.extend(["-c:v", video_codec])
        if video_bitrate:
            command.extend(["-b:v", video_bitrate])
            if crf is not None: # 通常比特率和CRF是互斥的质量控制方法
                 print(f"警告：同时指定了 video_bitrate ({video_bitrate}) 和 CRF ({crf})。通常只使用其中一个。FFmpeg 将优先考虑比特率（取决于具体编解码器行为）。")
        elif crf is not None and video_codec in ["libx264", "libx265", "libvpx-vp9", "libsvtav1", "libaom-av1"]:
            command.extend(["-crf", str(crf)])
        
        command.extend(["-preset", preset])
        
        if audio_codec:
            command.extend(["-c:a", audio_codec])
            if audio_bitrate:
                command.extend(["-b:a", audio_bitrate])
        else: # 如果不指定音频编码，尝试复制或静音
            command.extend(["-an"]) # 无音频
            print("警告：未指定音频编码器 (audio_codec)，将输出无音频视频。如果需要音频，请指定 audio_codec。")

        if threads is not None:
            command.extend(["-threads", str(threads)])
    else: # 流复制
        print(f"模式：流复制片段从 {start_s:.2f}s，持续 {duration_s:.2f}s (快速，但开始点可能不精确到帧)")
        command.extend(["-c", "copy"])
        command.extend(["-avoid_negative_ts", "make_zero"]) # 避免时间戳问题
        # command.extend(["-map_metadata", "0"]) # 复制全局元数据 (可选)

    # 对于 MP4 输出，添加 faststart 标志使得视频可以在下载时就开始播放
    if output_video_path.lower().endswith(".mp4"):
        command.extend(["-movflags", "+faststart"])
        
    command.append(output_video_path)

    print(f"执行命令: {' '.join(command)}")
    if realtime_output:
        print("--- FFmpeg 输出开始 ---")

    try:
        process = subprocess.run(
            command,
            capture_output=(not realtime_output), # 如果实时输出，则不捕获
            text=(not realtime_output),           # 同上
            check=False
        )
        
        if realtime_output:
            print("--- FFmpeg 输出结束 ---")

        if process.returncode == 0:
            print(f"FFmpeg 成功完成切割。输出文件: {output_video_path}")
            return True
        else:
            if not realtime_output: # 如果没有实时输出，现在打印捕获的错误
                print("FFmpeg 执行过程中发生错误:")
                print("--- STDOUT ---")
                print(process.stdout)
                print("--- STDERR ---")
                print(process.stderr)
            else: # 错误信息已经实时显示了
                print(f"FFmpeg 执行过程中发生错误 (返回码: {process.returncode}). "
                      "请查看上面终端输出的 FFmpeg 日志获取详细信息。")
            return False

    except FileNotFoundError:
        if realtime_output: print("--- FFmpeg 输出结束 ---")
        print("错误：找不到 FFmpeg 可执行文件。")
        return False
    except Exception as e:
        if realtime_output: print("--- FFmpeg 输出结束 ---")
        print(f"执行 FFmpeg 命令时发生意外错误: {e}")
        return False


def convert_to_cfr_ffmpeg_cli_realtime_output(
    input_path: str,
    output_path: Optional[str] = None,
    target_fps: int = 30,
    video_codec: str = "libx264",
    crf: int = 23,
    preset: str = "medium",
    audio_codec: str = "aac",
    audio_bitrate: str = "128k",
    threads: Optional[int] = None,
    overwrite: bool = True
) -> Optional[str]:
    """
    使用 FFmpeg 命令行直接将视频转换为固定帧率 (CFR) 和其他指定参数，
    并将 FFmpeg 的输出实时打印到终端。

    参数:
    - input_path (str): 输入视频文件的路径。
    - output_path (Optional[str]): 输出视频文件的路径。
                                   如果为 None，则在输入文件名后添加 "_cfr_fps[target_fps]"。
    - target_fps (int): 目标固定帧率，例如 30。
    - video_codec (str): 视频编解码器，例如 "libx264"。
    - crf (int): Constant Rate Factor (CRF) 值 (通常用于 libx264/libx265)。
    - preset (str): FFmpeg 的 preset 值 (例如 "ultrafast", "medium", "slow")。
    - audio_codec (str): 音频编解码器，例如 "aac"。
    - audio_bitrate (str): 音频比特率，例如 "128k"。
    - threads (Optional[int]): FFmpeg 使用的线程数。如果为 None 或 0，FFmpeg 会自动选择。
    - overwrite (bool): 如果输出文件已存在，是否覆盖。True 则覆盖，False 则不执行并报错。

    返回:
    - Optional[str]: 如果成功，返回输出文件的路径；否则返回 None。
    """

    if shutil.which("ffmpeg") is None:
        print("错误：找不到 FFmpeg。请确保 FFmpeg 已安装并在系统的 PATH 环境变量中。")
        return None

    if not os.path.exists(input_path):
        print(f"错误：输入文件 '{input_path}' 未找到。")
        return None

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cfr_fps{target_fps}{ext}"
    
    if os.path.exists(output_path) and not overwrite:
        print(f"错误：输出文件 '{output_path}' 已存在，并且 overwrite 设置为 False。")
        return None

    print(f"开始使用 FFmpeg CLI 转换视频: {input_path}")
    print(f"输出到: {output_path}")
    print(f"目标参数: FPS={target_fps}, VCodec={video_codec}, CRF={crf}, Preset={preset}, ACodec={audio_codec}, ABitrate={audio_bitrate}")

    command: List[str] = ["ffmpeg"]
    if overwrite:
        command.extend(["-y"])
    else:
        command.extend(["-n"])

    command.extend(["-i", input_path])
    command.extend(["-vf", f"fps={target_fps}"])
    command.extend(["-c:v", video_codec])

    if video_codec in ["libx264", "libx265", "libsvtav1", "libaom-av1"]:
        command.extend(["-crf", str(crf)])
    else:
        print(f"警告: 视频编解码器 '{video_codec}' 可能不直接支持 CRF={crf}。确保参数兼容。")

    command.extend(["-preset", preset])
    command.extend(["-c:a", audio_codec])
    command.extend(["-b:a", audio_bitrate])

    if threads is not None:
        command.extend(["-threads", str(threads)])
    
    command.append(output_path)

    print(f"执行命令: {' '.join(command)}")
    print("--- FFmpeg 输出开始 ---")

    try:
        # 执行命令，不捕获 stdout 和 stderr，使其直接输出到终端
        # universal_newlines=True (或 text=True in Python 3.7+) is not needed here
        # as we are not capturing the output to Python variables.
        process = subprocess.run(
            command,
            check=False # 我们将手动检查返回码
            # stdout 和 stderr 默认继承父进程，所以会直接打印到终端
        )
        
        print("--- FFmpeg 输出结束 ---")

        if process.returncode == 0:
            print(f"FFmpeg 成功完成转换。输出文件: {output_path}")
            return output_path
        else:
            # FFmpeg 的错误信息应该已经直接打印到终端了
            print(f"FFmpeg 执行过程中发生错误 (返回码: {process.returncode}). "
                  "请查看上面终端输出的 FFmpeg 日志获取详细信息。")
            return None

    except FileNotFoundError:
        print("--- FFmpeg 输出结束 ---")
        print("错误：找不到 FFmpeg 可执行文件。即使 shutil.which 通过了。")
        return None
    except Exception as e:
        print("--- FFmpeg 输出结束 ---")
        print(f"执行 FFmpeg 命令时发生意外错误: {e}")
        return None

def convert_to_cfr(input_path: str,
                   output_path: Optional[str] = None, # 修正类型提示
                   target_fps: int = 30,
                   video_codec: str = "libx264",
                   crf: int = 23,
                   preset: str = "medium",
                   audio_codec: str = "aac",
                   audio_bitrate: str = "128k",
                   threads: Optional[int] = None) -> Optional[str]: # 修正类型提示
    """
    使用 MoviePy 将视频转换为固定帧率 (CFR)。
    此函数会重新编码视频，以确保输出为指定的固定帧率。

    参数:
    - input_path (str): 输入视频文件的路径。
    - output_path (Optional[str]): 输出视频文件的路径。
                                   如果为 None，则在输入文件名后添加 "_cfr_fps[target_fps]"。
    - target_fps (int): 目标固定帧率，例如 30。
    - video_codec (str): 视频编解码器，例如 "libx264"。
    - crf (int): Constant Rate Factor (CRF) 值，用于 libx264 编码 (范围 0-51，越低质量越好)。
    - preset (str): FFmpeg 的 preset 值，影响编码速度和压缩率 (例如 "ultrafast", "medium", "slow")。
    - audio_codec (str): 音频编解码器，例如 "aac"。
    - audio_bitrate (str): 音频比特率，例如 "128k"。
    - threads (Optional[int]): 用于编码的线程数。默认为 MoviePy 的自动选择 (通常是 CPU 核心数)。

    返回:
    - Optional[str]: 如果成功，返回输出文件的路径；否则返回 None。
    """
    if not os.path.exists(input_path):
        print(f"错误：输入文件 '{input_path}' 未找到。")
        return None

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cfr_fps{target_fps}{ext}"

    print(f"开始转换视频: {input_path}")
    print(f"输出到: {output_path}")
    print(f"目标参数: FPS={target_fps}, Codec={video_codec}, CRF={crf}, Preset={preset}, AudioCodec={audio_codec}, AudioBitrate={audio_bitrate}")

    clip = None
    try:
        clip = VideoFileClip(input_path)
        ffmpeg_custom_params = ["-crf", str(crf)]

        clip.write_videofile(
            output_path,
            fps=target_fps,
            codec=video_codec,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            preset=preset,
            ffmpeg_params=ffmpeg_custom_params,
            threads=threads if threads else os.cpu_count(),
            logger='bar'
        )
        print(f"视频已成功转换为 CFR 并保存到: {output_path}")
        return output_path

    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return None
    finally:
        if clip:
            clip.close()

def cut_video_segment(
    input_video_path: str,
    output_video_path: str,
    start_time: float,
    end_time: float,
    video_codec: str = "libx264", # 默认视频编码器
    audio_codec: str = "aac",   # 默认音频编码器
    threads: Optional[int] = None,      # 编码线程数
    preset: str = "medium",       # FFmpeg 预设 (影响编码速度和压缩率)
    logger: Optional[str] = 'bar' # 显示进度条，设为 None 则不显示
) -> bool:
    """
    使用 MoviePy 从输入视频中切割出指定时间段的子视频。

    参数:
    - input_video_path (str): 输入视频文件的完整路径。
    - output_video_path (str): 切割后子视频的保存路径。
    - start_time (float): 子视频的开始时间 (单位：秒)。
    - end_time (float): 子视频的结束时间 (单位：秒)。
    - video_codec (str): 输出视频的视频编码器 (例如 'libx264', 'mpeg4')。
    - audio_codec (str): 输出视频的音频编码器 (例如 'aac', 'libmp3lame')。
    - threads (Optional[int]): 用于编码的线程数。None 表示 MoviePy/FFmpeg 自动选择。
    - preset (str): FFmpeg 的编码预设 (例如 'ultrafast', 'medium', 'slow')。
    - logger (Optional[str]): MoviePy 日志记录器。'bar' 会显示进度条。

    返回:
    - bool: 如果切割成功则返回 True，否则返回 False。
    """

    if not os.path.exists(input_video_path):
        print(f"错误：输入视频文件 '{input_video_path}' 未找到。")
        return False

    if start_time < 0:
        print(f"警告：开始时间 {start_time}s 小于 0，将从 0s 开始。")
        start_time = 0

    if end_time <= start_time:
        print(f"错误：结束时间 ({end_time}s) 必须大于开始时间 ({start_time}s)。")
        return False

    # 创建输出目录 (如果不存在)
    output_dir = os.path.dirname(output_video_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"已创建输出目录: {output_dir}")
        except OSError as e:
            print(f"错误：无法创建输出目录 '{output_dir}': {e}")
            return False
    
    main_clip: Optional[VideoFileClip] = None
    sub_clip_obj: Optional[VideoFileClip] = None

    try:
        # 1. 加载主视频剪辑
        main_clip = VideoFileClip(input_video_path)

        # 检查时间范围是否有效
        if start_time >= main_clip.duration:
            print(f"错误：开始时间 ({start_time}s) 超出或等于视频总时长 ({main_clip.duration}s)。")
            return False
        
        # MoviePy 的 subclip 会自动将超出视频时长的 end_time 限制在视频末尾
        # 但我们也可以显式地做一下说明或调整
        if end_time > main_clip.duration:
            print(f"警告：结束时间 ({end_time}s) 超出视频总时长 ({main_clip.duration}s)。")
            print(f"将剪辑到视频末尾 ({main_clip.duration}s)。")
            # end_time = main_clip.duration # subclip会自动处理，无需手动设置

        print(f"正在从 '{input_video_path}' 切割 [{start_time}s - {end_time}s]...")

        # 2. 创建子剪辑
        sub_clip_obj = main_clip.subclipped(start_time, end_time)

        # 3. 将子剪辑写入文件
        # write_videofile 总是会重新编码。
        # 如果需要尽可能无损，且格式允许，需要直接使用 ffmpeg -c copy
        print(f"正在将子剪辑保存到 '{output_video_path}'...")
        sub_clip_obj.write_videofile(
            output_video_path,
            codec=video_codec,
            audio_codec=audio_codec,
            threads=threads if threads else os.cpu_count(), # 使用所有可用核心数或指定数量
            preset=preset,
            logger=logger
        )
        print("子视频切割并保存成功！")
        return True

    except Exception as e:
        print(f"处理视频时发生错误: {e}")
        import traceback
        traceback.print_exc() # 打印详细的错误堆栈信息
        return False
    finally:
        # 4. 关闭剪辑以释放资源
        if sub_clip_obj:
            try:
                sub_clip_obj.close()
            except Exception as e:
                print(f"关闭子剪辑时出错: {e}")
        if main_clip:
            try:
                main_clip.close()
            except Exception as e:
                print(f"关闭主剪辑时出错: {e}")






def extract_frames_from_video(
    video_path: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    frame_interval: int = 1,  # 新增参数：帧提取间隔
    output_folder: Optional[str] = None,
    frame_filename_prefix: str = "frame_",
    filename_padding: int = 5
) -> List[np.ndarray]:
    """
    从视频中提取指定时间范围内的帧序列，并可以按指定间隔提取。

    如果未提供 start_time 和 end_time，则提取整个视频的帧。
    如果提供了 output_folder，则会将提取的帧保存为图像文件。

    参数:
    - video_path (str): 输入视频文件的路径。
    - start_time (Optional[float]): 开始提取的时间点 (秒)。默认为 None (从头开始)。
    - end_time (Optional[float]): 结束提取的时间点 (秒)。默认为 None (到视频末尾)。
    - frame_interval (int): 帧提取间隔。例如，1 表示提取所有帧，
                            2 表示每隔一帧提取一帧 (即提取第0, 2, 4,...帧)。默认为 1。
    - output_folder (Optional[str]): 保存提取帧的文件夹路径。如果为 None，则不保存帧。
    - frame_filename_prefix (str): 保存帧文件时的文件名前缀。
    - filename_padding (int): 保存的帧文件序号的位数，用于补零 (例如 5 表示 frame_00001.png)。

    返回:
    - List[np.ndarray]: 包含视频帧 (NumPy 数组) 的列表。如果发生错误则返回空列表。
    """
    if VideoFileClip is None:
        print("MoviePy 未成功加载，无法执行 extract_frames_from_video。")
        return []

    if not os.path.exists(video_path):
        print(f"错误：输入视频文件 '{video_path}' 未找到。")
        return []

    if not isinstance(frame_interval, int) or frame_interval <= 0:
        print(f"错误：frame_interval 必须是大于0的整数。得到: {frame_interval}。将使用默认值 1。")
        frame_interval = 1

    extracted_frames: List[np.ndarray] = []
    
    try:
        # 使用 'with' 语句自动管理 clip.close()
        with VideoFileClip(video_path) as clip:
            video_fps = clip.fps
            video_duration = clip.duration

            if video_fps is None or video_duration is None:
                print(f"错误：无法获取视频 '{video_path}' 的 FPS 或时长。")
                return []

            actual_start_time = 0.0 if start_time is None else max(0.0, start_time)
            actual_end_time = video_duration if end_time is None else min(video_duration, end_time)

            if actual_start_time >= actual_end_time:
                print(f"错误：开始时间 ({actual_start_time}s) 必须小于结束时间 ({actual_end_time}s)。")
                return []

            print(f"将从 '{video_path}' 提取帧:")
            print(f"  视频总时长: {video_duration:.2f}s, FPS: {video_fps:.2f}")
            print(f"  提取范围: 从 {actual_start_time:.2f}s 到 {actual_end_time:.2f}s")
            if frame_interval > 1:
                print(f"  提取间隔: 每隔 {frame_interval-1} 帧提取一帧 (即每 {frame_interval} 帧取一帧)")
            
            # 创建子剪辑的上下文管理器
            target_clip_instance = None # 用于确保 subclip 被正确关闭
            if actual_start_time > 0 or actual_end_time < video_duration:
                target_clip_instance = clip.subclipped(actual_start_time, actual_end_time)
                target_clip_to_iterate = target_clip_instance
                print(f"  已创建子剪辑，时长: {target_clip_to_iterate.duration:.2f}s")
            else:
                target_clip_to_iterate = clip # 直接迭代原始（完整）剪辑
                print("  将处理整个视频剪辑。")

            try:
                # 计数器，用于按 frame_interval 提取帧
                # 以及用于保存文件时的连续命名
                original_frame_iterator_idx = 0 
                saved_frame_counter = 0 # 已保存/提取的帧计数

                if output_folder:
                    os.makedirs(output_folder, exist_ok=True)
                    print(f"  帧将保存到: '{output_folder}'")

                # MoviePy 的 iter_frames 会根据剪辑的 FPS 返回帧
                # 我们在其基础上进行隔帧提取
                for frame in target_clip_to_iterate.iter_frames(
                                        fps=target_clip_to_iterate.fps, # 按原始帧率迭代
                                        logger='bar' if output_folder and frame_interval == 1 else None # 仅在提取所有帧时显示默认进度条
                                    ):
                    if original_frame_iterator_idx % frame_interval == 0:
                        extracted_frames.append(frame)
                        if output_folder:
                            # 文件名序号基于已提取的帧数 (saved_frame_counter)
                            filename = f"{frame_filename_prefix}{saved_frame_counter + 1:0{filename_padding}d}.png"
                            filepath = os.path.join(output_folder, filename)
                            try:
                                imageio.imwrite(filepath, frame)
                            except Exception as e_save:
                                print(f"保存帧 {filepath} 失败: {e_save}")
                        saved_frame_counter += 1
                    original_frame_iterator_idx += 1
                
                print(f"成功提取 {len(extracted_frames)} 帧。")

            finally: # 确保子剪辑被关闭（如果创建了的话）
                if target_clip_instance is not None:
                    target_clip_instance.close()
        
        return extracted_frames

    except Exception as e:
        print(f"提取帧过程中发生错误: {e}")
        import traceback
        traceback.print_exc() # 打印详细错误信息
        return []





if __name__ == '__main__':
    # ---- 使用示例 ----
    # 假设你有一个名为 "my_video.mp4" 的视频在脚本同目录下
    input_video = "test_data/test.mp4" # 请将此替换为您的视频文件名
    output_video = "test_data/test_cfr_fps30.mp4"

    # 1. 基本转换，使用默认输出名
    output_file1 = convert_to_cfr_ffmpeg_cli_realtime_output(input_video,output_path=output_video)
    if output_file1:
        print(f"示例1 完成: {output_file1}")
    else:
        print(f"示例1 转换失败。")

    print("-" * 30)


    # frames = extract_frames_from_video(output_file1,
    #                                 start_time=5.5,
    #                                 end_time=10.2)

    # if frames:
    #     print(f"从视频中提取了 {len(frames)} 帧。")
    #     # 你现在可以对这些帧 (NumPy 数组) 进行处理
    #     # 例如：average_pixel_value = frames[0].mean()
        
        
        
    print(f"\n--- 测试切割视频 '{input_video}' ---")
    print("\n--- 示例 1: 快速流复制切割 (5s - 15s) ---")
    start1 = 5.0
    end1 = 15.0
    output_fast_cut = "output_data/output_cut_fast.mp4"
    success1 = cut_video_segment_ffmpeg_cli(
        input_video,
        output_fast_cut,
        start_time=start1,
        end_time=end1,
        re_encode=False, # 关键：使用流复制
        realtime_output=True
    )
    if success1:
        print(f"快速切割成功: {output_fast_cut}")
        duration1 = get_video_duration_ffmpeg(output_fast_cut)
        if duration1 is not None:
            print(f"  输出视频时长: {duration1:.2f}s (预期约 {(end1-start1):.2f}s)")
    else:
        print("快速切割失败。")