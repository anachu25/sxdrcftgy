from rest_framework import serializers
from .models import Evento

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = [
            'id',
            'titulo',
            'descripcion',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'lugar',
            'ciclo',
            'curso',
            'tipo',
            'creado_por',
        ]
        read_only_fields = ['id', 'tipo', 'creado_por']