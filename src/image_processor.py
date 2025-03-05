#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片处理模块，用于处理图片和添加水印
"""

import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageColor
import config


def add_watermark(image_path, datetime_str, output_path=None):
    """
    在图片右下角添加日期时间水印，使用透明背景和黑色轮廓文字

    Args:
        image_path (str): 图片路径
        datetime_str (str): 日期时间字符串
        output_path (str, optional): 输出路径，如果为None则覆盖原图片

    Returns:
        str: 处理后的图片路径
    """
    try:
        # 打开图片
        img = Image.open(image_path)

        # 如果图片没有透明通道，添加一个
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # 创建一个透明图层用于绘制水印
        watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)

        # 尝试加载字体，如果失败则使用默认字体
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("Arial", config.WATERMARK_FONT_SIZE)
        except IOError:
            # 如果找不到指定字体，使用默认字体
            font = ImageFont.load_default()

        # 计算文本大小 - 使用较新版本Pillow中的方法
        try:
            # 对于Pillow 9.2.0及以上版本
            text_bbox = font.getbbox(datetime_str)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            # 对于较旧版本的Pillow
            text_width, text_height = draw.textsize(datetime_str, font=font)

        # 添加内边距
        padding = config.WATERMARK_PADDING

        # 计算文本位置（右下角）
        position = (
            img.width - text_width - padding * 2,
            img.height - text_height - padding * 2,
        )

        # 绘制文字轮廓（黑色）
        outline_color = (0, 0, 0, 255)  # 黑色，完全不透明
        outline_width = 2  # 轮廓宽度

        # 绘制轮廓（通过在原始位置的四周绘制文本）
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue  # 跳过中心点，稍后绘制
                draw.text(
                    (position[0] + offset_x, position[1] + offset_y),
                    datetime_str,
                    font=font,
                    fill=outline_color,
                )

        # 绘制文本（白色）
        text_color = config.WATERMARK_FONT_COLOR
        draw.text(position, datetime_str, font=font, fill=text_color)

        # 将水印图层合并到原图
        result = Image.alpha_composite(img, watermark_layer)

        # 如果原图不支持透明度，转换回原始模式
        if Image.open(image_path).mode != "RGBA":
            result = result.convert(Image.open(image_path).mode)

        # 保存图片
        if output_path:
            result.save(output_path)
            return output_path
        else:
            result.save(image_path)
            return image_path

    except Exception as e:
        print(f"添加水印时出错: {e}")
        return None


def process_image_pair(original_image_path, corrected_image_path, datetime_obj=None):
    """
    处理一对图片（原始图片和纠正后的图片），添加相同的日期时间水印

    Args:
        original_image_path (str): 原始图片路径
        corrected_image_path (str): 纠正后的图片路径
        datetime_obj (datetime, optional): 日期时间对象，如果为None则生成随机日期时间

    Returns:
        tuple: (处理后的原始图片路径, 处理后的纠正后的图片路径, 使用的日期时间字符串)
    """
    # 如果没有提供日期时间，则生成随机日期时间
    if datetime_obj is None:
        datetime_obj = config.generate_random_datetime()

    # 格式化日期时间字符串，使用AM/PM格式
    datetime_str = datetime_obj.strftime(config.WATERMARK_DATETIME_FORMAT)

    # 创建输出目录（如果不存在）
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # 生成输出文件名
    original_filename = os.path.basename(original_image_path)
    corrected_filename = os.path.basename(corrected_image_path)

    original_output_path = os.path.join(
        config.OUTPUT_DIR, f"watermarked_{original_filename}"
    )
    corrected_output_path = os.path.join(
        config.OUTPUT_DIR, f"watermarked_{corrected_filename}"
    )

    # 添加水印
    processed_original = add_watermark(
        original_image_path, datetime_str, original_output_path
    )
    processed_corrected = add_watermark(
        corrected_image_path, datetime_str, corrected_output_path
    )

    return (processed_original, processed_corrected, datetime_str)


def get_image_pairs(image_folder):
    """
    从图片文件夹中获取图片对（原始图片和纠正后的图片）
    这里使用一个简单的策略：随机选择图片对

    Args:
        image_folder (str): 图片文件夹路径

    Returns:
        list: 图片对列表，每个元素是一个元组 (原始图片路径, 纠正后的图片路径)
    """
    # 获取文件夹中的所有图片
    image_files = [
        f
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
    ]

    # 如果图片数量不足，则返回空列表
    if len(image_files) < 2:
        print(f"图片文件夹中的图片数量不足: {len(image_files)}")
        return []

    # 随机打乱图片列表
    random.shuffle(image_files)

    # 创建图片对
    image_pairs = []
    for i in range(0, len(image_files) - 1, 2):
        original_image = os.path.join(image_folder, image_files[i])
        corrected_image = os.path.join(image_folder, image_files[i + 1])
        image_pairs.append((original_image, corrected_image))

    return image_pairs
