# Laboratorio 1: VPC Básica

## Paso 1 – Crear una VPC

1. En la consola de AWS, busca `VPC` en la barra de búsqueda superior.
2. Ve al dashboard de VPC.
3. En el panel izquierdo, selecciona **Your VPCs**.
4. Haz clic en **Create VPC**.
5. En el formulario:
   - **Name tag:** `lab-vpc-01` (ejemplo)
   - **IPv4 CIDR block:** `10.0.0.0/16` (rango de direcciones IP para la VPC)
   - **IPv6 CIDR block:** Dejar vacío (opcional)
   - **Tenancy:** Default
6. Haz clic en **Create VPC**.

> **👉 Explicación:** Una VPC es una red virtual privada donde alojarás tus recursos. El bloque CIDR `10.0.0.0/16` proporciona 65,536 direcciones IP disponibles.

---

## Paso 2 – Crear primera subred pública

1. En el panel izquierdo del dashboard de VPC, selecciona **Subnets**.
2. Haz clic en **Create subnet**.
3. En el formulario:
   - **VPC ID:** Selecciona la VPC que creaste (`lab-vpc-01`).
   - **Subnet name:** `lab-subnet-public-01`
   - **Availability Zone:** Selecciona la primera disponible (ej. `eu-west-1a`).
   - **IPv4 CIDR block:** `10.0.0.0/24` (subred dentro del rango de la VPC)
4. Haz clic en **Create subnet**.

> **👉 Explicación:** Una subred pública es aquella que tiene acceso directo a internet a través de un Internet Gateway. El bloque CIDR `10.0.0.0/24` proporciona 256 direcciones IP.

---

## Paso 2.1 – Crear segunda subred pública

1. En el panel izquierdo del dashboard de VPC, selecciona **Subnets**.
2. Haz clic en **Create subnet**.
3. En el formulario:
   - **VPC ID:** Selecciona la VPC que creaste (`lab-vpc-01`).
   - **Subnet name:** `lab-subnet-public-02`
   - **Availability Zone:** Selecciona una diferente (ej. `eu-west-1b`).
   - **IPv4 CIDR block:** `10.0.1.0/24` (subred dentro del rango de la VPC)
4. Haz clic en **Create subnet**.

> **👉 Explicación:** Crear subnets en diferentes Availability Zones proporciona alta disponibilidad. Si una zona falla, tus recursos en la otra zona seguirán funcionando.

---

## Paso 3 – Crear primera subred privada

1. En el panel izquierdo del dashboard de VPC, selecciona **Subnets**.
2. Haz clic en **Create subnet**.
3. En el formulario:
   - **VPC ID:** Selecciona la VPC que creaste (`lab-vpc-01`).
   - **Subnet name:** `lab-subnet-private-01`
   - **Availability Zone:** Selecciona la primera disponible (ej. `eu-west-1a`).
   - **IPv4 CIDR block:** `10.0.2.0/24` (subred dentro del rango de la VPC)
4. Haz clic en **Create subnet**.

> **👉 Explicación:** Una subred privada no tiene acceso directo a internet. Los recursos en esta subred solo pueden comunicarse con otros recursos dentro de la VPC o a través de un NAT Gateway.

---

## Paso 3.1 – Crear segunda subred privada

1. En el panel izquierdo del dashboard de VPC, selecciona **Subnets**.
2. Haz clic en **Create subnet**.
3. En el formulario:
   - **VPC ID:** Selecciona la VPC que creaste (`lab-vpc-01`).
   - **Subnet name:** `lab-subnet-private-02`
   - **Availability Zone:** Selecciona una diferente (ej. `eu-west-1b`).
   - **IPv4 CIDR block:** `10.0.3.0/24` (subred dentro del rango de la VPC)
4. Haz clic en **Create subnet**.

> **👉 Resultado:** Ahora tienes dos subnets públicas y dos subnets privadas distribuidas en diferentes Availability Zones para alta disponibilidad.

---

## Paso 4 – Crear Internet Gateway

