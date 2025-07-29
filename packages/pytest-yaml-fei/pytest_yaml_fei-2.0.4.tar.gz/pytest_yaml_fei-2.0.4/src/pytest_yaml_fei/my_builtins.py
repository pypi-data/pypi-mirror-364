import random
import uuid
from faker import Faker
import time
from pathlib import Path
import json
import yaml
from .log import log
from typing import Any


def current_time(f: str = '%Y-%m-%d %H:%M:%S') -> str:
    """获取当前时间 2022-12-16 22:13:00"""
    return time.strftime(f)


def rand_value(target: list):
    """从返回的 list 结果随机取值"""
    if isinstance(target, list):
        return target[random.randint(0, len(target)-1)]
    else:
        return target


def rand_str(len_start=None, len_end=None) -> str:
    """生成随机字符串， 如
        ${rand_str()}  得到32位字符串
        ${rand_str(3)}  得到3位字符串
        ${rand_str(3, 10)}  得到3-10位字符串
    """
    uuid_str = str(uuid.uuid4()).replace('-', '')
    print(len(uuid_str))
    if not len_start and not len_end:
        return uuid_str
    if not len_end:
        return uuid_str[:len_start]
    else:
        return uuid_str[:random.randint(len_start, len_end)]


def to_json(obj: Any) -> str:
    """
      python 对象转 json
    """
    return json.dumps(obj, ensure_ascii=False)


# 生成随机测试数据
fake = Faker(locale="zh_CN")


def p(file_path: str, title: bool = True) -> list:
    """
        读取 json yaml text csv 文件数据参数化
    :param file_path: 文件路径
    :param title: 第一行是否有title
    :return: list
    """
    f = Path(file_path)
    res = []  # 收集数据的容器
    if not f.exists():
        from . import g
        if g.get('root_path'):
            f = g.get('root_path').joinpath(file_path)
            if not f.exists():
                log.error(f"文件路径不存在: {f.absolute()}")
                return res
        else:
            log.error(f"文件路径不存在: {f.absolute()}")
            return res
    log.info(f"读取文件路径: {f.absolute()}")
    if f.suffix == '.json':
        res = json.loads(f.read_text(encoding='utf8'))
    elif f.suffix in ['.yml', '.yaml']:
        res = yaml.safe_load(f.read_text(encoding='utf8'))
    elif f.suffix in ['.txt', '.csv']:
        with f.open(mode='r', encoding="utf-8") as fp:
            if title:
                first_list = fp.readline().rstrip('\n').split(',')
                print(first_list)
                for item in fp:
                    item_list = item.rstrip('\n').split(',')
                    # 字典推导式
                    line_dict = {key: value for key, value in zip(first_list, item_list)}
                    # append
                    res.append(line_dict)
            else:
                for item in fp:
                    item_list = item.rstrip('\n').split(',')
                    res.append(item_list)
    else:
        log.error("parameters data file only support in ['.txt', '.csv', '.yml', '.yaml', '.json']")
    return res


def P(file_path: str, title: bool = True) -> list:  # noqa
    """v1.2.5开始大写P也兼容"""
    return p(file_path, title)
