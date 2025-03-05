#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试AI图像识别功能
"""

import os
import sys
import argparse

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import data_processor
import ai_processor
import image_processor


def parse_arguments():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="测试AI图像识别功能")

    parser.add_argument("--image1", type=str, help="第一张图片路径")

    parser.add_argument("--image2", type=str, help="第二张图片路径")

    parser.add_argument(
        "--capa", type=str, default=config.CAPA_CSV_FILE, help="CAPA CSV文件路径"
    )

    parser.add_argument(
        "--manual-mode",
        action="store_true",
        default=False,
        help="使用手动模式（从images/before和images/after目录获取图像对）",
    )

    parser.add_argument(
        "--images",
        type=str,
        default=config.IMAGES_DIR,
        help="图片文件夹路径（用于手动模式）",
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
    print("测试AI图像识别功能")
    print("=" * 50)

    # 读取CAPA CSV数据
    print("正在读取CAPA CSV数据...")
    descriptions_and_actions, no_to_index = (
        data_processor.get_all_descriptions_and_actions()
    )
    if not descriptions_and_actions or descriptions_and_actions == [
        ("无描述", "无纠正措施")
    ]:
        print("无法读取CAPA CSV数据，使用默认描述")
        descriptions_and_actions = [("无描述", "无纠正措施")]
        no_to_index = {}

    # 获取图片对
    if args.manual_mode:
        print(f"使用手动模式获取图片对，图片目录: {args.images}")
        image_pairs = image_processor.get_manual_image_pairs(args.images)
        if not image_pairs:
            print("无法获取手动配对的图片对，程序退出")
            return

        # 处理每一对图片
        for i, (before_image, after_image, capa_index) in enumerate(image_pairs):
            print(f"\n处理图片对 {i+1}/{len(image_pairs)}")
            print(f"之前图片: {os.path.basename(before_image)}")
            print(f"之后图片: {os.path.basename(after_image)}")

            # 使用AI处理图片对
            print("使用AI识别图片内容...")
            before_img, after_img, description, action = (
                ai_processor.process_image_pair_with_ai(
                    before_image, after_image, descriptions_and_actions
                )
            )

            # 打印结果
            print("=" * 30)
            print("AI识别结果:")
            print(f"之前图片: {os.path.basename(before_img)}")
            print(f"之后图片: {os.path.basename(after_img)}")
            print(f"描述: {description}")
            print(f"纠正措施: {action}")

            # 如果有CAPA索引，打印对应的描述
            if capa_index is not None:
                if capa_index in no_to_index:
                    # 如果找到对应的No，使用对应的描述
                    index = no_to_index[capa_index]
                    manual_desc, manual_action = descriptions_and_actions[index]
                    print(f"\n手动指定的描述 (CAPA No.{capa_index}):")
                    print(f"描述: {manual_desc}")
                    print(f"纠正措施: {manual_action}")
                else:
                    print(f"\n警告：未找到CAPA No.{capa_index}的描述")
            print("=" * 30)
    else:
        # 单对图片模式
        if not args.image1 or not args.image2:
            print("错误: 在非手动模式下，必须指定--image1和--image2参数")
            return

        print(f"第一张图片: {args.image1}")
        print(f"第二张图片: {args.image2}")
        print(f"CAPA CSV文件: {args.capa}")
        print("=" * 50)

        # 检查图片文件是否存在
        if not os.path.exists(args.image1):
            print(f"图片文件不存在: {args.image1}")
            return

        if not os.path.exists(args.image2):
            print(f"图片文件不存在: {args.image2}")
            return

        # 使用AI处理图片对
        print("使用AI识别图片内容...")
        before_image, after_image, description, action = (
            ai_processor.process_image_pair_with_ai(
                args.image1, args.image2, descriptions_and_actions
            )
        )

        # 打印结果
        print("=" * 50)
        print("AI识别结果:")
        print(f"之前图片: {os.path.basename(before_image)}")
        print(f"之后图片: {os.path.basename(after_image)}")
        print(f"描述: {description}")
        print(f"纠正措施: {action}")
        print("=" * 50)


if __name__ == "__main__":
    main()
