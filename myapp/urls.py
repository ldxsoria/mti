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
    path('ticket/<int:ticket_id>/progress', views.progress_ticket, name = 'progress_ticket'),
    path('ticket/<int:ticket_id>/add', views.add_registro_ticket, name = 'add_registro_ticket'),
    path('ticket/<int:ticket_id>/area', views.add_ticket_to_area, name = 'add_ticket_to_area'),
    path('ticket/<int:ticket_id>/<str:cod_area>/del', views.delete_ticket_to_area, name = 'delete_ticket_to_area'),
    path('ticket/<int:ticket_id>/completed', views.completed_ticket, name = 'completed_ticket'),
    path('tickets/completed', views.completed_tickets, name = 'completed_tickets')
    #URL TESTING
    ]