from flask import Flask


def create_app():
    """
    Create a Flask applicatio using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("src.config.settings")
    app.config.from_pyfile("settings.py", silent=True)

    @app.route("/")
    def index():
        """
        Render a Hello World response.

        :return: Flask response
        """
        return "<h1>Hello World<h1>"

    return app
