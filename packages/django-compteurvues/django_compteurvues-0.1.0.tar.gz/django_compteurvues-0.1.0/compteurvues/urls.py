from django.urls import path
from . import views

app_name = "compteurvues"

urlpatterns = [
    path("<str:app_label>/<str:model>/<int:object_id>/", views.enregistrer_vue, name="vue"),
]
