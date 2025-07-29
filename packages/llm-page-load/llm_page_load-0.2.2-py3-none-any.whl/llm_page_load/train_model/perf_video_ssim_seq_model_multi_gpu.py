import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from torchcrf import CRF
import math
import random
import numpy as np
import copy
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import json
import optuna
from pathlib import Path

# 多GPU支持相关导入
import torch.distributed as dist
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.data.distributed import DistributedSampler
import torch.multiprocessing as mp

# --- 0. 全局常量定义 ---
PAD_LABEL_ID = -100
labels_map = {
    "O": 0,
    "LOADING": 1
}
num_classes = len(labels_map)
idx_to_label = {v: k for k, v in labels_map.items()}

# --- 1. 增强的配置参数（支持多GPU） ---
class Config:
    # 数据相关
    num_sequences = 500
    max_seq_len = 150
    min_seq_len = 50
    ssim_dim = 6
    num_op_types = 1
    op_type_embed_dim = 8
    include_operation_features = False
    validation_split = 0.2

    # 模型相关
    d_model = 64
    nhead = 2
    num_encoder_layers = 4
    dim_feedforward = 80
    dropout = 0.13948674899001207

    # 训练相关
    batch_size = 64  # 每个GPU的batch size
    val_batch_size = 64
    learning_rate = 0.0005995725881797109
    num_epochs = 200000
    CLASS_WEIGHTS_ALPHA = [0.1, 0.9]
    focal_loss_gamma = 8.0
    weight_decay = 1e-4

    # 早停相关
    early_stopping_patience = 1000
    early_stopping_min_delta = 0
    early_stopping_metric = 'val_loss'

    # 多GPU相关配置
    use_multi_gpu = True
    distributed = False
    world_size = -1
    rank = -1
    local_rank = -1
    backend = 'nccl'
    init_method = 'env://'
    
    # 数据加载相关
    num_workers = 0
    pin_memory = True
    
    # 其他
    device = None
    gpu_count = 0
    
    # 模型保存相关
    save_dir = "saved_models_cpu_focal_loss_8_class0109"
    experiment_name = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def __init__(self):
        """初始化配置，自动检测GPU"""
        self._setup_device()
    
    def _setup_device(self):
        """设置设备和多GPU配置"""
        if torch.cuda.is_available():
            self.gpu_count = torch.cuda.device_count()
            print(f"Found {self.gpu_count} GPU(s)")
            
            if self.distributed:
                # 分布式训练模式
                self.device = torch.device(f"cuda:{self.local_rank}")
                torch.cuda.set_device(self.device)
            else:
                # 单机多卡或单卡模式
                self.device = torch.device("cuda")
                if self.gpu_count > 1 and self.use_multi_gpu:
                    print(f"Using DataParallel with {self.gpu_count} GPUs")
                else:
                    print(f"Using single GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("No GPU available, using CPU")
            self.device = torch.device("cpu")
            self.use_multi_gpu = False
            self.distributed = False
            self.gpu_count = 0
    
    def get_effective_batch_size(self):
        """获取有效的批次大小（考虑多GPU）"""
        if self.distributed:
            return self.batch_size
        elif self.use_multi_gpu and self.gpu_count > 1:
            return self.batch_size * self.gpu_count
        else:
            return self.batch_size
    
    def to_dict(self):
        """将配置转换为字典（处理不能序列化的对象）"""
        config_dict = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            
            # 特殊处理不能直接序列化的对象
            if k == 'device':
                # 将device对象转换为字符串
                config_dict[k] = str(v) if v is not None else None
            elif k == 'CLASS_WEIGHTS_ALPHA':
                # 将tensor转换为列表
                if v is not None and hasattr(v, 'tolist'):
                    config_dict[k] = v.tolist()
                else:
                    config_dict[k] = v
            elif isinstance(v, torch.Tensor):
                # 处理其他可能的tensor
                config_dict[k] = v.tolist()
            elif isinstance(v, (int, float, str, bool, list, dict, type(None))):
                # 可以直接序列化的类型
                config_dict[k] = v
            else:
                # 其他类型转换为字符串
                config_dict[k] = str(v)
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict):
        """从字典创建配置"""
        config = cls()
        for k, v in config_dict.items():
            if k == 'device':
                # 从字符串恢复device对象
                if v is not None and v != 'None':
                    config.device = torch.device(v)
                else:
                    config.device = None
            elif k == 'CLASS_WEIGHTS_ALPHA':
                # 从列表恢复tensor
                if v is not None and isinstance(v, list):
                    config.CLASS_WEIGHTS_ALPHA = torch.tensor(v)
                else:
                    config.CLASS_WEIGHTS_ALPHA = v
            else:
                setattr(config, k, v)
        return config


# --- 2. 辅助函数：设置分布式训练 ---
def setup_distributed(rank, world_size, backend='nccl'):
    """初始化分布式训练环境"""
    os.environ['MASTER_ADDR'] = os.environ.get('MASTER_ADDR', 'localhost')
    os.environ['MASTER_PORT'] = os.environ.get('MASTER_PORT', '12355')
    
    # 初始化进程组
    dist.init_process_group(backend, rank=rank, world_size=world_size)
    
    # 设置当前进程使用的GPU
    torch.cuda.set_device(rank)
    
def cleanup_distributed():
    """清理分布式训练环境"""
    dist.destroy_process_group()

# --- 3. 数据并行包装器 ---
class ModelWrapper:
    """模型包装器，统一处理单GPU、DataParallel和DistributedDataParallel"""
    def __init__(self, model, config):
        self.config = config
        self.base_model = model
        
        if config.distributed:
            # 分布式数据并行
            self.model = DistributedDataParallel(
                model, 
                device_ids=[config.local_rank],
                output_device=config.local_rank,
                find_unused_parameters=True
            )
        elif config.use_multi_gpu and config.gpu_count > 1:
            # 数据并行
            self.model = DataParallel(model)
        else:
            # 单GPU或CPU
            self.model = model
    
    def get_base_model(self):
        """获取基础模型（去除并行包装）"""
        if isinstance(self.model, (DataParallel, DistributedDataParallel)):
            return self.model.module
        return self.model
    
    def train(self):
        """设置训练模式"""
        self.model.train()
    
    def eval(self):
        """设置评估模式"""
        self.model.eval()
    
    def __call__(self, *args, **kwargs):
        """前向传播"""
        output = self.model(*args, **kwargs)
        
        # 如果是DataParallel且输出是loss（张量），确保返回标量
        if isinstance(self.model, DataParallel) and isinstance(output, torch.Tensor) and output.dim() > 0:
            return output.mean()
        
        return output
    
    def parameters(self):
        """获取模型参数"""
        return self.model.parameters()
    
    def state_dict(self):
        """获取模型状态字典"""
        return self.get_base_model().state_dict()
    
    def load_state_dict(self, state_dict):
        """加载模型状态字典"""
        self.get_base_model().load_state_dict(state_dict)


# --- 4. 分布式数据采样器 ---
def create_data_loaders(train_dataset, val_dataset, config):
    """创建支持分布式的数据加载器"""
    if config.distributed:
        # 分布式采样器
        train_sampler = DistributedSampler(
            train_dataset,
            num_replicas=config.world_size,
            rank=config.rank,
            shuffle=True
        )
        val_sampler = DistributedSampler(
            val_dataset,
            num_replicas=config.world_size,
            rank=config.rank,
            shuffle=False
        )
        
        # 注意：使用分布式采样器时，不能在DataLoader中设置shuffle=True
        train_loader = DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            sampler=train_sampler,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            collate_fn=collate_fn
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=config.val_batch_size,
            sampler=val_sampler,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            collate_fn=collate_fn
        )
    else:
        # 非分布式训练
        train_loader = DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            collate_fn=collate_fn
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=config.val_batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            collate_fn=collate_fn
        )
    
    return train_loader, val_loader, train_sampler if config.distributed else None, val_sampler if config.distributed else None