1. En el panel izquierdo del dashboard de VPC, selecciona **Internet Gateways**.
2. Haz clic en **Create internet gateway**.
3. En el formulario:
   - **Name tag:** `lab-igw-01`
4. Haz clic en **Create internet gateway**.
5. Una vez creado, verás un botón **Attach to VPC**. Haz clic en él.
6. Selecciona la VPC que creaste (`lab-vpc-01`).
7. Haz clic en **Attach internet gateway**.

> **👉 Resultado:** El Internet Gateway está ahora asociado a tu VPC y permite que los recursos en subredes públicas accedan a internet.

---

## Paso 5 – Asociar Route Tables

### 5.1 – Configurar ruta pública

1. En el panel izquierdo del dashboard de VPC, selecciona **Route Tables**.
2. Busca la Route Table asociada a tu VPC (`lab-vpc-01`). Debería haber una creada automáticamente.
3. Selecciona la Route Table y ve a la pestaña **Routes**.
4. Haz clic en **Edit routes**.
5. Haz clic en **Add route**:
   - **Destination:** `0.0.0.0/0` (cualquier tráfico)
   - **Target:** Selecciona el Internet Gateway que creaste (`lab-igw-01`)
6. Haz clic en **Save routes**.

### 5.2 – Asociar Route Table a primera subred pública

1. En el panel izquierdo, selecciona **Subnets**.
2. Selecciona la subred pública (`lab-subnet-public-01`).
3. Ve a la pestaña **Route table association**.
4. Haz clic en **Edit route table association**.
5. Selecciona la Route Table que acabas de configurar.
6. Haz clic en **Save**.

### 5.3 – Asociar Route Table a segunda subred pública

1. En el panel izquierdo, selecciona **Subnets**.
2. Selecciona la subred pública (`lab-subnet-public-02`).
3. Ve a la pestaña **Route table association**.
4. Haz clic en **Edit route table association**.
5. Selecciona la misma Route Table.
6. Haz clic en **Save**.

> **👉 Resultado:** Ambas subnets públicas ahora tienen una ruta a internet a través del Internet Gateway.

---

## Paso 6 – Desplegar EC2 en ambas subnets

### 6.1 – Desplegar primera instancia en subred pública

1. En la consola de AWS, busca `EC2` en la barra de búsqueda superior.
2. Ve al dashboard de EC2 y haz clic en **Launch Instance**.
3. Completa la configuración:
   - **Name:** `lab-ec2-public-01`
   - **AMI:** Amazon Linux 2
   - **Instance Type:** `t2.micro`
   - **Key Pair:** Usa o crea un par de claves
4. En **Network settings**:
   - **VPC:** Selecciona `lab-vpc-01`
   - **Subnet:** Selecciona `lab-subnet-public-01`
   - **Auto-assign Public IP:** Habilita esta opción
   - **Security Group:** Crea uno nuevo o usa uno existente que permita SSH (puerto 22)
5. Haz clic en **Launch Instance**.

### 6.2 – Desplegar segunda instancia en subred pública

1. Haz clic en **Launch Instance** nuevamente.
2. Completa la configuración:
   - **Name:** `lab-ec2-public-02`
   - **AMI:** Amazon Linux 2
   - **Instance Type:** `t2.micro`
   - **Key Pair:** Usa el mismo par de claves
3. En **Network settings**:
   - **VPC:** Selecciona `lab-vpc-01`
   - **Subnet:** Selecciona `lab-subnet-public-02`
   - **Auto-assign Public IP:** Habilita esta opción
   - **Security Group:** Usa el mismo Security Group que la instancia anterior
4. Haz clic en **Launch Instance**.

### 6.3 – Desplegar primera instancia en subred privada

1. Haz clic en **Launch Instance** nuevamente.
2. Completa la configuración:
   - **Name:** `lab-ec2-private-01`
   - **AMI:** Amazon Linux 2
   - **Instance Type:** `t2.micro`
   - **Key Pair:** Usa el mismo par de claves
