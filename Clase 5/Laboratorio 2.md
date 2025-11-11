# Laboratorio 2: AWS CDK Python (Newsletter Lab Completo)

## Paso 1 – Preparar el archivo ZIP localmente

En este paso, prepararemos el archivo ZIP con el código del proyecto para subirlo a CloudShell.

### 1.1 – Comprimir la carpeta del proyecto

1. Abre una terminal en tu máquina local.
2. Navega a la carpeta padre de Laboratorio 2:

```bash
cd /Users/personal/Projects/Pontia/Clase\ 5
```

3. Crea un archivo ZIP con la carpeta Laboratorio 2:

```bash
zip -r Laboratorio2.zip Laboratorio\ 2/
```

> **👉 Resultado:** Se crea el archivo `Laboratorio2.zip` en la carpeta Clase 5.

---

## Paso 2 – Acceder a AWS CloudShell

1. Abre la consola de AWS en tu navegador.
2. En la barra superior, busca el icono de **CloudShell** (terminal) o haz clic en el icono de terminal.
3. Espera a que CloudShell se cargue (puede tardar unos segundos).

> **👉 Resultado:** Tienes una terminal en la nube lista para usar.

---

## Paso 3 – Subir el archivo ZIP a CloudShell

### 3.1 – Usar el gestor de archivos de CloudShell

1. En CloudShell, haz clic en el icono de **Actions** (arriba a la derecha).
2. Selecciona **Upload file**.
3. Selecciona el archivo `Laboratorio2.zip` de tu máquina local.
4. Espera a que se complete la carga.

> **✅ Resultado esperado:** El archivo ZIP está en CloudShell.

### 3.2 – Verificar que se subió correctamente

```bash
ls -lh Laboratorio2.zip
```

> **👉 Resultado:** Deberías ver el archivo listado con su tamaño.

---

## Paso 4 – Descomprimir y preparar el proyecto

```bash
# Descomprimir el archivo
unzip Laboratorio2.zip

# Navegar a la carpeta del proyecto
cd Laboratorio\ 2

# Verificar que los archivos están presentes
ls -la
```

> **👉 Resultado:** Ves los archivos `deploy_all.py`, `requirements.txt` y la carpeta `resources/`.

---

## Paso 5 – Instalar dependencias en CloudShell

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

## Paso 6 – Bootstrap del entorno CDK

El bootstrap prepara tu cuenta AWS para usar CDK:

```bash
# Obtener tu AWS Account ID
aws sts get-caller-identity --query Account --output text

# Bootstrap (reemplaza 838205824064 con tu Account ID)
cdk bootstrap aws://838205824064/eu-west-1
```

> **👉 Explicación:** Esto crea un bucket S3 y otros recursos necesarios para que CDK funcione en tu cuenta.

> **✅ Resultado esperado:** Ves un mensaje indicando que el bootstrap se completó.

---

## Paso 7 – Desplegar el Backend (sin Frontend)

Primero desplegaremos solo el backend (SNS, Lambda, DynamoDB, API Gateway). El frontend se subirá en un paso posterior.

```bash
# Reemplaza "usuario1" con tu nombre o apellido
cdk deploy --app "python3 deploy_all.py --lab-name newsletter-lab-alumno" --require-approval never
```

**Ejemplo:**
```bash
cdk deploy --app "python3 deploy_all.py --lab-name newsletter-lab-sboludaf" --require-approval never
```

### 7.1 – Qué se despliega

✅ **Backend:**
- SNS Topic: `newsletter-lab-usuario1-topic`
- DynamoDB Table: `newsletter-lab-usuario1-subscribers`
- 3 Lambda Functions:
  - `newsletter-lab-usuario1-register-user`
  - `newsletter-lab-usuario1-publish-message`
  - `newsletter-lab-usuario1-get-subscribers`
- API Gateway: `newsletter-lab-usuario1-api` (con CORS habilitado)
- IAM Role: `newsletter-lab-usuario1-lambda-execution-role`

✅ **Frontend (S3 Bucket):**
- S3 Bucket: `newsletter-lab-usuario1-{ACCOUNT_ID}` (creado pero vacío)
- Website configuration
- Políticas de acceso público

### 7.2 – Esperar a que se complete

El despliegue tarda aproximadamente 50 segundos. Verás:

```
✅ newsletter-lab-usuario1-stack: deployment succeeded
```

> **👉 Resultado:** El backend está completamente desplegado.

---

## Paso 8 – Obtener las URLs

Después del despliegue, verás los outputs en la terminal. Busca:

```
WebsiteUrl = http://newsletter-lab-usuario1-838205824064.s3-website-eu-west-1.amazonaws.com
ApiEndpoint = https://XXXXXXXX.execute-api.eu-west-1.amazonaws.com/prod
```

