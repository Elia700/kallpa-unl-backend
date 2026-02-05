# 📘 Manual de Instalación y Ejecución – KALLPA-UNL Backend

Este manual detalla paso a paso cómo configurar el entorno, la base de datos y ejecutar el proyecto junto con sus pruebas automatizadas.

**Rama objetivo:** `main`

---

## 🛠️ 1. Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
*   **Python 3.12+**: [Descargar Python](https://www.python.org/downloads/)
*   **PostgreSQL**: [Descargar PostgreSQL](https://www.postgresql.org/download/)
*   **Git**: [Descargar Git](https://git-scm.com/downloads)

---

## 🚀 2. Clonación y Configuración del Repositorio

### 2.1. Clonar el proyecto
Abre tu terminal (PowerShell, CMD, o Bash) y ejecuta:

```bash
git clone https://github.com/ThiagoAbrigo/kallpa-unl-backend.git
cd kallpa-unl-backend
```

### 2.2. Cambiar a la rama principal (Main)
Es **CRUCIAL** cambiar a la rama `main` para tener la versión correcta y estable del código:

```bash
git checkout main
```

---

## 🐍 3. Configuración del Entorno Virtual

Sigue las instrucciones según tu sistema operativo:

### 🖥️ Windows

1.  **Crear el entorno virtual:**
    ```powershell
    python -m venv venv
    ```
2.  **Activar el entorno:**
    ```powershell
    .\venv\Scripts\activate
    ```
    *(Verás `(venv)` al inicio de tu línea de comandos)*

### 🐧 Linux / 🍎 MacOS

1.  **Crear el entorno virtual:**
    ```bash
    python3 -m venv venv
    ```
2.  **Activar el entorno:**
    ```bash
    source venv/bin/activate
    ```

### 3.1. Instalar dependencias
Con el entorno activado, instala las librerías necesarias:

```bash
pip install -r requirements.txt
```

---

## 🗄️ 4. Configuración de la Base de Datos

### 4.1. Crear la Base de Datos
Debes crear una base de datos llamada `kallpa_bd`. Puedes usar pgAdmin o la terminal:

```bash
createdb -h localhost -U postgres kallpa_bd
```
*Te pedirá la contraseña de tu usuario postgres.*

### 4.2. Configurar Variables de Entorno (.env)
Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
cp .env.example .env
```

Luego edita el archivo `.env` con tu configuración:

```ini
FLASK_APP=Kallpa
FLASK_ENV=development

# Configuración de Base de Datos
USE_POSTGRES=true
PGUSER=postgres
PGPASSWORD=TU_PASSWORD_AQUI
PGHOST=localhost
PGDATABASE=kallpa_bd
PGPORT=5432

# Claves secretas
SECRET_KEY=kallpa123
JWT_SECRET_KEY=jwt_secret_kallpa
```

> [!IMPORTANT]
> Asegúrate de que `PGPASSWORD` coincida con la contraseña de tu usuario `postgres` local.

---

## ▶️ 5. Ejecución del Proyecto

Para iniciar el servidor de desarrollo:

```bash
python index.py
```
Si todo es correcto, verás: `Running on http://127.0.0.1:5000`

---

## ✅ 6. Ejecución de Pruebas

Las pruebas utilizan **mocks** y **NO requieren** que el servidor esté corriendo ni conexión a la base de datos.

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python3 -m unittest tests.pruebas_finales -v
```

Deberías ver una salida indicando `OK` si todas las pruebas pasan correctamente.

---

## 🚀 7. Pipeline de Continuous Delivery (GitHub Actions)

### 7.1. Descripción del Pipeline
Este proyecto incluye un pipeline completo de CD (Continuous Delivery) configurado con **GitHub Actions** que se ejecuta automáticamente al hacer `push` a la rama `main`.

### 7.2. Estructura del Pipeline

El pipeline está definido en [`.github/workflows/cd-backend.yml`](.github/workflows/cd-backend.yml) e incluye 3 jobs principales:

#### 📋 Job 1: build-test
- **Propósito**: Validar la calidad del código
- **Acciones**:
  - Checkout del repositorio
  - Configuración de Python 3.12
  - Instalación de dependencias (`requirements.txt`)
  - Ejecución de tests unitarios (`tests.pruebas_finales`)

#### 🚀 Job 2: deploy
- **Propósito**: Desplegar a Azure App Service
- **Dependencias**: Requiere que `build-test` sea exitoso
- **Acciones**:
  - Login a Azure usando credenciales del secret `AZURE_CREDENTIALS`
  - Deploy automático a Azure App Service

#### 🔍 Job 3: health-check
- **Propósito**: Verificar que el despliegue funcione correctamente
- **Dependencias**: Requiere que `deploy` sea exitoso
- **Acciones**:
  - Verificación del endpoint `/health`
  - Validación de respuesta HTTP 200

### 7.3. Variables de Entorno del Pipeline

```yaml
AZURE_WEBAPP_NAME: kallpa-backend-app
PYTHON_VERSION: '3.12'
```

### 7.4. Configuración Requerida en GitHub

Para que el pipeline funcione, necesitas configurar los siguientes **Secrets** en tu repositorio de GitHub:

#### Configurar Azure Credentials
1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Agregar nuevo secret: `AZURE_CREDENTIALS`

El formato del secret debe ser:
```json
{
  "clientId": "tu-client-id",
  "clientSecret": "tu-client-secret",
  "subscriptionId": "tu-subscription-id",
  "tenantId": "tu-tenant-id"
}
```

### 7.5. Endpoint de Health Check
El proyecto incluye un endpoint `/health` que responde con:
- **Status Code**: 200 OK
- **Response**:
```json
{
  "status": "OK",
  "message": "Kallpa Backend is running",
  "timestamp": "2026-02-05"
}
```

### 7.6. Activación del Pipeline

El pipeline se ejecuta automáticamente cuando:
1. Realizas `push` a la rama `main`
2. Haces `merge` de un Pull Request a `main`

### 7.7. Monitoreo del Pipeline

Para ver el estado del pipeline:
1. Ve a tu repositorio en GitHub
2. Pestaña **Actions**
3. Selecciona el workflow **"CD Backend Pipeline"**
4. Observa el progreso en tiempo real

### 7.8. Comandos para Desplegar

```bash
# Agregar cambios al repositorio
git add .

# Crear commit con mensaje descriptivo
git commit -m "Add CD pipeline GitHub Actions"

# Subir cambios a GitHub (activará el pipeline)
git push origin main
```

### 7.9. Arquitectura del Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   build-test    │───▶│     deploy      │───▶│   health-check  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Python 3.12   │    │ • Azure Login   │    │ • curl /health  │
│ • Install deps  │    │ • App Service   │    │ • Status 200    │
│ • Run tests     │    │ • Deploy app    │    │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 7.10. Beneficios del Pipeline como Código

- ✅ **Automatización completa**: Deploy sin intervención manual
- ✅ **Calidad asegurada**: Tests obligatorios antes del deploy
- ✅ **Versionado**: El pipeline está en código (YAML)
- ✅ **Trazabilidad**: Historial completo en GitHub Actions
- ✅ **Seguridad**: Uso de secrets para credenciales
- ✅ **Verificación**: Health check post-deploy automático

---