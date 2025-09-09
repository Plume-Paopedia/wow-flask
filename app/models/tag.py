"""
Modèle Tag pour le système de tags des tutoriels.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from slugify import slugify

from app.extensions import db


# Table d'association pour les tags de tutoriels (many-to-many)
tutorial_tags = db.Table(
    'tutorial_tags',
    db.Column('tutorial_id', db.Integer, db.ForeignKey('tutorial.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Tag(db.Model):
    """Modèle pour les tags de tutoriels."""
    
    __tablename__ = 'tag'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relations
    tutorials: Mapped[List["Tutorial"]] = relationship(
        "Tutorial", 
        secondary=tutorial_tags,
        back_populates="tags",
        lazy='dynamic'
    )
    
    def __repr__(self) -> str:
        return f'<Tag {self.name}>'
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def tutorial_count(self) -> int:
        """Nombre de tutoriels publiés avec ce tag."""
        return self.tutorials.filter_by(status='published').count()
    
    @property
    def url(self) -> str:
        """URL de la page du tag."""
        return f'/tags/{self.slug}'
    
    def set_slug(self) -> None:
        """Génère automatiquement le slug à partir du nom."""
        if not self.slug and self.name:
            base_slug = slugify(self.name, separator='-')
            
            # Vérifier l'unicité du slug
            counter = 1
            slug = base_slug
            while Tag.query.filter_by(slug=slug).filter(Tag.id != self.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
    
    def to_dict(self, include_tutorials: bool = False) -> Dict[str, Any]:
        """Convertit le tag en dictionnaire."""
        data = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'tutorial_count': self.tutorial_count,
            'url': self.url,
        }
        
        if include_tutorials:
            data['tutorials'] = [
                tutorial.to_dict() 
                for tutorial in self.tutorials.filter_by(status='published').all()
            ]
        
        return data
    
    @staticmethod
    def get_by_slug(slug: str) -> Optional['Tag']:
        """Récupère un tag par son slug."""
        return Tag.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_by_name(name: str) -> Optional['Tag']:
        """Récupère un tag par son nom."""
        return Tag.query.filter_by(name=name).first()
    
    @staticmethod
    def get_or_create(name: str, description: Optional[str] = None) -> 'Tag':
        """Récupère un tag existant ou le crée s'il n'existe pas."""
        tag = Tag.get_by_name(name)
        if not tag:
            tag = Tag(name=name, description=description)
            tag.set_slug()
            db.session.add(tag)
            db.session.flush()  # Pour obtenir l'ID sans commit
        return tag
    
    @staticmethod
    def search_by_name(query: str, limit: int = 10) -> List['Tag']:
        """Recherche des tags par nom (pour auto-complétion)."""
        return Tag.query.filter(
            Tag.name.ilike(f'%{query}%')
        ).order_by(Tag.name.asc()).limit(limit).all()
    
    @staticmethod
    def get_popular(limit: int = 20) -> List['Tag']:
        """Récupère les tags les plus populaires."""
        # Utilisation d'une sous-requête pour compter les tutoriels publiés
        from sqlalchemy import func
        from app.models.tutorial import Tutorial
        
        return db.session.query(Tag)\
            .join(tutorial_tags)\
            .join(Tutorial)\
            .filter(Tutorial.status == 'published')\
            .group_by(Tag.id)\
            .order_by(func.count(Tutorial.id).desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def create_default_tags():
        """Crée les tags par défaut."""
        default_tags = [
            # Classes
            {'name': 'Death Knight', 'description': 'Chevalier de la mort'},
            {'name': 'Demon Hunter', 'description': 'Chasseur de démons'},
            {'name': 'Druid', 'description': 'Druide'},
            {'name': 'Evoker', 'description': 'Évocateur'},
            {'name': 'Hunter', 'description': 'Chasseur'},
            {'name': 'Mage', 'description': 'Mage'},
            {'name': 'Monk', 'description': 'Moine'},
            {'name': 'Paladin', 'description': 'Paladin'},
            {'name': 'Priest', 'description': 'Prêtre'},
            {'name': 'Rogue', 'description': 'Voleur'},
            {'name': 'Shaman', 'description': 'Chaman'},
            {'name': 'Warlock', 'description': 'Démoniste'},
            {'name': 'Warrior', 'description': 'Guerrier'},
            
            # Rôles
            {'name': 'Tank', 'description': 'Rôle de tank'},
            {'name': 'Heal', 'description': 'Rôle de soigneur'},
            {'name': 'DPS', 'description': 'Rôle de dégâts'},
            
            # Contenu
            {'name': 'Mythic+', 'description': 'Donjons Mythiques+'},
            {'name': 'Raid', 'description': 'Contenu de raid'},
            {'name': 'Arena', 'description': 'Arènes PvP'},
            {'name': 'RBG', 'description': 'Champs de bataille cotés'},
            
            # Général
            {'name': 'Débutant', 'description': 'Contenu pour débutants'},
            {'name': 'Avancé', 'description': 'Contenu avancé'},
            {'name': 'WeakAura', 'description': 'WeakAuras et configurations'},
            {'name': 'Macro', 'description': 'Macros et scripts'},
            {'name': 'UI', 'description': 'Interface utilisateur'},
            {'name': 'Gold', 'description': 'Génération d\'or'},
            
            # Extensions
            {'name': 'Dragonflight', 'description': 'Extension Dragonflight'},
            {'name': 'Shadowlands', 'description': 'Extension Shadowlands'},
            {'name': 'BFA', 'description': 'Battle for Azeroth'},
            {'name': 'Legion', 'description': 'Extension Legion'},
        ]
        
        for tag_data in default_tags:
            existing = Tag.query.filter_by(name=tag_data['name']).first()
            if not existing:
                tag = Tag(
                    name=tag_data['name'],
                    description=tag_data['description']
                )
                tag.set_slug()
                db.session.add(tag)
        
        db.session.commit()