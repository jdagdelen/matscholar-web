import os, json
from os import environ
import dash
import dash_auth
import markdown2
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from flask import send_from_directory
from matscholar.rest import Rester, MatScholarRestError

from matscholar_web.view import summary_app, search_app, extract_app, material_search_app

# callbacks
from matscholar_web.callbacks import summary_callbacks, \
    material_search_callbacks, extract_callbacks, search_callbacks

"""
APP CONFIG
"""

app = dash.Dash()
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True
app.title = "matscholar - rediscover materials"

# Authentication
VALID_USERNAME_PASSWORD_PAIRS = [[environ['MATERIALS_SCHOLAR_WEB_USER'],
                                  environ['MATERIALS_SCHOLAR_WEB_PASS']]]
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# loading css files
css_files = ["skeleton.min.css", "matscholar_web.css", ]
stylesheets_links = [html.Link(rel='stylesheet', href='/static/css/' + css) for css in css_files]

"""
VIEW
"""
app_container = html.Div("", id="app_container")

app.layout = html.Div([
    html.Div(stylesheets_links, style={"display": "none"}),
    app_container],
    className='container',
    style={
        "maxWidth": "1600px",
        "height": "100%",
        "width": "100%",
        "padding": "0px 20px"})

"""
CALLBACKS
"""

# callbacks for loading different apps
@app.callback(
    Output('app_container', 'children'),
    [Input('url', 'pathname')])
def display_page(path):
    path = str(path)
    if path.startswith("/explore"):
        return mat2vec_app.serve_layout()
    elif path.startswith("/materials_map"):
        return materials_map_app.layout
    elif path.startswith("/search"):
        return search_app.serve_layout(path)
    elif path.startswith("/summary"):
        return summary_app.serve_layout()
    elif path.startswith("/extract"):
        return extract_app.serve_layout()
    elif path.startswith("/material_search"):
        return material_search_app.serve_layout()
    # elif path.startswith("/journal_suggestion"):
    #     return journal_suggestion_app.layout
    else:
        return search_app.serve_layout(path)


@app.callback(
    Output('app_container', 'children'),
    [Input('url', 'pathname')])
def display_page(path):
    path = str(path)
    return search_app.serve_layout(path)


# setting the static path for loading css files
@app.server.route('/static/css/<path:path>')
def get_stylesheet(path):
    static_folder = os.path.join(os.getcwd(), 'matscholar_web/static/css')
    return send_from_directory(static_folder, path)


# setting the static path for robots.txt
@app.server.route('/robots.txt')
def get_robots():
    static_folder = os.path.join(os.getcwd(), 'matscholar_web/static')
    path = "robots.txt"
    return send_from_directory(static_folder, path)


# setting the static path for about page
@app.server.route('/about')
def get_about():
    return markdown2.markdown_path(os.path.join(os.getcwd(), "README.md"))


search_callbacks.bind(app)
