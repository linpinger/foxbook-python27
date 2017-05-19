#! /usr/bin/python
# coding=UTF-8

import os

def fileread(filepath): # 读文件到变量
	f = open(filepath, 'rb')
	try:
		text = f.read()
	finally:
		f.close()
	return text

def filewrite(content, filepath): # 写变量到文件
	f = open(filepath, 'wb')
	try:
		text = f.write(content)
	finally:
		f.close()

def renameIfExist(filePath) :
	if os.path.exists(filePath + ".old") :
		os.remove(filePath + ".old")
	os.rename(filePath, filePath + ".old")

