# Laboratorio 1: SafetyVision Pro - Computer Vision con Rekognition (AWS CDK)

## 📋 Resumen del Despliegue

Este laboratorio despliega una aplicación completa de Computer Vision usando **AWS CDK con despliegue stack a stack**:

1. **Storage Stack** - S3 + DynamoDB + KMS (2-3 min)
2. **Rekognition Stack** - PPE Detection Project + SNS (5-8 min)
3. **Lambda Stack** - Upload + Analysis + Dashboard + Report Functions (3-4 min)
4. **API Stack** - API Gateway REST con 7 endpoints (2-3 min)
5. **Frontend Stack** - S3 Static Hosting (1-2 min)

**Tiempo total:** ~15-25 minutos

**Ventaja:** Puedes monitorear cada paso y resolver problemas de forma aislada.

---

## 🏗️ Arquitectura Desplegada

### Componentes Principales

- **Frontend**: Aplicación web interactiva (HTML/CSS/JavaScript)
- **API Gateway**: 7 endpoints REST para análisis de seguridad
- **Lambda Functions**: Procesamiento de imágenes, análisis PPE, dashboard, reportes
- **Rekognition**: Detección de equipo de protección personal (PPE)
- **S3**: Almacenamiento de imágenes, reportes y frontend estático
- **DynamoDB**: Metadata de análisis y estadísticas
- **SNS**: Notificaciones de alertas de seguridad
- **KMS**: Encriptación de todos los datos

### Flujo de Datos

```
Usuario → Frontend → API Gateway → Lambda → (Rekognition + S3 + DynamoDB) → SNS → Dashboard
```

---

## 🚀 Despliegue Rápido (Comando Único)

Para desplegar toda la aplicación de una vez:

```bash
# Reemplaza "alumno" con tu nombre o apellido
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno" --require-approval never
```

**Tiempo total:** ~15-20 minutos

---

## ⚡ Paso Opcional – Despliegue Completo en un Solo Comando

Si prefieres desplegar toda la aplicación de una vez en lugar de stack por stack, puedes usar este método alternativo.

### Opción A – Despliegue Completo (Recomendado para producción)

```bash
# Reemplaza "alumno" con tu nombre o apellido
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno" --require-approval never
```

**Qué se crea (todo en un solo paso):**
- ✅ Storage Stack: S3 buckets, DynamoDB tables, KMS encryption
- ✅ Rekognition Stack: PPE Detection project, SNS notifications
- ✅ Lambda Stack: 4 funciones para upload, análisis, dashboard y reportes
- ✅ API Stack: API Gateway con 7 endpoints REST
- ✅ Frontend Stack: Website estático con configuración automática

**Ventajas:**
- ⚡ **Más rápido**: Un solo comando en lugar de 5 pasos separados
- 🔄 **Automático**: Gestiona todas las dependencias automáticamente
- 📊 **Monitoreo centralizado**: Ves el progreso de todos los stacks juntos
- 🛠️ **Ideal para producción**: Despliegue consistente y repetible

**Tiempo:** ~15-20 minutos

**Cuándo usar esta opción:**
- ✅ Cuando ya estás familiarizado con la arquitectura
- ✅ Para despliegues de producción o staging
- ✅ Cuando quieres actualizar toda la aplicación
- ✅ Para entornos de desarrollo rápido

### Opción B – Despliegue Completo con Verificación Paso a Paso

Si quieres la velocidad del despliegue completo pero mantener el control paso a paso:

```bash
# 1. Preparar el entorno (igual que en la guía paso a paso)
cdk bootstrap aws://ACCOUNT_ID/eu-west-1

# 2. Desplegar todo en un solo comando
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno" --require-approval never

# 3. Verificar que todo esté funcionando
cdk list
```

### Opción C – Despliegue por Fases (Híbrido)

Combina lo mejor de ambos mundos:

