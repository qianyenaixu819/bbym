import sqlite3
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

DB = 'site.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, username TEXT, content TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, post_id INTEGER, PRIMARY KEY(user_id, post_id))''')
    conn.commit()
    conn.close()

init_db()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 关掉日志 省得烦
    
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        cookie = self.headers.get('Cookie', '')
        uid = None
        if 'session=' in cookie:
            uid = cookie.split('session=')[1].split(';')[0]
        
        if path == '/':
            self.home(uid, query.get('error', [''])[0])
        elif path == '/logout':
            self.logout()
        elif path.startswith('/delete/'):
            self.delete_post(uid, path.split('/')[-1])
        elif path.startswith('/like/'):
            self.like(uid, path.split('/')[-1])
        elif path.startswith('/delete_comment/'):
            self.delete_comment(uid, path.split('/')[-1])
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = parse_qs(self.rfile.read(length).decode())
        cookie = self.headers.get('Cookie', '')
        uid = None
        if 'session=' in cookie:
            uid = cookie.split('session=')[1].split(';')[0]
        
        if path == '/register':
            self.register(body)
        elif path == '/login':
            self.login(body)
        elif path == '/post':
            self.post(uid, body)
        elif path.startswith('/comment/'):
            self.comment(uid, path.split('/')[-1], body)
        else:
            self.send_error(404)
    
    def home(self, uid, error):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM posts ORDER BY time DESC")
        posts = c.fetchall()
        
        username = None
        if uid:
            c.execute("SELECT username FROM users WHERE id=?", (uid,))
            row = c.fetchone()
            if row:
                username = row[0]
        
        html = '''
        <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>不药娘网</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box}
            body{font-family:-apple-system,sans-serif;background:#f5f5f7;max-width:600px;margin:40px auto;padding:20px}
            h1{font-size:48px;margin-bottom:8px}
            .card{background:rgba(255,255,255,0.72);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-radius:24px;padding:24px;margin:20px 0;box-shadow:0 8px 32px rgba(0,0,0,0.04);border:1px solid rgba(255,255,255,0.5)}
            input{width:100%;padding:14px;margin:8px 0;border:1px solid #ddd;border-radius:16px;background:rgba(255,255,255,0.6)}
            button{background:#0071e3;color:#fff;border:none;padding:10px 20px;border-radius:16px;font-weight:600;margin:4px;cursor:pointer}
            .logout-btn{background:none;border:1px solid #ff3b30;color:#ff3b30;padding:8px 16px;border-radius:20px;cursor:pointer}
            .error{color:#ff3b30;margin:8px 0}
            .post{padding:15px 0;border-bottom:1px solid #eee}
            .comment{margin-left:20px;padding:10px;border-left:2px solid #0071e3;margin-top:10px}
            .footer{margin-top:40px;text-align:center;color:#86868b}
            .like-btn{background:none;border:none;color:#ff3b30;font-size:18px;cursor:pointer}
            .actions{display:flex;gap:8px;align-items:center;margin-top:8px}
            .header-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
        </style>
        </head><body>
        <h1>不药娘网 🏳️‍⚧️</h1>
        <p>一个很精彩的人 · 唐毓文</p >
        '''
        
        if username:
            html += f'''
            <div class="card">
                <div class="header-bar">
                    <b>👤 {username}</b>
                    <form method="GET" action="/logout" style="display:inline;">
                        <button type="submit" class="logout-btn">退出</button>
                    </form>
                </div>
                <form method="POST" action="/post">
                    <input name="content" placeholder="说点什么..." required>
                    <button type="submit">发帖</button>
                </form>
            </div>
            '''
        else:
            html += f'''
            <div class="card">
                <h3>登录</h3>
                <form method="POST" action="/login">
                    <input name="username" placeholder="账号" required>
                    <input name="password" type="password" placeholder="密码" required>
                    <button type="submit">登录</button>
                </form>
                <h3 style="margin-top:24px;">注册</h3>
                <form method="POST" action="/register">
                    <input name="username" placeholder="新账号" required>
                    <input name="password" type="password" placeholder="密码" required>
                    <button type="submit">注册</button>
                </form>
                {f'<div class="error">{error}</div>' if error else ''}
            </div>
            '''
        
        html += '<h2>全部帖子</h2>'
        
        for p in posts:
            pid = p[0]
            c.execute("SELECT COUNT(*) FROM likes WHERE post_id=?", (pid,))
            like_count = c.fetchone()[0]
            c.execute("SELECT * FROM comments WHERE post_id=? ORDER BY time ASC", (pid,))
            comments = c.fetchall()
            
            html += f'''
            <div class="card">
                <div class="post">
                    <b>{p[2]}</b> {p[3]}<br>
                    <small>{p[4][:16]}</small>
                    <div class="actions">
                        <a href=" "><button class="like-btn">❤️ {like_count}</button></a >
            '''
            if str(uid) == str(p[1]):
                html += f'<a href="/delete/{pid}" onclick="return confirm(\'删除这条？\')"><button>删除</button></a >'
            html += '</div></div>'
            
            if comments:
                html += '<div style="margin-top:12px;">'
                for cmt in comments:
                    html += f'''
                    <div class="comment">
                        <b>{cmt[3]}</b>: {cmt[4]} <small>{cmt[5][:16]}</small>
                        {f'<a href="/delete_comment/{cmt[0]}"><button style="padding:2px 8px;margin-left:8px;">删除</button></a >' if str(uid) == str(cmt[2]) else ''}
                    </div>
                    '''
                html += '</div>'
            
            if uid:
                html += f'''
                <form method="POST" action="/comment/{pid}" style="margin-top:12px;display:flex;gap:8px;">
                    <input name="content" placeholder="写评论..." style="margin:0;" required>
                    <button type="submit" style="width:auto;">发送</button>
                </form>
                '''
            html += '</div>'
        
        conn.close()
        html += '<div class="footer">🏳️‍⚧️ 跨儿帮助跨儿 · 唐毓文</div></body></html>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def logout(self):
        self.send_response(302)
        self.send_header('Set-Cookie', 'session=; Max-Age=0; Path=/')
        self.send_header('Location', '/')
        self.end_headers()
    
    def register(self, body):
        u = body.get('username', [''])[0].strip()
        p = body.get('password', [''])[0].strip()
        if not u or not p:
            self.redirect('/?error=不能为空')
            return
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            h = hashlib.sha256(p.encode()).hexdigest()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, h))
            conn.commit()
            uid = c.lastrowid
            self.send_response(302)
            self.send_header('Set-Cookie', f'session={uid}; Path=/')
            self.send_header('Location', '/')
            self.end_headers()
        except:
            self.redirect('/?error=账号已存在')
        finally:
            conn.close()
    
    def login(self, body):
        u = body.get('username', [''])[0].strip()
        p = body.get('password', [''])[0].strip()
        
        # 后门 4017
        if u == '4017' and p == '4017':
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username='4017'")
            row = c.fetchone()
            if not row:
                h = hashlib.sha256('4017'.encode()).hexdigest()
                c.execute("INSERT INTO users (username, password) VALUES ('4017', ?)", (h,))
                conn.commit()
                uid = c.lastrowid
            else:
                uid = row[0]
            conn.close()
            self.send_response(302)
            self.send_header('Set-Cookie', f'session={uid}; Path=/')
            self.send_header('Location', '/')
            self.end_headers()
            return
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        h = hashlib.sha256(p.encode()).hexdigest()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (u, h))
        row = c.fetchone()
        conn.close()
        if row:
            self.send_response(302)
            self.send_header('Set-Cookie', f'session={row[0]}; Path=/')
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.redirect('/?error=账号或密码错误')
    
    def post(self, uid, body):
        if not uid:
            self.redirect('/')
            return
        content = body.get('content', [''])[0].strip()
        if not content:
            self.redirect('/')
            return
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id=?", (uid,))
        row = c.fetchone()
        if row:
            uname = row[0]
            t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO posts (user_id, username, content, time, likes) VALUES (?, ?, ?, ?, 0)", (uid, uname, content, t))
            conn.commit()
        conn.close()
        self.redirect('/')
    
    def comment(self, uid, pid, body):
        if not uid:
            self.redirect('/')
            return
        content = body.get('content', [''])[0].strip()
        if not content:
            self.redirect('/')
            return
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id=?", (uid,))
        row = c.fetchone()
        if row:
            uname = row[0]
            t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO comments (post_id, user_id, username, content, time) VALUES (?, ?, ?, ?, ?)", (pid, uid, uname, content, t))
            conn.commit()
        conn.close()
        self.redirect('/')
    
    def delete_post(self, uid, pid):
        if not uid:
            self.redirect('/')
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("DELETE FROM comments WHERE post_id=?", (pid,))
        c.execute("DELETE FROM likes WHERE post_id=?", (pid,))
        c.execute("DELETE FROM posts WHERE id=? AND user_id=?", (pid, uid))
        conn.commit()
        conn.close()
        self.redirect('/')
    
    def delete_comment(self, uid, cid):
        if not uid:
            self.redirect('/')
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("DELETE FROM comments WHERE id=? AND user_id=?", (cid, uid))
        conn.commit()
        conn.close()
        self.redirect('/')
    
    def like(self, uid, pid):
        if not uid:
            self.redirect('/')
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?", (uid, pid))
        if c.fetchone():
            c.execute("DELETE FROM likes WHERE user_id=? AND post_id=?", (uid, pid))
            c.execute("UPDATE posts SET likes = likes - 1 WHERE id=?", (pid,))
        else:
            c.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (uid, pid))
            c.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        self.redirect('/')
    
    def redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

if __name__ == '__main__':
    print('http://127.0.0.1:5050')
    HTTPServer(('0.0.0.0', 5050), Handler).serve_forever()