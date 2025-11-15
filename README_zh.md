# TextDataset

一个可用于大语言模型的统一文本数据集管理和处理的综合性 Python 库。支持从 JSON/JSONL 文件或目录加载文本、应用过滤和采样、顺序或随机迭代、批量输出等操作。

[![语言](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)
[![许可证](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE.txt)

🌐  [**English**](README.md)

## ✨ 功能特性

- **🔄 多格式支持**: JSON、JSONL 和目录解析
- **🎯 智能文本提取**: 内置 ShareGPT 格式支持
- **🔍 高级过滤**: 多维度长度过滤（词/字符/标记）
- **🎲 灵活采样**: 随机、顺序和指定索引采样
- **🔄 多种迭代模式**: 顺序和随机批处理
- **📊 统计与分析**: 内置数据集统计功能
- **🎛️ 高度可配置**: 完善的配置系统
- **🚀 性能优化**: 高效处理，支持可选缓存

本目录提供针对文本数据的统一管理与处理能力，包括从 JSON/JSONL 文件或目录加载文本、过滤与采样、顺序/随机迭代、批量输出等。核心类为 `TextDataset`，并配套若干工具模块与类型定义。

## 目录结构
- `dataset.py`：核心类 `TextDataset`，封装索引构建、过滤、打乱、采样、迭代与批量输出
- `io.py`：数据源遍历与 JSON/JSONL 解析
- `extractors.py`：从原始条目中抽取文本，支持 ShareGPT 格式
- `filters.py`：按长度与自定义谓词过滤
- `samplers.py`：随机、顺序与指定索引采样器
- `types.py`：配置数据类 `FilterConfig`、`SampleConfig`
- `extract_method.py`：抽取方法的扩展点

## 快速开始
```python
from dataset_management import TextDataset, FilterConfig

# 创建数据集并构建索引（自动解析目录中的 JSON 或 JSONL 文件）
ds = TextDataset(source='data/', is_sharegpt=True, seed=42)
ds.build_index()

# 过滤：示例为按字符长度 30~50，且必须包含中文
import re
def has_chinese(t: str) -> bool:
    return re.search(r'[\u4e00-\u9fff]', t) is not None

ds.filter(FilterConfig(min_len=30, max_len=50, unit='chars', predicate=has_chinese))

# 打乱与获取文本
ds.shuffle()
texts = ds.texts
```

## 过滤与采样
- `FilterConfig`
  - `min_len`/`max_len`：长度范围（可选）
  - `unit`：`'words' | 'chars' | 'tokens'`（按词/字符/分词 token 计数）
  - `predicate`：自定义布尔函数，返回 `True` 的文本保留
- `SampleConfig`
  - `n`：采样数量
  - `mode`：`'random' | 'sequential' | 'specified'`
  - 其他：`seed`、`replace`、`indices`

示例：随机采样 100 条文本
```python
from dataset_management.types import SampleConfig
samples = ds.select(SampleConfig(n=100, mode='random', seed=123))
```

## 常见示例：过滤 30~50 字符的中文文本
```python
import re
def has_chinese(t: str) -> bool:
    return re.search(r'[\u4e00-\u9fff]', t) is not None

ds.filter(FilterConfig(min_len=30, max_len=50, unit='chars', predicate=has_chinese))
```

## 批量与迭代
- 顺序迭代：`for t in ds.iter(mode='sequential'):`
- 批量输出：
```python
for batch in ds.get_batch(batch_size=32, mode='sequential', drop_last=False):
    # 处理 batch (List[str])
    pass
```

## 注意事项
- 数据源 `source` 可为单个文件或目录；目录下的所有 `.json`/`.jsonl` 文件都会被解析
- `is_sharegpt=True` 时针对 ShareGPT 格式进行文本抽取
- 若需要按 `tokens` 过滤，需向 `TextDataset` 传入可用的 `tokenizer`
- `build_index()` 会在载入后进行基础去空与随机打乱（受 `seed` 影响）

## API 速览（核心）
- `TextDataset.build_index(drop_empty=True)`：解析并构建内部文本列表
- `TextDataset.filter(cfg: FilterConfig)`：长度范围与自定义谓词过滤
- `TextDataset.shuffle(seed: Optional[int] = None)`：打乱文本列表
- `TextDataset.select(cfg: SampleConfig) -> List[str]`：按配置采样
- `TextDataset.iter(mode='sequential', cycle=False)`：顺序迭代
- `TextDataset.get_batch(batch_size: int, mode='sequential'|'random', drop_last=False)`：批量迭代

## 🚀 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 基础使用示例

```python
from dataset_management import TextDataset, FilterConfig

# 创建数据集并构建索引
ds = TextDataset(source='data/', is_sharegpt=True, seed=42)
ds.build_index()

# 过滤：30-50字符，且必须包含中文
import re
def has_chinese(t: str) -> bool:
    return re.search(r'[\u4e00-\u9fff]', t) is not None

ds.filter(FilterConfig(min_len=30, max_len=50, unit='chars', predicate=has_chinese))

# 打乱与获取文本
ds.shuffle()
texts = ds.texts
```

## 📊 数据集统计

```python
# 获取数据集统计信息
stats = ds.stats()
print(f"数量: {stats['count']}")
print(f"最短词数: {stats['min_words']}")
print(f"最长词数: {stats['max_words']}")
print(f"中位数词数: {stats['p50_words']}")
print(f"90分位数词数: {stats['p90_words']}")
```

## 🔄 迭代与批处理

### 顺序迭代
```python
# 简单迭代
for text in ds.iter(mode='sequential'):
    print(text)

# 循环迭代（无限循环）
for text in ds.iter(mode='sequential', cycle=True):
    print(text)  # 将持续执行
```

### 批处理
```python
# 顺序批次
for batch in ds.get_batch(batch_size=32, mode='sequential', drop_last=False):
    # 处理批次 (List[str])
    process_batch(batch)

# 随机批次（已打乱）
for batch in ds.get_batch(batch_size=64, mode='random', drop_last=True):
    # 处理批次 (List[str])
    process_batch(batch)
```

## 📝 支持的数据格式

### JSON 文件
```json
{
  "text": "你好，世界！",
  "metadata": {
    "source": "dataset1"
  }
}
```

### JSONL 文件
```jsonl
{"text": "第一个文档"}
{"text": "第二个文档"}
{"text": "第三个文档"}
```

### ShareGPT 格式
```json
{
  "conversation": [
    {
      "human": "法国的首都是什么？",
      "gpt": "法国的首都是巴黎。"
    }
  ]
}
```

## ⚙️ 配置示例

### 实际应用示例：处理聊天数据

```python
from dataset_management import TextDataset, FilterConfig, SampleConfig
import re

# 加载 ShareGPT 格式聊天数据
ds = TextDataset(source='chat_data/', is_sharegpt=True, seed=42)
ds.build_index()

print(f"原始数据集大小: {len(ds.texts)}")

# 过滤掉过短或过长的对话
ds.filter(FilterConfig(
    min_len=20,  # 至少20个字符
    max_len=1000,  # 最多1000个字符
    unit='chars'
))

# 过滤包含问题的对话
def has_question(t: str) -> bool:
    return '?' in t

ds.filter(FilterConfig(predicate=has_question))

# 采样1000个高质量对话
samples = ds.select(SampleConfig(n=1000, mode='random', seed=123))

print(f"过滤后数据集大小: {len(samples)}")

# 训练用的批次处理
for batch in ds.get_batch(batch_size=64, mode='random'):
    # 批次包含已过滤和打乱的文本
    train_model(batch)
```

### 基于标记的过滤

```python
from transformers import AutoTokenizer

# 加载分词器用于基于标记的过滤
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

ds = TextDataset(source='data/', tokenizer=tokenizer, seed=42)
ds.build_index()

# 按标记数量过滤（例如用于语言模型训练）
ds.filter(FilterConfig(min_len=128, max_len=512, unit='tokens'))
```

## 📋 API 参考

### 核心类

#### `TextDataset`
数据集管理的主类。

**构造器参数：**
- `source`：数据源路径（单个文件或目录）
- `is_sharegpt`：是否按 ShareGPT 格式解析
- `tokenizer`：用于基于标记过滤的可选分词器
- `cache`：是否缓存解析结果（未来扩展）
- `seed`：用于可重复打乱和采样的随机种子

**主要方法：**
- `build_index(drop_empty=True)`：解析并构建内部文本索引
- `filter(cfg: FilterConfig)`：按长度范围和自定义谓词过滤
- `shuffle(seed: Optional[int] = None)`：打乱文本列表
- `select(cfg: SampleConfig) -> List[str]`：根据配置采样文本
- `iter(mode='sequential', cycle=False)`：顺序迭代
- `get_batch(batch_size: int, mode='sequential'|'random', drop_last=False)`：批量迭代
- `stats() -> dict`：获取数据集统计信息

#### `FilterConfig`
文本过滤配置。

**参数：**
- `min_len`：最小长度阈值
- `max_len`：最大长度阈值  
- `unit`：长度单位（`'words'`、`'chars'` 或 `'tokens'`）
- `predicate`：用于过滤的自定义布尔函数

#### `SampleConfig`
文本采样配置。

**参数：**
- `n`：要采样的文本数量
- `mode`：采样模式（`'random'`、`'sequential'` 或 `'specified'`）
- `indices`：`'specified'` 模式下的特定索引
- `replace`：是否带放回采样
- `seed`：用于可重复采样的随机种子

## ⚠️ 重要说明

- 数据源 `source` 可以是单个文件或目录；目录下的所有 `.json`/`.jsonl` 文件都会被解析
- 当 `is_sharegpt=True` 时，根据 ShareGPT 格式规范提取文本
- 对于基于标记的过滤，必须向 `TextDataset` 提供可用的 `tokenizer`
- `build_index()` 执行基础空文本移除和随机打乱（受 `seed` 影响）
- 库在过滤和采样操作期间保持文本顺序一致性

## 🤝 贡献

欢迎贡献！请随时提交拉取请求。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

---

📖 **详细英文文档请查看 [README.md](README.md)**