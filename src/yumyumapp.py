from google.appengine.api import urlfetch


from xml.etree import ElementTree

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import users
import os
from google.appengine.ext.webapp import template

class UserData(db.Model):
	user = db.UserProperty(required=True,auto_current_user_add=True)
	url = db.LinkProperty(required=True)
	ref = db.ReferenceProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class SiteData(db.Model):
	url = db.LinkProperty(required=True)
	data = db.BlobProperty()

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.path))
		query = UserData.all()
		query.filter('user =', user)
		results = query.fetch(10)
		for result in results:
			siteData = result.ref
			xml = ElementTree.fromstring(siteData.data)
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
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, None))

class AddSite(webapp.RequestHandler):
	def post(self):
		targetURL = self.request.get('url')
		result = urlfetch.fetch(targetURL)
		if result.status_code == 200:
			user = users.get_current_user()
			userDataKey = user.nickname()+targetURL
			userData = UserData.get_or_insert(userDataKey, url=targetURL)
			siteData = SiteData.get_by_key_name(targetURL)
			if not siteData:
				siteData = SiteData.get_or_insert(targetURL, url=targetURL)
			siteData.data = result.content
			siteData.put()
			userData.ref = siteData
			userData.put()
			self.redirect('/')
#		if result.status_code == 200:
#			xml = ElementTree.fromstring(result.content)
#			channel = xml.find("channel")
#			self.response.out.write("<p>%s</p>" % channel.find("title").text)
#			items = channel.findall("item")
#			i = 1
#			for item in items:
#				self.response.out.write("<p>Item%d : <a href=\"%s\">%s</a><br>" % (i, item.find("link").text, item.find("title").text))
#				description = item.find("description")
#				if description != None:
#					self.response.out.write("Content : %s</p>" % description.text)
#				i += 1
				
					
#			title = xml.find("title")
#			for title in titles:
#			self.response.out.write("title = %s<br>" % title.text)
#			for e in xml.getiterator():
#				self.response.out.write("%s = %s<br>" % (e.tag, e.text))
		


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/rss', AddSite)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
