from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class CompteurVue(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contenu = GenericForeignKey('content_type', 'object_id')

    total_vues = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.content_type} - {self.object_id} ({self.total_vues} vues)"
