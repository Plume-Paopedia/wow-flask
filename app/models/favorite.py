"""
Modèle Favorite pour le système de favoris des tutoriels.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Favorite(db.Model):
    """Modèle pour les favoris des utilisateurs."""
    
    __tablename__ = 'favorite'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relations
    tutorial_id: Mapped[int] = mapped_column(ForeignKey('tutorial.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relations
    tutorial: Mapped["Tutorial"] = relationship(
        "Tutorial", 
        back_populates="favorites"
    )
    
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="favorites"
    )
    
    # Contraintes
    __table_args__ = (
        # Un utilisateur ne peut mettre en favori qu'une fois par tutoriel
        UniqueConstraint('tutorial_id', 'user_id', name='unique_user_tutorial_favorite'),
        Index('ix_favorite_user_created', 'user_id', 'created_at'),
        Index('ix_favorite_tutorial_created', 'tutorial_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<Favorite User {self.user_id} → Tutorial {self.tutorial_id}>'
    
    def to_dict(self, include_tutorial: bool = False, include_user: bool = False) -> Dict[str, Any]:
        """Convertit le favori en dictionnaire."""
        data = {
            'id': self.id,
            'tutorial_id': self.tutorial_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_tutorial:
            data['tutorial'] = self.tutorial.to_dict() if self.tutorial else None
        
        if include_user:
            data['user'] = self.user.to_dict() if self.user else None
        
        return data
    
    @staticmethod
    def is_favorite(user_id: int, tutorial_id: int) -> bool:
        """Vérifie si un tutoriel est en favori pour un utilisateur."""
        return Favorite.query.filter_by(
            user_id=user_id, 
            tutorial_id=tutorial_id
        ).first() is not None
    
    @staticmethod
    def toggle_favorite(user_id: int, tutorial_id: int) -> tuple[bool, str]:
        """Active/désactive un favori. Retourne (is_favorite, message)."""
        existing_favorite = Favorite.query.filter_by(
            user_id=user_id, 
            tutorial_id=tutorial_id
        ).first()
        
        if existing_favorite:
            # Supprimer le favori
            db.session.delete(existing_favorite)
            db.session.commit()
            return False, "Tutoriel retiré des favoris"
        else:
            # Ajouter aux favoris
            favorite = Favorite(
                user_id=user_id,
                tutorial_id=tutorial_id
            )
            db.session.add(favorite)
            db.session.commit()
            return True, "Tutoriel ajouté aux favoris"
    
    @staticmethod
    def add_favorite(user_id: int, tutorial_id: int) -> Optional['Favorite']:
        """Ajoute un tutoriel aux favoris."""
        # Vérifier que le favori n'existe pas déjà
        if Favorite.is_favorite(user_id, tutorial_id):
            return None
        
        favorite = Favorite(
            user_id=user_id,
            tutorial_id=tutorial_id
        )
        db.session.add(favorite)
        db.session.commit()
        return favorite
    
    @staticmethod
    def remove_favorite(user_id: int, tutorial_id: int) -> bool:
        """Retire un tutoriel des favoris."""
        favorite = Favorite.query.filter_by(
            user_id=user_id, 
            tutorial_id=tutorial_id
        ).first()
        
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def get_user_favorites(user_id: int, limit: Optional[int] = None) -> List['Favorite']:
        """Récupère les favoris d'un utilisateur."""
        query = Favorite.query.filter_by(user_id=user_id)\
            .order_by(Favorite.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_tutorial_favorites(tutorial_id: int, limit: Optional[int] = None) -> List['Favorite']:
        """Récupère les utilisateurs qui ont mis ce tutoriel en favori."""
        query = Favorite.query.filter_by(tutorial_id=tutorial_id)\
            .order_by(Favorite.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_popular_tutorials(limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les tutoriels les plus mis en favoris."""
        from sqlalchemy import func
        from app.models.tutorial import Tutorial
        
        results = db.session.query(
            Tutorial.id,
            Tutorial.title,
            Tutorial.slug,
            func.count(Favorite.id).label('favorite_count')
        ).join(Favorite, Tutorial.id == Favorite.tutorial_id)\
         .filter(Tutorial.status == 'published')\
         .group_by(Tutorial.id, Tutorial.title, Tutorial.slug)\
         .order_by(func.count(Favorite.id).desc())\
         .limit(limit)\
         .all()
        
        return [
            {
                'tutorial_id': result.id,
                'title': result.title,
                'slug': result.slug,
                'favorite_count': result.favorite_count
            }
            for result in results
        ]