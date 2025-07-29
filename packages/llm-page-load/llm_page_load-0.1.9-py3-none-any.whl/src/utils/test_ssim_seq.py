from .video_pre_tools import extract_frames_from_video
from .frame_ssim_seq_gen import calculate_temporal_ssim_vectors_mp, plot_temporal_ssim_vectors
from .frame_ssim_seq_gen_gpu import calculate_temporal_ssim_vectors_gpu
import torch
def main():
    video_path = "test_data/test_cfr_fps30.mp4"
    start_time = 0
    end_time = 60
    frames = extract_frames_from_video(video_path,start_time,end_time)
    offsets = [1,10,30,90]
    if torch.cuda.is_available():
        ssim_vectors = calculate_temporal_ssim_vectors_gpu(frames, offsets,convert_to_gray=True,batch_size=128)
    else:
        ssim_vectors = calculate_temporal_ssim_vectors_mp(frames, offsets,convert_to_gray=True,num_workers=48)
    plot_temporal_ssim_vectors(ssim_vectors, offsets,x_axis_type="time",output_path="test_ssim_seq.png")

if __name__ == "__main__":
    main()