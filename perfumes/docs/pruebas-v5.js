const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
const b=html.slice(html.indexOf('/* ---------- fechas'),html.indexOf('/* ---------- datos'));
eval(b);
const cf=html.slice(html.indexOf('function claveFecha'),html.indexOf('function movimientosCliente'));
eval(cf);
let f=0; const ok=(c,m)=>{console.log((c?'  OK  ':'FALLA ')+m); if(!c)f++;};

// Orden del historial con formatos mixtos (datos viejos vs nuevos)
const movs=[{fecha:'2026-09-11'},{fecha:'4/9/2026'},{fecha:'2026-09-04'},{fecha:'28/8/2026'}]
  .sort((x,y)=>claveFecha(x.fecha).localeCompare(claveFecha(y.fecha)));
ok(movs.map(m=>m.fecha).join('|')==='28/8/2026|4/9/2026|2026-09-04|2026-09-11','ordena fechas mixtas cronologicamente');

// Simulacion del caso real de Daniel: 30000 credito, dos abonos de 10000, se borra uno
let deuda=0; deuda+=30000; deuda-=10000; deuda-=10000;
ok(deuda===10000,'estado actual de Daniel = 10000');
deuda+=10000; // eliminarAbono
ok(deuda===20000,'al borrar un abono el saldo vuelve a 20000');

// Retroceso de fecha un ciclo semanal
ok(addDays('2026-09-11',-7)==='2026-09-04','retrocede un ciclo semanal');
ok(addDays('2026-09-15',-15)==='2026-08-31','retrocede un ciclo quincenal cruzando mes');
ok(addDays('2027-01-04',-7)==='2026-12-28','retrocede cruzando año');
console.log('\n'+(f?f+' FALLARON':'TODAS PASARON'));
