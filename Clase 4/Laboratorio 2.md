# Laboratorio 2: S3 (Static Web App) y Lambda

## Paso 1 – Crear Bucket S3

1. En la consola de AWS, busca `S3` en la barra de búsqueda superior.
2. Ve al dashboard de S3.
3. Haz clic en **Create bucket**.
4. En el formulario:
   - **Bucket name:** `NOMBREALUMNO-notas-app` (reemplaza `NOMBREALUMNO` con tu nombre o apellido)
   - **AWS Region:** `eu-west-1` (Europa - Irlanda)
5. En **Block Public Access settings**:
   - **Desactiva** todas las opciones (necesitamos acceso público):
     - ☐ Block all public access
     - ☐ Block public access to buckets and objects granted through new access control lists (ACLs)
     - ☐ Block public access to buckets and objects granted through any access control lists (ACLs)
     - ☐ Block public access to buckets and objects granted through new public bucket or access point policies
     - ☐ Block public and cross-account access to buckets and objects through any public bucket or access point policies
6. Marca la casilla de confirmación: "I acknowledge that the current settings might result in this bucket and the objects within becoming public."
7. Haz clic en **Create bucket**.

> **👉 Resultado:** El bucket S3 ha sido creado con acceso público habilitado.

---

## Paso 2 – Configurar Static Web Hosting

1. En el dashboard de S3, selecciona tu bucket (`NOMBREALUMNO-notas-app`).
2. Ve a la pestaña **Properties**.
3. Desplázate hacia abajo hasta encontrar **Static website hosting**.
4. Haz clic en **Edit**.
5. En el formulario:
   - **Static website hosting:** Selecciona **Enable**
   - **Index document:** `index.html`
   - **Error document:** `index.html` (opcional, para SPA)
6. Haz clic en **Save changes**.
7. Copia la **Bucket website endpoint** (ejemplo: `http://NOMBREALUMNO-notas-app.s3-website-eu-west-1.amazonaws.com`). La necesitarás más adelante.

> **👉 Resultado:** El bucket está configurado como sitio web estático.

---

## Paso 3 – Añadir Policy que publique objetos

