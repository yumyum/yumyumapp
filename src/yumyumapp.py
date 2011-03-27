from google.appengine.api import urlfetch


from xml.etree import ElementTree

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import os
from google.appengine.ext.webapp import template

class Greeting(db.Model):
	author = db.UserProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, None))

class GetRSS(webapp.RequestHandler):
	def post(self):
		result = urlfetch.fetch(self.request.get('url'))
		if result.status_code == 200:
			xml = ElementTree.fromstring(result.content)
			channel = xml.find("channel")
			self.response.out.write("<p>%s</p>" % channel.find("title").text)
			items = channel.findall("item")
			i = 1
			for item in items:
				self.response.out.write("<p>Item%d : <a href=\"%s\">%s</a><br>" % (i, item.find("link").text, item.find("title").text))
				description = item.find("description")
				if description != None:
					self.response.out.write("Content : %s</p>" % description.text)
				i += 1
				
					
#			title = xml.find("title")
#			for title in titles:
#			self.response.out.write("title = %s<br>" % title.text)
#			for e in xml.getiterator():
#				self.response.out.write("%s = %s<br>" % (e.tag, e.text))
		


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/rss', GetRSS)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
