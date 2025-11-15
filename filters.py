from typing import Callable, Iterable, List, Optional, Tuple


def length_words(text: str) -> int:
    return len(text.split())


def length_chars(text: str) -> int:
    return len(text)


def length_tokens(text: str, tokenizer) -> int:
    return len(tokenizer(text).input_ids)


def by_length(
    texts: Iterable[str],
    min_len: Optional[int],
    max_len: Optional[int],
    unit: str = 'words',
    tokenizer=None,
) -> List[int]:
    idxs: List[int] = []
    for i, t in enumerate(texts):
        if unit == 'words':
            L = length_words(t)
        elif unit == 'chars':
            L = length_chars(t)
        elif unit == 'tokens':
            if tokenizer is None:
                raise ValueError('tokenizer is required for unit=tokens')
            L = length_tokens(t, tokenizer)
        else:
            raise ValueError(f'Unknown unit: {unit}')
        if (min_len is None or L >= min_len) and (max_len is None or L <= max_len):
            idxs.append(i)
    return idxs


def by_predicate(texts: Iterable[str], pred: Callable[[str], bool]) -> List[int]:
    return [i for i, t in enumerate(texts) if pred(t)]