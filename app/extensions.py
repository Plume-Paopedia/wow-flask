"""
Extensions Flask pour l'application WoW Flask.

Ce module centralise l'initialisation de toutes les extensions Flask utilisées.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mailman import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from authlib.integrations.flask_client import OAuth


# Base de données
db = SQLAlchemy()
migrate = Migrate()

# Authentification
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# Email
mail = Mail()

# Cache
cache = Cache()

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Internationalisation
babel = Babel()

# Protection CSRF
csrf = CSRFProtect()

# OAuth (Battle.net)
oauth = OAuth()

# Sécurité (headers, CSP, etc.)
talisman = Talisman()


@login_manager.user_loader
def load_user(user_id: str):
    """Charge un utilisateur depuis la session."""
    from app.models.user import User
    return User.query.get(int(user_id))


@babel.localeselector
def get_locale():
    """Sélectionne la locale pour l'utilisateur."""
    from flask import request, session, current_app
    from flask_login import current_user
    
    # 1. Locale forcée par l'utilisateur (URL ou session)
    if 'language' in session:
        return session['language']
    
    # 2. Locale de l'utilisateur connecté
    if current_user.is_authenticated and hasattr(current_user, 'locale'):
        return current_user.locale
    
    # 3. Locale du navigateur
    supported_languages = list(current_app.config['LANGUAGES'].keys())
    return request.accept_languages.best_match(supported_languages) or \
           current_app.config['BABEL_DEFAULT_LOCALE']


# Configuration des extensions qui nécessitent l'app context
def init_oauth_providers(app):
    """Initialise les providers OAuth."""
    if app.config.get('OAUTH_ENABLE_BNET'):
        # Configuration Battle.net OAuth
        region = app.config.get('BATTLE_NET_REGION', 'eu')
        
        # URLs par région
        oauth_urls = {
            'us': {
                'authorize_url': 'https://us.battle.net/oauth/authorize',
                'access_token_url': 'https://us.battle.net/oauth/token',
                'userinfo_url': 'https://us.battle.net/oauth/userinfo',
            },
            'eu': {
                'authorize_url': 'https://eu.battle.net/oauth/authorize', 
                'access_token_url': 'https://eu.battle.net/oauth/token',
                'userinfo_url': 'https://eu.battle.net/oauth/userinfo',
            },
            'kr': {
                'authorize_url': 'https://kr.battle.net/oauth/authorize',
                'access_token_url': 'https://kr.battle.net/oauth/token', 
                'userinfo_url': 'https://kr.battle.net/oauth/userinfo',
            },
        }
        
        region_urls = oauth_urls.get(region, oauth_urls['eu'])
        
        oauth.register(
            name='battlenet',
            client_id=app.config['BATTLE_NET_CLIENT_ID'],
            client_secret=app.config['BATTLE_NET_CLIENT_SECRET'],
            client_kwargs={'scope': 'openid'},
            authorize_url=region_urls['authorize_url'],
            access_token_url=region_urls['access_token_url'],
            userinfo_endpoint=region_urls['userinfo_url'],
        )