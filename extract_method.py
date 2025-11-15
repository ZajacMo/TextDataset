import os
import json
import logging
import random
from glob import glob

# 定义一个函数 extract，用于从给定的数据项中提取文本内容。
# item: 输入的数据项，可以是字符串、字典等。
# is_sharegpt: 布尔值，指示是否按照 ShareGPT 格式进行提取。
def extract(item, is_sharegpt=False):
    # 如果数据项是字符串类型
    if isinstance(item, str):
        # 直接返回去除首尾空白的字符串
        return item.strip()
    # 如果数据项是字典类型
    if isinstance(item, dict):
        # 如果 is_sharegpt 为 True，表示按 ShareGPT 格式处理
        if is_sharegpt:
            # 尝试获取 'conversation' 字段
            conv = item.get('conversation')
            # 如果 'conversation' 存在且是列表类型，并且不为空
            if isinstance(conv, list) and conv:
                # 初始化一个空列表用于存储提取的文本
                texts = []
                # 遍历 'conversation' 列表中的每个消息
                for m in conv:
                    # 如果消息是字典类型
                    if isinstance(m, dict):
                        # 尝试获取 'human' 字段（用户输入）
                        v = m.get('human')
                        # 如果 'human' 字段存在且是字符串类型
                        if isinstance(v, str):
                            # 将 'human' 文本按空格分割再重新连接（规范化空白），添加到 texts 列表
                            texts.append(' '.join(v.split()))
                # 如果 texts 列表不为空
                if texts:
                    # 将所有提取的文本用空格连接起来并返回
                    return ' '.join(texts)
            # 尝试获取 'conversations' 字段
            convs = item.get('conversations')
            # 如果 'conversations' 存在且是列表类型，并且不为空
            if isinstance(convs, list) and convs:
                # 获取 'conversations' 列表的第一个元素的 'value' 字段
                v = convs[0].get('value')
                # 如果 'value' 字段存在且是字符串类型
                if isinstance(v, str):
                    # 将 'value' 文本按空格分割再重新连接（规范化空白）并返回
                    return ' '.join(v.split())
        # 如果数据项中存在 'text' 字段且是字符串类型
        if isinstance(item.get('text'), str):
            # 返回 'text' 字段去除首尾空白后的内容
            return item['text'].strip()
        # 如果数据项中存在 'human' 字段且是字符串类型
        if isinstance(item.get('human'), str):
            # 返回 'human' 字段规范化空白后的内容
            return ' '.join(item['human'].split())
    # 如果以上条件都不满足，则返回 None
    return None

# 定义一个函数 prepare_texts，用于从 JSON 文件或目录中准备文本数据。
# path_json: JSON 文件路径或包含 JSON/JSONL 文件的目录路径。
# seed: 随机种子，用于打乱文本顺序。
# is_sharegpt: 布尔值，指示是否按照 ShareGPT 格式进行文本提取。
def prepare_texts(path_json, seed=0, is_sharegpt=False):
    # 初始化一个空列表，用于存储所有提取的文本
    texts = []
    # 检查 path_json 是否是一个目录
    if os.path.isdir(path_json):
        # 初始化一个空列表，用于存储找到的文件路径
        files = []
        # 查找目录中所有 .jsonl 文件并添加到 files 列表
        files.extend(glob(os.path.join(path_json, '*.jsonl')))
        # 查找目录中所有 .json 文件并添加到 files 列表
        files.extend(glob(os.path.join(path_json, '*.json')))
        # 遍历所有找到的文件
        for fp in files:
            # 使用 try-except 块处理文件读取过程中可能发生的异常
            try:
                # 如果文件以 .jsonl 结尾（JSON Lines 格式）
                if fp.endswith('.jsonl'):
                    # 以 UTF-8 编码只读方式打开文件
                    with open(fp, 'r', encoding='utf-8') as f:
                        # 逐行读取文件内容
                        for line in f:
                            # 移除行首尾的空白字符
                            line = line.strip()
                            # 如果行是空的，则跳过
                            if not line:
                                continue
                            # 尝试将行解析为 JSON 对象
                            try:
                                obj = json.loads(line)
                                # 使用 extract 函数提取文本
                                t = extract(obj,is_sharegpt)
                                # 如果成功提取到文本
                                if t:
                                    # 将提取的文本添加到 texts 列表
                                    texts.append(t)
                            # 如果 JSON 解析失败，则将原始行作为文本添加
                            except Exception:
                                texts.append(line)
                # 如果文件以 .json 结尾（标准 JSON 格式）
                else:
                    # 以 UTF-8 编码只读方式打开文件
                    with open(fp, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # 如果 JSON 数据是列表类型
                    if isinstance(data, list):
                        # 遍历列表中的每个数据项
                        for it in data:
                            # 使用 extract 函数提取文本
                            t = extract(it,is_sharegpt)
                            # 如果成功提取到文本
                            if t:
                                texts.append(t)
                    # 如果 JSON 数据是字典类型
                    elif isinstance(data, dict):
                        # 使用 extract 函数提取文本
                        t = extract(data,is_sharegpt)
                        # 如果成功提取到文本
                        if t:
                            texts.append(t)
            # 如果文件读取或 JSON 解析过程中发生任何异常，则跳过当前文件
            except Exception:
                continue
    # 如果 path_json 不是目录，则视为单个文件
    else:
        # 尝试以标准 JSON 格式读取文件
        try:
            # 以 UTF-8 编码只读方式打开文件
            with open(path_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 如果 JSON 数据是列表类型
            if isinstance(data, list):
                # 遍历列表中的每个数据项
                for it in data:
                    # 使用 extract 函数提取文本
                    t = extract(it,is_sharegpt)
                    # 如果成功提取到文本
                    if t:
                        texts.append(t)
            # 如果 JSON 数据是字典类型
            elif isinstance(data, dict):
                # 使用 extract 函数提取文本
                t = extract(data,is_sharegpt)
                # 如果成功提取到文本
                if t:
                    texts.append(t)
        # 如果标准 JSON 解析失败，则尝试以 JSON Lines 格式读取文件
        except Exception:
            # 以 UTF-8 编码只读方式打开文件
            with open(path_json, 'r', encoding='utf-8') as f:
                # 逐行读取文件内容
                for line in f:
                    # 移除行首尾的空白字符
                    line = line.strip()
                    # 如果行是空的，则跳过
                    if not line:
                        continue
                    # 尝试将行解析为 JSON 对象
                    try:
                        obj = json.loads(line)
                        # 使用 extract 函数提取文本
                        t = extract(obj,is_sharegpt)
                        # 如果成功提取到文本
                        if t:
                            texts.append(t)
                    # 如果 JSON 解析失败，则将原始行作为文本添加
                    except Exception:
                        texts.append(line)

    # 如果最终没有提取到任何文本，则抛出 ValueError 异常
    if not texts:
        raise ValueError("No valid texts found in the input file, please check the file format and the processing function")
    # 记录日志，显示输入文本的数量
    logging.info(f'n of input {len(texts)}')
    # 设置随机种子，确保结果可复现
    random.seed(seed)
    # 随机打乱文本列表的顺序
    random.shuffle(texts)
    # 返回处理后的文本列表
    return texts