USAR MathQuill

<h1 align="center">
  <img src="https://img.shields.io/badge/ÁLGEBRA_LINEAL-MUNGUIA_CORE-800080?style=for-the-badge&logo=github&logoColor=white">
</h1>
---

# Calculadora MUNGUIA_CORE

Este proyecto corresponde a una **API backend construida con Django REST Framework**, diseñada para servir como motor matemático de una aplicación educativa que procesa cálculos avanzados orientados a:

* Álgebra lineal
* Métodos numéricos
* Manipulación de matrices y vectores
* Sistemas de ecuaciones
* Cálculo de errores
* Paso a paso para aprendizaje

Dicho Backend se integra con un frontend desarrollado en **React** con **TypeScript**.

---

## 🚀 Funcionalidades principales

### 🔢 Álgebra Lineal

* Suma, resta, multiplicación y operaciones elementales de matrices
* Cálculo de la matriz inversa con pasos
* Determinantes:

  * Regla de Sarrus
  * Expansión por Cofactores
  * Método de Cramer
* Vectores: combinaciones lineales, norma, operaciones básicas
* Sistemas de ecuaciones:

  * Eliminación Gaussiana
  * Gauss-Jordan
  * Detección de soluciones únicas, múltiples o inconsistentes
  * Reporte detallado de cada operación

### 🧮 Métodos Numéricos

* Error absoluto y error relativo
* Simulación de error acumulado por:

  * **Truncamiento**
  * **Redondeo**
* Resultados completamente desglosados para uso didáctico
* Representación detallada de fórmulas, operaciones y resultados

---

## 📁 Estructura del proyecto

```
calculadora_backend/
│── algebra/
│   ├── algorithms/        # Lógica matemática detallada
│   ├── api/               # Views + Serializers
│   ├── utils/             # Steps, formateo, validaciones
│   └── Constants/
│
│── calculadora_backend/
│   ├── settings.py
│   ├── urls.py
│   └── ...`
│── calculadora_frontend/
│   ├── src/               # Componentes
│   ├── package.json
│   └── ...
│
│── .env.example
│── manage.py
│── requirements.txt
```

---

## 🔧 Instalación y configuración-Backend

### I. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### II. Instalar dependencias

```bash
pip install -r requirements.txt
```

### III. Configurar variables de entorno

Copia `.env.example` a `.env`:

```
cp .env.example .env
```

En `.env`, agrega una SECRET_KEY válida:

```
SECRET_KEY=coloca-aqui-una-key-real
DEBUG=True
ALLOWED_HOSTS=*
```

### IV. Migraciones

```bash
python manage.py migrate
```

### V. Ejecutar el servidor

```bash
python manage.py runserver
```

## 🔧 Instalación y configuración-Backend

### I. Muevete al Directorio Correspondiente
```bash
cd calculadora_frontend
```

### II. Instala las dependencias del package.json
```bash
npm install
```

### III. Corre el servidor
```bash
npm run build
# O
npm run dev
```


### IV. Checkeos con Typescript
```bash
npx tcs --noEmit # Checkea todo el proyecto sin generar algun js file
```
---

## 🧪 Pruebas

Puedes utilizar:

* Thunder Client
* Postman
* cURL
* Frontend en React

Todos los endpoints reciben y devuelven JSON estructurado para fácil consumo.

---

## 🎯 Objetivo del proyecto

Este sistema está diseñado para servir como **herramienta educativa**, proporcionando:

* Transparencia del proceso matemático
* Pasos detallados tipo "libro de texto"
* Precision fraccional
* Formatos compatibles con renderizadores de matemáticas (KaTeX / MathJax)

---

## 🤝 Contribuciones

Pull requests y mejoras son bienvenidas.

Si querés soporte para nuevas funciones, abrí un issue o pedilo directamente.

---

## 📄 Licencia MIT

Proyecto de uso académico.

---

## Colaboradores
<p align="left">
  <img src="https://avatars.githubusercontent.com/u/166463207" alt="Foto de SteMt323" width="50" height="50" style="border-radius:50%;"/>
  <a href="https://github.com/SteMt323" style="margin-left:10px; text-decoration:none; font-weight:bold; color:#0366d6; font-size:16px;">
    <span style="background-color:#f0f0f0; padding:4px 8px; border-radius:6px;">SteMt323</span>
  </a>
</p>

<p align="left">
  <img src="https://avatars.githubusercontent.com/u/169182686" alt="Foto de SteMt323" width="50" height="50" style="border-radius:50%;"/>
  <a href="https://github.com/THEGABOALE" style="margin-left:10px; text-decoration:none; font-weight:bold; color:#0366d6; font-size:16px;">
    <span style="background-color:#f0f0f0; padding:4px 8px; border-radius:6px;">THEGABOALE</span>
  </a>
</p>