# --- 5. Focal Loss 定义（支持多GPU） ---
class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0, reduction='mean', ignore_index=PAD_LABEL_ID):
        super(FocalLoss, self).__init__()
        if alpha is not None and not isinstance(alpha, torch.Tensor):
            alpha = torch.tensor(alpha)
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.ignore_index = ignore_index

    def forward(self, inputs, targets):
        if inputs.dim() > 2:
            inputs = inputs.reshape(-1, inputs.size(-1))
            targets = targets.reshape(-1)

        valid_mask = targets != self.ignore_index
        inputs = inputs[valid_mask]
        targets = targets[valid_mask]
        
        if inputs.numel() == 0:
            return torch.tensor(0.0, device=inputs.device, requires_grad=True)

        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma * ce_loss)

        if self.alpha is not None:
            if self.alpha.device != focal_loss.device:
                self.alpha = self.alpha.to(focal_loss.device)
            alpha_t = self.alpha[targets]
            focal_loss = alpha_t * focal_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

# --- 6. Transformer 模型定义（优化多GPU支持） ---
class FrameTaggingTransformerWithCRF(nn.Module):
    def __init__(self, model_config: Config,
                 d_model, nhead, num_encoder_layers, 
                 dim_feedforward, num_classes_out, dropout=0.1, 
                 use_op_features: bool = True):
        super(FrameTaggingTransformerWithCRF, self).__init__()
        self.d_model = d_model
        self.use_op_features = use_op_features
        self.config = model_config

        self.op_type_embedding = nn.Embedding(self.config.num_op_types, self.config.op_type_embed_dim)
        self.embed_dropout = nn.Dropout(dropout)

        current_input_dim = self.config.ssim_dim
        if self.use_op_features:
            current_input_dim += self.config.op_type_embed_dim + 1
        
        self.input_projection = nn.Linear(current_input_dim, d_model)
        self.projection_dropout = nn.Dropout(dropout)
        self.model_dropout = nn.Dropout(p=dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True, activation='gelu'
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        
        self.output_dropout = nn.Dropout(dropout)
        self.hidden2tag = nn.Linear(d_model, num_classes_out)

        self.crf = CRF(num_tags=num_classes_out, batch_first=True)

    def _generate_positional_encoding(self, seq_len, device):
        pe = torch.zeros(seq_len, self.d_model, device=device)
        position = torch.arange(0, seq_len, dtype=torch.float, device=device).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.d_model, 2).float().to(device) * (-math.log(10000.0) / self.d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe

    def _get_emissions(self, ssim_features, op_types, op_frame_flags, src_padding_mask=None):
        batch_size, seq_len, _ = ssim_features.shape

        if self.use_op_features:
            op_embeds = self.op_type_embedding(op_types)
            op_embeds = self.embed_dropout(op_embeds)
            op_embeds_expanded = op_embeds.unsqueeze(1).repeat(1, seq_len, 1)
            combined_features = torch.cat([ssim_features, op_embeds_expanded, op_frame_flags], dim=-1)
        else:
            combined_features = ssim_features

        projected_features = self.input_projection(combined_features)
        projected_features = self.projection_dropout(projected_features)
        
        projected_features = projected_features * math.sqrt(self.d_model)
        pe = self._generate_positional_encoding(seq_len, ssim_features.device)
        pos_encoded_features = projected_features + pe.unsqueeze(0)
        pos_encoded_features = self.model_dropout(pos_encoded_features)

        transformer_output = self.transformer_encoder(pos_encoded_features, src_key_padding_mask=src_padding_mask)
        transformer_output = self.output_dropout(transformer_output)
        
        emissions = self.hidden2tag(transformer_output)
        return emissions

    def forward(self, ssim_features, op_types, op_frame_flags, labels=None, src_padding_mask=None):
        emissions = self._get_emissions(ssim_features, op_types, op_frame_flags, src_padding_mask)
        
        if src_padding_mask is not None:
            crf_mask = ~src_padding_mask
        elif labels is not None:
            crf_mask = torch.ones_like(labels, dtype=torch.bool, device=labels.device)
        else:
            crf_mask = torch.ones_like(emissions[..., 0], dtype=torch.bool, device=emissions.device)

        if labels is not None:
            # 优化：更安全的CRF标签处理
            valid_label_mask = (labels != PAD_LABEL_ID)
            effective_mask = crf_mask & valid_label_mask
            
            safe_labels = labels.clone()
            safe_labels[~effective_mask] = 0
            
            byte_crf_mask = effective_mask.byte()
            
            loss = -self.crf(emissions, safe_labels, mask=byte_crf_mask, reduction='mean')
            return loss
        else:
            byte_crf_mask = crf_mask.byte() if crf_mask is not None else None
            decoded_tags = self.crf.decode(emissions, mask=byte_crf_mask)
            return decoded_tags

# --- 7. 数据集和数据加载器（保持不变） ---
class ScreenRecordingDataset(Dataset):
    def __init__(self, data_items):
        self.data_items = data_items
    
    def __len__(self):
        return len(self.data_items)
    
    def __getitem__(self, idx):
        return self.data_items[idx]

def collate_fn(batch):
    ssim_features_list = [item["ssim_features"] for item in batch]
    op_types_list = torch.stack([item["op_type"] for item in batch]) 
    op_frame_flags_list = [item["op_frame_flag"] for item in batch]
    labels_list = [item["labels"] for item in batch]
    ids = [item["id"] for item in batch]
    padded_ssim_features = pad_sequence(ssim_features_list, batch_first=True, padding_value=0.0)
    padded_op_frame_flags = pad_sequence(op_frame_flags_list, batch_first=True, padding_value=0.0) 
    padded_labels = pad_sequence(labels_list, batch_first=True, padding_value=PAD_LABEL_ID)
    lengths = torch.tensor([len(s) for s in ssim_features_list])
    max_len_in_batch = padded_ssim_features.size(1) 
    src_key_padding_mask = torch.arange(max_len_in_batch)[None, :] >= lengths[:, None] 
    return {"ids": ids, "ssim_features": padded_ssim_features, "op_types": op_types_list, 
            "op_frame_flags": padded_op_frame_flags, "labels": padded_labels, 
            "src_key_padding_mask": src_key_padding_mask}

# --- 8. 早停类定义（支持分布式） ---
class EarlyStopping:
    def __init__(self, patience=7, min_delta=0, verbose=False, path='checkpoint.pt', 
                 distributed=False, rank=0):
        self.patience = patience
        self.min_delta = min_delta
        self.verbose = verbose
        self.path = path
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_model_wts = None
        self.distributed = distributed
        self.rank = rank

    def __call__(self, val_metric, model):
        score = val_metric
        if self.verbose and (not self.distributed or self.rank == 0):
            print(f'[EarlyStopping] Received val_metric: {score:.6f}. Current best_score: {self.best_score if self.best_score is not None else "N/A"}. Counter: {self.counter}/{self.patience}.')

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_metric, model)
            if self.verbose and (not self.distributed or self.rank == 0):
                print(f'[EarlyStopping] Initialized best_score to {self.best_score:.6f}.')
        elif score < self.best_score - self.min_delta:
            if self.verbose and (not self.distributed or self.rank == 0):
                print(f'[EarlyStopping] Validation metric improved from {self.best_score:.6f} to {score:.6f}. Resetting counter.')
            self.best_score = score
            self.save_checkpoint(val_metric, model)
            self.counter = 0
        else:
            self.counter += 1
            if self.verbose and (not self.distributed or self.rank == 0):
                print(f'[EarlyStopping] Validation metric did not improve significantly. Counter: {self.counter}/{self.patience}.')
            if self.counter >= self.patience:
                self.early_stop = True
                if self.verbose and (not self.distributed or self.rank == 0):
                    print(f'[EarlyStopping] Early stopping triggered after {self.counter} epochs without improvement.')

    def save_checkpoint(self, val_metric, model):
        if self.verbose and (not self.distributed or self.rank == 0):
            print(f'[EarlyStopping] Saving model weights due to validation metric improvement ({self.best_score:.6f} --> {val_metric:.6f})...')
        # 获取基础模型的state_dict
        if hasattr(model, 'state_dict'):
            self.best_model_wts = copy.deepcopy(model.state_dict())
        elif hasattr(model, 'get_base_model'):
            self.best_model_wts = copy.deepcopy(model.get_base_model().state_dict())
        else:
            self.best_model_wts = copy.deepcopy(model.module.state_dict())

    def load_best_weights(self, model):
        if self.best_model_wts and (not self.distributed or self.rank == 0):
            if hasattr(model, 'load_state_dict'):
                model.load_state_dict(self.best_model_wts)
            elif hasattr(model, 'get_base_model'):
                model.get_base_model().load_state_dict(self.best_model_wts)
            else:
                model.module.load_state_dict(self.best_model_wts)
            if self.verbose:
                print("Loaded best model weights for final use.")

