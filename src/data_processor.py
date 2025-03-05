#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel数据处理模块，用于读取和处理Excel文件中的数据
"""

import os
import random
import pandas as pd
import config


def read_excel_data(excel_path=None):
    """
    读取Excel文件中的数据

    Args:
        excel_path (str, optional): Excel文件路径，如果为None则使用配置中的路径

    Returns:
        pandas.DataFrame: 读取的数据
    """
    if excel_path is None:
        excel_path = config.EXCEL_FILE

    try:
        # 读取Excel文件
        df = pd.read_excel(excel_path)

        # 检查数据是否为空
        if df.empty:
            print(f"Excel文件 {excel_path} 中没有数据")
            return None

        return df

    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


def get_random_description_and_action(data=None):
    """
    从Excel数据中随机选择一个描述和纠正措施

    Args:
        data (pandas.DataFrame, optional): Excel数据，如果为None则读取配置中的Excel文件

    Returns:
        tuple: (描述, 纠正措施)
    """
    if data is None:
        data = read_excel_data()

    if data is None or data.empty:
        return ("无描述", "无纠正措施")

    # 获取描述和纠正措施的列名
    # 假设Excel文件的第一列是描述，第二列是纠正措施
    # 如果列名不同，可以根据实际情况修改
    description_col = data.columns[0]
    action_col = data.columns[1]

    # 随机选择一行
    random_index = random.randint(0, len(data) - 1)
    random_row = data.iloc[random_index]

    # 获取描述和纠正措施
    description = random_row[description_col]
    action = random_row[action_col]

    # 如果描述或纠正措施为空，则使用默认值
    if pd.isna(description):
        description = "无描述"
    if pd.isna(action):
        action = "无纠正措施"

    return (description, action)


def get_all_descriptions_and_actions(data=None):
    """
    获取Excel数据中的所有描述和纠正措施

    Args:
        data (pandas.DataFrame, optional): Excel数据，如果为None则读取配置中的Excel文件

    Returns:
        list: 描述和纠正措施的列表，每个元素是一个元组 (描述, 纠正措施)
    """
    if data is None:
        data = read_excel_data()

    if data is None or data.empty:
        return [("无描述", "无纠正措施")]

    # 获取描述和纠正措施的列名
    description_col = data.columns[0]
    action_col = data.columns[1]

    # 获取所有描述和纠正措施
    result = []
    for _, row in data.iterrows():
        description = (
            row[description_col] if not pd.isna(row[description_col]) else "无描述"
        )
        action = row[action_col] if not pd.isna(row[action_col]) else "无纠正措施"
        result.append((description, action))

    return result
