"""
API Blueprint pour l'application WoW Flask.
"""
from flask import Blueprint

# Créer le blueprint API
api_bp = Blueprint('api', __name__)

# TODO: Configurer Flask-Smorest pour OpenAPI
# from flask_smorest import Api
# api = Api()

# Import des resources
# from .resources import tutorials, auth, categories, tags, comments