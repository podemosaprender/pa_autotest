#INFO: rewrite urls within html, css, js so everything goes through our proxy
#U: 1. mitmproxy -m reverse:https://original-site.make.podemosaprender.org -p 7777 -s 01host_rewrite.py
#U: 2. point your browser to http://localhost:7777 (check in network all comes from "localhost")
#FROM: https://github.com/mitmproxy/mitmproxy/blob/main/examples/addons/http-reply-from-proxy.py

from mitmproxy import http
from os import getenv

PROXY_HOST= getenv('P_PROXY_HOST','users-login-here-for-debug.make.podemosaprender.org')
REVERSED_HOST= getenv('P_REVERSED_HOST', 'original-site.make.podemosaprender.org')
PROXY_PROTO= getenv('P_PROXY_PROTO','https')

def response(flow: http.HTTPFlow) -> None:
	if flow.response and flow.response.content:
		if flow.response.headers.get('Location',None):
			flow.response.headers['Location']= PROXY_PROTO+'://'+PROXY_HOST

		cookie= flow.response.headers.get('Set-Cookie',None)
		if cookie:
			flow.response.headers['Set-Cookie']= cookie.replace(
				REVERSED_HOST, PROXY_HOST #A:NO PORT HERE
			)
		print(f"Cookie {cookie}")

		flow.response.content = flow.response.content.replace(
			bytes("https://"+REVERSED_HOST,'utf8'), bytes(PROXY_PROTO+"://"+PROXY_HOST,'utf8')
		)
