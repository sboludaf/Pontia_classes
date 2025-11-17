# Laboratorio 1: Bedrock Agents con Lambda Functions

## Objetivo
Crear un agente de Bedrock que integre dos funciones Lambda (DateTimeFunction y WeatherFunction) mediante Action Groups, permitiendo al agente consultar la fecha/hora actual y el clima de cualquier ciudad.

---

## Paso 1: Crear la función Lambda DateTimeFunction-ALUMNO

1. Ve a la consola de AWS Lambda
2. Haz clic en **Create function**
3. Configura:
   - **Function name**: `DateTimeFunction-sboludaf`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
4. Haz clic en **Create function**

---

## Paso 2: Subir el código desplegado en el bucket S3

1. Descarga el archivo ZIP desde: `s3://clase8-lab1/TIME/time-lambda.zip`
2. En la consola de Lambda, ve a la sección **Code**
3. Haz clic en **Upload from** → **S3**
4. Ingresa la URL: `s3://clase8-lab1/TIME/time-lambda.zip`
5. Haz clic en **Save**

---

## Paso 3: Añadir Resource-based policy statements con permisos de Bedrock

1. En la consola de Lambda, ve a la pestaña **Configuration** → **Permissions**
2. Desplázate hasta **Resource-based policy statements**
3. Haz clic en **Add permissions**
4. Configura:
   - **Principal**: `bedrock.amazonaws.com`
   - **Action**: `lambda:InvokeFunction`
   - **Resource ARN**: `arn:aws:bedrock:eu-west-1:838205824064:agent/*`
5. Haz clic en **Save**

---

## Paso 4: Crear la función Lambda WeatherFunction-ALUMNO

1. Ve a la consola de AWS Lambda
2. Haz clic en **Create function**
3. Configura:
   - **Function name**: `WeatherFunction-sboludaf`
   - **Runtime**: Python 3.11
   - **Architecture**: x86_64
4. Haz clic en **Create function**

---

## Paso 5: Subir el código zip desplegado en bucket S3

1. Descarga el archivo ZIP desde: `s3://clase8-lab1/weather/weather-lambda.zip`
2. En la consola de Lambda, ve a la sección **Code**
3. Haz clic en **Upload from** → **S3**
4. Ingresa la URL: `s3://clase8-lab1/weather/weather-lambda.zip`
5. Haz clic en **Save**

---

## Paso 6: Añadir el Resource-based policy statements con permisos de Bedrock

1. En la consola de Lambda, ve a la pestaña **Configuration** → **Permissions**
2. Desplázate hasta **Resource-based policy statements**
3. Haz clic en **Add permissions**
4. Configura:
   - **Principal**: `bedrock.amazonaws.com`
   - **Action**: `lambda:InvokeFunction`
   - **Resource ARN**: `arn:aws:bedrock:eu-west-1:838205824064:agent/*`
5. Haz clic en **Save**

---

## Paso 7: En Amazon Bedrock, crear un agente

