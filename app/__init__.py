# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={
        r"/*": {"origins": app.config['CORS_ORIGINS']}
    })

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import auth_bp

    # モデル登録
    from . import models

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

    app.register_blueprint(access_scope_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(objectives_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(task_access_bp)
    app.register_blueprint(task_core_bp)
    app.register_blueprint(task_export_bp)
    app.register_blueprint(task_order_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(user_bp)

    return app