```bash
# Fase 1: Backend completo (Storage + Rekognition + Lambda + API)
cdk deploy safety-vision-alumno-storage safety-vision-alumno-rekognition safety-vision-alumno-lambdas safety-vision-alumno-api --app "python3 cdk_app.py --lab-name safety-vision-alumno" --require-approval never

# Fase 2: Frontend (después de verificar que el backend funciona)
cdk deploy safety-vision-alumno-frontend --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack frontend --upload-frontend" --require-approval never
```

**Ventajas del enfoque híbrido:**
- 🎯 **Control**: Puedes verificar el backend antes de desplegar el frontend
- ⚡ **Eficiencia**: Despliegue múltiple en lugar de uno por uno
- 🔍 **Debugging**: Fácil identificar problemas por fases

---

## 📚 Despliegue Paso a Paso (Método Educativo)

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
zip -r safety-vision-lab.zip Laboratorio\ 1/
```

> **👉 Resultado:** Se crea el archivo `safety-vision-lab.zip` en la carpeta Clase 7.

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
3. Selecciona el archivo `safety-vision-lab.zip` de tu máquina local.
4. Espera a que se complete la carga.

> **✅ Resultado esperado:** El archivo ZIP está en CloudShell.

#### 3.2 – Verificar que se subió correctamente

```bash
ls -lh safety-vision-lab.zip
```

> **👉 Resultado:** Deberías ver el archivo listado con su tamaño.

---

### Paso 4 – Descomprimir y preparar el proyecto

```bash
# Descomprimir el archivo
unzip safety-vision-lab.zip

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

### Paso 6 – Bootstrap del entorno CDK

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

### Paso 7 – Desplegar Stack a Stack

Desplegaremos la infraestructura paso a paso para monitorear el progreso.

#### 7.1 – Desplegar Storage Stack

```bash
# Reemplaza "alumno" con tu nombre o apellido
cdk deploy --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack storage" --require-approval never
```

**Qué se crea:**
- S3 Bucket para imágenes: `safety-vision-alumno-images`
- S3 Bucket para reportes: `safety-vision-alumno-reports`
- DynamoDB Table: `safety-vision-alumno-analysis` (resultados de análisis)
- DynamoDB Table: `safety-vision-alumno-stats` (estadísticas)
- KMS Key para encriptación
- IAM Roles para Lambda y Rekognition

**Tiempo:** ~2-3 minutos

> **✅ Resultado:** Storage desplegado correctamente.

#### 7.2 – Desplegar Rekognition Stack

```bash
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack rekognition" --require-approval never
```

**Qué se crea:**
- Rekognition Project: `safety-vision-alumno-ppe-detection`
- Rekognition Collection: `safety-vision-alumno-ppe-collection`
- SNS Topic: `safety-vision-alumno-safety-alerts` (notificaciones)

**Tiempo:** ~5-8 minutos (Rekognition tarda más en crearse)

> **✅ Resultado:** Rekognition Project creado y listo para detectar PPE.

#### 7.3 – Desplegar Lambda Stack

```bash
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack lambdas" --require-approval never
```

**Qué se crea:**
- Lambda Function: `safety-vision-alumno-upload` - Procesa uploads de imágenes
- Lambda Function: `safety-vision-alumno-analyze` - Análisis PPE con Rekognition
- Lambda Function: `safety-vision-alumno-dashboard` - Datos para dashboard
- Lambda Function: `safety-vision-alumno-report-generator` - Generación de reportes
- IAM Role con permisos para S3, DynamoDB, Rekognition y SNS

**Tiempo:** ~3-4 minutos

> **✅ Resultado:** Lambda Functions desplegadas y configuradas.

#### 7.4 – Desplegar API Stack

```bash
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack api" --require-approval never
```

**Qué se crea:**
- API Gateway: `safety-vision-alumno-api`
- Endpoints:
  - `POST /upload` - Subir imagen
  - `POST /analyze` - Analizar PPE
  - `GET /dashboard` - Datos del dashboard
  - `GET /stats` - Estadísticas
  - `GET /reports` - Reportes
  - `GET /documents` - Listar documentos
  - `GET /health` - Health check
