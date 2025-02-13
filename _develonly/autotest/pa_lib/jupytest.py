#INFO: convenience functions for autotest using jupyter

import os
os.putenv('P_VISIBLE','1')
import re
import json

from IPython.display import Image
from pa_lib.webdriver import *
from pa_lib.shortcuts import *
from pa_lib import shortcuts

from pa_lib.testlibloader import TestLibLoader

tests= TestLibLoader()
args= {'MAIN': True} #U: default as global, so we can use function argument with loader

b= None
show_after= True #U: default, show screenshot after each command
def set_show_after(v):
	global show_after
	show_after= v

url_prefix= ''
def set_url_pfx(pfx,force=False):
	global url_prefix
	if (url_prefix=='' or force):
		url_prefix= pfx

def browser(forceRestart=False):
	if (shortcuts.browser==None or forceRestart):
		shortcuts.browser= get_browser()
		b= shortcuts.browser
	return shortcuts.browser

def image(el,only_show_after=False):
	if el!=None and (not only_show_after or show_after):
		try:
			png= getattr(el,'screenshot_as_png',None) or getattr(el,'get_screenshot_as_png',None)()
			display(Image(png))
		except:
			pass #A: no image, no problem

def screen(only_show_after=False):
	image(browser(), only_show_after)

def navTo(url=''):
	try:
		url2=url_prefix + url if not url.startswith('http') else url
		browser().get(url2)
		#TODO:check we got there!
		browser().execute_script("""
		(function (XHR) {
			var element = document.createElement('div');  element.style='display: none;'; element.id = "pa_test_ajax";
			element.appendChild(document.createTextNode("")); document.body.appendChild(element);
			//A: element to save responses

			var open = XHR.prototype.open; var send = XHR.prototype.send; //A: ori for monkey patch
			XHR.prototype.open = function(method, url, async, user, pass) {
				this._url = url; //A: save to track the url requested
				open.call(this, method, url, async, user, pass);
			};

			XHR.prototype.send = function(data) {
				var self = this; var oldOnReadyStateChange; var url = this._url;

				function onReadyStateChange() {
					if(self.readyState == 4 /* complete */) {
						console.log("pa_test XMLHttpRequest response");
						document.getElementById("pa_test_ajax").innerHTML +=
							JSON.stringify({url: this._url, status: self.status, data: self.responseText})+',\\n';
					}
					if(oldOnReadyStateChange) { oldOnReadyStateChange(); }
				}

				if(this.addEventListener) { this.addEventListener("readystatechange", onReadyStateChange, false);
				} else {
					oldOnReadyStateChange = this.onreadystatechange;
					this.onreadystatechange = onReadyStateChange;
				}
				send.call(this, data);
			}

			console.log("pa_test XMLHttpRequest patched");
		})(XMLHttpRequest)
		""")
		screen(True)
		return b
	except:
		raise Exception(f"navTo '{url2}'")

def ajaxData():
	dls= attr('innerHTML','pa_test_ajax').split('\n')
	r= []
	for dl in dls:
		try:
			d= json.loads(dl[:-1]) #A:final ,
			try:
				d['text']= d.get('data','')
				d['data']= json.loads(d['text']);
			except:
				pass
			r.append(d)
		except:
			pass
	return r	

shortcuts_find= shortcuts.find #A: save for monkey patch
def find(*find_args,**find_kwargs):
	el= shortcuts_find(*find_args,**find_kwargs)
	if (el):
		image(el, True)
	return el
shortcuts.find= find #A: monkey patch

def click(*find_args,**find_kwargs):
	el= shortcuts.click(*find_args,**find_kwargs)
	screen(True)
	return el

def clickRight(*find_args,**find_kwargs):
	el= shortcuts.clickRight(*find_args,**find_kwargs)
	screen(True)
	return el

def contextMenu(*find_args,**find_kwargs):
	menu= shortcuts.contextMenu(*find_args,**find_kwargs)
	image(menu,True)	
	return menu

def contextMenuClick(*find_args,**find_kwargs):
	el= shortcuts.contextMenuClick(*find_args,**find_kwargs)
	screen(True)
	return el

def write(*find_args,**find_kwargs):
	el= shortcuts.write(*find_args,**find_kwargs)
	screen(True)
	return el 

set_url_pfx(os.getenv('TEST_URL_PFX',''))
