"""
Modèles SQLAlchemy pour l'application WoW Flask.

Ce module expose tous les modèles de l'application pour faciliter les imports.
"""

from .user import User
from .role import Role
from .tutorial import Tutorial
from .category import Category
from .tag import Tag
from .comment import Comment
from .rating import Rating
from .favorite import Favorite
from .attachment import Attachment
from .moderation import ModerationLog
from .audit import AuditEvent
from .invite import Invite

__all__ = [
    'User',
    'Role', 
    'Tutorial',
    'Category',
    'Tag',
    'Comment',
    'Rating',
    'Favorite', 
    'Attachment',
    'ModerationLog',
    'AuditEvent',
    'Invite',
]