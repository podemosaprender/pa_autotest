#FROM: https://www.selenium.dev/selenium/docs/api/py/index.html
from pa_lib import BaseTest

class TestExample(BaseTest):
	def testPageTitleFalla(self):
		self.browser.get('http://www.google.com')
		self.assertIn("example this can't be the title", self.browser.title)

	def testPageTitleOk(self):
		self.browser.get('http://www.google.com')
		print(f'title is {self.browser.title}')
		self.assertIn('Google', self.browser.title)

if __name__ == '__main__':
	unittest.main(verbosity=2)


