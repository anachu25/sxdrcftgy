from django.db import models
from django.contrib.auth.models import User


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    roles = models.ManyToManyField(Rol, blank=True, related_name='perfiles_extra')

    class Meta:
        db_table = 'perfil'

    def __str__(self):
        return f"{self.user.username} — {self.rol.nombre}"

    def get_all_roles(self):
        """Devuelve todos los roles del usuario (principal + extras) sin duplicados."""
        all_roles = [self.rol.nombre]
        for r in self.roles.all():
            if r.nombre not in all_roles:
                all_roles.append(r.nombre)
        return all_roles


class Evento(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=120, blank=True)
    ciclo = models.CharField(max_length=100, blank=True)
    curso = models.CharField(max_length=20, blank=True)
    tipo = models.CharField(max_length=50, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_creados')

    class Meta:
        db_table = 'evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"