# --- 9. 分布式训练辅助函数 ---
def reduce_tensor(tensor, world_size):
    """对张量进行all-reduce操作，用于分布式训练中的指标聚合"""
    rt = tensor.clone()
    dist.all_reduce(rt, op=dist.ReduceOp.SUM)
    rt /= world_size
    return rt

def gather_tensors(tensor, world_size, rank):
    """收集所有进程的张量到rank 0"""
    gathered_tensors = [torch.zeros_like(tensor) for _ in range(world_size)]
    dist.all_gather(gathered_tensors, tensor)
    return gathered_tensors

def is_main_process(config):
    """检查是否为主进程"""
    return not config.distributed or config.rank == 0

# --- 10. 训练和评估函数（支持多GPU） ---
def _train_epoch_internal(model_wrapper, dataloader, criterion_focal, optimizer, device, 
                         epoch_num, num_epochs, config, use_crf=True, train_sampler=None):
    """支持多GPU的训练函数"""
    model_wrapper.train()
    total_loss = 0
    num_batches = len(dataloader)
    
    # 如果使用分布式训练，设置epoch以确保每个epoch的数据打乱不同
    if train_sampler is not None:
        train_sampler.set_epoch(epoch_num)
    
    for i, batch in enumerate(dataloader):
        ssim_features = batch["ssim_features"].to(device)
        op_types = batch["op_types"].to(device)
        op_frame_flags = batch["op_frame_flags"].to(device)
        labels = batch["labels"].to(device)
        src_key_padding_mask = batch["src_key_padding_mask"].to(device)

        optimizer.zero_grad()
        
        if use_crf:
            loss = model_wrapper(ssim_features, op_types, op_frame_flags, 
                               labels=labels, src_padding_mask=src_key_padding_mask)
        else:
            # 对于非CRF模型，需要获取基础模型来调用_get_emissions
            base_model = model_wrapper.get_base_model()
            emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
            loss = criterion_focal(emissions, labels)
        
        # 确保loss是标量
        if loss.dim() > 0:
            # 如果loss不是标量，取平均值
            loss = loss.mean()
        
        loss.backward()
        optimizer.step()
        
        # 在分布式训练中，需要对loss进行all-reduce
        if config.distributed:
            reduced_loss = reduce_tensor(loss.data, config.world_size)
            total_loss += reduced_loss.item()
        else:
            total_loss += loss.item()
        
        # 只在主进程打印日志
        if is_main_process(config) and ((i + 1) % (max(1, num_batches//5)) == 0 or i == num_batches - 1):
            current_loss = reduced_loss.item() if config.distributed else loss.item()
            print(f"Epoch [{epoch_num+1}/{num_epochs}], Batch [{i+1}/{num_batches}], "
                  f"Train Loss: {current_loss:.4f}")
    
    return total_loss / num_batches

def _evaluate_epoch_internal(model_wrapper, dataloader, criterion_focal, device, config, use_crf=True):
    """支持多GPU的评估函数"""
    model_wrapper.eval()
    total_loss = 0
    num_batches = len(dataloader)
    
    with torch.no_grad():
        for batch in dataloader:
            ssim_features = batch["ssim_features"].to(device)
            op_types = batch["op_types"].to(device)
            op_frame_flags = batch["op_frame_flags"].to(device)
            labels = batch["labels"].to(device)
            src_key_padding_mask = batch["src_key_padding_mask"].to(device)
            
            if use_crf:
                loss = model_wrapper(ssim_features, op_types, op_frame_flags, 
                                   labels=labels, src_padding_mask=src_key_padding_mask)
            else:
                base_model = model_wrapper.get_base_model()
                emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                loss = criterion_focal(emissions, labels)
            
            # 确保loss是标量
            if loss.dim() > 0:
                loss = loss.mean()
            
            # 在分布式训练中，需要对loss进行all-reduce
            if config.distributed:
                reduced_loss = reduce_tensor(loss.data, config.world_size)
                total_loss += reduced_loss.item()
            else:
                total_loss += loss.item()
    
    return total_loss / num_batches




# --- 11. 增强的评估函数（支持多GPU） ---
def plot_confusion_matrix(cm, class_names, save_path=None):
    """绘制混淆矩阵"""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_pr_curve(y_true, y_scores, class_names, save_path=None):
    """绘制PR曲线"""
    plt.figure(figsize=(10, 8))
    
    for i, class_name in enumerate(class_names):
        y_true_binary = (y_true == i).astype(int)
        y_scores_binary = y_scores[:, i]
        
        precision, recall, _ = precision_recall_curve(y_true_binary, y_scores_binary)
        
        plt.plot(recall, precision, label=f'{class_name}')
    
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curves')
    plt.legend()
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def evaluate_model_with_metrics(model_wrapper, test_dataloader, device, local_idx_to_label, 
                               config, use_crf=True, save_dir=None, local_pad_label_id=PAD_LABEL_ID):
    """增强的模型评估函数，支持多GPU"""
    model_wrapper.eval()
    all_true_labels = []
    all_pred_labels = []
    all_pred_probs = []
    
    # 只在主进程打印
    if is_main_process(config):
        print("\nStarting enhanced evaluation on the test set...")
    
    # 对于DataParallel + CRF的特殊处理
    is_data_parallel = isinstance(model_wrapper.model, DataParallel)
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(test_dataloader):
            ssim_features = batch["ssim_features"].to(device)
            op_types = batch["op_types"].to(device)
            op_frame_flags = batch["op_frame_flags"].to(device)
            labels_batch = batch["labels"].to(device)
            src_key_padding_mask = batch["src_key_padding_mask"].to(device)
            actual_lengths = (~src_key_padding_mask).sum(dim=1)

            base_model = model_wrapper.get_base_model()
            
            if use_crf:
                # 获取emissions用于计算概率
                if is_data_parallel:
                    # 对于DataParallel，直接使用基础模型避免gather问题
                    emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                    # 手动处理CRF解码
                    crf_mask = ~src_key_padding_mask
                    byte_crf_mask = crf_mask.byte() if crf_mask is not None else None
                    predicted_sequences_list = base_model.crf.decode(emissions, mask=byte_crf_mask)
                else:
                    # 非DataParallel模式，正常调用
                    emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                    predicted_sequences_list = model_wrapper(ssim_features, op_types, op_frame_flags, 
                                                           labels=None, src_padding_mask=src_key_padding_mask)
                
                # 将emissions转换为概率
                probs = torch.softmax(emissions, dim=-1)
                
                for i in range(len(predicted_sequences_list)):
                    seq_len_actual = actual_lengths[i].item()
                    true_labels_for_sample = labels_batch[i][:seq_len_actual].cpu().numpy()
                    pred_labels_for_sample = predicted_sequences_list[i][:seq_len_actual]
                    pred_probs_for_sample = probs[i][:seq_len_actual].cpu().numpy()
                    
                    all_true_labels.extend(true_labels_for_sample)
                    all_pred_labels.extend(pred_labels_for_sample)
                    all_pred_probs.extend(pred_probs_for_sample)
                    
            else:
                # 非CRF模式
                if is_data_parallel:
                    # 直接使用基础模型
                    emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                else:
                    emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                
                probs = torch.softmax(emissions, dim=-1)
                predictions_indices_batch = torch.argmax(emissions, dim=-1)

                for i in range(predictions_indices_batch.shape[0]):
                    seq_len_actual = actual_lengths[i].item()
                    true_labels_for_sample = labels_batch[i][:seq_len_actual].cpu().numpy()
                    pred_labels_for_sample = predictions_indices_batch[i][:seq_len_actual].cpu().numpy()
                    pred_probs_for_sample = probs[i][:seq_len_actual].cpu().numpy()
                    
                    all_true_labels.extend(true_labels_for_sample)
                    all_pred_labels.extend(pred_labels_for_sample)
                    all_pred_probs.extend(pred_probs_for_sample)
            
            if is_main_process(config) and (batch_idx + 1) % max(1, len(test_dataloader)//2) == 0:
                print(f"  Evaluated batch {batch_idx+1}/{len(test_dataloader)}")
    
    # 在分布式训练中，需要收集所有进程的结果
    if config.distributed:
        # 将列表转换为张量以便进行gather操作
        # Ensure labels are long type
        all_true_labels_tensor = torch.tensor(all_true_labels, dtype=torch.long, device=device)
        all_pred_labels_tensor = torch.tensor(all_pred_labels, dtype=torch.long, device=device)

        if all_pred_probs: # 确保列表不为空
            try:
                # all_pred_probs is a list of 1D numpy arrays, each of shape (num_classes,)
                # Convert to a single 2D numpy array: (total_frames_on_rank, num_classes)
                np_array_of_probs = np.array(all_pred_probs, dtype=np.float32)
                
                # If num_classes is 1, np.array might produce a 1D array. Reshape to 2D.
                # num_classes is a global variable.
                if np_array_of_probs.ndim == 1 and len(all_pred_probs) > 0 and num_classes == 1:
                    np_array_of_probs = np_array_of_probs[:, np.newaxis]
                elif np_array_of_probs.ndim != 2 and len(all_pred_probs) > 0:
                    # This case should ideally not be hit if upstream logic is correct.
                    # It indicates all_pred_probs was not a list of 1D arrays of consistent length.
                    print(f"Warning: np_array_of_probs has ndim {np_array_of_probs.ndim} (expected 2) and shape {np_array_of_probs.shape}. Fallback to torch.tensor direct conversion.")
                    raise ValueError("np_array_of_probs not 2D as expected")


                all_pred_probs_tensor = torch.from_numpy(np_array_of_probs).to(device)
            except Exception as e: # Catch any conversion error
                print(f"Warning: Error converting all_pred_probs (list of np arrays) to a single tensor: {e}. Falling back to torch.tensor directly on the list.")
                # This fallback might also have issues if the list structure is not what torch.tensor expects for a 2D tensor.
                all_pred_probs_tensor = torch.tensor(all_pred_probs, dtype=torch.float32, device=device)
        else: # all_pred_probs list is empty
            # Create an empty 2D tensor: (0, num_classes)
            # num_classes is a global variable.
            all_pred_probs_tensor = torch.empty((0, num_classes), dtype=torch.float32, device=device)
        
        # 收集所有进程的结果到主进程
        # DEBUG: Print shapes before gathering (on each rank, can be verbose)
        # print(f"[Rank {config.rank}] Shapes before gather: true={all_true_labels_tensor.shape}, pred={all_pred_labels_tensor.shape}, probs={all_pred_probs_tensor.shape}, true_numel={all_true_labels_tensor.numel()}, probs_numel={all_pred_probs_tensor.numel()}")

        gathered_true_labels = gather_tensors(all_true_labels_tensor, config.world_size, config.rank)
        gathered_pred_labels = gather_tensors(all_pred_labels_tensor, config.world_size, config.rank)
        gathered_pred_probs = gather_tensors(all_pred_probs_tensor, config.world_size, config.rank)
        
        if is_main_process(config):
            # 合并所有进程的结果
            all_true_labels = torch.cat(gathered_true_labels).cpu().numpy()
            all_pred_labels = torch.cat(gathered_pred_labels).cpu().numpy()
            all_pred_probs = torch.cat(gathered_pred_probs).cpu().numpy()
        else:
            # 非主进程返回None
            return None
    else:
        # 非分布式训练，直接转换为numpy数组
        all_true_labels = np.array(all_true_labels)
        all_pred_labels = np.array(all_pred_labels)
        all_pred_probs = np.array(all_pred_probs)
    
    # 以下代码保持不变...
    valid_mask = all_true_labels != local_pad_label_id
    all_true_labels = all_true_labels[valid_mask]
    all_pred_labels = all_pred_labels[valid_mask]
    all_pred_probs = all_pred_probs[valid_mask] if len(all_pred_probs) > 0 else all_pred_probs
    
    if len(all_true_labels) == 0:
        print("Error: No valid labels for evaluation.")
        return None
    
    class_names = [local_idx_to_label[i] for i in sorted(local_idx_to_label.keys()) if i != local_pad_label_id]
    
    results = {}
    
    # 计算各种指标
    results['accuracy'] = accuracy_score(all_true_labels, all_pred_labels)
    
    f1_per_class = f1_score(all_true_labels, all_pred_labels, average=None)
    results['f1_weighted'] = f1_score(all_true_labels, all_pred_labels, average='weighted')
    results['f1_macro'] = f1_score(all_true_labels, all_pred_labels, average='macro')
    
    loading_class_idx = labels_map.get("LOADING", 1)
    results['f1_loading'] = f1_per_class[loading_class_idx] if loading_class_idx < len(f1_per_class) else 0.0
    
    report = classification_report(all_true_labels, all_pred_labels, 
                                 target_names=class_names, digits=4, output_dict=True)
    results['classification_report'] = report
    
    cm = confusion_matrix(all_true_labels, all_pred_labels)
    results['confusion_matrix'] = cm
    
    # 打印结果
    print("\n" + "="*50)
    print("ENHANCED EVALUATION RESULTS")
    print("="*50)
    print(f"Overall Accuracy: {results['accuracy']:.4f}")
    print(f"F1 Score (Weighted): {results['f1_weighted']:.4f}")
    print(f"F1 Score (Macro): {results['f1_macro']:.4f}")
    print(f"F1 Score (LOADING class): {results['f1_loading']:.4f}")
    print("\nPer-Class F1 Scores:")
    for i, class_name in enumerate(class_names):
        if i < len(f1_per_class):
            print(f"  {class_name}: {f1_per_class[i]:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(all_true_labels, all_pred_labels, target_names=class_names, digits=4))
    
    # 保存可视化结果
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        
        cm_path = os.path.join(save_dir, 'confusion_matrix.png')
        plot_confusion_matrix(cm, class_names, cm_path)
        
        if len(all_pred_probs) > 0:
            pr_path = os.path.join(save_dir, 'pr_curve.png')
            plot_pr_curve(all_true_labels, all_pred_probs, class_names, pr_path)
        
        results_json = {
            'accuracy': float(results['accuracy']),
            'f1_weighted': float(results['f1_weighted']),
            'f1_macro': float(results['f1_macro']),
            'f1_loading': float(results['f1_loading']),
            'confusion_matrix': cm.tolist(),
            'classification_report': report
        }
        
        with open(os.path.join(save_dir, 'evaluation_results.json'), 'w') as f:
            json.dump(results_json, f, indent=4)
    
    return results

# --- 12. 模型保存和加载功能（支持多GPU） ---
def save_model(model_wrapper, optimizer, epoch, loss, config, save_path, additional_info=None):
    """保存模型、优化器状态、配置和其他信息（支持多GPU）"""
    # 只在主进程保存
    if not is_main_process(config):
        return
    
    # 获取基础模型的state_dict
    base_model = model_wrapper.get_base_model()
    
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': base_model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'config': config.to_dict() if hasattr(config, 'to_dict') else config.__dict__,
        'model_architecture': {
            'd_model': base_model.d_model,
            'nhead': base_model.config.nhead,
            'num_encoder_layers': base_model.config.num_encoder_layers,
            'dim_feedforward': base_model.config.dim_feedforward,
            'num_classes': num_classes,
            'use_op_features': base_model.use_op_features
        }
    }
    
    if additional_info:
        checkpoint.update(additional_info)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    torch.save(checkpoint, save_path)
    print(f"Model saved to {save_path}")
    
    config_path = save_path.replace('.pt', '_config.json')
    with open(config_path, 'w') as f:
        json.dump(checkpoint['config'], f, indent=4)

def load_model(model_path, device=None, config=None):
    """加载模型和配置（支持多GPU）"""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    checkpoint = torch.load(model_path, map_location=device)
    
    # 恢复配置
    if config is None:
        config = Config()
    
    if 'config' in checkpoint:
        for k, v in checkpoint['config'].items():
            if hasattr(config, k) and k !="distributed":
                setattr(config, k, v)
    
    # 重建模型
    model_arch = checkpoint.get('model_architecture', {})
    model = FrameTaggingTransformerWithCRF(
        model_config=config,
        d_model=model_arch.get('d_model', config.d_model),
        nhead=model_arch.get('nhead', config.nhead),
        num_encoder_layers=model_arch.get('num_encoder_layers', config.num_encoder_layers),
        dim_feedforward=model_arch.get('dim_feedforward', config.dim_feedforward),
        num_classes_out=model_arch.get('num_classes', num_classes),
        dropout=config.dropout,
        use_op_features=model_arch.get('use_op_features', config.include_operation_features)
    ).to(device)
    
    # 加载模型权重
    model.load_state_dict(checkpoint['model_state_dict'])
    # 创建模型包装器
    model_wrapper = ModelWrapper(model, config)
    
    # 创建优化器
    optimizer = optim.AdamW(model_wrapper.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    if 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    return model_wrapper, optimizer, checkpoint.get('epoch', 0), checkpoint.get('loss', float('inf')), config

# --- 13. 预测函数（支持多GPU） ---
def predict_on_single_item(model_wrapper, item_data, device, local_idx_to_label, use_crf=True):
    """对单个样本进行预测并展示结果（支持DataParallel）"""
    model_wrapper.eval()
    base_model = model_wrapper.get_base_model()
    is_data_parallel = isinstance(model_wrapper.model, DataParallel)
    
    with torch.no_grad():
        ssim_features = item_data["ssim_features"].unsqueeze(0).to(device)
        op_types = item_data["op_type"].unsqueeze(0).to(device)
        op_frame_flags = item_data["op_frame_flag"].unsqueeze(0).to(device)
        seq_len = ssim_features.size(1)
        src_key_padding_mask = torch.zeros(1, seq_len, dtype=torch.bool).to(device)

        if use_crf:
            if is_data_parallel:
                # 对于DataParallel + CRF，直接使用基础模型
                emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                crf_mask = ~src_key_padding_mask
                byte_crf_mask = crf_mask.byte()
                predicted_sequence_list = base_model.crf.decode(emissions, mask=byte_crf_mask)
            else:
                predicted_sequence_list = model_wrapper(ssim_features, op_types, op_frame_flags, 
                                                      labels=None, src_padding_mask=src_key_padding_mask)
            predictions_indices = torch.tensor(predicted_sequence_list[0], device=device)
        else:
            emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
            predictions_indices = torch.argmax(emissions, dim=-1).squeeze(0)

    # 打印预测结果的代码保持不变...
    print(f"\n--- Prediction for Sample ID: {item_data['id']} (OpType: {item_data['op_type'].item()}) ---")
    print(f"Sequence Length: {seq_len}")
    op_features_used_str = "Yes" if base_model.use_op_features else "No"
    print(f"Model used OpFeatures: {op_features_used_str}")
    print("Frame | Op? | True Label       | Predicted Label  | Match")
    print("-" * 65)
    
    true_labels_present = "labels" in item_data and item_data["labels"] is not None
    correct_predictions = 0
    
    for i in range(seq_len):
        true_label_str = "N/A"
        match_str = "N/A"
        
        if true_labels_present:
            true_label_val = item_data["labels"][i].item()
            true_label_str = local_idx_to_label.get(true_label_val, f"INVALID({true_label_val})")
        
        pred_idx = i if i < len(predictions_indices) else -1
        if pred_idx != -1:
            pred_label_val = predictions_indices[pred_idx].item()
            pred_label_str = local_idx_to_label.get(pred_label_val, f"ERR({pred_label_val})")
        else:
            pred_label_str = "ERR (Index out of bounds)"

        if true_labels_present and pred_idx != -1:
            if item_data["labels"][i].item() == predictions_indices[pred_idx].item():
                match_str = "✓"
                correct_predictions += 1
            else:
                match_str = "✗"

        op_flag_str = "Yes" if item_data["op_frame_flag"][i].item() == 1.0 else "No "
        print(f"{i:05d} | {op_flag_str} | {true_label_str:<16} | {pred_label_str:<16} | {match_str}")
    
    if true_labels_present:
        accuracy = correct_predictions / seq_len
        print("-" * 65)
        print(f"Sample Accuracy: {accuracy:.4f} ({correct_predictions}/{seq_len})")
    print("-" * 65)


def batch_inference(model_wrapper, dataloader, device, config, use_crf=True):
    """对整个数据集进行批量推理（支持多GPU）"""
    model_wrapper.eval()
    all_predictions = []
    all_ids = []
    
    with torch.no_grad():
        for batch in dataloader:
            ssim_features = batch["ssim_features"].to(device)
            op_types = batch["op_types"].to(device)
            op_frame_flags = batch["op_frame_flags"].to(device)
            src_key_padding_mask = batch["src_key_padding_mask"].to(device)
            ids = batch["ids"]
            
            if use_crf:
                predictions = model_wrapper(ssim_features, op_types, op_frame_flags, 
                                          labels=None, src_padding_mask=src_key_padding_mask)
            else:
                base_model = model_wrapper.get_base_model()
                emissions = base_model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                predictions = torch.argmax(emissions, dim=-1).cpu().tolist()
            
            all_predictions.extend(predictions)
            all_ids.extend(ids)
    
    return all_ids, all_predictions

# --- 14. 超参数优化（支持多GPU） ---
def create_model_with_config(config, device):
    """根据配置创建模型"""
    model = FrameTaggingTransformerWithCRF(
        model_config=config,
        d_model=config.d_model,
        nhead=config.nhead,
        num_encoder_layers=config.num_encoder_layers,
        dim_feedforward=config.dim_feedforward,
        num_classes_out=num_classes,
        dropout=config.dropout,
        use_op_features=config.include_operation_features
    ).to(device)
    return model

def optuna_objective(trial, train_data, val_data, base_config, use_crf=True, num_epochs=20):
    """Optuna超参数优化的目标函数（带完整的内存管理和错误处理）"""
    # 记录试验开始
    print(f"\n[Trial {trial.number}] Starting...")
    
    # 用于存储需要清理的对象
    objects_to_clean = []
    
    try:
        # 创建试验配置
        config = copy.deepcopy(base_config)
        
        # 超参数搜索空间
        config.d_model = trial.suggest_int('d_model', 4, 64, step=4)  # 减小上限
        config.nhead = trial.suggest_categorical('nhead', [2,4])  # 减少选项
        config.num_encoder_layers = trial.suggest_int('num_encoder_layers', 1, 4)  # 减小上限
        config.dim_feedforward = trial.suggest_int('dim_feedforward', 8, 128, step=8)  # 减小上限
        config.dropout = trial.suggest_float('dropout', 0.1, 0.9)
        config.learning_rate = trial.suggest_float('lr', 1e-5, 1e-2, log=True)  # 使用新API
        config.batch_size = trial.suggest_categorical('batch_size', [64, 128 ,256])  # 更小的批次大小
        
        # 确保d_model能被nhead整除
        if config.d_model % config.nhead != 0:
            config.d_model = (config.d_model // config.nhead) * config.nhead
        
        # 在超参数优化时，使用单GPU和更保守的设置
        config.num_workers = 0  # 避免多进程内存问题
        
        print(f"[Trial {trial.number}] Config: d_model={config.d_model}, nhead={config.nhead}, "
              f"layers={config.num_encoder_layers}, batch_size={config.batch_size},dim_feedforward={config.dim_feedforward}")
        
        # 创建数据加载器
        train_dataset = ScreenRecordingDataset(train_data)
        val_dataset = ScreenRecordingDataset(val_data)
        objects_to_clean.append(train_dataset)
        objects_to_clean.append(val_dataset)
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=config.batch_size, 
            shuffle=True, 
            collate_fn=collate_fn,
            num_workers=0,
            pin_memory=False
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=min(config.batch_size, 32),  # 验证时使用更小的批次
            shuffle=False, 
            collate_fn=collate_fn,
            num_workers=0,
            pin_memory=False
        )
        objects_to_clean.append(train_loader)
        objects_to_clean.append(val_loader)
        
        # 创建模型
        model = create_model_with_config(config, config.device)
        model_wrapper = ModelWrapper(model, config)
        objects_to_clean.append(model)
        objects_to_clean.append(model_wrapper)
        
        # 计算模型参数量
        total_params = sum(p.numel() for p in model.parameters())
        print(f"[Trial {trial.number}] Model parameters: {total_params:,}")
        
        # 损失函数和优化器
        criterion_focal = None
        if not use_crf:
            criterion_focal = FocalLoss(gamma=config.focal_loss_gamma, ignore_index=PAD_LABEL_ID)
            objects_to_clean.append(criterion_focal)
        
        optimizer = optim.AdamW(
            model_wrapper.parameters(), 
            lr=config.learning_rate, 
            weight_decay=config.weight_decay
        )
        objects_to_clean.append(optimizer)
        
        # 训练循环（简化版）
        best_val_loss = float('inf')
        
        for epoch in range(num_epochs):
            # 在每个epoch开始前检查GPU内存
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / 1024**3  # GB
                if gpu_memory > 60:  # 如果使用超过60GB，提前停止
                    print(f"[Trial {trial.number}] GPU memory usage too high: {gpu_memory:.2f}GB")
                    return float('inf')
            
            try:
                # 训练一个epoch
                train_loss = _train_epoch_internal(
                    model_wrapper, train_loader, criterion_focal, optimizer, 
                    config.device, epoch, num_epochs, config, use_crf=use_crf
                )
                
                # 评估
                val_loss = _evaluate_epoch_internal(
                    model_wrapper, val_loader, criterion_focal, 
                    config.device, config, use_crf=use_crf
                )
                
                print(f"[Trial {trial.number}] Epoch {epoch+1}/{num_epochs}: "
                      f"train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
                
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                
                # 报告中间结果
                trial.report(val_loss, epoch)
                
                # 如果被剪枝，则提前停止
                if trial.should_prune():
                    print(f"[Trial {trial.number}] Pruned at epoch {epoch+1}")
                    raise optuna.exceptions.TrialPruned()
                    
            except torch.cuda.OutOfMemoryError as e:
                print(f"[Trial {trial.number}] OOM at epoch {epoch+1}: {str(e)}")
                return float('inf')
        
        print(f"[Trial {trial.number}] Completed. Best val_loss: {best_val_loss:.4f}")
        return best_val_loss
        
    except torch.cuda.OutOfMemoryError as e:
        # 处理GPU内存不足错误
        print(f"[Trial {trial.number}] Failed due to OOM: {str(e)}")
        return float('inf')
        
    except optuna.exceptions.TrialPruned:
        # 重新抛出剪枝异常
        raise
        
    except Exception as e:
        # 处理其他错误
        print(f"[Trial {trial.number}] Failed with unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return float('inf')
        
    finally:
        # 清理所有对象
        print(f"[Trial {trial.number}] Cleaning up...")
        
        # 删除所有tracked对象
        for obj in objects_to_clean:
            try:
                if hasattr(obj, 'to'):
                    obj.cpu()  # 将张量移到CPU
                del obj
            except:
                pass
        
        # 删除局部变量
        for var_name in ['model', 'model_wrapper', 'optimizer', 'train_loader', 
                        'val_loader', 'train_dataset', 'val_dataset', 'criterion_focal']:
            if var_name in locals():
                try:
                    del locals()[var_name]
                except:
                    pass
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        # 清空GPU缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # 打印当前GPU内存使用情况
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            print(f"[Trial {trial.number}] GPU memory after cleanup: "
                  f"allocated={allocated:.2f}GB, reserved={reserved:.2f}GB")


def run_hyperparameter_optimization(train_data, val_data, base_config, n_trials=50, use_crf=True):
    """运行超参数优化（在主进程的单GPU上运行）"""
    study = optuna.create_study(
        direction='minimize',
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=10)
    )
    
    study.optimize(
        lambda trial: optuna_objective(trial, train_data, val_data, base_config, use_crf),
        n_trials=n_trials
    )
    
    print("Best trial:")
    print(f"Value: {study.best_value}")
    print("Params:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")
    
    # 创建最佳配置
    best_config = copy.deepcopy(base_config)
    for key, value in study.best_params.items():
        if key == 'lr':
            setattr(best_config, 'learning_rate', value)
        elif hasattr(best_config, key):
            setattr(best_config, key, value)
    
    # 确保d_model能被nhead整除
    if best_config.d_model % best_config.nhead != 0:
        best_config.d_model = (best_config.d_model // best_config.nhead) * best_config.nhead
    
    return best_config, study

# --- 15. 完整训练流程（支持多GPU） ---
def run_training_pipeline(all_raw_data: list, training_config: Config, use_crf_layer: bool, 
                         save_best_model: bool = True, rank=None):
    """完整的训练流程函数（支持多GPU）"""
    # 如果是分布式训练，设置rank
    if rank is not None:
        training_config.rank = rank
        training_config.local_rank = rank
        setup_distributed(rank, training_config.world_size, training_config.backend)
        training_config.device = torch.device(f"cuda:{rank}")
    
    if is_main_process(training_config):
        print(f"--- Starting Training Pipeline ---")
        print(f"Device: {training_config.device}")
        print(f"Using CRF layer: {use_crf_layer}")
        print(f"Including operation features: {training_config.include_operation_features}")
        if training_config.distributed:
            print(f"Distributed training with {training_config.world_size} processes")
        elif training_config.use_multi_gpu and training_config.gpu_count > 1:
            print(f"DataParallel training with {training_config.gpu_count} GPUs")

    # 数据准备与划分
    random.shuffle(all_raw_data)
    split_idx = int(len(all_raw_data) * (1 - training_config.validation_split))
    train_raw_data = all_raw_data[:split_idx]
    val_raw_data = all_raw_data[split_idx:]

    if is_main_process(training_config):
        print(f"Total samples: {len(all_raw_data)}, Training: {len(train_raw_data)}, Validation: {len(val_raw_data)}")

    train_dataset = ScreenRecordingDataset(train_raw_data)
    val_dataset = ScreenRecordingDataset(val_raw_data)
    
    # 创建数据加载器（支持分布式）
    train_loader, val_loader, train_sampler, val_sampler = create_data_loaders(
        train_dataset, val_dataset, training_config
    )

    # Alpha 权重计算
    current_alpha_weights = None
    if not use_crf_layer and len(train_raw_data) > 0 and is_main_process(training_config):
        all_train_labels_flat = torch.cat([d["labels"] for d in train_raw_data if d["labels"] is not None])
        all_train_labels_flat_no_pad = all_train_labels_flat[all_train_labels_flat != PAD_LABEL_ID]
        
        if len(all_train_labels_flat_no_pad) > 0:
            class_counts = torch.bincount(all_train_labels_flat_no_pad, minlength=num_classes)
            alpha_w = 1.0 / (class_counts.float() + 1e-6) 
            alpha_w = alpha_w / alpha_w.sum()
            current_alpha_weights = alpha_w.to(training_config.device)
            print(f"Calculated Alpha Weights for Focal Loss: {current_alpha_weights}")
    if training_config.CLASS_WEIGHTS_ALPHA:
        print(f"use CLASS_WEIGHTS_ALPHA:{training_config.CLASS_WEIGHTS_ALPHA}")
        current_alpha_weights = training_config.CLASS_WEIGHTS_ALPHA
    
    # 模型、损失、优化器、调度器、早停 初始化
    model = create_model_with_config(training_config, training_config.device)
    model_wrapper = ModelWrapper(model, training_config)

    criterion_focal = None
    if not use_crf_layer:
        criterion_focal = FocalLoss(alpha=current_alpha_weights, 
                                    gamma=training_config.focal_loss_gamma, 
                                    ignore_index=PAD_LABEL_ID)

    optimizer = optim.AdamW(model_wrapper.parameters(), 
                           lr=training_config.learning_rate, 
                           weight_decay=training_config.weight_decay)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 'min', 
        patience=max(2, training_config.early_stopping_patience // 10),
        factor=0.5, verbose=is_main_process(training_config), min_lr=1e-7
    )
    
    early_stopper = EarlyStopping(
        patience=training_config.early_stopping_patience, 
        min_delta=training_config.early_stopping_min_delta, 
        verbose=is_main_process(training_config),
        distributed=training_config.distributed,
        rank=training_config.rank if training_config.distributed else 0
    )

    # 创建保存目录
    if save_best_model and is_main_process(training_config):
        save_dir = os.path.join(training_config.save_dir, training_config.experiment_name)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存初始配置
        with open(os.path.join(save_dir, 'config.json'), 'w') as f:
            json.dump(training_config.to_dict(), f, indent=4)

    # 训练循环
    history = {'train_loss': [], 'val_loss': []}
    best_val_loss = float('inf')
    
    if is_main_process(training_config):
        print("\nStarting training loop...")
    
    for epoch in range(training_config.num_epochs):
        avg_train_loss = _train_epoch_internal(
            model_wrapper, train_loader, criterion_focal, optimizer, 
            training_config.device, epoch, training_config.num_epochs, 
            training_config, use_crf=use_crf_layer, train_sampler=train_sampler
        )
        
        avg_val_loss = _evaluate_epoch_internal(
            model_wrapper, val_loader, criterion_focal, 
            training_config.device, training_config, use_crf=use_crf_layer
        )
        
        if is_main_process(training_config):
            print(f"Epoch [{epoch+1}/{training_config.num_epochs}] summary. "
                  f"Avg Train Loss: {avg_train_loss:.4f}, Avg Val Loss: {avg_val_loss:.4f}, "
                  f"LR: {optimizer.param_groups[0]['lr']:.2e}")

        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        
        # 保存最佳模型
        if save_best_model and avg_val_loss < best_val_loss and is_main_process(training_config):
            best_val_loss = avg_val_loss
            model_path = os.path.join(save_dir, 'best_model.pt')
            save_model(model_wrapper, optimizer, epoch, avg_val_loss, training_config, model_path,
                      additional_info={'history': history, 'use_crf': use_crf_layer})
        
        scheduler.step(avg_val_loss)
        early_stopper(avg_val_loss, model_wrapper)
        
        if early_stopper.early_stop:
            if is_main_process(training_config):
                print(f"Early stopping triggered at epoch {epoch+1}.")
            break
    
    if is_main_process(training_config):
        print("Training finished.")
    
    early_stopper.load_best_weights(model_wrapper)
    
    # 保存最终模型
    if save_best_model and is_main_process(training_config):
        final_model_path = os.path.join(save_dir, 'final_model.pt')
        save_model(model_wrapper, optimizer, epoch, avg_val_loss, training_config, final_model_path,
                  additional_info={'history': history, 'use_crf': use_crf_layer})
        
        # 保存训练历史
        history_path = os.path.join(save_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=4)

    # 清理分布式训练
    if training_config.distributed:
        # cleanup_distributed() # Removed this line
        pass # Pass if no other logic remains in this block, or simply remove the if block if empty

    return model_wrapper, history

# --- 16. 分布式训练主函数 ---
def distributed_main(rank, world_size, train_data, config, use_crf):
    """分布式训练的主函数（每个进程执行）"""
    config.rank = rank
    config.world_size = world_size
    config.distributed = True
    
    # 运行训练流程
    model_wrapper, history = run_training_pipeline(
        all_raw_data=train_data,
        training_config=config,
        use_crf_layer=use_crf,
        save_best_model=True,
        rank=rank
    )
    
    return model_wrapper, history

# 在主函数开始处添加以下代码，替换原有的 if __name__ == "__main__": 部分

def main():
    """主函数，支持torchrun启动"""
    # 1. 初始化配置
    master_config = Config()
    
    # 检查是否通过torchrun启动
    if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
        # torchrun模式
        master_config.distributed = True
        master_config.rank = int(os.environ["RANK"])
        master_config.world_size = int(os.environ["WORLD_SIZE"])
        master_config.local_rank = int(os.environ["LOCAL_RANK"])
        
        # 初始化分布式环境
        torch.cuda.set_device(master_config.local_rank)
        master_config.device = torch.device(f"cuda:{master_config.local_rank}")
        
        dist.init_process_group(
            backend=master_config.backend,
            init_method=master_config.init_method,
            world_size=master_config.world_size,
            rank=master_config.rank
        )
        
        print(f"Initialized process {master_config.rank}/{master_config.world_size} on GPU {master_config.local_rank}")
    else:
        # 非分布式模式
        master_config.distributed = False
        master_config.use_multi_gpu = True  # 可以使用DataParallel
    
    # 2. 加载数据
    train_set_paths = ["part_1_train_data_fps30_offsets6_ssim_20250601.pt","part_2_train_data_fps30_offsets6_ssim_20250601.pt"]
    test_set_paths = ["part_1_test_data_fps30_offsets6_ssim_20250601.pt","part_2_test_data_fps30_offsets6_ssim_20250601.pt"]
    
    combined_train_set = []
    for t_path in train_set_paths:
        try:
            if is_main_process(master_config):
                print(f"Loading training data from: {t_path}")
            loaded_data = torch.load(t_path)
            if isinstance(loaded_data, list):
                combined_train_set.extend(loaded_data)
        except Exception as e:
            if is_main_process(master_config):
                print(f"Warning: Error loading {t_path}: {e}")

    test_set = []
    for t_path in test_set_paths:
        try:
            if is_main_process(master_config):
                print(f"Loading test data from: {t_path}")
            loaded_data = torch.load(t_path)
            if isinstance(loaded_data, list):
                test_set.extend(loaded_data)
        except Exception as e:
            if is_main_process(master_config):
                print(f"Warning: Error loading {t_path}: {e}")

    if not combined_train_set:
        print("Error: No valid training data loaded.")
        exit(1)
    
    if is_main_process(master_config):
        print(f"Loaded {len(combined_train_set)} training samples and {len(test_set)} test samples.")
    
    # 3. 设置训练参数
    RUN_HYPERPARAMETER_OPTIMIZATION = True
    SHOULD_USE_CRF = False
    
    # 4. 超参数优化（只在主进程运行）
    if RUN_HYPERPARAMETER_OPTIMIZATION and is_main_process(master_config) and not master_config.distributed:
        print("\n--- Running Hyperparameter Optimization ---")
        split_idx = int(len(combined_train_set) * 0.8)
        optuna_train_data = combined_train_set[:split_idx]
        optuna_val_data = combined_train_set[split_idx:]
        
        best_config, study = run_hyperparameter_optimization(
            optuna_train_data, 
            optuna_val_data, 
            master_config, 
            n_trials=200,
            use_crf=SHOULD_USE_CRF
        )
        
        # 保存优化结果
        optuna_results_dir = os.path.join(master_config.save_dir, "optuna_results")
        os.makedirs(optuna_results_dir, exist_ok=True)
        
        # 保存最佳配置
        with open(os.path.join(optuna_results_dir, 'best_config.json'), 'w') as f:
            json.dump(best_config.to_dict(), f, indent=4)
        
        # 保存优化历史
        study_df = study.trials_dataframe()
        study_df.to_csv(os.path.join(optuna_results_dir, 'optimization_history.csv'), index=False)
        
        # 可视化优化过程
        try:
            import optuna.visualization as vis
            
            # 优化历史图
            fig = vis.plot_optimization_history(study)
            fig.write_html(os.path.join(optuna_results_dir, 'optimization_history.html'))
            
            # 参数重要性图
            fig = vis.plot_param_importances(study)
            fig.write_html(os.path.join(optuna_results_dir, 'param_importances.html'))
            
            # 参数关系图
            fig = vis.plot_parallel_coordinate(study)
            fig.write_html(os.path.join(optuna_results_dir, 'parallel_coordinate.html'))
            
            # 超参数的分布图
            fig = vis.plot_slice(study)
            fig.write_html(os.path.join(optuna_results_dir, 'param_slice.html'))
            
            # 参数之间的关系图
            fig = vis.plot_contour(study)
            fig.write_html(os.path.join(optuna_results_dir, 'param_contour.html'))
            
        except ImportError:
            print("Optuna visualization requires plotly. Install with: pip install plotly kaleido")
        except Exception as e:
            print(f"Warning: Failed to generate some visualizations: {e}")
        
        print(f"\nOptimization complete. Best validation loss: {study.best_value:.4f}")
        print("Best parameters:")
        for key, value in study.best_params.items():
            print(f"  {key}: {value}")
        
        print("Using optimized configuration for training...")
        training_config = best_config
    else:
        training_config = master_config

    
    # 5. 运行训练
    if is_main_process(training_config):
        print("\n--- Starting Model Training ---")
        if training_config.distributed:
            print(f"Distributed training with {training_config.world_size} processes")
    
    trained_model_wrapper, training_run_history = run_training_pipeline(
        all_raw_data=combined_train_set,
        training_config=training_config,
        use_crf_layer=SHOULD_USE_CRF,
        save_best_model=True
    )
    
    # 6. 评估和测试（只在主进程执行）
    if trained_model_wrapper and test_set and is_main_process(training_config):
        print("\n--- Evaluating on Test Set ---")
        
        test_dataset = ScreenRecordingDataset(test_set)
        test_dataloader = DataLoader(
            test_dataset, 
            batch_size=training_config.batch_size, 
            shuffle=False, 
            collate_fn=collate_fn,
            num_workers=training_config.num_workers,
            pin_memory=training_config.pin_memory
        )
        
        eval_save_dir = os.path.join(training_config.save_dir, training_config.experiment_name, 'evaluation')
        
        evaluation_results = evaluate_model_with_metrics(
            trained_model_wrapper,
            test_dataloader,
            training_config.device,
            idx_to_label,
            training_config,
            use_crf=SHOULD_USE_CRF,
            save_dir=eval_save_dir,
            local_pad_label_id=PAD_LABEL_ID
        )
        
        # 使用evaluation_results生成最终报告
        if evaluation_results:
            # 生成实验总结报告
            experiment_report = {
                "experiment_name": training_config.experiment_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "configuration": training_config.to_dict(),
                "training_summary": {
                    "total_samples": len(combined_train_set),
                    "train_samples": int(len(combined_train_set) * (1 - training_config.validation_split)),
                    "val_samples": int(len(combined_train_set) * training_config.validation_split),
                    "test_samples": len(test_set),
                    "use_crf": SHOULD_USE_CRF,
                    "epochs_trained": len(training_run_history.get('train_loss', [])) if 'training_run_history' in locals() else 0,
                    "final_train_loss": training_run_history['train_loss'][-1] if 'training_run_history' in locals() and training_run_history.get('train_loss') else None,
                    "final_val_loss": training_run_history['val_loss'][-1] if 'training_run_history' in locals() and training_run_history.get('val_loss') else None,
                },
                "test_performance": {
                    "accuracy": evaluation_results['accuracy'],
                    "f1_weighted": evaluation_results['f1_weighted'],
                    "f1_macro": evaluation_results['f1_macro'],
                    "f1_loading": evaluation_results['f1_loading'],
                    "confusion_matrix": evaluation_results['confusion_matrix'].tolist(),
                }
            }
            
            # 保存完整的实验报告
            report_path = os.path.join(training_config.save_dir, training_config.experiment_name, 'final_experiment_report.json')
            with open(report_path, 'w') as f:
                json.dump(experiment_report, f, indent=4)
            
            # 打印最终总结
            print("\n" + "="*60)
            print("FINAL EXPERIMENT SUMMARY")
            print("="*60)
            print(f"Experiment: {training_config.experiment_name}")
            print(f"\nTest Set Performance:")
            print(f"  - Accuracy: {evaluation_results['accuracy']:.4f}")
            print(f"  - F1 Score (Weighted): {evaluation_results['f1_weighted']:.4f}")
            print(f"  - F1 Score (Macro): {evaluation_results['f1_macro']:.4f}")
            print(f"  - F1 Score (LOADING class): {evaluation_results['f1_loading']:.4f}")
            
            # 打印混淆矩阵
            print(f"\nConfusion Matrix:")
            cm = evaluation_results['confusion_matrix']
            print(f"              Predicted")
            print(f"              O    LOADING")
            print(f"Actual O      {cm[0][0]:<6} {cm[0][1]:<6}")
            print(f"       LOADING {cm[1][0]:<6} {cm[1][1]:<6}")
            
            print(f"\nFull report saved to: {report_path}")
            print("="*60)
        
        # 展示一些样本预测
        print("\n--- Sample Predictions ---")
        num_samples_to_show = min(3, len(test_set))
        sample_indices = random.sample(range(len(test_set)), num_samples_to_show)
        
        for idx in sample_indices:
            predict_on_single_item(
                trained_model_wrapper,
                test_set[idx],
                training_config.device,
                idx_to_label,
                use_crf=SHOULD_USE_CRF
            )
    
    # 7. 生成训练历史图表（如果有matplotlib）
    if is_main_process(training_config) and 'training_run_history' in locals() and training_run_history:
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(10, 6))
            plt.plot(training_run_history['train_loss'], label='Train Loss', alpha=0.8)
            plt.plot(training_run_history['val_loss'], label='Validation Loss', alpha=0.8)
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.title(f'Training History - {training_config.experiment_name}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plot_path = os.path.join(training_config.save_dir, training_config.experiment_name, 'final_training_history.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"\nTraining history plot saved to: {plot_path}")
        except ImportError:
            print("\nMatplotlib not available, skipping training history plot")
    
    # 8. 清理
    if training_config.distributed:
        dist.destroy_process_group()
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        if is_main_process(training_config):
            print("\nGPU memory cleared.")
    
    if is_main_process(training_config):
        print("\n" + "="*60)
        print("TRAINING PIPELINE COMPLETE!")
        print("="*60)
        
        # 打印一些有用的后续步骤
        print("\nNext steps:")
        print(f"1. Review the full report at: {training_config.save_dir}/{training_config.experiment_name}/")
        print("2. Check the evaluation visualizations in the 'evaluation' subdirectory")
        print("3. Use the saved model for inference:")
        print(f"   model_path = '{training_config.save_dir}/{training_config.experiment_name}/best_model.pt'")
        print("4. Compare with other experiments using the JSON reports")

if __name__ == "__main__":
    main()
