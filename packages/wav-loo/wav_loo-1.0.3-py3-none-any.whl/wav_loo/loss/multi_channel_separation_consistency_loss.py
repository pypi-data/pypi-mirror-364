import torch
import torch.nn as nn
import itertools

def multi_channel_separation_consistency_loss(pred_specs: torch.Tensor, target_specs: torch.Tensor) -> torch.Tensor:
    """
    计算多通道（N>2）分离一致性损失。
    该损失鼓励预测源之间的差异幅度与目标源之间的差异幅度保持一致。

    Args:
        pred_specs (torch.Tensor): 预测的复数谱图张量。
                                  形状: (B, N, F, T)，其中 B=批大小, N=通道数, F=频率轴, T=时间轴。
                                  数据类型: torch.cfloat
        target_specs (torch.Tensor): 目标的复数谱图张量。
                                     形状: (B, N, F, T)，与 pred_specs 相同。
                                     数据类型: torch.cfloat

    Returns:
        torch.Tensor: 一个标量张量，表示该批次的平均损失。
    """
    if pred_specs.shape != target_specs.shape:
        raise ValueError(f"预测和目标的形状必须一致, 但得到 {pred_specs.shape} 和 {target_specs.shape}")
        
    if not torch.is_complex(pred_specs) or not torch.is_complex(target_specs):
        raise TypeError("输入张量必须是复数类型 (torch.cfloat)")

    # 获取通道数 N
    num_channels = pred_specs.shape[1]

    # 如果通道数少于2，无法计算配对差异，损失为0
    if num_channels < 2:
        return torch.tensor(0.0, device=pred_specs.device)

    # 使用 itertools.combinations 生成所有唯一的通道索引对
    # 例如，对于 N=4, 它会生成 (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)
    indices = list(itertools.combinations(range(num_channels), 2))
    
    # 用于存储每个配对的损失
    all_pair_losses = []

    for i, j in indices:
        # 提取对应通道的预测谱图和目标谱图
        pred_i = pred_specs[:, i]
        pred_j = pred_specs[:, j]
        
        target_i = target_specs[:, i]
        target_j = target_specs[:, j]
        
        # 计算预测谱图对的差值幅度
        # torch.abs 在复数张量上计算其模长（magnitude）
        diff_pred_mag = torch.abs(pred_i - pred_j)
        
        # 计算目标谱图对的差值幅度
        diff_target_mag = torch.abs(target_i - target_j)
        
        # 计算两者幅度的 L1 差值 (绝对值差)
        # 这对应于 | |P_i - P_j| - |T_i - T_j| |
        pair_loss = torch.abs(diff_pred_mag - diff_target_mag)
        
        # 对该配对的损失在频率和时间维度上求平均
        # 我们先把每个pair的loss tensor存起来，最后一起求平均
        all_pair_losses.append(pair_loss)

    # 将所有配对的损失张量在新的维度上堆叠起来
    # 形状将变为 (num_pairs, B, F, T)
    stacked_losses = torch.stack(all_pair_losses, dim=0)
    
    # 对所有维度（包括配对、批次、频率和时间）求均值，得到最终的标量损失
    final_loss = torch.mean(stacked_losses)
    
    return final_loss

# --- 使用示例 ---
if __name__ == '__main__':
    # 定义模型参数
    BATCH_SIZE = 8
    NUM_CHANNELS = 4  # 4通道分离
    FREQ_BINS = 257
    TIME_FRAMES = 100

    # 创建模拟的预测输出和目标真值
    # 使用 torch.cfloat 来模拟复数谱图
    predicted_spectrograms = torch.randn(BATCH_SIZE, NUM_CHANNELS, FREQ_BINS, TIME_FRAMES, dtype=torch.cfloat)
    target_spectrograms = torch.randn(BATCH_SIZE, NUM_CHANNELS, FREQ_BINS, TIME_FRAMES, dtype=torch.cfloat)

    # 计算损失
    loss = multi_channel_separation_consistency_loss(predicted_spectrograms, target_spectrograms)

    print(f"为 {NUM_CHANNELS} 通道分离计算的一致性损失: {loss.item()}")

    # 测试2通道情况，以验证其与原始公式的兼容性
    predicted_2ch = torch.randn(BATCH_SIZE, 2, FREQ_BINS, TIME_FRAMES, dtype=torch.cfloat)
    target_2ch = torch.randn(BATCH_SIZE, 2, FREQ_BINS, TIME_FRAMES, dtype=torch.cfloat)
    loss_2ch = multi_channel_separation_consistency_loss(predicted_2ch, target_2ch)
    print(f"为 2 通道分离计算的一致性损失: {loss_2ch.item()}")