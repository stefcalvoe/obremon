# 📊 Aforador AMSA v16.15 - Guía de Almacenamiento de IA

## Flujo de Datos

```
[CONTADOR MANUAL] ➜ [IA APRENDIENDO] ➜ [HACER CORTE] ➜ [GUARDAR + DESCARGAR]
    Efectivo          Listo: X         Genera JSON      localStorage
   Electrónico        Personas         JSON descarga      + Archivo
    Cédula           Muestras         automático        local
```

---

## 🗄️ Dónde se guardan los datos

### 1️⃣ **localStorage del Navegador** (Persisten)
- **Ubicación**: Almacenamiento local del navegador (Chrome DevTools → Application → Local Storage)
- **Clave**: `ia_training_samples`
- **Formato**: Array JSON con todas las muestras acumuladas
- **Capacidad**: ~5-10 MB por dominio (suficiente para miles de muestras)
- **Persistencia**: Sobrevive cerrar/abrir navegador

### 2️⃣ **Descargas JSON** (Backup local)
- **Ubicación**: Carpeta de Descargas del sistema
- **Nombre**: `ia_training_TIMESTAMP.json`
- **Contenido**: Muestra individual del corte (video, conteos, diferencias)
- **Se descarga**: Automáticamente al hacer CORTE

### 3️⃣ **Opción: Servidor Remoto** (Futuro)
- Se puede conectar un backend para:
  - Sincronizar datos entre dispositivos
  - Reentrenar modelo YOLOv8 automáticamente
  - Historial centralizado

---

## 📈 Estructura de datos

```json
{
  "timestamp": "2026-04-24T15:30:00.000Z",
  "videos": [
    {
      "video": "Bus080_2026-04-16_05-57-00_20.mov",
      "manual": 24,
      "ia": 22,
      "diff": 2,
      "types": {
        "efectivo": 15,
        "electronico": 7,
        "cedula": 2
      }
    }
  ],
  "totalManual": 24,
  "totalIA": 22
}
```

---

## 🚀 Workflow

### Al hacer CORTE:
1. ✅ Se genera JSON con comparación manual vs IA
2. 💾 Se guarda en `localStorage` (acumula todas las muestras)
3. 📥 Se descarga archivo JSON automático
4. 📊 Panel muestra: "N muestras guardadas"

### Recuperar datos:
```javascript
// Desde consola del navegador:
JSON.parse(localStorage.getItem('ia_training_samples'))
```

### Limpiar datos:
```javascript
localStorage.removeItem('ia_training_samples')
```

---

## 💡 Casos de uso

| Caso | Solución |
|------|----------|
| Ver progreso del aprendizaje | Panel IA muestra "N muestras guardadas" |
| Backup de datos | Descargas JSON se acumulan en carpeta Descargas |
| Reentrenar modelo | Exportar JSON de localStorage → alimentar YOLOv8 |
| Sincronizar entre PCs | Copiar archivos JSON descargados a otro PC |
| Base de datos centralizada | Integrar API backend para guardar en servidor |

---

## 🔧 Próximos pasos

### Fase 2: Reentrenamiento
```python
# Cargar datos de entrenamiento
import json
samples = json.load(open('ia_training_*.json'))

# Crear dataset custom
# Entrenar YOLOv8 con smart_counter_improved.py
# Validar precision
```

### Fase 3: Integración con Backend (Opcional)
```javascript
// Enviar a servidor
fetch('/api/training/save', {
  method: 'POST',
  body: JSON.stringify(training)
})
```

---

**Estado actual**: ✅ Almacenamiento local completo con localStorage + descarga automática JSON
