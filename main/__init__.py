from flask import Flask
from flask_cors import CORS
from main.config import Config
from redis import Redis
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os

jwt = JWTManager()
config = Config()
redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
    )
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt.init_app(app)

    db.init_app(app)
    db.app = app

    from main.routes.config_routes import config_bp
    from main.routes.scoreboard_routes import scoreboard_bp
    from main.routes.streaming_routes import streaming_bp

    app.register_blueprint(config_bp)
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(streaming_bp)

    CORS(app)

    return app

app = create_app()
