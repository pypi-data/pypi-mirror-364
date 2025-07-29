import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from torchcrf import CRF
import math
import random
import numpy as np
import copy # 用于深拷贝最佳模型
from sklearn.metrics import classification_report, accuracy_score # 导入评估工具
# import os # 如果 EarlyStopping 保存到文件并需要检查路径

# --- 0. 全局常量定义 ---
PAD_LABEL_ID = -100
labels_map = {
    "O": 0,
    "LOADING": 1
}
num_classes = len(labels_map) # 在这里计算，供全局使用
idx_to_label = {v: k for k, v in labels_map.items()}


# --- 1. 配置参数 ---
class Config:
    # 数据相关
    num_sequences = 500
    max_seq_len = 150
    min_seq_len = 50
    ssim_dim = 6
    num_op_types = 1 # 需要与 op_type_embedding 匹配
    op_type_embed_dim = 8
    include_operation_features = False
    validation_split = 0.2

    # 模型相关
    d_model = 32
    nhead = 4
    num_encoder_layers = 2
    dim_feedforward = 64
    dropout = 0.4

    # 训练相关
    batch_size = 512
    val_batch_size = 64
    learning_rate = 1e-4
    num_epochs = 100000
    CLASS_WEIGHTS_ALPHA = None # 会在训练流程中基于数据计算
    focal_loss_gamma = 2.0
    weight_decay = 1e-4

    # 早停相关
    early_stopping_patience = 3000
    early_stopping_min_delta = 0.0001
    early_stopping_metric = 'val_loss'

    # 其他
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 2. Focal Loss 定义 ---
class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0, reduction='mean', ignore_index=PAD_LABEL_ID): # 使用全局 PAD_LABEL_ID
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
            alpha_t = self.alpha[targets] # Assuming targets are 0-indexed class labels
            focal_loss = alpha_t * focal_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

# --- 3. Transformer 模型定义 (集成CRF) ---
class FrameTaggingTransformerWithCRF(nn.Module):
    def __init__(self, model_config: Config, # 传入Config对象获取模型参数
                 d_model, nhead, num_encoder_layers, 
                 dim_feedforward, num_classes_out, dropout=0.1, 
                 use_op_features: bool = True):
        super(FrameTaggingTransformerWithCRF, self).__init__()
        self.d_model = d_model
        self.use_op_features = use_op_features
        self.config = model_config # 保存config引用

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
        self.hidden2tag = nn.Linear(d_model, num_classes_out) # num_classes_out 应为全局的 num_classes

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
        
        # src_padding_mask is True for padded elements.
        # crf_mask needs True for non-padded (valid) elements.
        if src_padding_mask is not None:
            crf_mask = ~src_padding_mask
        elif labels is not None: # No src_padding_mask, but labels exist (all valid)
            crf_mask = torch.ones_like(labels, dtype=torch.bool, device=labels.device)
        else: # No src_padding_mask and no labels (inference on potentially full batch)
            crf_mask = torch.ones_like(emissions[..., 0], dtype=torch.bool, device=emissions.device)


        if labels is not None: # Training or evaluation with labels
            # --- BEGIN MODIFICATION ---
            # Create a copy of labels to modify PAD_LABEL_ID for CRF input
            labels_for_crf = labels.clone()
            
            # Replace PAD_LABEL_ID with a valid label index (e.g., 0).
            # The crf_mask will ensure these positions do not contribute to the loss.
            # This step is to prevent indexing errors within the CRF layer if it
            # attempts to use PAD_LABEL_ID values internally before applying the mask effects.
            labels_for_crf[labels == PAD_LABEL_ID] = 0 # Assuming 0 is a valid class index ("O")
            # --- END MODIFICATION ---

            # Ensure crf_mask is in byte format for torchcrf
            # (Newer torchcrf versions might also accept bool, but byte is safer)
            byte_crf_mask = crf_mask.byte() if crf_mask is not None else None

            loss = -self.crf(emissions, labels_for_crf, mask=byte_crf_mask, reduction='mean')
            return loss
        else: # Inference
            byte_crf_mask = crf_mask.byte() if crf_mask is not None else None
            decoded_tags = self.crf.decode(emissions, mask=byte_crf_mask)
            return decoded_tags



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
    padded_labels = pad_sequence(labels_list, batch_first=True, padding_value=PAD_LABEL_ID) # 使用全局 PAD_LABEL_ID
    lengths = torch.tensor([len(s) for s in ssim_features_list])
    max_len_in_batch = padded_ssim_features.size(1) 
    src_key_padding_mask = torch.arange(max_len_in_batch)[None, :] >= lengths[:, None] 
    return {"ids": ids, "ssim_features": padded_ssim_features, "op_types": op_types_list, 
            "op_frame_flags": padded_op_frame_flags, "labels": padded_labels, 
            "src_key_padding_mask": src_key_padding_mask}

