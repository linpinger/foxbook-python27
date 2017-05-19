#! /usr/bin/python
# coding=UTF-8

import foxOS
import re

def loadFML(shelfPath='FoxBook.fml'):
	txt = foxOS.fileread(shelfPath)

	bn = re.compile('<bookname>(.*?)</bookname>', re.I)
	bu = re.compile('<bookurl>(.*?)</bookurl>', re.I)
	bd = re.compile('<delurl>(.*?)</delurl>', re.S|re.I)
	bs = re.compile('<statu>(.*?)</statu>', re.I)
	bq = re.compile('<qidianBookID>(.*?)</qidianBookID>', re.I)
	ba = re.compile('<author>(.*?)</author>', re.I)
	bcs = re.compile('<chapters>(.*?)</chapters>', re.S|re.I)

	pn = re.compile('<pagename>(.*?)</pagename>', re.I)
	pu = re.compile('<pageurl>(.*?)</pageurl>', re.I)
	ps = re.compile('<size>(.*?)</size>', re.I)
	pc = re.compile('<content>(.*?)</content>', re.S|re.I)

	sc = re.compile('<novel>(.*?)</novel>', re.S|re.I)
	cc = re.compile('<page>(.*?)</page>', re.S|re.I)

	shelf = []
	for bookg in sc.finditer(txt):
		book = {}
		bookStr = bookg.group(1)
		book['bookname'] = bn.findall(bookStr)[0]
		book['bookurl']  = bu.findall(bookStr)[0]
		book['delurl']   = bd.findall(bookStr)[0]
		book['statu']    = bs.findall(bookStr)[0]
		book['author']   = ba.findall(bookStr)[0]
		book['qidianBookID'] = bq.findall(bookStr)[0]
		pages = []
		for pageg in cc.finditer(bookStr):
			page = {}
			pageStr = pageg.group(1)
			page['pagename'] = pn.findall(pageStr)[0]
			page['pageurl']  = pu.findall(pageStr)[0]
			page['size']     = ps.findall(pageStr)[0]
			page['content']  = pc.findall(pageStr)[0]
			pages.append(page)
		book['chapters'] = pages
		shelf.append(book)
	return shelf

def saveFML(shelf, savePath='FoxBook.fml'):
	fml = ['<?xml version="1.0" encoding="utf-8"?>\n\n<shelf>\n']
	for book in shelf:
		fml.append('<novel>')
		fml.append('\t<bookname>' + book['bookname'] + '</bookname>')
		fml.append('\t<bookurl>' + book['bookurl'] + '</bookurl>')
		fml.append('\t<delurl>' + book['delurl'] + '</delurl>')
		fml.append('\t<statu>' + book['statu'] + '</statu>')
		fml.append('\t<qidianBookID>' + book['qidianBookID'] + '</qidianBookID>')
		fml.append('\t<author>' + book['author'] + '</author>')
		fml.append('<chapters>')
		for page in book['chapters'] :
			fml.append('<page>')
			fml.append('\t<pagename>' + page['pagename'] + '</pagename>')
			fml.append('\t<pageurl>' + page['pageurl'] + '</pageurl>')
			fml.append('\t<content>' + page['content'] + '</content>')
			fml.append('\t<size>' + page['size'] + '</size>')
			fml.append('</page>')
		fml.append('</chapters>')
		fml.append('</novel>\n')
	fml.append('</shelf>\n')
	foxOS.filewrite('\n'.join(fml), savePath)


# main 测试
if "__main__" == __name__ :
	import time
	sTime = time.clock()
	shelf = loadFML('D:\\bin\\sqlite\\FoxBook\\FoxBook.fml.old')

	eTime1 = time.clock() - sTime
	sTime = time.clock()

	saveFML(shelf, './xxx.fml')

	eTime2 = time.clock() - sTime

	print(eTime1)
	print(eTime2)

"""
for book in shelf:
	print( book['bookurl'] + "|" + book['bookname'].decode('UTF-8').encode('GBK') )
	for page in book['chapters'] :
		print( "\t" + page['pageurl'] + "|" + page['pagename'].decode('UTF-8').encode('GBK') )
"""

