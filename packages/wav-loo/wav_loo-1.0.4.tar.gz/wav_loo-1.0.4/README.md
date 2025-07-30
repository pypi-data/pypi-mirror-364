# WAV Loo

版本：1.0.4

`wav-loo` 是一个为音频处理和云原生开发设计的集成工具箱，它提供了三大核心功能：

1.  **WAV 文件查找器**：在本地或远程URL中快速定位WAV音频文件。
2.  **命令行快捷别名**：集成了数十个常用的 `kubectl`、`atlasctl` 和其他开发运维命令，提升效率。
3.  **Loss 函数库**：提供针对音频信号处理和深度学习的专用损失函数。

## 安装

```bash
pip install wav-loo
```

## 功能一：WAV 文件查找

你可以在Python代码中或通过命令行来查找WAV文件。

### 命令行用法

```bash
wav-loo find <路径或URL> [--output <文件>] [--verbose]
```
-   **示例**:
    -   `wav-loo find /path/to/audio`
    -   `wav-loo find https://example.com/audio-files/`

### Python API 用法

```python
from wav_loo import WavFinder
finder = WavFinder()
wavs = finder.find_wav_files('/path/to/audio')
print(wavs)
```

## 功能二：快捷命令

通过 `wav-loo` 执行常用的运维开发命令，无需配置复杂的alias。

### 命令行用法

只需将别名作为 `wav-loo` 的子命令即可。

-   **示例**:
    ```bash
    # 查看pods (等价于 kubectl get pods -o wide)
    wav-loo kg

    # 查看signal命名空间日志 (等价于 kubectl logs -n signal)
    wav-loo kln

    # 使用unimirror安装numpy (等价于 uv pip install -i ... numpy)
    wav-loo uv numpy
    ```

### 支持的快捷命令列表

| 子命令 | 等价 bash 命令                                    | 说明                                     |
|--------|---------------------------------------------------|------------------------------------------|
| `kd`   | `kubectl delete pods`                             | 删除所有pods                             |
| `kg`   | `kubectl get pods -o wide`                        | 查看pods（详细）                         |
| `kl`   | `kubectl logs`                                    | 查看日志                                 |
| `rs`   | `kubectl describe ResourceQuota -n ...`           | 查看资源配额（需补命名空间）             |
| `kdn`  | `kubectl delete pods -n signal`                   | 删除signal命名空间pods                   |
| `kgn`  | `kubectl get pods -o wide -n signal`              | 查看signal命名空间pods                   |
| `kln`  | `kubectl logs -n signal`                          | 查看signal命名空间日志                   |
| `at`   | `atlasctl top node`                               | atlas节点监控                            |
| `ad`   | `atlasctl delete job`                             | 删除atlas作业                            |
| `atd`  | `atlasctl delete`                                 | 删除atlas资源                            |
| `adp`  | `atlasctl delete job pytorchjob`                  | 删除pytorch作业                          |
| `adn`  | `atlasctl delete job -n signal`                   | 删除signal命名空间作业                   |
| `tb`   | `tensorboard --port=3027 --logdir=.`              | 启动tensorboard                          |
| `ca`   | `conda activate <env>`                            | 激活conda环境（需补环境名）              |
| `gp`   | `gpustat -i`                                      | 查看GPU状态                              |
| `kgg`  | `kubectl get po --all-namespaces -o wide | grep ...`| 全局查找pod（需补pod名）                 |
| `uv`   | `uv pip install -i ...`                           | 使用unimirror安装PyPI包（需补包名）      |


## 功能三：Loss 函数库

`wav-loo` 提供了一系列在信号处理和深度学习中常用的损失函数。

### `multi_channel_separation_consistency_loss`

**功能**:

计算多通道（N>2）音频信号分离后的一致性损失。该损失旨在惩罚模型输出的多个通道之间的**幅度谱**差异与原始目标信号中对应通道之间的**幅度谱**差异不一致的情况。它通过计算所有通道对 (pair) 的预测幅度谱差异和目标幅度谱差异，然后最小化这两组差异之间的L1距离来实现。

**使用方法**:

```python
import torch
from wav_loo.loss import multi_channel_separation_consistency_loss

# 假设 pred_mag_specs 和 target_mag_specs 是你的模型输出和目标真值
# 形状: (B, N, F, T), 类型: torch.float32
# B: batch_size, N: 通道数, F: 频率bins, T: 时间帧
pred_mag_specs = torch.randn(8, 4, 257, 100, dtype=torch.float32)
target_mag_specs = torch.randn(8, 4, 257, 100, dtype=torch.float32)

loss = multi_channel_separation_consistency_loss(pred_mag_specs, target_mag_specs)
print(f"一致性损失: {loss.item()}")
```

## 依赖
- Python 3.7+
- requests
- beautifulsoup4
- urllib3

## 许可证
MIT License 