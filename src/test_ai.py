#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试AI图像识别功能的脚本
"""

import os
import sys
import argparse

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import ai_processor
import data_processor


def parse_arguments():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="测试AI图像识别功能")

    parser.add_argument("--image1", type=str, required=True, help="第一张图片路径")

    parser.add_argument("--image2", type=str, required=True, help="第二张图片路径")

    parser.add_argument(
        "--excel", type=str, default=config.EXCEL_FILE, help="Excel文件路径"
    )

    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()

    # 检查图片是否存在
    if not os.path.isfile(args.image1):
        print(f"错误：图片 {args.image1} 不存在")
        return

    if not os.path.isfile(args.image2):
        print(f"错误：图片 {args.image2} 不存在")
        return

    # 读取Excel数据
    print("正在读取Excel数据...")
    excel_data = data_processor.read_excel_data(args.excel)
    if excel_data is None:
        print("无法读取Excel数据，程序退出")
        return

    # 获取所有描述和纠正措施
    descriptions_and_actions = data_processor.get_all_descriptions_and_actions(
        excel_data
    )

    # 使用AI处理图片对
    print("=" * 50)
    print("使用AI识别图片内容...")
    print(f"图片1: {args.image1}")
    print(f"图片2: {args.image2}")
    print("=" * 50)

    # 分析图片对
    print("正在分析图片对...")
    before_image, after_image, content_description = ai_processor.analyze_image_pair(
        args.image1, args.image2
    )

    print(f"AI判断结果:")
    print(f"- 之前图片: {os.path.basename(before_image)}")
    print(f"- 之后图片: {os.path.basename(after_image)}")
    print(f"- 内容描述: {content_description}")
    print("=" * 50)

    # 找到最匹配的描述
    print("正在查找最匹配的描述...")
    description, action = ai_processor.find_best_description_match(
        content_description, descriptions_and_actions
    )

    print(f"最匹配的描述和纠正措施:")
    print(f"- 描述: {description}")
    print(f"- 纠正措施: {action}")
    print("=" * 50)


if __name__ == "__main__":
    main()
