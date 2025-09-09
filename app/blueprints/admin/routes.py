"""
Routes d'administration pour l'application WoW Flask.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

bp = Blueprint('admin', __name__)


def admin_required(f):
    """Décorateur pour vérifier les droits d'admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès refusé', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    """Décorateur pour vérifier les droits de modérateur."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator:
            flash('Accès refusé', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@moderator_required
def index():
    """Tableau de bord admin."""
    # TODO: Statistiques et métriques
    return render_template('admin/index.html')


@bp.route('/users')
@login_required
@admin_required
def users():
    """Gestion des utilisateurs."""
    # TODO: Liste des utilisateurs avec pagination
    return render_template('admin/users.html')


@bp.route('/tutorials')
@login_required
@moderator_required
def tutorials():
    """Gestion des tutoriels."""
    # TODO: Liste des tutoriels avec filtres
    return render_template('admin/tutorials.html')


@bp.route('/tutorials/review')
@login_required
@moderator_required
def review_queue():
    """File d'attente de modération."""
    # TODO: Tutoriels en attente de modération
    return render_template('admin/review_queue.html')


@bp.route('/tutorials/<int:id>/approve', methods=['POST'])
@login_required
@moderator_required
def approve_tutorial(id):
    """Approuver un tutoriel."""
    # TODO: Approuver et logger l'action
    flash('Tutoriel approuvé', 'success')
    return redirect(url_for('admin.review_queue'))


@bp.route('/tutorials/<int:id>/reject', methods=['POST'])
@login_required
@moderator_required
def reject_tutorial(id):
    """Rejeter un tutoriel."""
    # TODO: Rejeter et logger l'action
    flash('Tutoriel rejeté', 'info')
    return redirect(url_for('admin.review_queue'))


@bp.route('/comments')
@login_required
@moderator_required
def comments():
    """Modération des commentaires."""
    # TODO: Commentaires signalés
    return render_template('admin/comments.html')


@bp.route('/categories')
@login_required
@admin_required
def categories():
    """Gestion des catégories."""
    # TODO: CRUD des catégories
    return render_template('admin/categories.html')


@bp.route('/tags')
@login_required
@moderator_required
def tags():
    """Gestion des tags."""
    # TODO: CRUD des tags
    return render_template('admin/tags.html')


@bp.route('/invites')
@login_required
@admin_required
def invites():
    """Gestion des invitations."""
    # TODO: Créer et gérer les invites
    return render_template('admin/invites.html')


@bp.route('/logs')
@login_required
@admin_required
def logs():
    """Logs de modération et audit."""
    # TODO: Affichage des logs
    return render_template('admin/logs.html')


@bp.route('/settings')
@login_required
@admin_required
def settings():
    """Paramètres du site."""
    # TODO: Configuration du site
    return render_template('admin/settings.html')