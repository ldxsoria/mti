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
class EstadosTicket(models.Model):
    estado = models.SmallIntegerField(primary_key=True)
    desc = models.CharField(max_length=20)

    def __str__(self):
        return self.desc

class Registro(models.Model):
    #FK
    responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    #estado = models.SmallIntegerField(blank=False, choices=ESTADOS_TICKET, default=1)
    estado = models.ForeignKey(EstadosTicket, on_delete=models.CASCADE)
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
    fecha_cierre= models.DateField(auto_now_add=True,null=True, blank=True)
    hora_cierre = models.TimeField(auto_now_add=True,null=True, blank=True)
    #UN TICKET TIENE MUCHOS REGISTROS
    registro = models.ManyToManyField(Registro, blank=True)
    #FK
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Ticket {self.id} - by {self.solicitante.username}'


class Area(models.Model):
    cod_area = models.CharField(primary_key=True, max_length=10)
    descripcion = models.CharField(max_length=35)
    siglas = models.CharField(max_length=50, blank=True)
    #UN AREA TIENE MUCHOS TICKTES
    ticket = models.ManyToManyField(Ticket, blank=True)

    def __str__(self):
        return f'{self.descripcion}'
        
class Zona(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=25)
    #UN ZONA TIENE MUCHOS AREAS
    area = models.ManyToManyField(Area, blank=True)

