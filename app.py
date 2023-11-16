import random
import os
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
import time
import config
from decorators import login_limit

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
@login_limit
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

# Decorators wrap the original function bottom to top
# When applying further decorators, always remember that the route() decorator is the outermost.
# If you apply first (namely, you put other decorators outer than route()), it adds a URL rule for the original function (without the login decorator). The login decorator wraps the function, but route() has already stored the original unwrapped version, so the wrapping has no effect.

# Issue Details
@app.route('/issue/<Ino>', methods=['GET', 'POST'])
@login_limit
def issue_detail(Ino):
    if request.method == 'GET':
        try:
            if request.method == 'GET':
                cur = db.cursor()
                sql = "select Issue.title from Issue where Ino = '%s'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                issue_title = cur.fetchone()[0] # because cur.fetchone() returns a list (even if there is only one element)
                sql = "select UserInformation.nickname,Comment.comment,Comment.comment_time,Comment.Cno from Comment,UserInformation where Comment.email = UserInformation.email and Ino = '%s'" % Ino
                db.ping(reconnect=True)
                cur.execute(sql)
                comment = cur.fetchall()
                cur.close()
                # return view with parameters
                return render_template('issue_detail.html', Ino=Ino, issue_title=issue_title, comment=comment)
        except Exception as e:
            raise e

    if request.method == 'POST':
        Ino = request.values.get('Ino')
        email = session.get('email')
        comment = request.values.get('editorValue')
        comment_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = db.cursor()
            sql = "select max(Cno) from Comment where Ino = '%s' " % Ino
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            Cno = int(result[0]) + 1
            Cno = str(Cno)
            sql = "insert into Comment(Cno, Ino, comment, comment_time, email) VALUES ('%s','%s','%s','%s','%s')" % (
            Cno, Ino, comment, comment_time, email)
            cur.execute(sql)
            db.commit()
            cur.close()
            return redirect(url_for('issue_detail',Ino = Ino))
        except Exception as e:
            raise e

# Personal Center
@app.route('/personal')
@login_limit
def personal():
    if request.method == 'GET':
        email = session.get('email')
        try:
            cur = db.cursor()
            sql = "select email, nickname, type, create_time, phone from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            personal_info = cur.fetchone()
        except Exception as e:
            print('Exception:', e)
            raise e
        return render_template('personal.html',personal_info = personal_info)

# Change Password
@app.route('/change_password',methods=['GET','POST'])
@login_limit
def change_password():
    if request.method == 'GET':
        return render_template('change_password.html')
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')
        if not all([old_password,new_password1,new_password2]):
            flash("Incomplete information!")
            return render_template('change_password.html')
        if new_password1 != new_password2:
            flash("The two new passwords are inconsistent!")
            return render_template('change_password.html')
        email = session.get('email')
        try:
            cur = db.cursor()
            sql = "select password from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            password = cur.fetchone()[0]
            if check_password_hash(password,old_password):
                password = generate_password_hash(new_password1, method="pbkdf2:sha256", salt_length=8)
                sql = "update UserInformation set password = '%s' where email = '%s'" % (password,email)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
                return render_template('index.html')
            else:
                flash("The old password is wrong!")
                return render_template('change_password.html')
        except Exception as e:
            raise e

# Check your issues
@app.route('/show_issue')
@login_limit
def show_issue():
    if request.method == 'GET':
        email = session.get('email')
        try:
            cur = db.cursor()
            sql = "select ino, email, title, issue_time from Issue where email = '%s' order by issue_time desc" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            issue_detail = cur.fetchall()
        except Exception as e:
            print('Exception:', e)
            raise e
        return render_template('show_issue.html',issue_detail=issue_detail)
    
# Generate 120-bit random id for security
def gengenerateFno():
    re = ""
    for i in range(120):
        re += chr(random.randint(65, 90))
    return re

# 资源上传页面
@app.route('/post_file',methods=['GET','POST'])
@login_limit
def post_file():
    if request.method == 'GET':
        return render_template('post_file.html')
    if request.method == 'POST':
        email = session.get('email')
        upload_file = request.files.get('file')
        filename = request.form.get('filename')
        file_info = request.form.get('file_info')
        file_path = 'store'
        file_time = time.strftime("%Y-%m-%d %H:%M:%S")
        Fno = gengenerateFno()
        try:
            cur = db.cursor()
            sql = "select * from Files where Fno = '%s'" % Fno
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            # 如果result不为空，即该Fno已存在时，一直生成随机的Fno，只到该数据库中不存在
            while result is not None:
                Fno = gengenerateFno()
                sql = "select * from Files where Fno = '%s'" % Fno
                db.ping(reconnect=True)
                cur.execute(sql)
                result = cur.fetchone()
            # 获取文件的后缀
            upload_name = str(upload_file.filename)
            houzhui = upload_name.split('.')[-1]
            # 保存在本地的名字为生成的Fno+文件后缀，同时修改Fno的值
            Fno = Fno+"."+houzhui
            # 保存文件到我们的服务器中
            upload_file.save(os.path.join(file_path,Fno))
            # 将文件信息存储到数据库中
            sql = "insert into Files(Fno, filename, file_info, file_time,email) VALUES ('%s','%s','%s','%s','%s')" % (Fno,filename,file_info,file_time,email)
            db.ping(reconnect=True)
            cur.execute(sql)
            db.commit()
            cur.close()
            return redirect(url_for('source'))
        except Exception as e:
            raise e

# 资源专区
@app.route('/source')
def source():
    if request.method == 'GET':
        try:
            cur = db.cursor()
            sql = "select Fno,filename,file_info,file_time,nickname from Files,UserInformation where Files.email = UserInformation.email"
            db.ping(reconnect=True)
            cur.execute(sql)
            files = cur.fetchall()
            cur.close()
            return render_template('source.html',files = files)
        except Exception as e:
            raise e

# 在线查看文件
@app.route('/online_file/<Fno>')
def online_file(Fno):
    return send_from_directory(os.path.join('store'), Fno)

# 文件下载功能
@app.route('/download/<Fno>')
def download(Fno):
    return send_file(os.path.join('store') + "/" + Fno, as_attachment=True)

if __name__ == '__main__':
    app.run()