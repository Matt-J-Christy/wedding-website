"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template, redirect, url_for, request
from app.credentials import username, password
import markdown
import os

app = Flask(__name__, static_url_path='/static/')


# define login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('root'))
    return render_template('login.html', error=error)


@app.route("/home")
def root() -> str:
    data = {}
    data["page_title"] = "Splash Page"

    with open('app/markdown_pages/splash_page.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/our_story')
def our_story() -> str:
    data = {}
    data["page_title"] = "Our Story"

    with open('app/markdown_pages/our_story.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/things_to_do')
def things_to_do() -> str:
    data = {}
    data["page_title"] = "Things to do"

    with open('app/markdown_pages/things_to_do.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/wedding_weekend')
def wedding_weekend() -> str:
    data = {}
    data["page_title"] = "The Wedding Weekend"

    with open('app/markdown_pages/wedding_weekend.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)

# TODO: Get a function that dynamically creates
# static pages rather than hardcoding each page
# @app.route("/<filename>")
# def make_page(title: str, filename: str) -> str:
#     data = {}
#     data["page_title"] = title

#     path = 'app/markdown_pages/' + filename + '.md'

#     with open(path, 'r') as f:
#         text = f.read()
#         data["html"] = markdown.markdown(text)

#     return render_template('index.html', data=data)

# make_page(title='Our Story', filename='our_story')
# post('thing_to_do')
# post('wedding_weekend')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
