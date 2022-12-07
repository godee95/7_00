# flask, flask-jwt-extended, pymysql 라이브러리 설치
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
from datetime import datetime, timedelta
import json
import jwt

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'

#! 메인 페이지


@app.route('/')
def home():
    return render_template('index.html')

#! 로그인 페이지


@app.route('/login')
def login():
    return render_template('login.html')

#! 로그인


@app.route('/users/login', methods=['POST'])
def log_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT *
		FROM users u
		where u.email = %s
		"""

    curs.execute(sql, email_receive)

    users_result = curs.fetchall()

    # json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()

    if users_result[0][2] != password_receive:
        msg = "비밀번호가 일치하지 않습니다. 다시 로그인해주세요."
        return jsonify({'result': 'fail', 'msg': msg})

    else:
        # 토큰 발행, id, payload, 시크릿키가 필요
        payload = {
            'id': email_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60*60*24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})


#! 게시판 작성 페이지


@app.route('/write_page')
def write_page():
    return render_template('write_page.html')

#! 사용자만 게시판 작성 페이지로 이동


@app.route('/user_only', methods=['POST'])
def move_to_write_page():
    token_receive = request.cookies.get('mytoken')

    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인을 먼저 진행해주세요!!'})

#! 게시글 수정 페이지


@app.route('/write_page_update')
def write_page_update():
    return render_template('write_page_update.html')


#! 게시글 불러오기


@app.route('/posts/list')
def get_post():
    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT title,content,topic,file
		FROM posts p
		"""

    curs.execute(sql)

    post_list = curs.fetchall()

    db.commit()
    db.close()

    return jsonify({'post_list': post_list})

#! 게시글 작성


@app.route("/posts/save", methods=["POST"])
def save_post():
    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']
    file = request.files['file']

    print(request.form)
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		INSERT INTO posts (title,topic,content,file) VALUES (%s,%s,%s,%s)
		"""

    curs.execute(sql, (title, topic, content, save_to))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 작성 완료!'})

# 게시글 업데이트


@app.route('/updatepost', methods=["PUT"])
def update():
    post_id = request.form['post_id']
    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		UPDATE posts SET title = %s, topic = %s, content = %s WHERE post_id = %s
		"""

    curs.execute(sql, (title, topic, content, post_id))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 수정 완료'})


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
