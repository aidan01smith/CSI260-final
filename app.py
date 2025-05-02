# Import necessary libraries
# sqlite3 for database operations, Flask for web framework, and other utilities
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from stock_tracking import register_stocks_blueprint


# Function to establish a connection to the SQLite database
# Sets row_factory to sqlite3.Row for dictionary-like row access
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Function to retrieve a single post by its ID from the database
# Raises a 404 error if the post doesn't exist
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


# Initialize the Flask application
app = Flask(__name__)

# Configure a secret key for session management and flash messages
app.config['SECRET_KEY'] = 'flask_secret_key'

# Register the stocks blueprint (likely contains additional routes)
register_stocks_blueprint(app)


# Route for the home page that displays all posts
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# Sample hardcoded posts data (note: this isn't used in the current implementation)
posts = [ 
    {
        'title': 'first post',
        'content': 'this is the content of the first post'
    },
    {
        'title': 'second post',
        'content': 'this is the content of the second post'
    }
]


# Route to display a single post by its ID
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


# Route for creating a new post, handles both GET and POST methods
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')  # Show error if title is missing
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect to home page after creation

    return render_template('create.html')  # Show the creation form for GET requests


# Route for editing an existing post, handles both GET and POST methods
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)  # Retrieve the existing post

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')  # Show error if title is missing
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect to home page after update

    return render_template('edit.html', post=post)  # Show the edit form with current post data


# Route for deleting a post, only accepts POST requests
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)  # Retrieve the post to be deleted
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))  # Show success message
    return redirect(url_for('index'))  # Redirect to home page after deletion
