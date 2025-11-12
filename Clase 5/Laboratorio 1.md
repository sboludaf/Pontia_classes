# Laboratorio 1: CloudFormation (S3 + SNS + Lambda + DynamoDB)

## Paso 1 – Desplegar Plantilla Backend (SNS + Lambda + DynamoDB)

En este paso, desplegaremos la infraestructura backend usando CloudFormation a través de la consola de AWS.

### 1.1 – Acceder a CloudFormation

1. En la consola de AWS, busca `CloudFormation` en la barra de búsqueda superior.
2. Ve al dashboard de CloudFormation.
3. Haz clic en **Create stack**.
4. Selecciona **With new resources (standard)**.

### 1.2 – Subir la plantilla

1. En **Prepare template**, selecciona **Template is ready**.
2. En **Specify template**, selecciona **Upload a template file**.
3. Haz clic en **Choose file** y selecciona el archivo `00-Infrastructure-APIGateway.yaml`.
4. Haz clic en **Next**.

### 1.3 – Configurar parámetros del stack

1. En **Stack name**, introduce: `NOMBREALUMNO-newsletter-backend` (reemplaza `NOMBREALUMNO` con tu nombre o apellido)
2. En **Parameters**:
   - **LabName:** `NOMBREALUMNO-newsletter` (este nombre se usará para todos los recursos)
3. Haz clic en **Next**.

### 1.4 – Configurar opciones del stack

1. En **Stack failure options**, selecciona **Rollback all stack resources**.
2. Haz clic en **Next**.

### 1.5 – Revisar y crear

1. Revisa la configuración.
2. En **Capabilities**, marca la casilla: "I acknowledge that AWS CloudFormation might create IAM resources."
3. Haz clic en **Create stack**.

> **👉 Resultado:** CloudFormation comienza a desplegar los recursos.

### 1.6 – Esperar a que se complete

1. En el dashboard de CloudFormation, selecciona tu stack (`NOMBREALUMNO-newsletter-stack`).
2. Ve a la pestaña **Events** para ver el progreso.
3. Espera a que el estado cambie a **CREATE_COMPLETE** (puede tardar 2-3 minutos).

> **✅ Resultado esperado:** El stack se ha creado exitosamente con todos los recursos (SNS, Lambda, DynamoDB, API Gateway).

### 1.7 – Obtener el Endpoint del API Gateway

1. En el dashboard de CloudFormation, selecciona tu stack.
2. Ve a la pestaña **Outputs**.
3. Busca el output `ApiEndpoint` (ejemplo: `https://XXXXXXXX.execute-api.eu-west-1.amazonaws.com/prod`).
4. **Copia esta URL** - la necesitarás en el siguiente paso.

> **👉 Explicación:** Este es el endpoint que tu aplicación web usará para comunicarse con el backend.

---

## Paso 2 – Realizar Modificaciones en index.html

1. Abre el archivo `index.html` en tu editor de código.
2. Localiza la línea que contiene `const API_GATEWAY_URL`:

```javascript
const API_GATEWAY_URL = 'https://XXXXXXXX.execute-api.eu-west-1.amazonaws.com/prod';
```

3. Reemplaza la URL con el `ApiEndpoint` que obtuviste en el Paso 1.7.

**Ejemplo:**
```javascript
const API_GATEWAY_URL = 'https://a1b2c3d4e5.execute-api.eu-west-1.amazonaws.com/prod';
```

4. **No cambies nada más.** Los paths (`/register`, `/publish`, `/subscribers`) se construyen automáticamente.

5. Guarda el archivo.

> **👉 Resultado:** La aplicación web ahora apunta a tu backend.

---

## Paso 3 – Desplegar Plantilla Frontend (S3)

En este paso, desplegaremos el bucket S3 para alojar la aplicación web.

### 3.1 – Crear nuevo stack para el frontend

1. En el dashboard de CloudFormation, haz clic en **Create stack**.
2. Selecciona **With new resources (standard)**.
3. En **Prepare template**, selecciona **Template is ready**.
4. En **Specify template**, selecciona **Upload a template file**.
5. Haz clic en **Choose file** y selecciona el archivo `01-Frontend.yaml`.
6. Haz clic en **Next**.

### 3.2 – Configurar parámetros del stack frontend

1. En **Stack name**, introduce: `NOMBREALUMNO-newsletter-frontend`
2. En **Parameters**:
   - **LabName:** `NOMBREALUMNO-newsletter` (debe ser el **mismo** que en el backend)
3. Haz clic en **Next**.

### 3.3 – Revisar y crear

1. Revisa la configuración.
2. Haz clic en **Create stack**.

> **👉 Resultado:** CloudFormation comienza a desplegar el bucket S3.

### 3.4 – Esperar a que se complete

1. En el dashboard de CloudFormation, selecciona tu stack frontend.
2. Espera a que el estado cambie a **CREATE_COMPLETE**.

### 3.5 – Obtener información del bucket

1. En el dashboard de CloudFormation, selecciona tu stack frontend.
2. Ve a la pestaña **Outputs**.
3. Anota:
   - **BucketName:** Nombre del bucket S3
   - **WebsiteUrl:** URL del sitio web (ejemplo: `http://NOMBREALUMNO-newsletter-ACCOUNTID.s3-website-eu-west-1.amazonaws.com`)

> **👉 Resultado:** Tienes el nombre del bucket y la URL del sitio web.

---

## Paso 4 – Subir index.html al bucket S3

