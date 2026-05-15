# 📊 Guía de Exportación Excel con IA

## Columnas del Excel actualizado

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **BUS** | Identificador del autobús | Bus080 |
| **CONDUCTOR** | Nombre del conductor | Juan Pérez |
| **FECHA** | Fecha del conteo | 16/04/2026 |
| **INICIO** | Hora inicio (del 1er video) | 05:57:00 |
| **FINAL** | Hora final (del último video) | 06:05:03 |
| **TOTAL** | Conteo MANUAL total | 243 |
| **EFECTIVO** | Conteo manual - Efectivo | 120 |
| **ELECTRÓNICO** | Conteo manual - Electrónico | 100 |
| **CÉDULA** | Conteo manual - Cédula | 23 |
| **🆕 CONTEO_IA** | Personas detectadas por IA | 235 |
| **🆕 DIFERENCIA** | Diferencia absoluta (manual - IA) | 8 |
| **🆕 PRECISION_%** | % de similitud | 96% |
| **🆕 ESTADO_IA** | Validación de datos | MATCH |
| **OBSERVACIONES** | Notas del contador | Tráfico intenso |

---

## 📈 Significado de ESTADO_IA

```
┌─────────────────────────────────────────────────────┐
│ ESTADO_IA               │ Significado               │
├─────────────────────────────────────────────────────┤
│ MATCH     (✅)          │ Conteos coinciden         │
│ CHECK     (⚠️)          │ Diferencia > 2 personas   │
│ PENDING   (⏳)          │ Sin datos de IA           │
└─────────────────────────────────────────────────────┘
```

### Cálculo de PRECISION_%

```
Precision = 100 - (Diferencia / Total Manual) × 100

Ej:
  Manual: 240 personas
  IA: 236 personas
  Diferencia: 4
  Precision: 100 - (4/240)*100 = 98.3%
```

---

## 💡 Uso práctico

### 1. Validar calidad del contador manual
```
Si PRECISION% < 95% → Revisar video manualmente
Si ESTADO_IA = "CHECK" → Diferencia significativa
```

### 2. Entrenar IA
- Usar datos donde ESTADO_IA = "MATCH" (datos confiables)
- Investigar "CHECK" para entender discrepancias
- Acumular datos para mejorar modelo

### 3. Reportes gerenciales
- Ver si contador manual es consistente
- Detectar patrones en discrepancias (ej: cierta hora del día)
- Validar eficiencia del contador

---

## 📋 Ejemplo de Excel generado

```
AFORADOR DE PASAJEROS — AUTOTRANSPORTES MORAVIA
Exportado: 24/04/2026 15:30:00

BUS  CONDUCTOR   FECHA      INICIO    FINAL     TOTAL  E  T  C  IA  DIF  PREC  ESTADO  OBS
─────────────────────────────────────────────────────────────────────────────────────
080  Juan Pérez  16/04/2026  05:57:00  06:05:03  240   120 100 20  236   4   98%   MATCH   OK
080  Juan Pérez  17/04/2026  06:15:00  07:20:00  185   92  75  18  -     -    -    PENDING  Tráfico
─────────────────────────────────────────────────────────────────────────────────────
TOTAL                                            425   212 175 38

```

---

## 🔧 Cómo interpretar discrepancias

| Situación | Causa probable | Acción |
|-----------|---|---|
| PRECISION = 100% | IA muy precisa | ✅ Usar para entrenamiento |
| 90% < PRECISION < 98% | Variabilidad normal | 📊 Monitorear |
| PRECISION < 90% | Error en manual o IA | 🔍 Revisar video |
| CONTEO_IA = "-" | Sin datos IA cargados | ⏳ Cargar modelo IA |

---

## 📥 Próximas mejoras

- [ ] Gráfica de tendencias Precision% por hora
- [ ] Alertas automáticas si Precision% baja
- [ ] Exportar datos brutos (per-frame) para análisis
- [ ] Dashboard de desempeño IA vs contador manual
