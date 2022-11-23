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
import csv, io
from import_export import resources
from django.contrib.auth.hashers import make_password #USER > PASSWORD

#REQUISITOS PARA EL CORREO
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site #para obtener el dominio actual
import threading


#FUNCIONES_GENERALES##################################################################################
def create_mail(user, cc_mails, subject, template_path, context):

    template = get_template(template_path)
    content = template.render(context)

    mail = EmailMultiAlternatives(
        subject=subject,
        body=content,
        from_email=settings.EMAIL_HOST_USER,
        to=[
            user.email,
        ],
        cc= cc_mails
    )

    mail.attach_alternative(content, 'text/html')
    mail.send(fail_silently=False)
    #return mail


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
            ticket = Ticket.objects.get(id=ticket.id)
            registro =  ticket.registro.order_by('-id')[:1].values()
            read = Registro.objects.filter(ticket__id=ticket.id).order_by('-id')[:1]
        
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
            #ENVIAR CORREO
            cc_mails = ['ldxsoria@gmail.com', 'ldxnotes@gmail.com']
            subject= f'Ticket #{new_ticket.id}'
            template_path = 'tickets/correo_new_ticket.html'
            dominio = get_current_site(request).domain
            context = {
                'user' : request.user,
                'ticket' : new_ticket,
                'dominio' : dominio
            }
            #ENVIO NORMAL
            #new_ticket_mail = create_mail(request.user, cc_mails, subject, template_path, context)
            #new_ticket_mail.send(fail_silently=False)
            
            thread = threading.Thread(
                target= create_mail,
                args=(request.user, cc_mails, subject, template_path, context)
            )
            thread.start()
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

@login_required
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
    #ticket.fecha_cierre = Timezon
    #ticket.hora_cierre =
    new_registro.save()
    ticket.registro.add(new_registro)
    ticket.save()
   
    return redirect('tickets')
#EXPORT VIEWS##########################################################################################

@login_required       
def export_csv(request):
    if request.user.is_staff:
        tickets_resource = resources.modelresource_factory(model=Ticket)()
        dataset = tickets_resource.export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'atachment; filename="tickets_export.csv"'
        return response

#IMPORT VIEWS##########################################################################################

@login_required    
def import_csv(request):

    if request.user.is_staff:
        #libreria import_export
        import tablib

        with open("example.csv", "r") as csv_file:
            usuarios_resource = resources.modelresource_factory(model=User)()
            dataset = tablib.Dataset(headers=[field.name for field in User._meta.fields]).load(csv_file)
            result = usuarios_resource.import_data(dataset, dry_run=True)
        if not result.has_errors():
            usuarios_resource.import_data(dataset, dry_run=False)
        return HttpResponse(
            "Users successfully imported"
        )

@login_required
def auto_import(request, model):
    if request.user.is_staff:
        template = 'general/import.html'
        context = {

        }
        if model == 'areas' or model == 'users' or model == 'estados-ticket':
            if request.method == 'GET':
                return render(request, template, context)
            try:
                csv_file = request.FILES['file']
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string)

                if model == 'areas':
                    for column in csv.reader(io_string, delimiter=',', quotechar='|'):
                        created = Area.objects.update_or_create(
                            cod_area=column[0],
                            descripcion=column[1],
                            siglas=column[2],
                        )

                elif model == 'users':
                    for column in csv.reader(io_string, delimiter=',', quotechar='|'):
                        created = User.objects.update_or_create(
                            username=column[0],
                            first_name=column[1],
                            last_name=column[2],
                            email=column[3],
                            password=make_password(column[4])
                        )
                elif model == 'estados-ticket':
                    for column in csv.reader(io_string, delimiter=',', quotechar='|'):
                        created = EstadosTicket.objects.update_or_create(
                            estado=column[0],
                            desc=column[1],
                        )                    

                else:
                    return redirect('main')

                context = {
                    'type' : 'success',
                    'alert' : '¡El CSV fue cargardo con exito!'
                }
                return render(request, template, context)
            except:
                context = {
                'type' : 'danger',
                'alert' : 'Selecciona un .CSV'
                }
                return render(request, template, context)
        else:
            return redirect('main')
            



    