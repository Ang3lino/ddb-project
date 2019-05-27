# ddb-project Fragmentador de bases de datos

Dependencias:
-python 3
-mysql
-flask flask-mysql (bibliotecas de python)

```
sudo apt install mysql-server flask 
pip3 install flask flask-mysql
```
si hubo error
> pip3 install flask flask-mysql --user

#### Requerimientos: 
1. Tener una base de datos cargada, para iniciar la base en donde se probo esta aplicacion hacer **source db/load_see.sql** en mysql.
2. Tener el nombre de usuario y contraseña en config.py

#### Ejecucion de la aplicacion
>python app.py 
o bien 
>python3 app.py

Ahora podra ver la renderizacion de la pagina poniendo 127.0.0.1:5000 en el navegador

