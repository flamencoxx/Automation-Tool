# import pytest
# from app import app as flask_app, db
#
#
# @pytest.fixture
# def app():
#     flask_app.config.update({
#         "TESTING": True,
#         "SQLALCHEMY_DATABASE_URI": "postgresql://username:password@localhost/test_db"
#     })
#     with flask_app.app_context():
#         db.create_all()
#     yield flask_app
#     with flask_app.app_context():
#         db.drop_all()
#
#
# @pytest.fixture
# def client(app):
#     return app.test_client()
#
#
# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()
