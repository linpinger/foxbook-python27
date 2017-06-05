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


def getAllNeedUpIDX() : # ��ȡ������Ҫ����TOC��bookIDX�б�����shelf
	retList = []
	idx = 0
	for book in shelf:
		if '0' == book['statu'] :
			retList.append(idx)
		idx = 1 + idx
	return retList

def getNewFromRemoteBookCase(cookieXML) : # ���� shelf
	remoteList = []

	firstBookURL = shelf[0]['bookurl']
	if '.biquge.' in firstBookURL :
		html = foxhttp.gethtml("http://www.biquge.com.tw/modules/article/bookcase.php", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'biquge')))
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"([^\"]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) } )
	elif '.dajiadu.' in firstBookURL :
		html = foxhttp.gethtml("http://www.dajiadu.net/modules/article/bookcase.php", foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'dajiadu')))
		# ͬ dajiadu
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
		# ͬ dajiadu
		for it in re.finditer('<tr>.*?<a [^>]*?>([^<]*)<.*?<a href=\"[^\"]*cid=([0-9]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1).decode('gb18030').encode('utf-8'), 'newpageurl': it.group(2) + ".html" } )
	elif '.xxbiquge.' in firstBookURL :
		xxbiqugeCookie = foxhttp.cookie2Field(foxhttp.getCookieStr(cookieXML, 'xxbiquge'))
		html = foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php", xxbiqugeCookie)
		html = html + foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php?page=2", xxbiqugeCookie)
		html = html + foxhttp.gethtml("http://www.xxbiquge.com/bookcase.php?page=3", xxbiqugeCookie)
		for it in re.finditer('\"s2\"><a [^>]*?>([^<]*)<.*?\"s4\"><a href=\"([^\"]*)\"', html, re.S | re.M | re.I) : # bname,newurl
			remoteList.append({'bookname': it.group(1), 'newpageurl': it.group(2) } )
	else : # ��֧�ֵ���ܣ�����
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

	bStartCompare = False # �ҵ���һ����
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
		for idx in self.idxList : # ����Ŀ¼ҳ���õ����½ڲ�д��shelf
			# �Ƚϵõ����½�
			nowBookURL = shelf[idx]['bookurl']
			nowBookDelList = shelf[idx]['delurl']
			for page in shelf[idx]['chapters']:
				nowBookDelList = nowBookDelList + page['pageurl'] + '|' + page['pagename'] + '\n'
			if bDebug : print('  ' + self.getName() + ' down: ' + nowBookURL)
			html = foxhttp.gethtml(nowBookURL, '', RETRY)
#			nowEnc = foxhttp.detectHtmlEncoding(html, nowBookURL)
			html = foxhttp.html2utf8(html, nowBookURL) # �����������⣬תutf-8�������⣬������

			if 'druid.if.qidian.com/Atom.axd/Api/Book/GetChapterList' in nowBookURL :
				nowtoc = foxnovel.qidian_GetTOC_Android7(html)
			else :
				nowtoc = foxnovel.getTOC(html)
			newList = compareToGetNewPages(nowtoc, nowBookDelList)
			newCount = len(newList)
			if newCount > 0 : # �����½�
				for np in newList :
					# nowpagename = np['name'].decode(nowEnc).encode('utf-8') # ת��ôһȦҲ�۰�
					page = {'pagename': np['name'], 'pageurl': np['url'], 'size': '0', 'content': ''}
					shelf[idx]['chapters'].append(page)

					threadLock.acquire()
					newPagesList.append({'bookIDX': idx, 'bookurl': nowBookURL, 'pageIDX': len(shelf[idx]['chapters']) - 1, 'pageurl': np['url'] }) # ���߳�׷�ӵ��б���
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
			# ����ҳ��
			html = foxhttp.gethtml(pageFullURL, '', RETRY)
			# д��ṹ
			if '.qidian.com/' in pageFullURL :
				text = foxnovel.qidian_GetContent_Android7(html.decode('utf-8'))
			else :
				nowEnc = foxhttp.detectHtmlEncoding(html, pageFullURL)
				text = foxnovel.getContent(html).decode(nowEnc).encode('utf-8')

			nowLen = len(text)
			nowLen = ( nowLen - nowLen % 3 ) / 3  # ����utf8������3���ֽ�

			page['content'] = text
			page['size'] = str(nowLen)

def getItemCountPerThread(itemCount, threadCount=3) :
	n = 0 # ÿ���߳� task��
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
	# Ĭ��ֵ
	bDebug = False  # �Ƿ����
	bDownAllTOC = False # �Ƿ���������TOC
	bUpdateShortPages = False # �Ƿ���¶���
	THREAD = 3 # �߳���
	RETRY  = 3 # �������Դ���

	# fml �����ļ���
	wDir  = 'D:/bin/sqlite/FoxBook/'
	wDir2 = 'D:/bin/sqlite/more_FML/'
	if not os.path.exists(wDir) :
		wDir  = 'C:/bin/sqlite/FoxBook/'
		wDir2 = 'C:/bin/sqlite/more_FML/'
	if 'linux' in sys.platform :
		wDir = './'
		wDir2 = './'
	shelfPath = wDir + 'FoxBook.fml'
	cookiePath = wDir + 'FoxBook.cookie' # ������

	# ��������
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hadsT:t:', ['help', 'all', 'debug', 'short', 'thread=', 'times='])
	except getopt.GetoptError:
		usage()
		sys.exit()
	if len(args) > 0 : # fmlPath
		fpath = args[0]
		if os.path.isabs(fpath) : # ����·��
			if os.path.exists(fpath) : shelfPath = fpath
		else : # �ļ���
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
	if 0 == len(shelf) : sys.exit() # ������˳�

	# ��ȡҪ���µ�IDX�б�: needUpdateIdxList
	if bDownAllTOC :
		needUpdateIdxList = getAllNeedUpIDX()
	else :
		needUpdateIdxList = getNewFromRemoteBookCase(cookieXML) # �Ƚ���ܣ��õ��и��µ�IDX�б�
		if None == needUpdateIdxList : # ��֧�ֵ����
			needUpdateIdxList = getAllNeedUpIDX()

	newPagesList = [] # ���߳�׷�ӵ�
	threadLock = threading.Lock()

	# ׷�Ӷ��½ڽ�newPagesList
	if bUpdateShortPages :
		nowBIDX = 0
		for book in shelf :
			nowBookURL = book['bookurl']
			nowPIDX = 0
			for page in book['chapters'] :
				if len(page['content']) < 3000 : # utf8����3���ַ�����
					newPagesList.append({'bookIDX': nowBIDX, 'bookurl': nowBookURL, 'pageIDX': nowPIDX, 'pageurl': page['pageurl'] }) # ���߳�׷�ӵ��б���
				nowPIDX = 1 + nowPIDX
			nowBIDX = 1 + nowBIDX

	# ����TOC, ��ȡ���½��б�newPagesList
	idxCount = len(needUpdateIdxList)
	if idxCount >= THREAD : # ������������߳����������߳�
		if bDebug : print('  Down IDX Use ' + str(THREAD) + ' threads, URL Count: ' + str(idxCount))
		itemCountPerThread = getItemCountPerThread(idxCount, THREAD) # ÿ���߳�idx��

		threadList = []
		nowIdxList = []
		count = 0
		for idx in needUpdateIdxList :
			count = 1 + count
			nowIdxList.append(idx)
			if count == itemCountPerThread : # ����
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
	else :  # ����˳�����
		if bDebug : print('  Down IDX One by One, URL Count: ' + str(idxCount))
		nowThread = updateBooksTOC(needUpdateIdxList)
		nowThread.start()
		nowThread.join()

	# ����newPagesList�������½�
	newPageCount = len(newPagesList)
	if newPageCount >= THREAD : # ������������߳����������߳�
		if bDebug : print('  Down Pages Use ' + str(THREAD) + ' threads, URL Count: ' + str(newPageCount))
		itemCountPerThread = getItemCountPerThread(newPageCount, THREAD) # ÿ���߳�task��

		threadList = []
		nowTaskList = []
		count = 0
		for tsk in newPagesList :
			count = 1 + count
			nowTaskList.append(tsk)
			if count == itemCountPerThread : # ����
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
	elif newPageCount > 0 :  # ����˳�����
		if bDebug : print('  Down Pages One by One, URL Count: ' + str(newPageCount))
		nowThread = updatePages(newPagesList)
		nowThread.start()
		nowThread.join()

	# �����½ھͱ���fml
	if newPageCount > 0 :
		shelf.sort(key=lambda obj:len(obj.get('chapters')), reverse=True) # ����so easy
		foxOS.renameIfExist(shelfPath)
		fmlStor.saveFML(shelf, shelfPath)

	print('\n# Main End : ' + str(int(time.time() - sTime)) + 's : ' + shelfPath + '\n')
#	os.system('pause')


