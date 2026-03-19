# Laboratorio 1: Detección de Equipo de Seguridad con AWS Rekognition (AWS CDK)

## 📋 Resumen del Despliegue

Este laboratorio despliega una aplicación completa de **visión por computadora** usando **AWS CDK** para detectar equipo de protección personal (EPP) en imágenes de obras:

1. **Infrastructure Stack** - S3 + DynamoDB + IAM (2-3 min)
2. **Lambda Stack** - Función de análisis con Rekognition (2-3 min)
3. **API Gateway Stack** - Endpoint REST con CORS (2-3 min)
4. **Frontend Stack** - S3 Static Hosting (1-2 min)

**Tiempo total:** ~8-12 minutos

**Ventaja:** Despliegue automatizado con nombres únicos para evitar colisiones entre usuarios.

---

## 🏗️ Arquitectura Desplegada

### Componentes Principales

- **Frontend**: Aplicación web interactiva (HTML/CSS/JavaScript)
- **API Gateway**: Endpoint REST para análisis de imágenes
- **Lambda Function**: Procesamiento con AWS Rekognition
- **Rekognition**: Detección de objetos y escenas en imágenes
- **S3**: Almacenamiento de imágenes y frontend estático
- **DynamoDB**: Resultados de análisis y metadata

### Flujo de Datos

```
Usuario → Frontend → API Gateway → Lambda → (Rekognition + S3 + DynamoDB) → Frontend
```

---

## 🚀 Despliegue Rápido (Comando Único)

Para desplegar toda la aplicación de una vez:

```bash
# Reemplaza "tu-nombre" con tu nombre o apellido
cdk deploy --require-approval never
```

**Tiempo total:** ~8-12 minutos

---

## � Ejecución Local con Python

Si prefieres ejecutar el proyecto localmente en tu máquina:

### Requisitos Previos
- Python 3.9+
- Node.js 18+
- AWS CLI configurado con credenciales
- AWS CDK CLI instalado

### Pasos de Instalación y Despliegue

#### 1. Crear entorno virtual

```bash
# Navegar a la carpeta del proyecto
cd clase7_lab1

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # En macOS/Linux
# o
venv\Scripts\activate  # En Windows
```

#### 2. Instalar dependencias

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Verificar que aws-cdk-lib está instalado
pip list | grep aws-cdk-lib
```

#### 3. Configurar el proyecto

Edita `cdk.json` con tu nombre único:

```json
{
  "app": "python cdk_app.py",
  "require_approval": "never",
  "context": {
    "lab_name": "clase7-lab1-tu-nombre",
    "region": "eu-west-1"
  }
}
```

#### 4. Desplegar la infraestructura

```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Desplegar con CDK
cdk deploy --require-approval never
```

#### 5. Actualizar la URL del frontend

Después del despliegue, ejecuta el script para actualizar la URL del API:

```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Ejecutar script de actualización
python3 update_frontend_url.py
```

Este script:
- Obtiene la URL del API Gateway desde CloudFormation
- Actualiza el archivo `frontend/app.js` con la URL correcta
- Sube el archivo actualizado al bucket S3

#### 6. Acceder a la aplicación

La URL del frontend se mostrará en los outputs:

```
FrontendURL = http://clase7-lab1-tu-nombre-{ACCOUNT_ID}-eu-west-1.s3-website-eu-west-1.amazonaws.com
```

---

## �📚 Despliegue Paso a Paso

### Paso 1 – Preparar el archivo ZIP localmente

En este paso, prepararemos el archivo ZIP con el código del proyecto para subirlo a CloudShell.

#### 1.1 – Comprimir la carpeta del proyecto

1. Abre una terminal en tu máquina local.
2. Navega a la carpeta padre de Laboratorio 1:

```bash
cd /Users/personal/Projects/Pontia/Clase\ 7
```

3. Crea un archivo ZIP con la carpeta Laboratorio 1:

```bash
zip -r seguridad-lab.zip Laboratorio\ 1/
```

> **👉 Resultado:** Se crea el archivo `seguridad-lab.zip` en la carpeta Clase 7.

---

### Paso 2 – Acceder a AWS CloudShell

1. Abre la consola de AWS en tu navegador.
2. En la barra superior, busca el icono de **CloudShell** (terminal) o haz clic en el icono de terminal.
3. Espera a que CloudShell se cargue (puede tardar unos segundos).

> **👉 Resultado:** Tienes una terminal en la nube lista para usar.

---

### Paso 3 – Subir el archivo ZIP a CloudShell

#### 3.1 – Usar el gestor de archivos de CloudShell

1. En CloudShell, haz clic en el icono de **Actions** (arriba a la derecha).
2. Selecciona **Upload file**.
3. Selecciona el archivo `seguridad-lab.zip` de tu máquina local.
4. Espera a que se complete la carga.

> **✅ Resultado esperado:** El archivo ZIP está en CloudShell.

#### 3.2 – Verificar que se subió correctamente

```bash
ls -lh seguridad-lab.zip
```

> **👉 Resultado:** Deberías ver el archivo listado con su tamaño.

---

### Paso 4 – Descomprimir y preparar el proyecto

```bash
# Descomprimir el archivo
unzip seguridad-lab.zip