- CORS habilitado

**Tiempo:** ~2-3 minutos

> **✅ Resultado:** API Gateway completamente funcional.

---

### Paso 8 – Desplegar Frontend Stack

Ahora que el backend está completamente desplegado, subiremos el frontend al bucket S3.

```bash
cdk deploy --all --app "python3 cdk_app.py --lab-name safety-vision-alumno --stack frontend --upload-frontend" --require-approval never
```

Este comando:
- Sube el frontend (`index.html`, `styles.css`, `app.js`) al bucket S3
- Inyecta automáticamente la URL del API Gateway en el frontend
- Configura el website hosting en S3

**Qué se crea:**
- S3 Bucket: `safety-vision-alumno-frontend-{ACCOUNT_ID}`
- Website configuration en S3
- Archivos frontend subidos
- config.json con la URL del API Gateway

**Tiempo:** ~1-2 minutos

> **✅ Resultado:** Frontend está subido al bucket S3 y listo para usar.

---

### Paso 9 – Acceder a la aplicación

1. Abre tu navegador web.
2. Ve a la **FrontendUrl** que obtuviste en el despliegue:
   ```
   http://safety-vision-alumno-frontend-ACCOUNT_ID.s3-website-eu-west-1.amazonaws.com
   ```
3. Deberías ver la interfaz de SafetyVision Pro con:
   - Panel de upload de imágenes
   - Dashboard de análisis PPE
   - Estadísticas de seguridad
   - Reportes generados

> **✅ Resultado esperado:** La aplicación carga correctamente.

---

### Paso 10 – Probar la aplicación

#### 10.1 – Subir una imagen

1. En el panel **📤 Subir Imágenes**:
   - Arrastra una imagen o haz clic para seleccionar
   - Haz clic en **Subir Imagen**
2. Abre la consola del navegador (F12) para ver los logs.

> **✅ Resultado esperado:**
> - La imagen se sube a S3
> - Se registra en DynamoDB
> - Lambda procesa y guarda metadata

#### 10.2 – Analizar PPE

1. En el panel **👷 Análisis PPE**:
   - Selecciona una imagen subida
   - Haz clic en **Analizar PPE**
2. La aplicación analizará la imagen con Rekognition

> **✅ Resultado esperado:**
> - Rekognition detecta equipo de protección personal
> - Se muestra resultados con confianza
> - Se guardan análisis en DynamoDB

#### 10.3 – Ver Dashboard

1. Navega al panel **📊 Dashboard**
2. Revisa estadísticas y análisis recientes

> **✅ Resultado esperado:**
> - Gráficos de detección de PPE
> - Estadísticas de seguridad
> - Historial de análisis

---

## 🧭 Navegación por Servicios AWS

### 📊 ¿Qué Hemos Desplegado?

#### 1. **Frontend - Interfaz de Usuario**
- **Propósito**: Aplicación web para análisis de seguridad
- **Tecnología**: HTML5, CSS3, JavaScript vanilla
- **Funcionalidades**:
  - Upload de imágenes con drag & drop
  - Análisis PPE con Rekognition
  - Dashboard interactivo con estadísticas
  - Generación de reportes PDF
  - Diseño responsive y moderno
- **Ubicación**: S3 Static Website Hosting

#### 2. **API Gateway - Puerta de Entrada**
- **Propósito**: Exponer 7 endpoints REST para la aplicación
- **Endpoints**:
  - `POST /upload` - Procesa uploads de imágenes
  - `POST /analyze` - Análisis PPE con Rekognition
  - `GET /dashboard` - Datos para dashboard
  - `GET /stats` - Estadísticas de seguridad
  - `GET /reports` - Reportes generados
  - `GET /documents` - Listar imágenes
  - `GET /health` - Health check
- **Características**: CORS habilitado, integración con Lambda

#### 3. **Lambda Functions - Lógica de Negocio**
- **Upload Lambda**:
  - Procesa archivos de imágenes subidos
  - Guarda en S3 y registra metadata en DynamoDB
  - Valida formatos de imagen
