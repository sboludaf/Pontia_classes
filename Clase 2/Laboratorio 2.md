# Laboratorio 2: Roles y buenas prácticas

## Paso 1 – Crear rol IAM para EC2

1. En la consola de AWS, busca `IAM` en la barra de búsqueda superior.
2. Ve a **Roles** en el panel izquierdo.
3. Haz clic en **Create role**.
4. En la sección **Select trusted entity**:
   - Selecciona **AWS service**.
   - En el campo de búsqueda, busca y selecciona **EC2**.
   - Haz clic en **Next**.
5. En la sección **Add permissions**:
   - Haz clic en **Next** (sin seleccionar políticas por ahora, las añadiremos después).
6. En la sección **Name, review, and create**:
   - **Role name:** `EC2-S3-ReadOnly` (ejemplo)
   - **Description:** (opcional) "Rol para EC2 con acceso de lectura a S3"
7. Haz clic en **Create role**.

> **👉 Resultado:** El rol IAM ha sido creado y está listo para ser asignado a instancias EC2.

---

## Paso 1.1 – Adjuntar política personalizada al rol

1. En la lista de roles, selecciona el rol que acabas de crear (`EC2-S3-ReadOnly`).
2. Ve a la pestaña **Permissions**.
3. Haz clic en **Add permissions** → **Create inline policy**.
4. Selecciona **JSON** como editor.
5. Reemplaza el contenido con la siguiente política personalizada (reemplaza `lab-s3-primerapellido2025` con el nombre de tu bucket):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::BUCKET_USUARIO",
        "arn:aws:s3:::BUCKET_USUARIO/*"
      ]
    }
  ]
}
```

> **👉 Explicación de la política:**
> - `s3:ListBucket`: Permite listar los objetos dentro del bucket específico.
> - `s3:GetObject`: Permite descargar/leer objetos del bucket.
> - `Resource`: Especifica que solo se puede acceder al bucket del alumno (no a otros buckets).

6. Haz clic en **Review policy**.
7. En el campo **Policy name**, introduce: `S3BucketAccess`
8. Haz clic en **Create policy**.

> **👉 Resultado:** El rol ahora tiene una política personalizada que permite acceso de lectura solo al bucket específico del alumno.

---

## Paso 2 – Lanzar una instancia EC2 con ese rol

1. En la consola de AWS, busca `EC2` en la barra de búsqueda superior.
2. Ve al dashboard de EC2 y haz clic en **Launch Instance**.
3. Completa la configuración básica:
   - **Name:** `lab-ec2-with-role`
   - **AMI:** Amazon Linux 2
   - **Instance Type:** `t2.micro` (capa gratuita)
   - **Key Pair:** Usa el par de claves existente o crea uno nuevo
4. En **Advanced details** (desplázate hacia abajo):
   - Busca la sección **IAM instance profile**.
   - Selecciona el rol que creaste: `EC2-S3-ReadOnly`.
5. En **Network settings**:
   - Asegúrate de que la VPC por defecto esté seleccionada.
   - Configura el **Security Group** para permitir **SSH (puerto 22)** desde `My IP`.
6. Haz clic en **Launch Instance**.
7. Verifica en el dashboard que la instancia aparece con estado **running**.

> **👉 Resultado:** La instancia EC2 ahora tiene asignado el rol IAM con permisos de lectura en S3.

---

## Paso 3 – Conectarse por SSH y validar acceso a S3

### 3.1 – Conectarse por SSH

1. En el dashboard de EC2, selecciona tu instancia (`lab-ec2-with-role`).
2. Haz clic en el botón **Connect**.
3. Ve a la pestaña **SSH client**.
4. Copia el comando sugerido y ejecútalo en tu terminal local.
5. Acepta la huella digital escribiendo `yes`.

### 3.2 – Ejecutar comando AWS CLI

Una vez conectado por SSH a la instancia, ejecuta:

```bash
aws s3 ls
```

Este comando listará todos los buckets S3 de tu cuenta.

> **👉 Importante:** Observa que **no necesitas introducir credenciales** (Access Key ID ni Secret Access Key). El rol IAM asignado a la instancia proporciona automáticamente las credenciales temporales necesarias.

### 3.3 – Validar restricciones

Intenta ejecutar un comando que requiera permisos de escritura:

```bash
# Intentar crear un bucket (debería fallar)
aws s3 mb s3://test-bucket-name
```

Deberías recibir un error indicando que no tienes permisos para realizar esta acción.

> **👉 Resultado:** Verificas que el rol solo permite lectura en S3, no escritura.

---

## Paso 4 – Diferencias entre Rol e Usuario IAM

### Usuario IAM

- **Identidad permanente** con credenciales de larga duración.
- Requiere **Access Key ID** y **Secret Access Key** para acceso programático.
- Ideal para personas que necesitan acceso a la consola o a herramientas externas.
- Las credenciales deben ser **rotadas periódicamente** (cada 90 días recomendado).
- Si las credenciales se comprometer, pueden ser usadas indefinidamente.

### Rol IAM

- **Identidad temporal** con credenciales de corta duración (por defecto 1 hora).
- Genera **credenciales temporales** automáticamente (Access Key ID, Secret Access Key, Session Token).
- Ideal para servicios de AWS (EC2, Lambda, etc.) que necesitan permisos.
- Las credenciales **se renuevan automáticamente**.
- Si se comprometen, solo son válidas durante el período de sesión.
- **No requiere gestión manual de credenciales**.

### Comparación visual

| Aspecto | Usuario IAM | Rol IAM |
|--------|-----------|---------|
| **Duración** | Permanente | Temporal (1 hora por defecto) |
| **Credenciales** | Estáticas | Dinámicas (se renuevan) |
| **Rotación** | Manual | Automática |
| **Caso de uso** | Personas, aplicaciones externas | Servicios AWS |
| **Seguridad** | Menor (credenciales estáticas) | Mayor (credenciales temporales) |

---

## Buenas prácticas en IAM

### 1. Un usuario por persona, nunca compartir credenciales

- Cada miembro del equipo debe tener su propio usuario IAM.
- Nunca compartas credenciales (Access Keys, contraseñas).
- Esto permite auditar quién realizó cada acción en AWS.

```
❌ Incorrecto: Compartir un usuario "admin" entre varios desarrolladores.
✅ Correcto: Crear usuarios individuales (developer-alice, developer-bob, etc.).
```

### 2. Usar roles en lugar de Access Keys cuando sea posible

- Prefiere roles IAM para servicios AWS (EC2, Lambda, ECS, etc.).
- Los roles proporcionan credenciales temporales automáticamente.
- Evita hardcodear Access Keys en aplicaciones o instancias.

```
❌ Incorrecto: Guardar Access Keys en variables de entorno o archivos de configuración.
✅ Correcto: Asignar un rol IAM a la instancia EC2 o función Lambda.
```

### 3. Rotar claves periódicamente

- Cambia las contraseñas de usuarios IAM cada 90 días.
- Rota las Access Keys cada 90 días.
- Desactiva y elimina claves antiguas después de la rotación.

```
Proceso de rotación de Access Keys:
1. Crear una nueva Access Key.
2. Actualizar aplicaciones con la nueva clave.
3. Desactivar la clave antigua (no eliminar inmediatamente).
4. Después de verificar que todo funciona, eliminar la clave antigua.
```

### 4. Aplicar el principio de menor privilegio (Least Privilege)

- Asigna solo los permisos **mínimos necesarios** para realizar el trabajo.
- Evita usar políticas como `AdministratorAccess` para usuarios normales.
- Revisa y audita periódicamente los permisos asignados.

### 5. Usar MFA (Multi-Factor Authentication)

- Habilita MFA para todos los usuarios IAM, especialmente los con acceso administrativo.
- Usa aplicaciones como Google Authenticator, Authy o hardware keys.

### 6. Monitorear y auditar acceso

- Usa **CloudTrail** para registrar todas las acciones en AWS.
- Revisa regularmente los logs de acceso.
- Configura alertas para actividades sospechosas.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Creado un rol IAM con permisos específicos.
- ✅ Asignado el rol a una instancia EC2.
- ✅ Accedido a S3 desde la instancia sin credenciales hardcodeadas.
- ✅ Comprendido las diferencias entre roles e usuarios IAM.
- ✅ Aprendido las buenas prácticas de seguridad en IAM.
- ✅ Entendido por qué los roles son más seguros que Access Keys para servicios AWS.
