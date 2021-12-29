'''
Description:


by: Joel A. Gongora
date:
'''

from flask_app import my_app

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from app import dash_app

# @my_app.route('/snotel_dashboard')
# def render_dashboard():
#     return flask.redirect('/snotel_dashboard')

# application = DispatcherMiddleware(
#     my_app, {
#         '/snotel_dashboard': dash_app.server,
#     }
# )


if __name__ == '__main__':
    my_app.secret_key='secret123'
    run_simple('localhost', 8050, my_app) 
