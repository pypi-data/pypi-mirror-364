from django.shortcuts import get_object_or_404, render
from django.contrib.contenttypes.models import ContentType
from .models import CompteurVue


def enregistrer_vue(request, app_label, model, object_id):
    content_type = get_object_or_404(ContentType, app_label=app_label, model=model)

    compteur, _ = CompteurVue.objects.get_or_create(
        content_type=content_type,
        object_id=object_id
    )

    compteur.total_vues += 1
    compteur.save()

    return render(request, "compteurvues/compteur.html", {"compteur": compteur})
