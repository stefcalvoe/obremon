const fs = require('fs');
const html = fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');

// Extraer el bloque REAL de funciones de fecha del archivo entregado
const ini = html.indexOf('/* ---------- fechas');
const fin = html.indexOf('/* ---------- datos');
if (ini < 0 || fin < 0) { console.error('NO se pudo extraer el bloque de fechas'); process.exit(1); }
const bloque = html.slice(ini, fin);
eval(bloque);

let fallos = 0;
function ok(cond, msg, extra='') {
  if (cond) console.log('  OK  ' + msg);
  else { console.log('FALLA ' + msg + '  ' + extra); fallos++; }
}

console.log('--- Fechas ---');
ok(addDays('2026-09-04', 7)  === '2026-09-11', 'semanal simple');
ok(addDays('2026-09-04', 15) === '2026-09-19', 'quincenal simple');
ok(addDays('2026-09-28', 7)  === '2026-10-05', 'cruce de mes');
ok(addDays('2026-12-28', 7)  === '2027-01-04', 'cruce de año');
ok(addDays('2028-02-25', 7)  === '2028-03-03', 'año bisiesto (29 feb existe)');
ok(addDays('2026-02-25', 7)  === '2026-03-04', 'año no bisiesto');
ok(fmtFecha('2026-09-04') === '4/9/2026', 'formato de despliegue');
ok(fmtFecha('4/9/2026')   === '4/9/2026', 'tolera fechas viejas en formato local');
ok(fmtFecha('') === '', 'fecha vacía no rompe');

console.log('--- Estado de cobro ---');
const hoy = hoyISO();
ok(diasDesdeHoy(hoy) === 0, 'hoy = 0 días');
ok(diasDesdeHoy(addDays(hoy, 3)) === 3, 'futuro = +3');
ok(diasDesdeHoy(addDays(hoy, -5)) === -5, 'pasado = -5');
ok(estadoCobro(hoy).badge === 'hoy', 'badge hoy');
ok(estadoCobro(addDays(hoy,-1)).badge === 'vencido', 'badge vencido');
ok(estadoCobro(addDays(hoy,10)).badge === 'prox', 'badge próximo');
ok(estadoCobro('').txt === 'Sin fecha', 'sin fecha programada');

console.log('--- Avance del plan de cobro ---');
// caso normal: al día, avanza una vuelta
const p1 = avanzarProx(addDays(hoy, 2), 7);
ok(p1 === addDays(hoy, 9), 'al día: avanza 7 desde la fecha programada');
// caso atrasado leve: la siguiente cuota ya cae en futuro
const p2 = avanzarProx(addDays(hoy, -3), 7);
ok(p2 === addDays(hoy, 4), 'atraso leve: siguiente cuota queda en futuro');
// caso muy atrasado: no debe devolver fecha pasada
const p3 = avanzarProx(addDays(hoy, -60), 15);
ok(diasDesdeHoy(p3) >= 0, 'atraso grande: nunca deja fecha vencida', p3);
ok(diasDesdeHoy(p3) < 15, 'atraso grande: no se pasa de un ciclo', p3);
// quincenal desde hoy
ok(avanzarProx(hoy, 15) === addDays(hoy, 15), 'quincenal desde hoy');
// sin frecuencia => sin fecha
ok(avanzarProx(hoy, '') === '', 'sin plan no programa fecha');

console.log('--- Saldos y abonos (recálculo independiente) ---');
// Simulación independiente de la regla: deuda = créditos - abonos aplicados, nunca negativa
function simular(eventos) {
  let deuda = 0, abonado = 0;
  for (const e of eventos) {
    if (e.t === 'credito') deuda += e.m;
    if (e.t === 'contado') { /* no toca deuda */ }
    if (e.t === 'abono') { const ap = Math.min(e.m, deuda); deuda -= ap; abonado += ap; }
  }
  return { deuda: Math.round(deuda*100)/100, abonado };
}
let r;
r = simular([{t:'credito',m:13000},{t:'abono',m:5000}]);
ok(r.deuda === 8000 && r.abonado === 5000, 'venta 13000 - abono 5000 = 8000');

r = simular([{t:'credito',m:13000},{t:'abono',m:5000},{t:'credito',m:30000},{t:'abono',m:5000}]);
ok(r.deuda === 33000, 'deuda acumulativa con segunda compra = 33000');

r = simular([{t:'credito',m:13000},{t:'abono',m:20000}]);
ok(r.deuda === 0 && r.abonado === 13000, 'sobrepago se limita a la deuda, no queda negativa');

r = simular([{t:'contado',m:30000},{t:'credito',m:13000}]);
ok(r.deuda === 13000, 'la venta de contado no suma deuda');

r = simular([{t:'credito',m:13000},{t:'abono',m:4333.33},{t:'abono',m:4333.33},{t:'abono',m:4333.34}]);
ok(r.deuda === 0, 'tres cuotas con decimales cierran en cero exacto', r.deuda);

console.log('--- Balance (identidades contables) ---');
const ventasT = [
  {total:13000, costoTotal:6400, metodo:'credito'},
  {total:30000, costoTotal:12500, metodo:'contado'}
];
const abonosT = [{monto:5000}];
const comprasT = [{cantidad:1,costoUnit:6400},{cantidad:1,costoUnit:12500},{cantidad:1,costoUnit:17000}];
const totalVendido = ventasT.reduce((a,v)=>a+v.total,0);
const costoVendido = ventasT.reduce((a,v)=>a+v.costoTotal,0);
const contado = ventasT.filter(v=>v.metodo==='contado').reduce((a,v)=>a+v.total,0);
const credito = ventasT.filter(v=>v.metodo==='credito').reduce((a,v)=>a+v.total,0);
const abonado = abonosT.reduce((a,x)=>a+x.monto,0);
const pendiente = credito - abonado;
const invertido = comprasT.reduce((a,c)=>a+c.cantidad*c.costoUnit,0);

ok(totalVendido === contado + credito, 'vendido = contado + crédito');
ok(totalVendido - costoVendido === 24100, 'ganancia bruta correcta (43000-18900)');
ok(contado + abonado === 35000, 'efectivo recuperado = 35000');
ok(pendiente === 8000, 'pendiente de cobro = 8000');
ok(contado + abonado + pendiente === totalVendido, 'cobrado + pendiente = vendido');
ok(contado + abonado - invertido === -900, 'posición de caja = 35000 - 35900');

console.log('\n' + (fallos === 0 ? 'TODAS LAS PRUEBAS PASARON' : fallos + ' PRUEBA(S) FALLARON'));
process.exit(fallos ? 1 : 0);
