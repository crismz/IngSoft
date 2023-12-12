# La Cosa (frontend).

## Descripción.

Este es un respositorio correspondiente al frontend de una versión online del juego "La Cosa", el cuál es desarrollado para la materia Ingeniería del Software dictada el año 2023 en FAMAF.

## Tabla de Contenidos.

1. [Requisitos previos](#requisitos-previos)
2. [Comandos útiles](#comandos-útiles)
3. [Reglas de código](#reglas-de-código)
4. [Estructura de directorios](#estructura-de-directorios)
5. [Tecnologías a utilizar](#tecnologías-a-utilizar)

## Requisitos previos.

Para poder correr este proyecto se necesita tener instalado [NodeJS](https://nodejs.org/es) en su versión 16 o superior. También es necesario tener instalado [npm](https://www.npmjs.com/), aunque generalmente ya vendrá instalado junto con NodeJS.

## Comandos útiles.

### instalar paquetes del proyecto:

Para realizar la descarga inicial de los paquetes deberán hacer:

```bash
npm install
```

Este comando descargará todos los paquetes necesarios para poder correr el proyecto de manera local. Los paquetes serán guardados de manera automática en una carpeta llamada `node_modules`.

### Correr el proyecto:

Una vez instaladas las dependencias, vamos a poder probar el proyecto usando el siguiente comando:

```bash
npm run dev
```

Dicho comando devolverá una respuesta de la siguiente forma:

```bash
  VITE v4.4.9  ready in 838 ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

Y entonces, debemos copiar y pegar en el navegador el link proporcionado por `Local`, el cuál será en nuestro ejemplo `http://127.0.0.1:5173/`.

### Correr todos los tests:
Para poder correr todos los test debemos ejecutar el siguiente comando:

```bash
npm test
```

Dicho comando nos mostrará en la consola si los test se han ejecutado correctamente. Es importante destacar que los test se ejecutarán con hot reload, lo que significa que al cambiar el código de algún test, entonces los tests volverán a ejecutarse automáticamente.

## Reglas de código.

A continuación se dará unas reglas de código que recomendamos seguir para lograr que el proyecto creado sea uniforme.

- Se recomienda el uso de `Prettier` para formatear el código de manera automática.
- Se recomienda el uso del punto y coma para separar cada línea de código de JavaScript.
- Se recomienda la utilización de los `arrow function` en lugar de definirlos con la palabra `function`. Por ejemplo:

  ```javascript
  /* ✅ Este código es correcto. */
  const factorial = (num) => {
  	if (num === 0 || num === 1) return 1;
  	for (let i = num - 1; i >= 1; i--) {
  		num *= i;
  	}
  	return num;
  };

  factorial(5); // 120

  /* ⚠️ Este código no es recomendable, pero funciona. */
  function factorial(num) {
  	if (num === 0 || num === 1) return 1;
  	for (let i = num - 1; i >= 1; i--) {
  		num *= i;
  	}
  	return num;
  }

  factorial(5); // 120
  ```

- Se recomienda utilizar la `igualdad estricta` (===) en lugar de la `igualdad regular` (==).
- Se recomienda utilizar `let` y `const`. Principalmente `const` lo utilizaremos en arreglos y objetos para evitar desreferenciarlos por error.

## Estructura de directorios.

Para el proyecto hemos decidido tener la siguiente estructura de directorios:

```
🗁 NOMBRE_DEL_PROYECTO
    │
    ├ 🗀 node_modules
    │
    ├ 🗀 public
    │
    ├ 🗁 src
    │   │
    │   ├ 🗁 assets
    │   │   │
    │   │   ├ 🗀 img
    │   │   │
    │   │   ├ 🗀 fonts
    │   │   │
    │   │   ...
    │   │
    │   ├ 🗁 components
    │   │   │
    │   │   ├ 🗁 NOMBRE_DEL_COMPONENTE
    │   │   │   │
    │   │   │   ├ 🗋 NOMBRE_DEL_COMPONENTE.jsx
    │   │   │   │
    │   │   │   └ 🗋 NOMBRE_DEL_COMPONENTE.test.js
    │   │   ...
    │   │
    │   ├ 🗁 utils
    │   │   │
    │   │   ├ 🗀 functions
    │   │   │
    │   │   ├ 🗀 hooks
    │   │   │
    │   │   ...
    │   │
    │   ├ 🗁 views
    │   │   │
    │   │   ├ 🗋 NOMBRE_DE_LA_VISTA.jsx
    │   │   │
    │   │   ...
    │   │
    │   ├ 🗋 main.css
    │   │
    │   ├ 🗋 routes.jsx
    │   │
    │   └ 🗋 main.jsx
    │
    ├ 🗋 .eslintrc.cjs
    │
    ├ 🗋 .gitignore
    │
    ├ 🗋 index.html
    │
    ├ 🗋 package-lock.json
    │
    ├ 🗋 package.json
    │
    ├ 🗋 postcss.config.js
    │
    ├ 🗋 tailwind.config.js
    │
    └ 🗋 vite.config.js
```

Como se puede observar en este árbol de directorios, hemos generalizado la estructura de directorios que tendrá el proyecto, el cuál consitirá de:

- `assets`: Allí se guardarán las imágenes, fuentes y demás información que no será de utilidad para el sitio web.

- `components`: Por cada componente crearemos un directorio que tendrá el nombre del componente a implementar, y que contendrá el código del componente y sus correspondientes tests unitarios.

- `utils`: Allí se guardarán tanto funciones como custom hooks que nos serán de utilidad en el proyecto.

- `views`: Como utilizamos rutas, el código correspondiente a cada ruta se guardará en este directorio. 

- `routes.jsx`: Allí es donde definiremos las rutas y cuál será su vista correspondiente.

- `main.jsx`: Es el código inicial de React.

## Tecnologías a utilizar.

El proyecto en general estará desarrollado utilizando la librería llamada `React`. También hemos decidido crear el proyecto utilizando `vite`.

Por otro lado, hemos decidido utilizar las siguientes tecnologías para poder ayudarnos a realizar tareas específicas:

- [React Router DOM](https://reactrouter.com/en/main): Nos servirá para poder crear rutas en nuestro proyecto de una manera fácil y cómoda.

- [Tailwind CSS](https://tailwindcss.com/): Nos permitirá estilizar nuestros componentes utilizando estilos atómicos de CSS.

- [Vitest](https://vitest.dev/): Nos permitirá crear el código de los tests y ejecutarlos mediante hot reload.

- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/): Nos proveerá una buena API para poder testear los componentes de React.