#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试CAPA CSV文件读取功能
"""

import os
import sys

# 添加当前目录到系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

import config
import data_processor


def test_read_capa_csv():
    """
    测试从CAPA CSV文件读取数据
    """
    print("=" * 50)
    print("测试CAPA CSV文件读取功能")
    print("=" * 50)

    # 获取CAPA CSV文件路径
    capa_csv_path = config.CAPA_CSV_FILE
    print(f"CAPA CSV文件路径: {capa_csv_path}")

    # 检查文件是否存在
    if not os.path.exists(capa_csv_path):
        print(f"错误: CAPA CSV文件不存在: {capa_csv_path}")
        return

    # 读取CAPA CSV数据
    print("正在读取CAPA CSV数据...")
    capa_data = data_processor.read_capa_csv_data(capa_csv_path)

    if capa_data is None or len(capa_data) == 0:
        print("错误: 无法读取CAPA CSV数据或数据为空")
        return

    # 打印数据行数和前5行数据
    print(f"成功读取CAPA CSV数据，共{len(capa_data)}行")
    print("\n前5行数据:")
    for i, row in enumerate(capa_data[:5], 1):
        print(f"行 {i}: {row}")

    # 获取所有描述和纠正措施
    print("\n获取所有描述和纠正措施...")
    descriptions_and_actions = data_processor.get_all_descriptions_and_actions()

    if not descriptions_and_actions:
        print("错误: 无法获取描述和纠正措施")
        return

    # 打印前5对描述和纠正措施
    print(f"成功获取描述和纠正措施，共{len(descriptions_and_actions)}对")
    print("\n前5对描述和纠正措施:")
    for i, (desc, action) in enumerate(descriptions_and_actions[:5], 1):
        print(f"对 {i}:")
        print(f"  描述: {desc}")
        print(f"  纠正措施: {action}")

    print("=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_read_capa_csv()
