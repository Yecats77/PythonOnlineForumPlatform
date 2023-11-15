import random
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
import time
import config

app = Flask(__name__)

# import config
app.config.from_object(config)


# Homepage
@app.route('/')
def index():
    return render_template('index.html')


# Register Page
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')
        phone = request.form.get('phone')
        if not all([email,nickname,password_1,password_2,phone]):
            flash("The information is incomplete, please fill in the information completely")
            return render_template('register.html')
        if password_1 != password_2:
            flash("The passwords filled in twice are inconsistent!")
            return render_template('register.html')
        password = generate_password_hash(password_1, method="pbkdf2:sha256", salt_length=8)
        try:
            cur = db.cursor()
            sql = "select * from UserInformation where email = '%s'"%email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result is not None:
                flash("This email already exists!")
                return render_template('register.html')
            else:
                create_time = time.strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into UserInformation(email, nickname, password, type, create_time, phone) VALUES ('%s','%s','%s','0','%s','%s')" %(email,nickname,password,create_time,phone)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
                return redirect(url_for('index'))
        except Exception as e:
            raise e

# Login Page
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # print('email', email, 'password', password)
        if not all([email,password]):
            flash("Please fill in the information completely")
            return render_template('login.html')
        try:
            cur = db.cursor()
            sql = "select password from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            # print('result', result)
            if result is None:
                flash("This user does not exist")
                return render_template('login.html')
            if check_password_hash(result[0],password):
                session['email'] = email
                # session.modified = True
                session.permanent = True
                return redirect(url_for('index'))
            else:
                flash("Wrong password!")
                return render_template('login.html')
        except Exception as e:
            raise e

# Maintain Login Status
@app.context_processor
def login_status():
    # Obtain email from session
    email = session.get('email')
    # If there is email info, it proves that you have logged in. Get the login name and user type from the DB to return to the global.
    if email:
        try:
            cur = db.cursor()
            sql = "select nickname,type from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result:
                return {'email': email,'nickname': result[0] ,'user_type': result[1]}
                # return render_template('register.html', email=email,nickname=result[0] ,user_type=result[1])
        except Exception as e:
            raise e
    # If no email information, you are not logged in and return NULL.
    return {}

# User Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for(('index')))

# Generate 128-bit random id for security
def gengenerateID():
    re = ""
    for i in range(128):
        re += chr(random.randint(65, 90))
    return re

# Post Issue
@app.route('/post_issue', methods=['GET', 'POST'])
def post_issue():
    if request.method == 'GET':
        return render_template('post_issue.html')
    if request.method == 'POST':
        # Get issue info from editor 
        title = request.form.get('title')
        comment = request.form.get('editorValue')
        email = session.get('email')
        issue_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = db.cursor()
            Ino = gengenerateID()
            sql = "select * from Issue where Ino = '%s'" % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            # If result is not null, i.e. current id is existing, continuously generate id until it is unique
            while result is not None:
                Ino = gengenerateID()
                sql = "select * from Issue where Ino = '%s'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()

            sql = "insert into Issue(Ino, email, title, issue_time) VALUES ('%s','%s','%s','%s')" % (Ino, email, title, issue_time)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            sql = "insert into Comment(Cno, Ino, comment, comment_time, email) VALUES ('%s','%s','%s','%s','%s')" % ('1', Ino, comment, issue_time, email)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
            return redirect(url_for('formula'))
        except Exception as e:
            raise e

# Forum Page
@app.route('/formula')
def formula():
    if request.method == 'GET':
        try:
            cur = db.cursor()
            sql = "select Issue.Ino, Issue.email, UserInformation.nickname, issue_time, Issue.title, Comment.comment " + "from Issue, UserInformation, Comment " + "where Issue.email = UserInformation.email and Issue.Ino = Comment.Ino and Cno = '1' order by issue_time DESC "
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_information = cur.fetchall()
            cur.close()
            return render_template('formula.html', issue_information = issue_information)
        except Exception as e:
            raise e





if __name__ == '__main__':
    app.run()
