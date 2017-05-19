#! /usr/bin/python
# coding=UTF-8

import urllib2
import socket
import httplib
import re

def gethtml(url, cookie='', retry=3):
	for n in range(retry) :
		html, code = gethtml1(url, cookie)
		if '0' == code :
			break
		else :
			print(' ReDown: ' + str(n+1) + ' : ' + url + ' : ' + code)
	return html

def gethtml1(url, cookie=''):
	req = urllib2.Request(url)
#	req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)') # XP IE8
	req.add_header('User-Agent', 'xxxxxx')
	if '' != cookie :
		req.add_header('Cookie', cookie)
	fhttp = None
	html = ''
	code = '0'
	try:
		fhttp = urllib2.urlopen(req, timeout=5)
		html = fhttp.read()
	except socket.timeout :
		code = 'Socket.Timeout'
	except httplib.IncompleteRead :
		code = 'httplib.IncompleteRead'
	except urllib2.HTTPError as e :
		code = 'HTTPError: code=' + str(e.code) + ' , ' + str(e.reason)
	except urllib2.URLError as e :
		code = 'URLError: ' + str(e.reason)
	finally:
		if None != fhttp :
			fhttp.close()
	return html, code

def getCookieStr(XMLStr, tagName='biquge'):
	if '<' + tagName + '>' in XMLStr :
		return XMLStr[XMLStr.find('<' + tagName + '>') + len('<' + tagName + '>') : XMLStr.find('</' + tagName + '>')]

def cookie2Field(iCookieStr): # Wget Cookie 转为HTTP头中Cookie字段
	oList = []
	for line in iCookieStr.split('\n'):
		if '\t' in line:
			field = line.split('\t')
			oList.append(field[5] + '=' + field[6])
	return '; '.join(oList)

def detectHtmlEncoding(html, inURL='') :
	if '.xxbiquge.' in inURL : return 'utf-8'
	if '.qidian.com' in inURL : return 'utf-8'
	nowenc = 'gb18030'
	xx = re.search('<meta[^>]*charset=[" ]*([^" >]*)[" ]*', html, re.I)
	if xx :
		if xx.group(1) not in ('gbk', 'GBK', 'gb2312', 'GB2312', 'gb18030', 'GB18030') :
			nowenc = xx.group(1)
	return nowenc

def html2utf8(html='', inURL='') :
	nowenc = detectHtmlEncoding(html, inURL)
	return html.decode(nowenc).encode('UTF-8')

if '__main__' == __name__ :
	import foxOS
	bookurl = 'http://www.google.com/'
	print(gethtml(bookurl))


