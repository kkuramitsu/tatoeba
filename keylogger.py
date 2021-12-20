import os
import uuid
import json

try:
    import IPython
    from google.colab import output
    try:
        from slackweb import Slack     
    except ModuleNotFoundError:
        import os
        os.system('pip install slackweb')
        from slackweb import Slack     
except ModuleNotFoundError:
    pass


# ダミー関数

HTML_SIMPLE = '''
<textarea id="input" style="float: left; width: 48%; height:100px; font-size: large;"></textarea>
<textarea id="output" style="width: 48%; height:100px; font-size: large;"></textarea>
'''

HTML_NOBU = '''
<style>
.parent {
  background-color: #edebeb;
  width: 100%;
  height: 150px;
}
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:120px; 
  font-size: large;
  outline: none;           /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
.box11{
//    padding: 0.5em 1em;
//    margin: 2em 0;
    color: #5d627b;
    background: white;
    border-top: solid 5px #5d627b;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.22);
}
.box18{
  //padding: 0.2em 0.5em;
  //margin: 2em 0;
  color: #565656;
  background: #ffeaea;
  background-image: url(https://2.bp.blogspot.com/-u7NQvQSgyAY/Ur1HXta5W7I/AAAAAAAAcfE/omW7_szrzao/s800/dog_corgi.png);
  background-size: 150%;
  background-repeat: no-repeat;
  background-position： top right;
  background-color:rgba(255,255,255,0.8);
  background-blend-mode:lighten;
  //box-shadow: 0px 0px 0px 10px #ffeaea;
  border: dashed 2px #ffc3c3;
  //border-radius: 8px;
}
.box16{
    //padding: 0.5em 1em;
    //margin: 2em 0;
    background: -webkit-repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
    background: repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
}
.box24 {
    position: relative;
    padding: 0.5em 0.7em;
    margin: 2em 0;
    background: #6f4b3e;
    color: white;
    font-weight: bold;
}
.box24:after {
    position: absolute;
    content: '';
    top: 100%;
    left: 30px;
    border: 15px solid transparent;
    border-top: 15px solid #6f4b3e;
    width: 0;
    height: 0;
}
</style>
<input id="name"/><label>👈名前(ニックネーム)</label>
<div class="parent">
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">改行を忘れないで</label>
<textarea id="input" class="box16"></textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">見本</label>
<textarea id="output" class="box18 python" readonly></textarea>
</div>
</div>
'''

SCRIPT = '''
<script>
    var timer = null;
    var buffers = [];
    var inputPane = document.getElementById('input');
    var send_data = () => {
        var name = document.getElementById('name').value;
        var value = inputPane.value;
        var text = buffers.join(' ');
        google.colab.kernel.invokeFunction('notebook.Convert', [text, value, name], {});
        buffers=[];
    };
    var log_data = () => {
      if(buffers.length !== 0) {
        send_data();
      }
      google.colab.kernel.invokeFunction('notebook.Logger', [], {});
    };
    var before = new Date().getTime();
    inputPane.addEventListener('keydown', (e) => {
      var now = new Date().getTime();
      var value = e.srcElement.value;
      if(e.key === ' ') {
        buffers.push(`${now - before} SPACE`);
      }
      else {
        buffers.push(`${now - before} ${e.key}`);
      }
      before = now;
      if(e.keyCode === 13) {
        send_data();
      }
      if(timer !== null) {
        clearTimeout(timer);
      }
      timer = setTimeout(log_data, 1000*30); //
    });
</script>
'''

SAMPLE = '''import math
print('hello world')
x = math.sin(math.pi/4)
y = math.cos(math.pi/2)
print(x+y)
'''

def print_nop(*x):
    pass

def key_logger(text=SAMPLE, print=print_nop):
    session = str(uuid.uuid1())
    seq = 0
    logs = []
    cached = {'':''}
    HOST = 'slack.com'
    ID = 'T02NYCBFP7B'
    ID2 = 'B02QPM8HNBH'
    ID3 = 'jszfGMmnZ9JL7WVVRGpy0Uvd'
    url = f'https://hooks.{HOST}/services/{ID}/{ID2}/{ID3}'
    slack = Slack(url)

    def convert(text, value, name):
        nonlocal seq
        try:
            data = text.split('\n')[-1]
            value = value.split('\n')[-1]
            jsondata = {
                'seq': seq,
                'name': name,
                'uuid': str(uuid.uuid4()),
                'input': value,
                'data': data,
            }
            seq += 1
            logs.append(jsondata)
            # jsondata = json.dumps(jsondata, ensure_ascii=False)
            # print(jsondata)
            # slack.notify(text = jsondata)
        except Exception as e:
            print(e)
        return e

    def logger():
        nonlocal logs
        try:
            if len(logs) > 0:
                jsondata = json.dumps(logs, ensure_ascii=False)
                print(jsondata)
                slack.notify(text = jsondata)
                logs = []
        except Exception as e:
            print(e)
        return e

    output.register_callback('notebook.Convert', convert)
    output.register_callback('notebook.Logger', logger)
    HTML=HTML_NOBU.replace('readonly></text', f'readonly>{text}</text')
    display(IPython.display.HTML(HTML))
    display(IPython.display.HTML(SCRIPT))

#key_logger()
