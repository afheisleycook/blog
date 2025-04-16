from flask import Flask, render_template, redirect, request, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Create users table for login functionality
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Create posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        ''')
        conn.commit()

# Route for the home page
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts')
        posts = cursor.fetchall()
        return render_template('home.html', posts=posts)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect('/')
            else:
                flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Route for registering a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect('/login')
            except sqlite3.IntegrityError:
                flash('Username already exists', 'error')
    return render_template('register.html')

# Route for adding a new post
@app.route('/add', methods=['POST'])
def add_post():
    if 'user_id' not in session:
        return redirect('/login')
    content = request.form['content']
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (content) VALUES (?)', (content,))
        conn.commit()
    return redirect('/')

# Route for deleting a post
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
    return redirect('/')

# Route for editing a post
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            content = request.form['content']
            cursor.execute('UPDATE posts SET content = ? WHERE id = ?', (content, post_id))
            conn.commit()
            return redirect('/')
        else:
            cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
            post = cursor.fetchone()
            return render_template('edit.html', post=post)

# Route for viewing a post
@app.route('/view/<int:post_id>')
def view_post(post_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = cursor.fetchone()
        return render_template('view.html', post=post)

init_db()