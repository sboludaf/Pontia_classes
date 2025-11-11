# Laboratorio 1: Primeros Pasos en AWS

## Paso 1 – Acceder a la consola usando SSO

1. Abre tu navegador y dirígete a la URL de inicio de sesión que te haya dado la organización/laboratorio (ej. `https://<alias>.awsapps.com/start`).
2. Selecciona el método de acceso SSO (Single Sign-On).
3. Introduce tus credenciales (usuario/contraseña o MFA si está habilitado).
4. Una vez validado, se abrirá la AWS Management Console.

> **👉 Nota para los alumnos:** Si no usan SSO, pueden iniciar sesión directamente en https://console.aws.amazon.com con su usuario IAM o la cuenta root (no recomendable).

---

## Paso 2 – Primera navegación por la consola

Observa la barra superior y sus componentes principales:

- **Services:** Catálogo de servicios (más usados → EC2, S3, IAM).
- **Search:** Buscador rápido de servicios.
- **Cuenta:** Información de usuario, región activa, facturación.

### Actividades:

1. Cambia de región (ej. de N. Virginia a Europa (Madrid)). Verás cómo cambian los recursos disponibles.
2. Accede a la sección **Billing** (facturación) para ver cómo se muestran costes y el panel de uso (aunque no se generen todavía).

---

## Paso 3 – Principales servicios

Realiza un recorrido por los siguientes servicios:

- **IAM:** Comprueba que hay un usuario IAM creado y revisa políticas básicas.
- **S3:** Entra al servicio, visualiza que aún no hay buckets creados.
- **EC2:** Abre el panel y observa el dashboard: número de instancias, volúmenes, VPCs.
- **VPC:** Localiza la VPC por defecto que AWS crea automáticamente.
- **CloudWatch:** Revisa la consola de métricas, aunque aún no haya recursos desplegados.

---

## Objetivos de aprendizaje

Al final del recorrido, cada alumno debe saber:

- ✅ Cómo cambiar de región.
- ✅ Cómo buscar un servicio en segundos.
- ✅ Dónde ver los costes básicos.
- ✅ Qué servicios aparecen ya preconfigurados en una cuenta (ej. VPC default).
