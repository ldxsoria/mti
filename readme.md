# Requisitos
1) Instalar GIT, Python3 y tener pip-python3
2) Clonar el proyecto

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

# ¿Comó usar la aplicación?
1) Ingresamos al {{dominio}}/admin con la cuenta de superusuario
2) Ingresamos a {{dominio}}/ y importamos lo siguiente desde un .csv:
* Estados de los tickets de atención (int:estado, str:desc)
* Usuarios (username,first_name,last_name,email,password)
* Areas (str:cod_area, str: descrpition, str:siglas)