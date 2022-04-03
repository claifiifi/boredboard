from flask import Flask, request, render_template, redirect, g, make_response
import werkzeug, os
import psycopg2
from psycopg2 import pool
import datetime
from pytz import timezone
from random import choice

def get_db():
    print ('GETTING CONN')
    if 'db' not in g:
        g.db = app.config['postgreSQL_pool'].getconn()
    return g.db
def due(title):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT due FROM posts WHERE title=%s", (title,))
    due = cur.fetchone()[0].isoformat()
    print(due)
    cur.close()
    return due

def addtolist(list, filelist, title, board):
    today=datetime.datetime.now(timezone('Asia/Seoul')).date()
    list=list
    if len(filelist) != 0:
        if title=="Today":
            list += '<p style="font-family:Gowun Dodum; margin-block-start: 0px;">%s:</p>' % title
        else:
            list += '<p style="font-family:Gowun Dodum">%s:</p>' % title
        for i in range(len(filelist)):
            if title[:3] == "This Week":
                gap = filelist[i][2]-today
                list += '<li><a href="/board?board={board}&id={id}">{filename}[{gap}]</a></li>'.format(board=board, id=filelist[i][0], filename=filelist[i][1], gap=gap.days)
            else:
                list += '<li><a href="/board?board={board}&id={id}">{filename}</a></li>'.format(board=board, id=filelist[i][0], filename=filelist[i][1])
    return list
def templateList(board):
  db = get_db()
  cur = db.cursor()
  today=datetime.datetime.now(timezone('Asia/Seoul')).date()
  cur.execute("DELETE FROM posts WHERE due<%s", (today - datetime.timedelta(1),))
  cur.execute("SELECT id, title FROM posts WHERE due=%s AND board=%s", (today, board))
  filelist = cur.fetchall()
  list = '<ol style="font-size:5vw; font-family:Gowun Dodum; margin: 0px 0px;" id="rcorners">';
  list = addtolist(list, filelist, "Today", board)
  cur.execute("SELECT id, title FROM posts WHERE due=%s AND board=%s", (today + datetime.timedelta(1), board))
  filelist=cur.fetchall()
  list = addtolist(list, filelist, "Tomorrow", board)
  cur.execute("SELECT id, title, due FROM posts WHERE due<=%s AND due>%s AND board=%s ORDER BY due ASC", (today + datetime.timedelta( (4-today.weekday()) % 7 ), today + datetime.timedelta(1), board))
  filelist=cur.fetchall()
  list = addtolist(list, filelist, "This  Week", board)
  cur.execute("SELECT id, title, due FROM posts WHERE due>%s AND board=%s ORDER BY due ASC", (today + datetime.timedelta( (4-today.weekday()) % 7 ), board))
  filelist = cur.fetchall()
  list = addtolist(list, filelist, "After This Week", board)
  cur.execute("SELECT id, title FROM posts WHERE due<%s AND board=%s ORDER BY due ASC", (today, board))
  filelist = cur.fetchall()
  list = addtolist(list, filelist, "Overdue", board)
  cur.close()
  return list;

