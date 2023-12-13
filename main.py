"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template
import markdown

app = Flask(__name__)
app.app_context().push()


@app.route("/")
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
