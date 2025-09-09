"""
Modèle Role pour la gestion des rôles et permissions.
"""
from typing import List, Set, Dict, Any
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import user_roles


class Role(db.Model):
    """Modèle pour les rôles utilisateur."""
    
    __tablename__ = 'role'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relations
    users: Mapped[List["User"]] = relationship(
        "User", 
        secondary=user_roles, 
        back_populates="roles"
    )
    
    def __repr__(self) -> str:
        return f'<Role {self.name}>'
    
    def has_permission(self, permission: str) -> bool:
        """Vérifie si ce rôle a une permission spécifique."""
        return permission in self.get_permissions()
    
    def get_permissions(self) -> Set[str]:
        """Retourne l'ensemble des permissions pour ce rôle."""
        permissions_map = {
            'admin': {
                '*',  # Toutes les permissions
            },
            'moderator': {
                'tutorial:review',
                'tutorial:approve', 
                'tutorial:reject',
                'tutorial:edit_any',
                'tutorial:delete_any',
                'comment:moderate',
                'comment:hide',
                'comment:delete',
                'user:ban',
                'user:view_profile',
                'tag:create',
                'tag:edit',
                'tag:delete',
                'category:create',
                'category:edit',
                'category:delete',
                'moderation:view_logs',
                'tutorial:view',
                'comment:write',
                'rating:write',
                'favorite:add',
            },
            'author': {
                'tutorial:create',
                'tutorial:edit_own',
                'tutorial:delete_own',
                'tutorial:submit_review',
                'attachment:upload',
                'comment:write',
                'comment:edit_own',
                'comment:delete_own',
                'rating:write',
                'favorite:add',
                'tutorial:view',
                'profile:edit_own',
            },
            'member': {
                'tutorial:view',
                'comment:write',
                'comment:edit_own', 
                'comment:delete_own',
                'rating:write',
                'favorite:add',
                'profile:edit_own',
            }
        }
        
        return permissions_map.get(self.name, set())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le rôle en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': list(self.get_permissions())
        }
    
    @staticmethod
    def get_default_role():
        """Retourne le rôle par défaut pour les nouveaux utilisateurs."""
        return Role.query.filter_by(name='member').first()
    
    @staticmethod
    def create_default_roles():
        """Crée les rôles par défaut s'ils n'existent pas."""
        default_roles = [
            {
                'name': 'admin',
                'description': 'Administrateur avec tous les droits'
            },
            {
                'name': 'moderator', 
                'description': 'Modérateur avec droits de modération et gestion du contenu'
            },
            {
                'name': 'author',
                'description': 'Auteur pouvant créer et gérer ses propres tutoriels'
            },
            {
                'name': 'member',
                'description': 'Membre standard avec droits de lecture et interaction'
            }
        ]
        
        for role_data in default_roles:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(
                    name=role_data['name'],
                    description=role_data['description']
                )
                db.session.add(role)
        
        db.session.commit()