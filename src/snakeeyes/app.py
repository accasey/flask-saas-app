import os
import sys


from flask import Flask

# print(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# print(sys.path)


from snakeeyes.blueprints.page import page


def create_app(settings_override=None):
    """
    Create a Flask applicatio using the app factory pattern.

    :return: Flask app
    """
    # app = Flask(__name__, instance_relative_config=True)
    app = Flask(__name__, instance_path="/snakeeyes")

    app.config.from_object("config.settings")
    app.config.from_pyfile("../instance/settings.py", silent=False)  # instance settings

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page)

    return app
