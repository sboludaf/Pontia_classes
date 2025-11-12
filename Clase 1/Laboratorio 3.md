# Laboratorio 3: Introducción a Amazon EC2

## Paso 1 – Ir al servicio EC2

1. En la consola de AWS, busca `EC2` en la barra de búsqueda superior.
2. Accede al **dashboard de EC2**.
3. Observa los elementos principales:
   - **Número de instancias en ejecución** (Running instances).
   - **Security Groups** (grupos de seguridad).
   - **VPC por defecto** (red virtual preconfigurada).

---

## Paso 2 – Desplegar instancia

1. En el dashboard de EC2, haz clic en el botón **Launch Instance**.
2. Completa la configuración recomendada:

   | Campo | Valor |
   |-------|-------|
   | **Name** | `lab-ec2-01` |
   | **AMI** | Amazon Linux 2 |
   | **Instance Type** | `t2.micro` (capa gratuita) |
   | **Key Pair** | Crear o usar un par de claves existente para conexión SSH |

3. En **Network settings**:
   - Asegúrate de que la VPC por defecto esté seleccionada.
   - Configura el **Security Group** para permitir:
     - **SSH (puerto 22)** desde `My IP` (tu dirección IP).
     - **HTTP (puerto 80)** desde `My IP` (opcional, para acceso web).

4. Haz clic en **Launch Instance**.
5. Verifica en el dashboard que la instancia aparece con estado **running** (puede tardar unos segundos).

---

## Paso 3 – Conectarse por SSH

1. En el dashboard de EC2, selecciona tu instancia (`lab-ec2-01`).
2. Haz clic en el botón **Connect** (en la parte superior derecha).
3. Ve a la pestaña **SSH client**.
4. Copia el comando sugerido (ejemplo: `ssh -i "mi-clave.pem" ec2-user@ec2-xx-xx-xx-xx.compute-1.amazonaws.com`).
5. Abre una terminal en tu máquina local y pega el comando.
6. La primera vez, acepta la huella digital del servidor escribiendo `yes`.

> **👉 Resultado:** Ya estás dentro de la máquina virtual. Puedes ejecutar comandos como si fuera un servidor remoto.

---

## Paso 4 – Probar comandos básicos

Una vez conectado por SSH, ejecuta los siguientes comandos en la terminal de la instancia:

```bash
# Información del sistema operativo
uname -a

# Tiempo de actividad de la instancia
uptime

# Uso de memoria (en MB)
free -m

# Uso de disco
df -h

# Ver IP pública desde dentro de la instancia
curl ifconfig.me
```

Estos comandos te permitirán verificar que la instancia está funcionando correctamente y obtener información básica del sistema.

---

## Paso 5 – Hacer instantánea (snapshot) de la instancia

1. En el dashboard de EC2, selecciona tu instancia (`lab-ec2-01`).
2. Ve a la pestaña **Storage**.
3. Selecciona el volumen **EBS** (Elastic Block Store) asociado a la instancia.
4. Haz clic en **Create Snapshot**.
5. En el formulario:
   - **Snapshot name:** `lab-ec2-snapshot01`
   - **Description:** (opcional) Descripción breve del snapshot.
6. Haz clic en **Create Snapshot**.

> **👉 Resultado:** Se crea una copia de seguridad del disco. Podrás usar este snapshot para restaurar la instancia o crear nuevas instancias con la misma configuración.

---

## Paso 6 – Diferencias entre STOP y TERMINATE

### STOP (Detener)

- La instancia se **apaga**.
- El volumen **EBS persiste** (no se elimina).
- Puedes **reiniciar la misma instancia** más tarde.
- **Seguirás pagando** por el almacenamiento EBS, pero no por la instancia en ejecución.

### TERMINATE (Terminar)

- La instancia se **destruye definitivamente**.
- El volumen **EBS asociado se elimina** (a menos que se configure lo contrario).
- **No puedes volver a encenderla**.
- Dejarás de pagar por la instancia y el almacenamiento.

### Demo: Detener y reiniciar

1. En el dashboard de EC2, selecciona tu instancia.
2. Haz clic en **Instance State** → **Stop**.
3. Espera a que el estado cambie a **stopped**.
4. Haz clic en **Instance State** → **Start**.
5. Observa que la **IP pública ha cambiado** (la IP privada permanece igual).

> **👉 Importante:** Cada vez que detienes y reiniciar una instancia, AWS asigna una nueva IP pública. Si necesitas una IP fija, deberás usar **Elastic IP**.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Accedido al dashboard de EC2 y comprendido sus elementos principales.
- ✅ Desplegado una instancia EC2 con configuración básica.
- ✅ Conectado a la instancia por SSH desde su máquina local.
- ✅ Ejecutado comandos básicos en la instancia para verificar su funcionamiento.
- ✅ Creado un snapshot (copia de seguridad) del volumen EBS.
- ✅ Comprendido las diferencias entre STOP y TERMINATE.
