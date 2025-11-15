import random
from typing import List, Optional, Iterable, Iterator

from .types import FilterConfig, SampleConfig
from .io import iter_json, iter_jsonl, iter_sources
from .extractors import extract
from .filters import by_length, by_predicate
from .samplers import RandomSampler, SequentialSampler, SpecifiedSampler


class TextDataset:
    """
    文本数据集核心类，封装从JSON/JSONL文件（或目录）加载、过滤、采样与迭代的全流程能力
    支持ShareGPT格式解析、多维度长度过滤、三种采样模式（随机/顺序/指定索引）与批量迭代
    使用示例：
    ds = TextDataset(source='data_dir/', is_sharegpt=True, seed=42)
    ds.build_index()  # 解析并构建文本索引
    ds.filter(FilterConfig(min_len=32, max_len=512, unit='words'))  # 按词长过滤
    samples = ds.select(SampleConfig(n=100, mode='random'))  # 随机采样100条
    """
    def __init__(
        self,
        source: str,
        is_sharegpt: bool = False,
        tokenizer=None,
        cache: bool = True,
        seed: int = 0,
    ):
        self.source = source  # 数据来源路径（单文件或目录）
        self.is_sharegpt = is_sharegpt  # 是否按ShareGPT格式解析文本
        self.tokenizer = tokenizer  # 可选Tokenizer，用于按token长度过滤
        self.cache = cache  # 是否缓存解析结果（暂未实现，预留扩展）
        self.seed = seed  # 随机种子，保证打乱与采样可复现
        self._texts: List[str] = []  # 内部存储的已处理文本列表

    @property
    def texts(self) -> List[str]:
        """返回已处理的文本列表（只读）"""
        return self._texts

    def build_index(self, drop_empty: bool = True) -> None:
        texts: List[str] = []
        for fp in iter_sources(self.source):
            iters = iter_jsonl(fp) if fp.endswith('.jsonl') else iter_json(fp)
            """
            遍历数据源文件：
            - JSONL文件逐行解析
            - JSON文件按列表/字典解析
            调用extract函数抽取文本并过滤空值
            """
            for item in iters:
                t = extract(item, self.is_sharegpt)
                if t:
                    texts.append(t)
        if drop_empty:
            texts = [t for t in texts if t and t.strip()]
        if not texts:
            """若未提取到有效文本，抛出值错误"""
            raise ValueError('No valid texts found from source')
        rnd = random.Random(self.seed)
        rnd.shuffle(texts)
        self._texts = texts

    def stats(self) -> dict:
        """
        返回文本列表的统计信息（仅基于词长）
        返回结构：
        - count: 文本数量
        - min_words: 最短词长
        - max_words: 最长词长
        - p50_words: 50分位数词长
        - p90_words: 90分位数词长
        """
        if not self._texts:
            return {'count': 0}
        lengths = [len(t.split()) for t in self._texts]
        lengths_sorted = sorted(lengths)
        def pct(p):
            i = max(0, min(len(lengths_sorted)-1, int(p * (len(lengths_sorted)-1))))
            return lengths_sorted[i]
        return {
            'count': len(self._texts),
            'min_words': lengths_sorted[0],
            'max_words': lengths_sorted[-1],
            'p50_words': pct(0.5),
            'p90_words': pct(0.9),
        }

    def filter(self, cfg: FilterConfig) -> None:
        """
        根据FilterConfig过滤文本列表
        支持：
        - 长度范围过滤（词/字符/token单位）
        - 自定义谓词过滤
        """
        idxs = list(range(len(self._texts)))
        if cfg.min_len is not None or cfg.max_len is not None:
            idxs = by_length(self._texts, cfg.min_len, cfg.max_len, cfg.unit, self.tokenizer)
        if cfg.predicate is not None:
            pidx = by_predicate([self._texts[i] for i in idxs], cfg.predicate)
            idxs = [idxs[i] for i in pidx]
        self._texts = [self._texts[i] for i in idxs]

    def shuffle(self, seed: Optional[int] = None) -> None:
        """
        打乱文本列表顺序，支持指定新种子覆盖初始化种子
        """
        rnd = random.Random(self.seed if seed is None else seed)
        rnd.shuffle(self._texts)

    def select(self, cfg: SampleConfig) -> List[str]:
        """
        根据SampleConfig选择文本样本
        支持模式：
        - random: 随机采样（支持有放回/无放回）
        - sequential: 顺序采样
        - specified: 指定索引采样
        """
        if cfg.mode == 'random':
            sampler = RandomSampler(self._texts, seed=cfg.seed or self.seed, replace=cfg.replace)
        elif cfg.mode == 'sequential':
            sampler = SequentialSampler(self._texts)
        elif cfg.mode == 'specified':
            sampler = SpecifiedSampler(self._texts, cfg.indices or [])
        else:
            raise ValueError(f'Unknown sample mode: {cfg.mode}')
        return sampler.sample(cfg.n)

    def iter(self, mode: str = 'sequential', cycle: bool = False) -> Iterator[str]:
        """
        迭代输出文本
        参数：
        - mode: 仅支持'sequential'（顺序迭代）
        - cycle: 是否循环迭代（到达末尾后重新开始）
        """
        if mode == 'sequential':
            sampler = SequentialSampler(self._texts)
            yield from sampler.iterate(cycle=cycle)
        else:
            raise ValueError('Only sequential iteration is supported for iter()')

    def get_batch(self, batch_size: int, mode: str = 'sequential', drop_last: bool = False) -> Iterator[List[str]]:
        """
        批量迭代输出文本
        参数：
        - batch_size: 批次大小
        - mode: 'sequential'（顺序批处理）/ 'random'（随机批处理）
        - drop_last: 是否丢弃最后一个不足批次大小的批次
        返回：迭代器，每次返回一个文本列表（批次）
        """
        if mode == 'sequential':
            for i in range(0, len(self._texts), batch_size):
                batch = self._texts[i:i + batch_size]
                if batch or not drop_last:
                    yield batch
        elif mode == 'random':
            sampler = RandomSampler(self._texts, seed=self.seed)
            items = sampler.sample(len(self._texts))
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                if batch or not drop_last:
                    yield batch
        else:
            raise ValueError(f'Unknown batch mode: {mode}')