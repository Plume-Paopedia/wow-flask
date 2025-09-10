# WoW Flask Tutorial Portal

Portail communautaire français pour regrouper, publier et modérer des tutoriels World of Warcraft.

## 🌟 Fonctionnalités

- **Authentification complète** : Email/mot de passe + OAuth Battle.net optionnel
- **Gestion de contenu** : Éditeur Markdown, workflow de modération, uploads média
- **Recherche avancée** : Multi-backends (Meilisearch, PostgreSQL, SQLite)
- **Système social** : Commentaires, notes, favoris
- **Administration** : Panel d'admin, modération, audit
- **API REST** : Documentation OpenAPI, rate limiting
- **SEO optimisé** : Sitemaps, OpenGraph, JSON-LD
- **Sécurité** : CSRF, CSP, sanitisation HTML, headers sécurisés
- **Performance** : Cache Redis, optimisations N+1
- **Déploiement** : Docker, Railway/Render/Fly.io compatible

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- PostgreSQL (production) ou SQLite (développement)
- Redis (optionnel, pour cache et rate limiting)
- Node.js (pour TailwindCSS, optionnel)

### Installation

```bash
# Cloner le projet
git clone https://github.com/Plume-Paopedia/wow-flask.git
cd wow-flask

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -e .[dev]

# Copier la configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Initialiser la base de données
make migrate
make seed

# Lancer le serveur de développement
make run
```

### Docker

```bash
# Développement
docker-compose up -d

# Production
docker build -t wow-flask .
docker run -p 8000:8000 --env-file .env wow-flask
```

## 🔧 Configuration

### Variables d'environnement essentielles

```bash
# Application
FLASK_ENV=development
SECRET_KEY=your-very-long-secret-key
APP_BASE_URL=http://localhost:5000

# Base de données
DATABASE_URL=sqlite:///app.db  # Développement
# DATABASE_URL=postgresql://user:pass@localhost/wowflask  # Production

# Cache et rate limiting (optionnel)
REDIS_URL=redis://localhost:6379

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@wowflask.fr

# Battle.net OAuth (optionnel)
OAUTH_ENABLE_BNET=false
BATTLE_NET_CLIENT_ID=your-bnet-client-id
BATTLE_NET_CLIENT_SECRET=your-bnet-client-secret
BATTLE_NET_REDIRECT_URI=http://localhost:5000/auth/bnet/callback

# Recherche (optionnel)
SEARCH_BACKEND=sqlite_fts  # ou pg ou meilisearch
MEILI_URL=http://localhost:7700
MEILI_MASTER_KEY=your-meili-key

# Uploads
ALLOWED_UPLOAD_EXT=jpg,png,webp,mp4,webm,pdf
MAX_CONTENT_LENGTH_MB=200

# S3 (production, optionnel)
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_BUCKET_NAME=your-bucket
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
```

### Configuration avancée

Voir `.env.example` pour la liste complète des variables disponibles.

## 🛠️ Commandes de développement

```bash
# Serveur de développement
make run

# Tests
make test
make test-cov

# Formatage et linting
make format
make lint
make type-check

# Base de données
make migrate        # Appliquer les migrations
make migration      # Créer une nouvelle migration
make seed          # Peupler avec des données de test
make reset-db      # Réinitialiser la DB

# Recherche
make reindex       # Réindexer le moteur de recherche

# Docker
make docker-build
make docker-up
make docker-down

# Production
make install-prod
make collect-static
```

## 📁 Structure du projet

```
wow-flask/
├── app/                    # Application Flask
│   ├── __init__.py        # Factory et configuration
│   ├── extensions.py      # Extensions Flask
│   ├── config.py          # Classes de configuration
│   ├── models/            # Modèles SQLAlchemy
│   ├── blueprints/        # Routes organisées par modules
│   │   ├── public/        # Pages publiques
│   │   ├── auth/          # Authentification
│   │   ├── dashboard/     # Tableau de bord utilisateur
│   │   ├── admin/         # Administration
│   │   └── api/           # API REST
│   ├── services/          # Logique métier
│   ├── templates/         # Templates Jinja2
│   └── static/            # Assets statiques
├── migrations/            # Migrations Alembic
├── scripts/              # Scripts utilitaires
├── tests/                # Tests pytest
├── docker/               # Configuration Docker
├── docs/                 # Documentation
├── Makefile              # Commandes de développement
├── pyproject.toml        # Configuration Python
├── docker-compose.yml    # Docker Compose
├── Dockerfile            # Image Docker
└── README.md
```

## 🎯 Utilisation

### Créer un tutoriel

1. Créer un compte et se connecter
2. Aller dans "Mes Tutoriels" → "Nouveau"
3. Rédiger en Markdown avec l'éditeur intégré
4. Ajouter tags, catégorie, cover image
5. Soumettre pour review ou publier directement (selon permissions)

### Modération

Les modérateurs peuvent :
- Approuver/rejeter les tutoriels en attente
- Modérer les commentaires
- Gérer les tags et catégories
- Consulter les logs d'audit

### API REST

Documentation interactive disponible sur `/api/docs`

Exemples d'endpoints :
- `GET /api/v1/tutorials` - Liste des tutoriels
- `POST /api/v1/tutorials` - Créer un tutoriel
- `GET /api/v1/tutorials/{slug}` - Détails d'un tutoriel
- `POST /api/v1/auth/login` - Connexion

## 🔒 Sécurité

- Protection CSRF sur tous les formulaires
- Sanitisation HTML avec bleach
- Headers de sécurité (CSP, HSTS, etc.)
- Rate limiting sur l'API et l'authentification
- Hachage sécurisé des mots de passe (Argon2)
- Sessions sécurisées avec HttpOnly/SameSite

## 🚀 Déploiement

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/wow-flask)

Railway détecte automatiquement la configuration et déploie l'application:

```bash
# Cloner et déployer
git clone https://github.com/Plume-Paopedia/wow-flask.git
cd wow-flask

# Déployer sur Railway (nécessite Railway CLI)
railway login
railway link
railway up
```

Variables d'environnement à configurer sur Railway :
- `SECRET_KEY` (obligatoire)
- `DATABASE_URL` (PostgreSQL automatique)
- `REDIS_URL` (Redis automatique)
- Autres variables selon vos besoins (voir `.env.example`)

📖 [Guide complet Railway](RAILWAY.md)

### Render

1. Connecter votre repo GitHub
2. Configurer les variables d'environnement
3. Déployer automatiquement

### Docker générique

```bash
docker build -t wow-flask .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="..." \
  wow-flask
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Coverage complet
make test-cov
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committer les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Pousser la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

### Standards de code

- Formatage : Black
- Linting : Ruff
- Type checking : MyPy
- Tests : pytest avec couverture >80%

## 📄 Licence

MIT License - voir le fichier [LICENSE](LICENSE) pour les détails.

## 🆘 Support

- Issues GitHub : [https://github.com/Plume-Paopedia/wow-flask/issues](https://github.com/Plume-Paopedia/wow-flask/issues)
- Documentation : [https://docs.wowflask.fr](https://docs.wowflask.fr)
- Discord : [https://discord.gg/wowflask](https://discord.gg/wowflask)

---

Fait avec ❤️ pour la communauté World of Warcraft française