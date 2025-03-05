#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
报告生成模块，用于生成Word文档格式的报告
"""

import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import config


def create_report():
    """
    创建一个新的报告文档

    Returns:
        docx.Document: 创建的文档对象
    """
    # 创建文档对象
    doc = Document()

    # 设置文档标题
    title = doc.add_heading(config.REPORT_TITLE, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 添加文档属性
    doc.core_properties.author = config.REPORT_AUTHOR
    doc.core_properties.title = config.REPORT_TITLE

    return doc


def add_image_pair_to_report(
    doc, original_image_path, corrected_image_path, description, action
):
    """
    将一对图片及其描述和纠正措施添加到报告中

    Args:
        doc (docx.Document): 文档对象
        original_image_path (str): 原始图片路径
        corrected_image_path (str): 纠正后的图片路径
        description (str): 描述
        action (str): 纠正措施

    Returns:
        docx.Document: 更新后的文档对象
    """
    # 创建一个2x1的表格（两列一行）用于放置图片
    table = doc.add_table(rows=1, cols=2)

    # 设置表格样式
    table.style = "Table Grid"

    # 获取单元格
    cell1 = table.cell(0, 0)
    cell2 = table.cell(0, 1)

    # 在单元格中添加图片
    cell1_para = cell1.paragraphs[0]
    cell1_run = cell1_para.add_run()
    cell1_run.add_picture(original_image_path, width=Inches(3.0))

    cell2_para = cell2.paragraphs[0]
    cell2_run = cell2_para.add_run()
    cell2_run.add_picture(corrected_image_path, width=Inches(3.0))

    # 添加描述和纠正措施
    # 创建一个1x2的表格（一行两列）用于放置描述和纠正措施
    desc_table = doc.add_table(rows=1, cols=2)
    desc_table.style = "Table Grid"

    # 获取单元格
    desc_cell = desc_table.cell(0, 0)
    action_cell = desc_table.cell(0, 1)

    # 在单元格中添加文本
    desc_cell.text = f"描述: {description}"
    action_cell.text = f"纠正措施: {action}"

    # 添加空行
    doc.add_paragraph()

    return doc


def save_report(doc, output_path=None):
    """
    保存报告到指定路径

    Args:
        doc (docx.Document): 文档对象
        output_path (str, optional): 输出路径，如果为None则使用配置中的路径

    Returns:
        str: 保存的文件路径
    """
    if output_path is None:
        output_path = config.OUTPUT_REPORT

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # 保存文档
        doc.save(output_path)
        print(f"报告已保存到: {output_path}")
        return output_path

    except Exception as e:
        print(f"保存报告时出错: {e}")
        return None


def generate_report(image_pairs_with_data):
    """
    生成报告

    Args:
        image_pairs_with_data (list): 图片对及其数据的列表，每个元素是一个元组
                                     (原始图片路径, 纠正后的图片路径, 描述, 纠正措施)

    Returns:
        str: 生成的报告路径
    """
    # 创建报告
    doc = create_report()

    # 添加图片对和描述
    for original_image, corrected_image, description, action in image_pairs_with_data:
        add_image_pair_to_report(
            doc, original_image, corrected_image, description, action
        )

    # 保存报告
    return save_report(doc)
