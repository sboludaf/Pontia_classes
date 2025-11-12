# Laboratorio 1: Lambda y DynamoDB

## Paso 1 – Ir a DynamoDB

1. En la consola de AWS, busca `DynamoDB` en la barra de búsqueda superior.
2. Ve al dashboard de DynamoDB.
3. En el panel izquierdo, selecciona **Tables**.

> **👉 Explicación:** DynamoDB es una base de datos NoSQL completamente administrada por AWS. Es ideal para aplicaciones que requieren acceso rápido a datos con baja latencia.

---

## Paso 2 – Crear una tabla sencilla

1. En el dashboard de DynamoDB, haz clic en **Create table**.
2. En el formulario:
   - **Table name:** `NOMBREALUMNO-notes` (reemplaza `NOMBREALUMNO` con tu nombre o apellido)
   - **Partition key:** `id` (tipo String)
   - **Sort key:** (dejar vacío)
3. En **Billing settings**:
   - Selecciona **On-demand** (pago por uso, ideal para laboratorios)
4. Haz clic en **Create table**.
5. Espera a que el estado cambie a **Active** (puede tardar unos segundos).

> **👉 Resultado:** La tabla DynamoDB ha sido creada con `id` como clave primaria.

---

## Paso 3 – Crear una Policy que permita escribir en DynamoDB

1. En la consola de AWS, busca `IAM` en la barra de búsqueda superior.
2. Ve a **Policies** en el panel izquierdo.
3. Haz clic en **Create policy**.
4. Selecciona **JSON** como editor.
5. Reemplaza el contenido con la siguiente política (reemplaza `NOMBREALUMNO-notes` con el nombre de tu tabla):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/NOMBREALUMNO-notes"
    }
  ]
}
```

> **👉 Explicación de las acciones:**
> - `PutItem`: Insertar un nuevo elemento.
> - `GetItem`: Obtener un elemento por clave.
> - `UpdateItem`: Actualizar un elemento existente.
> - `DeleteItem`: Eliminar un elemento.
> - `Scan`: Leer todos los elementos (usado por la Lambda Reader).
> - `Query`: Consultar elementos por clave de partición.

6. Haz clic en **Next**.
7. En **Policy name**, introduce: `NOMBREALUMNO-DynamoDBPolicy`
8. Haz clic en **Create policy**.

> **👉 Resultado:** La política ha sido creada y está lista para ser asignada a un rol.

---

## Paso 4 – Crear el Role de la Lambda

1. En el dashboard de IAM, ve a **Roles** en el panel izquierdo.
2. Haz clic en **Create role**.
3. En **Select trusted entity**:
   - Selecciona **AWS service**.
   - Busca y selecciona **Lambda**.
   - Haz clic en **Next**.
4. En **Add permissions**:
   - Busca la política que creaste: `NOMBREALUMNO-DynamoDBPolicy`.
   - Selecciónala.
   - Haz clic en **Next**.
5. En **Name, review, and create**:
   - **Role name:** `NOMBREALUMNO-LambdaRole`
6. Haz clic en **Create role**.

> **👉 Resultado:** El rol de Lambda ha sido creado con permisos para acceder a DynamoDB.

---

## Paso 5 – Crear Lambda Writer

### 5.1 – Crear la función Lambda

1. En la consola de AWS, busca `Lambda` en la barra de búsqueda superior.
2. Ve al dashboard de Lambda.
3. Haz clic en **Create function**.
4. En el formulario:
   - **Function name:** `NOMBREALUMNO-Write`
   - **Runtime:** Python 3.12
   - **Execution role:** Selecciona **Use an existing role** → `NOMBREALUMNO-LambdaRole`
5. Haz clic en **Create function**.

### 5.2 – Añadir el código

1. En el editor de código, reemplaza el contenido con:

```python
import os, json, uuid, boto3, time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # event esperado: {"name":"Alice","note":"hola"}
    item_id = event.get("id") or str(uuid.uuid4())
    now = int(time.time())
    item = {
        "id": item_id,
        "name": event.get("name", "anon"),
        "note": event.get("note", ""),
        "created_at": now
    }
    table.put_item(Item=item)
    return {"status":"ok","id": item_id}
