from main import create_app

app = create_app()
with app.app_context():
    from flask import current_app
    redis = current_app.redis