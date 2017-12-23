from collections import Counter
from _speller import SearchWord
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from _parser import get_terms, search, read_index, parse_files


HOST = 'localhost'
PORT = 8080
server = (HOST, PORT)

sw = SearchWord()

def make_list(s):
	return '<li>%s</li>\n' % s

def make_anc(s):
	return '<a href="/?search=%s">%s</a>\n' % (s, s)

class CozmoIgnite(BaseHTTPRequestHandler):
	def success(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_GET(self):
		if self.path == '/':
			self.success()
			with open('./home.html') as fp:
				page = fp.read()
				self.wfile.write(page.encode())

		elif self.path.startswith('/?search='):
			self.success()
			query = urlparse(self.path).query[7:]
			with open('./home.html') as fp:
				page = fp.read().split('<!--cut-->')
				self.wfile.write(page[0].encode())
				self.wfile.write(b'<ul>\n\n')
				
				# Processing query
				print(query)
				result = Counter(search(query.replace('+', ' '))).most_common()
				# test = sw.find(query)
				#if not test:
				if result:
					print(result)
					for r in result:
						self.wfile.write(make_list(r).encode())
					self.wfile.write(b'\n</ul>\n')	
				else:
					result = sw.suggested(query)
					self.wfile.write('<p>Did you mean? </p>'.encode())
					for r in result:
						self.wfile.write(make_anc(r).encode())
				self.wfile.write(page[1].encode())


def start_engine():
	try:
		print("[*] Starting server...")
		server = HTTPServer((HOST, PORT), CozmoIgnite)
		server.serve_forever()
		print("[*] Server running!")
	except KeyboardInterrupt:
		print('\b\b[*] Engine shut!')