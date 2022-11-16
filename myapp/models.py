from unittest.util import _MAX_LENGTH
from django.db import models #DJANGO DEFAULT
from django.db.models.signals import post_save #COLABORADOR
from django.dispatch import receiver #COLABORADOR
from django.contrib.auth.models import User #COLABORADOR

# Create your models here.
ESTADOS_TICKET = [
        (1, 'Registrado'),
        (2, 'En espera'),
        (3, 'En proceso'),
        (4, 'Atendiendo'),
        (5, 'Cancelado'),

    ]

class Registro(models.Model):
    #FK
    responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.SmallIntegerField(blank=False, choices=ESTADOS_TICKET, default=1)
    comment_estado = models.TextField(max_length=120, blank=True)
    fecha_estado = models.DateField(auto_now_add=True)
    hora_estado = models.TimeField(auto_now_add=True)


class Ticket(models.Model):
    asunto = models.CharField(max_length=50,blank=False)
    descripcion = models.TextField(max_length=120,blank=True)
    lugar = models.CharField(max_length=50, blank=False)
    fecha_solicitud = models.DateField(auto_now_add=True)
    hora_solicitud = models.TimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    #UN TICKET TIENE MUCHOS REGISTROS
    registo = models.ManyToManyField(Registro, blank=True)
    #FK
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE)


class Area(models.Model):
    cod_area = models.CharField(primary_key=True, max_length=10)
    descripcion = models.CharField(max_length=35)
    #UN AREA TIENE MUCHOS TICKTES
    ticket = models.ManyToManyField(Ticket, blank=True)

class Zona(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=25)
    #UN ZONA TIENE MUCHOS AREAS
    area = models.ManyToManyField(Area, blank=True)

