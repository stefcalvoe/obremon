# App de perfumes — contexto del proyecto

Negocio personal de venta de perfumes en Costa Rica. Un solo usuario (el dueño),
se usa desde el teléfono. Moneda: colones (₡).

## Restricciones duras

- **Un solo archivo**: `index.html`. Todo el CSS y JS van embebidos. No hay build,
  no hay dependencias, no hay backend.
- **Se abre desde el teléfono**, a veces desde `file://` o `content://`. No usar
  nada que requiera servidor (fetch a APIs, módulos ES, service workers con scope).
- **Persistencia: `localStorage` únicamente.** Es el único almacén de datos del
  negocio; perder una clave es perder registros reales del usuario.
- Interfaz en español de Costa Rica, tono cercano ("vos"). Formato de moneda
  `₡` con separador de miles es-CR.

## Claves de localStorage

| Clave | Contenido |
|---|---|
| `inventario` | `{id, nombre, marca, costo, precio, stock}` |
| `clientes` | `{id, nombre, telefono, deuda, frec, cuota, prox}` |
| `ventas` | `{id, fecha, perfumeId, perfumeNombre, clienteId, clienteNombre, cantidad, total, costoTotal, metodo}` |
| `abonos` | `{id, fecha, clienteId, monto}` |
| `compras` | `{id, fecha, perfumeId, nombre, cantidad, costoUnit}` |

`frec` es `7` (semanal), `15` (quincenal) o `''` (sin plan). `prox` es la fecha
del próximo cobro en ISO `yyyy-mm-dd`.

**Nunca renombrar ni eliminar una clave sin escribir una migración** en el bloque
de migraciones al inicio del script. Ya hay dos: reconstrucción de `compras` para
inventarios viejos, y alta de los campos de plan de cobro en `clientes`.

## Reglas de negocio

- La deuda es **acumulativa por cliente**, no por venta. Una segunda compra a
  crédito se suma al mismo saldo y el plan de cobro sigue igual.
- La cuota es **sugerida, no obligatoria**: el modal la prellena pero el monto es
  editable.
- Un abono nunca deja saldo negativo: se aplica `Math.min(monto, deuda)`.
- Al saldar la deuda, `prox` se limpia. Al registrar una venta a crédito a un
  cliente sin `prox` pero con `frec`, se programa a `hoy + frec`.
- `avanzarProx` adelanta un ciclo desde la fecha **programada**, no desde la de
  pago, y si quedó muy atrasada sigue avanzando hasta que caiga en el futuro.
- Eliminar una venta devuelve el stock y ajusta la deuda. Eliminar un abono
  devuelve el monto al saldo y ofrece retroceder `prox` un ciclo.

## Fechas

Todo en ISO `yyyy-mm-dd`, sin `Date.parse` de strings ni UTC: las fechas se
construyen con `new Date(y, m-1, d)` para evitar corrimientos de zona horaria.
Hay datos viejos guardados en formato local `d/m/yyyy`; `fmtFecha` y `claveFecha`
toleran ambos. No romper esa compatibilidad.

## Verificación antes de entregar

```bash
node docs/pruebas-base.js   # fechas, saldos, identidades del balance
node docs/pruebas-v5.js     # orden del historial, reversión de abonos
```

Los scripts extraen las funciones reales del HTML por posición de comentarios
(`/* ---------- fechas`, `/* ---------- datos`). Si se mueven esos marcadores,
hay que ajustar los slices.

Identidad que siempre debe cumplirse: `contado + abonos + pendiente = vendido`.

## Estado actual (v5)

Funciona: inventario con reabastecimiento y edición, clientes con plan de cobro
semanal/quincenal, agenda de cobros con vencidos, abonos con modal, historial por
cliente con borrado de abonos, balance con costos/ganancias/flujo, respaldo
exportar/importar en JSON.

Pendiente o posible: alertas de stock bajo (el usuario las pospuso hasta que el
negocio crezca), despliegue en Netlify Drop para poder instalar como PWA desde el
teléfono.

## Cómo trabaja el usuario

Respuestas cortas y directas, sin relleno. Prefiere iteración práctica sobre
arquitectura elaborada. Reporta bugs con capturas de pantalla del teléfono.
Antes de cambios grandes, recordarle descargar el respaldo desde Balance.
