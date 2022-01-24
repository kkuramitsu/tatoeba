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

import requests
from bs4 import BeautifulSoup

SAMPLE = {}

def get_sample(problem):
  problem = problem.lower()
  if '_' in problem:
    problem, num = problem.split('_')
  else:
    num = problem[-1]
    problem = problem[:-1]
  pid = f'{problem}_{num}'
  if pid in SAMPLE:
    return SAMPLE[pid]
  response_text = requests.get(url=f"https://atcoder.jp/contests/{problem}/tasks/{problem}_{num}").text
  html = BeautifulSoup(response_text, "lxml")
  d = {}
  for a in html.find_all("section"):
    #print(a)
    if a.h3 and a.pre:
      key = a.h3.text.replace('\r\n','\n')
      value = a.pre.text.replace('\r\n','\n')
      d[key]=value
  
  SAMPLE[pid] = d
  return d

import os, sys, traceback
from IPython.core.magic import register_cell_magic, register_line_cell_magic
import IPython
from IPython.display import display, HTML
import builtins

lines = None
outputs = []

def input(s=''):
  global lines
  if lines is not None and len(lines) > 0:
    return lines.pop(0)
  else:
    lines = None
  return builtins.input(s)

def print(*a, **kw):
  builtins.print(*a, **kw)
  if outputs is not None:
    sep = kw.get('sep', ' ')
    end = kw.get('end', '\n')
    s = sep.join([str(s) for s in a]) + end
    outputs.append(s)

def judge(problem, code):
  global lines, outputs
  d = get_sample(problem)
  try:
    for key in ['入力例 1', '入力例 2', '入力例 3']:
      if key not in d:
        continue
      display(HTML(f'<h3>{key}</h3><pre style="background: lightgray">{d[key]}</pre>'))
      lines = [s for s in d[key].split('\n') if len(s)>0] 
      outputs = []
      res = get_ipython().run_cell(code)
      res.raise_error()
      key = key.replace('入力', '出力')
      output_example = d[key]
      result = ''.join(outputs)
      if result != output_example:
        display(HTML(f'<h3>{key}</h3><pre style="background: lightgray">{d[key]}</pre>'))
        _display_diff(output_example, result)
      lines = None
      outputs = None
  except Exception as e:
    msg = translate_error(str(e))
    if msg is not None:
      display(HTML(f'<h3>コーギーのエラー分析</h3>'))
      display(HTML(msg))
      if '構文エラー' in msg:
        display(_codeHTML(code))
  finally:
    lines = None
    outputs = None


import difflib

def _display_diff(ground_truth, target):
    """
    文字列の差異をハイライト表示する
    """
    color_dic = {
        'yellow':'<span style="background: pink">',
        'red':'<span style="background: lightblue">',  
        'end':'</span>'
    }
    if ground_truth == target:
      return

    d = difflib.Differ()
    diffs = d.compare(ground_truth, target)

    result = ''
    for diff in diffs:
        status, _, character = list(diff)
        if status == '-':
            character = color_dic['red'] + character + color_dic['end']
        elif status == '+':
            character = color_dic['yellow'] + character + color_dic['end']
        else:
            pass
        result += character

    display(HTML(f'<h3>差分</h3><div style="white-space: pre-wrap;">{result}</div>'))

@register_cell_magic
def atcoder(problem, code): #Colab上で最初に一度定義する。
  try:
    judge(problem, code)
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


STYLE = '''
拡大するから落ち着いて、構文エラーを探してください
<div style="white-space: pre; font-family: monospace; font-size: 16pt; ">
$CODE
</div>
'''

def _codeHTML(s):
  ss = []
  for c in s:
    if c == '\t':
      ss.append(f'<span style="background: lightblue; color: white">→→</span>')
    elif ord(c) > 126:
      ss.append(f'<span style="background: pink; color: white">{c}</span>')
    else:
      ss.append(c)
  return HTML(STYLE.replace('$CODE', ''.join(ss)))

import re

NameError_ = re.compile('name \'(.*?)\' is not defined')
TypeError_ = re.compile('\'(.*?)\' object is not callable')
AttributeError_ = re.compile('\'(.*?)\' object has no attribute \'(.*?)\'')
UnsupportedOperand_ = re.compile('unsupported operand type\(s\) for (.*?): \'(.*?)\' and \'(.*?)\'')
IndentationError_ = re.compile('expected an indented block')
SyntaxError_ = re.compile('invalid character in identifier')
SyntaxError_ = re.compile('unexpected EOF while parsing')

def translate_error(s):
  result = NameError_.match(s)
  if result:
    name = result.group(1)
    return "NameError: 変数名{}は、打ち間違いか、まだインポートされていないか、とにかく未定義です".format(name)
  result = TypeError_.match(s)
  if result:
    obj = result.group(1)
    return "TypeError: {}の値をたぶん関数名に代入してしまったため、呼び出せなくなっています".format(obj)
  result = AttributeError_.match(s)
  if result:
    obj = result.group(1)
    name = result.group(2)
    return "AttributeError: {}型には、{}のようなメソッドやプロパティはありません".format(obj,name)
  result = UnsupportedOperand_.match(s)
  if result:
    operand = result.group(1)
    type1 = result.group(2)
    type2 = result.group(3)
    return "TypeError: {}型と{}型の間で演算子 {} を計算しようとしましたが、そこでは使えません".format(type1,type2,operand)
  result = IndentationError_.match(s)
  if result:
    return "<b>構文エラー</b>: ブロックはインデントされるはずですが、インデントされていません"
  result = SyntaxError_.match(s)
  if result:
    return "<b>構文エラー</b>: 半角文字を使うところで、全角文字が使われています"
  result = SyntaxError2_.match(s)
  if result:
    return "<b>構文エラー</b>: 括弧やクオートの閉じ忘れの可能性が高いです"

  return None

