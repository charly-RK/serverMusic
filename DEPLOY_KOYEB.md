# Guía de Despliegue en Koyeb

## Paso 1: Preparar GitHub (si no lo has hecho)

1. **Abre terminal en la carpeta backend**:
   ```cmd
   cd "C:\Users\RISK\Desktop\Proyectos\ 2026\FLUTTER\musicrk_1\backend"
   ```

2. **Inicializa Git**:
   ```cmd
   git init
   git add .
   git commit -m "Backend para Koyeb"
   ```

3. **Crea repositorio en GitHub**:
   - Ve a: https://github.com/new
   - Nombre: `musicrk-backend`
   - Público
   - Click "Create repository"

4. **Sube el código**:
   ```cmd
   git remote add origin https://github.com/TU_USUARIO/musicrk-backend.git
   git branch -M main
   git push -u origin main
   ```

## Paso 2: Crear Cuenta en Koyeb

1. **Ve a**: https://www.koyeb.com/
2. **Click "Sign Up"**
3. **Elige una opción**:
   - GitHub (recomendado - más rápido)
   - O email
4. **Verifica tu email** (si usaste email)
5. **Completa el perfil** (nombre, etc.)

## Paso 3: Crear App en Koyeb

1. **En el Dashboard, click "Create App"**

2. **Selecciona "GitHub"** como fuente

3. **Autoriza Koyeb** para acceder a GitHub
   - Click "Authorize Koyeb"
   - Selecciona tu repositorio `musicrk-backend`

4. **Configuración del Servicio**:

   ### Builder:
   - **Builder**: `Buildpack`
   - **Build command**: 
     ```
     pip install -r requirements.txt
     ```
   
   ### Run command:
   ```
   gunicorn server:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
   ```

   ### Instance:
   - **Region**: Selecciona el más cercano (ej: Washington, D.C.)
   - **Instance type**: `Eco` (gratis)
   
   ### Scaling:
   - **Min instances**: `1`
   - **Max instances**: `1`

   ### Port:
   - **Port**: `8000` (Koyeb usa 8000 por defecto)

5. **Environment Variables** (opcional):
   - Click "Add variable"
   - **Name**: `PYTHON_VERSION`
   - **Value**: `3.11`

6. **App name**: 
   - Pon un nombre único, ej: `musicrk-backend-123`
   - O deja que Koyeb genere uno automático

7. **Click "Deploy"**

## Paso 4: Esperar el Deploy

1. **Verás la pantalla de deploy** con logs en tiempo real
2. **Espera 5-10 minutos** para que:
   - Clone el repositorio
   - Instale dependencias
   - Inicie el servidor
3. **Cuando veas "Healthy"** ✅ está listo

## Paso 5: Obtener la URL

1. **En la página de tu app**, verás:
   - **Public URL**: `https://tu-app.koyeb.app`
2. **Copia esta URL**

## Paso 6: Actualizar Flutter App

1. **Edita `lib/config/api_config.dart`**:
   ```dart
   static const String baseUrl = 'https://tu-app.koyeb.app';
   ```

2. **Guarda el archivo**

3. **Hot restart** en la app (presiona `r`)

4. **Prueba buscar una canción** - ¡debería funcionar!

## Verificar que Funciona

1. **Abre en navegador**: `https://tu-app.koyeb.app/health`
   - Deberías ver: `{"status":"ok","message":"Server is running"}`

2. **Si funciona**, prueba en la app

## Notas Importantes

### Plan Gratuito Koyeb:
- ✅ 2 servicios gratis
- ✅ Siempre activo (no se duerme)
- ✅ 512 MB RAM
- ✅ Suficiente para tu backend
- ⚠️ Límite de 100GB de transferencia/mes

### Limitaciones:
- Si excedes 100GB/mes, el servicio se pausa hasta el próximo mes
- Para uso personal normal, es más que suficiente

## Actualizar el Backend

Cuando hagas cambios al código:

```cmd
git add .
git commit -m "Descripción del cambio"
git push
```

Koyeb detectará el push y re-desplegará automáticamente.

## Monitoreo

- **Logs**: En Koyeb → tu app → pestaña "Logs"
- **Métricas**: Pestaña "Metrics"
- **Settings**: Para cambiar configuración

## Solución de Problemas

### Si el deploy falla:
1. Revisa los logs en Koyeb
2. Verifica que `requirements.txt` esté correcto
3. Asegúrate de que el puerto sea `8000`

### Si FFmpeg no funciona:
Koyeb incluye FFmpeg por defecto, pero si falla:
1. Ve a Settings → Environment variables
2. Agrega:
   - **Name**: `FFMPEG_LOCATION`
   - **Value**: `/usr/bin/ffmpeg`

### Si las descargas son lentas:
1. Aumenta el timeout en el run command:
   ```
   gunicorn server:app --bind 0.0.0.0:$PORT --timeout 600 --workers 2
   ```

## Ventajas de Koyeb

- ✅ No requiere tarjeta de crédito
- ✅ Siempre activo (no se duerme como Render free)
- ✅ Deploy automático desde GitHub
- ✅ SSL/HTTPS incluido
- ✅ Fácil de usar
- ✅ Buen plan gratuito

¡Listo! Ahora tu backend estará disponible 24/7 desde cualquier lugar del mundo.
