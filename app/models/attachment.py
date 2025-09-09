"""
Modèle Attachment pour les fichiers attachés aux tutoriels.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Attachment(db.Model):
    """Modèle pour les pièces jointes des tutoriels."""
    
    __tablename__ = 'attachment'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Relations
    tutorial_id: Mapped[int] = mapped_column(ForeignKey('tutorial.id'), nullable=False)
    uploader_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    
    # Informations du fichier
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Métadonnées optionnelles
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relations
    tutorial: Mapped["Tutorial"] = relationship(
        "Tutorial", 
        back_populates="attachments"
    )
    
    uploader: Mapped["User"] = relationship("User")
    
    # Index pour les performances
    __table_args__ = (
        Index('ix_attachment_tutorial_created', 'tutorial_id', 'created_at'),
        Index('ix_attachment_uploader', 'uploader_id'),
    )
    
    def __repr__(self) -> str:
        return f'<Attachment {self.filename}>'
    
    @property
    def is_image(self) -> bool:
        """Vérifie si le fichier est une image."""
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self) -> bool:
        """Vérifie si le fichier est une vidéo."""
        return self.mime_type.startswith('video/')
    
    @property
    def is_document(self) -> bool:
        """Vérifie si le fichier est un document."""
        document_mimes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
        ]
        return self.mime_type in document_mimes
    
    @property
    def file_extension(self) -> str:
        """Retourne l'extension du fichier."""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''
    
    @property
    def size_human(self) -> str:
        """Retourne la taille du fichier en format lisible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size_bytes < 1024.0:
                return f"{self.size_bytes:.1f} {unit}"
            self.size_bytes /= 1024.0
        return f"{self.size_bytes:.1f} TB"
    
    def get_thumbnail_url(self, size: int = 150) -> Optional[str]:
        """Retourne l'URL du thumbnail si c'est une image."""
        if not self.is_image:
            return None
        
        # Pour l'instant, retourne l'image originale
        # TODO: Implémenter la génération de thumbnails
        return self.url
    
    def to_dict(self, include_uploader: bool = False) -> Dict[str, Any]:
        """Convertit l'attachment en dictionnaire."""
        data = {
            'id': self.id,
            'tutorial_id': self.tutorial_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'url': self.url,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'size_human': self.size_human,
            'alt_text': self.alt_text,
            'description': self.description,
            'is_image': self.is_image,
            'is_video': self.is_video,
            'is_document': self.is_document,
            'file_extension': self.file_extension,
            'thumbnail_url': self.get_thumbnail_url() if self.is_image else None,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_uploader:
            data['uploader'] = self.uploader.to_dict() if self.uploader else None
        
        return data
    
    @staticmethod
    def get_for_tutorial(tutorial_id: int) -> List['Attachment']:
        """Récupère les attachments d'un tutoriel."""
        return Attachment.query.filter_by(tutorial_id=tutorial_id)\
            .order_by(Attachment.created_at.asc()).all()
    
    @staticmethod
    def get_images_for_tutorial(tutorial_id: int) -> List['Attachment']:
        """Récupère uniquement les images d'un tutoriel."""
        return Attachment.query.filter_by(tutorial_id=tutorial_id)\
            .filter(Attachment.mime_type.like('image/%'))\
            .order_by(Attachment.created_at.asc()).all()
    
    @staticmethod
    def get_by_filename(filename: str) -> Optional['Attachment']:
        """Récupère un attachment par son nom de fichier."""
        return Attachment.query.filter_by(filename=filename).first()
    
    @staticmethod
    def create_attachment(
        tutorial_id: int,
        uploader_id: int,
        filename: str,
        original_filename: str,
        url: str,
        mime_type: str,
        size_bytes: int,
        alt_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> 'Attachment':
        """Crée un nouvel attachment."""
        attachment = Attachment(
            tutorial_id=tutorial_id,
            uploader_id=uploader_id,
            filename=filename,
            original_filename=original_filename,
            url=url,
            mime_type=mime_type,
            size_bytes=size_bytes,
            alt_text=alt_text,
            description=description
        )
        
        db.session.add(attachment)
        db.session.commit()
        return attachment
    
    @staticmethod
    def delete_attachment(attachment_id: int) -> bool:
        """Supprime un attachment."""
        attachment = Attachment.query.get(attachment_id)
        if attachment:
            db.session.delete(attachment)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_uploads(user_id: int, limit: Optional[int] = None) -> List['Attachment']:
        """Récupère les uploads d'un utilisateur."""
        query = Attachment.query.filter_by(uploader_id=user_id)\
            .order_by(Attachment.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()