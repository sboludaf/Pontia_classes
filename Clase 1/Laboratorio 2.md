# Laboratorio 2: Introducción a Amazon S3

## Paso 1 – Acceder al servicio S3

1. Inicia sesión en la **AWS Management Console**.
2. En la barra de búsqueda superior, escribe `S3` y selecciona el servicio.
3. Accederás al panel principal de S3, donde verás la lista de buckets existentes (si es una cuenta nueva, estará vacío).

---

## Paso 2 – Navegación por el servicio

En la consola de S3, encontrarás los siguientes elementos principales:

- **Buckets:** "Contenedores" lógicos de objetos (almacenamiento de datos).
- **Objects:** Archivos que se suben (hasta 5 TB por objeto).
- **Properties:** Configuración de versionado, cifrado, políticas de acceso.
- **Permissions:** Control de acceso (ACLs, bucket policies, IAM).

> **👉 Importante:** S3 aparenta ser global, pero cada bucket está asociado a una región concreta. Los datos se almacenan en la región que selecciones.

---

## Paso 3 – Crear un bucket S3

1. En la consola de S3, haz clic en el botón **Create bucket**.
2. En el formulario que aparece:
   - **Bucket name:** Introduce un nombre único global (ejemplo: `lab-s3-primerapellido2025`).
   - **AWS Region:** Selecciona la región más cercana (ej. `Europe (Madrid) eu-south-2`).
3. Desplázate hacia abajo y verifica que **Block all public access** esté **activado** (se puede desmarcar más adelante solo para pruebas).
4. Haz clic en **Create bucket** → verás tu bucket en la lista de buckets.

---

## Paso 4 – Activar versionado

1. En la consola de S3, haz clic en tu bucket recién creado para abrirlo.
2. Ve a la pestaña **Properties** (en la parte superior derecha).
3. Busca la sección **Bucket Versioning**.
4. Haz clic en **Edit**.
5. Selecciona **Enable** para activar el versionado.
6. Haz clic en **Save changes**.

> **👉 Resultado:** Ahora, cada vez que subas un archivo con el mismo nombre, S3 guardará varias versiones del archivo. Podrás recuperar versiones anteriores si es necesario.

---

## Paso 5 – Probar acceso al archivo público

### 5.1 – Subir un archivo

1. En tu bucket, ve a la pestaña **Objects**.
2. Haz clic en **Upload**.
3. Selecciona un archivo sencillo (ejemplo: `index.html` o una imagen).
4. Haz clic en **Upload** para completar la carga.

### 5.2 – Hacer el archivo público

1. En la pestaña **Objects**, selecciona el archivo que acabas de subir.
2. Haz clic en **Object actions** (menú desplegable en la parte superior).
3. Selecciona **Make public** (nota: si la opción no aparece, necesitarás ajustar los permisos del bucket desde la política de acceso).
4. Confirma la acción.

### 5.3 – Acceder al archivo desde el navegador

1. Selecciona el archivo nuevamente.
2. En la sección **Object overview**, copia la **Object URL** (URL del objeto).
3. Abre una nueva pestaña en tu navegador y pega la URL.
4. Si todo está correcto → deberías ver tu archivo público servido desde S3.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Creado su primer bucket S3 en una región específica.
- ✅ Activado el versionado en el bucket.
- ✅ Subido un archivo al bucket.
- ✅ Hecho el archivo público y accedido a él a través de una URL pública.
- ✅ Comprendido la diferencia entre buckets privados y públicos.
