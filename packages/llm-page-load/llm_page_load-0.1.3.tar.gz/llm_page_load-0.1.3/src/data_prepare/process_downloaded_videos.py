#!/usr/bin/env python3
"""
完整的视频数据处理流程：
1. 将downloaded_videos的新格式JSON转换为旧格式
2. 使用gen_seq_emb_for_tf_model.py生成模型训练数据
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_prepare.convert_new_format_to_old import process_downloaded_videos_folder
from src.data_prepare.gen_seq_emb_for_tf_model import main_refactored


def main():
    parser = argparse.ArgumentParser(description="完整的视频数据处理流程")
    parser.add_argument("--downloaded_videos_dir", type=str, default="downloaded_videos", 
                       help="downloaded_videos文件夹路径")
    parser.add_argument("--converted_dir", type=str, default="downloaded_videos",
                       help="转换后的数据目录（转换后的JSON将保存在视频目录下）")
    parser.add_argument("--final_output_dir", type=str, default="downloaded_videos_processed",
                       help="最终处理输出目录")
    parser.add_argument("--overwrite_action_items", type=bool, default=False, 
                       help="是否覆盖已存在的处理结果")
    parser.add_argument("--save_all_extracted_frames", type=bool, default=True, 
                       help="是否将提取的帧保存为NumPy数组")
    parser.add_argument("--generate_ssim_sequence", type=bool, default=True, 
                       help="是否计算SSIM相似度序列")
    parser.add_argument("--save_frames_as_video", type=bool, default=True, 
                       help="是否将提取的帧保存为视频")
    parser.add_argument("--gpu_id", type=int, default=None, 
                       help="指定使用的GPU ID")
    parser.add_argument("--skip_conversion", action="store_true",
                       help="跳过格式转换步骤（如果已经转换过）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("视频数据处理流程开始")
    print("=" * 60)
    
    # 步骤1：格式转换
    if not args.skip_conversion:
        print(f"\n步骤1: 转换 {args.downloaded_videos_dir} 中的JSON格式...")
        converted_files = process_downloaded_videos_folder(
            args.downloaded_videos_dir
        )
        
        if not converted_files:
            print("错误: 没有成功转换任何文件，请检查输入目录")
            return
        
        print(f"✓ 格式转换完成，共转换 {len(converted_files)} 个文件")
    else:
        print(f"\n步骤1: 跳过格式转换（使用已存在的 {args.downloaded_videos_dir}）")
        if not os.path.exists(args.downloaded_videos_dir):
            print(f"错误: 指定的转换目录 {args.downloaded_videos_dir} 不存在")
            return
    
    # 步骤2：生成模型训练数据
    print(f"\n步骤2: 生成模型训练数据...")
    print(f"输入目录: {args.downloaded_videos_dir}")
    print(f"输出目录: {args.final_output_dir}")
    
    try:
        main_refactored(
            data_dir=args.downloaded_videos_dir,
            overwrite_action_items=args.overwrite_action_items,
            save_all_extracted_frames=args.save_all_extracted_frames,
            generate_ssim_sequence=args.generate_ssim_sequence,
            save_frames_as_video=args.save_frames_as_video,
            get_json_video_pairs_func_name="v2",
            custom_detailed_output_dir=args.final_output_dir,
            target_gpu_id=args.gpu_id
        )
        print("✓ 模型训练数据生成完成")
    except Exception as e:
        print(f"错误: 生成模型训练数据失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("处理流程完成！")
    print("=" * 60)
    print(f"转换后的JSON文件: 保存在 {args.downloaded_videos_dir} 下的各视频目录中")
    print(f"详细的处理结果: {args.final_output_dir}")
    print(f"模型训练数据: 当前目录下的 .pt 文件")
    
    # 列出生成的模型文件
    pt_files = [f for f in os.listdir(".") if f.endswith('.pt') and 'train_data' in f]
    if pt_files:
        print(f"\n生成的模型文件:")
        for pt_file in pt_files:
            print(f"  - {pt_file}")


if __name__ == "__main__":
    main() 