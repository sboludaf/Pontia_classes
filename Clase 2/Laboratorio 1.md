# Laboratorio 1: Usuarios, grupos y políticas

## Paso 1 – Acceso y navegación por el servicio de IAM

1. En la consola de AWS, busca `IAM` en la barra de búsqueda superior.
2. Accede al **dashboard de IAM**.
3. Observa los elementos principales en el panel izquierdo:
   - **Users** (Usuarios).
   - **Groups** (Grupos).
   - **Roles** (Roles).
   - **Policies** (Políticas).

> **👉 Importante:** IAM es un servicio **global**, no está asociado a ninguna región específica.

---

## Paso 2 – Crear un grupo "Developers" con permisos limitados

1. En el dashboard de IAM, ve a **User groups** en el panel izquierdo.
2. Haz clic en **Create group**.
3. En el formulario:
   - **Group name:** `Developers`
4. En la sección **Attach permissions policies**:
   - Busca y selecciona la política **AmazonS3ReadOnlyAccess** (acceso de solo lectura a S3).
   - Esta política permitirá al grupo listar y leer buckets de S3, pero no crear ni eliminar.
5. Haz clic en **Create group**.

> **👉 Resultado:** El grupo "Developers" ha sido creado con permisos limitados solo a S3.

---

## Paso 3 – Crear usuario IAM con acceso a consola

1. En el dashboard de IAM, ve a **Users** en el panel izquierdo.
2. Haz clic en **Create user**.
3. En el formulario:
   - **User name:** `developer-user-01` (ejemplo)
4. Haz clic en **Next**.
5. En la sección **Set permissions**:
   - Selecciona **Add user to group**.
   - Busca y selecciona el grupo `Developers`.
6. Haz clic en **Next** → **Create user**.

### 3.1 – Configurar contraseña para acceso a consola

1. En la lista de usuarios, selecciona el usuario que acabas de crear (`developer-user-01`).
2. Ve a la pestaña **Security credentials**.
3. En la sección **Console password**, haz clic en **Set password**.
4. Selecciona **Generate a password** (AWS genera una contraseña segura).
5. **Marca la opción** "Users must create a new password on next sign-in" (forzar cambio en primer login).
6. Haz clic en **Set password**.
7. Copia la contraseña temporal y guárdala de forma segura.

> **👉 Resultado:** El usuario tiene acceso a la consola y deberá cambiar su contraseña en el primer login.

---

## Paso 4 – Crear usuario IAM con acceso programático (Access Key)

1. En el dashboard de IAM, ve a **Users** en el panel izquierdo.
2. Haz clic en **Create user**.
3. En el formulario:
   - **User name:** `developer-api-01` (ejemplo)
4. Haz clic en **Next**.
5. En la sección **Set permissions**:
   - Selecciona **Add user to group**.
   - Busca y selecciona el grupo `Developers`.
6. Haz clic en **Next** → **Create user**.

### 4.1 – Generar Access Key

1. En la lista de usuarios, selecciona el usuario que acabas de crear (`developer-api-01`).
2. Ve a la pestaña **Security credentials**.
3. En la sección **Access keys**, haz clic en **Create access key**.
4. Selecciona **Application running outside AWS** (para uso programático).
5. Haz clic en **Next**.
6. (Opcional) Añade una descripción (ej. "API access for development").
7. Haz clic en **Create access key**.
8. **Descarga el archivo CSV** con las credenciales (Access Key ID y Secret Access Key).

> **⚠️ Importante:** Guarda estas credenciales de forma segura. No podrás volver a ver la Secret Access Key después de cerrar esta pantalla.

---

## Paso 5 – Probar login con el nuevo usuario en consola

1. Abre una **nueva ventana de navegador en modo incógnito** (para evitar conflictos de sesión).
2. Ve a https://console.aws.amazon.com.
3. Selecciona **IAM user** como tipo de login.
4. Introduce:
   - **Account ID o alias:** El ID de tu cuenta AWS (puedes encontrarlo en el dashboard de IAM).
   - **User name:** `developer-user-01`
   - **Password:** La contraseña temporal que copiaste.
5. En el primer login, te pedirá que cambies la contraseña. Introduce una nueva contraseña segura.
6. Una vez dentro, intenta acceder a diferentes servicios:
   - **S3:** Deberías poder listar buckets (permiso concedido).
   - **EC2:** No deberías poder acceder (permiso denegado).
   - **IAM:** No deberías poder acceder (permiso denegado).

> **👉 Resultado:** Verificas que las restricciones de permisos funcionan correctamente.

---

## Paso 6 – Adjuntar política personalizada JSON al grupo

1. En el dashboard de IAM, ve a **User groups**.
2. Selecciona el grupo `Developers`.
3. Ve a la pestaña **Permissions**.
4. Haz clic en **Add permissions** → **Create inline policy**.
5. Selecciona **JSON** como editor.
6. Reemplaza el contenido con la siguiente política:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "*"
    }
  ]
}
```

7. Haz clic en **Review policy**.
8. En el campo **Policy name**, introduce: `S3ListBucketPolicy`
9. Haz clic en **Create policy**.

> **👉 Resultado:** La política personalizada ha sido adjuntada al grupo "Developers". Ahora los usuarios del grupo solo pueden listar buckets de S3, pero no pueden crear, eliminar ni modificar objetos.

---

## Paso 7 – Probar restricciones con el usuario programático

1. En tu máquina local, abre una terminal.
2. Configura las credenciales de AWS usando el AWS CLI:

```bash
aws configure
```

3. Introduce:
   - **AWS Access Key ID:** El Access Key ID del usuario `developer-api-01`.
   - **AWS Secret Access Key:** El Secret Access Key del usuario `developer-api-01`.
   - **Default region:** `eu-west-1` (o la región que prefieras).
   - **Default output format:** `json`

4. Prueba el acceso a S3:

```bash
# Listar buckets (debería funcionar)
aws s3 ls

# Intentar crear un bucket (debería fallar)
aws s3 mb s3://test-bucket-name
```

> **👉 Resultado:** Verificas que el usuario programático solo puede ejecutar acciones permitidas por la política.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Accedido al servicio IAM y comprendido su estructura.
- ✅ Creado un grupo "Developers" con permisos limitados a S3.
- ✅ Creado un usuario IAM con acceso a consola y contraseña temporal.
- ✅ Creado un usuario IAM con acceso programático (Access Key).
- ✅ Probado el login con el nuevo usuario y verificado las restricciones.
- ✅ Adjuntado una política personalizada JSON al grupo.
- ✅ Comprendido la diferencia entre acceso a consola y acceso programático.
- ✅ Verificado que las políticas de permisos se aplican correctamente.
