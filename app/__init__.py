# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from flask_smorest import Api 
from dotenv import load_dotenv
from app.extensions import db, login_manager, migrate
import os

def create_app(config_class=Config):
    if os.getenv("PYTEST_CURRENT_TEST"):
        # ✅ pytest実行中ならテスト用.envを読み込む
        env_file = ".env.test"
    else:
        env_file = ".env"
    load_dotenv(env_file, override=True)
    URL_PREFIX = os.getenv('URL_PREFIX')

    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={
        r"/*": {"origins": app.config['CORS_ORIGINS']}
    })

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Swagger/OpenAPI用設定
    app.config['API_TITLE'] = 'Task Progress API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config["OPENAPI_URL_PREFIX"] = URL_PREFIX
    app.config["OPENAPI_JSON_PATH"] = "openapi.json"
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"
    app.config["OPENAPI_REDOC_URL"] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'



    from app.auth import auth_bp

    # モデル登録
    from . import models

    # Flask-SmorestのApiオブジェクト生成
    api = Api(app)


    #Blueprint登録
    from app.routes.access_scope_routes import access_scope_bp
    from app.routes.ai_route import ai_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.company_routes import company_bp
    from app.routes.objectives_route import objectives_bp
    from app.routes.organization_routes import organization_bp
    from app.routes.progress_updates_route import progress_bp
    from app.routes.task_access_route import task_access_bp
    from app.routes.task_core_route import task_core_bp
    from app.routes.task_export_route import task_export_bp
    from app.routes.task_order_route import task_order_bp
    from app.routes.test_routes import test_bp
    from app.routes.user_routes import user_bp

    api.register_blueprint(access_scope_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(ai_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(auth_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(company_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(objectives_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(organization_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(progress_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(task_access_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(task_core_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(task_export_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(task_order_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(test_bp, url_prefix=URL_PREFIX)
    api.register_blueprint(user_bp, url_prefix=URL_PREFIX)

    return app

