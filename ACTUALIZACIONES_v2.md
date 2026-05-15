# 🚀 Aforador AMSA v16.15 - Actualizaciones v2

## ✨ Nuevas funcionalidades implementadas

### 1️⃣ **Atajos de teclado mejorados**

| Tecla | Acción | Nota |
|-------|--------|------|
| **1** | +Efectivo | Existente |
| **2** | +Electrónico | Existente |
| **3** | +Cédula | Existente |
| **4** | ➜ Siguiente video | **NUEVO** |
| **ESPACIO** | ➜ Siguiente video | **NUEVO** |
| **ENTER** | ➜ Siguiente video | Existente |
| **+** o **=** | Hacer corte | Existente |

**Nota importante**: El espacio funciona NORMALMENTE (como espacio) cuando escribes en las casillas de Observaciones o cualquier textarea/input.

---

### 2️⃣ **Campo AFORADOR agregado**

- Nueva sección colapsable: **📝 AFORADOR**
- Almacena el nombre de quien cuenta los pasajeros
- Se guarda en cada corte
- **Se exporta en el Excel** con los datos del corte

---

### 3️⃣ **Bug de Observaciones CORREGIDO** ✅

- Las observaciones ahora se exportan correctamente en Excel
- Se incluyen en cada fila del corte

---

### 4️⃣ **Layout 3 COLUMNAS con Panel Retractable**

```
┌────────────────────────────────────────────────┐
│ AFORADOR DE PASAJEROS v16.15                   │
├──────────────────┬──────────────┬──────────────┤
│                  │              │   VIDEOS ◀   │
│  VIDEO PLAYER    │  CONTROLES   │   (Retract)  │
│  (Grande)        │              │              │
│                  │ • Cortes     │ • Bus080...  │
│                  │ • Total      │ • Bus080...  │
│                  │ • Contadores │ • Bus080...  │
│                  │ • Conductor  │              │
│                  │ • Aforador   │              │
│                  │ • Obs        │              │
│                  │ • IA Panel   │              │
│                  │              │              │
└──────────────────┴──────────────┴──────────────┘
```

**Características del panel videos**:
- 📌 Botón toggle **"◀ VIDEOS"** en la esquina superior derecha
- 🎯 Click para ocultar/mostrar hacia la derecha
- 📊 Cuando está oculto, gana más espacio para los controles
- ⏱️ Transición suave (0.3 segundos)

---

## 📋 Cambios técnicos

### Estado (state)
```javascript
const state = {
  vids: {},
  queue: [],
  cur: null,
  curIdx: -1,
  cortes: [],
  corteStart: 0,
  e: 0, t: 0, c: 0,
  aforador: '',  // NUEVO
  ia: { count: 0, status: 'ready', trainingSamples: 0 }
}
```

### Funciones nuevas
- `toggleVideoPanel()` - Muestra/oculta panel de videos

### Grid CSS actualizado
```css
.body {
  grid-template-columns: 1fr 340px 320px;  /* Video | Controles | Videos */
}
```

---

## 📊 Excel exportación

**Nuevas columnas en Excel**:
- AFORADOR → Nombre de quien contó
- Observaciones ahora se exportan correctamente
- Además: CONTEO_IA, DIFERENCIA, PRECISION_%, ESTADO_IA (del update anterior)

**Estructura del Excel ahora**:
```
| BUS | CONDUCTOR | AFORADOR | FECHA | INICIO | FINAL | TOTAL | E | T | C | IA | DIF | PREC | ESTADO | OBS |
```

---

## 🎯 Flujo de trabajo recomendado

1. **Cargar videos** → Aparecen en panel derecho
2. **Contar pasajeros** → Con atajos 1/2/3 o botones
3. **Atajos rápidos** → 4 o ESPACIO para siguiente video
4. **Hacer corte** → Se guardan: Conductor, Aforador, Observaciones
5. **Exportar Excel** → Con todos los datos incluidos

---

## 💡 Notas

- El espacio en textareas (Observaciones) funciona NORMALMENTE
- El espacio fuera de textareas = siguiente video
- Panel videos se oculta hacia la DERECHA (no desaparece, está ahí)
- Todos los datos se sincronizan con IA automáticamente

---

## 📁 Archivo actualizado
`C:\aforador-ia\Aforador_AMSA_v16.15_IA.html`

---

**Estado**: ✅ Listo para testear en navegador
