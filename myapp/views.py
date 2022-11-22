from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import  AuthenticationForm #SIGNIN

#MODELOS
from .models import Ticket, EstadosTicket, Registro, Area

#PROJECTS ROUTES
from django.contrib.auth import login, logout, authenticate #para crear cookie de inicio de sesion
from django.contrib.auth.decorators import login_required #MAIN

#MY REQUIREMENTS
from .forms import TicketForm, RegistroForm

#IMPORT CSV REQUIREMENTS
import csv


##########################################################################################################

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
        tickets = Ticket.objects.all().exclude(completado=True).order_by('-id')
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
def completed_tickets(request):
    if request.user.is_staff:
        tickets = Ticket.objects.filter(completado=True).order_by('-id')
        for ticket in tickets:
            print(ticket.id)
            #registro = Registro.objects.filter(ticket__id=ticket.id).order_by('-id')[:1]
            #registro = Registro.objects.filter(ticket_id=ticket.id, ticket__completado=True)
            ticket = Ticket.objects.get(id=ticket.id)
            registro =  ticket.registro.order_by('-id')[:1].values()
            read = Registro.objects.filter(ticket__id=ticket.id).order_by('-id')[:1]
            #print(read.query)
        
        return render(request, 'tickets/completed_tickets.html', {
            'tickets': tickets,
            'title': 'Tickets completados',
        })
    else:
        tickets = Ticket.objects.filter(solicitante_id=request.user.id, completado=True).order_by('-id')
        return render(request, 'tickets/completed_tickets.html', {
            'tickets': tickets,
            'title': 'Mis tickets completados'
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
        areas = Area.objects.all()

        area_actual = Area.objects.filter(ticket=ticket_id)
        print(area_actual)

        return render(request, 'tickets/progress_ticket.html',{
            'registros':registros,
            'ticket': ticket,
            'form': form,
            'formAddRegistro' : formAddRegistro,
            'estados': estados,
            'areas': areas,
            'area_actual':area_actual
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
        return HttpResponse('ERROR add_registro_ticket')
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

@login_required
def add_ticket_to_area(request, ticket_id):
    if request.user.is_staff:
        if request.method == 'POST':
            #OBTENGO EL ID DE LA LA PETICION
            ticket = Ticket.objects.get(id=ticket_id)
            #OBTENGO EL AREA SELECIONA DE FORM POR EL POST
            area = Area.objects.get(cod_area=request.POST['area'])
            #ASIGNO EL TICKET A AREA
            area.ticket.add(ticket)
            area.save()
    
            return redirect('progress_ticket', ticket_id)

@login_required
def delete_ticket_to_area(request, ticket_id, cod_area):
    if request.user.is_staff:
        if request.method == 'POST':
            #OBTENGO EL ID DE LA LA PETICION
            ticket = Ticket.objects.get(id=ticket_id)
            #OBTENGO EL AREA SELECIONA DEL FORM
            area = Area.objects.get(cod_area=cod_area)
            #ASIGNO EL TICKET A AREA
            area.ticket.remove(ticket)
            area.save()
    
            return redirect('progress_ticket', ticket_id)

@login_required
def completed_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.completado = True
    new_registro = Registro(responsable=request.user, estado=EstadosTicket(estado=6))#6 - RESUELTO
    new_registro.save()
    ticket.registro.add(new_registro)
    ticket.save()
   
    return redirect('tickets')
        
def export_csv(request):
    #Query
    queryset = Ticket.objects.all()

    #Obtener campos del modelo
    options = Ticket._meta #AQUI ESTAN LOS CAMPOS DEL MODELO
    fields = [field.name for field in options.fields]
    #['id',...]

    #Construir respuesta
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = "atachment; filename=tickets.csv"

    writer = csv.writer(response)
    writer.writerow([options.get_field(field).verbose_name for field in fields])
    #Escribiendo data
    for obj in queryset:
        writer.writerow(getattr(obj, field) for field in fields)
    
    return response

def import_csv(request):
    usuarios = []
    with open("example.csv", "r") as csv_file:
        data = list(csv.reader(csv_file, delimiter=","))
        for row in data [1:]:
            usuarios.append(
                User(
                    username = row[0],
                    first_name = row[1],
                    last_name = row[2],
                    email=row[3]
                )
            )
    if len(usuarios) > 0:
        User.objects.bulk_create(usuarios)

    return HttpResponse("Successfully imported")