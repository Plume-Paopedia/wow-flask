"""
Modèle ModerationLog pour l'audit et la traçabilité des actions de modération.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ModerationLog(db.Model):
    """Modèle pour les logs de modération."""
    
    __tablename__ = 'moderation_log'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Qui a effectué l'action
    actor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Sur quoi l'action a été effectuée
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tutorial, comment, user, etc.
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Quelle action
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # approve, reject, hide, ban, etc.
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Métadonnées supplémentaires (JSON)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relations
    actor: Mapped["User"] = relationship("User")
    
    # Index pour les performances
    __table_args__ = (
        Index('ix_moderation_entity', 'entity_type', 'entity_id'),
        Index('ix_moderation_actor_created', 'actor_id', 'created_at'),
        Index('ix_moderation_action_created', 'action', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<ModerationLog {self.action} on {self.entity_type}:{self.entity_id}>'
    
    def to_dict(self, include_actor: bool = True) -> Dict[str, Any]:
        """Convertit le log en dictionnaire."""
        data = {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'reason': self.reason,
            'metadata': self.extra_data,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_actor:
            data['actor'] = self.actor.to_dict() if self.actor else None
        
        return data
    
    @staticmethod
    def log_action(
        actor_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        reason: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> 'ModerationLog':
        """Enregistre une action de modération."""
        log = ModerationLog(
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            reason=reason,
            extra_data=extra_data or {}
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_tutorial_action(
        actor_id: int,
        tutorial_id: int,
        action: str,
        reason: Optional[str] = None,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None
    ) -> 'ModerationLog':
        """Log spécifique pour les actions sur les tutoriels."""
        extra_data = {}
        if previous_status:
            extra_data['previous_status'] = previous_status
        if new_status:
            extra_data['new_status'] = new_status
        
        return ModerationLog.log_action(
            actor_id=actor_id,
            entity_type='tutorial',
            entity_id=tutorial_id,
            action=action,
            reason=reason,
            extra_data=extra_data
        )
        
        return ModerationLog.log_action(
            actor_id=actor_id,
            entity_type='tutorial',
            entity_id=tutorial_id,
            action=action,
            reason=reason,
            extra_data=extra_data
        )
    
    @staticmethod
    def log_comment_action(
        actor_id: int,
        comment_id: int,
        action: str,
        reason: Optional[str] = None,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None
    ) -> 'ModerationLog':
        """Log spécifique pour les actions sur les commentaires."""
        extra_data = {}
        if previous_status:
            extra_data['previous_status'] = previous_status
        if new_status:
            extra_data['new_status'] = new_status
        
        return ModerationLog.log_action(
            actor_id=actor_id,
            entity_type='comment',
            entity_id=comment_id,
            action=action,
            reason=reason,
            extra_data=extra_data
        )
    
    @staticmethod
    def log_user_action(
        actor_id: int,
        user_id: int,
        action: str,
        reason: Optional[str] = None,
        duration_hours: Optional[int] = None
    ) -> 'ModerationLog':
        """Log spécifique pour les actions sur les utilisateurs."""
        extra_data = {}
        if duration_hours:
            extra_data['duration_hours'] = duration_hours
        
        return ModerationLog.log_action(
            actor_id=actor_id,
            entity_type='user',
            entity_id=user_id,
            action=action,
            reason=reason,
            extra_data=extra_data
        )
    
    @staticmethod
    def get_for_entity(entity_type: str, entity_id: int) -> List['ModerationLog']:
        """Récupère les logs pour une entité spécifique."""
        return ModerationLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(ModerationLog.created_at.desc()).all()
    
    @staticmethod
    def get_recent_logs(limit: int = 50) -> List['ModerationLog']:
        """Récupère les logs récents."""
        return ModerationLog.query.order_by(ModerationLog.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_logs_by_actor(actor_id: int, limit: Optional[int] = None) -> List['ModerationLog']:
        """Récupère les logs d'un modérateur."""
        query = ModerationLog.query.filter_by(actor_id=actor_id)\
            .order_by(ModerationLog.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_action_stats(days: int = 30) -> Dict[str, int]:
        """Récupère les statistiques d'actions de modération."""
        from sqlalchemy import func
        from datetime import timedelta
        
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        results = db.session.query(
            ModerationLog.action,
            func.count(ModerationLog.id).label('count')
        ).filter(ModerationLog.created_at >= since_date)\
         .group_by(ModerationLog.action)\
         .all()
        
        return {result.action: result.count for result in results}