# --- 5. 早停类定义 ---
class EarlyStopping:
    """
    训练早停工具类：用于在验证集指标（如val_loss）多轮未提升时自动停止训练，防止过拟合。
    支持保存最佳模型权重，训练结束后可恢复。
    """
    def __init__(self, patience=7, min_delta=0, verbose=False, path='checkpoint.pt'):
        """
        :param patience: 容忍多少个epoch验证集指标未提升（超过则早停）
        :param min_delta: 指标提升的最小幅度（小于等于此幅度视为未提升）
        :param verbose: 是否打印详细日志
        :param path: 预留参数，当前未用（如需保存到文件可用）
        """
        self.patience = patience
        self.min_delta = min_delta
        self.verbose = verbose
        self.path = path # 文件路径当前未使用，因为直接保存权重到 best_model_wts
        self.counter = 0 # 连续未提升的epoch计数
        self.best_score = None # 当前最佳指标
        self.early_stop = False # 是否触发早停
        self.best_model_wts = None # 最佳模型权重（内存保存）

    def __call__(self, val_metric, model):
        """
        每个epoch结束后调用，判断是否需要早停，并保存最佳模型权重。
        :param val_metric: 当前epoch的验证集指标（如val_loss，越低越好）
        :param model: 当前模型实例
        """
        score = val_metric
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_metric, model)
        elif score < self.best_score - self.min_delta:
            # 指标有明显提升，更新最佳分数并保存权重
            self.best_score = score
            self.save_checkpoint(val_metric, model)
            self.counter = 0
        else:
            # 指标无提升，计数加1
            self.counter += 1
            if self.verbose:
                print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True

    def save_checkpoint(self, val_metric, model):
        """
        保存当前模型的权重到内存（如需保存到文件可扩展path参数）。
        :param val_metric: 当前验证集指标
        :param model: 当前模型实例
        """
        if self.verbose:
            print(f'Validation metric improved ({self.best_score:.6f} --> {val_metric:.6f}). Saving model weights...')
        self.best_model_wts = copy.deepcopy(model.state_dict())

    def load_best_weights(self, model):
        """
        训练结束后调用，将模型恢复到最佳权重。
        :param model: 当前模型实例
        """
        if self.best_model_wts:
            model.load_state_dict(self.best_model_wts)
            if self.verbose:
                print("Loaded best model weights for final use.")