- **Analysis Lambda**:
  - Analiza imágenes con Rekognition PPE
  - Detecta cascos, chalecos, botas de seguridad
  - Guarda resultados en DynamoDB
  - Envía alertas SNS si es necesario
- **Dashboard Lambda**:
  - Agrega datos para dashboard
  - Calcula estadísticas de seguridad
  - Formatea datos para visualización
- **Report Generator Lambda**:
  - Genera reportes PDF de análisis
  - Compila estadísticas temporales
  - Guarda reportes en S3

#### 4. **Rekognition - Computer Vision**
- **Propósito**: Detección de equipo de protección personal
- **Configuración**:
  - Custom PPE Detection Project
  - Collection para almacenar modelos
  - Detección de cascos, chalecos, botas
  - Confidence scores para cada detección

#### 5. **S3 - Almacenamiento**
- **Bucket de Imágenes**: Almacena imágenes originales para análisis
- **Bucket de Reportes**: Almacena reportes PDF generados
- **Bucket de Frontend**: Hosting de archivos web estáticos
- **Características**: Versioning, KMS encryption, lifecycle policies

#### 6. **DynamoDB - Base de Datos**
- **Tabla de Análisis**: Resultados de análisis PPE, timestamps
- **Tabla de Estadísticas**: Datos agregados para dashboard
- **Ventajas**: Escalable, serverless, baja latencia

#### 7. **SNS - Notificaciones**
- **Topic**: Alertas de seguridad en tiempo real
- **Uso**: Notificar cuando se detecta falta de PPE
- **Integración**: Lambda functions y dashboard

### 🔍 Cómo Navegar y Verificar los Servicios

#### AWS Management Console

1. **CloudFormation**
   - Busca los stacks: `safety-vision-alumno-storage`, `safety-vision-alumno-rekognition`, etc.
   - Revisa los outputs y recursos creados

2. **S3**
   - Bucket: `safety-vision-alumno-images` - imágenes subidas
   - Bucket: `safety-vision-alumno-reports` - reportes PDF
   - Bucket: `safety-vision-alumno-frontend-{ACCOUNT_ID}` - frontend

3. **DynamoDB**
   - Tabla: `safety-vision-alumno-analysis` - resultados de análisis
   - Tabla: `safety-vision-alumno-stats` - estadísticas

4. **Lambda**
   - Función: `safety-vision-alumno-upload` - logs de uploads
   - Función: `safety-vision-alumno-analyze` - logs de análisis PPE
   - Función: `safety-vision-alumno-dashboard` - logs de dashboard
   - Función: `safety-vision-alumno-report-generator` - logs de reportes

5. **API Gateway**
   - API: `safety-vision-alumno-api` - 7 endpoints
   - Testea los endpoints directamente desde la consola

6. **Rekognition**
   - Project: `safety-vision-alumno-ppe-detection` - estado y métricas
   - Collection: `safety-vision-alumno-ppe-collection`

7. **SNS**
   - Topic: `safety-vision-alumno-safety-alerts` - notificaciones

8. **CloudWatch**
   - Logs de Lambda para debugging
   - Métricas de rendimiento y errores

#### Comandos AWS CLI Útiles

```bash
# Verificar Rekognition
aws rekognition describe-project --project-arn PROJECT_ARN --region eu-west-1

# Listar análisis en DynamoDB
aws dynamodb scan --table-name safety-vision-alumno-analysis --region eu-west-1

# Ver estadísticas
aws dynamodb scan --table-name safety-vision-alumno-stats --region eu-west-1

# Revisar logs de Lambda
aws logs tail /aws/lambda/safety-vision-alumno-analyze --follow --region eu-west-1

# Listar imágenes en S3
aws s3 ls s3://safety-vision-alumno-images/ --recursive --region eu-west-1
```

### 🎯 Flujo Completo de Análisis PPE