1. Ve a la [Consola de Bedrock](https://console.aws.amazon.com/bedrock)
2. En el panel izquierdo, selecciona **Agents** bajo **Builder tools**
3. Haz clic en **Create agent**
4. Configura:
   - **Name**: `MyBedrockAgent-sboludaf`
   - **Description**: (Opcional) Agente con acceso a funciones de tiempo y clima
5. Haz clic en **Create**

---

## Paso 8: Seleccionar el Rol "BedrockAgentsRole"

1. En la sección **Agent resource role**, selecciona **Use an existing service role**
2. Busca y selecciona: `BedrockAgentsRole`
3. Haz clic en **Save**

---

## Paso 9: Cambiar el modelo a Nova Micro

1. En la sección **Select model**, haz clic en el dropdown
2. Busca y selecciona: **Amazon Nova Micro**
3. Haz clic en **Save**

---

## Paso 10: Añadir una instrucción sencilla al agente (Primera versión)

1. En la sección **Instructions for the Agent**, ingresa:
   ```
   Eres un simpático agente que ayuda al usuario en sus necesidades.
   ```
2. Haz clic en **Save**

---

## Paso 11: Probar unos prompts sencillos (Sin herramientas)

1. En el panel derecho, verás una sección de **Test agent**
2. Prueba los siguientes prompts:
   - "Hola, ¿cómo estás?"
   - "¿Cuál es la fecha de hoy?"
   - "¿Qué tiempo hace en Madrid?"

**Resultado esperado**: El agente responderá de forma amigable, pero indicará que no tiene herramientas conectadas para responder preguntas sobre clima y hora.

---

## Paso 12: Añadir Action Group "TimeActions"

1. Ve a la pestaña **Action groups**
2. Haz clic en **Add**
3. Configura:
   - **Action group name**: `TimeActions`
   - **Description**: Obtener fecha y hora actual
4. Haz clic en **Next**

---

## Paso 13: Seleccionar "Define with API schemas"

1. En **Action group type**, selecciona: **Define with API schemas**
2. Haz clic en **Next**

---

## Paso 14: Select an existing Lambda function

1. En **Action group invocation**, selecciona: **Select an existing Lambda function**
2. En el dropdown, selecciona: `DateTimeFunction-sboludaf`
3. Haz clic en **Next**

---

## Paso 15: Select an existing API schema

1. En **Action group schema**, selecciona: **Define via S3 URL**
2. Ingresa la URL: `s3://clase8-lab1/TIME/time_API_SCHEMA.yaml`
3. Haz clic en **Create**

---

## Paso 16: Modificar el System Prompt con la nueva tool (Segunda versión)

1. Haz clic en **Save**
2. Haz clic en **Prepare** para preparar el agente
3. En la sección **Instructions for the Agent**, actualiza el prompt a:
   ```
   Eres un simpático agente que ayuda al usuario en sus necesidades. 
   Tienes acceso a funciones para obtener la fecha y hora actual.
   ```
4. Haz clic en **Save** nuevamente

---

## Paso 16.5: Probar TimeActions

1. En el panel de prueba, prueba los siguientes prompts:
   - "¿Cuál es la fecha y hora actual?"
   - "¿Qué hora es?"

**Resultado esperado**: El agente invoca `TimeActions` y retorna la fecha y hora actual.

---

## Paso 17: Añadir Action Group "WeatherActions"

1. Ve a la pestaña **Action groups**
2. Haz clic en **Add**
3. Configura:
   - **Action group name**: `WeatherActions`
   - **Description**: Obtener información del clima actual
4. Haz clic en **Next**

---

## Paso 18: Configurar WeatherActions con API Schema

1. En **Action group type**, selecciona: **Define with API schemas**
2. En **Action group invocation**, selecciona: **Select an existing Lambda function**
3. Selecciona: `WeatherFunction-sboludaf`
4. En **Action group schema**, selecciona: **Define via S3 URL**
5. Ingresa la URL: `s3://clase8-lab1/weather/Weather_API_SCHEMA.yaml`
6. Haz clic en **Create**

---

## Paso 19: Modificar el System Prompt con ambas tools (Tercera versión)

1. Haz clic en **Save**
2. Haz clic en **Prepare** para preparar el agente con ambas herramientas
3. En la sección **Instructions for the Agent**, actualiza el prompt a:
   ```
   Eres un simpático agente que ayuda al usuario en sus necesidades. 
   Tienes acceso a funciones para obtener la fecha y hora actual, 
   así como información del clima de cualquier ciudad.
   ```
4. Haz clic en **Save** nuevamente
5. Haz clic en **Prepare** para preparar el agente con la nueva instrucción
6. Haz clic en **Save and exit**

---

## Paso 20: Probar las 2 tools

En el panel de prueba del agente, prueba los siguientes prompts:

### Prueba 1: Obtener fecha y hora
```
¿Cuál es la fecha y hora actual?
```
**Resultado esperado**: El agente invoca `TimeActions` y retorna la fecha y hora actual.

### Prueba 2: Obtener clima
```
¿Qué tiempo hace en Barcelona?
```
**Resultado esperado**: El agente invoca `WeatherActions` y retorna la temperatura, viento y descripción del clima.

### Prueba 3: Consulta combinada
```
Dime la hora actual y el clima en Madrid
```
**Resultado esperado**: El agente invoca ambas herramientas y proporciona ambas respuestas.

### Prueba 4: Consulta general
```
Hola, ¿puedes ayudarme con información sobre el clima en París?
```
**Resultado esperado**: El agente responde de forma amigable e invoca la herramienta de clima.

---

## Verificación Final

✅ Ambas funciones Lambda están creadas y tienen permisos de Bedrock
✅ El agente está configurado con el rol `BedrockAgentsRole-sboludaf`
✅ El modelo es Amazon Nova Micro
✅ Ambos Action Groups están configurados y funcionando
✅ El agente responde correctamente a consultas sobre hora y clima

---

## Recursos

- **Bucket S3**: `s3://clase8-lab1/`
  - TIME: `s3://clase8-lab1/TIME/`
  - Weather: `s3://clase8-lab1/weather/`
- **Rol IAM**: `BedrockAgentsRole-sboludaf`
- **Región**: `eu-west-1` (West Europe)

