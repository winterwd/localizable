#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: exportLocalizable
:date: 2024/01/11
:desc: 将 Localizable 所有语言翻译导出excel
"""

import os
import sys
import re
import xlwings as xw

# 多语言翻译文件 Excel 文件
# line1: 语言类型 = zh-Hans, en ...
EXCEL_PATH = "./result/Localizable/localizable.xlsx"
# 多语言文件(如果先运行了 localizable.py，就会生成以下路径的文件)
# /zh-Hans.lproj/Localizable.strings
TARGET_LOCALIZABLE_DIR = "./result/Localizable"

# 正则匹配 "重新添加" = "<#code#>";
PATTERN = r'"(?:\\.|[^"\\])*"'
REPLACE_TEXT = "<#code#>"
KEY_LANG = "zh-Hans"


# 单行注释
def isSignalNote(string):
    if string.startswith("//"):
        return True
    if string.startswith("#pragma"):
        return True
    return False


def get_all_lproj_path(directory):
    all_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if ".lproj" in file_path:
                all_files.append(file_path)

    return all_files


# 取出语言中对应的翻译
# needKey: 是否取出key
def parse_lproj_file(path, needKey=False):
    print(f"Processing file: {path}")
    # path: xx/zh-Hans.lproj/Localizable.strings
    # excel 第一行写入语言类型
    lproj_name = path.split("/")[-2].split(".")[0]
    datas = [lproj_name]

    f = open(path)
    for line, text in enumerate(f):
        text = text.strip()
        if not text:
            continue

        if isSignalNote(text):
            continue

        # text: "重新添加" = "<#code#>";
        # 替换文本中出现的\"转义字符 "abcd\"efg\"hij" -> "abcd&&efg&&hij"
        line_text = text.replace('\\"', "&&")
        # 找出文本中的所有 "" 的字符串
        matches = re.findall(r"\".*?\"", line_text)
        count = len(matches)
        if count > 1:
            match = matches[0 if needKey else 1]
            # 还原 && -> \\"
            match = match.replace("&&", '\\"')
            # 去除首尾的双引号
            match = match.strip('"')
            datas.append(match.replace(REPLACE_TEXT, ""))
    return datas


# 从多语言文件中取出已翻译的文本
# return: [[xx,xx],[xx,xx]..]
def parse_localizable(paths):
    all_datas = []
    for path in paths:
        if KEY_LANG in path:
            # 中文作为key
            temp = parse_lproj_file(path, needKey=True)
            if len(temp) > 1:
                temp[0] = "key"
                all_datas.insert(0, temp)

        datas = parse_lproj_file(path)
        if len(datas) > 1:
            all_datas.append(datas)
    return all_datas


# 将文本数组写入到 excel 中
# datas: [[xx,xx],[xx,xx]..]
def write_to_excel(path, data):
    try:
        # 打开 Excel 文件
        app = xw.App(visible=False, add_book=False)
        wb = app.books.add()

        # 选择第一个工作簿
        sheet = wb.sheets[0]

        # 写入数据到 Excel
        for col_idx, col_data in enumerate(data):
            col_letter = chr(ord("A") + col_idx)
            start_cell = f"{col_letter}1"
            sheet.range(start_cell).options(transpose=True).value = col_data

    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        # 保存并关闭 Excel 文件
        if "wb" in locals():
            wb.save(path)
            wb.close()
            app.quit()
            print("结果已保存: " + path)


# 创建xlsx文件
def create_xlsx(path):
    # 创建目录
    output_dir = os.path.dirname(path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("创建目录：" + output_dir)

    # 创建xlsx文件
    try:
        os.remove(path)
    except Exception as e:
        pass

    # 创建一个新的空文件
    with open(path, "w"):
        pass
    print("创建xlsx文件：" + path)


def main():
    localizable_path = TARGET_LOCALIZABLE_DIR
    if not os.path.exists(localizable_path):
        print("TARGET_LOCALIZABLE_DIR 不存在 = " + localizable_path)
        sys.exit()

    file_path = EXCEL_PATH
    paths = get_all_lproj_path(localizable_path)
    datas = parse_localizable(paths)
    create_xlsx(file_path)
    write_to_excel(file_path, datas)


if __name__ == "__main__":
    main()
