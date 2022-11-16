from django.urls import path
from . import views

#
urlpatterns = [
    #URL GLOBALES
    path('', views.signin, name = 'singin'),
    path('main/', views.main, name = 'main'),
    path('logout/', views.signout, name = 'logout'),
    #URL TICKETS
    path('tickets/', views.tickets, name = 'tickets'),
    path('ticket/create', views.create_ticket, name = 'create_ticket' ),
    path('ticket/<int:ticket_id>/progress', views.progress_ticket, name = 'progress_ticket')
    ]