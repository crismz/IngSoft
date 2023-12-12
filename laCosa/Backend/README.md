# La Cosa (backend).

## Descripción

Este es un respositorio correspondiente al backend de una versión online del juego "La Cosa", el cuál es desarrollado para la materia Ingeniería del Software dictada el año 2023 en FAMAF.

## Tabla de Contenidos

1. [Crear entorno virtual](#crear-entorno-virtual)
2. [Comandos útiles](#comandos-útiles)
3. [Estructura de directorios](#estructura-de-directorios)

## Crear entorno virtual.

En Python es una buena práctica trabajar dentro de un entorno virtual, ya que nos facilitará gestionar las dependencias de una manera cómoda y sencilla.
Usaremos la versión de Python 3.10.11 para el funcionamiento de PonyORM.

### Instalar virtualenv:

Para poder crear un entorno virtual vamos a tener que instalar `virtualenv` de la siguiente manera:

```bash
pip install virtualenv
```

### Crear el entorno virtual:

Luego, vamos a crear nuestro entorno virtual de la siguiente manera:

```bash
virtualenv -p 3.10 .venv
```

Dicho comando nos creará un directorio llamado `.venv`, el cuál contendrá la información de nuestro entorno virtual.

### Ejecutar el entorno virtual:

Finalmente, para poder ejecutar nuestro entorno virtual, vamos a tener que hacer alguno de los siguientes comandos en función de su sistema operativo:

- `Para macOS y Linux:`

  ```bash
  source .venv/bin/activate
  ```

- `Para Windows (powershell):`
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

Y notaremos que el comando ha funcionado si ahora nos aparece un `(.venv)` al inicio del prompt en la consola.

A lo largo del proyecto vamos a trabajar con el entrono virtual activado.

## Comandos útiles.

### actualizar requirements.txt:

En el archivo `requirements.txt` se encuentran todos los módulos necesarios que tendrá nuestro proyecto. Si se agrega un nuevo módulo al proyecto, debemos actualizar dicho archivo usando el siguiente comando: 

```bash
pip freeze > requirements.txt
```

### instalar módulos necesarios:

Para instalar los módulos que necesita nuestro proyecto, haremos lo siguiente:

```bash
pip install -r requirements.txt
```

Y esto nos instalará todos los módulos necesarios para hacer correr el proyecto.

### Correr el proyecto:

Para correr el proyecto vamos a tener que utilizar `uvicorn`. Para lograr correrlo, tendremos que posicionarnos en el directorio llamado `src` y luego ejecutar el siguiente comando:

```bash
uvicorn main:app --reload
```

Esto nos dará mucha información, pero nos interesará aquella que se parezca a lo siguiente:

```bash
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Y luego podemos probar nuestro backend en la dirección mostrada.
