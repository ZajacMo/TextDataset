import logging
from typing import Any, Optional


def extract(item: Any, is_sharegpt: bool = False) -> Optional[str]:
    """
    从输入对象中抽取文本。
    - 支持字符串、字典（普通 JSON 与 ShareGPT 格式）。
    - 返回规范化（去首尾空白、压缩多空格）的文本或 None。
    """
    if isinstance(item, str):
        t = item.strip()
        return t if t else None

    if isinstance(item, dict):
        if is_sharegpt:
            conv = item.get('conversation')
            if isinstance(conv, list) and conv:
                texts = []
                for m in conv:
                    if isinstance(m, dict):
                        v = m.get('human')
                        if isinstance(v, str):
                            texts.append(' '.join(v.split()))
                if texts:
                    return ' '.join(texts)

            convs = item.get('conversations')
            if isinstance(convs, list) and convs:
                v = convs[0].get('value')
                if isinstance(v, str):
                    return ' '.join(v.split())

        v_text = item.get('text')
        if isinstance(v_text, str):
            t = v_text.strip()
            return t if t else None

        v_human = item.get('human')
        if isinstance(v_human, str):
            t = ' '.join(v_human.split())
            return t if t else None

    return None