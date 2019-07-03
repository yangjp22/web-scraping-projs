import requests

class HTMLDownload(object):

	def download(self, url, method = 'get'):
		if url is None:
			return

		sess = requests.Session()
		sess.headers['User-Agent'] = 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 63.0.3239.132Safari / 537.36'

		if method == 'get':
			response = sess.get(url)
		else:
			response = sess.post(url)

		if response.status_code == 200:
			response.encoding = response.apparent_encoding
			return response.text
		else:
			return

