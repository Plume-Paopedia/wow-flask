#!/bin/bash
set -e

echo "🚀 Démarrage de WoW Flask..."

# Attendre que la base de données soit prête (si PostgreSQL)
if [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Attente de la base de données PostgreSQL..."
    
    # Extraire les informations de connexion depuis DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Attendre que PostgreSQL soit prêt
    while ! nc -z $DB_HOST ${DB_PORT:-5432}; do
        echo "⏳ PostgreSQL n'est pas encore prêt, attente..."
        sleep 1
    done
    echo "✅ PostgreSQL est prêt !"
fi

# Exécuter les migrations de base de données
echo "📊 Exécution des migrations de base de données..."
flask --app app db upgrade || {
    echo "❌ Erreur lors des migrations, initialisation de la base..."
    flask --app app db init
    flask --app app db migrate -m "Initial migration"
    flask --app app db upgrade
}

# Créer les données initiales si nécessaire
if [[ "$AUTO_SEED" == "true" ]]; then
    echo "🌱 Création des données initiales..."
    python scripts/seed.py || echo "⚠️  Données déjà présentes ou erreur de seeding"
fi

# Créer les répertoires nécessaires
mkdir -p instance uploads logs

echo "✅ Initialisation terminée !"

# Exécuter la commande demandée
exec "$@"