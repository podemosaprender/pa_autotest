#INFO: nombres cortos para controlar desde interactivo

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

browser= None

def _locators(what, by="sel id name aria value text"):
	return list([ ( 
			By.XPATH if how=='text' else By.CSS_SELECTOR, 
			( 
				what if how=='sel' else
				f'#{what}' if how=='id' else
				f'[name="{what}"]' if how=='name' else
				f'[aria-label="{what}"]' if how=='aria' else
				f'[value="{what}"]' if how=='value' else
				f".//*[text()='{what}']"	
			)
		) #A: a tuple for selenium
		for how in by.split(' ')
	])

def _find_attempt(locators,parent):
	#DBG: print("parent:",parent)
	for l in locators:
		try:
			el= parent.find_element(*l)	
			if el:
				return el
		except:
			pass

def find(what, parent=None, by="sel id name aria value text", wait_s=10, path=None):
	"""find an element"""
	el= None #DFLT
	if type(what)!=str:	 #A: is element
		el= what 
	else:
		parent= parent or browser
		el= None
		ls= _locators(what, by)
		try:
			el= WebDriverWait(parent, wait_s).until( lambda p: _find_attempt(ls, parent) )
		except:
			pass

	if el:
		if path:
			el= el.find_element(By.XPATH, path)
		return el

	return None

def click(*find_args,**find_kwargs):
	"""find and click an element"""
	el= find(*find_args,**find_kwargs)
	browser.execute_script("arguments[0].scrollIntoView(true);", el)
	try:
		el.click()
	except (ElementClickInterceptedException, ElementNotInteractableException) as ex1:
		browser.execute_script("arguments[0].click();", el)

	return el

def clickRight(*find_args,**find_kwargs):
	el= find(*find_args,**find_kwargs)
	actions = ActionChains(browser)
	actions.context_click(el).perform()	
	return el
	
def write(what, txt,*find_args,**find_kwargs): 
	"""find and send keys to an element"""
	txt2= txt.replace('\n',Keys.ENTER)
	el= find(what,*find_args,**find_kwargs)
	el.send_keys(Keys.CONTROL + "a")
	el.send_keys(Keys.DELETE)
	el.send_keys(txt2)
	return el

def contextMenu(*find_args,**find_kwargs):
	el= find(*find_args,**find_kwargs)
	if el:
		elchs= el.find_elements(By.CSS_SELECTOR,'*')
		if elchs and len(elchs)>0: #A: in case handler is only for inner elemenets
			clickRight(elchs[0])
		else:
			clickRight(el)

	menuEs= browser.find_elements(By.CSS_SELECTOR,'.context-menu-list') #TODO:jquery ui specific
	for menu in menuEs:
		if menu.value_of_css_property('display')!='none':
			return menu
	return none

def contextMenuOptions(*find_args,**find_kwargs):
	menu= contextMenu(*find_args,**find_kwargs)
	menu_opts={ el.text:el for el in menu.find_elements(By.CSS_SELECTOR,'li')}
	return menu_opts

def contextMenuClick(what,option,*find_args,**find_kwargs):
	menu= contextMenuOptions(what,*find_args,**find_kwargs)
	opt_el= menu[option]
	return click(opt_el)

def dropdownSelect(what,option,*find_args,**find_kwargs):
		dropdown=find(what,*find_args,**find_kwargs)
		dropdown.find_element(By.XPATH,f"//option[text()='{option}']").click()

def attr(attr,*find_args,**find_kwargs):
	el= find(*find_args,**find_kwargs)
	return el.get_attribute(attr)

def html(*find_args,**find_kwargs):
	return attr('outerHTML',*find_args,**find_kwargs)

def data(*find_args,**find_kwargs):
	el= find(*find_args,**find_kwargs)
	el_html= html(el)
	el_tag0= re.match(r'<([^>]+)', el_html)
	el_attrs= [	 { att[0]:(att[1] or att[2]) 
		 for att in re.findall(r'(\w+)=(?:"([^"]+)")|([^"\s]+)',atts) 
		 if att[0]!='style'
		}
		for atts in re.findall(r'<\w+\s+([^>]+)',el_html)
	]
	return {
		'text': el.text,
		'pos': el.location,
		'html': el_html,
		'attrs': el_attrs,
	}

def search(parent=None):
	"""list available inputs, buttons, links..."""
	#TODO: return a list of kv, filter by tag, regex, etc.
	for t in ['input','button','a']:
		for e in (parent or browser).find_elements(By.TAG_NAME,t): 
			print(t+': '+'\t'.join([ k+"='"+e.get_attribute('name')+"'" for k in ['id','name','type','href'] ]))