**Alternativa: Obtener URLs con AWS CLI**

```bash
# API Gateway Endpoint
aws cloudformation describe-stacks \
  --stack-name newsletter-lab-usuario1-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text \
  --region eu-west-1

# S3 Website URL
aws cloudformation describe-stacks \
  --stack-name newsletter-lab-usuario1-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`WebsiteUrl`].OutputValue' \
  --output text \
  --region eu-west-1
```

> **👉 Resultado:** Tienes las URLs para acceder a la aplicación.

---

## Paso 9 – Subir el Frontend a S3

Ahora que el backend está desplegado y tenemos el `ApiEndpoint`, subiremos el frontend al bucket S3.

### 9.1 – Subir el frontend con el parámetro --upload-frontend

```bash
# Reemplaza "usuario1" con tu nombre
cdk deploy --app "python3 deploy_all.py --lab-name newsletter-lab-sboludaf --upload-frontend" --require-approval never
```

Este comando:
- Detecta que el stack ya existe
- Sube el frontend (`index.html`, `styles.css`, `app.js`) al bucket S3
- Inyecta automáticamente la URL del API Gateway en el `index.html`

### 9.2 – Esperar a que se complete

```
✅ newsletter-lab-usuario1-stack: deployment succeeded
```

> **👉 Resultado:** El frontend está subido al bucket S3 y listo para usar.

---

## Paso 10 – Acceder a la aplicación

1. Abre tu navegador web.
2. Ve a la **WebsiteUrl** que obtuviste en el Paso 8.
3. Deberías ver la interfaz de la aplicación Newsletter.

> **✅ Resultado esperado:** La aplicación carga correctamente.

---

## Paso 11 – Probar la aplicación

### 6.1 – Registrar un usuario

1. En el panel **📝 Registrarse**:
   - **Nombre:** Introduce tu nombre
   - **Email:** Introduce tu email
2. Haz clic en **Registrarse**.
3. Abre la consola del navegador (F12) para ver los logs.

> **✅ Resultado esperado:**
> - El usuario se registra en DynamoDB
> - Se crea una suscripción en SNS
> - Recibirás un email de confirmación de AWS SNS

### 6.2 – Confirmar suscripción

1. Abre tu email.
2. Busca el email de confirmación de AWS SNS.
3. Haz clic en el enlace de confirmación.

> **✅ Resultado esperado:** Tu suscripción está confirmada.

### 6.3 – Acceder al Panel de Administrador

1. En el panel **🔐 Panel Administrador**:
   - **Clave:** `admin-secret-key-123`
2. Haz clic en **Verificar**.

> **✅ Resultado esperado:** Se abre el panel de admin.

### 6.4 – Enviar un mensaje

1. En el panel de admin:
   - **Asunto:** Introduce un asunto
   - **Mensaje:** Introduce un mensaje
2. Haz clic en **Enviar a Confirmados**.
3. Verifica en la consola que el mensaje se envía.

> **✅ Resultado esperado:**
> - El mensaje se publica en SNS
> - Se envía a todos los suscriptores confirmados
> - Recibirás el mensaje por email

### 6.5 – Ver suscriptores

1. En el panel de admin, haz clic en **Actualizar Suscriptores**.
2. Deberías ver la lista de suscriptores registrados.

> **✅ Resultado esperado:** Se muestra la lista con email, nombre y fecha de registro.

---

## Paso 12 – Verificar recursos en AWS

### 7.1 – Verificar DynamoDB

1. En la consola de AWS, busca `DynamoDB`.
2. Ve a **Tables**.
3. Selecciona la tabla `newsletter-lab-usuario1-subscribers`.
4. Ve a **Items** para ver los suscriptores registrados.

> **👉 Resultado:** Verificas que los datos se guardan correctamente.

### 7.2 – Verificar SNS

1. En la consola de AWS, busca `SNS`.
2. Ve a **Topics**.
3. Selecciona el topic `newsletter-lab-usuario1-topic`.
4. Ve a **Subscriptions** para ver los suscriptores de SNS.

> **👉 Resultado:** Verificas que las suscripciones se crean correctamente.

### 7.3 – Verificar Lambdas

1. En la consola de AWS, busca `Lambda`.
2. Ve a **Functions**.
3. Deberías ver tres funciones:
   - `newsletter-lab-usuario1-register-user`
   - `newsletter-lab-usuario1-publish-message`
   - `newsletter-lab-usuario1-get-subscribers`
4. Selecciona una Lambda y ve a **Monitor** → **Logs** para ver los logs de ejecución.

