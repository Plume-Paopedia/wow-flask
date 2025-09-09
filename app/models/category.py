"""
Modèle Category pour la taxonomie des tutoriels.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from slugify import slugify

from app.extensions import db


class Category(db.Model):
    """Modèle pour les catégories de tutoriels."""
    
    __tablename__ = 'category'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Métadonnées SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    
    # Relations
    tutorials: Mapped[List["Tutorial"]] = relationship(
        "Tutorial", 
        back_populates="category",
        lazy='dynamic'
    )
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def tutorial_count(self) -> int:
        """Nombre de tutoriels publiés dans cette catégorie."""
        return self.tutorials.filter_by(status='published').count()
    
    @property
    def url(self) -> str:
        """URL de la page de la catégorie."""
        return f'/categories/{self.slug}'
    
    def set_slug(self) -> None:
        """Génère automatiquement le slug à partir du nom."""
        if not self.slug and self.name:
            base_slug = slugify(self.name, separator='-')
            
            # Vérifier l'unicité du slug
            counter = 1
            slug = base_slug
            while Category.query.filter_by(slug=slug).filter(Category.id != self.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
    
    def to_dict(self, include_tutorials: bool = False) -> Dict[str, Any]:
        """Convertit la catégorie en dictionnaire."""
        data = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'tutorial_count': self.tutorial_count,
            'url': self.url,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
        }
        
        if include_tutorials:
            data['tutorials'] = [
                tutorial.to_dict() 
                for tutorial in self.tutorials.filter_by(status='published').all()
            ]
        
        return data
    
    @staticmethod
    def get_by_slug(slug: str) -> Optional['Category']:
        """Récupère une catégorie par son slug."""
        return Category.query.filter_by(slug=slug).first()
    
    @staticmethod
    def get_ordered() -> List['Category']:
        """Récupère toutes les catégories triées par ordre."""
        return Category.query.order_by(Category.order.asc(), Category.name.asc()).all()
    
    @staticmethod
    def create_default_categories():
        """Crée les catégories par défaut."""
        default_categories = [
            {
                'name': 'Classes',
                'description': 'Guides et tutoriels spécifiques aux classes de personnages',
                'order': 10
            },
            {
                'name': 'Raids',
                'description': 'Stratégies et guides pour les raids',
                'order': 20
            },
            {
                'name': 'Donjons',
                'description': 'Guides pour les donjons et Mythique+',
                'order': 30
            },
            {
                'name': 'Leveling',
                'description': 'Guides de montée de niveau et progression',
                'order': 40
            },
            {
                'name': 'Métiers',
                'description': 'Guides des métiers et professions',
                'order': 50
            },
            {
                'name': 'Addons',
                'description': 'Recommandations et configurations d\'addons',
                'order': 60
            },
            {
                'name': 'UI & WeakAuras',
                'description': 'Interfaces utilisateur et WeakAuras',
                'order': 70
            },
            {
                'name': 'Macros',
                'description': 'Macros utiles et personnalisations',
                'order': 80
            },
            {
                'name': 'PvE',
                'description': 'Contenu Joueur contre Environnement général',
                'order': 90
            },
            {
                'name': 'PvP',
                'description': 'Guides et stratégies Joueur contre Joueur',
                'order': 100
            },
            {
                'name': 'Goldmaking',
                'description': 'Techniques et stratégies pour gagner de l\'or',
                'order': 110
            },
            {
                'name': 'Lore',
                'description': 'Histoire et univers de Warcraft',
                'order': 120
            },
            {
                'name': 'Patch Notes',
                'description': 'Analyses des mises à jour et changements',
                'order': 130
            }
        ]
        
        for category_data in default_categories:
            existing = Category.query.filter_by(name=category_data['name']).first()
            if not existing:
                category = Category(
                    name=category_data['name'],
                    description=category_data['description'],
                    order=category_data['order']
                )
                category.set_slug()
                db.session.add(category)
        
        db.session.commit()