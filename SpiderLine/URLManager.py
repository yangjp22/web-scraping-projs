class URLManager(object):

	def __init__(self):
		# 建立两个集合存储爬取过和未爬取的链接，集合操作可去重
		self.oldUrls = set()
		self.newUrls = set()

	# 返回已成功爬取的链接总数
	def oldUrlSize(self):
		return len(self.oldUrls)

	# 判断是否在未爬取链接集合中还有未爬取的 url
	def newUrlEmpty(self):
		return len(self.newUrls) == 0

	# 未爬取的链接集合中取出一个链接去进行爬取，并放入已爬取的链接集合，同时返回此链接用以内容爬取
	def getNewUrl(self):
		newUrl = self.newUrls.pop()
		self.oldUrls.add(newUrl)
		return newUrl

	## 将新链接添加到未爬取的集合中(单个链接)
	def addNewUrl(self, url):
		if url is None:
			return
		if url not in self.oldUrls and url not in self.newUrls:
			self.newUrls.add(url)

	# 将新链接添加到未爬取的集合中(此为一系列的新链接)
	def addNewUrls(self, urls):
		if urls is None or len(urls) == 0:
			return
		for url in urls:
			self.addNewUrl(url)