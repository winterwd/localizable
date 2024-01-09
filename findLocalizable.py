#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: findLocalizable
:date: 2022/10/5
:desc: 找出项目中所有的需要国际化的字符串
"""

import os
import re
import sys
import importlib

importlib.reload(sys)
# 查找目录下.m 文件，暂不支持 swift
DESPATH = "./"

# 正则匹配 @"Hello, world!".yg_localized @ "Bonjour".yg_localized @"Bon\"+\"jour".yg_localized
# PATTERN = r'@"((?:[^"\\]|\\.)*)"\.yg_localized'

# 正则匹配 NSLocalizedString(@"Hello, world!", nil)
PATTERN = r'NSLocalizedString\(@"([^"]+)"(?=, nil\))'
# swift NSLocalizedString("Hello, world!", comment: "")
SWIFT_PATTERN = r'NSLocalizedString\("([^"]+)"(?=, comment: ""\))'

# 解析结果存放的路径
WDESPATH = "./result/Localizable.strings"

# 目录黑名单，这个目录下所有的文件将被忽略
BLACKDIRLIST = [
    # DESPATH + '/Classes/Personal/PERSetting/PERAccount',  # 多级目录
    # DESPATH + '/Utils',  # Utils 下所有的文件将被忽略
    DESPATH + "/smartlife/supercam/Vendor",
    DESPATH + "/Pods",
]

# 输出分隔符
SEPREATE = " = <#code#>"
_result = []


def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]


# 单行注释
def isSignalNote(string):
    if string.startswith("//"):
        return True
    elif string.startswith("#pragma"):
        return True
    return False


# log信息
def isLogMsg(string):
    if string.startswith("NSLog"):
        # OC
        return True
    elif string.startswith("print"):
        # swift
        return True
    return False


# 是否为swift文件
def isSwiftFile(filePath):
    return filePath.endswith(".swift")


# 是否为OC文件
def isOCFile(filePath):
    return filePath.endswith(".m")


def localizedStrings(filePath, wf):
    f = open(filePath)
    fileName = fileNameAtPath(filePath)
    isMultiNote = False
    isHaveWriteFileName = False

    for index, line in enumerate(f):
        line: str = line.strip()
        if line:
            # 多行注释
            if line.startswith("/*"):
                isMultiNote = True
                continue
            if line.endswith("*/"):
                isMultiNote = False
                continue
            if isMultiNote:
                continue

            # 单行注释
            if isSignalNote(line):
                continue

            # 打印信息
            if isLogMsg(line):
                continue

            # 正则表达式匹配
            matches: list
            if isOCFile(filePath):
                matches = re.findall(PATTERN, line)
            elif isSwiftFile(filePath):
                matches = re.findall(SWIFT_PATTERN, line)
            else:
                continue

            count = len(matches)
            if count > 0:
                if not isHaveWriteFileName:
                    # 出现的具体文件
                    wf.write("\n" + "// " + fileName + "\n")
                    isHaveWriteFileName = True

                # 出现的具体代码
                # wf.write('// ' + line + '\n')
                for match in matches:
                    if match not in _result:
                        _result.append(match)
                        wf.write('"' + match + '"' + SEPREATE + ";\n")
                    else:
                        # 重复的
                        # wf.write('// 重复 // "' + match + '"' + SEPREATE + ";\n")
                        print(f'{fileName} 重复: {match}')


def isInBlackList(filePath):
    if os.path.isfile(filePath):
        return fileNameAtPath(filePath) in BLACKDIRLIST
    if filePath:
        return filePath in BLACKDIRLIST
    return False


def findFromFile(path, wf):
    paths = os.listdir(path)
    for component in paths:
        aPath = os.path.join(path, component)
        if isInBlackList(aPath):
            print("在黑名单中，被自动忽略" + aPath)
            continue

        if os.path.isdir(aPath):
            findFromFile(aPath, wf)
        elif os.path.isfile(aPath):
            ext = os.path.splitext(aPath)[1]
            if ext == ".m" or ext == ".swift":
                localizedStrings(aPath, wf)


def main():
    file_path = WDESPATH
    # 如果目录不存在，则创建目录
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("创建目录：" + output_dir)

    _wf = open(file_path, "w")
    findFromFile(DESPATH, _wf)
    _wf.close()
    print("已解析完成，结果已保存 : " + file_path)


if __name__ == "__main__":
    main()
