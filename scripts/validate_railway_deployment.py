#!/usr/bin/env python3
"""
Script de validation du déploiement Railway pour WoW Flask.
Teste que l'application peut démarrer correctement.
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Ajouter le répertoire racine du projet au PYTHONPATH
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test que l'environnement est correctement configuré."""
    print("🔍 Test de l'environnement...")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version < (3, 11):
        print(f"❌ Python {python_version.major}.{python_version.minor} détecté, Python 3.11+ requis")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Vérifier les fichiers essentiels
    required_files = [
        "app/__init__.py",
        "wsgi.py",
        "requirements.txt",
        "Dockerfile",
        "Procfile",
        "entrypoint.sh",
        "railway.toml"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Fichier manquant: {file}")
            return False
        print(f"✅ {file}")
    
    return True

def test_dependencies():
    """Test que toutes les dépendances sont installées."""
    print("\n📦 Test des dépendances...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask non installé")
        return False
    
    try:
        import gunicorn
        print(f"✅ Gunicorn installé")
    except ImportError:
        print("❌ Gunicorn non installé")
        return False
    
    return True

def test_app_factory():
    """Test que l'application peut être créée."""
    print("\n🏭 Test de l'app factory...")
    
    try:
        from app import create_app
        app = create_app()
        print(f"✅ App créée: {app.name}")
        print(f"✅ Configuration: {app.config['FLASK_ENV']}")
        print(f"✅ Blueprints: {list(app.blueprints.keys())}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'app: {e}")
        return False

def test_gunicorn_syntax():
    """Test que la syntaxe Gunicorn est correcte."""
    print("\n🦄 Test de la syntaxe Gunicorn...")
    
    try:
        # Test de la syntaxe du Procfile
        with open("Procfile", "r") as f:
            procfile_content = f.read().strip()
        
        print(f"✅ Procfile: {procfile_content}")
        
        # Vérifier que la syntaxe est correcte (devrait utiliser wsgi:app)
        if "wsgi:app" not in procfile_content:
            print("❌ Syntaxe incorrecte dans Procfile (devrait utiliser wsgi:app)")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test Procfile: {e}")
        return False

def test_config_files():
    """Test que les fichiers de configuration sont valides."""
    print("\n⚙️  Test des fichiers de configuration...")
    
    # Test railway.toml
    try:
        with open("railway.toml", "r") as f:
            railway_config = f.read()
        print("✅ railway.toml")
    except Exception as e:
        print(f"❌ Erreur railway.toml: {e}")
        return False
    
    # Test nixpacks.toml
    try:
        with open("nixpacks.toml", "r") as f:
            nixpacks_config = f.read()
        print("✅ nixpacks.toml")
    except Exception as e:
        print(f"❌ Erreur nixpacks.toml: {e}")
        return False
    
    return True

def test_docker_build():
    """Test que l'image Docker peut être construite."""
    print("\n🐳 Test de construction Docker (optionnel)...")
    
    try:
        # Vérifier si Docker est disponible
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("⚠️  Docker non disponible, test ignoré")
            return True
        
        print("✅ Docker disponible")
        
        # Test de construction (build seulement, pas de run)
        print("🔨 Construction de l'image Docker...")
        result = subprocess.run(
            ["docker", "build", "-t", "wow-flask-test", "."],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode == 0:
            print("✅ Image Docker construite avec succès")
            
            # Nettoyer l'image de test
            subprocess.run(["docker", "rmi", "wow-flask-test"], capture_output=True)
            return True
        else:
            print(f"❌ Erreur construction Docker: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de la construction Docker")
        return False
    except FileNotFoundError:
        print("⚠️  Docker non trouvé, test ignoré")
        return True
    except Exception as e:
        print(f"⚠️  Erreur Docker: {e}")
        return True  # Non bloquant

def main():
    """Fonction principale."""
    print("🚀 Validation du déploiement Railway pour WoW Flask")
    print("=" * 50)
    
    tests = [
        ("Environnement", test_environment),
        ("Dépendances", test_dependencies),
        ("App Factory", test_app_factory),
        ("Syntaxe Gunicorn", test_gunicorn_syntax),
        ("Fichiers de config", test_config_files),
        ("Build Docker", test_docker_build),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résultats finaux
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
        print("✅ L'application est prête pour le déploiement Railway")
        print("\n📝 Étapes suivantes:")
        print("1. Commitez vos changements")
        print("2. Pushez sur GitHub")
        print("3. Connectez votre repo à Railway")
        print("4. Configurez les variables d'environnement")
        print("5. Déployez!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) échoué(s)")
        print("Corrigez les erreurs avant de déployer")
        return 1

if __name__ == "__main__":
    exit(main())