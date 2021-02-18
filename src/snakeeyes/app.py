from flask import Flask

from src.snakeeyes.blueprints.page import page


def create_app():
    """
    Create a Flask applicatio using the app factory pattern.

    :return: Flask app
    """
    # app = Flask(__name__, instance_relative_config=True)
    app = Flask(__name__, instance_path="/snakeeyes")

    app.config.from_object("src.config.settings")
    app.config.from_pyfile("../instance/settings.py", silent=False) # instance settings

    app.register_blueprint(page)

    return app
