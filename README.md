# TextDataset

A comprehensive Python library for unified text dataset management and processing especially for **large language models**. Load text from JSON/JSONL files or directories, apply filtering and sampling, iterate sequentially or randomly, and batch output with ease.

[![Language](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE.txt)

🌐  [**中文**](README_zh.md)

## ✨ Features

- **🔄 Multi-format Support**: JSON, JSONL, and directory parsing
- **🎯 Smart Text Extraction**: Built-in ShareGPT format support
- **🔍 Advanced Filtering**: Multi-dimensional length filtering (words/chars/tokens)
- **🎲 Flexible Sampling**: Random, sequential, and specified index sampling
- **🔄 Multiple Iteration Modes**: Sequential and random batch processing
- **📊 Statistics & Analytics**: Built-in dataset statistics
- **🎛️ Highly Configurable**: Comprehensive configuration system
- **🚀 Performance Optimized**: Efficient processing with optional caching

## 📁 Project Structure

- `dataset.py`: Core `TextDataset` class for indexing, filtering, shuffling, sampling, iteration, and batch output
- `io.py`: Data source traversal and JSON/JSONL parsing utilities
- `extractors.py`: Text extraction from raw entries, ShareGPT format support
- `filters.py`: Length-based and custom predicate filtering
- `samplers.py`: Random, sequential, and specified index samplers
- `types.py`: Configuration data classes (`FilterConfig`, `SampleConfig`)
- `extract_method.py`: Extension points for extraction methods

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from dataset_management import TextDataset, FilterConfig

# Create dataset and build index (automatically parses JSON/JSONL files in directory)
ds = TextDataset(source='data/', is_sharegpt=True, seed=42)
ds.build_index()

# Filter: 30-50 characters, must contain Chinese characters
import re
def has_chinese(t: str) -> bool:
    return re.search(r'[\u4e00-\u9fff]', t) is not None

ds.filter(FilterConfig(min_len=30, max_len=50, unit='chars', predicate=has_chinese))

# Shuffle and get texts
ds.shuffle()
texts = ds.texts
```

## 🔧 Advanced Configuration

### Filtering Options

**FilterConfig Parameters:**
- `min_len`/`max_len`: Length range (optional)
- `unit`: `'words' | 'chars' | 'tokens'` (count by words/characters/token)
- `predicate`: Custom boolean function, texts returning `True` are kept

**Examples:**

```python
# Filter by word count
ds.filter(FilterConfig(min_len=10, max_len=100, unit='words'))

# Filter by character count  
ds.filter(FilterConfig(min_len=50, max_len=500, unit='chars'))

# Custom predicate filtering
def is_english(t: str) -> bool:
    return re.match(r'^[a-zA-Z\s]+$', t) is not None

ds.filter(FilterConfig(predicate=is_english))
```

### Sampling Options

**SampleConfig Parameters:**
- `n`: Number of samples to select
- `mode`: `'random' | 'sequential' | 'specified'`
- Other: `seed`, `replace`, `indices`

**Examples:**

```python
from dataset_management.types import SampleConfig

# Random sample 100 texts
samples = ds.select(SampleConfig(n=100, mode='random', seed=123))

# Sequential sample all texts
samples = ds.select(SampleConfig(mode='sequential'))

# Sample specific indices
samples = ds.select(SampleConfig(n=50, mode='specified', indices=[0, 2, 5, 10]))
```

## 📊 Dataset Statistics

```python
# Get dataset statistics
stats = ds.stats()
print(f"Count: {stats['count']}")
print(f"Min words: {stats['min_words']}")
print(f"Max words: {stats['max_words']}")
print(f"P50 words: {stats['p50_words']}")
print(f"P90 words: {stats['p90_words']}")
```

## 🔄 Iteration & Batch Processing

### Sequential Iteration
```python
# Simple iteration
for text in ds.iter(mode='sequential'):
    print(text)

# Cyclical iteration (loops forever)
for text in ds.iter(mode='sequential', cycle=True):
    print(text)  # Will continue indefinitely
```

### Batch Processing
```python
# Sequential batches
for batch in ds.get_batch(batch_size=32, mode='sequential', drop_last=False):
    # Process batch (List[str])
    process_batch(batch)

# Random batches (shuffled)
for batch in ds.get_batch(batch_size=64, mode='random', drop_last=True):
    # Process batch (List[str])
    process_batch(batch)
```

## 📝 Supported Data Formats

### JSON Files
```json
{
  "text": "Hello, world!",
  "metadata": {
    "source": "dataset1"
  }
}
```

### JSONL Files
```jsonl
{"text": "First document"}
{"text": "Second document"}
{"text": "Third document"}
```

### ShareGPT Format
```json
{
  "conversation": [
    {
      "human": "What is the capital of France?",
      "gpt": "The capital of France is Paris."
    }
  ]
}
```

## ⚙️ Configuration Examples

### Real-world Example: Processing Chat Data

```python
from dataset_management import TextDataset, FilterConfig, SampleConfig
import re

# Load ShareGPT format chat data
ds = TextDataset(source='chat_data/', is_sharegpt=True, seed=42)
ds.build_index()

print(f"Original dataset size: {len(ds.texts)}")

# Filter out very short or very long conversations
ds.filter(FilterConfig(
    min_len=20,  # At least 20 characters
    max_len=1000,  # Max 1000 characters
    unit='chars'
))

# Filter for conversations containing questions
def has_question(t: str) -> bool:
    return '?' in t

ds.filter(FilterConfig(predicate=has_question))

# Sample 1000 high-quality conversations
samples = ds.select(SampleConfig(n=1000, mode='random', seed=123))

print(f"Filtered dataset size: {len(samples)}")

# Process in batches for training
for batch in ds.get_batch(batch_size=64, mode='random'):
    # Batch contains filtered and shuffled texts
    train_model(batch)
```

### Token-based Filtering

```python
from transformers import AutoTokenizer

# Load tokenizer for token-based filtering
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

ds = TextDataset(source='data/', tokenizer=tokenizer, seed=42)
ds.build_index()

# Filter by token count (e.g., for language model training)
ds.filter(FilterConfig(min_len=128, max_len=512, unit='tokens'))
```

## 📋 API Reference

### Core Classes

#### `TextDataset`
Main class for dataset management.

**Constructor Parameters:**
- `source`: Data source path (single file or directory)
- `is_sharegpt`: Whether to parse in ShareGPT format
- `tokenizer`: Optional tokenizer for token-based filtering
- `cache`: Whether to cache parsed results (future extension)
- `seed`: Random seed for reproducible shuffling and sampling

**Key Methods:**
- `build_index(drop_empty=True)`: Parse and build internal text index
- `filter(cfg: FilterConfig)`: Filter by length range and custom predicates
- `shuffle(seed: Optional[int] = None)`: Shuffle text list
- `select(cfg: SampleConfig) -> List[str]`: Sample texts according to configuration
- `iter(mode='sequential', cycle=False)`: Sequential iteration
- `get_batch(batch_size: int, mode='sequential'|'random', drop_last=False)`: Batch iteration
- `stats() -> dict`: Get dataset statistics

#### `FilterConfig`
Configuration for text filtering.

**Parameters:**
- `min_len`: Minimum length threshold
- `max_len`: Maximum length threshold  
- `unit`: Length unit (`'words'`, `'chars'`, or `'tokens'`)
- `predicate`: Custom boolean function for filtering

#### `SampleConfig`
Configuration for text sampling.

**Parameters:**
- `n`: Number of texts to sample
- `mode`: Sampling mode (`'random'`, `'sequential'`, or `'specified'`)
- `indices`: Specific indices for `'specified'` mode
- `replace`: Whether to sample with replacement
- `seed`: Random seed for reproducible sampling

## ⚠️ Important Notes

- Data source `source` can be a single file or directory; all `.json`/`.jsonl` files in the directory will be parsed
- When `is_sharegpt=True`, texts are extracted according to ShareGPT format specifications
- For token-based filtering, a usable `tokenizer` must be provided to `TextDataset`
- `build_index()` performs basic empty text removal and random shuffling (affected by `seed`)
- The library maintains text order consistency during filtering and sampling operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

📖 **For detailed Chinese documentation, see [README_zh.md](README_zh.md)**