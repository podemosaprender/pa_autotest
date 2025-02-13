#INFO: como subir un archivo
#VER: http://the-internet.herokuapp.com/

from pa_lib.webdriver import get_browser, free_browser

dst_fname= 'results/x_screenshot.png'

def main():
	browser= get_browser()
	browser.get('http://timeanddate.com')
	browser.save_screenshot(dst_fname)
	print(f'Screenshot saved as {dst_fname}')
	free_browser()

if __name__=="__main__":
	main()