1. **Usuario** sube imagen en el frontend
2. **Frontend** envía a API Gateway (`POST /upload`)
3. **API Gateway** invoca Lambda Upload
4. **Lambda** guarda imagen en S3 y metadata en DynamoDB
5. **Usuario** solicita análisis PPE
6. **Frontend** envía a API Gateway (`POST /analyze`)
7. **API Gateway** invoca Lambda Analysis
8. **Lambda** envía imagen a Rekognition
9. **Rekognition** detecta PPE con confidence scores
10. **Lambda** guarda resultados en DynamoDB
11. **Lambda** envía alertas SNS si es necesario
12. **Frontend** muestra resultados con visualización

---

## 🔧 Troubleshooting

### Error: "SSM parameter /cdk-bootstrap/hnb659fds/version not found"

**Solución:** Ejecutar bootstrap primero:
```bash
cdk bootstrap aws://ACCOUNT_ID/eu-west-1
```

### Error: "Rekognition project not found"

**Solución:** Verifica que Rekognition esté habilitado en tu región:
```bash
aws rekognition describe-project --project-arn PROJECT_ARN --region eu-west-1
```

### Las imágenes no se analizan

**Solución:** Revisa logs de Lambda Analysis:
```bash
aws logs tail /aws/lambda/safety-vision-alumno-analyze --follow --region eu-west-1
```

### La aplicación no carga

**Solución:** Recarga la página con Ctrl+Shift+R para limpiar la caché del navegador.

### Error de CORS

**Solución:** El API Gateway ya tiene CORS configurado. Verifica los headers en la respuesta.

---

## 🧹 Limpieza (Opcional)

Para eliminar todos los recursos creados:

```bash
cdk destroy --app "python3 cdk_app.py --lab-name safety-vision-alumno"
```

> **👉 Nota:** CDK eliminará automáticamente todos los recursos (Rekognition, Lambda, DynamoDB, API Gateway, S3, IAM roles, etc.).

---

## 🎓 Resultado Esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ **Desplegado** una aplicación de Computer Vision completa con AWS CDK
- ✅ **Configurado** Rekognition para detección de PPE
- ✅ **Integrado** múltiples servicios AWS (S3, DynamoDB, Lambda, API Gateway)
- ✅ **Creado** una interfaz web moderna para análisis de seguridad
- ✅ **Procesado** imágenes con metadata en DynamoDB
- ✅ **Implementado** análisis PPE con detección en tiempo real
- ✅ **Verificado** todos los servicios AWS desplegados
- ✅ **Comprendido** la arquitectura serverless y sus interacciones
- ✅ **Aprendido** a usar AWS CDK para infraestructura como código
- ✅ **Entendido** la integración de Computer Vision con servicios AWS

### 🚀 **Aplicación SafetyVision Pro 100% Funcional**

**Frontend**: http://safety-vision-alumno-frontend-{ACCOUNT_ID}.s3-website-eu-west-1.amazonaws.com  
**API**: https://{api-id}.execute-api.eu-west-1.amazonaws.com/prod/

La aplicación está lista para producción con todas las funcionalidades de Computer Vision implementadas.

---

## 🎯 **Elección del Método de Despliegue**

### 📚 **Método Paso a Paso (Recomendado para aprendizaje)**
- ✅ **Ideal para**: Primer despliegue, aprendizaje, debugging
- ✅ **Ventajas**: Control total, comprensión detallada, fácil troubleshooting
- ✅ **Tiempo**: 15-25 minutos con monitoreo individual

### ⚡ **Método Completo (Recomendado para producción)**
- ✅ **Ideal para**: Despliegues rápidos, producción, staging
- ✅ **Ventajas**: Más rápido, automático, consistente
- ✅ **Tiempo**: 15-20 minutos en un solo comando

### 🔄 **Método Híbrido (Balanceado)**
- ✅ **Ideal para**: Desarrollo rápido con control parcial
- ✅ **Ventajas**: Eficiencia + verificación por fases
- ✅ **Tiempo**: 15-20 minutos en dos fases

**Recomendación**: Usa el método paso a paso para tu primer despliegue, luego el método completo para actualizaciones y producción.
