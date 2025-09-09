"""
WoW Flask Tutorial Portal

Application factory pour le portail communautaire de tutoriels World of Warcraft.
"""
from typing import Optional, Dict, Any

from flask import Flask, request, current_app
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import config
from app import extensions
from app.extensions import (
    db, migrate, login_manager, mail, cache, limiter, babel, csrf,
    oauth, talisman
)


def create_app(config_name: Optional[str] = None) -> Flask:
    """Factory pour créer l'application Flask.
    
    Args:
        config_name: Nom de la configuration à utiliser (development, production, testing)
        
    Returns:
        Instance Flask configurée
    """
    app = Flask(__name__)
    
    # Configuration
    if config_name is None:
        config_name = app.config.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Middleware pour les proxys (Railway, Render, etc.)
    if app.config['TRUST_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Gestionnaires d'erreurs
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    # CLI commands
    register_cli_commands(app)
    
    return app


def init_extensions(app: Flask) -> None:
    """Initialise les extensions Flask."""
    # Base de données
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentification
    login_manager.init_app(app)
    
    # Email
    if app.config['MAIL_SERVER']:
        mail.init_app(app)
    
    # Cache
    if app.config['CACHE_TYPE'] != 'NullCache':
        cache.init_app(app)
    
    # Rate limiting
    if app.config['RATELIMIT_ENABLED']:
        limiter.init_app(app)
    
    # Internationalisation
    babel.init_app(app)
    # babel.localeselector(extensions.get_locale)
    
    # Sécurité CSRF
    if app.config['CSRF_ENABLED']:
        csrf.init_app(app)
    
    # OAuth (optionnel)
    if app.config['OAUTH_ENABLE_BNET']:
        oauth.init_app(app)
    
    # Sécurité (headers, CSP, etc.)
    if app.config['FLASK_ENV'] == 'production':
        talisman.init_app(app, **app.config['TALISMAN_CONFIG'])


def register_blueprints(app: Flask) -> None:
    """Enregistre les blueprints de l'application."""
    from app.blueprints.public.routes import bp as public_bp
    from app.blueprints.auth.routes import bp as auth_bp
    from app.blueprints.dashboard.routes import bp as dashboard_bp
    from app.blueprints.admin.routes import bp as admin_bp
    from app.blueprints.api import api_bp
    
    # Pages publiques
    app.register_blueprint(public_bp)
    
    # Authentification
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Tableau de bord utilisateur
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Administration
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # API REST
    app.register_blueprint(api_bp, url_prefix='/api/v1')


def register_error_handlers(app: Flask) -> None:
    """Enregistre les gestionnaires d'erreurs personnalisés."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        from flask import render_template
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        from flask import render_template
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        from flask import render_template
        return render_template('errors/500.html'), 500


def register_context_processors(app: Flask) -> None:
    """Enregistre les context processors globaux."""
    
    @app.context_processor
    def inject_config() -> Dict[str, Any]:
        """Injecte la configuration dans les templates."""
        return {
            'config': current_app.config,
            'app_name': current_app.config['APP_NAME'],
            'app_version': current_app.config.get('APP_VERSION', '1.0.0'),
        }
    
    @app.context_processor 
    def inject_user_counts() -> Dict[str, Any]:
        """Injecte les statistiques globales."""
        try:
            from app.models.user import User
            from app.models.tutorial import Tutorial
            
            return {
                'stats': {
                    'total_users': User.query.count(),
                    'total_tutorials': Tutorial.query.filter_by(status='published').count(),
                }
            }
        except Exception:
            return {'stats': {'total_users': 0, 'total_tutorials': 0}}


def register_cli_commands(app: Flask) -> None:
    """Enregistre les commandes CLI personnalisées."""
    
    @app.cli.command()
    def init_db():
        """Initialise la base de données."""
        from flask_migrate import init, migrate, upgrade
        
        try:
            init()
        except Exception:
            pass  # Migrations déjà initialisées
        
        migrate(message='Initial migration')
        upgrade()
        click.echo('Base de données initialisée.')
    
    @app.cli.command()
    def seed_db():
        """Peuple la base de données avec des données de test."""
        from scripts.seed import seed_database
        seed_database()
        click.echo('Base de données peuplée.')
    
    @app.cli.command()
    def create_admin():
        """Crée un utilisateur administrateur."""
        from app.models.user import User
        from app.models.role import Role
        from app.services.auth import AuthService
        
        email = click.prompt('Email de l\'administrateur')
        password = click.prompt('Mot de passe', hide_input=True, confirmation_prompt=True)
        
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            click.echo('Erreur: Le rôle admin n\'existe pas. Exécutez d\'abord seed_db.')
            return
        
        user = AuthService.create_user(
            email=email,
            password=password,
            username=email.split('@')[0],
            email_verified=True
        )
        user.roles.append(admin_role)
        db.session.commit()
        
        click.echo(f'Administrateur {email} créé avec succès.')


# Imports nécessaires pour les gestionnaires d'erreurs
from flask import render_template
import click