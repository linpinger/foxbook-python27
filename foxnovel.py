#! /usr/bin/python
# coding=UTF-8

import re

def getTOC(html=''):
	linkCount = {}

	toc = [] # 获取目录列表{'url':, 'name':, 'len':n }
	for link in re.finditer('<a[^>]*?href=[\"|\']([^\"\']*?)[\"|\'][^>]*?>([^<]*)<', html, re.M | re.I) :
		item = {}
		item['url'] = link.group(1)
		item['name'] = link.group(2)
		nowLinkLen = len(link.group(1))
		item['len'] = nowLinkLen
		toc.append(item)
		if linkCount.has_key(nowLinkLen) :
			linkCount[nowLinkLen] = 1 + linkCount[nowLinkLen]
		else :
			linkCount[nowLinkLen] = 1
#	print linkCount
	if 0 == len(toc) : return toc # 解析错误

	maxCount = 0 # 计算最多相同长度的链接数
	maxLen = 0
	for k in linkCount :
		if linkCount[k] > maxCount :
			maxCount = linkCount[k]
			maxLen = k
#	print 'maxCount=' + str(maxCount) + '\nmaxLen=' + str(maxLen)

	halfPos = len(toc) / 2 # 中点
	startLen = maxLen - 1 # 边界长S
	hasLess = False
	if linkCount.has_key(startLen) :
		hasLess = True
	else :
		startLen = maxLen
	endLen = maxLen + 1 # 边界长E
	hasMore = False
	if linkCount.has_key(endLen) :
		hasMore = True
	else :
		endLen = maxLen

	# 找开始: startPos
	startPos = 0 # 第一章
	bMax = True
	for cc in range(halfPos, -1, -1) :
		nowLen = toc[cc]['len']
#		print str(cc) + ' : ' + str(nowLen)
		if hasLess :
			if nowLen == maxLen :
				if bMax :
					startPos = cc
				else :
					break
			elif nowLen == startLen :
				bMax = False
				startPos = cc
			else :
				break
		else :
			if nowLen == maxLen :
				startPos = cc
			else :
				break
#	print startPos
	
	# 结束: endPos
	endPos = halfPos # 最后一章
	bMin = True
	for cc in range(halfPos, len(toc), 1) :
		nowLen = toc[cc]['len']
#		print str(cc) + ' : ' + str(nowLen)
		if hasMore :
			if nowLen == maxLen :
				if bMin :
					endPos = cc
				else :
					break
			elif nowLen == endLen :
				bMin = False
				endPos = cc
			else :
				break
		else :
			if nowLen == maxLen :
				endPos = cc
			else :
				break
#	print endPos
	
	# 删除
	for cc in range(len(toc) - 1, endPos, -1) :
#		print str(cc) + ' : ' + str(toc[cc]['len']) + ' : ' + toc[cc]['url']
		del toc[cc]
	for cc in range(startPos - 1, -1, -1) :
#		print str(cc) + ' : ' + str(toc[cc]['len']) + ' : ' + toc[cc]['url']
		del toc[cc]

	return toc

def getContent(html='') :
	# 获取body标签中间的内容
	mo = re.search('<body[^>]*?>(.*)</body>', html, re.S | re.M | re.I)
	if mo : html = mo.group(1)

	# 替换无用标签，可根据需要自行添加
	html = re.sub('<script[^>]*?>.*?</script>', '', html, 0, re.S | re.M | re.I)
	html = re.sub('<style[^>]*?>.*?</style>', '', html, 0, re.S | re.M | re.I)
	html = re.sub('<a[^>]*?>', '<a>', html, 0, re.S | re.M | re.I) # 非必须: 替换链接里的代码
	html = re.sub('<div[^>]*?>', '<div>', html, 0, re.S | re.M | re.I) # 非必须: 替换链接里的代码

	# 下面这两个是必需的
	html = re.sub('[\r\n]*', '', html, 0, re.S | re.M | re.I)
#	if '</div>' in html or '</DIV>' in html :  # 特殊的没有div的正文，一般是比较干净的页面才这样
	html = re.sub('</div>', '</div>\n', html, 0, re.S | re.M | re.I)

	# 获取最长的行
	maxLine = ''
	maxLen = 0
	for line in html.split('\n') :
		if '<br' in line or '<p' in line or '<BR' in line or '<P' in line : # 这里按需添加
			nowLen = len(line)
			if nowLen > maxLen :
				maxLen = nowLen
				maxLine = line
	html = maxLine

	# 替换内容里面的html标签
	html = html.replace('\t', '')
	html = html.replace('&nbsp;', ' ')
	html = html.replace('</p>', '\n')
	html = html.replace('</P>', '\n')
	html = html.replace('<p>', '\n')
	html = html.replace('<P>', '\n')
	html = html.replace('</br>', '\n')
	html = re.sub('<br[ /]*>', '\n', html, 0, re.I)
	html = re.sub('<a[^>]*?>.*?</a>', '\n', html, 0, re.M | re.I)

	html = re.sub('<[^>]*?>', '', html, 0, re.M | re.I) # 删除所有标签
	html = re.sub('^[ \t]*', '', html, 0, re.M | re.I)
	html = html.lstrip('\n')
	html = html.replace('\n\n', '\n')
	return html

def qidian_GetTOC_Android7(html) :
	""" URL Like: http://druid.if.qidian.com/Atom.axd/Api/Book/GetChapterList?BookId=1009281388&timeStamp=0&requestSource=0&md5Signature= """
	urlHead = ''
	xx = re.search('"BookId":([0-9]+),', html, re.I)
#	if xx : urlHead = "http://files.qidian.com/Author" + str( 1 + ( int(xx.group(1)) % 8 ) ) + "/" + xx.group(1) + "/"
	if xx : urlHead = "GetContent?BookId=" + xx.group(1) + "&ChapterId="

	toc = [] # 获取目录列表{'url':, 'name':, 'len':n }
	for link in re.finditer('"c":([0-9]+),"n":"([^"]+)".*?"v":([01]),', html, re.M | re.I) :
		item = {}
		item['url']  = urlHead + link.group(1)
		item['name'] = link.group(2)
		item['len']  = len(item['url'])
		if '0' == link.group(3) : # Public Chapters
			toc.append(item)
#			print(link.group(1) + '\t' + link.group(2) + '\t' + link.group(3))
	return toc

def qidian_GetContent_Android7(html) :
	xx = re.search('"Data":"([^"]+)"', html, re.M | re.I)
	if xx : html = xx.group(1)
	return html.replace(u'\\r\\n', '\n').replace(u"　　", "")

if '__main__' == __name__ :
	import foxOS
	html = foxOS.fileread('22.json').decode('utf-8')
	print qidian_GetContent_Android7(html)

#	for lk in getTOC(html):
#		print lk['url'] + " : " + lk['name']

