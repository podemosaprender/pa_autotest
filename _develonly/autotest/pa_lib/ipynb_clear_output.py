#!/usr/bin/env python
#
# to use : [python|pypy] clear_ipynb.py -s --empty-markdown -o out.ipynb in.ipynb

import os  # to read/write files
import codecs  # to read/write UTF-8 files
import sys  # to print to stdout in UTF-8
import argparse  # to parse arguments
import json  # to parse the .ipynb which is a json file
import re  # to strip the solutions


def print_error(message):
    print(f"{'':->21}\n -- !!!-- {message}\n{'':->21}")


# create the argument parser
parser = argparse.ArgumentParser(description="""
Clear a Jupyter notebook:
- clear cell outputs [except if --no-outputs]
- clear cell metadata.scrolled [except if --no-scrolled]
- clear cell execution counts [except if --no-execution-count]
- clear metadate to keep only the standard parts [except if --keep-metadata]
- remove empty code cells [except if --no-empty-code]
- remove empty markdown cells [if --empty-markdown]
- strip solutions (parts between comments)  [if --strip-solutions or -s]
    - in this case protect cells [except if --no-protect-cells] against deletion and edition
""",
                                 formatter_class=argparse.RawTextHelpFormatter)

# get the arguments
parser.add_argument('in_file', nargs=1, metavar="in.ipynb", help='the file name of jupyer notebook to clear')
parser.add_argument('-o', '--out-file', nargs=1, metavar="out.ipynb", help='save to the indicated file')
parser.add_argument('-i', '--in-place', action="store_true", help='edit file in-place, save backup as <filename>_bak.ipynb')
parser.add_argument('-a', '--all', action="store_true", help='maximal cleaning = -s --empty-markdown')
parser.add_argument('-s', '--strip-solutions', action="store_true", help='strip the solutions, and save to indicated file')
parser.add_argument('-v', '--verbose', action="store_true", help='provide additional informations')
parser.add_argument('--no-scrolled', action="store_true", help='do not clear metadata.scrolled')
parser.add_argument('--no-outputs', action="store_true", help='do not clear outputs')
parser.add_argument('--no-execution-count', action="store_true", help='do not clear execution counts')
parser.add_argument('--keep-metadata', action="store_true", help='do not clear the global metadata')
parser.add_argument('--no-empty-code', action="store_true", help='do not remove empty code cells')
parser.add_argument('--empty-markdown', action="store_true", help='remove empty markdown cells')
parser.add_argument('--no-protect-cells', action="store_true", help='do not protect cells from deletion/edition')
parser.add_argument('--no-backup', action="store_true", help='do not backup the original [valid only with -i]')
argop = vars(parser.parse_args())

in_file = argop['in_file'][0]
if argop['out_file']:
    out_file = argop['out_file'][0]
else:
    out_file = False

if argop['all']:
    argop['strip_solutions'] = True
    argop['empty_markdown'] = True

strip_solutions = argop['strip_solutions']
in_place = argop['in_place']
if in_place and out_file:
    print(f"Error : -i and -o options are incompatible !")
    exit(1)
if in_place and strip_solutions:
    print(f"Error : -i and -s options are incompatible !")
    exit(1)
if out_file == in_file:
    print(f"Error : the destination and the original files are the same !")
    exit(1)

clear_scrolled = not argop['no_scrolled']
clear_outputs = not argop['no_outputs']
clear_execution_count = not argop['no_execution_count']
clear_metadata = not argop['keep_metadata']
empty_code = not argop['no_empty_code']
empty_markdown = argop['empty_markdown']
protect_cells = not argop['no_protect_cells']
backup_original = not argop['no_backup']
verbose = argop['verbose']

