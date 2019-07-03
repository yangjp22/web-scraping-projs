import codecs

class DataOutput(object):

	def __init__(self):
		self.datas = []

	def storeData(self, data):
		if data is None:
			return

		self.datas.append(data)

	def outputHtml(self):
		fout = codecs.open('baike.html', 'a',encoding = 'utf-8')
		fout.write('<html>')
		fout.write('<head><meta charset="utf-8"/></head>')
		fout.write('<body>')
		fout.write('<table>')
		for data in self.datas:
			fout.write('<tr>')
			fout.write('<td>%s</td>'%data['url'])
			fout.write('<td>《%s》</td>'%data['title'])
			fout.write('</tr>')
			self.datas.remove(data)

		fout.write('</table>')
		fout.write('</body>')
		fout.write('</html>')

		fout.close()