> **👉 Resultado:** Verificas que las Lambdas se ejecutan correctamente.

### 7.4 – Ver logs de Lambda

```bash
# Logs de registro
aws logs tail /aws/lambda/newsletter-lab-usuario1-register-user --follow --region eu-west-1

# Logs de publicación
aws logs tail /aws/lambda/newsletter-lab-usuario1-publish-message --follow --region eu-west-1

# Logs de suscriptores
aws logs tail /aws/lambda/newsletter-lab-usuario1-get-subscribers --follow --region eu-west-1
```

> **👉 Resultado:** Ves los logs detallados de cada Lambda.

### 7.5 – Verificar API Gateway

1. En la consola de AWS, busca `API Gateway`.
2. Selecciona el API `newsletter-lab-usuario1-api`.
3. Ve a **Resources** para ver los endpoints:
   - `/register` (POST)
   - `/publish` (POST)
   - `/subscribers` (GET)

> **👉 Resultado:** Verificas que los endpoints están configurados correctamente.

---

## Paso 13 – Entender la estructura del proyecto CDK

### 8.1 – Archivo principal: deploy_all.py

Este archivo contiene toda la infraestructura:

```python
class NewsletterLabCompleteStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, lab_name: str, **kwargs):
        # SNS Topic
        # DynamoDB Table
        # IAM Role
        # Lambda Functions
        # API Gateway
        # S3 Bucket
        # Frontend upload
```

### 8.2 – Estructura de carpetas

```
Laboratorio 2/
├── deploy_all.py           # ⭐ Archivo principal (CDK Stack)
├── requirements.txt        # Dependencias Python
└── resources/
    ├── lambdas/
    │   ├── register.py     # Lambda de registro
    │   ├── publish.py      # Lambda de publicación
    │   └── subscribers.py  # Lambda de suscriptores
    └── frontend/
        ├── index.html      # HTML principal
        ├── styles.css      # Estilos CSS
        ├── app.js          # Lógica JavaScript
        └── config.js       # Configuración del frontend
```

### 8.3 – Parámetros disponibles

```bash
python3 deploy_all.py \
  --lab-name newsletter-lab-usuario1 \
  --account 838205824064 \
  --region eu-west-1 \
  --upload-frontend
```

**Opciones:**
- `--lab-name`: Nombre único del laboratorio (default: newsletter-lab)
- `--account`: AWS Account ID (default: 838205824064)
- `--region`: AWS Region (default: eu-west-1)
- `--upload-frontend`: Subir frontend a S3 automáticamente

---

## Paso 14 – Troubleshooting

### Error: "SSM parameter /cdk-bootstrap/hnb659fds/version not found"

**Solución:** Ejecutar bootstrap primero:
```bash
cdk bootstrap aws://838205824064/eu-west-1
```

### Error: "Export with name ... is already exported"

**Solución:** Usa un `lab_name` único:
```bash
cdk deploy --app "python3 deploy_all.py --lab-name newsletter-lab-nuevo-usuario --upload-frontend" --require-approval never
```

### La aplicación no carga o muestra errores en consola

**Solución:** Recarga la página con Ctrl+Shift+R para limpiar la caché del navegador.

### Verificar config.json en S3

```bash
aws s3 cp s3://newsletter-lab-usuario1-838205824064/config.json - --region eu-west-1
```

Debe mostrar:
```json
{"apiEndpoint": "https://XXXXXXXX.execute-api.eu-west-1.amazonaws.com/prod"}
```

---

## Paso 15 – Limpieza (Opcional)

Para eliminar todos los recursos creados:

```bash
cdk destroy --app "python3 deploy_all.py --lab-name newsletter-lab-usuario1"
```

> **👉 Nota:** CDK eliminará automáticamente todos los recursos (SNS, Lambda, DynamoDB, API Gateway, S3, IAM roles, etc.).

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Instalado y configurado AWS CDK Python.
- ✅ Ejecutado bootstrap en su cuenta AWS.
- ✅ Desplegado la infraestructura completa con un único comando CDK.
- ✅ Comprendido cómo CDK automatiza el despliegue de recursos complejos.
- ✅ Accedido a la aplicación Newsletter desde el navegador.
- ✅ Registrado usuarios y confirmado suscripciones.
- ✅ Enviado mensajes a través de SNS.
- ✅ Visualizado la lista de suscriptores.
- ✅ Verificado los recursos en DynamoDB, SNS, Lambda y API Gateway.
- ✅ Entendido la diferencia entre CloudFormation (declarativo) y CDK (programático).
- ✅ Aprendido a usar CDK para infraestructura como código (IaC).
- ✅ Comprendido cómo CDK genera automáticamente CloudFormation templates.
