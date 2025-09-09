#!/usr/bin/env python3
"""
Script de peuplement de la base de données avec des données initiales.
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User


def seed_database():
    """Peuple la base de données avec les données initiales."""
    print("🌱 Début du peuplement de la base de données...")
    
    try:
        # Créer les rôles par défaut
        print("📝 Création des rôles...")
        Role.create_default_roles()
        
        # Créer les catégories par défaut
        print("📁 Création des catégories...")
        Category.create_default_categories()
        
        # Créer les tags par défaut
        print("🏷️  Création des tags...")
        Tag.create_default_tags()
        
        # Créer un utilisateur admin par défaut (optionnel)
        admin_role = Role.query.filter_by(name='admin').first()
        existing_admin = User.query.join(User.roles).filter(Role.name == 'admin').first()
        
        if not existing_admin:
            print("👤 Création de l'utilisateur admin par défaut...")
            admin_user = User(
                email='admin@wowflask.fr',
                username='admin',
                email_verified=True
            )
            admin_user.set_password('admin123')  # Mot de passe temporaire
            admin_user.roles.append(admin_role)
            
            db.session.add(admin_user)
            
            print("⚠️  Utilisateur admin créé :")
            print("   Email: admin@wowflask.fr")
            print("   Mot de passe: admin123")
            print("   ⚠️  CHANGEZ LE MOT DE PASSE EN PRODUCTION !")
        
        db.session.commit()
        print("✅ Peuplement terminé avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors du peuplement : {e}")
        db.session.rollback()
        return False
    
    return True


def create_sample_data():
    """Crée des données d'exemple pour le développement."""
    print("🎭 Création des données d'exemple...")
    
    try:
        from app.models.tutorial import Tutorial
        from app.models.user import User
        from app.models.category import Category
        from app.models.tag import Tag
        
        # Créer quelques utilisateurs de test
        author_role = Role.query.filter_by(name='author').first()
        member_role = Role.query.filter_by(name='member').first()
        
        if not User.query.filter_by(username='author1').first():
            author1 = User(
                email='author1@wowflask.fr',
                username='author1',
                email_verified=True,
                bio='Auteur de guides pour mages et raids'
            )
            author1.set_password('author123')
            author1.roles.append(author_role)
            db.session.add(author1)
        
        if not User.query.filter_by(username='member1').first():
            member1 = User(
                email='member1@wowflask.fr', 
                username='member1',
                email_verified=True
            )
            member1.set_password('member123')
            member1.roles.append(member_role)
            db.session.add(member1)
        
        db.session.commit()
        
        # Créer quelques tutoriels d'exemple
        author = User.query.filter_by(username='author1').first()
        if author:
            mage_category = Category.query.filter_by(slug='classes').first()
            raid_category = Category.query.filter_by(slug='raids').first()
            
            mage_tag = Tag.query.filter_by(slug='mage').first()
            dps_tag = Tag.query.filter_by(slug='dps').first()
            
            if mage_category and not Tutorial.query.filter_by(title='Guide Mage Feu 10.2').first():
                tutorial1 = Tutorial(
                    title='Guide Mage Feu 10.2',
                    summary='Guide complet du Mage Feu pour la patch 10.2',
                    content_markdown='''# Guide Mage Feu 10.2

## Introduction

Ce guide vous explique comment jouer Mage Feu de manière optimale...

## Talents

Voici les talents recommandés...

## Rotation

La rotation de base est la suivante...
''',
                    content_html_sanitized='''<h1>Guide Mage Feu 10.2</h1>
<h2>Introduction</h2>
<p>Ce guide vous explique comment jouer Mage Feu de manière optimale...</p>
<h2>Talents</h2>
<p>Voici les talents recommandés...</p>
<h2>Rotation</h2>
<p>La rotation de base est la suivante...</p>''',
                    category=mage_category,
                    author=author,
                    status='published',
                    expansion='Dragonflight',
                    patch_version='10.2',
                    class_name='Mage',
                    spec_name='Feu',
                    difficulty='normal'
                )
                tutorial1.set_slug()
                tutorial1.publish()
                
                if mage_tag:
                    tutorial1.tags.append(mage_tag)
                if dps_tag:
                    tutorial1.tags.append(dps_tag)
                
                db.session.add(tutorial1)
            
            if raid_category and not Tutorial.query.filter_by(title='Stratégie Fyrakk Mythique').first():
                tutorial2 = Tutorial(
                    title='Stratégie Fyrakk Mythique',
                    summary='Guide de stratégie pour le boss Fyrakk en difficulté Mythique',
                    content_markdown='''# Fyrakk Mythique

## Vue d'ensemble

Fyrakk est le boss final du raid...

## Phases

### Phase 1
...

### Phase 2
...
''',
                    content_html_sanitized='''<h1>Fyrakk Mythique</h1>
<h2>Vue d'ensemble</h2>
<p>Fyrakk est le boss final du raid...</p>
<h2>Phases</h2>
<h3>Phase 1</h3>
<p>...</p>
<h3>Phase 2</h3>
<p>...</p>''',
                    category=raid_category,
                    author=author,
                    status='published',
                    expansion='Dragonflight',
                    patch_version='10.2',
                    difficulty='mythic'
                )
                tutorial2.set_slug()
                tutorial2.publish()
                
                raid_tag = Tag.query.filter_by(slug='raid').first()
                if raid_tag:
                    tutorial2.tags.append(raid_tag)
                
                db.session.add(tutorial2)
        
        db.session.commit()
        print("✅ Données d'exemple créées !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données d'exemple : {e}")
        db.session.rollback()


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Vérifier que les tables existent
        try:
            db.create_all()
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables : {e}")
            sys.exit(1)
        
        # Peupler avec les données de base
        if seed_database():
            # Si en développement, créer aussi des données d'exemple
            if app.config.get('FLASK_ENV') == 'development':
                create_sample_data()
        else:
            sys.exit(1)