"""
Routes du tableau de bord utilisateur pour l'application WoW Flask.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Tableau de bord principal."""
    # Statistiques utilisateur
    user_tutorials = current_user.tutorials.all()
    user_favorites = current_user.favorites.all()
    
    return render_template('dashboard/index.html',
                         user_tutorials=user_tutorials,
                         user_favorites=user_favorites)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Page de profil utilisateur."""
    if request.method == 'POST':
        # TODO: Mettre à jour le profil
        flash('Profil mis à jour', 'success')
    
    return render_template('dashboard/profile.html')


@bp.route('/tutorials')
@login_required
def my_tutorials():
    """Mes tutoriels."""
    tutorials = current_user.tutorials.order_by('created_at desc').all()
    return render_template('dashboard/tutorials.html', tutorials=tutorials)


@bp.route('/tutorials/new', methods=['GET', 'POST'])
@login_required
def new_tutorial():
    """Créer un nouveau tutoriel."""
    if not current_user.is_author:
        flash('Vous n\'avez pas les permissions pour créer des tutoriels', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # TODO: Créer le tutoriel
        flash('Tutoriel créé', 'success')
        return redirect(url_for('dashboard.my_tutorials'))
    
    return render_template('dashboard/tutorial_form.html')


@bp.route('/tutorials/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tutorial(id):
    """Éditer un tutoriel."""
    # TODO: Vérifier les permissions et éditer
    return render_template('dashboard/tutorial_form.html')


@bp.route('/favorites')
@login_required
def favorites():
    """Mes favoris."""
    favorites = current_user.favorites.order_by('created_at desc').all()
    return render_template('dashboard/favorites.html', favorites=favorites)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Paramètres du compte."""
    if request.method == 'POST':
        # TODO: Mettre à jour les paramètres
        flash('Paramètres mis à jour', 'success')
    
    return render_template('dashboard/settings.html')