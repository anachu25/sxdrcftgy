from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, EventoSerializer
from .models import Evento
import datetime


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            # Obtener el rol del usuario a través de su perfil
            rol = 'sin_rol'
            nombre = user.get_full_name() or user.username
            roles = []
            try:
                perfil = user.perfil
                rol = perfil.rol.nombre
                roles = perfil.get_all_roles()
            except Exception:
                roles = [rol]

            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'rol': rol,
                'roles': roles,
                'nombre': nombre,
                'username': user.username,
                'mensaje': 'Login exitoso'
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class EventoListCreateView(generics.ListCreateAPIView):
    queryset = Evento.objects.all().order_by('fecha', 'hora_inicio')
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    ALLOWED_ROLES = {
        'admin', 'secretario', 'secretaria', 'director', 'directivo', 'jefe_area',
        'preceptor', 'jefe_preceptores', 'j_preceptores', 'profesor', 'jefe_departamento',
    }

    ROLE_TYPE_MAP = {
        'admin': 'admin',
        'secretario': 'admin',
        'secretaria': 'admin',
        'director': 'admin',
        'directivo': 'admin',
        'jefe_area': 'admin',
        'preceptor': 'preceptor',
        'jefe_preceptores': 'preceptor',
        'j_preceptores': 'preceptor',
        'profesor': 'docente',
        'jefe_departamento': 'docente',
    }

    def perform_create(self, serializer):
        user = self.request.user
        perfil = getattr(user, 'perfil', None)
        if not perfil:
            raise PermissionDenied('Usuario no autorizado.')

        rol = perfil.rol.nombre
        if rol not in self.ALLOWED_ROLES and not any(r in self.ALLOWED_ROLES for r in perfil.get_all_roles()):
            raise PermissionDenied('No estás autorizado para crear eventos.')

        fecha = serializer.validated_data.get('fecha')
        hora_inicio = serializer.validated_data.get('hora_inicio')
        hora_fin = serializer.validated_data.get('hora_fin')

        evento_hora = hora_inicio or hora_fin or datetime.time(0, 0)
        event_datetime = datetime.datetime.combine(fecha, evento_hora)
        if timezone.is_naive(event_datetime):
            event_datetime = timezone.make_aware(event_datetime, datetime.timezone.utc)

        if event_datetime <= timezone.now():
            raise serializers.ValidationError({'fecha': 'El evento debe programarse para una fecha y hora futura.'})

        tipo = self.ROLE_TYPE_MAP.get(rol, 'otro')
        serializer.save(creado_por=user, tipo=tipo)
