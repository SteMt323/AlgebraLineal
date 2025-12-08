# 🚀 **Guía de instalación y ejecución del Backend**

Esta guía explica cómo clonar, configurar e iniciar el backend de la calculadora matemática desarrollado con **Django + Django REST Framework**.

---

# **1. Requisitos previos**

Antes de comenzar, asegúrate de tener instalado:

| Herramienta                            | Requerido      |
| -------------------------------------- | -------------- |
| Python                                 | 3.10 – 3.12    |
| pip                                    | Última versión |
| Git                                    | Sí             |
| Virtualenv (opcional pero recomendado) | Sí             |

---

# **2. Clonar el repositorio**

```bash
git clone https://github.com/SteMt323/AlgebraLineal.git
cd AlgebraLineal
```

---

# **3. Crear y activar entorno virtual**

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / MacOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# **4. Instalar dependencias**

```bash
pip install -r requirements.txt
```

Esto instalará:

* Django
* Django REST Framework
* django-cors-headers
* drf-spectacular
* numpy
* sympy
* antlr4-runtime (para parseo de LaTeX)
* etc.

---

# **5. Configurar variables de entorno**

El proyecto usa un archivo `.env` para almacenar la **SECRET_KEY** y otras configuraciones privadas.

Dentro del repo encontrarás un archivo:

```
.env.example
```

Cópialo y renómbralo:

```bash
cp .env.example .env
```

Ahora edítalo:

```env
DJANGO_SECRET_KEY=pon_aqui_una_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Importante:

* **Nunca subas `.env` al repositorio.**
* La SECRET_KEY puede generarse con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Pega ese valor en `DJANGO_SECRET_KEY`.

---

# **6. Migraciones iniciales**

Crea la base de datos (SQLite por defecto):

```bash
python manage.py migrate
```

---

# **7. Ejecutar el servidor**

```bash
python manage.py runserver
```

Ahora el backend está disponible en:

```
http://127.0.0.1:8000/api/v1/
```

---

# **8. Probar las APIs**

Puedes usar:

* Thunder Client
* Postman
* Insomnia
* Curl
* Frontend React (cuando esté conectado)

Ejemplo:

```bash
POST http://127.0.0.1:8000/api/v1/numeric/abs-rel-error
```

---

# **9. Estructura del proyecto**

```
/calculadora_backend
    /algebra
        /algorithms
        /api
        /serializers
        /utils
        urls.py
    settings.py
.env
requirements.txt
manage.py
```

---

# **10. Problemas comunes**

### “SECRET_KEY missing”

Tu archivo `.env` no existe o falta la variable.

### “Invalid host header”

Agrega tu host en `.env` → `ALLOWED_HOSTS=localhost,127.0.0.1`

### Error con numpy o sympy

Reinstalar:

```bash
pip install --force-reinstall numpy sympy
```
