# dataset_management 使用说明

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