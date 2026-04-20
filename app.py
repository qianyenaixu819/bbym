from flask import Flask, render_template_string
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>就那样</title></head>
<body>
<h1>🤓☝️ 一个很精彩的人</h1>
<p>内容自己填，我只负责看框架</p >
<p>人各有命吧</p >
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/diary')
def diary():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True, port=5000)