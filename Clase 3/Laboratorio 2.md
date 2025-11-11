# Laboratorio 2: Desplegar N8N en EC2

## Paso 1 – Conectarse a la instancia pública por SSH

1. En el dashboard de EC2, selecciona la instancia `lab-ec2-public-01`.
2. Haz clic en **Connect**.
3. Ve a la pestaña **SSH client**.
4. Copia el comando sugerido y ejecútalo en tu terminal local.
5. Acepta la huella digital escribiendo `yes`.

> **✅ Resultado esperado:** Deberías estar conectado a la instancia pública.

---

## Paso 2 – Instalar Docker en la instancia

Una vez conectado por SSH, ejecuta los siguientes comandos:

```bash
# Actualizar el sistema
sudo yum update -y

# Instalar Docker
sudo yum install docker -y

# Iniciar el servicio Docker
sudo systemctl start docker

# Habilitar Docker para que inicie automáticamente
sudo systemctl enable docker

# Agregar el usuario ec2-user al grupo docker (para no usar sudo)
sudo usermod -aG docker ec2-user

# Salir y volver a conectar para aplicar los cambios de grupo
exit
```

Después de ejecutar `exit`, reconéctate por SSH a la instancia.

> **✅ Resultado esperado:** Docker está instalado y funcionando en la instancia.

---

## Paso 3 – Crear volumen de datos para N8N

Una vez reconectado, ejecuta:

```bash
docker volume create n8n_data
```

> **👉 Explicación:** Este volumen persistente almacenará los datos de N8N (flujos, credenciales, etc.) incluso si el contenedor se reinicia.

---

## Paso 4 – Obtener la IP pública de la instancia

Ejecuta el siguiente comando para obtener la IP pública:

```bash
curl ifconfig.me
```

Anota esta IP, la necesitarás en el siguiente paso.

---

## Paso 5 – Desplegar N8N con Docker

Ejecuta el siguiente comando, reemplazando `<IP_PUBLICA>` con la IP que obtuviste en el paso anterior:

```bash
docker run -it --rm \
--name n8n \
-p 5678:5678 \
-e GENERIC_TIMEZONE="Europe/Berlin" \
-e TZ="Europe/Berlin" \
-e N8N_HOST="<IP_PUBLICA>" \
-e N8N_PORT=5678 \
-e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
-e N8N_RUNNERS_ENABLED=true \
-e N8N_SECURE_COOKIE=false \
-v n8n_data:/home/node/.n8n \
docker.n8n.io/n8nio/n8n
```

**Ejemplo con IP real:**

```bash
docker run -it --rm \
--name n8n \
-p 5678:5678 \
-e GENERIC_TIMEZONE="Europe/Berlin" \
-e TZ="Europe/Berlin" \
-e N8N_HOST="54.123.45.67" \
-e N8N_PORT=5678 \
-e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
-e N8N_RUNNERS_ENABLED=true \
-e N8N_SECURE_COOKIE=false \
-v n8n_data:/home/node/.n8n \
docker.n8n.io/n8nio/n8n
```

> **👉 Explicación de las variables de entorno:**
> - `GENERIC_TIMEZONE` y `TZ`: Zona horaria de la aplicación.
> - `N8N_HOST`: IP pública de la instancia (necesaria para acceder desde el navegador).
> - `N8N_PORT`: Puerto en el que escucha N8N.
> - `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS`: Valida permisos de archivos de configuración.
> - `N8N_RUNNERS_ENABLED`: Habilita los ejecutores de N8N.
> - `N8N_SECURE_COOKIE`: Deshabilitado porque no usamos HTTPS (en producción, habilitarlo).
> - `-v n8n_data:/home/node/.n8n`: Monta el volumen persistente.

---

## Paso 6 – Intentar acceder a N8N desde el navegador (fallará)

1. Abre tu navegador web.
2. Ve a `http://<IP_PUBLICA>:5678` (reemplaza `<IP_PUBLICA>` con la IP de tu instancia).
3. Intenta acceder a N8N.

> **❌ Resultado esperado:** La conexión fallará con un timeout o error de conexión rechazada. Esto ocurre porque el Security Group no permite tráfico en el puerto 5678 desde internet.

> **👉 Explicación:** Aunque N8N está corriendo en la instancia, el Security Group actúa como un firewall que bloquea el acceso externo al puerto 5678.

---

## Paso 7 – Verificar que N8N está corriendo

Desde otra terminal (sin desconectarte de la instancia), ejecuta:

```bash
docker ps
```

Deberías ver el contenedor `n8n` en la lista.

---

## Paso 8 – Modificar Security Groups para permitir acceso a N8N

1. En la consola de AWS, busca `EC2` en la barra de búsqueda superior.
2. Ve al dashboard de EC2 y selecciona **Security Groups** en el panel izquierdo.
3. Selecciona el Security Group asociado a la instancia pública (`lab-ec2-public-01` o `lab-ec2-public-02`).
4. Ve a la pestaña **Inbound rules**.
5. Haz clic en **Edit inbound rules**.
6. Haz clic en **Add rule**:
   - **Type:** Custom TCP
   - **Protocol:** TCP
   - **Port range:** `5678` (puerto de N8N)
   - **Source:** `0.0.0.0/0` (acceso desde cualquier IP; en producción, restringir a IPs específicas)
7. Haz clic en **Save rules**.

> **👉 Resultado:** El Security Group ahora permite tráfico en el puerto 5678 desde internet.

---

## Paso 9 – Acceder a N8N desde el navegador (ahora funcionará)

1. Vuelve a tu navegador.
2. Recarga la página o ve a `http://<IP_PUBLICA>:5678`.
3. Deberías ver la interfaz de N8N.
4. Completa la configuración inicial (crear usuario, contraseña, etc.).

> **✅ Resultado esperado:** N8N está funcionando y accesible desde internet.

---

## Paso 10 – Detener N8N (opcional)

Para detener N8N, presiona `Ctrl+C` en la terminal donde está corriendo el contenedor.

> **👉 Nota:** Los datos se guardarán en el volumen `n8n_data`, así que cuando reinicies el contenedor, todos tus flujos y configuración se recuperarán automáticamente.

---

## Paso 11 – Reiniciar N8N en segundo plano (opcional)

Si quieres que N8N se ejecute en segundo plano, usa el flag `-d`:

```bash
docker run -d \
--name n8n \
-p 5678:5678 \
-e GENERIC_TIMEZONE="Europe/Berlin" \
-e TZ="Europe/Berlin" \
-e N8N_HOST="<IP_PUBLICA>" \
-e N8N_PORT=5678 \
-e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
-e N8N_RUNNERS_ENABLED=true \
-e N8N_SECURE_COOKIE=false \
-v n8n_data:/home/node/.n8n \
docker.n8n.io/n8nio/n8n
```

Para ver los logs:

```bash
docker logs -f n8n
```

Para detener el contenedor:

```bash
docker stop n8n
```

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Modificado el Security Group para permitir tráfico en el puerto 5678.
- ✅ Instalado Docker en la instancia EC2 pública.
- ✅ Creado un volumen persistente para N8N.
- ✅ Desplegado N8N en un contenedor Docker.
- ✅ Accedido a N8N desde el navegador usando la IP pública.
- ✅ Comprendido cómo funcionan los volúmenes persistentes en Docker.
- ✅ Aprendido a gestionar contenedores Docker (iniciar, detener, ver logs).
- ✅ Entendido la importancia de los Security Groups para controlar el acceso a servicios.
