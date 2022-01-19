import os, sys, traceback
from IPython.core.magic import register_cell_magic, register_line_cell_magic
import builtins

try:
    from slackweb import Slack     
except ModuleNotFoundError:
    import os
    os.system('pip install slackweb')
    from slackweb import Slack     

_name = 'unknown'
_code = None

def _logging(data):
  if _code is None:
    return
  slack = Slack(_code)
  data['name'] = _name
  text = json.dumps(data, ensure_ascii=False)
  slack.notify(text = text)

def login(name, code=None):
  global _name, _code
  _name = name
  _code = code

lines = []

def input(s=''):
  global lines
  if lines is not None and len(lines) > 0:
    return lines.pop(0)
  else:
    print('[FIXME] input()の実行回数が多過ぎ. RE になります')
    lines = None
  return builtins.input(s)

def _call_func(func: str):
  try:
    get_ipython().ev(f'{func}()')
  except NameError as e:
    if f"'{func}'" in str(e):
      return False
  return True

@register_cell_magic
def In(line, cell): #Colab上で最初に一度定義する。
  global lines
  lines = [line for line in cell.split('\n') if len(line) > 0]
  try:
    if not _call_func('main'):
      print('[FIXME] main 関数を定義してね')
  except Exception as e:
    #print('Error', e, type(e))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    formatted_lines = traceback.format_exc().splitlines()
    code = False
    code_lines = []
    for l in formatted_lines:
      if code == True:
        code_lines.append(l)
      if 'ipython-input-' in l:
        code = True
        continue
      code = False
    traceback.print_exc()
    print(code_lines[-1])
  finally:
    lines = None
    #raise e
  return None

import IPython
from IPython.display import display, HTML

STYLE = '''
<div style="white-space: pre; font-family: monospace; font-size: 16pt; ">
$CODE
</div>
'''

def _html(s):
  ss = []
  for c in s:
    if c == '\t':
      ss.append(f'<span style="background: lightblue; color: white">→→</span>')
    elif ord(c) > 126:
      ss.append(f'<span style="background: pink; color: white">{c}</span>')
    else:
      ss.append(c)
  return HTML(STYLE.replace('$CODE', ''.join(ss)))

@register_cell_magic
def cc(line, cell): 
  lines  = [line for line in cell.split('\n') if len(line.strip()) > 0]
  display(_html(cell))
  try:
    ipy = get_ipython()
    ipy.ex(cell)
  except SyntaxError as e:
    traceback.print_exc()
    raise e

import re

NameError_ = re.compile('NameError: name \'(.*?)\' is not defined')
TypeError_ = re.compile('TypeError: \'(.*?)\' object is not callable')
AttributeError_ = re.compile('AttributeError: \'(.*?)\' object has no attribute \'(.*?)\'')

def translate_error(s):
  result = NameError_.match(s)
  if result:
    name = result.group(1)
    return "NameError: 変数名{}は、打ち間違いか、まだインポートされていないか、とにかく未定義です".format(name)
  result = TypeError_.match(s)
  if result:
    obj = result.group(1)
    return "TypeError: {}の値を関数名に代入してしまったため、呼び出せない".format(obj)
  result = AttributeError_.match(s)
  if result:
    obj = result.group(1)
    name = result.group(2)
    return "AttributeError: {}型には、{}のようなメソッドやプロパティはありません".format(obj,name)
  return s

def t(e):
  print(e, translate_error(e),sep='\n\t=>')

# t("NameError: name 'X' is not defined")
# t("TypeError: 'int' object is not callable")
# t("AttributeError: 'int' object has no attribute 'find'")

