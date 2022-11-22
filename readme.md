# Clonar proyecto
Primero clonamos el proyecto

# Configurar entorno
Se recomienda instalar y usar virtualenv, para luego iniciar el entorno
```bash
virtualenv venv
source venv/bin/activate
```
Instalamos las dependencias
```bash
pip install -r requirements.py
```

# Configurar la base de datos
Realizamos las migraciones 

```bash
python manage.py makimigrations
python manage.py migrate
```
Creamos el usuario administrador para que pueda funcionar el proyecto
```bash
python manage.py createsuperuser
```

# Ejecución
Finamente, iniciamos el proyecto
```bash
python manage.py runserver
```

# Orientación
1) Ingresamos al {dominio}/admin con la cuenta de superusuario
2) Creamos las áreas (para que funcione el formulario para crear tickets)