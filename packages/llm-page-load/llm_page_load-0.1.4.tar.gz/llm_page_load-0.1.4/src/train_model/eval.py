import torch
import os
import json
from datetime import datetime
from torch.utils.data import DataLoader
from .perf_video_ssim_seq_model_multi_gpu import ScreenRecordingDataset, collate_fn, evaluate_model_with_metrics, load_model, PAD_LABEL_ID, idx_to_label

def run_evaluation_only(model_path, test_data_paths, config=None, save_dir=None):
    """
    独立的评估函数，可以单独调用来评估已保存的模型
    
    Args:
        model_path: 模型文件路径
        test_data_paths: 测试数据文件路径列表
        config: 配置对象（可选，如果不提供将从模型文件中恢复）
        save_dir: 评估结果保存目录（可选）
    
    Returns:
        evaluation_results: 评估结果字典
    """
    # 加载测试数据
    test_set = []
    for t_path in test_data_paths:
        try:
            print(f"Loading test data from: {t_path}")
            loaded_data = torch.load(t_path)
            if isinstance(loaded_data, list):
                test_set.extend(loaded_data)
        except Exception as e:
            print(f"Warning: Error loading {t_path}: {e}")
    
    if not test_set:
        print("Error: No test data loaded.")
        return None
    
    print(f"Loaded {len(test_set)} test samples.")
    
    # 加载模型
    print(f"\nLoading model from: {model_path}")
    try:
        model_wrapper, optimizer, epoch, loss, loaded_config = load_model(
            model_path, 
            device=None,  # 让load_model自动选择设备
            config=config
        )
        
        # 获取use_crf信息
        checkpoint = torch.load(model_path, map_location='cpu')
        use_crf = checkpoint.get('use_crf', True)
        
        print(f"Successfully loaded model from epoch {epoch} with loss {loss:.4f}")
        print(f"Model configuration: d_model={loaded_config.d_model}, "
              f"nhead={loaded_config.nhead}, layers={loaded_config.num_encoder_layers}")
        print(f"Using CRF: {use_crf}")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 创建数据加载器
    test_dataset = ScreenRecordingDataset(test_set)
    test_dataloader = DataLoader(
        test_dataset, 
        batch_size=loaded_config.batch_size,
        shuffle=False, 
        collate_fn=collate_fn,
        num_workers=loaded_config.num_workers,
        pin_memory=loaded_config.pin_memory
    )
    
    # 设置保存目录
    if save_dir is None:
        model_dir = os.path.dirname(model_path)
        save_dir = os.path.join(model_dir, f'evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    # 运行评估
    evaluation_results = evaluate_model_with_metrics(
        model_wrapper,
        test_dataloader,
        loaded_config.device,
        idx_to_label,
        loaded_config,
        use_crf=use_crf,
        save_dir=save_dir,
        local_pad_label_id=PAD_LABEL_ID
    )
    
    # 保存评估配置信息
    if evaluation_results:
        eval_info = {
            "model_path": model_path,
            "test_data_paths": test_data_paths,
            "test_samples": len(test_set),
            "evaluation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_epoch": epoch,
            "model_config": loaded_config.to_dict()
        }
        
        with open(os.path.join(save_dir, 'evaluation_info.json'), 'w') as f:
            json.dump(eval_info, f, indent=4)
    
    return evaluation_results


# 使用示例：
if __name__ == "__main__":  # 设置为True来运行独立评估
    # 独立评估示例
    results = run_evaluation_only(
        model_path="saved_models_cpu/exp_20250601_081739/best_model.pt",
        test_data_paths=["part_1_test_data_fps30_offsets6_ssim_20250601.pt",
                        "part_2_test_data_fps30_offsets6_ssim_20250601.pt"],
        save_dir="evaluation_results/manual_eval_001"
    )