# Navegar a la carpeta del proyecto
cd Laboratorio\ 1

# Verificar que los archivos están presentes
ls -la
```

> **👉 Resultado:** Ves los archivos `cdk_app.py`, `requirements.txt`, carpetas `stacks/`, `lambdas/`, `frontend/`.

---

### Paso 5 – Instalar dependencias en CloudShell

CloudShell ya tiene Python y Node.js instalados. Solo necesitas instalar las dependencias del proyecto:

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar AWS CDK CLI (si no está instalado)
npm install -g aws-cdk

# Verificar que CDK está instalado
cdk --version
```

> **✅ Resultado esperado:** Todas las dependencias están instaladas.

---

### Paso 6 – Configurar tu laboratorio único

Edita el archivo `cdk.json` para personalizar tu laboratorio:

```bash
nano cdk.json
```

Cambia el `lab_name` a algo único:

```json
{
  "app": "python cdk_app.py",
  "require_approval": "never",
  "context": {
    "lab_name": "seguridad-tu-nombre",
    "region": "eu-west-1"
  }
}
```

> **👉 Importante:** Usa un nombre único para evitar conflictos con otros usuarios.

---

### Paso 7 – Bootstrap del entorno CDK

El bootstrap prepara tu cuenta AWS para usar CDK:

```bash
# Obtener tu AWS Account ID
aws sts get-caller-identity --query Account --output text

# Bootstrap (reemplaza ACCOUNT_ID con tu ID)
cdk bootstrap aws://ACCOUNT_ID/eu-west-1
```

> **👉 Explicación:** Esto crea un bucket S3 y otros recursos necesarios para que CDK funcione en tu cuenta.

> **✅ Resultado esperado:** Ves un mensaje indicando que el bootstrap se completó.

---

### Paso 8 – Desplegar la aplicación completa

```bash
# Desplegar toda la infraestructura
cdk deploy --require-approval never
```

**Qué se crea:**
- S3 Bucket para imágenes: `seguridad-tu-nombre-{ACCOUNT_ID}-{region}`
- DynamoDB Table: `seguridad-tu-nombre-analisis`
- Lambda Function: `seguridad-tu-nombre-analyzer`
- API Gateway: `seguridad-tu-nombre-api`
- Frontend hosting en S3

**Tiempo:** ~8-12 minutos

> **✅ Resultado:** Toda la infraestructura desplegada correctamente.

---

### Paso 9 – Acceder a la aplicación

1. Abre tu navegador web.
2. Ve a la **FrontendUrl** que obtuviste en el despliegue:
   ```
   http://seguridad-tu-nombre-{ACCOUNT_ID}-{region}.s3-website-{region}.amazonaws.com
   ```
3. Deberías ver la interfaz de la aplicación con:
   - Panel de subida de imágenes
   - Área de resultados de análisis
   - Historial de análisis recientes

> **✅ Resultado esperado:** La aplicación carga correctamente.

---

### Paso 10 – Probar la aplicación

#### 10.1 – Subir una imagen

