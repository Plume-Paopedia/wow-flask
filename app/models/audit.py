"""
Modèle AuditEvent pour l'audit et la traçabilité des actions utilisateur.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class AuditEvent(db.Model):
    """Modèle pour les événements d'audit."""
    
    __tablename__ = 'audit_event'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Utilisateur (optionnel pour les actions anonymes)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)
    
    # Type d'événement
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Données de l'événement (JSON)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Informations de session/connexion
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Relations
    user: Mapped[Optional["User"]] = relationship("User")
    
    # Index pour les performances
    __table_args__ = (
        Index('ix_audit_user_event', 'user_id', 'event_type'),
        Index('ix_audit_event_created', 'event_type', 'created_at'),
        Index('ix_audit_ip_created', 'ip_address', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<AuditEvent {self.event_type}>'
    
    def to_dict(self, include_user: bool = False) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire."""
        data = {
            'id': self.id,
            'event_type': self.event_type,
            'payload': self.payload,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_user:
            data['user'] = self.user.to_dict() if self.user else None
        
        return data
    
    @staticmethod
    def log_event(
        event_type: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Enregistre un événement d'audit."""
        event = AuditEvent(
            event_type=event_type,
            payload=payload,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def log_user_login(
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> 'AuditEvent':
        """Log une tentative de connexion."""
        return AuditEvent.log_event(
            event_type='user_login_success' if success else 'user_login_failed',
            payload={'user_id': user_id, 'success': success},
            user_id=user_id if success else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_user_logout(
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log une déconnexion."""
        return AuditEvent.log_event(
            event_type='user_logout',
            payload={'user_id': user_id},
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_tutorial_view(
        tutorial_id: int,
        tutorial_slug: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log la consultation d'un tutoriel."""
        return AuditEvent.log_event(
            event_type='tutorial_view',
            payload={
                'tutorial_id': tutorial_id,
                'tutorial_slug': tutorial_slug
            },
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_tutorial_create(
        tutorial_id: int,
        tutorial_slug: str,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log la création d'un tutoriel."""
        return AuditEvent.log_event(
            event_type='tutorial_create',
            payload={
                'tutorial_id': tutorial_id,
                'tutorial_slug': tutorial_slug
            },
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_search(
        query: str,
        results_count: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log une recherche."""
        return AuditEvent.log_event(
            event_type='search',
            payload={
                'query': query,
                'results_count': results_count
            },
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_rating(
        tutorial_id: int,
        rating_score: int,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log une notation."""
        return AuditEvent.log_event(
            event_type='tutorial_rating',
            payload={
                'tutorial_id': tutorial_id,
                'rating_score': rating_score
            },
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_favorite(
        tutorial_id: int,
        action: str,  # 'add' ou 'remove'
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> 'AuditEvent':
        """Log l'ajout/suppression d'un favori."""
        return AuditEvent.log_event(
            event_type='tutorial_favorite',
            payload={
                'tutorial_id': tutorial_id,
                'action': action
            },
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def get_user_events(user_id: int, limit: Optional[int] = None) -> List['AuditEvent']:
        """Récupère les événements d'un utilisateur."""
        query = AuditEvent.query.filter_by(user_id=user_id)\
            .order_by(AuditEvent.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_recent_events(limit: int = 100) -> List['AuditEvent']:
        """Récupère les événements récents."""
        return AuditEvent.query.order_by(AuditEvent.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_events_by_type(event_type: str, limit: Optional[int] = None) -> List['AuditEvent']:
        """Récupère les événements d'un type spécifique."""
        query = AuditEvent.query.filter_by(event_type=event_type)\
            .order_by(AuditEvent.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_login_attempts(
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        hours: int = 24
    ) -> List['AuditEvent']:
        """Récupère les tentatives de connexion récentes."""
        from datetime import timedelta
        
        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = AuditEvent.query.filter(
            AuditEvent.event_type.in_(['user_login_success', 'user_login_failed']),
            AuditEvent.created_at >= since_date
        )
        
        if ip_address:
            query = query.filter_by(ip_address=ip_address)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(AuditEvent.created_at.desc()).all()