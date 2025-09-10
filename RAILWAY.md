# Railway Deployment Guide

Ce guide vous explique comment déployer WoW Flask Portal sur Railway.

## 🚀 Déploiement rapide

### 1. Prérequis
- Un compte Railway: https://railway.app
- Votre code sur GitHub/GitLab (recommandé)

### 2. Déploiement via GitHub

1. **Connecter votre repo**:
   - Allez sur https://railway.app/new
   - Sélectionnez "Deploy from GitHub repo"
   - Choisissez votre repository `wow-flask`

2. **Railway détectera automatiquement**:
   - Le `Dockerfile` ou utilisera Nixpacks
   - Les variables d'environnement nécessaires
   - Le port d'exposition

3. **Ajouter les services**:
   - **PostgreSQL**: Cliquez sur "Add Service" → "Database" → "PostgreSQL"
   - **Redis** (optionnel): Cliquez sur "Add Service" → "Database" → "Redis"

### 3. Variables d'environnement requises

Dans le dashboard Railway, ajoutez ces variables dans "Variables":

#### Variables obligatoires
```bash
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
FLASK_ENV=production
```

#### Variables de base de données (automatiques)
Railway fournit automatiquement:
- `DATABASE_URL` (PostgreSQL)
- `REDIS_URL` (si Redis activé)
- `PORT` (port de déploiement)

#### Variables optionnelles
```bash
# Email (si fonctionnalités email souhaitées)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app
MAIL_DEFAULT_SENDER=noreply@votre-domaine.com

# Battle.net OAuth (si authentification Battle.net souhaitée)
OAUTH_ENABLE_BNET=true
BATTLE_NET_CLIENT_ID=votre-client-id
BATTLE_NET_CLIENT_SECRET=votre-client-secret
BATTLE_NET_REDIRECT_URI=https://votre-app.railway.app/auth/bnet/callback

# Uploads S3 (si stockage externe souhaité)
S3_BUCKET_NAME=votre-bucket
S3_ACCESS_KEY_ID=votre-access-key
S3_SECRET_ACCESS_KEY=votre-secret-key
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

### 4. Configuration du domaine

1. **Domaine Railway** (gratuit):
   - Votre app sera accessible sur `https://votre-app-nom.railway.app`

2. **Domaine personnalisé**:
   - Dans "Settings" → "Domains"
   - Cliquez "Add Custom Domain"
   - Suivez les instructions DNS

### 5. Vérification du déploiement

1. **Logs de déploiement**:
   - Onglet "Deployments" pour voir les logs de build
   - Vérifiez qu'il n'y a pas d'erreurs

2. **Logs de l'application**:
   - Onglet "Logs" pour voir les logs en temps réel
   - Vérifiez que l'app démarre correctement

3. **Test de l'application**:
   - Visitez `https://votre-app.railway.app`
   - Testez `/health` pour vérifier le statut

## 🔧 Configuration avancée

### Variables d'environnement complètes

Consultez `.env.example` pour voir toutes les variables disponibles.

### Gestion des migrations

Les migrations sont exécutées automatiquement au démarrage via `entrypoint.sh`:
- `flask db upgrade` est appelé automatiquement
- Si c'est le premier déploiement, la base sera initialisée

### Monitoring et logs

- **Logs**: Disponibles dans l'onglet "Logs" de Railway
- **Métriques**: CPU, RAM, réseau dans l'onglet "Metrics"
- **Health check**: L'endpoint `/health` est configuré pour Railway

### Scaling

- Railway gère automatiquement le scaling vertical
- Pour plus de ressources, upgrader votre plan Railway

## 🐛 Dépannage

### Problèmes courants

1. **Build fails**:
   - Vérifiez que `requirements.txt` est présent
   - Consultez les logs de build pour voir l'erreur exacte

2. **App crashes au démarrage**:
   - Vérifiez que `SECRET_KEY` est défini
   - Vérifiez que `DATABASE_URL` est disponible
   - Consultez les logs de l'application

3. **Database connection error**:
   - Assurez-vous d'avoir ajouté le service PostgreSQL
   - Vérifiez que `DATABASE_URL` est automatiquement défini
   - Les migrations peuvent prendre quelques secondes

4. **502 Bad Gateway**:
   - L'app n'écoute pas sur le bon port
   - Vérifiez que la variable `PORT` est utilisée

### Commandes utiles

```bash
# Voir les logs en temps réel
railway logs

# Connecter une base de données locale
railway connect

# Redéployer
railway up

# Variables d'environnement
railway variables
```

## 🚀 Optimisations production

### Performance

1. **Workers Gunicorn**: Ajustés automatiquement selon les ressources
2. **Database connection pooling**: Configuré dans SQLAlchemy
3. **Cache Redis**: Activé automatiquement si Redis est disponible

### Sécurité

1. **HTTPS**: Forcé automatiquement par Railway
2. **Headers de sécurité**: Configurés via Talisman
3. **Variables sensibles**: Stockées sécurisément dans Railway

### Monitoring

1. **Health checks**: `/health` endpoint configuré
2. **Error tracking**: Configurable avec Sentry (voir variables d'env)
3. **Performance**: Monitoring intégré Railway

## 📚 Ressources

- [Documentation Railway](https://docs.railway.app/)
- [Railway Templates](https://railway.app/templates)
- [Communauté Railway](https://railway.app/discord)

## ⚡ Déploiement one-click

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/wow-flask)

Cliquez sur le bouton ci-dessus pour déployer automatiquement avec PostgreSQL et Redis préconfigurés.