def create_app():
    app = Flask(__name__)
    app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(1, 20,user = "<USER_NAME>",
                                                  password = "<PASSWORD>",
                                                  host = "<HOST>",
                                                  port = "<PORT>",
                                                  database = "<DATABASE>")


    @app.teardown_appcontext
    def close_conn(e):
        print('CLOSING CONN')
        db = g.pop('db', None)
        if db is not None:
            app.config['postgreSQL_pool'].putconn(db)


    @app.route("/")
    def home():
        if request.cookies.get("board") != None:
            return redirect("/board?board="+request.cookies.get("board"))
        else:
            return render_template('main.html', title="Home", list='''
            <script>
            sessionStorage.name = "BoredBoard";
            sessionStorage.link = "/";
            sessionStorage.description = "Hello";
            </script>
            <form action="/boarding_num" method="post">
                <input type="number" name="board_num" placeholder="Enter existing board ID"><br><br>
                <input type="password" name="num_password" placeholder="Password"><br><br>

                <input type="submit">
            </form>
            ''',
            body='''
            <form action="/boarding_name" method="post">
                <input type="text" name="board_name" placeholder="Enter new board's name"><br><br>
                <input type="text" name="board_desc" placeholder="Enter new board's description"><br><br>
                <input type="password" name="board_pw" placeholder="Enter new board's password"><br><br>
                <input type="submit">
            </form>
            ''')
    
    @app.route("/boarding_name", methods = ['POST', 'GET'])
    def boarding_name():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            if request.form['board_name'] != None:
                board_name=request.form['board_name']
                board_pw=request.form['board_pw']
                board_desc=request.form['board_desc']
                cur.execute("INSERT INTO boards (name, password, description) VALUES (%s, %s, %s)", (board_name, board_pw, board_desc))
                db.commit()
                cur.execute("SELECT id FROM boards WHERE name=%s ORDER BY id ASC", (board_name,))
                board=cur.fetchall()[-1][0]
                res = make_response(redirect("/board?board=%s" % board))
                res.set_cookie("board", str(board), expires=datetime.datetime(2023, 3, 1, 0, 0))
                res.set_cookie("password", board_pw, expires=datetime.datetime(2023, 3, 1, 0, 0))
                return res
        cur.close()

    @app.route("/boarding_num", methods = ['POST', 'GET'])
    def boarding_num():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            print(request.form['board_num'])
            if request.form['board_num'] != None:
                res = make_response(redirect("/board?board=%s" % request.form['board_num']))
                res.set_cookie("board", request.form['board_num'], expires=datetime.datetime(2023, 3, 1, 0, 0))
                print("set board")
                res.set_cookie("password", request.form['num_password'], expires=datetime.datetime(2023, 3, 1, 0, 0))
                print("set password")
                return res
        cur.close()

    @app.route("/board")
    def board():
        db = get_db()
        cur = db.cursor()
        print(request.args.get('id'))
        board = request.args.get('board')
        cur.execute("SELECT id FROM boards")
        boards = cur.fetchall()
        password=request.cookies.get("password")
        try:
            int(board)
        except:
            return redirect("reset")
        if (int(board),) in boards:
            cur.execute("SELECT name, password, description FROM boards WHERE id=%s", (board,))
            output = cur.fetchone()
            if password==output[1]:
                if request.args.get('id') == None:
                    title = 'Welcome'
                    cur.execute("SELECT * FROM quotes")
                    quote = choice(cur.fetchall())
                    return render_template('main.html', title=title, list=templateList(int(request.args.get('board'))),body='''
                    <h2 style="font-size:10vw;">{title}</h2>
                    <p style="font-size:5vw;">{quote}</p>
                    <p style="font-size:5vw;">{author}</p>
                    <script>
                    sessionStorage.name = "{name}";
                    sessionStorage.link = "/board?board={board}";
                    sessionStorage.description = "{description}"
                    </script>
                    '''.format(title=title, quote=quote[0], author=quote[1], board=board, name = output[0], description = output[2]),control='''
                    <a style="font-size:5vw;" href="/create?board={board}">Create</a>
                    '''.format(title='Welcome', board=request.args.get('board')))

                else:
                    id = request.args.get('id')
                    cur.execute("SELECT title, description FROM posts WHERE id=%s" % ("'" + id +"'"))
                    output=cur.fetchone()
                    title=output[0]
                    description=output[1]
                    return render_template('main.html', title=title, list=templateList(int(request.args.get('board'))), body = '''
                    <h2 style="font-size:10vw;">{title}</h2>
                    <p style="font-size:5vw;">기한: {due}</p>
                    <p style="white-space: pre-wrap; font-size:5vw;">{description}</p>
                    '''.format(title=title, description=description, due=due(title)),control='''
                    <a style="font-size:5vw;" href="/create?board={board}">Create</a>
                    <a style="font-size:5vw;" href="/update?board={board}&id={id}">Update</a>
                    <form action="/delete_process" method="post" onsubmit="return confirm('삭제하시겠습니까?');">
                    <input type="hidden" name="id" value="{id}">
                    <input type="submit" value="Delete">
                    </form>

                '''.format(title=title, board=request.args.get('board'), id=id))
            else:
                res = make_response(
                    '''
                    <script>
                    alert("Incorrect password");
                    window.location.href = '/';
                    </script>''')
                res.set_cookie('board', '', expires=0)
                res.set_cookie('password', '', expires=0)
                return res
                
        else:
            res = make_response(
                '''
                <script>
                alert("The board doesn't exist yet.");
                window.location.href = '/';
                </script>''')
            res.set_cookie('board', '', expires=0)
            res.set_cookie('password', '', expires=0)
            return res
        cur.close()

    @app.route("/create")
    def create():
        db = get_db()
        cur = db.cursor()
        title = 'Create'
        return render_template('main.html', title=title, list=templateList(int(request.args.get('board'))), body = '''
        <form action="/create_process?board={board}" method="post">
        <p><input type="text" name="title" placeholder="Title"></p>
        <label for="due">Due:</label>
        <input type="date" id="due" name="due">
        <p>
          <textarea name="description" placeholder="Description"></textarea>
        </p>
        <div class="row">
          <input type="submit">
        </div>
        </form>
        '''.format(board=request.args.get('board')))
        cur.close()

    @app.route("/create_process", methods = ['POST', 'GET'])
    def create_process():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            
            title=request.form['title']
            description=request.form['description']
            due=request.form['due']
            cur.execute("INSERT INTO posts (title, description, due, board) VALUES (%s, %s, %s, %s)", (title, description, datetime.date.fromisoformat(due), request.args.get('board')))
            db.commit()
            cur.execute("SELECT id FROM posts WHERE title=%s", (request.form['title'],))
            return redirect("/board?board=%s&id=%s" % (request.args.get('board'), cur.fetchall()[-1][0]))
        cur.close()
    @app.route("/update")
    def update():
        db = get_db()
        cur = db.cursor()
        id= request.args.get('id')
        cur.execute("SELECT title, description FROM posts WHERE id=%s" % ("'" + id +"'"))
        output=cur.fetchone()
        title=output[0]
        description=output[1]

        return render_template('main.html', title=title, list=templateList(int(request.args.get('board'))), body = '''
        <form action="/update_process?board={board}" method="post">
        <input type="hidden" name="id" value="{id}">
        <p><input type="text" name="title" placeholder="Title" value="{title}"></p>
        <label for="due">Due:</label>
        <input type="date" id="due" name="due" value={date}>
        <p>
          <textarea name="description" placeholder="Description">{description}</textarea>
        </p>
        <div class="row">
          <input type="submit">
        </div>
        </form>
        '''.format(id=id, title=title, description=description, date=due(title), board=request.args.get('board')), control='<a href="/create">Create</a> <a href="/update?id={title}">Update</a>'.format(title=title))
        cur.close()
    @app.route("/update_process", methods = ['POST', 'GET'])
    def update_process():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            id=request.form['id']
            description=request.form['description']
            title=request.form['title']
            due=request.form['due']
            cur.execute("UPDATE posts SET description=%s, title=%s, due=%s WHERE id=%s", (description, title, datetime.date.fromisoformat(due), id))
            db.commit()
            cur.execute("SELECT board FROM posts WHERE id=%s", (id,))
            return redirect("/board?board=%s&id=%s" % (cur.fetchone()[0], id))
        cur.close()
    @app.route("/delete_process", methods = ['POST', 'GET'])
    def delete_process():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            id=request.form['id']
            #print(title)
            cur.execute("DELETE FROM posts WHERE id=%s", (id,))
            db.commit()
            return redirect("/")
        cur.close()
    
    @app.route("/settings")
    def settings():
        board = request.args.get('board')
        if board != None:
            db = get_db()
            cur = db.cursor()
            id= request.args.get('id')
            cur.execute("SELECT name, description FROM boards WHERE id=%s" % (str(board)))
            output=cur.fetchone()
            title="Settings"
            name=output[0]
            description=output[1]

            return render_template('main.html', title=title, list=templateList(int(request.args.get('board'))), body = '''
            <form action="/updating_settings?board={board}" method="post">
            <input type="hidden" name="id" value="{id}">
            <p><input type="text" name="name" placeholder="Name" value="{name}"></p>
            <p>
            <textarea name="description" placeholder="Description">{description}</textarea>
            </p>
            <div class="row">
            <input type="submit">
            </div>
            </form>
            '''.format(id=board, name=name, description=description, board=request.args.get('board')), control='<a href="/create">Create</a>')
            cur.close()

    @app.route("/updating_settings", methods = ['POST', 'GET'])
    def update_settings():
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            id=request.form['id']
            description=request.form['description']
            title=request.form['name']
            cur.execute("UPDATE boards SET description=%s, name=%s WHERE id=%s", (description, title, id))
            db.commit()
            return redirect("/board?board=%s" % (id))
        cur.close()

    @app.route("/reset")
    def reset():
        res = make_response(redirect("/"))
        res.set_cookie('board', '', expires=0)
        res.set_cookie('password', '', expires=0)
        return res
    return app
app = create_app()
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
