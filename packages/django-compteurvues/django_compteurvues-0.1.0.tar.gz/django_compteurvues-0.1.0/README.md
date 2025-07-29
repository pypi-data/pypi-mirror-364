# django-compteurvues

"djangocompteurvues" est un package Django réutilisable permettant de compter et afficher le nombre de vues sur n’importe quel objet de votre projet Django (articles, pages, produits, etc.).

Il utilise la puissance des relations génériques (`GenericForeignKey`) pour s’adapter à tout modèle, et fournit une interface simple avec une vue et un template minimaliste.


## Fonctionnalités

- Comptabilisation automatique des vues sur n’importe quel modèle Django.
- Généricité totale grâce à `ContentType` et `GenericForeignKey`.
- Interface simple (pas de JavaScript, juste du HTML).
- L'intégration est facile dans n’importe quel projet Django.
- Gestion des compteurs visible et modifiable dans l’admin Django.

## Prérequis
Ce package est une app Django.
Vous devez déjà avoir un projet Django existant (avec un manage.py).

## Installation

1. Installez le package via pip :

    pip install django-compteurvues

2. Ajoutez `compteurvues` à la liste `INSTALLED_APPS` de votre fichier `settings.py` :

    INSTALLED_APPS = [
        ...
        'compteurvues',
    ]

3. Lancez les migrations :

    python manage.py migrate


## Utilisation
1. Ajoutez le compteur dans votre vue :

    from compteurvues.utils import ajouter_vue

    def detail_article(request, pk):
        article = get_object_or_404(Article, pk=pk)
        ajouter_vue(request, article)  # Enregistre une vue
        return render(request, "article_detail.html", {"article": article})

2. Affichez le nombre de vues dans votre template :

    <p>{{ article.vues }} vues</p>

Exemple de modèle personnalisé

    from compteurvues.models import VueCompteurMixin

    class Article(VueCompteurMixin, models.Model):
        titre = models.CharField(max_length=200)
        contenu = models.TextField()

-ADMIN

Le modèle `CompteurVue` est visible dans l’interface d’administration Django.
