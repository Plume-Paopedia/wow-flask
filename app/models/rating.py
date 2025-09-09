"""
Modèle Rating pour le système de notation des tutoriels.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Rating(db.Model):
    """Modèle pour les notes des tutoriels (1 à 5 étoiles)."""
    
    __tablename__ = 'rating'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relations
    tutorial_id: Mapped[int] = mapped_column(ForeignKey('tutorial.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Note (1-5 étoiles)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relations
    tutorial: Mapped["Tutorial"] = relationship(
        "Tutorial", 
        back_populates="ratings"
    )
    
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="ratings"
    )
    
    # Contraintes
    __table_args__ = (
        # Un utilisateur ne peut noter qu'une fois par tutoriel
        UniqueConstraint('tutorial_id', 'user_id', name='unique_user_tutorial_rating'),
        Index('ix_rating_tutorial_score', 'tutorial_id', 'score'),
        Index('ix_rating_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<Rating {self.score}/5 by User {self.user_id} for Tutorial {self.tutorial_id}>'
    
    def to_dict(self, include_user: bool = False) -> Dict[str, Any]:
        """Convertit la note en dictionnaire."""
        data = {
            'id': self.id,
            'tutorial_id': self.tutorial_id,
            'score': self.score,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_user:
            data['user'] = self.user.to_dict() if self.user else None
        
        return data
    
    @staticmethod
    def get_user_rating(user_id: int, tutorial_id: int) -> Optional['Rating']:
        """Récupère la note d'un utilisateur pour un tutoriel."""
        return Rating.query.filter_by(
            user_id=user_id, 
            tutorial_id=tutorial_id
        ).first()
    
    @staticmethod
    def set_rating(user_id: int, tutorial_id: int, score: int) -> 'Rating':
        """Définit ou met à jour la note d'un utilisateur."""
        if not (1 <= score <= 5):
            raise ValueError("Le score doit être entre 1 et 5")
        
        # Chercher une note existante
        rating = Rating.get_user_rating(user_id, tutorial_id)
        
        if rating:
            # Mettre à jour la note existante
            rating.score = score
        else:
            # Créer une nouvelle note
            rating = Rating(
                user_id=user_id,
                tutorial_id=tutorial_id,
                score=score
            )
            db.session.add(rating)
        
        db.session.flush()
        
        # Mettre à jour les statistiques du tutoriel
        from app.models.tutorial import Tutorial
        tutorial = Tutorial.query.get(tutorial_id)
        if tutorial:
            tutorial.update_rating()
        
        return rating
    
    @staticmethod
    def get_tutorial_stats(tutorial_id: int) -> Dict[str, Any]:
        """Récupère les statistiques de notation d'un tutoriel."""
        from sqlalchemy import func
        
        # Compter les notes par score
        score_counts = db.session.query(
            Rating.score,
            func.count(Rating.score).label('count')
        ).filter(Rating.tutorial_id == tutorial_id)\
         .group_by(Rating.score)\
         .all()
        
        # Calculer les statistiques
        total_ratings = sum(item.count for item in score_counts)
        if total_ratings == 0:
            return {
                'total_ratings': 0,
                'average_score': 0.0,
                'distribution': {i: 0 for i in range(1, 6)}
            }
        
        total_score = sum(item.score * item.count for item in score_counts)
        average_score = round(total_score / total_ratings, 1)
        
        # Distribution des scores
        distribution = {i: 0 for i in range(1, 6)}
        for item in score_counts:
            distribution[item.score] = item.count
        
        return {
            'total_ratings': total_ratings,
            'average_score': average_score,
            'distribution': distribution
        }
    
    @staticmethod
    def get_user_ratings(user_id: int, limit: Optional[int] = None) -> List['Rating']:
        """Récupère les notes données par un utilisateur."""
        query = Rating.query.filter_by(user_id=user_id)\
            .order_by(Rating.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()