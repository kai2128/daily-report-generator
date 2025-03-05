#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试水印功能的脚本
"""

import os
import sys
import argparse
from datetime import datetime

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import image_processor


def parse_arguments():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="测试水印功能")

    parser.add_argument("--image", type=str, required=True, help="要添加水印的图片路径")

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出图片路径，如果不指定则在原图片名前添加watermarked_前缀",
    )

    parser.add_argument(
        "--datetime",
        type=str,
        default=None,
        help="要添加的日期时间，格式为YYYY-MM-DD HH:MM AM/PM，如果不指定则使用当前时间",
    )

    parser.add_argument(
        "--font-size",
        type=int,
        default=config.WATERMARK_FONT_SIZE,
        help=f"水印字体大小，默认为{config.WATERMARK_FONT_SIZE}",
    )

    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()

    # 检查图片是否存在
    if not os.path.isfile(args.image):
        print(f"错误：图片 {args.image} 不存在")
        return

    # 设置输出路径
    if args.output is None:
        # 在原图片名前添加watermarked_前缀
        image_dir = os.path.dirname(args.image)
        image_filename = os.path.basename(args.image)
        args.output = os.path.join(image_dir, f"watermarked_{image_filename}")

    # 设置日期时间
    if args.datetime is None:
        # 使用当前时间，使用AM/PM格式
        datetime_str = datetime.now().strftime(config.WATERMARK_DATETIME_FORMAT)
    else:
        # 使用指定的日期时间
        datetime_str = args.datetime

    # 临时修改字体大小（如果指定）
    original_font_size = config.WATERMARK_FONT_SIZE
    if args.font_size != config.WATERMARK_FONT_SIZE:
        config.WATERMARK_FONT_SIZE = args.font_size

    # 添加水印
    print(f"正在为图片 {args.image} 添加水印...")
    print(f"水印日期时间: {datetime_str}")
    print(f"水印字体大小: {config.WATERMARK_FONT_SIZE}")
    print(f"输出路径: {args.output}")

    result = image_processor.add_watermark(args.image, datetime_str, args.output)

    # 恢复原始字体大小
    config.WATERMARK_FONT_SIZE = original_font_size

    if result:
        print(f"水印添加成功: {result}")
    else:
        print("水印添加失败")


if __name__ == "__main__":
    main()
