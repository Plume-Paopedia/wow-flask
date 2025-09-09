"""
Modèle Invite pour le système d'invitations.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import secrets
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Invite(db.Model):
    """Modèle pour les invitations d'inscription."""
    
    __tablename__ = 'invite'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Code unique d'invitation
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Email spécifique (optionnel)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Rôle à attribuer lors de l'acceptation
    role_on_accept: Mapped[str] = mapped_column(String(50), default='member', nullable=False)
    
    # Utilisateur qui a utilisé cette invitation (optionnel)
    used_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)
    
    # Créateur de l'invitation
    created_by_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relations
    used_by: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[used_by_id],
        post_update=True
    )
    
    created_by: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[created_by_id],
        post_update=True
    )
    
    # Index pour les performances
    __table_args__ = (
        Index('ix_invite_code_expires', 'code', 'expires_at'),
        Index('ix_invite_email_expires', 'email', 'expires_at'),
        Index('ix_invite_creator', 'created_by_id'),
    )
    
    def __repr__(self) -> str:
        return f'<Invite {self.code}>'
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si l'invitation a expiré."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_used(self) -> bool:
        """Vérifie si l'invitation a été utilisée."""
        return self.used_by_id is not None
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si l'invitation est valide (non expirée et non utilisée)."""
        return not self.is_expired and not self.is_used
    
    @property
    def invitation_url(self) -> str:
        """Retourne l'URL d'invitation."""
        from flask import current_app
        base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
        return f"{base_url}/auth/signup?invite={self.code}"
    
    def use_invite(self, user_id: int) -> None:
        """Marque l'invitation comme utilisée."""
        self.used_by_id = user_id
        self.used_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """Convertit l'invitation en dictionnaire."""
        data = {
            'id': self.id,
            'code': self.code,
            'email': self.email,
            'role_on_accept': self.role_on_accept,
            'is_expired': self.is_expired,
            'is_used': self.is_used,
            'is_valid': self.is_valid,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'invitation_url': self.invitation_url,
        }
        
        if include_relations:
            data.update({
                'created_by': self.created_by.to_dict() if self.created_by else None,
                'used_by': self.used_by.to_dict() if self.used_by else None,
            })
        
        return data
    
    @staticmethod
    def generate_code(length: int = 16) -> str:
        """Génère un code d'invitation unique."""
        while True:
            code = secrets.token_urlsafe(length)[:length].upper()
            
            # Vérifier l'unicité
            if not Invite.query.filter_by(code=code).first():
                return code
    
    @staticmethod
    def create_invite(
        created_by_id: int,
        email: Optional[str] = None,
        role_on_accept: str = 'member',
        expires_in_days: int = 7
    ) -> 'Invite':
        """Crée une nouvelle invitation."""
        invite = Invite(
            code=Invite.generate_code(),
            email=email,
            role_on_accept=role_on_accept,
            created_by_id=created_by_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        )
        
        db.session.add(invite)
        db.session.commit()
        return invite
    
    @staticmethod
    def get_by_code(code: str) -> Optional['Invite']:
        """Récupère une invitation par son code."""
        return Invite.query.filter_by(code=code).first()
    
    @staticmethod
    def get_valid_by_code(code: str) -> Optional['Invite']:
        """Récupère une invitation valide par son code."""
        invite = Invite.get_by_code(code)
        return invite if invite and invite.is_valid else None
    
    @staticmethod
    def get_by_email(email: str) -> List['Invite']:
        """Récupère les invitations pour un email spécifique."""
        return Invite.query.filter_by(email=email)\
            .order_by(Invite.created_at.desc()).all()
    
    @staticmethod
    def get_valid_by_email(email: str) -> Optional['Invite']:
        """Récupère une invitation valide pour un email."""
        invites = Invite.query.filter_by(email=email)\
            .filter(Invite.expires_at > datetime.now(timezone.utc))\
            .filter(Invite.used_by_id.is_(None))\
            .order_by(Invite.created_at.desc())\
            .all()
        
        return invites[0] if invites else None
    
    @staticmethod
    def get_created_by(user_id: int, limit: Optional[int] = None) -> List['Invite']:
        """Récupère les invitations créées par un utilisateur."""
        query = Invite.query.filter_by(created_by_id=user_id)\
            .order_by(Invite.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def cleanup_expired() -> int:
        """Supprime les invitations expirées non utilisées."""
        expired_invites = Invite.query.filter(
            Invite.expires_at < datetime.now(timezone.utc),
            Invite.used_by_id.is_(None)
        ).all()
        
        count = len(expired_invites)
        for invite in expired_invites:
            db.session.delete(invite)
        
        db.session.commit()
        return count
    
    @staticmethod
    def get_stats() -> Dict[str, int]:
        """Récupère les statistiques des invitations."""
        total = Invite.query.count()
        used = Invite.query.filter(Invite.used_by_id.isnot(None)).count()
        expired = Invite.query.filter(
            Invite.expires_at < datetime.now(timezone.utc),
            Invite.used_by_id.is_(None)
        ).count()
        valid = total - used - expired
        
        return {
            'total': total,
            'used': used,
            'expired': expired,
            'valid': valid
        }