# read the .ipynb file to `data` variable
try:
    with codecs.open(in_file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
except Exception as e:
    print_error(f"Error parsing file : {in_file}")
    print(f"Error message: {e}")
    exit(1)

# set the counters
number = {
    'cleared': {
        'outputs': 0,
        'execution_count': 0,
        'scrolled': 0,
    },
    'removed': {
        'empty code cells': 0,
        'empty markdown cells': 0,
        'global metadata elements': 0,
    },
    'striped': {
        'code': 0,
        'markdown': 0,
    }
}
# standard meta data to keep
standard_meta_keys = ['kernelspec', 'language_info']

# start cleanings
if in_place or out_file:
    in_place_str = " (in place)" if in_place else ""
    print(f"Cleaning{in_place_str} {in_file}")

if 'cells' in data:
    for cell in data['cells']:

        # clear the outputs
        if clear_outputs and ('outputs' in cell) and len(cell['outputs']) > 0:
            cell['outputs'].clear()
            number['cleared']['outputs'] += 1
        if clear_execution_count and ('execution_count' in cell) and cell['execution_count'] is not None:
            cell['execution_count'] = None
            number['cleared']['execution_count'] += 1
        if clear_scrolled:
            try:
                del cell['metadata']['scrolled']
                number['cleared']['scrolled'] += 1
            except KeyError:
                pass
        if empty_code and (cell['cell_type'] == "code") and (not cell['source']):
            cell.clear()
            number['removed']['empty code cells'] += 1
        elif empty_markdown and (cell['cell_type'] == "markdown") and (not cell['source']):
            cell.clear()
            number['removed']['empty markdown cells'] += 1

        # strip the solutions
        if cell and strip_solutions:
            if protect_cells:
                cell['metadata']['deletable'] = False
                cell['metadata']['editable'] = False
            if ('source' in cell) and cell['source'] and cell['cell_type'] in number['striped']:
                old_source = json.dumps(cell['source'])
                re_solutions = r'[,\s\n]*"\s*(#|<!)\s*--- .*?solution[\d\D]*?"\s*(#|<!)\s*--- .*?solution.*?"'
                new_source = re.sub(re_solutions, r"", old_source, 0, re.MULTILINE).replace('[,', '[')
                if old_source != new_source:
                    cell['source'] = json.loads(new_source)
                    if protect_cells:
                        del cell['metadata']['editable']  # can be edited but not deleted
                    number['striped'][cell['cell_type']] += 1

    # remove empty cells if any and if needed
    if empty_code or empty_markdown:
        data['cells'] = list(filter(None, data['cells']))

    # clear global metadata
    if clear_metadata and 'metadata' in data:
        for key in data['metadata']:
            if not key in standard_meta_keys:
                number['removed']['global metadata elements'] += 1
        data['metadata'] = {key: data['metadata'][key] for key in standard_meta_keys if key in data['metadata']}

# Print the modifications
if in_place or out_file:
    changes = 0
    for t in number:
        for k in number[t]:
            if number[t][k] > 0 or verbose:
                changes += 1
                print(f"Number of {t} '{k}': {number[t][k]}")
    if changes == 0 and not verbose:
        print("File was already clean.")

# if file is replaced (with cleared cells, but keeping the solutions)
if in_place:
    if backup_original:
        try:
            backup = re.sub(r"(\.ipynb)$", r"_bak.ipynb", in_file)
            os.rename(in_file, backup)
            if verbose:
                print(f"Backup in {backup}")
        except Exception as e:
            print_error(f"Error during the rename : {in_file} »»» {backup}")
            print(f"Error message: {e}")
    elif verbose:
        print("No backup.")

    try:
        with codecs.open(in_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1, sort_keys=True, ensure_ascii=False)
        if verbose:
            print(f"Save cleaned version in {in_file}")
    except Exception as e:
        print_error(f"Error saving file : {in_file}")
        print(f"Error message: {e}")
        exit(1)
    exit()

# if file is saved as another file
if out_file:
    try:
        with codecs.open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1, sort_keys=True, ensure_ascii=False)
        if verbose:
            print(f"Save cleaned version in {out_file}")
    except Exception as e:
        print_error(f"Error saving file : {out_file}")
        print(f"Error message: {e}")
        exit(1)
    exit()

# dump to the output the cleaned file
# so we can use clean_ipynb in.ipynb > out.ipynb
sys.stdout.reconfigure(encoding='utf-8')
json.dump(data, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)

