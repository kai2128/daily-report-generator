#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序，用于协调各个模块的工作
"""

import os
import sys
import argparse
from datetime import datetime
import random
import glob

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import image_processor
import data_processor
import report_generator
import ai_processor


def parse_args():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="日报生成器")

    # 路径参数
    parser.add_argument("--output", help="输出文件夹路径", default=config.OUTPUT_DIR)
    parser.add_argument(
        "--images",
        "--images-dir",
        dest="images_dir",
        help="图片文件夹路径",
        default=config.IMAGES_DIR,
    )
    parser.add_argument("--capa", help="CAPA CSV文件路径", default=config.CAPA_CSV_FILE)
    parser.add_argument(
        "--input", help="输入CSV文件路径", default=config.INPUT_CSV_FILE
    )
    parser.add_argument(
        "--template",
        help="报告模板文件路径",
        default=os.path.join(config.BASE_DIR, "template", "report-template.docx"),
    )

    # 水印参数
    parser.add_argument("--watermark", help="水印文本", default=None)
    parser.add_argument("--no-watermark", action="store_true", help="不添加水印")

    # AI参数
    parser.add_argument("--ai", action="store_true", help="使用AI识别图片内容")
    parser.add_argument("--no-ai", action="store_true", help="不使用AI识别图片内容")

    # 模式参数
    parser.add_argument(
        "--manual-mode",
        action="store_true",
        help="使用手动模式（从images/before和images/after目录获取图像对）",
    )
    parser.add_argument(
        "--use-capa", action="store_true", help="使用CAPA CSV文件中的描述和纠正措施"
    )
    parser.add_argument(
        "--use-input",
        action="store_true",
        help="使用input CSV文件中的编号、位置和日期信息",
    )
    parser.add_argument(
        "--no-input", action="store_true", help="不使用input CSV文件中的数据"
    )
    parser.add_argument(
        "--use-template", action="store_true", help="使用模板文件生成报告"
    )

    # 位置参数
    parser.add_argument("--location", help="设置所有图像对的位置信息", default="")
    parser.add_argument(
        "--locations-file",
        help="包含位置信息的文件路径，每行一个位置，与图像对一一对应",
        default=None,
    )

    return parser.parse_args()


def process_images(args):
    """
    处理图像并生成报告

    Args:
        args (argparse.Namespace): 命令行参数

    Returns:
        str: 生成的报告路径
    """
    # 读取CAPA CSV数据
    descriptions_and_actions, no_to_index = (
        data_processor.get_all_descriptions_and_actions()
    )

    # 读取input CSV数据（如果启用）
    input_data = None
    no_to_location_date = {}
    use_input_csv = (
        (hasattr(args, "use_input") and args.use_input)
        or (not hasattr(args, "no_input") or not args.no_input)
        and config.USE_INPUT_CSV
    )

    if use_input_csv:
        input_data, no_to_location_date = data_processor.read_input_csv_data(
            args.input if hasattr(args, "input") else None
        )
        print(f"从input CSV文件读取了 {len(no_to_location_date)} 条记录")
        # 打印读取到的位置和日期信息，方便调试
        for no, (location, date_obj) in no_to_location_date.items():
            date_str = date_obj.strftime("%Y-%m-%d") if date_obj else "无日期"
            print(f"编号 {no}: 位置 '{location}', 日期 {date_str}")

    # 处理图像
    image_pairs_with_data = []
    locations = []  # 存储位置信息

    # 处理位置信息
    default_location = args.location if hasattr(args, "location") else ""
    locations_from_file = []

    # 如果提供了位置文件，读取位置信息
    if hasattr(args, "locations_file") and args.locations_file:
        try:
            with open(args.locations_file, "r", encoding="utf-8") as f:
                locations_from_file = [line.strip() for line in f.readlines()]
            print(
                f"从文件 {args.locations_file} 读取了 {len(locations_from_file)} 个位置信息"
            )
        except Exception as e:
            print(f"读取位置文件时出错: {e}")
            locations_from_file = []

    if args.manual_mode:
        # 修改调用方式，传入input_data
        image_pairs = image_processor.get_manual_image_pairs(args.images_dir, input_data)
        
        if image_pairs is None:
            print("无法获取手动配对的图像对，程序退出")
            return None

        # 移除之前的排序逻辑，直接处理image_pairs
        for i, (before_image, after_image, capa_index, pairing_id) in enumerate(image_pairs):
            # 获取位置和日期信息（如果有）
            location = default_location
            datetime_obj = None

            # 首先尝试使用pairing_id作为键
            if use_input_csv and pairing_id in no_to_location_date:
                location_from_input, date_from_input = no_to_location_date[pairing_id]
                if location_from_input:
                    location = location_from_input
                    print(f"图像对 {pairing_id} 使用input CSV中的位置: {location}")
                if date_from_input:
                    datetime_obj = date_from_input
                    print(
                        f"图像对 {pairing_id} 使用input CSV中的日期: {date_from_input.strftime('%Y-%m-%d')}"
                    )
            # 如果pairing_id不存在，但capa_index存在，则尝试使用capa_index
            elif (
                use_input_csv
                and capa_index is not None
                and capa_index in no_to_location_date
            ):
                location_from_input, date_from_input = no_to_location_date[capa_index]
                if location_from_input:
                    location = location_from_input
                    print(
                        f"图像对 {pairing_id} (CAPA索引 {capa_index}) 使用input CSV中的位置: {location}"
                    )
                if date_from_input:
                    datetime_obj = date_from_input
                    print(
                        f"图像对 {pairing_id} (CAPA索引 {capa_index}) 使用input CSV中的日期: {date_from_input.strftime('%Y-%m-%d')}"
                    )

            # 处理图像对，添加水印
            processed_before, processed_after, datetime_str = (
                image_processor.process_image_pair(
                    before_image, after_image, datetime_obj
                )
            )

            if processed_before is None or processed_after is None:
                print(f"处理图像对 {i+1} 失败，跳过")
                continue

            # 根据CAPA索引选择描述和纠正措施
            if capa_index is not None and args.use_capa:
                print(f"\n处理图像对 {pairing_id}:")
                print(f"尝试使用CAPA索引 {capa_index} 匹配CAPA条目...")
                
                # 打印CAPA映射表内容用于调试
                if config.DEBUG_MODE:
                    print("当前CAPA映射表 (No -> 索引):")
                    for no, idx in no_to_index.items():
                        print(f"  No {no} -> 索引 {idx}")

                if capa_index in no_to_index:
                    idx = no_to_index[capa_index]
                    print(f"找到匹配的CAPA条目: No {capa_index} 对应索引 {idx}")
                    
                    if idx < len(descriptions_and_actions):
                        description, action = descriptions_and_actions[idx]
                        print(f"成功获取描述和措施:")
                        print(f"描述: {description}")
                        print(f"纠正措施: {action}")
                    else:
                        print(f"警告：索引 {idx} 超出范围（总条目数 {len(descriptions_and_actions)}）")
                        description, action = random.choice(descriptions_and_actions)
                else:
                    available_nos = sorted(no_to_index.keys())
                    print(f"错误：CAPA索引 {capa_index} 不存在！可用No列表: {available_nos}")
                    print(f"将使用随机选择的描述和措施")
                    description, action = random.choice(descriptions_and_actions)
                
                print("-" * 50)
            else:
                # 随机选择描述和纠正措施
                description, action = random.choice(descriptions_and_actions)

            # 添加到结果列表
            image_pairs_with_data.append(
                (processed_before, processed_after, description, action)
            )

            # 添加位置信息
            locations.append(location)

    else:
        # 自动模式：使用AI识别图像内容
        if args.ai:
            # 获取所有图像文件
            image_files = []
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                image_files.extend(glob.glob(os.path.join(args.images_dir, ext)))

            # 确保有偶数个图像
            if len(image_files) % 2 != 0:
                image_files = image_files[:-1]

            # 按照修改时间排序
            image_files.sort(key=os.path.getmtime)

            # 两两配对处理
            for i in range(0, len(image_files), 2):
                if i + 1 < len(image_files):
                    image1 = image_files[i]
                    image2 = image_files[i + 1]

                    # 使用AI分析图像对
                    before_image, after_image, best_description = (
                        ai_processor.analyze_image_pair(image1, image2)
                    )

                    if before_image is None or after_image is None:
                        print(f"分析图像对 {image1} 和 {image2} 失败，跳过")
                        continue

                    # 处理图像对，添加水印
                    processed_before, processed_after, datetime_str = (
                        image_processor.process_image_pair(before_image, after_image)
                    )

                    if processed_before is None or processed_after is None:
                        print(f"处理图像对 {before_image} 和 {after_image} 失败，跳过")
                        continue

                    # 查找最匹配的描述和纠正措施
                    description, action = ai_processor.find_best_description_match(
                        best_description, descriptions_and_actions
                    )

                    # 添加到结果列表
                    image_pairs_with_data.append(
                        (processed_before, processed_after, description, action)
                    )

                    # 添加位置信息
                    location_index = len(image_pairs_with_data) - 1
                    if location_index < len(locations_from_file):
                        locations.append(locations_from_file[location_index])
                    else:
                        locations.append(default_location)
        else:
            # 不使用AI，随机配对图像
            # 获取所有图像文件
            image_files = []
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                image_files.extend(glob.glob(os.path.join(args.images_dir, ext)))

            # 确保有偶数个图像
            if len(image_files) % 2 != 0:
                image_files = image_files[:-1]

            # 随机打乱图像顺序
            random.shuffle(image_files)

            # 两两配对处理
            for i in range(0, len(image_files), 2):
                if i + 1 < len(image_files):
                    image1 = image_files[i]
                    image2 = image_files[i + 1]

                    # 处理图像对，添加水印
                    processed_image1, processed_image2, datetime_str = (
                        image_processor.process_image_pair(image1, image2)
                    )

                    if processed_image1 is None or processed_image2 is None:
                        print(f"处理图像对 {image1} 和 {image2} 失败，跳过")
                        continue

                    # 随机选择描述和纠正措施
                    description, action = random.choice(descriptions_and_actions)

                    # 添加到结果列表
                    image_pairs_with_data.append(
                        (processed_image1, processed_image2, description, action)
                    )

                    # 添加位置信息
                    location_index = len(image_pairs_with_data) - 1
                    if location_index < len(locations_from_file):
                        locations.append(locations_from_file[location_index])
                    else:
                        locations.append(default_location)

    # 生成报告
    if image_pairs_with_data:
        # 如果使用模板，则调用模板报告生成函数
        if hasattr(args, "use_template") and args.use_template:
            template_path = args.template if hasattr(args, "template") else None
            return report_generator.generate_report_from_template(
                image_pairs_with_data, locations, template_path
            )
        else:
            return report_generator.generate_report(image_pairs_with_data, locations)
    else:
        print("没有可用的图像对，无法生成报告")
        return None


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()

    # 打印欢迎信息
    print("=" * 50)
    print("日报表生成器")
    print("=" * 50)
    print(f"图片文件夹: {args.images_dir}")
    print(f"CAPA CSV文件: {args.capa}")
    if hasattr(args, "input"):
        print(f"输入CSV文件: {args.input}")
    print(f"输出文件夹: {args.output}")
    if hasattr(args, "template") and args.template:
        print(f"报告模板文件: {args.template}")
    print(f"使用AI: {'是' if args.ai else '否'}")
    print(f"手动模式: {'是' if args.manual_mode else '否'}")
    print(
        f"使用input CSV: {'是' if hasattr(args, 'use_input') and args.use_input else '否'}"
    )
    print(
        f"使用模板: {'是' if hasattr(args, 'use_template') and args.use_template else '否'}"
    )
    if hasattr(args, "location") and args.location:
        print(f"位置信息: {args.location}")
    if hasattr(args, "locations_file") and args.locations_file:
        print(f"位置信息文件: {args.locations_file}")
    print("=" * 50)

    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)

    # 处理图像并生成报告
    report_path = process_images(args)

    if report_path:
        print(f"报告已生成: {report_path}")
    else:
        print("报告生成失败")


if __name__ == "__main__":
    main()
