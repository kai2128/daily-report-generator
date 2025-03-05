#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序，用于协调各个模块的工作
"""

import os
import sys
import argparse
from datetime import datetime

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import image_processor
import data_processor
import report_generator


def parse_arguments():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="生成日报表")

    parser.add_argument(
        "--images", type=str, default=config.IMAGES_DIR, help="图片文件夹路径"
    )

    parser.add_argument(
        "--excel", type=str, default=config.EXCEL_FILE, help="Excel文件路径"
    )

    parser.add_argument(
        "--output", type=str, default=config.OUTPUT_DIR, help="输出文件夹路径"
    )

    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()

    # 打印欢迎信息
    print("=" * 50)
    print("日报表生成器")
    print("=" * 50)
    print(f"图片文件夹: {args.images}")
    print(f"Excel文件: {args.excel}")
    print(f"输出文件夹: {args.output}")
    print("=" * 50)

    # 确保输出文件夹存在
    os.makedirs(args.output, exist_ok=True)

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

    # 获取图片对
    print("正在获取图片对...")
    image_pairs = image_processor.get_image_pairs(args.images)
    if not image_pairs:
        print("无法获取图片对，程序退出")
        return

    print(f"找到 {len(image_pairs)} 对图片")

    # 处理图片对并添加水印
    print("正在处理图片并添加水印...")
    processed_pairs = []
    for i, (original_image, corrected_image) in enumerate(image_pairs):
        print(f"处理图片对 {i+1}/{len(image_pairs)}")

        # 生成随机日期时间
        random_datetime = config.generate_random_datetime()

        # 处理图片对
        processed_original, processed_corrected, datetime_str = (
            image_processor.process_image_pair(
                original_image, corrected_image, random_datetime
            )
        )

        # 如果处理失败，跳过这对图片
        if processed_original is None or processed_corrected is None:
            print(f"处理图片对 {i+1} 失败，跳过")
            continue

        # 获取描述和纠正措施
        # 如果描述和纠正措施不足，则循环使用
        index = i % len(descriptions_and_actions)
        description, action = descriptions_and_actions[index]

        # 添加到处理后的图片对列表
        processed_pairs.append(
            (processed_original, processed_corrected, description, action)
        )

    # 如果没有处理成功的图片对，则退出
    if not processed_pairs:
        print("没有处理成功的图片对，程序退出")
        return

    # 生成报告
    print("正在生成报告...")
    report_path = report_generator.generate_report(processed_pairs)

    if report_path:
        print(f"报告生成成功: {report_path}")
    else:
        print("报告生成失败")


if __name__ == "__main__":
    main()
