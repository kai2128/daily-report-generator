#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
报告生成模块，用于生成Word文档格式的报告
"""

import os
import copy
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
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


def set_cell_background(cell, color):
    """
    设置单元格背景颜色

    Args:
        cell: 单元格对象
        color: RGB颜色元组，例如(255, 255, 0)表示黄色
    """
    shading_elm = OxmlElement("w:shd")
    shading_elm.set(qn("w:fill"), f"{color[0]:02x}{color[1]:02x}{color[2]:02x}")
    cell._tc.get_or_add_tcPr().append(shading_elm)


def add_image_pair_to_report(
    doc, original_image_path, corrected_image_path, description, action, location=""
):
    """
    将一对图片及其描述和纠正措施添加到报告中，格式与示例一致

    Args:
        doc (docx.Document): 文档对象
        original_image_path (str): 原始图片路径
        corrected_image_path (str): 纠正后的图片路径
        description (str): 描述
        action (str): 纠正措施
        location (str, optional): 位置信息，默认为空

    Returns:
        docx.Document: 更新后的文档对象
    """
    # 创建一个1行1列的表格作为主表格
    main_table = doc.add_table(rows=5, cols=1)
    main_table.style = "Table Grid"

    # 设置第一行为"Observation"标题行，并设置黄色背景
    header_cell = main_table.cell(0, 0)
    header_cell.text = "Observation"
    header_para = header_cell.paragraphs[0]
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.runs[0]
    header_run.bold = True
    header_run.font.size = Pt(14)
    # 设置黄色背景
    set_cell_background(header_cell, (255, 255, 0))  # 黄色

    # 设置第二行为位置信息
    location_cell = main_table.cell(1, 0)
    location_cell.text = f"Location: {location}"
    location_para = location_cell.paragraphs[0]
    location_run = location_para.runs[0]
    location_run.bold = True

    # 第三行为图片表格
    images_cell = main_table.cell(2, 0)
    # 在单元格中创建一个嵌套表格用于放置图片
    images_table = images_cell.add_table(rows=2, cols=2)

    # 设置"Before"和"After"标题
    before_cell = images_table.cell(0, 0)
    before_cell.text = "Before"
    before_para = before_cell.paragraphs[0]
    before_run = before_para.runs[0]
    before_run.bold = True
    before_run.font.size = Pt(12)

    after_cell = images_table.cell(0, 1)
    after_cell.text = "After"
    after_para = after_cell.paragraphs[0]
    after_run = after_para.runs[0]
    after_run.bold = True
    after_run.font.size = Pt(12)

    # 添加图片
    before_img_cell = images_table.cell(1, 0)
    before_img_para = before_img_cell.paragraphs[0]
    before_img_run = before_img_para.add_run()
    before_img_run.add_picture(original_image_path, width=Inches(3.0))

    after_img_cell = images_table.cell(1, 1)
    after_img_para = after_img_cell.paragraphs[0]
    after_img_run = after_img_para.add_run()
    after_img_run.add_picture(corrected_image_path, width=Inches(3.0))

    # 第四行为描述和纠正措施表格
    desc_cell = main_table.cell(3, 0)
    # 在单元格中创建一个嵌套表格用于放置描述和纠正措施
    desc_table = desc_cell.add_table(rows=2, cols=2)

    # 设置"Description"和"Corrective Action"标题
    desc_header_cell = desc_table.cell(0, 0)
    desc_header_cell.text = "Description"
    desc_header_para = desc_header_cell.paragraphs[0]
    desc_header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    desc_header_run = desc_header_para.runs[0]
    desc_header_run.bold = True

    action_header_cell = desc_table.cell(0, 1)
    action_header_cell.text = "Corrective Action"
    action_header_para = action_header_cell.paragraphs[0]
    action_header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    action_header_run = action_header_para.runs[0]
    action_header_run.bold = True

    # 添加描述和纠正措施内容
    desc_content_cell = desc_table.cell(1, 0)
    desc_content_cell.text = description
    desc_content_para = desc_content_cell.paragraphs[0]
    desc_content_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    action_content_cell = desc_table.cell(1, 1)
    action_content_cell.text = action
    action_content_para = action_content_cell.paragraphs[0]
    action_content_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 第五行为空行，用于分隔不同的观察项
    main_table.cell(4, 0).text = ""

    return doc


def add_image_pair_to_template_page(
    doc,
    page_index,
    original_image_path,
    corrected_image_path,
    description,
    action,
    location="",
):
    """
    将一对图片及其描述和纠正措施添加到模板页面中

    Args:
        doc (docx.Document): 文档对象
        page_index (int): 页面索引
        original_image_path (str): 原始图片路径
        corrected_image_path (str): 纠正后的图片路径
        description (str): 描述
        action (str): 纠正措施
        location (str, optional): 位置信息，默认为空

    Returns:
        docx.Document: 更新后的文档对象
    """
    # 查找表格
    tables = doc.tables
    if page_index >= len(tables):
        print(
            f"警告：页面索引 {page_index} 超出范围，当前文档只有 {len(tables)} 个表格"
        )
        return doc

    # 获取当前页面的表格
    table = tables[page_index]

    # 设置位置信息
    # 假设位置信息在第二行
    location_cell = None
    for row in table.rows:
        for cell in row.cells:
            if cell.text.startswith("Location:"):
                location_cell = cell
                break
        if location_cell:
            break

    if location_cell:
        location_cell.text = f"Location: {location}"
        for paragraph in location_cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
    else:
        print("警告：未找到位置信息单元格")

    # 查找Before和After图片单元格
    before_img_cell = None
    after_img_cell = None
    for row in table.rows:
        for cell in row.cells:
            if "Before" in cell.text:
                # 假设图片单元格在"Before"标题下方
                before_img_cell = table.cell(
                    row._tr.index(row._tr) + 1, cell._tc.index(cell._tc)
                )
            elif "After" in cell.text:
                # 假设图片单元格在"After"标题下方
                after_img_cell = table.cell(
                    row._tr.index(row._tr) + 1, cell._tc.index(cell._tc)
                )

    # 添加图片
    if before_img_cell:
        before_img_cell.text = ""  # 清除单元格内容
        before_img_para = before_img_cell.paragraphs[0]
        before_img_run = before_img_para.add_run()
        before_img_run.add_picture(original_image_path, width=Inches(3.0))
    else:
        print("警告：未找到Before图片单元格")

    if after_img_cell:
        after_img_cell.text = ""  # 清除单元格内容
        after_img_para = after_img_cell.paragraphs[0]
        after_img_run = after_img_para.add_run()
        after_img_run.add_picture(corrected_image_path, width=Inches(3.0))
    else:
        print("警告：未找到After图片单元格")

    # 查找Description和Corrective Action单元格
    desc_cell = None
    action_cell = None
    for row in table.rows:
        for cell in row.cells:
            if "Description" in cell.text:
                # 假设内容单元格在标题下方
                desc_cell = table.cell(
                    row._tr.index(row._tr) + 1, cell._tc.index(cell._tc)
                )
            elif "Corrective Action" in cell.text:
                # 假设内容单元格在标题下方
                action_cell = table.cell(
                    row._tr.index(row._tr) + 1, cell._tc.index(cell._tc)
                )

    # 添加描述和纠正措施内容
    if desc_cell:
        desc_cell.text = description
        for paragraph in desc_cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        print("警告：未找到Description单元格")

    if action_cell:
        action_cell.text = action
        for paragraph in action_cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        print("警告：未找到Corrective Action单元格")

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


def generate_report(image_pairs_with_data, locations=None):
    """
    生成报告

    Args:
        image_pairs_with_data (list): 图片对及其数据的列表，每个元素是一个元组
                                     (原始图片路径, 纠正后的图片路径, 描述, 纠正措施)
        locations (list, optional): 位置信息列表，与image_pairs_with_data一一对应，默认为None

    Returns:
        str: 生成的报告路径
    """
    # 创建报告
    doc = create_report()

    # 添加图片对和描述
    for i, (original_image, corrected_image, description, action) in enumerate(
        image_pairs_with_data
    ):
        # 获取位置信息，如果没有提供则使用空字符串
        location = ""
        if locations and i < len(locations):
            location = locations[i]

        add_image_pair_to_report(
            doc, original_image, corrected_image, description, action, location
        )

    # 保存报告
    return save_report(doc)


def generate_report_from_template(
    image_pairs_with_data, locations=None, template_path=None
):
    """
    使用模板生成报告，为每个图像对复制模板页面

    Args:
        image_pairs_with_data (list): 图片对及其数据的列表，每个元素是一个元组
                                     (原始图片路径, 纠正后的图片路径, 描述, 纠正措施)
        locations (list, optional): 位置信息列表，与image_pairs_with_data一一对应，默认为None
        template_path (str, optional): 模板文件路径，如果为None则使用默认模板

    Returns:
        str: 生成的报告路径
    """
    # 如果没有指定模板路径，则使用默认模板
    if template_path is None:
        template_path = os.path.join(
            config.BASE_DIR, "template", "report-template.docx"
        )

    # 检查模板文件是否存在
    if not os.path.exists(template_path):
        print(f"错误：模板文件 {template_path} 不存在")
        return None

    try:
        # 使用python-docx和lxml处理Word文档
        import shutil
        import copy
        import tempfile
        from docx import Document
        from docx.shared import Inches
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        # 创建输出文件路径
        output_path = config.OUTPUT_REPORT

        # 打开模板文件
        template_doc = Document(template_path)

        # 创建一个新文档
        new_doc = Document()

        # 确定第二页的表格（假设第二个表格是第二页的表格）
        if len(template_doc.tables) < 2:
            print("警告：模板文档中表格数量不足，至少需要2个表格")
            if len(template_doc.tables) == 0:
                print("错误：模板文档中没有表格")
                return None
            template_table = template_doc.tables[0]
        else:
            template_table = template_doc.tables[1]  # 使用第二个表格作为模板

        print(
            f"使用第二个表格作为模板，行数：{len(template_table.rows)}，列数：{len(template_table.columns)}"
        )

        # 复制模板文档的前两页内容到新文档
        # 我们假设第一个表格在第一页，第二个表格在第二页

        # 复制所有段落和表格，直到第二个表格
        table_count = 0
        for element in template_doc.element.body:
            # 如果是表格，增加计数
            if element.tag.endswith("tbl"):
                table_count += 1
                # 复制表格
                new_doc.element.body.append(copy.deepcopy(element))
                # 如果已经复制了两个表格，就停止
                if table_count >= 2:
                    break
            else:
                # 复制其他元素（段落等）
                new_doc.element.body.append(copy.deepcopy(element))

        # 处理第一个图像对（替换第二页的内容）
        if len(image_pairs_with_data) > 0 and len(new_doc.tables) >= 2:
            original_image, corrected_image, description, action = (
                image_pairs_with_data[0]
            )

            # 获取位置信息
            location = ""
            if locations and 0 < len(locations):
                location = locations[0]

            # 获取第二个表格
            observation_table = new_doc.tables[1]

            # 替换表格中的内容
            for row in observation_table.rows:
                for cell in row.cells:
                    # 替换占位符
                    if "<LOCATION>" in cell.text:
                        cell.text = cell.text.replace("<LOCATION>", location)
                    elif "<DESCRIPTION_BEFORE>" in cell.text:
                        cell.text = cell.text.replace(
                            "<DESCRIPTION_BEFORE>", description
                        )
                    elif "<DESCRIPTION_AFTER>" in cell.text:
                        cell.text = cell.text.replace("<DESCRIPTION_AFTER>", action)
                    elif "<IMAGE_BEFORE>" in cell.text:
                        cell.text = ""  # 清除占位符
                        paragraph = cell.paragraphs[0]
                        run = paragraph.add_run()
                        run.add_picture(original_image, width=Inches(3.0))
                    elif "<IMAGE_AFTER>" in cell.text:
                        cell.text = ""  # 清除占位符
                        paragraph = cell.paragraphs[0]
                        run = paragraph.add_run()
                        run.add_picture(corrected_image, width=Inches(3.0))

            # 如果没有找到占位符，尝试使用标题匹配
            for row_idx, row in enumerate(observation_table.rows):
                for col_idx, cell in enumerate(row.cells):
                    if "Location:" in cell.text:
                        cell.text = f"Location: {location}"
                    elif "Before" in cell.text and row_idx + 1 < len(
                        observation_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置图片
                        img_cell = observation_table.cell(row_idx + 1, col_idx)
                        if not img_cell.text or img_cell.text.isspace():
                            img_cell.text = ""  # 清除单元格内容
                            paragraph = img_cell.paragraphs[0]
                            run = paragraph.add_run()
                            run.add_picture(original_image, width=Inches(3.0))
                    elif "After" in cell.text and row_idx + 1 < len(
                        observation_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置图片
                        img_cell = observation_table.cell(row_idx + 1, col_idx)
                        if not img_cell.text or img_cell.text.isspace():
                            img_cell.text = ""  # 清除单元格内容
                            paragraph = img_cell.paragraphs[0]
                            run = paragraph.add_run()
                            run.add_picture(corrected_image, width=Inches(3.0))
                    elif cell.text.strip() == "Description" and row_idx + 1 < len(
                        observation_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置描述
                        desc_cell = observation_table.cell(row_idx + 1, col_idx)
                        if not desc_cell.text or desc_cell.text.isspace():
                            desc_cell.text = description
                    elif cell.text.strip() == "Corrective Action" and row_idx + 1 < len(
                        observation_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置纠正措施
                        action_cell = observation_table.cell(row_idx + 1, col_idx)
                        if not action_cell.text or action_cell.text.isspace():
                            action_cell.text = action

        # 为每个额外的图像对创建新页面
        for i in range(1, len(image_pairs_with_data)):
            original_image, corrected_image, description, action = (
                image_pairs_with_data[i]
            )

            # 获取位置信息
            location = ""
            if locations and i < len(locations):
                location = locations[i]

            # 添加分页符
            new_doc.add_page_break()

            # 复制模板表格
            new_table = new_doc.add_table(
                rows=len(template_table.rows), cols=len(template_table.columns)
            )
            new_table.style = template_table.style

            # 复制表格内容和格式
            for row_idx, row in enumerate(template_table.rows):
                for col_idx, cell in enumerate(row.cells):
                    # 获取新表格中的对应单元格
                    new_cell = new_table.cell(row_idx, col_idx)

                    # 复制单元格文本（除了需要替换的内容）
                    if "<LOCATION>" in cell.text:
                        new_cell.text = cell.text.replace("<LOCATION>", location)
                    elif "<DESCRIPTION_BEFORE>" in cell.text:
                        new_cell.text = cell.text.replace(
                            "<DESCRIPTION_BEFORE>", description
                        )
                    elif "<DESCRIPTION_AFTER>" in cell.text:
                        new_cell.text = cell.text.replace("<DESCRIPTION_AFTER>", action)
                    elif "<IMAGE_BEFORE>" in cell.text or "<IMAGE_AFTER>" in cell.text:
                        new_cell.text = ""  # 图片单元格先清空
                    else:
                        new_cell.text = cell.text

                    # 复制单元格格式
                    if hasattr(cell, "_element") and hasattr(new_cell, "_element"):
                        # 复制单元格属性
                        if cell._element.tcPr is not None:
                            if new_cell._element.tcPr is None:
                                new_cell._element.tcPr = OxmlElement("w:tcPr")

                            # 复制背景色
                            if cell._element.tcPr.xpath("./w:shd"):
                                for shd in cell._element.tcPr.xpath("./w:shd"):
                                    new_cell._element.tcPr.append(copy.deepcopy(shd))

                            # 复制边框
                            if cell._element.tcPr.xpath("./w:tcBorders"):
                                for border in cell._element.tcPr.xpath("./w:tcBorders"):
                                    new_cell._element.tcPr.append(copy.deepcopy(border))

            # 添加图片和内容
            for row_idx, row in enumerate(new_table.rows):
                for col_idx, cell in enumerate(row.cells):
                    # 处理Location单元格
                    if "Location:" in cell.text:
                        cell.text = f"Location: {location}"

                    # 处理Before标题单元格
                    elif "Before" in cell.text and row_idx + 1 < len(new_table.rows):
                        # 获取下一行同列的单元格用于放置图片
                        img_cell = new_table.cell(row_idx + 1, col_idx)
                        img_cell.text = ""  # 清除单元格内容
                        paragraph = img_cell.paragraphs[0]
                        run = paragraph.add_run()
                        run.add_picture(original_image, width=Inches(3.0))

                    # 处理After标题单元格
                    elif "After" in cell.text and row_idx + 1 < len(new_table.rows):
                        # 获取下一行同列的单元格用于放置图片
                        img_cell = new_table.cell(row_idx + 1, col_idx)
                        img_cell.text = ""  # 清除单元格内容
                        paragraph = img_cell.paragraphs[0]
                        run = paragraph.add_run()
                        run.add_picture(corrected_image, width=Inches(3.0))

                    # 处理Description标题单元格
                    elif cell.text.strip() == "Description" and row_idx + 1 < len(
                        new_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置描述
                        desc_cell = new_table.cell(row_idx + 1, col_idx)
                        desc_cell.text = description

                    # 处理Corrective Action标题单元格
                    elif cell.text.strip() == "Corrective Action" and row_idx + 1 < len(
                        new_table.rows
                    ):
                        # 获取下一行同列的单元格用于放置纠正措施
                        action_cell = new_table.cell(row_idx + 1, col_idx)
                        action_cell.text = action

        # 复制模板文档的剩余内容（如果有的话）
        # 从第三个表格开始复制
        table_count = 0
        for element in template_doc.element.body:
            if element.tag.endswith("tbl"):
                table_count += 1
                if table_count > 2:  # 跳过前两个表格
                    new_doc.element.body.append(copy.deepcopy(element))
            elif table_count >= 2:  # 只复制第二个表格之后的非表格元素
                new_doc.element.body.append(copy.deepcopy(element))

        # 保存文档
        new_doc.save(output_path)
        print(f"报告已保存到: {output_path}")
        return output_path

    except Exception as e:
        print(f"生成报告时出错: {e}")
        import traceback

        traceback.print_exc()
        return None