1. En la consola de AWS, busca `S3` en la barra de búsqueda superior.
2. Ve al dashboard de S3.
3. Selecciona el bucket que se creó con CloudFormation (el nombre está en los Outputs del stack frontend).
4. Ve a la pestaña **Objects**.
5. Haz clic en **Upload**.
6. Arrastra o selecciona el archivo `index.html` (el que modificaste en el Paso 2).
7. Haz clic en **Upload**.

> **✅ Resultado esperado:** El archivo `index.html` se ha subido al bucket S3.

---

## Paso 5 – Probar la aplicación

### 5.1 – Acceder a la aplicación

1. Abre tu navegador web.
2. Ve a la **WebsiteUrl** que obtuviste en el Paso 3.5 (ejemplo: `http://NOMBREALUMNO-newsletter-ACCOUNTID.s3-website-eu-west-1.amazonaws.com`).
3. Deberías ver la interfaz de la aplicación Newsletter.

### 5.2 – Registrar un suscriptor

1. En el formulario **Registrar Suscriptor**:
   - **Email:** Introduce un email de prueba
   - **Nombre:** Introduce un nombre
2. Haz clic en **Registrar**.
3. Abre la consola del navegador (F12) para ver los logs.

> **✅ Resultado esperado:**
> - El suscriptor se registra en DynamoDB
> - Se crea una suscripción en SNS
> - Ves un mensaje de éxito

### 5.3 – Publicar un mensaje

1. En el formulario **Publicar Mensaje**:
   - **Asunto:** Introduce un asunto
   - **Mensaje:** Introduce un mensaje
2. Haz clic en **Publicar**.
3. Verifica en la consola que el mensaje se envía.

> **✅ Resultado esperado:**
> - El mensaje se publica en SNS
> - Se envía a todos los suscriptores
> - Ves un mensaje de confirmación

### 5.4 – Ver suscriptores

1. Haz clic en **Obtener Suscriptores**.
2. Deberías ver la lista de suscriptores registrados.

> **✅ Resultado esperado:**
> - Se muestra la lista de suscriptores
> - Incluye email, nombre y fecha de registro

---

## Paso 6 – Verificar recursos en AWS

### 6.1 – Verificar DynamoDB

1. En la consola de AWS, busca `DynamoDB`.
2. Ve a **Tables**.
3. Selecciona la tabla `NOMBREALUMNO-newsletter-subscribers`.
4. Ve a **Items** para ver los suscriptores registrados.

> **👉 Resultado:** Verificas que los datos se guardan correctamente en DynamoDB.

### 6.2 – Verificar SNS

1. En la consola de AWS, busca `SNS`.
2. Ve a **Topics**.
3. Selecciona el topic `NOMBREALUMNO-newsletter-topic`.
4. Ve a **Subscriptions** para ver los suscriptores de SNS.

> **👉 Resultado:** Verificas que los suscriptores se crean en SNS.

### 6.3 – Verificar Lambdas

1. En la consola de AWS, busca `Lambda`.
2. Ve a **Functions**.
3. Deberías ver tres funciones:
   - `NOMBREALUMNO-newsletter-register-user`
   - `NOMBREALUMNO-newsletter-publish-message`
   - `NOMBREALUMNO-newsletter-get-subscribers`
4. Selecciona una Lambda y ve a **Monitor** → **Logs** para ver los logs de ejecución.

> **👉 Resultado:** Verificas que las Lambdas se ejecutan correctamente.

### 6.4 – Verificar API Gateway

1. En la consola de AWS, busca `API Gateway`.
2. Selecciona el API `NOMBREALUMNO-newsletter-api`.
3. Ve a **Resources** para ver los endpoints:
   - `/register` (POST)
   - `/publish` (POST)
   - `/subscribers` (GET)

> **👉 Resultado:** Verificas que los endpoints están configurados correctamente.

---

## Paso 7 – Limpieza (Opcional)

Si quieres eliminar todos los recursos creados:

### 7.1 – Eliminar el stack frontend

1. En el dashboard de CloudFormation, selecciona tu stack frontend (`NOMBREALUMNO-newsletter-frontend-stack`).
2. Haz clic en **Delete**.
3. Confirma la eliminación.

> **👉 Nota:** CloudFormation eliminará automáticamente el bucket S3 y todos sus contenidos.

### 7.2 – Eliminar el stack backend

1. En el dashboard de CloudFormation, selecciona tu stack backend (`NOMBREALUMNO-newsletter-stack`).
2. Haz clic en **Delete**.
3. Confirma la eliminación.

> **👉 Nota:** CloudFormation eliminará automáticamente todos los recursos (SNS, Lambda, DynamoDB, API Gateway, IAM roles, etc.).

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Desplegado la plantilla backend con CloudFormation (SNS, Lambda, DynamoDB, API Gateway).
- ✅ Modificado el `index.html` con la URL del API Gateway.
- ✅ Desplegado la plantilla frontend con CloudFormation (S3).
- ✅ Subido el `index.html` al bucket S3.
- ✅ Accedido a la aplicación Newsletter desde el navegador.
- ✅ Registrado suscriptores en la aplicación.
- ✅ Publicado mensajes que se envían a todos los suscriptores.
- ✅ Visualizado la lista de suscriptores.
- ✅ Verificado los recursos en DynamoDB, SNS, Lambda y API Gateway.
- ✅ Comprendido cómo CloudFormation automatiza el despliegue de infraestructura compleja.
- ✅ Aprendido a integrar múltiples servicios de AWS (S3, SNS, Lambda, DynamoDB, API Gateway).