1. En el dashboard de S3, selecciona tu bucket.
2. Ve a la pestaña **Permissions**.
3. Desplázate hasta **Bucket policy**.
4. Haz clic en **Edit**.
5. Reemplaza el contenido con la siguiente política (reemplaza `NOMBREALUMNO-notas-app` con el nombre de tu bucket):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::NOMBREALUMNO-notas-app/*"
    }
  ]
}
```

6. Haz clic en **Save**.

> **👉 Resultado:** Todos los objetos del bucket son ahora públicamente legibles.

---

## Paso 4 – Modificar URLs de Lambdas en app.js

1. Abre el archivo `app.js` en tu editor de código.
2. Localiza las líneas 9-10:

```javascript
const CONFIG = {
    LAMBDA_WRITE_URL: 'https://2icc3yp7h5ubkzydx46apbumw40npxbi.lambda-url.eu-west-1.on.aws/',
    LAMBDA_READ_URL: 'https://h4s7xgl477lmqu6ko6nyqdx7yi0fywdf.lambda-url.eu-west-1.on.aws/'
};
```

3. Reemplaza las URLs con las Function URLs de tus Lambdas:
   - `LAMBDA_WRITE_URL`: URL de la Lambda `NOMBREALUMNO-Write`
   - `LAMBDA_READ_URL`: URL de la Lambda `NOMBREALUMNO-Read`

> **👉 Cómo obtener las URLs:**
> 1. Ve a AWS Console → Lambda
> 2. Selecciona tu Lambda (ej. `NOMBREALUMNO-Write`)
> 3. Ve a **Configuration** → **Function URL**
> 4. Copia la URL completa

4. Guarda el archivo.

> **👉 Resultado:** La aplicación ahora apunta a tus Lambdas.

---

## Paso 5 – Subir archivos al bucket S3

### Opción A: Usando AWS Console (Manual)

1. En el dashboard de S3, selecciona tu bucket.
2. Ve a la pestaña **Objects**.
3. Haz clic en **Upload**.
4. Arrastra o selecciona los siguientes archivos:
   - `index.html`
   - `styles.css`
   - `app.js`
5. Haz clic en **Upload**.

> **✅ Resultado esperado:** Los archivos se suben correctamente.

### Opción B: Usando AWS CLI (Recomendado)

1. Abre una terminal en el directorio del proyecto.
2. Ejecuta:

```bash
# Subir todos los archivos (excepto README.md)
aws s3 sync . s3://NOMBREALUMNO-notas-app \
  --exclude "README.md" \
  --exclude ".git/*" \
  --acl public-read
```

Reemplaza `NOMBREALUMNO-notas-app` con el nombre de tu bucket.

> **✅ Resultado esperado:** Los archivos se sincronizan con S3.

---

## Paso 6 – Probar la aplicación

1. Abre tu navegador web.
2. Ve a la URL del bucket (obtenida en el Paso 2):
   ```
   http://NOMBREALUMNO-notas-app.s3-website-eu-west-1.amazonaws.com
   ```

3. Deberías ver la interfaz de la aplicación de gestión de notas.

### Pruebas funcionales

#### 6.1 – Registrar una nota

1. Completa el formulario:
   - **Nombre:** Tu nombre
   - **Nota:** Una nota de prueba
2. Haz clic en **Enviar**.
3. Abre la consola del navegador (F12) para ver los logs detallados.

> **✅ Resultado esperado:** 
> - La nota se registra en DynamoDB
> - Ves un mensaje de éxito
> - Los logs muestran el flujo completo

#### 6.2 – Visualizar notas

1. Haz clic en **Actualizar notas** o recarga la página.
2. Deberías ver la lista de notas registradas.
3. Abre la consola para ver los logs del escaneo de DynamoDB.

> **✅ Resultado esperado:**
> - Las notas se cargan desde DynamoDB
> - Se muestran con timestamp y nombre

#### 6.3 – Cambiar límite de notas

1. Selecciona un número diferente en el dropdown **Límite de notas**.
2. Haz clic en **Actualizar notas**.
3. Verifica que se carga el número correcto de notas.

> **✅ Resultado esperado:**
> - El límite se aplica correctamente
> - Los logs muestran la nueva petición

---

## Paso 7 – Verificar logs en la consola

1. Abre la aplicación en el navegador.
2. Abre las DevTools (F12 o Click derecho → Inspeccionar).
3. Ve a la pestaña **Console**.
4. Realiza operaciones (registrar nota, actualizar lista).
5. Observa los logs detallados que muestran:
   - Configuración inicial
   - Elementos DOM encontrados
   - Eventos del formulario
   - Llamadas HTTP (URL, método, payload)
   - Respuestas de las Lambdas
   - Tiempos de respuesta
   - Procesamiento de datos

> **👉 Explicación:** Los logs educativos permiten entender exactamente qué está pasando en cada paso.

---

## Paso 8 – Troubleshooting

### Error de CORS

**Síntoma:** 
```
Access to fetch at 'https://...' from origin 'http://...' has been blocked by CORS policy
```

**Solución:**
1. Ve a AWS Console → Lambda
2. Selecciona tu Lambda
3. Ve a **Configuration** → **Function URL** → **Edit**
4. Verifica que CORS esté habilitado con:
   - **Allowed origins:** `*`
   - **Allowed methods:** `*`
   - **Allowed headers:** `Content-Type`

### Notas no se cargan

**Síntoma:** La lista de notas está vacía o muestra error.

**Solución:**
1. Abre la consola (F12) y busca errores
2. Verifica que las URLs de las Lambdas en `app.js` sean correctas
3. Verifica que las Lambdas estén activas en AWS
4. Verifica que DynamoDB tenga datos (ve a AWS Console → DynamoDB → Tables → tu tabla)

### No se puede subir a S3

**Síntoma:** Error al ejecutar `aws s3 sync`.

**Solución:**
1. Verifica tus credenciales AWS: `aws configure`
2. Verifica que tengas permisos de S3
3. Verifica que el nombre del bucket sea correcto
4. Verifica que el bucket exista: `aws s3 ls`

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Creado un bucket S3 con acceso público habilitado.
- ✅ Configurado Static Web Hosting en el bucket.
- ✅ Añadido una política de bucket que permite lectura pública.
- ✅ Modificado las URLs de las Lambdas en `app.js`.
- ✅ Subido los archivos de la aplicación a S3.
- ✅ Accedido a la aplicación desde el navegador.
- ✅ Registrado y visualizado notas en la aplicación.
- ✅ Verificado los logs en la consola del navegador.
- ✅ Entendido la arquitectura completa: S3 → Lambda → DynamoDB.
- ✅ Aprendido a depurar aplicaciones web conectadas a AWS.
