#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据处理模块，用于读取和处理CAPA CSV文件中的数据
"""

import os
import random
import pandas as pd
import config


def read_capa_csv_data(csv_path=None):
    """
    读取CAPA CSV文件中的数据

    Args:
        csv_path (str, optional): CSV文件路径，如果为None则使用配置中的路径

    Returns:
        pandas.DataFrame: 读取的数据
    """
    if csv_path is None:
        csv_path = config.CAPA_CSV_FILE

    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)

        # 检查数据是否为空
        if df.empty:
            print(f"CSV文件 {csv_path} 中没有数据")
            return None

        # 检查是否包含必要的列
        required_columns = ["No", "Before", "CAPA"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"CSV文件 {csv_path} 中缺少必要的列: {', '.join(missing_columns)}")
            return None

        return df

    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None


def get_random_description_and_action(data=None):
    """
    从CAPA CSV数据中随机选择一个描述和纠正措施

    Args:
        data (pandas.DataFrame, optional): CAPA CSV数据，如果为None则读取配置中的CSV文件

    Returns:
        tuple: (描述, 纠正措施)
    """
    if data is None:
        data = read_capa_csv_data()

    if data is None or data.empty:
        return ("无描述", "无纠正措施")

    # 随机选择一行
    random_index = random.randint(0, len(data) - 1)
    random_row = data.iloc[random_index]

    # 获取描述和纠正措施
    description = random_row["Before"]
    action = random_row["CAPA"]

    # 如果描述或纠正措施为空，则使用默认值
    if pd.isna(description):
        description = "无描述"
    if pd.isna(action):
        action = "无纠正措施"

    return (description, action)


def get_all_descriptions_and_actions(data=None):
    """
    获取CAPA CSV数据中的所有描述和纠正措施

    Args:
        data (pandas.DataFrame, optional): CAPA CSV数据，如果为None则读取配置中的CSV文件

    Returns:
        list: 描述和纠正措施的列表，每个元素是一个元组 (描述, 纠正措施)
        dict: No到索引的映射，用于通过No查找对应的描述
    """
    if data is None:
        data = read_capa_csv_data()

    if data is None or data.empty:
        return [("无描述", "无纠正措施")], {}

    # 获取描述和纠正措施的列名
    no_col = "No"
    description_col = "Before"
    action_col = "CAPA"

    # 获取所有描述和纠正措施
    result = []
    no_to_index = {}

    for i, row in data.iterrows():
        description = (
            row[description_col] if not pd.isna(row[description_col]) else "无描述"
        )
        action = row[action_col] if not pd.isna(row[action_col]) else "无纠正措施"
        result.append((description, action))

        # 记录No到索引的映射
        if no_col in row and not pd.isna(row[no_col]):
            try:
                no = int(row[no_col])
                no_to_index[no] = i
            except (ValueError, TypeError):
                # 如果No不是整数，则忽略
                pass

    return result, no_to_index
