from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import  AuthenticationForm #SIGNIN

#MODELOS
from .models import Ticket, EstadosTicket, Registro

#PROJECTS ROUTES
from django.contrib.auth import login, logout, authenticate #para crear cookie de inicio de sesion
from django.contrib.auth.decorators import login_required #MAIN

#MY REQUIREMENTS
from .forms import TicketForm, RegistroForm

# Create your views here.
def signin(request):
    #Si esta autenticado la pagina principal debe de ser main
    if request.user.is_authenticated:
        return render(request, 'main.html')
    else:
        if request.method == 'GET':
            return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
        else:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

            if user is None:
                return render(request, 'signin.html',{
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
            else:
                login(request, user)
                return redirect('main/')

@login_required
def signout(request):
    logout(request)
    return redirect('/')

@login_required
def main(request):
    return render(request, 'main.html')

#TICKET###############################################################################################

@login_required      
def tickets(request):
    if request.user.is_staff:
        #https://stackoverflow.com/questions/7590692/django-get-unique-object-list-from-queryset
        tickets = Ticket.objects.all().exclude(completado=True)
        #print(HistorialTicket.objects.order_by('id').distinct('id'))
        #print(HistorialTicket.objects.all().distinct('ticket_id'))
        #print(HistorialTicket.objects.order_by('-id').distinct())
        #x = Ticket.registros.estado
        #print(x)
        return render(request, 'tickets/tickets.html', {
            'tickets': tickets,
            'title': 'Tickets nuevos'
        })
    else:
        tickets = Ticket.objects.filter(solicitante_id=request.user.id).exclude(completado=True)
        return render(request, 'tickets/tickets.html', {
            'tickets': tickets,
            'title': 'Mis tickets pendientes'
        })

@login_required
def create_ticket(request):
    if request.method == 'GET':
        return render(request, "tickets/create_ticket.html", {
            'form': TicketForm
        })
    else:
        try:
            form = TicketForm(request.POST)
            #CREO EL TICKET
            new_ticket = form.save(commit=False)
            new_ticket.solicitante = request.user
            new_ticket.save()
            #AGREGO EL REGISTRO=Registrado AL TICKET
            new_registro = Registro(responsable=request.user, estado=EstadosTicket(estado=1), comment_estado='REGISTRO AUTOMATICO')
            new_registro.save()
            new_ticket.registro.add(new_registro)
            new_ticket.save()
            #------------
            return redirect('main')
            #return redirect(f'{new_ticket.id}/progress')
        except ValueError as e:
            return render(request, 'tickets/create_ticket.html', {
                'form': TicketForm,
                'error': f'Please provide valida data > {e}'
            })

@login_required
def progress_ticket(request, ticket_id):
    if request.method == 'GET':
        registros = Registro.objects.filter(ticket__id=ticket_id).order_by('-hora_estado', 'fecha_estado')
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        form = TicketForm(instance=ticket)
        formAddRegistro = RegistroForm(instance=ticket)
        estados = EstadosTicket.objects.all()

        return render(request, 'tickets/progress_ticket.html',{
            'registros':registros,
            'ticket': ticket,
            'form': form,
            'formAddRegistro' : formAddRegistro,
            'estados': estados
        })
    else:
        try:
            registros = Registro.objects.filter(ticket__id=ticket_id).order_by('-hora_estado', 'fecha_estado')
            ticket = get_object_or_404(Ticket, pk=ticket_id)
            form = TicketForm(request.POST or None, instance=ticket)
            if form.is_valid():
                form.save()
                return redirect('progress_ticket', ticket_id)
            else:
                print('ERROR'*100)
        except ValueError:
            return HttpResponse('No funciono ERROR')

def add_registro_ticket(request, ticket_id): 
    if request.method == 'GET':
        return HttpResponse('EROR')
    else:
        try:
            #print(request.POST['estado'])
            #print(request.POST['comentario'])
            #------------
            ticket = Ticket.objects.get(id=ticket_id)
            new_registro = Registro(responsable=request.user, estado=EstadosTicket(estado=request.POST['estado']), comment_estado=request.POST['comentario'])
            new_registro.save()
            ticket.registro.add(new_registro)
            ticket.save()
            #------------
            return redirect('progress_ticket', ticket_id)
        except ValueError as e:
            return render(request, 'tickets/create_ticket.html', {
                'form': TicketForm,
                'error': f'Please provide valida data > {e}'
            })