"""
Routes d'authentification pour l'application WoW Flask.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        # TODO: Implémenter la logique de connexion
        flash('Connexion en cours de développement', 'info')
    
    return render_template('auth/login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Page d'inscription."""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        # TODO: Implémenter la logique d'inscription
        flash('Inscription en cours de développement', 'info')
    
    return render_template('auth/signup.html')


@bp.route('/logout')
@login_required
def logout():
    """Déconnexion."""
    logout_user()
    flash('Vous êtes maintenant déconnecté', 'info')
    return redirect(url_for('public.index'))


@bp.route('/reset', methods=['GET', 'POST'])
def reset_request():
    """Demande de réinitialisation de mot de passe."""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        # TODO: Implémenter l'envoi d'email de reset
        flash('Email de réinitialisation envoyé', 'info')
    
    return render_template('auth/reset_request.html')


@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Réinitialisation de mot de passe avec token."""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    # TODO: Vérifier le token et permettre la réinitialisation
    return render_template('auth/reset_password.html')


@bp.route('/verify/<token>')
def verify_email(token):
    """Vérification d'adresse email."""
    # TODO: Vérifier le token et marquer l'email comme vérifié
    flash('Email vérifié avec succès', 'success')
    return redirect(url_for('public.index'))


# Battle.net OAuth (si activé)
@bp.route('/bnet')
def bnet_login():
    """Connexion Battle.net OAuth."""
    # TODO: Implémenter l'OAuth Battle.net
    flash('Connexion Battle.net en cours de développement', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/bnet/callback')
def bnet_callback():
    """Callback OAuth Battle.net."""
    # TODO: Gérer le callback OAuth
    return redirect(url_for('public.index'))