# --- 6. 训练与评估函数 (内部辅助函数) ---
def _train_epoch_internal(model, dataloader, criterion_focal, optimizer, device, epoch_num, num_epochs, use_crf=True):
    model.train()
    total_loss = 0
    for i, batch in enumerate(dataloader):
        ssim_features = batch["ssim_features"].to(device)
        op_types = batch["op_types"].to(device)
        op_frame_flags = batch["op_frame_flags"].to(device)
        labels = batch["labels"].to(device)
        src_key_padding_mask = batch["src_key_padding_mask"].to(device)

        optimizer.zero_grad()
        if use_crf:
            loss = model(ssim_features, op_types, op_frame_flags, labels=labels, src_padding_mask=src_key_padding_mask)
        else:
            emissions = model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
            loss = criterion_focal(emissions, labels) # labels already have PAD_LABEL_ID
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        if (i + 1) % (max(1, len(dataloader)//5)) == 0 or i == len(dataloader) -1 :
             print(f"Epoch [{epoch_num+1}/{num_epochs}], Batch [{i+1}/{len(dataloader)}], Train Loss: {loss.item():.4f}")
    return total_loss / len(dataloader)

def _evaluate_epoch_internal(model, dataloader, criterion_focal, device, use_crf=True):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for batch in dataloader:
            ssim_features = batch["ssim_features"].to(device)
            op_types = batch["op_types"].to(device)
            op_frame_flags = batch["op_frame_flags"].to(device)
            labels = batch["labels"].to(device)
            src_key_padding_mask = batch["src_key_padding_mask"].to(device)
            if use_crf:
                loss = model(ssim_features, op_types, op_frame_flags, labels=labels, src_padding_mask=src_key_padding_mask)
            else:
                emissions = model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                loss = criterion_focal(emissions, labels)
            total_loss += loss.item()
    return total_loss / len(dataloader)

# --- 7. 预测函数 (可供外部使用) ---
def predict_on_single_item(model, item_data, device, local_idx_to_label, use_crf=True):
    # item_data is expected to be a single dictionary from raw_data_list
    model.eval()
    with torch.no_grad():
        ssim_features = item_data["ssim_features"].unsqueeze(0).to(device)
        op_types = item_data["op_type"].unsqueeze(0).to(device)
        op_frame_flags = item_data["op_frame_flag"].unsqueeze(0).to(device)
        seq_len = ssim_features.size(1)
        src_key_padding_mask = torch.zeros(1, seq_len, dtype=torch.bool).to(device)

        if use_crf:
            predicted_sequence_list = model(ssim_features, op_types, op_frame_flags, labels=None, src_padding_mask=src_key_padding_mask)
            predictions_indices = torch.tensor(predicted_sequence_list[0], device=device)
        else:
            emissions = model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
            predictions_indices = torch.argmax(emissions, dim=-1).squeeze(0)

    print(f"\n--- Prediction for Sample ID: {item_data['id']} (OpType: {item_data['op_type'].item()}) ---")
    print(f"Sequence Length: {seq_len}")
    op_features_used_str = "Yes" if model.use_op_features else "No"
    print(f"Model used OpFeatures: {op_features_used_str}")
    print("Frame | Op? | True Label       | Predicted Label")
    print("---------------------------------------------------")
    true_labels_present = "labels" in item_data and item_data["labels"] is not None
    for i in range(seq_len):
        true_label_str = "N/A"
        if true_labels_present:
            true_label_val = item_data["labels"][i].item()
            true_label_str = local_idx_to_label.get(true_label_val, f"INVALID({true_label_val})")
        
        pred_idx = i if i < len(predictions_indices) else -1 # Safety for varying length from CRF decode
        if pred_idx != -1:
            pred_label_val = predictions_indices[pred_idx].item()
            pred_label_str = local_idx_to_label.get(pred_label_val, f"ERR({pred_label_val})")
        else:
            pred_label_str = "ERR (Index out of bounds)"

        op_flag_str = "Yes" if item_data["op_frame_flag"][i].item() == 1.0 else "No "
        print(f"{i:03d}   | {op_flag_str} | {true_label_str:<16} | {pred_label_str:<16}")
    print("---------------------------------------------------")


# --- NEW: 7.5. 整体评估函数 ---
def evaluate_model_on_test_set(model, test_dataloader, device, local_idx_to_label, use_crf=True, local_pad_label_id=PAD_LABEL_ID):
    model.eval()
    all_true_labels_flat = []
    all_pred_labels_flat = []
    print("\nStarting evaluation on the test set...")
    with torch.no_grad():
        for batch_idx, batch in enumerate(test_dataloader):
            ssim_features = batch["ssim_features"].to(device)
            op_types = batch["op_types"].to(device)
            op_frame_flags = batch["op_frame_flags"].to(device)
            labels_batch = batch["labels"].to(device) # (B, SeqLen)
            src_key_padding_mask = batch["src_key_padding_mask"].to(device)
            actual_lengths = (~src_key_padding_mask).sum(dim=1) # (B)

            if use_crf:
                # model returns list of lists of decoded tags
                # e.g. [[tag1, tag2], [tagA, tagB, tagC]] for batch_size=2
                predicted_sequences_list_of_lists = model(ssim_features, op_types, op_frame_flags, labels=None, src_padding_mask=src_key_padding_mask)
                
                for i in range(len(predicted_sequences_list_of_lists)):
                    true_labels_for_sample = labels_batch[i][:actual_lengths[i]].tolist()
                    pred_labels_for_sample = predicted_sequences_list_of_lists[i] # Already a list
                    
                    # Ensure pred_labels match actual_length (CRF output length should match unpadded input length)
                    if len(pred_labels_for_sample) != actual_lengths[i]:
                        # This case should ideally not happen if CRF mask is correct
                        # print(f"Warning: Mismatch in length for sample {i}. True: {actual_lengths[i]}, Pred: {len(pred_labels_for_sample)}. Truncating/Padding pred.")
                        # For safety, align lengths. This might affect metrics if frequent.
                        pred_labels_for_sample = pred_labels_for_sample[:actual_lengths[i]]
                        while len(pred_labels_for_sample) < actual_lengths[i]:
                            pred_labels_for_sample.append(0) # Pad with a default label like 'O'
                            
                    all_true_labels_flat.extend(true_labels_for_sample)
                    all_pred_labels_flat.extend(pred_labels_for_sample)

            else: # Not using CRF
                emissions = model._get_emissions(ssim_features, op_types, op_frame_flags, src_key_padding_mask)
                predictions_indices_batch = torch.argmax(emissions, dim=-1) # (B, SeqLen)

                for i in range(predictions_indices_batch.shape[0]): # Iterate over batch
                    seq_len_actual = actual_lengths[i].item()
                    true_labels_for_sample = labels_batch[i][:seq_len_actual].tolist()
                    pred_labels_for_sample = predictions_indices_batch[i][:seq_len_actual].tolist()
                    
                    all_true_labels_flat.extend(true_labels_for_sample)
                    all_pred_labels_flat.extend(pred_labels_for_sample)
            
            if (batch_idx + 1) % (max(1, len(test_dataloader)//2)) == 0 or batch_idx == len(test_dataloader) -1 :
                 print(f"  Evaluated batch {batch_idx+1}/{len(test_dataloader)}")

    if not all_true_labels_flat or not all_pred_labels_flat:
        print("Error: No labels collected for evaluation. Cannot generate report.")
        return None
    
    # Filter out PAD_LABEL_ID if they somehow made it (though logic above tries to use actual_lengths)
    # This step might not be strictly necessary if above logic is perfect, but as a safeguard.
    # For classification_report, we need to ensure inputs are consistent.
    # However, the above logic using actual_lengths should prevent PAD_LABEL_ID from being included.

    target_names = [local_idx_to_label[i] for i in sorted(local_idx_to_label.keys()) if i != local_pad_label_id]
    labels_for_report = [i for i in sorted(local_idx_to_label.keys()) if i != local_pad_label_id]

    # Ensure all_pred_labels_flat contains only labels present in labels_for_report, or handle unknown preds
    # This is mostly for safety if model predicts something unexpected, though unlikely with fixed num_classes
    filtered_preds = []
    filtered_trues = []
    for true_label, pred_label in zip(all_true_labels_flat, all_pred_labels_flat):
        if true_label in labels_for_report: # Only consider true labels that are not PAD
            filtered_trues.append(true_label)
            # If pred_label is somehow outside our known non-PAD labels, map it to a default (e.g., "O") or skip
            # For now, let's assume predictions are within the class range
            filtered_preds.append(pred_label if pred_label in labels_for_report else labels_map.get("O", 0))

    if not filtered_trues or not filtered_preds:
        print("Error: After filtering, no valid labels for evaluation.")
        return None

    try:
        print("\n==== Test Set Evaluation Report ====")
        # Ensure labels_for_report doesn't include PAD_LABEL_ID for report generation.
        report = classification_report(filtered_trues, filtered_preds, labels=labels_for_report, target_names=target_names, digits=4, zero_division=0)
        overall_accuracy = accuracy_score(filtered_trues, filtered_preds)
        print(report)
        print(f"Overall Accuracy: {overall_accuracy:.4f}")
        return {"report": report, "accuracy": overall_accuracy}
    except Exception as e:
        print(f"Error generating classification report: {e}")
        print("Unique true labels collected:", sorted(list(set(all_true_labels_flat))))
        print("Unique pred labels collected:", sorted(list(set(all_pred_labels_flat))))
        print("Labels for report:", labels_for_report)
        print("Target names for report:", target_names)
        return None

# --- 8. 封装的训练流程函数 ---
def run_training_pipeline(
    all_raw_data: list,
    training_config: Config,
    use_crf_layer: bool
):
    """
    完整的训练流程函数。
    Args:
        all_raw_data (list): 包含所有数据项的列表。
        training_config (Config): 配置对象。
        use_crf_layer (bool): 是否在模型中使用CRF层。
    Returns:
        tuple: (trained_model, training_history)
               trained_model: 训练好的模型 (已加载最佳权重)。
               training_history: 包含训练和验证损失的字典。
    """
    print(f"--- Starting Training Pipeline ---")
    print(f"Device: {training_config.device}")
    print(f"Using CRF layer: {use_crf_layer}")
    print(f"Including operation features: {training_config.include_operation_features}")

    # --- 数据准备与划分 ---
    random.shuffle(all_raw_data)
    split_idx = int(len(all_raw_data) * (1 - training_config.validation_split))
    train_raw_data = all_raw_data[:split_idx]
    val_raw_data = all_raw_data[split_idx:]

    print(f"Total samples: {len(all_raw_data)}, Training: {len(train_raw_data)}, Validation: {len(val_raw_data)}")

    train_dataset = ScreenRecordingDataset(train_raw_data)
    val_dataset = ScreenRecordingDataset(val_raw_data)
    
    train_dataloader = DataLoader(train_dataset, batch_size=training_config.batch_size, shuffle=True, collate_fn=collate_fn)
    val_dataloader = DataLoader(val_dataset, batch_size=training_config.val_batch_size, shuffle=False, collate_fn=collate_fn)

    # Alpha 权重计算 (基于训练集)
    current_alpha_weights = None
    if not use_crf_layer and len(train_raw_data) > 0: # 仅当不使用CRF且需要Focal Loss时计算
        all_train_labels_flat = torch.cat([d["labels"] for d in train_raw_data if d["labels"] is not None])
        all_train_labels_flat_no_pad = all_train_labels_flat[all_train_labels_flat != PAD_LABEL_ID]
        
        if len(all_train_labels_flat_no_pad) > 0:
            # 使用全局 num_classes
            class_counts = torch.bincount(all_train_labels_flat_no_pad, minlength=num_classes)
            alpha_w = 1.0 / (class_counts.float() + 1e-6) 
            alpha_w = alpha_w / alpha_w.sum()
            current_alpha_weights = alpha_w.to(training_config.device)
            print(f"Calculated Alpha Weights for Focal Loss: {current_alpha_weights}")
        else:
            print("Warning: No valid labels in training set for alpha weights.")
    
    # --- 模型、损失、优化器、调度器、早停 初始化 ---
    # 使用全局 num_classes
    model = FrameTaggingTransformerWithCRF(
        model_config=training_config, # 传入完整config
        d_model=training_config.d_model,
        nhead=training_config.nhead,
        num_encoder_layers=training_config.num_encoder_layers,
        dim_feedforward=training_config.dim_feedforward,
        num_classes_out=num_classes, 
        dropout=training_config.dropout,
        use_op_features=training_config.include_operation_features
    ).to(training_config.device)

    criterion_focal = None
    if not use_crf_layer:
        criterion_focal = FocalLoss(alpha=current_alpha_weights, 
                                    gamma=training_config.focal_loss_gamma, 
                                    ignore_index=PAD_LABEL_ID)

    optimizer = optim.AdamW(model.parameters(), lr=training_config.learning_rate, weight_decay=training_config.weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', 
                                                     patience=max(2, training_config.early_stopping_patience // 3),
                                                     factor=0.5, verbose=True, min_lr=1e-7)
    early_stopper = EarlyStopping(patience=training_config.early_stopping_patience, 
                                  min_delta=training_config.early_stopping_min_delta, 
                                  verbose=True)

    # --- 训练循环 ---
    history = {'train_loss': [], 'val_loss': []}
    print("\nStarting training loop...")
    for epoch in range(training_config.num_epochs):
        avg_train_loss = _train_epoch_internal(model, train_dataloader, criterion_focal, optimizer, 
                                          training_config.device, epoch, training_config.num_epochs, 
                                          use_crf=use_crf_layer)
        avg_val_loss = _evaluate_epoch_internal(model, val_dataloader, criterion_focal, 
                                           training_config.device, use_crf=use_crf_layer)
        
        print(f"Epoch [{epoch+1}/{training_config.num_epochs}] summary. Avg Train Loss: {avg_train_loss:.4f}, Avg Val Loss: {avg_val_loss:.4f}, LR: {optimizer.param_groups[0]['lr']:.2e}")

        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        
        scheduler.step(avg_val_loss)
        early_stopper(avg_val_loss, model)
        if early_stopper.early_stop:
            print(f"Early stopping triggered at epoch {epoch+1}.")
            break
    
    print("Training finished.")
    early_stopper.load_best_weights(model) # 加载最佳模型权重

    return model, history

# --- Main Execution Block ---
if __name__ == "__main__":
    # 1. 初始化配置
    master_config = Config()
    
    # 可以按需修改配置项，例如:
    # master_config.num_epochs = 5
    # master_config.include_operation_features = False
    # master_config.early_stopping_patience = 3

    # --- MODIFIED: Load multiple training files ---
    train_set_paths = ["train_data.pt"] # 用户可以修改这里，添加更多文件路径
    # Example: train_set_paths = ["train_data_fold1.pt", "train_data_fold2.pt"]
    
    # --- MODIFIED: Load multiple test files ---
    test_set_paths = ["test_data.pt"] # 用户可以修改这里，添加更多文件路径
    # Example: test_set_paths = ["test_data_fold1.pt", "test_data_fold2.pt"]
    
    combined_train_set = []
    if not train_set_paths:
        print("错误：训练文件路径列表为空！")
        exit(1) # 或者抛出异常

    for t_path in train_set_paths:
        try:
            print(f"Loading training data from: {t_path}")
            loaded_data = torch.load(t_path)
            if isinstance(loaded_data, list):
                combined_train_set.extend(loaded_data)
            else:
                print(f"警告：文件 {t_path} 未包含列表数据，已跳过。")
        except FileNotFoundError:
            print(f"警告：训练文件 {t_path} 未找到，已跳过。")
        except Exception as e:
            print(f"警告：加载训练文件 {t_path} 时出错: {e}，已跳过。")

    if not combined_train_set:
        print("错误：未能从指定路径加载任何有效的训练数据。")
        exit(1) # 或者抛出异常
    
    print(f"Successfully loaded a total of {len(combined_train_set)} training samples from {len(train_set_paths)} file(s).")
    
    # --- MODIFIED: Load and combine multiple test set files ---
    test_set = [] # Initialize as an empty list to extend
    if not test_set_paths:
        print("警告：测试文件路径列表为空，测试集将为空。")
    else:
        for t_path in test_set_paths:
            try:
                print(f"Loading test data from: {t_path}")
                loaded_data = torch.load(t_path)
                if isinstance(loaded_data, list):
                    test_set.extend(loaded_data)
                else:
                    print(f"警告：测试文件 {t_path} 未包含列表数据，已跳过。")
            except FileNotFoundError:
                print(f"警告：测试文件 {t_path} 未找到，已跳过。")
            except Exception as e:
                print(f"警告：加载测试文件 {t_path} 时出错: {e}，已跳过。")

    if test_set:
        print(f"Successfully loaded a total of {len(test_set)} test samples from {len(test_set_paths)} file(s).")
    else:
        print("警告：未能从指定路径加载任何有效的测试数据，测试集为空。")
    
    # 3. 设置是否使用CRF层
    SHOULD_USE_CRF = True

    # 4. 调用训练流程函数
    trained_model_instance, training_run_history = run_training_pipeline(
        all_raw_data=combined_train_set, # 使用合并后的训练集
        training_config=master_config,
        use_crf_layer=SHOULD_USE_CRF
    )
    print("\n==== 训练完成，训练历史 ====")
    if training_run_history and training_run_history.get('train_loss') and training_run_history.get('val_loss'): # 检查 history 内容
        for epoch_idx, (tl, vl) in enumerate(zip(training_run_history['train_loss'], training_run_history['val_loss'])):
            print(f"Epoch {epoch_idx+1}: Train Loss: {tl:.4f}, Val Loss: {vl:.4f}")
    else:
        print("没有记录到训练历史或历史记录不完整。")

    # === MODIFIED: 对测试集进行整体评估 ===
    if trained_model_instance and test_set:
        # 为测试集创建 DataLoader
        test_dataset = ScreenRecordingDataset(test_set)
        test_dataloader = DataLoader(test_dataset, batch_size=master_config.batch_size, shuffle=False, collate_fn=collate_fn)
        
        evaluate_model_on_test_set(
            trained_model_instance,
            test_dataloader,
            master_config.device,
            idx_to_label, # 全局变量
            use_crf=SHOULD_USE_CRF,
            local_pad_label_id=PAD_LABEL_ID # 全局变量
        )
    elif not trained_model_instance:
        print("模型未成功训练，无法进行评估。")
    elif not test_set:
        print("测试集为空或加载失败，无法进行评估。")
    else:
        print("未知原因，无法进行测试集评估。")
