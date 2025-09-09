"""
Routes publiques pour l'application WoW Flask.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.tutorial import Tutorial
from app.models.category import Category
from app.models.tag import Tag

bp = Blueprint('public', __name__)


@bp.route('/')
def index():
    """Page d'accueil."""
    # Tutoriels récents
    recent_tutorials = Tutorial.get_recent(limit=6)
    
    # Tutoriels populaires  
    popular_tutorials = Tutorial.get_popular(limit=6)
    
    # Catégories principales
    categories = Category.get_ordered()
    
    return render_template('public/index.html',
                         recent_tutorials=recent_tutorials,
                         popular_tutorials=popular_tutorials,
                         categories=categories)


@bp.route('/tutos')
def tutorials():
    """Liste des tutoriels avec filtres."""
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    
    # TODO: Implémenter la pagination et les filtres
    tutorials = Tutorial.get_published(limit=20)
    
    return render_template('public/tutorials.html',
                         tutorials=tutorials)


@bp.route('/tutos/<slug>')
def tutorial_detail(slug):
    """Page détail d'un tutoriel."""
    tutorial = Tutorial.get_by_slug(slug)
    if not tutorial:
        return render_template('errors/404.html'), 404
    
    # Incrémenter les vues
    tutorial.increment_views()
    
    return render_template('public/tutorial_detail.html',
                         tutorial=tutorial)


@bp.route('/categories')
def categories():
    """Liste des catégories."""
    categories = Category.get_ordered()
    return render_template('public/categories.html', categories=categories)


@bp.route('/categories/<slug>')
def category_detail(slug):
    """Tutoriels d'une catégorie."""
    category = Category.get_by_slug(slug)
    if not category:
        return render_template('errors/404.html'), 404
    
    tutorials = Tutorial.get_by_category(category.id)
    return render_template('public/category_detail.html',
                         category=category,
                         tutorials=tutorials)


@bp.route('/tags')
def tags():
    """Liste des tags."""
    popular_tags = Tag.get_popular(limit=50)
    return render_template('public/tags.html', tags=popular_tags)


@bp.route('/tags/<slug>')
def tag_detail(slug):
    """Tutoriels d'un tag."""
    tag = Tag.get_by_slug(slug)
    if not tag:
        return render_template('errors/404.html'), 404
    
    tutorials = Tutorial.get_by_tag(tag.id)
    return render_template('public/tag_detail.html',
                         tag=tag,
                         tutorials=tutorials)


@bp.route('/search')
def search():
    """Page de recherche."""
    query = request.args.get('q', '')
    
    # TODO: Implémenter la recherche
    results = []
    
    return render_template('public/search.html',
                         query=query,
                         results=results)


@bp.route('/a-propos')
def about():
    """Page à propos."""
    return render_template('public/about.html')


@bp.route('/contact')
def contact():
    """Page de contact.""" 
    return render_template('public/contact.html')


# SEO et métadonnées
@bp.route('/sitemap.xml')
def sitemap():
    """Sitemap XML."""
    # TODO: Implémenter le sitemap
    return '', 200, {'Content-Type': 'application/xml'}


@bp.route('/robots.txt')
def robots():
    """Fichier robots.txt."""
    robots_content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dashboard/
Disallow: /auth/

Sitemap: {base_url}/sitemap.xml
""".format(base_url=request.url_root.rstrip('/'))
    
    return robots_content, 200, {'Content-Type': 'text/plain'}


@bp.route('/feed.xml')
def rss_feed():
    """Flux RSS des derniers tutoriels."""
    # TODO: Implémenter le flux RSS
    return '', 200, {'Content-Type': 'application/rss+xml'}