```

2. Haz clic en **Deploy**.

### 5.3 – Configurar variable de entorno

1. Ve a la pestaña **Configuration** → **Environment variables**.
2. Haz clic en **Edit**.
3. Haz clic en **Add environment variable**:
   - **Key:** `TABLE_NAME`
   - **Value:** `NOMBREALUMNO-notes` (nombre de tu tabla DynamoDB)
4. Haz clic en **Save**.

> **👉 Resultado:** La Lambda Writer está lista para escribir notas en DynamoDB.

### 5.4 – Crear Function URL

1. Ve a la pestaña **Configuration** → **Function URL**.
2. Haz clic en **Create function URL**.
3. En el formulario:
   - **Auth type:** `NONE` (sin autenticación, para laboratorio)
   - **Cors:** Habilita CORS
4. En **CORS configuration**:
   - **Allowed origins:** `*`
   - **Allowed methods:** `*`
   - **Allowed headers:** `Content-Type`
   - **Max age:** `86400`
5. Haz clic en **Save**.
6. Copia la **Function URL** y guárdala (la necesitarás para probar).

> **👉 Resultado:** La Lambda Writer tiene una URL pública con CORS habilitado.

---

## Paso 6 – Crear Lambda Reader

### 6.1 – Crear la función Lambda

1. En el dashboard de Lambda, haz clic en **Create function**.
2. En el formulario:
   - **Function name:** `NOMBREALUMNO-Read`
   - **Runtime:** Python 3.12
   - **Execution role:** Selecciona **Use an existing role** → `NOMBREALUMNO-LambdaRole`
3. Haz clic en **Create function**.

### 6.2 – Añadir el código

1. En el editor de código, reemplaza el contenido con:

```python
import os, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # event opcional: {"limit": 25}
    limit = int(event.get("limit", 20))
    resp = table.scan(Limit=limit)
    return {"count": resp.get("Count",0), "items": resp.get("Items", [])}
```

2. Haz clic en **Deploy**.

### 6.3 – Configurar variable de entorno

1. Ve a la pestaña **Configuration** → **Environment variables**.
2. Haz clic en **Edit**.
3. Haz clic en **Add environment variable**:
   - **Key:** `TABLE_NAME`
   - **Value:** `NOMBREALUMNO-notes` (nombre de tu tabla DynamoDB)
4. Haz clic en **Save**.

> **👉 Resultado:** La Lambda Reader está lista para leer notas de DynamoDB.

### 6.4 – Crear Function URL

1. Ve a la pestaña **Configuration** → **Function URL**.
2. Haz clic en **Create function URL**.
3. En el formulario:
   - **Auth type:** `NONE`
   - **Cors:** Habilita CORS
4. En **CORS configuration**:
   - **Allowed origins:** `*`
   - **Allowed methods:** `*`
   - **Allowed headers:** `Content-Type`
   - **Max age:** `86400`
5. Haz clic en **Save**.
6. Copia la **Function URL** y guárdala.

> **👉 Resultado:** La Lambda Reader tiene una URL pública con CORS habilitado.

---

## Paso 7 – Probar las Lambdas

### 7.1 – Probar Lambda Writer

1. Abre una terminal o usa una herramienta como Postman o curl.
2. Ejecuta:

```bash
curl -X POST https://TU-FUNCTION-URL-WRITER \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","note":"Hola desde Lambda"}'
```

Reemplaza `TU-FUNCTION-URL-WRITER` con la URL de la Lambda Writer.

> **✅ Resultado esperado:** Deberías recibir una respuesta como `{"status":"ok","id":"uuid-generado"}`.

### 7.2 – Probar Lambda Reader

1. Ejecuta:

```bash
curl -X POST https://TU-FUNCTION-URL-READER \
  -H "Content-Type: application/json" \
  -d '{"limit":10}'
```

Reemplaza `TU-FUNCTION-URL-READER` con la URL de la Lambda Reader.

> **✅ Resultado esperado:** Deberías recibir una respuesta con el conteo de notas y la lista de elementos.

### 7.3 – Probar desde el navegador

1. Abre la consola del navegador (F12).
2. Ve a la pestaña **Console**.
3. Ejecuta:

```javascript
// Escribir una nota
fetch('https://TU-FUNCTION-URL-WRITER', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Bob', note: 'Nota desde el navegador'})
})
.then(r => r.json())
.then(d => console.log(d))

// Leer notas
fetch('https://TU-FUNCTION-URL-READER', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({limit: 20})
})
.then(r => r.json())
.then(d => console.log(d))
```

> **✅ Resultado esperado:** Las Lambdas funcionan correctamente desde el navegador.

---

## Resultado esperado

Al finalizar este laboratorio, cada alumno debe haber:

- ✅ Creado una tabla DynamoDB con `id` como clave primaria.
- ✅ Creado una policy IAM que permite acciones sobre DynamoDB.
- ✅ Creado un rol de Lambda con permisos a DynamoDB.
- ✅ Creado una Lambda Writer que inserta notas en DynamoDB.
- ✅ Creado una Lambda Reader que lee notas de DynamoDB.
- ✅ Configurado variables de entorno en ambas Lambdas.
- ✅ Creado Function URLs con CORS habilitado para ambas Lambdas.
- ✅ Probado las Lambdas desde curl y desde el navegador.
- ✅ Comprendido cómo Lambda y DynamoDB trabajan juntas.
- ✅ Aprendido a usar CORS para permitir acceso desde aplicaciones web.
