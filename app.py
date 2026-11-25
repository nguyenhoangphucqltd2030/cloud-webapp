import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Cấu hình kết nối MariaDBMySQL từ biến môi trường
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = fmysql+pymysql{db_user}{db_pass}@{db_host}{db_name}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Bảng Người dùng
class User(db.Model)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# Bảng Đối tượng quản lý (Công việc  Ghi chú)
class Task(db.Model)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='Đang làm')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- ROUTES XÁC THỰC ---
@app.route('register', methods=['GET', 'POST'])
def register()
    if request.method == 'POST'
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first()
            flash('Tên đăng nhập đã tồn tại!')
            return redirect(url_for('register'))
        
        # Băm mật khẩu trước khi lưu vào CSDL
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công! Hãy đăng nhập.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('login', methods=['GET', 'POST'])
def login()
    if request.method == 'POST'
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password)
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

@app.route('logout')
def logout()
    session.clear()
    return redirect(url_for('login'))

# --- ROUTES CRUD ĐỐI TƯỢNG ---
@app.route('')
def index()
    if 'user_id' not in session
        return redirect(url_for('login'))
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', tasks=tasks, username=session['username'])

@app.route('add', methods=['POST'])
def add_task()
    if 'user_id' not in session
        return redirect(url_for('login'))
    title = request.form['title']
    if title
        new_task = Task(title=title, user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('editintid', methods=['POST'])
def edit_task(id)
    if 'user_id' not in session
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    if task.user_id == session['user_id']
        task.title = request.form['title']
        task.status = request.form['status']
        db.session.commit()
    return redirect(url_for('index'))

@app.route('deleteintid')
def delete_task(id)
    if 'user_id' not in session
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    if task.user_id == session['user_id']
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__'
    with app.app_context()
        db.create_all()
    app.run(host='127.0.0.1', port=5000)