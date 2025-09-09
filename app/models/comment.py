"""
Modèle Comment pour le système de commentaires des tutoriels.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import bleach

from app.extensions import db


class Comment(db.Model):
    """Modèle pour les commentaires des tutoriels."""
    
    __tablename__ = 'comment'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relations
    tutorial_id: Mapped[int] = mapped_column(ForeignKey('tutorial.id'), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Contenu
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Modération
    status: Mapped[str] = mapped_column(
        Enum('visible', 'hidden', 'flagged', name='comment_status'),
        default='visible',
        nullable=False,
        index=True
    )
    
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
    
    # Relations
    tutorial: Mapped["Tutorial"] = relationship(
        "Tutorial", 
        back_populates="comments"
    )
    
    author: Mapped["User"] = relationship(
        "User", 
        back_populates="comments"
    )
    
    # Index pour les performances
    __table_args__ = (
        Index('ix_comment_tutorial_status', 'tutorial_id', 'status'),
        Index('ix_comment_author_created', 'author_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<Comment {self.id} on Tutorial {self.tutorial_id}>'
    
    @property
    def is_visible(self) -> bool:
        """Vérifie si le commentaire est visible."""
        return self.status == 'visible'
    
    @property
    def is_flagged(self) -> bool:
        """Vérifie si le commentaire est signalé."""
        return self.status == 'flagged'
    
    def sanitize_content(self) -> None:
        """Sanitise le contenu HTML du commentaire."""
        # Tags autorisés dans les commentaires (plus restrictif que les tutoriels)
        allowed_tags = [
            'p', 'br', 'strong', 'b', 'em', 'i', 'u', 
            'a', 'code', 'blockquote'
        ]
        
        allowed_attributes = {
            'a': ['href', 'title', 'rel'],
            'code': ['class'],
        }
        
        allowed_protocols = ['http', 'https']
        
        self.content_html = bleach.clean(
            self.content_html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            protocols=allowed_protocols,
            strip=True
        )
    
    def hide(self) -> None:
        """Masque le commentaire."""
        self.status = 'hidden'
    
    def flag(self) -> None:
        """Signale le commentaire pour modération."""
        self.status = 'flagged'
    
    def approve(self) -> None:
        """Approuve le commentaire."""
        self.status = 'visible'
    
    def to_dict(self, include_content: bool = True, include_author: bool = True) -> Dict[str, Any]:
        """Convertit le commentaire en dictionnaire."""
        data = {
            'id': self.id,
            'tutorial_id': self.tutorial_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_content:
            data['content_html'] = self.content_html if self.is_visible else None
        
        if include_author:
            data['author'] = self.author.to_dict() if self.author else None
        
        return data
    
    @staticmethod
    def get_for_tutorial(tutorial_id: int, include_hidden: bool = False) -> List['Comment']:
        """Récupère les commentaires d'un tutoriel."""
        query = Comment.query.filter_by(tutorial_id=tutorial_id)
        
        if not include_hidden:
            query = query.filter_by(status='visible')
        
        return query.order_by(Comment.created_at.asc()).all()
    
    @staticmethod
    def get_flagged() -> List['Comment']:
        """Récupère les commentaires signalés pour modération."""
        return Comment.query.filter_by(status='flagged')\
            .order_by(Comment.created_at.desc()).all()