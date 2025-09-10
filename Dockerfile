# Multi-stage build pour optimiser la taille de l'image
FROM python:3.11-slim as base

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage de développement
FROM base as development

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY pyproject.toml ./
COPY requirements*.txt* ./

# Installer les dépendances Python (dev)
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e .[dev,admin]

# Copier le code source
COPY . .

# Changer le propriétaire des fichiers
RUN chown -R app:app /app

# Basculer vers l'utilisateur non-root
USER app

# Exposer le port
EXPOSE 5000

# Commande par défaut pour le développement
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]

# Stage de production
FROM base as production

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash --user-group app

# Créer les répertoires nécessaires
RUN mkdir -p /app /app/instance /app/uploads /app/logs && \
    chown -R app:app /app

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY pyproject.toml ./

# Installer les dépendances Python (production uniquement)
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e .

# Copier le code source (sans les fichiers de développement)
COPY --chown=app:app app ./app/
COPY --chown=app:app migrations ./migrations/
COPY --chown=app:app scripts ./scripts/
COPY --chown=app:app entrypoint.sh ./

# Rendre le script d'entrée exécutable
RUN chmod +x entrypoint.sh

# Basculer vers l'utilisateur non-root
USER app

# Exposer le port (Railway utilise la variable PORT)
EXPOSE ${PORT:-8000}

# Variables d'environnement de production
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Point de montage pour les volumes persistants
#VOLUME ["/app/instance", "/app/uploads", "/app/logs"]

# Commande par défaut
ENTRYPOINT ["./entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 wsgi:app"]

# Stage pour les tests
FROM development as testing

# Copier les tests
COPY tests/ ./tests/

# Installer les dépendances de test
RUN pip install -e .[dev]

# Commande pour les tests
CMD ["pytest", "--cov=app", "--cov-report=term-missing"]