1. En el panel **📤 Subir Imagen**:
   - Arrastra una imagen o haz clic para seleccionar
   - Haz clic en **Analizar Imagen**
2. Abre la consola del navegador (F12) para ver los logs.

> **✅ Resultado esperado:**
> - La imagen se sube a S3
> - Rekognition analiza la imagen
> - Se muestra el análisis de cumplimiento de EPP

#### 10.2 – Ver resultados del análisis

La aplicación mostrará:
- **Porcentaje de cumplimiento**: Basado en EPP obligatorios (casco, gafas, guantes)
- **Items detectados**: Lista de equipo de seguridad encontrado
- **Estado**: Cumple/No cumple normativa
- **Historial**: Análisis anteriores con timestamp

> **✅ Resultado esperado:** Análisis completo con detección de equipo de seguridad.

---

## 🧭 Navegación por Servicios AWS

### 📊 ¿Qué Hemos Desplegado?

#### 1. **Frontend - Interfaz de Usuario**
- **Propósito**: Aplicación web para análisis de imágenes
- **Tecnología**: HTML5, CSS3 (Tailwind), JavaScript vanilla
- **Funcionalidades**:
  - Subida de imágenes con drag & drop
  - Análisis en tiempo real con AWS Rekognition
  - Visualización de resultados de cumplimiento
  - Historial de análisis recientes
- **Ubicación**: S3 Static Website Hosting

#### 2. **API Gateway - Puerta de Entrada**
- **Propósito**: Exponer endpoint REST para análisis
- **Endpoint**: `POST /analyze` - Procesa imágenes con Rekognition
- **Características**: CORS habilitado, integración con Lambda

#### 3. **Lambda Function - Lógica de Negocio**
- **Análisis Lambda**:
  - Procesa imágenes en base64
  - Invoca AWS Rekognition para detección de objetos
  - Evalúa cumplimiento de EPP obligatorios
  - Guarda resultados en DynamoDB
  - Sube imagen original a S3

#### 4. **Rekognition - Visión por Computadora**
- **Propósito**: Detección automática de objetos en imágenes
- **Configuración**:
  - `detect-labels` con MaxLabels=20, MinConfidence=70
  - Detección de equipo de seguridad (casco, gafas, guantes, chaleco, calzado)
  - Análisis de confianza y bounding boxes

#### 5. **S3 - Almacenamiento**
- **Bucket de Imágenes**: Almacena imágenes originales analizadas
- **Bucket de Frontend**: Hosting de archivos web estáticos
- **Características**: Website hosting, CORS configurado

#### 6. **DynamoDB - Base de Datos**
- **Tabla de Análisis**: Resultados, metadata, timestamps
- **Ventajas**: Escalable, serverless, baja latencia

### 🔍 Cómo Navegar y Verificar los Servicios

#### AWS Management Console

1. **CloudFormation**
   - Busca el stack: `seguridad-tu-nombre-stack`
   - Revisa los outputs y recursos creados

2. **S3**
   - Bucket: `seguridad-tu-nombre-{ACCOUNT_ID}-{region}`
   - Revisa imágenes subidas en la raíz
   - Verifica archivos frontend: `index.html`, `app.js`

3. **DynamoDB**
   - Tabla: `seguridad-tu-nombre-analisis` - resultados de análisis
   - Explora items para ver estructura de datos

4. **Lambda**
   - Función: `seguridad-tu-nombre-analyzer` - logs de procesamiento
   - Configuración, variables de entorno, métricas

5. **API Gateway**
   - API: `seguridad-tu-nombre-api` - endpoint y configuración
   - Testea el endpoint directamente desde la consola

6. **Rekognition**
   - Verifica límites y uso en la consola
   - Revisa etiquetas detectadas en imágenes de prueba

7. **CloudWatch**
   - Logs de Lambda para debugging
   - Métricas de rendimiento y errores

#### Comandos AWS CLI Útiles

