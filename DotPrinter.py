#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: DotPrinter
:date: 2022/10/5
:desc: 
"""
import time
import threading

class DotPrinter:
    def __init__(self):
        self.i = 1
        self.thread = None
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.print_dots)
        self.thread.start()

    def stop(self):
        # 在控制台中打印点号字符串
        print('\n')
        self.running = False
        if self.thread is not None:
            self.thread.join()

    def print_dots(self):
        while self.running:
            # 将点号字符串连接为一个字符串
            dots = '.' * self.i

            # 在控制台中打印点号字符串
            print('\r' + dots, end='', flush=True)

            self.i += 1
            time.sleep(0.5)