3. En **Network settings**:
   - **VPC:** Selecciona `lab-vpc-01`
   - **Subnet:** Selecciona `lab-subnet-private-01`
   - **Auto-assign Public IP:** Déjalo deshabilitado (las instancias privadas no necesitan IP pública)
   - **Security Group:** Crea uno nuevo que permita SSH desde la subred pública (ej. desde `10.0.0.0/24` y `10.0.1.0/24`)
4. Haz clic en **Launch Instance**.

### 6.4 – Desplegar segunda instancia en subred privada

1. Haz clic en **Launch Instance** nuevamente.
2. Completa la configuración:
   - **Name:** `lab-ec2-private-02`
   - **AMI:** Amazon Linux 2
   - **Instance Type:** `t2.micro`
   - **Key Pair:** Usa el mismo par de claves
3. En **Network settings**:
   - **VPC:** Selecciona `lab-vpc-01`
   - **Subnet:** Selecciona `lab-subnet-private-02`
   - **Auto-assign Public IP:** Déjalo deshabilitado
   - **Security Group:** Usa el mismo Security Group que la instancia privada anterior
4. Haz clic en **Launch Instance**.

> **👉 Resultado:** Tienes cuatro instancias EC2 distribuidas en dos subnets públicas (accesibles desde internet) y dos subnets privadas (solo accesibles desde dentro de la VPC).

---

## Paso 7 – Comprobar accesos SSH

### 7.1 – Conectarse a una instancia pública

1. En el dashboard de EC2, selecciona la instancia `lab-ec2-public-01`.
2. Haz clic en **Connect**.
3. Ve a la pestaña **SSH client**.
4. Copia el comando sugerido y ejecútalo en tu terminal local.
5. Acepta la huella digital escribiendo `yes`.

> **✅ Resultado esperado:** Deberías conectarte exitosamente a la instancia pública.

### 7.2 – Conectarse a una instancia privada desde la instancia pública

1. Una vez conectado a la instancia pública, ejecuta:

```bash
# Copiar la clave privada a la instancia pública
# (desde tu máquina local, en otra terminal)
scp -i "tu-clave.pem" tu-clave.pem ec2-user@<IP-PUBLICA>:/home/ec2-user/

# Luego, desde la instancia pública:
ssh -i /home/ec2-user/tu-clave.pem ec2-user@10.0.2.X
```

Reemplaza `10.0.2.X` con la IP privada de la instancia privada `lab-ec2-private-01` (puedes verla en el dashboard de EC2).

> **✅ Resultado esperado:** Deberías conectarte a la instancia privada a través de la instancia pública (conexión en cascada).

### 7.3 – Verificar conectividad entre subnets

Desde la instancia privada, ejecuta:

```bash
# Verificar que puedes hacer ping a la instancia pública
ping 10.0.0.X

# Ver la tabla de rutas
route -n

# Verificar conectividad con otra instancia privada
ping 10.0.3.X
```

Reemplaza `10.0.0.X` con la IP privada de una instancia pública y `10.0.3.X` con la IP privada de `lab-ec2-private-02`.

> **👉 Resultado:** Verificas que la comunicación entre subnets funciona correctamente en ambas zonas de disponibilidad.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Creado una VPC con un bloque CIDR específico.
- ✅ Creado dos subnets públicas en diferentes Availability Zones.
- ✅ Creado dos subnets privadas en diferentes Availability Zones.
- ✅ Creado un Internet Gateway y lo asoció a la VPC.
- ✅ Configurado Route Tables para permitir tráfico a internet desde ambas subnets públicas.
- ✅ Desplegado cuatro instancias EC2 (dos públicas y dos privadas) distribuidas en diferentes zonas.
- ✅ Verificado la conectividad SSH entre instancias públicas y privadas.
- ✅ Comprendido la diferencia entre subnets públicas y privadas.
- ✅ Aprendido cómo acceder a instancias privadas a través de instancias públicas (bastion host).
- ✅ Entendido la importancia de la alta disponibilidad mediante múltiples Availability Zones.
