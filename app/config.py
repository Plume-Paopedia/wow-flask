"""
Configuration de l'application WoW Flask.

Classes de configuration pour les différents environnements (développement, production, tests).
Toutes les configurations sont basées sur des variables d'environnement.
"""
import os
from typing import Dict, Any, List, Optional
from datetime import timedelta


class Config:
    """Configuration de base pour l'application."""
    
    # Application
    APP_NAME = 'WoW Flask Tutorial Portal'
    APP_VERSION = '1.0.0'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this-in-production'
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    
    # Base de données
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = os.environ.get('SQLALCHEMY_RECORD_QUERIES', 'false').lower() == 'true'
    
    # Sessions et cookies
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT_MINUTES', 120)))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # CSRF Protection
    CSRF_ENABLED = os.environ.get('CSRF_ENABLED', 'true').lower() == 'true'
    WTF_CSRF_ENABLED = CSRF_ENABLED
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@wowflask.fr')
    
    # Cache configuration
    CACHE_TYPE = 'RedisCache' if os.environ.get('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_KEY_PREFIX = 'wowflask:'
    
    # Rate limiting
    RATELIMIT_ENABLED = os.environ.get('REDIS_URL') is not None
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = '1000 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Internationalization
    LANGUAGES = {
        'fr': 'Français',
        'en': 'English'
    }
    BABEL_DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE', 'fr')
    BABEL_DEFAULT_TIMEZONE = os.environ.get('TIMEZONE', 'Europe/Paris')
    
    # Battle.net OAuth
    OAUTH_ENABLE_BNET = os.environ.get('OAUTH_ENABLE_BNET', 'false').lower() == 'true'
    BATTLE_NET_CLIENT_ID = os.environ.get('BATTLE_NET_CLIENT_ID')
    BATTLE_NET_CLIENT_SECRET = os.environ.get('BATTLE_NET_CLIENT_SECRET') 
    BATTLE_NET_REDIRECT_URI = os.environ.get('BATTLE_NET_REDIRECT_URI')
    BATTLE_NET_REGION = os.environ.get('BATTLE_NET_REGION', 'eu')
    
    # File uploads
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 200)) * 1024 * 1024
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_UPLOAD_EXTENSIONS = set(
        os.environ.get('ALLOWED_UPLOAD_EXT', 'jpg,jpeg,png,webp,gif,mp4,webm,pdf').split(',')
    )
    
    # S3 Configuration (optionnel)
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_REGION = os.environ.get('S3_REGION', 'eu-west-3')
    
    # Search configuration
    SEARCH_BACKEND = os.environ.get('SEARCH_BACKEND', 'sqlite_fts')  # sqlite_fts, pg, meilisearch
    MEILI_URL = os.environ.get('MEILI_URL', 'http://localhost:7700')
    MEILI_MASTER_KEY = os.environ.get('MEILI_MASTER_KEY')
    
    # Features toggles
    ENABLE_SIGNUP = os.environ.get('ENABLE_SIGNUP', 'true').lower() == 'true'
    ENABLE_INVITE_ONLY = os.environ.get('ENABLE_INVITE_ONLY', 'false').lower() == 'true'
    AUTO_MODERATION = os.environ.get('AUTO_MODERATION', 'true').lower() == 'true'
    
    # Pagination
    DEFAULT_PER_PAGE = int(os.environ.get('DEFAULT_PER_PAGE', 20))
    MAX_PER_PAGE = int(os.environ.get('MAX_PER_PAGE', 100))
    
    # Celery (tâches asynchrones)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    # Analytics (optionnel)
    PLAUSIBLE_DOMAIN = os.environ.get('PLAUSIBLE_DOMAIN')
    PLAUSIBLE_SCRIPT_URL = os.environ.get('PLAUSIBLE_SCRIPT_URL', 'https://plausible.io/js/script.js')
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Sécurité
    TRUST_PROXY = True  # Pour Railway, Render, etc.
    SECURE_COOKIES = os.environ.get('SECURE_COOKIES', 'false').lower() == 'true'
    
    # Configuration Talisman (sécurité)
    TALISMAN_CONFIG = {
        'force_https': False,  # Géré par le reverse proxy
        'strict_transport_security': True,
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': [
                "'self'", 
                "'unsafe-inline'",  # Pour Alpine.js inline
                "https://unpkg.com",  # CDN pour Tailwind/Alpine/HTMX
                "https://cdn.jsdelivr.net",
            ],
            'style-src': [
                "'self'", 
                "'unsafe-inline'",  # Pour Tailwind
                "https://unpkg.com",
                "https://cdn.jsdelivr.net",
            ],
            'img-src': [
                "'self'", 
                "data:",
                "https:",  # Pour les images externes (avatars, covers)
            ],
            'font-src': [
                "'self'",
                "https://fonts.gstatic.com",
            ],
            'media-src': [
                "'self'",
                "https:",  # Pour les vidéos YouTube/Vimeo
            ],
            'frame-src': [
                "https://www.youtube.com",
                "https://player.vimeo.com",
            ],
        },
        'referrer_policy': 'strict-origin-when-cross-origin',
    }

    @staticmethod
    def init_app(app) -> None:
        """Initialisation spécifique à la configuration."""
        pass


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Base de données SQLite par défaut
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/app.db'
    
    # Désactiver la sécurité stricte en dev
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SECURE_COOKIES = False
    
    # Cache simple en mémoire si pas de Redis
    CACHE_TYPE = 'RedisCache' if os.environ.get('REDIS_URL') else 'SimpleCache'
    
    # Rate limiting plus permissif
    RATELIMIT_DEFAULT = '10000 per hour'
    
    # Pas de CSP strict en développement  
    TALISMAN_CONFIG = {
        'force_https': False,
        'strict_transport_security': False,
        'content_security_policy': False,  # Désactivé pour plus de flexibilité
    }
    
    # Debug toolbar
    DEBUG_TB_ENABLED = os.environ.get('FLASK_DEBUG_TOOLBAR_ENABLED', 'true').lower() == 'true'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    @staticmethod
    def init_app(app) -> None:
        """Initialisation pour le développement."""
        # Activer le debug toolbar si demandé
        if app.config['DEBUG_TB_ENABLED']:
            try:
                from flask_debugtoolbar import DebugToolbarExtension
                DebugToolbarExtension(app)
            except ImportError:
                pass


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Base de données PostgreSQL par défaut
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/wowflask'
    
    # Sécurité stricte
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SECURE_COOKIES = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Forcer HTTPS et sécurité stricte
    TALISMAN_CONFIG = Config.TALISMAN_CONFIG.copy()
    TALISMAN_CONFIG.update({
        'force_https': True,
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,  # 1 an
    })
    
    @staticmethod
    def init_app(app) -> None:
        """Initialisation pour la production."""
        # Configuration de logging pour la production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # Logging vers fichier
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/wowflask.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('WoW Flask startup')


class TestingConfig(Config):
    """Configuration pour les tests."""
    
    TESTING = True
    FLASK_ENV = 'testing'
    
    # Base de données en mémoire pour les tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Désactiver la sécurité pour les tests
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    
    # Cache null pour les tests
    CACHE_TYPE = 'NullCache'
    
    # Pas de rate limiting en test
    RATELIMIT_ENABLED = False
    
    # Pas de sécurité stricte
    TALISMAN_CONFIG = {
        'force_https': False,
        'strict_transport_security': False,
        'content_security_policy': False,
    }


# Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}