```bash
# Listar imágenes en el bucket
aws s3 ls s3://seguridad-tu-nombre-ACCOUNT_ID-eu-west-1/

# Ver análisis en DynamoDB
aws dynamodb scan --table-name seguridad-tu-nombre-analisis --region eu-west-1

# Revisar logs de Lambda
aws logs tail /aws/lambda/seguridad-tu-nombre-analyzer --follow --region eu-west-1

# Probar API Gateway directamente
curl -X POST https://api-id.execute-api.eu-west-1.amazonaws.com/prod/analyze \
  -H "Content-Type: application/json" \
  -d '{"image":"base64-data","filename":"test.jpg"}'
```

### 🎯 Flujo Completo de Análisis

1. **Usuario** sube imagen al frontend
2. **Frontend** convierte a base64 y envía a API Gateway
3. **API Gateway** invoca Lambda Function
4. **Lambda** decodifica imagen y la sube a S3
5. **Lambda** invoca Rekognition para detectar objetos
6. **Rekognition** retorna etiquetas con confianza
7. **Lambda** evalúa cumplimiento de EPP obligatorios
8. **Lambda** guarda resultados en DynamoDB
9. **Frontend** muestra análisis con porcentaje de cumplimiento

---

## 🔧 Troubleshooting

### Error: "SSM parameter /cdk-bootstrap/hnb659fds/version not found"

**Solución:** Ejecutar bootstrap primero:
```bash
cdk bootstrap aws://ACCOUNT_ID/eu-west-1
```

### Error: "Bucket already exists"

**Solución:** Cambia el `lab_name` en `cdk.json` a algo único.

### Error CORS en el frontend

**Solución:** El stack ya incluye configuración CORS completa en API Gateway.

### Rekognition no detecta objetos

**Solución:** Verifica que la imagen sea clara y tenga buena iluminación. Rekognition funciona mejor con imágenes de buena calidad.

### La aplicación no carga

**Solución:** Recarga la página con Ctrl+Shift+R para limpiar la caché del navegador.

### Error de Lambda con timeout

**Solución:** El timeout está configurado a 30 segundos. Para imágenes muy grandes, considera optimizar el tamaño.

---

## 🧹 Limpieza (Opcional)

Para eliminar todos los recursos creados:

```bash
cdk destroy
```

> **👉 Nota:** CDK eliminará automáticamente todos los recursos (Lambda, DynamoDB, API Gateway, S3, IAM roles, etc.).

---

## 🎓 Resultado Esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ **Desplegado** una aplicación de visión por computadora con AWS CDK
- ✅ **Configurado** AWS Rekognition para detección de equipo de seguridad
- ✅ **Integrado** Lambda con S3, DynamoDB y Rekognition
- ✅ **Creado** una interfaz web moderna con drag & drop
- ✅ **Procesado** imágenes con análisis de cumplimiento de EPP
- ✅ **Implementado** evaluación de normativa de seguridad
- ✅ **Verificado** todos los servicios AWS desplegados
- ✅ **Comprendido** la arquitectura serverless y sus interacciones
- ✅ **Aprendido** a usar AWS CDK para infraestructura como código
- ✅ **Entendido** la integración de servicios de IA de AWS

### 🚀 **Aplicación de Seguridad 100% Funcional**

**Frontend**: http://seguridad-tu-nombre-{ACCOUNT_ID}-{region}.s3-website-{region}.amazonaws.com  
**API**: https://{api-id}.execute-api.{region}.amazonaws.com/prod/analyze

La aplicación está lista para producción con todas las funcionalidades de detección de EPP implementadas.

---

## 📊 Análisis de Cumplimiento Implementado

### EPP Obligatorios (100% requerido)
- **Casco/Hardhat**: Protección craneal
- **Gafas de seguridad**: Protección ocular  
- **Guantes**: Protección de manos

### EPP Recomendados (puntos extra)
- **Chaleco reflectante**: Visibilidad
- **Calzado de seguridad**: Protección de pies

### Niveles de Riesgo
- **✅ CUMPLE NORMATIVA**: 100% EPP obligatorios
- **⚠️ CUMPLIMIENTO PARCIAL**: 67-99% EPP obligatorios
- **🚨 INCUMPLIMIENTO MODERADO**: 33-66% EPP obligatorios
- **🚨🚨 ALTO RIESGO**: 0-32% EPP obligatorios

La aplicación proporciona análisis instantáneo con visualización intuitiva del estado de cumplimiento.
