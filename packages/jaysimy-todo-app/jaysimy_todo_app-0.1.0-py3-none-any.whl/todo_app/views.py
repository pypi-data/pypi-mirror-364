from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Tache
from .forms import TacheForm

class TacheListView(ListView):
    model = Tache
    template_name = 'todo_app/list.html'
    context_object_name = 'taches'

class TacheCreateView(CreateView):
    model = Tache
    form_class = TacheForm
    template_name = 'todo_app/form.html'
    success_url = reverse_lazy('todo_app:liste')

class TacheUpdateView(UpdateView):
    model = Tache
    form_class = TacheForm
    template_name = 'todo_app/form.html'
    success_url = reverse_lazy('todo_app:liste')

class TacheDeleteView(DeleteView):
    model = Tache
    template_name = 'todo_app/delete.html'
    success_url = reverse_lazy('todo_app:liste')
