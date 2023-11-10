#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: findLocalizable
:date: 2022/10/5
:desc: 找出项目中所有的需要国际化的字符串，暂不支持 swift
"""

import os
import re
import sys
import importlib

importlib.reload(sys)
# 查找目录下.m 文件，暂不支持 swift
DESPATH = "./"

# 正则匹配 @"Hello, world!".yg_localized @ "Bonjour".yg_localized @"Bon\"+\"jour".yg_localized
# PATTERN = r'@"([^"]*)"\.yg_localized'
PATTERN = r'@"((?:[^"\\]|\\.)*)"\.yg_localized'

# 解析结果存放的路径
WDESPATH = "./result/Localizable.strings"

# 目录黑名单，这个目录下所有的文件将被忽略
BLACKDIRLIST = [
    # DESPATH + '/Classes/Personal/PERSetting/PERAccount',  # 多级目录
    # DESPATH + '/Utils',  # Utils 下所有的文件将被忽略
    # 'xxx.m',
]

# 输出分隔符
SEPREATE = ' = <#code#>'
_result = []
wf = None

def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]


# 单行注释
def isSignalNote(string):
    if '//' in string:
        return True
    if string.startswith('#pragma'):
        return True
    return False


# log信息
def isLogMsg(string):
    if string.startswith('NSLog'):
        return True
    return False


def localizedStrings(filePath):
    f = open(filePath)
    fileName = fileNameAtPath(filePath)
    isMultiNote = False
    isHaveWriteFileName = False

    for index, line in enumerate(f):
        # 多行注释
        line = line.strip()
        if '/*' in line:
            isMultiNote = True
        if '*/' in line:
            isMultiNote = False
        if isMultiNote:
            continue

        # 单行注释
        if isSignalNote(line):
            continue

        # 打印信息
        if isLogMsg(line):
            continue

        # 定义正则表达式
        matches = re.findall(PATTERN, line)
        count = len(matches)
        if count > 0:
            if not isHaveWriteFileName:
                # 出现的具体文件
                wf.write('\n' + '// ' + fileName + '\n')
                isHaveWriteFileName = True

            # 出现的具体代码
            # wf.write('// ' + line + '\n')
            for match in matches:
                if match not in _result:
                    _result.append(match)
                    wf.write('\"' + match + '\"' + SEPREATE + ';\n')


def isInBlackList(filePath):
    if os.path.isfile(filePath):
        return fileNameAtPath(filePath) in BLACKDIRLIST
    if filePath:
        return filePath in BLACKDIRLIST
    return False


def findFromFile(path):
    paths = os.listdir(path)
    for component in paths:
        aPath = os.path.join(path, component)
        if isInBlackList(aPath):
            print('在黑名单中，被自动忽略' + aPath)
            continue

        if os.path.isdir(aPath):
            findFromFile(aPath)
        elif os.path.isfile(aPath):
            ext = os.path.splitext(aPath)[1]
            if ext == '.m':  # or ext == '.swift':
                localizedStrings(aPath)


def main():
    file_path = WDESPATH
    # 如果目录不存在，则创建目录
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print('创建目录：' + output_dir)

    global wf
    _wf = open(file_path, 'w')
    wf = _wf
    findFromFile(DESPATH)
    wf.close()
    print('已解析完成，结果已保存 : ' + file_path)


if __name__ == '__main__':
    main()