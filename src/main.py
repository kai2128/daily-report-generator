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
import ai_processor


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
        "--capa", type=str, default=config.CAPA_CSV_FILE, help="CAPA CSV文件路径"
    )

    parser.add_argument(
        "--output", type=str, default=config.OUTPUT_DIR, help="输出文件夹路径"
    )

    parser.add_argument(
        "--use-ai",
        action="store_true",
        default=config.USE_AI,
        help="使用AI识别图片内容",
    )

    parser.add_argument(
        "--no-ai", action="store_false", dest="use_ai", help="不使用AI识别图片内容"
    )

    parser.add_argument(
        "--manual-mode",
        action="store_true",
        default=False,
        help="使用手动模式（从images/before和images/after目录获取图像对）",
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
    print(f"CAPA CSV文件: {args.capa}")
    print(f"输出文件夹: {args.output}")
    print(f"使用AI: {'是' if args.use_ai else '否'}")
    print(f"手动模式: {'是' if args.manual_mode else '否'}")
    print("=" * 50)

    # 确保输出文件夹存在
    os.makedirs(args.output, exist_ok=True)

    # 读取CAPA CSV数据
    print("正在读取CAPA CSV数据...")
    descriptions_and_actions, no_to_index = (
        data_processor.get_all_descriptions_and_actions()
    )
    if not descriptions_and_actions or descriptions_and_actions == [
        ("无描述", "无纠正措施")
    ]:
        print("无法读取CAPA CSV数据，程序退出")
        return

    # 获取图片对
    if args.manual_mode:
        print("使用手动模式获取图片对...")
        image_pairs = image_processor.get_manual_image_pairs(args.images)
        if not image_pairs:
            print("无法获取手动配对的图片对，尝试使用默认方法...")
            image_pairs = image_processor.get_image_pairs(args.images)
            if not image_pairs:
                print("无法获取图片对，程序退出")
                return
            # 转换为普通模式的图片对
            image_pairs = [(img1, img2, None) for img1, img2 in image_pairs]
    else:
        print("正在获取图片对...")
        image_pairs = image_processor.get_image_pairs(args.images)
        if not image_pairs:
            print("无法获取图片对，程序退出")
            return
        # 转换为与手动模式兼容的格式
        image_pairs = [(img1, img2, None) for img1, img2 in image_pairs]

    print(f"找到 {len(image_pairs)} 对图片")

    # 处理图片对并添加水印
    print("正在处理图片并添加水印...")
    processed_pairs = []
    for i, (before_image, after_image, capa_index) in enumerate(image_pairs):
        print(f"处理图片对 {i+1}/{len(image_pairs)}")

        # 使用AI处理图片对或根据手动模式选择描述
        if args.use_ai:
            print("使用AI识别图片内容...")
            before_img, after_img, description, action = (
                ai_processor.process_image_pair_with_ai(
                    before_image, after_image, descriptions_and_actions
                )
            )
            print(
                f"AI识别结果: 之前图片={os.path.basename(before_img)}, 之后图片={os.path.basename(after_img)}"
            )
            print(f"选择的描述: {description}")
            print(f"选择的纠正措施: {action}")
        else:
            # 不使用AI，根据capa_index选择描述和纠正措施
            if capa_index is not None:
                # 使用指定的CAPA索引（文件名中的索引是CAPA CSV中的No列）
                if capa_index in no_to_index:
                    # 如果找到对应的No，使用对应的描述
                    index = no_to_index[capa_index]
                    description, action = descriptions_and_actions[index]
                    print(f"使用CAPA No.{capa_index}的描述")
                else:
                    # 如果没有找到对应的No，使用随机描述
                    print(f"警告：未找到CAPA No.{capa_index}，使用随机描述")
                    index = i % len(descriptions_and_actions)
                    description, action = descriptions_and_actions[index]
            else:
                # 随机选择描述和纠正措施
                index = i % len(descriptions_and_actions)
                description, action = descriptions_and_actions[index]
                print(f"随机选择描述（索引 {index}）")

        # 生成随机日期时间
        random_datetime = config.generate_random_datetime()

        # 处理图片对
        processed_before, processed_after, datetime_str = (
            image_processor.process_image_pair(
                before_image, after_image, random_datetime
            )
        )

        # 如果处理失败，跳过这对图片
        if processed_before is None or processed_after is None:
            print(f"处理图片对 {i+1} 失败，跳过")
            continue

        # 添加到处理后的图片对列表
        processed_pairs.append((processed_before, processed_after, description, action))

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
