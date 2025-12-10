# Guía para Subir Backend a Render

## Paso 1: Preparar el Repositorio Git

1. **Abre una terminal en la carpeta backend**:
   ```cmd
   cd "C:\Users\RISK\Desktop\Proyectos\ 2026\FLUTTER\musicrk_1\backend"
   ```

2. **Inicializa Git** (si no lo has hecho):
   ```cmd
   git init
   git add .
   git commit -m "Initial backend commit"
   ```

3. **Crea un repositorio en GitHub**:
   - Ve a https://github.com/new
   - Nombre: `musicrk-backend` (o el que prefieras)
   - Público o Privado (tu elección)
   - NO inicialices con README
   - Click "Create repository"

4. **Sube tu código a GitHub**:
   ```cmd
   git remote add origin https://github.com/TU_USUARIO/musicrk-backend.git
   git branch -M main
   git push -u origin main
   ```

## Paso 2: Crear Servicio en Render

1. **Ve a Render**: https://dashboard.render.com/

2. **Crea una cuenta** (puedes usar GitHub para login rápido)

3. **Click en "New +"** → **"Web Service"**

4. **Conecta tu repositorio**:
   - Click "Connect account" si es la primera vez
   - Autoriza Render para acceder a GitHub
   - Selecciona tu repositorio `musicrk-backend`
   - Click "Connect"

## Paso 3: Configurar el Servicio

En la página de configuración, llena los siguientes campos:

### Basic Settings:
- **Name**: `musicrk-backend` (o el que prefieras)
- **Region**: Selecciona el más cercano a ti (ej: Oregon USA)
- **Branch**: `main`
- **Root Directory**: deja vacío (o pon `backend` si subiste todo el proyecto)
- **Runtime**: `Python 3`

### Build & Deploy:
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  gunicorn server:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
  ```

### Instance Type:
- Selecciona **"Free"** (gratis, pero con limitaciones)
- O **"Starter"** ($7/mes, más estable)

### Environment Variables:
Click "Add Environment Variable" y agrega:
- **Key**: `PYTHON_VERSION`
- **Value**: `3.11.0`

## Paso 4: Deploy

1. **Click "Create Web Service"**

2. **Espera a que se despliegue** (puede tomar 5-10 minutos)
   - Verás los logs en tiempo real
   - Debe decir "Build successful" y luego "Deploy live"

3. **Copia tu URL**:
   - Será algo como: `https://musicrk-backend.onrender.com`

## Paso 5: Actualizar la App Flutter

1. **Edita `lib/config/api_config.dart`**:
   ```dart
   static const String baseUrl = 'https://musicrk-backend.onrender.com';
   ```

2. **Haz hot restart** en la app

3. **Prueba buscar y descargar** - ¡debería funcionar desde cualquier lugar!

## Notas Importantes

### Plan Gratuito de Render:
- ✅ Gratis para siempre
- ⚠️ Se "duerme" después de 15 minutos de inactividad
- ⚠️ Primera petición después de dormir tarda ~30 segundos
- ⚠️ 750 horas/mes (suficiente para uso personal)

### Plan Starter ($7/mes):
- ✅ Siempre activo (no se duerme)
- ✅ Más rápido
- ✅ Mejor para uso frecuente

### Limitaciones de FFmpeg:
- Render incluye FFmpeg por defecto
- Si no funciona, agrega al `requirements.txt`:
  ```
  ffmpeg-python
  ```

## Solución de Problemas

### Si el deploy falla:
1. Revisa los logs en Render
2. Verifica que `requirements.txt` esté correcto
3. Asegúrate de que `Procfile` existe

### Si FFmpeg no funciona:
1. Agrega variable de entorno en Render:
   - **Key**: `FFMPEG_LOCATION`
   - **Value**: `/usr/bin/ffmpeg`

### Si las descargas fallan:
1. Aumenta el timeout en `Procfile`:
   ```
   --timeout 600
   ```

## Actualizar el Backend

Cuando hagas cambios:

```cmd
git add .
git commit -m "Descripción de cambios"
git push
```

Render detectará el push y re-desplegará automáticamente.

## Monitoreo

- **Logs**: Ve a tu servicio en Render → pestaña "Logs"
- **Métricas**: Pestaña "Metrics" muestra uso de CPU/memoria
- **Shell**: Pestaña "Shell" para ejecutar comandos en el servidor
