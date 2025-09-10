#!/bin/bash
set -e

echo "🚀 Démarrage de WoW Flask..."

# Définir le port par défaut si PORT n'est pas défini (Railway/Render style)
export PORT=${PORT:-8000}
echo "📡 Port configuré: $PORT"

# Attendre que la base de données soit prête (si PostgreSQL)
if [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Attente de la base de données PostgreSQL..."
    
    # Extraire les informations de connexion depuis DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Attendre que PostgreSQL soit prêt (avec timeout)
    timeout=30
    count=0
    while ! nc -z $DB_HOST ${DB_PORT:-5432}; do
        echo "⏳ PostgreSQL n'est pas encore prêt, attente... ($count/$timeout)"
        sleep 1
        count=$((count + 1))
        if [ $count -ge $timeout ]; then
            echo "⚠️  Timeout atteint, continuation sans vérification DB"
            break
        fi
    done
    
    if [ $count -lt $timeout ]; then
        echo "✅ PostgreSQL est prêt !"
    fi
fi

# Exécuter les migrations de base de données
echo "📊 Exécution des migrations de base de données..."
flask --app app db upgrade 2>/dev/null || {
    echo "❌ Erreur lors des migrations, initialisation de la base..."
    flask --app app db init 2>/dev/null || echo "⚠️  Migrations déjà initialisées"
    flask --app app db migrate -m "Initial migration" 2>/dev/null || echo "⚠️  Migration existante"
    flask --app app db upgrade 2>/dev/null || echo "⚠️  Erreur de migration, continuation..."
}

# Créer les données initiales si nécessaire
if [[ "$AUTO_SEED" == "true" ]]; then
    echo "🌱 Création des données initiales..."
    python scripts/seed.py 2>/dev/null || echo "⚠️  Données déjà présentes ou script de seed manquant"
fi

# Créer les répertoires nécessaires
mkdir -p instance uploads logs

echo "✅ Initialisation terminée !"

# Exécuter la commande demandée
exec "$@"