from django.urls import path
from .views import LoginView, EventoListCreateView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('eventos/', EventoListCreateView.as_view(), name='eventos'),
]