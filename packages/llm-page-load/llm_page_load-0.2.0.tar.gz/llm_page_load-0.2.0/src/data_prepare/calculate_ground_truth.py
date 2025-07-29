#!/usr/bin/env python3
"""
计算ground truth并更新results.json
从action_info.json中提取时间信息，计算对应的帧索引
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional


def parse_case_key(case_key: str) -> tuple:
    """
    解析case_key，提取视频名和时间信息
    格式: "2025-07-03_1751514078822,VID_20250703_113456/1_15s"
    """
    try:
        # 分割视频名和时间
        video_part, time_part = case_key.split('/')
        
        # 解析时间部分 "1_15s" -> 1.15
        time_str = time_part.replace('s', '')
        if '_' in time_str:
            action_time_str, fraction_str = time_str.split('_')
            action_time = float(action_time_str) + float(fraction_str) / 100.0
        else:
            action_time = float(time_str)
            
        return video_part, action_time
    except Exception as e:
        print(f"解析case_key失败: {case_key}, 错误: {e}")
        return None, None


def find_action_info_file(video_name: str, action_time: float, processed_dirs: List[str]) -> Optional[str]:
    """
    在processed目录中查找对应的action_info.json文件
    """
    for processed_dir in processed_dirs:
        if not os.path.exists(processed_dir):
            continue
            
        # 查找匹配的视频目录
        for item in os.listdir(processed_dir):
            item_path = os.path.join(processed_dir, item)
            if not os.path.isdir(item_path):
                continue
                
            # 检查是否是目标视频（精确匹配）
            if video_name == item:
                # 查找对应时间点的action_info.json
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if not os.path.isdir(subitem_path):
                        continue
                        
                    # 检查时间是否匹配
                    time_str = f"{action_time:.0f}_{int(action_time % 1 * 100)}s"
                    if time_str in subitem:
                        action_info_path = os.path.join(subitem_path, "action_info.json")
                        if os.path.exists(action_info_path):
                            return action_info_path
    
    return None


def calculate_ground_truth_frame(action_info_path: str) -> Optional[int]:
    """
    从action_info.json计算ground truth帧索引
    """
    try:
        with open(action_info_path, 'r', encoding='utf-8') as f:
            action_info = json.load(f)
        
        # 提取关键信息
        original_action = action_info.get('original_action_item', {})
        extraction_params = action_info.get('extraction_parameters', {})
        
        marked_end_time = original_action.get('marked_end_time')
        extract_start_time_sec = extraction_params.get('extract_start_time_sec')
        fps = extraction_params.get('fps', 30)
        
        if marked_end_time is None or extract_start_time_sec is None:
            print(f"缺少必要的时间信息: marked_end_time={marked_end_time}, extract_start_time_sec={extract_start_time_sec}")
            return None
        
        # 计算ground truth帧索引
        # gt_frame = (marked_end_time - extract_start_time_sec) * fps
        gt_frame = int(round((marked_end_time - extract_start_time_sec) * fps))
        
        print(f"计算ground truth: marked_end_time={marked_end_time}s, extract_start_time_sec={extract_start_time_sec}s, fps={fps}")
        print(f"  gt_frame = ({marked_end_time} - {extract_start_time_sec}) * {fps} = {gt_frame}")
        
        return gt_frame
        
    except Exception as e:
        print(f"计算ground truth失败: {e}")
        return None


def update_results_with_ground_truth(results_path: str, processed_dirs: List[str]) -> Dict:
    """
    更新results.json，添加ground truth信息
    """
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
        
        updated_results = []
        total_cases = len(results_data.get('results', []))
        updated_cases = 0
        
        for result in results_data.get('results', []):
            case_key = result.get('case_key')
            if not case_key:
                continue
                
            # 解析case_key
            video_name, action_time = parse_case_key(case_key)
            if not video_name or action_time is None:
                print(f"跳过无效的case_key: {case_key}")
                updated_results.append(result)
                continue
            
            # 查找action_info.json
            action_info_path = find_action_info_file(video_name, action_time, processed_dirs)
            if not action_info_path:
                print(f"未找到action_info.json: {case_key}")
                updated_results.append(result)
                continue
            
            # 计算ground truth
            gt_end_frame = calculate_ground_truth_frame(action_info_path)
            if gt_end_frame is not None:
                # 更新结果
                result['gt_end_frame'] = gt_end_frame
                
                # 计算差异
                pred_end_frame = result.get('pred_end_frame')
                if pred_end_frame is not None:
                    diff = abs(pred_end_frame - gt_end_frame)
                    result['diff'] = diff
                    
                    # 更新match_type
                    if diff == 0:
                        result['match_type'] = 'perfect_match'
                    elif diff <= 3:
                        result['match_type'] = 'close_match'
                    elif diff <= 10:
                        result['match_type'] = 'mid_match'
                    else:
                        result['match_type'] = 'other_match'
                
                updated_cases += 1
                print(f"✓ 更新 {case_key}: gt_end_frame={gt_end_frame}")
            else:
                print(f"✗ 计算ground truth失败: {case_key}")
            
            updated_results.append(result)
        
        # 更新summary
        summary = results_data.get('summary', {})
        perfect_matches = sum(1 for r in updated_results if r.get('match_type') == 'perfect_match')
        close_matches = sum(1 for r in updated_results if r.get('match_type') == 'close_match')
        mid_matches = sum(1 for r in updated_results if r.get('match_type') == 'mid_match')
        other_matches = sum(1 for r in updated_results if r.get('match_type') == 'other_match')
        failed_cases = sum(1 for r in updated_results if r.get('match_type') == 'no_gt')
        
        summary.update({
            'perfect_matches': perfect_matches,
            'close_matches': close_matches,
            'mid_matches': mid_matches,
            'other_matches': other_matches,
            'failed_cases': failed_cases
        })
        
        return {
            'results': updated_results,
            'summary': summary
        }
        
    except Exception as e:
        print(f"更新results.json失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="计算ground truth并更新results.json")
    parser.add_argument("--results_path", type=str, required=True,
                       help="results.json文件路径")
    parser.add_argument("--processed_dirs", type=str, nargs='+', 
                       default=["downloaded_videos_processed", "downloaded_videos_processed_action_items"],
                       help="包含action_info.json的目录列表")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("开始计算ground truth并更新results.json")
    print("=" * 60)
    print(f"Results文件: {args.results_path}")
    print(f"处理目录: {args.processed_dirs}")
    
    # 更新results.json
    updated_data = update_results_with_ground_truth(args.results_path, args.processed_dirs)
    
    if updated_data:
        # 保存更新后的结果
        backup_path = args.results_path.replace('.json', '_backup.json')
        try:
            # 创建备份
            import shutil
            shutil.copy2(args.results_path, backup_path)
            print(f"已创建备份: {backup_path}")
        except Exception as e:
            print(f"创建备份失败: {e}")
        
        # 保存更新后的结果
        with open(args.results_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 更新完成！已保存到: {args.results_path}")
        
        # 显示统计信息
        summary = updated_data.get('summary', {})
        print(f"\n统计信息:")
        print(f"  总案例数: {summary.get('total_cases', 0)}")
        print(f"  完美匹配: {summary.get('perfect_matches', 0)}")
        print(f"  接近匹配: {summary.get('close_matches', 0)}")
        print(f"  中等匹配: {summary.get('mid_matches', 0)}")
        print(f"  其他匹配: {summary.get('other_matches', 0)}")
        print(f"  失败案例: {summary.get('failed_cases', 0)}")
        
    else:
        print("✗ 更新失败")


if __name__ == "__main__":
    main() 