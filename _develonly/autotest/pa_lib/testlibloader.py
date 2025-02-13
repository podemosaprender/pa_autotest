#INFO: load other ipynb as functions

import json

def ipynb_to_source(fname): 
		src_json= None
		with open(fname+'.ipynb','rt') as srcnb: #TODO:pathS to search
			src_json= json.loads(srcnb.read())

		if 'cells' in src_json:
			src='\n'.join(src_json['cells'][0]['source'])+'\ndef fun(*largs,**args):'
			for c in src_json['cells'][1:]:
				if c['cell_type']=='code':
					#DBG: print(f"SRC: {c['source']}")
					src= src + '\n\t' + '\n\t'.join(c['source'])
		
		return src
	
class TestLibLoader():
	def __getattr__(self,k):
		parts= k.split('__',2)
		fname= parts[0]
		part= parts[1] if len(parts)>1 else 'default'
		src= ipynb_to_source(fname)
		g= {}
		exec(src,g)
		return g['fun']


