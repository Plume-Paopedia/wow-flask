"""
Modèle User pour l'authentification et la gestion des utilisateurs.
"""
from datetime import datetime, timezone
from typing import List, Optional

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


# Table d'association pour les rôles utilisateur (many-to-many)
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """Modèle utilisateur avec authentification et profil."""
    
    __tablename__ = 'user'
    
    # Identifiants
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Vérification email
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Profil utilisateur
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    locale: Mapped[str] = mapped_column(String(5), default='fr', nullable=False)
    
    # Battle.net OAuth (optionnel)
    bnet_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    bnet_battletag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # État du compte
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relations
    roles: Mapped[List["Role"]] = relationship(
        "Role", 
        secondary=user_roles, 
        back_populates="users",
        lazy='selectin'
    )
    
    tutorials: Mapped[List["Tutorial"]] = relationship(
        "Tutorial", 
        back_populates="author", 
        lazy='dynamic'
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="author", 
        lazy='dynamic'
    )
    
    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", 
        back_populates="user", 
        lazy='dynamic'
    )
    
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", 
        back_populates="user", 
        lazy='dynamic'
    )
    
    # Index composites
    __table_args__ = (
        Index('ix_user_email_active', 'email', 'is_active'),
        Index('ix_user_username_active', 'username', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password: str) -> None:
        """Définit le mot de passe hashé."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe."""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name: str) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique."""
        return any(role.name == role_name for role in self.roles)
    
    def can(self, permission: str) -> bool:
        """Vérifie si l'utilisateur a une permission spécifique."""
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.has_role('admin')
    
    @property 
    def is_moderator(self) -> bool:
        """Vérifie si l'utilisateur est modérateur ou admin."""
        return self.has_role('moderator') or self.has_role('admin')
    
    @property
    def is_author(self) -> bool:
        """Vérifie si l'utilisateur peut créer des tutoriels."""
        return self.has_role('author') or self.is_moderator
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage préféré."""
        return self.bnet_battletag or self.username
    
    @property
    def tutorial_count(self) -> int:
        """Nombre de tutoriels publiés par l'utilisateur."""
        return self.tutorials.filter_by(status='published').count()
    
    @property
    def favorite_count(self) -> int:
        """Nombre de tutoriels favoris."""
        return self.favorites.count()
    
    def get_avatar_url(self, size: int = 64) -> str:
        """Retourne l'URL de l'avatar."""
        if self.avatar_url:
            return self.avatar_url
        
        # Avatar par défaut basé sur Gravatar
        import hashlib
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion."""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self, include_email: bool = False) -> dict:
        """Convertit l'utilisateur en dictionnaire pour l'API."""
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.get_avatar_url(),
            'locale': self.locale,
            'tutorial_count': self.tutorial_count,
            'created_at': self.created_at.isoformat(),
            'roles': [role.name for role in self.roles]
        }
        
        if include_email:
            data['email'] = self.email
            data['email_verified'] = self.email_verified
            data['last_login_at'] = self.last_login_at.isoformat() if self.last_login_at else None
        
        return data
    
    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Récupère un utilisateur par son email."""
        return User.query.filter_by(email=email, is_active=True).first()
    
    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        """Récupère un utilisateur par son nom d'utilisateur.""" 
        return User.query.filter_by(username=username, is_active=True).first()
    
    @staticmethod
    def get_by_bnet_id(bnet_id: str) -> Optional['User']:
        """Récupère un utilisateur par son ID Battle.net."""
        return User.query.filter_by(bnet_id=bnet_id, is_active=True).first()