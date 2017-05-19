# FoxBook(狐狸的小说下载阅读及转换工具) Python 2.7 命令行版

**名称:** FoxBook

**功能:** 狐狸的小说下载阅读及转换工具(更新小说站小说)

**作者:** 爱尔兰之狐(linpinger)

**邮箱:** <mailto:linpinger@gmail.com>

**主页:** <http://linpinger.github.io?s=FoxBook-Python27_MD>

**缘起:** 用别人写的工具，总感觉不能随心所欲，于是自己写个下载管理工具，基本能用，基本满意

**原理:** 下载网页，分析网页，文本保存在XML中

**亮点:** 

- 通用小说网站规则能覆盖大部分文字站的目录及正文内容分析，不需要针对每个网站的规则
- 本版本是用Python脚本语言开发的，所以可以在 win/linux/mac 下运行
- win/linux可通用，全部使用标准库
- 和之前的[AHK版][foxbook-ahk](win专用/linux下wine)，[Android版][foxbook-android]使用同一个数据库

**提示:** 本版本仅能快速更新数据库，目前不具备其他功能，制作这个版本的目的是为了方便linux下快速更新的需求，ahk版需要wine，java需要jre太庞大，所以搞出这个版本以填补空缺

**源码及下载:**

- [源码工程](https://github.com/linpinger/foxbook-python27)

- [文件下载点1:baidu][pan_baidu]

**安装及使用方法:**
- win下安装python2.7版 https://www.python.org/downloads/
- 最新linux一般内置了python, 只要chmod a+x fbFML.py 然后 ./fbFML.py 即可
- 书架的cookie文件应保存在 FoxBook.cookie文件中，格式: <cookie><sitename>cookieStr</sitename><sitename>another CookieStr</sitename></cookie>

**其他小提示:**
- 各小说站(目前只支持13xs,biquge,dajiadu,qreader)，注册账号，然后将自己的小说添加到书架，然后用IE导出cookie，填入数据库的config表中的cookie字段，site字段就是网址类似http://www.biquge.com.tw
- 可以使用多开进程更新多个数据库，速度杠杠滴


**更新日志:**
- 2017-05-19: 第一个发布版本
- ...: 懒得写了，就这样吧


[foxbook-ahk]: https://github.com/linpinger/foxbook-ahk
[foxbook-android]: https://github.com/linpinger/foxbook-android
[pan_baidu]: http://pan.baidu.com/s/1bnqxdjL "百度网盘共享"

