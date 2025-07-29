from django.urls import path
from . import views

app_name = 'todo_app'

urlpatterns = [
    path('', views.TacheListView.as_view(), name='liste'),
    path('ajouter/', views.TacheCreateView.as_view(), name='ajouter'),
    path('modifier/<int:pk>/', views.TacheUpdateView.as_view(), name='modifier'),
    path('supprimer/<int:pk>/', views.TacheDeleteView.as_view(), name='supprimer'),
]
