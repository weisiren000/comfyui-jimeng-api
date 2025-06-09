"""
文件操作工具函数
"""

import os
import datetime


def ensure_directory(path):
    """确保目录存在，如果不存在则创建"""
    os.makedirs(path, exist_ok=True)
    return path


def get_timestamp_string(format_str="_%Y%m%d_%H%M%S"):
    """获取时间戳字符串"""
    return datetime.datetime.now().strftime(format_str)


def get_date_folder():
    """获取日期文件夹名称"""
    return datetime.datetime.now().strftime("%Y-%m-%d")


def generate_unique_filename(directory, base_filename):
    """生成唯一文件名，避免文件覆盖"""
    if not os.path.exists(os.path.join(directory, base_filename)):
        return base_filename
    
    name_part, ext_part = os.path.splitext(base_filename)
    counter = 1
    
    while True:
        new_filename = f"{name_part}_{counter:03d}{ext_part}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1


def normalize_path(path):
    """标准化路径，转换为绝对路径"""
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path


def create_filename(prefix, file_format, add_timestamp=True, index=None):
    """创建文件名"""
    timestamp = get_timestamp_string() if add_timestamp else ""
    index_suffix = f"_{index:03d}" if index is not None else ""
    return f"{prefix}{timestamp}{index_suffix}.{file_format}"
