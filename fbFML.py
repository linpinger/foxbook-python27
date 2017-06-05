#! /usr/bin/python
# coding=UTF-8
# -*- coding: utf-8 -*-

import foxOS
import fmlStor
import foxhttp
import foxnovel

import threading
import os
import re
from urlparse import urljoin
import getopt

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def getAllNeedUpIDX() : # 获取所有需要更新TOC的bookIDX列表，依赖shelf
	retList = []
	idx = 0
	for book in shelf:
		if '0' == book['statu'] :
			retList.append(idx)
		idx = 1 + idx
	return retList

def getNewFromRemoteBookCase(cookieXML) : # 依赖 shelf
	remoteList = []

	firstBookURL = shelf[0]['bookurl']
	if '.biquge.' in firstBookURL :
		html = foxhttp.gethtml("http://www.biquge.com.tw/modules/article/bookcase.php", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'biquge')))
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"([^\"]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) } )
	elif '.dajiadu.' in firstBookURL :
		html = foxhttp.gethtml("http://www.dajiadu.net/modules/article/bookcase.php", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'dajiadu')))
		# 同 dajiadu
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"[^\"]*cid=([0-9]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) + ".html" } )
	elif '.piaotian.' in firstBookURL :
		html = foxhttp.gethtml("http://www.piaotian.com/modules/article/bookcase.php", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'piaotian')))
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"[^\"]*cid=([0-9]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) + ".html" } )
	elif '.13xxs.' in firstBookURL :
		html = foxhttp.gethtml("http://www.13xxs.com/modules/article/bookcase.php?classid=0", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, '13xxs')))
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"[^\"]*?/([0-9]*.html)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) } )
	elif '.xqqxs.' in firstBookURL :
		html = foxhttp.gethtml("http://www.xqqxs.com/modules/article/bookcase.php?delid=604", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'xqqxs')))
		# 同 dajiadu
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"[^\"]*cid=([0-9]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) + ".html" } )
	elif '.xxbiquge.' in firstBookURL :
		xxbiqugeCookie = foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'xxbiquge'))
		html = foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php", xxbiqugeCookie)
		html = html + foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php?page=2", xxbiqugeCookie)
		html = html + foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php?page=3", xxbiqugeCookie)
		for it in re.finditer('\"s2\"><a [^>]*?>([^<]*)<.*?\"s4\"><a href=\"([^\"]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1), 'newpageurl': it.group(2) } )
	else : # 非支持的书架，返回
		return None

	idx = 0
	retList = []
	for book in shelf :
		isInBookCase = False
		for ri in remoteList :
			if ri['bookname'] == book['bookname'] :
				isInBookCase = True
				nowBookDelList = book['delurl']
				for page in book['chapters']:
					nowBookDelList = nowBookDelList + page['pageurl'] + '|' + page['pagename'] + '\n'
				if ri['newpageurl'] + '|' in nowBookDelList :
					continue
				else :
					retList.append(idx)
					if bDebug : print( " + new: " + book['bookname'].decode('utf8') + " have new page" )
				break
		if not isInBookCase : retList.append(idx)
		idx = 1 + idx
	return retList

def compareToGetNewPages(toc, nowBookDelList) :
	xx = re.search('([^\r\n\|]+)|.*', nowBookDelList, re.U)
	if xx :
		firstURL = xx.group(1)
	else :
		print('foxsaid: parse DelURL error')

	bStartCompare = False # 找到第一行了
	newPages = []
	for lk in toc :
		if bStartCompare :
			if lk['url'] + '|' not in nowBookDelList :
				newPages.append(lk)
		else :
			if firstURL == lk['url'] :
				bStartCompare = True
	return newPages

class updateBooksTOC(threading.Thread):
	def __init__(self, idxList):
		threading.Thread.__init__(self)
		self.idxList = idxList
	def run(self):
		for idx in self.idxList : # 下载目录页，得到新章节并写入shelf
			# 比较得到新章节
			nowBookURL = shelf[idx]['bookurl']
			nowBookDelList = shelf[idx]['delurl']
			for page in shelf[idx]['chapters']:
				nowBookDelList = nowBookDelList + page['pageurl'] + '|' + page['pagename'] + '\n'
			if bDebug : print('  ' + self.getName() + ' down: ' + nowBookURL)
			html = foxhttp.gethtml(nowBookURL, '', RETRY)
#			nowEnc = foxhttp.detectHtmlEncoding(html, nowBookURL)
			html = foxhttp.html2utf8(html, nowBookURL) # 当下载有问题，转utf-8就有问题，都是泪

			if 'druid.if.qidian.com/Atom.axd/Api/Book/GetChapterList' in nowBookURL :
				nowtoc = foxnovel.qidian_GetTOC_Android7(html)
			else :
				nowtoc = foxnovel.getTOC(html)
			newList = compareToGetNewPages(nowtoc, nowBookDelList)
			newCount = len(newList)
			if newCount > 0 : # 有新章节
				for np in newList :
					# nowpagename = np['name'].decode(nowEnc).encode('utf-8') # 转这么一圈也累啊
					page = {'pagename': np['name'], 'pageurl': np['url'], 'size': '0', 'content': ''}
					shelf[idx]['chapters'].append(page)

					threadLock.acquire()
					newPagesList.append({'bookIDX': idx, 'bookurl': nowBookURL, 'pageIDX': len(shelf[idx]['chapters']) - 1, 'pageurl': np['url'] }) # 各线程追加到列表中
					threadLock.release()
				print( "+ " +  self.getName() + " : TOC : " + str(newCount) + " newPages : " + nowBookURL )

class updatePages(threading.Thread):
	def __init__(self, taskList):
		threading.Thread.__init__(self)
		self.taskList = taskList # {'bookIDX', 'bookurl', 'pageIDX', 'pageurl'}
	def run(self):
		for pt in self.taskList :
			bIDX = pt['bookIDX']
			pIDX = pt['pageIDX']
			pageFullURL = urljoin(pt['bookurl'], pt['pageurl'])
			page = shelf[bIDX]['chapters'][pIDX]
			print( "# " + self.getName() + " : " + shelf[bIDX]['bookname'].decode('utf8') + ' : ' + page['pagename'].decode('utf8') )
			# 下载页面
			html = foxhttp.gethtml(pageFullURL, '', RETRY)
			# 写入结构
			if '.qidian.com/' in pageFullURL :
				text = foxnovel.qidian_GetContent_Android7(html.decode('utf-8'))
			else :
				nowEnc = foxhttp.detectHtmlEncoding(html, pageFullURL)
				text = foxnovel.getContent(html).decode(nowEnc).encode('utf-8')

			nowLen = len(text)
			nowLen = ( nowLen - nowLen % 3 ) / 3  # 中文utf8编码算3个字节

			page['content'] = text
			page['size'] = str(nowLen)

def getItemCountPerThread(itemCount, threadCount=3) :
	n = 0 # 每个线程 task数
	if itemCount % threadCount == 0 :
		n = itemCount / threadCount
	else :
		n = ( itemCount - ( itemCount % threadCount ) ) / threadCount + 1
	return n

def usage() :
	print('Usage: ' + sys.argv[0] + ' [Option]... fmlPath\n')
	print('Switch:')
	print('  -h,  --help        Print This Help.')
	print('  -a,  --all         Download All TOC, Not Only New in BookCase.')
	print('  -d,  --debug       Print Debug Info.')
	print('  -s,  --short       Download Pages which Len(Content) < 999.')
	print('')
	print('Arg:')
	print('  -T,  --thread=     Set Download Thread, Default is 3.')
	print('  -t,  --times=      Download Retry Times, Default is 3.')

if "__main__" == __name__ :
	# 默认值
	bDebug = False  # 是否调试
	bDownAllTOC = False # 是否下载所有TOC
	bUpdateShortPages = False # 是否更新短章
	THREAD = 3 # 线程数
	RETRY  = 3 # 下载重试次数

	# fml 所在文件夹
	wDir  = 'D:/bin/sqlite/FoxBook/'
	wDir2 = 'D:/bin/sqlite/more_FML/'
	if not os.path.exists(wDir) :
		wDir  = 'C:/bin/sqlite/FoxBook/'
		wDir2 = 'C:/bin/sqlite/more_FML/'
	if 'linux' in sys.platform :
		wDir = './'
		wDir2 = './'
	shelfPath = wDir + 'FoxBook.fml'
	cookiePath = wDir + 'FoxBook.cookie' # 待处理

	# 解析参数
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hadsT:t:', ['help', 'all', 'debug', 'short', 'thread=', 'times='])
	except getopt.GetoptError:
		usage()
		sys.exit()
	if len(args) > 0 : # fmlPath
		fpath = args[0]
		if os.path.isabs(fpath) : # 绝对路径
			if os.path.exists(fpath) : shelfPath = fpath
		else : # 文件名
			if 'fb' == fpath : fpath = 'FoxBook.fml'
			if 'dj' == fpath : fpath = 'dajiadu.fml'
			if 'pt' == fpath : fpath = 'piaotian.fml'
			if '13' == fpath : fpath = '13xxs.fml'
			if 'xq' == fpath : fpath = 'xqqxs.fml'
			if 'xx' == fpath : fpath = 'xqqxs.fml'
			if os.path.exists(wDir2 + fpath) : shelfPath = wDir2 + fpath
			if os.path.exists(wDir + fpath) : shelfPath = wDir + fpath
			if os.path.exists(os.getcwd() + os.path.sep + fpath) : shelfPath = os.getcwd() + os.path.sep + fpath
	else :
		print('NowDir: ' + os.getcwd())
		print('You Now Use:  FoxBook.fml or -h for help or below:\n  fb = FoxBook.fml\t  dj = dajiadu.fml\t  pt = piaotian.fml\n  13 = 13xxs.fml\t  xq = xqqxs.fml\t  xx = xxbiquge.fml\n')
	for oo, aa in opts :
		if oo in ('-h', '--help') :
			usage()
			sys.exit()
		elif oo in ('-s', '--short') :
			bUpdateShortPages = True
		elif oo in ('-a', '--all') :
			bDownAllTOC = True
		elif oo in ('-d', '--debug') :
			bDebug = True
		elif oo in ('-T', '--thread') :
			THREAD = int(aa)
		elif oo in ('-t', '--times') :
			RETRY = int(aa)

	import time
	sTime = time.time()

	print('\n# Main Start: ' + shelfPath + '\n')
	if os.path.exists(shelfPath) : shelf = fmlStor.loadFML(shelfPath) # fml -> obj
	if os.path.exists(cookiePath) : cookieXML = foxOS.fileread(cookiePath)
	if 0 == len(shelf) : sys.exit() # 空书架退出

	# 获取要更新的IDX列表: needUpdateIdxList
	if bDownAllTOC :
		needUpdateIdxList = getAllNeedUpIDX()
	else :
		needUpdateIdxList = getNewFromRemoteBookCase(cookieXML) # 比较书架，得到有更新的IDX列表
		if None == needUpdateIdxList : # 非支持的书架
			needUpdateIdxList = getAllNeedUpIDX()

	newPagesList = [] # 供线程追加的
	threadLock = threading.Lock()

	# 追加短章节进newPagesList
	if bUpdateShortPages :
		nowBIDX = 0
		for book in shelf :
			nowBookURL = book['bookurl']
			nowPIDX = 0
			for page in book['chapters'] :
				if len(page['content']) < 3000 : # utf8中文3个字符长度
					newPagesList.append({'bookIDX': nowBIDX, 'bookurl': nowBookURL, 'pageIDX': nowPIDX, 'pageurl': page['pageurl'] }) # 各线程追加到列表中
				nowPIDX = 1 + nowPIDX
			nowBIDX = 1 + nowBIDX

	# 更新TOC, 获取新章节列表newPagesList
	idxCount = len(needUpdateIdxList)
	if idxCount >= THREAD : # 如果数量大于线程数，就用线程
		if bDebug : print('  Down IDX Use ' + str(THREAD) + ' threads, URL Count: ' + str(idxCount))
		itemCountPerThread = getItemCountPerThread(idxCount, THREAD) # 每个线程idx数

		threadList = []
		nowIdxList = []
		count = 0
		for idx in needUpdateIdxList :
			count = 1 + count
			nowIdxList.append(idx)
			if count == itemCountPerThread : # 够数
				count = 0
				nowThread = updateBooksTOC(nowIdxList)
				nowThread.start()
				threadList.append(nowThread)
				nowIdxList = []
		if idxCount % THREAD > 0 :
			nowThread = updateBooksTOC(nowIdxList)
			nowThread.start()
			threadList.append(nowThread)
		for nowThread in threadList :
			nowThread.join()
	else :  # 否则顺序更新
		if bDebug : print('  Down IDX One by One, URL Count: ' + str(idxCount))
		nowThread = updateBooksTOC(needUpdateIdxList)
		nowThread.start()
		nowThread.join()

	# 依据newPagesList更新新章节
	newPageCount = len(newPagesList)
	if newPageCount >= THREAD : # 如果数量大于线程数，就用线程
		if bDebug : print('  Down Pages Use ' + str(THREAD) + ' threads, URL Count: ' + str(newPageCount))
		itemCountPerThread = getItemCountPerThread(newPageCount, THREAD) # 每个线程task数

		threadList = []
		nowTaskList = []
		count = 0
		for tsk in newPagesList :
			count = 1 + count
			nowTaskList.append(tsk)
			if count == itemCountPerThread : # 够数
				count = 0
				nowThread = updatePages(nowTaskList)
				nowThread.start()
				threadList.append(nowThread)
				nowTaskList = []
		if newPageCount % THREAD > 0 :
			nowThread = updatePages(nowTaskList)
			nowThread.start()
			threadList.append(nowThread)
		for nowThread in threadList :
			nowThread.join()
	elif newPageCount > 0 :  # 否则顺序更新
		if bDebug : print('  Down Pages One by One, URL Count: ' + str(newPageCount))
		nowThread = updatePages(newPagesList)
		nowThread.start()
		nowThread.join()

	# 有新章节就保存fml
	if newPageCount > 0 :
		shelf.sort(key=lambda obj:len(obj.get('chapters')), reverse=True) # 排序so easy
		foxOS.renameIfExist(shelfPath)
		fmlStor.saveFML(shelf, shelfPath)

	print('\n# Main End : ' + str(int(time.time() - sTime)) + 's : ' + shelfPath + '\n')
#	os.system('pause')


