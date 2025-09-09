"""
Modèle Tutorial - Cœur de l'application pour les tutoriels WoW.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import re
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, Float, 
    ForeignKey, Index, Enum, event
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from slugify import slugify
import bleach

from app.extensions import db
from app.models.tag import tutorial_tags


class Tutorial(db.Model):
    """Modèle principal pour les tutoriels."""
    
    __tablename__ = 'tutorial'
    
    # Identifiants
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    
    # Contenu principal
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    content_html_sanitized: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Taxonomie
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Workflow de publication
    status: Mapped[str] = mapped_column(
        Enum('draft', 'review', 'published', 'archived', name='tutorial_status'),
        default='draft',
        nullable=False,
        index=True
    )
    
    # Médias
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Métadonnées WoW
    expansion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    patch_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    class_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    spec_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(
        Enum('normal', 'heroic', 'mythic', 'arena', 'rbg', name='difficulty_level'),
        nullable=True,
        index=True
    )
    
    # Métriques
    estimated_read_min: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        index=True
    )
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
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    
    # Relations
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="tutorials",
        lazy='joined'
    )
    
    author: Mapped["User"] = relationship(
        "User", 
        back_populates="tutorials",
        lazy='joined'
    )
    
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=tutorial_tags,
        back_populates="tutorials",
        lazy='selectin'
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="tutorial",
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    
    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", 
        back_populates="tutorial",
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", 
        back_populates="tutorial",
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", 
        back_populates="tutorial",
        lazy='selectin',
        cascade="all, delete-orphan"
    )
    
    # Index composites pour les performances
    __table_args__ = (
        Index('ix_tutorial_status_published', 'status', 'published_at'),
        Index('ix_tutorial_category_status', 'category_id', 'status'),
        Index('ix_tutorial_author_status', 'author_id', 'status'),
        Index('ix_tutorial_expansion_class', 'expansion', 'class_name'),
    )
    
    def __repr__(self) -> str:
        return f'<Tutorial {self.title}>'
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def url(self) -> str:
        """URL canonique du tutoriel."""
        return f'/tutos/{self.slug}'
    
    @property
    def is_published(self) -> bool:
        """Vérifie si le tutoriel est publié."""
        return self.status == 'published'
    
    @property
    def comment_count(self) -> int:
        """Nombre de commentaires visibles."""
        return self.comments.filter_by(status='visible').count()
    
    @property
    def favorite_count(self) -> int:
        """Nombre de favoris."""
        return self.favorites.count()
    
    def set_slug(self) -> None:
        """Génère automatiquement le slug à partir du titre."""
        if not self.slug and self.title:
            base_slug = slugify(self.title, separator='-', max_length=150)
            
            # Vérifier l'unicité du slug
            counter = 1
            slug = base_slug
            while Tutorial.query.filter_by(slug=slug).filter(Tutorial.id != self.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
    
    def sanitize_html(self) -> None:
        """Sanitise le contenu HTML avec bleach."""
        # Tags autorisés
        allowed_tags = [
            'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'strike', 'del',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'dl', 'dt', 'dd',
            'blockquote', 'pre', 'code',
            'a', 'img',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'div', 'span'
        ]
        
        # Attributs autorisés par tag
        allowed_attributes = {
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
            'div': ['class'],
            'span': ['class'],
            'code': ['class'],
            'pre': ['class'],
        }
        
        # Protocoles autorisés pour les liens
        allowed_protocols = ['http', 'https', 'mailto']
        
        self.content_html_sanitized = bleach.clean(
            self.content_html_sanitized,
            tags=allowed_tags,
            attributes=allowed_attributes,
            protocols=allowed_protocols,
            strip=True
        )
    
    def calculate_reading_time(self) -> None:
        """Calcule le temps de lecture estimé."""
        # Supprimer les balises HTML pour compter les mots
        text_content = bleach.clean(self.content_html_sanitized, tags=[], strip=True)
        
        # Compter les mots (approximation)
        words = len(re.findall(r'\b\w+\b', text_content))
        
        # 200 mots par minute en moyenne
        self.estimated_read_min = max(1, round(words / 200))
    
    def publish(self) -> None:
        """Publie le tutoriel."""
        if self.status != 'published':
            self.status = 'published'
            self.published_at = datetime.now(timezone.utc)
    
    def unpublish(self) -> None:
        """Dépublie le tutoriel."""
        if self.status == 'published':
            self.status = 'archived'
            self.published_at = None
    
    def increment_views(self) -> None:
        """Incrémente le compteur de vues."""
        self.views_count += 1
        db.session.commit()
    
    def update_rating(self) -> None:
        """Met à jour la note moyenne et le nombre de votes."""
        from sqlalchemy import func
        
        result = db.session.query(
            func.avg(Rating.score).label('avg_score'),
            func.count(Rating.score).label('count')
        ).filter(Rating.tutorial_id == self.id).first()
        
        if result and result.count > 0:
            self.rating_avg = round(float(result.avg_score), 1)
            self.rating_count = result.count
        else:
            self.rating_avg = 0.0
            self.rating_count = 0
    
    def to_dict(self, include_content: bool = False, include_relations: bool = False) -> Dict[str, Any]:
        """Convertit le tutoriel en dictionnaire."""
        data = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'summary': self.summary,
            'status': self.status,
            'cover_image_url': self.cover_image_url,
            'video_url': self.video_url,
            'expansion': self.expansion,
            'patch_version': self.patch_version,
            'class_name': self.class_name,
            'spec_name': self.spec_name,
            'difficulty': self.difficulty,
            'estimated_read_min': self.estimated_read_min,
            'views_count': self.views_count,
            'rating_avg': self.rating_avg,
            'rating_count': self.rating_count,
            'comment_count': self.comment_count,
            'favorite_count': self.favorite_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'url': self.url,
        }
        
        if include_content:
            data.update({
                'content_markdown': self.content_markdown,
                'content_html': self.content_html_sanitized,
            })
        
        if include_relations:
            data.update({
                'category': self.category.to_dict() if self.category else None,
                'author': self.author.to_dict() if self.author else None,
                'tags': [tag.to_dict() for tag in self.tags],
                'attachments': [attachment.to_dict() for attachment in self.attachments],
            })
        
        return data
    
    @staticmethod
    def get_by_slug(slug: str, include_drafts: bool = False) -> Optional['Tutorial']:
        """Récupère un tutoriel par son slug."""
        query = Tutorial.query.filter_by(slug=slug)
        
        if not include_drafts:
            query = query.filter_by(status='published')
        
        return query.first()
    
    @staticmethod
    def get_published(limit: Optional[int] = None) -> List['Tutorial']:
        """Récupère les tutoriels publiés."""
        query = Tutorial.query.filter_by(status='published')\
            .order_by(Tutorial.published_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_popular(limit: int = 10) -> List['Tutorial']:
        """Récupère les tutoriels les plus populaires."""
        return Tutorial.query.filter_by(status='published')\
            .order_by(Tutorial.views_count.desc(), Tutorial.rating_avg.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_recent(limit: int = 10) -> List['Tutorial']:
        """Récupère les tutoriels récents."""
        return Tutorial.query.filter_by(status='published')\
            .order_by(Tutorial.published_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_by_category(category_id: int, limit: Optional[int] = None) -> List['Tutorial']:
        """Récupère les tutoriels d'une catégorie."""
        query = Tutorial.query.filter_by(category_id=category_id, status='published')\
            .order_by(Tutorial.published_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_by_tag(tag_id: int, limit: Optional[int] = None) -> List['Tutorial']:
        """Récupère les tutoriels avec un tag spécifique."""
        from app.models.tag import Tag
        
        query = Tutorial.query.join(Tutorial.tags).filter(
            Tag.id == tag_id,
            Tutorial.status == 'published'
        ).order_by(Tutorial.published_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()


# Événements SQLAlchemy pour automatiser certaines actions
@event.listens_for(Tutorial, 'before_insert')
@event.listens_for(Tutorial, 'before_update')
def tutorial_before_save(mapper, connection, target):
    """Actions à effectuer avant sauvegarde."""
    # Générer le slug automatiquement
    if not target.slug:
        target.set_slug()
    
    # Calculer le temps de lecture
    if target.content_html_sanitized:
        target.calculate_reading_time()
    
    # Sanitiser le HTML
    if target.content_html_sanitized:
        target.sanitize_html()