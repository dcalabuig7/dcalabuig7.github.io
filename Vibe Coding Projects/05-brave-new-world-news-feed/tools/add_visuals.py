import json
d = json.load(open('edition-v4.json'))
V = {
"uk-boe": {
 "why": "Encarece las hipotecas variables y los préstamos en Reino Unido y mejora algo lo que pagan los ahorros. El banco sube tipos para frenar una inflación que espera que siga subiendo.",
 "terms": [{"t":"Bank Rate","d":"El tipo de interés oficial del Banco de Inglaterra. Marca lo que cuesta pedir dinero prestado en el país."},
           {"t":"IPC","d":"Índice de precios al consumo: mide cuánto suben los precios. El objetivo del banco es el 2%."}],
 "visual": {"type":"bars","title":"Inflación en Reino Unido: dato y previsión del banco","unit":"%","ref":{"value":2,"label":"Objetivo 2%"},
   "items":[{"label":"Sept. 2026 (dato)","value":3.5},{"label":"T1 2027 (previsión)","value":4.5,"dim":True},{"label":"T2 2027 (previsión)","value":5,"dim":True}],
   "source":"Bank of England, noviembre 2026"}},
"uk-pmi": {
 "why": "El PMI es un termómetro rápido de la actividad. Por debajo de 50 significa que el sector se está contrayendo, y en octubre cayó todavía más.",
 "terms": [{"t":"PMI","d":"Índice basado en encuestas a directivos de compras. 50 es la frontera: por encima crece la actividad, por debajo se reduce."}],
 "visual": {"type":"bars","title":"PMI de construcción en Reino Unido","unit":"","ref":{"value":50,"label":"50: frontera entre crecer y caer"},"min":40,
   "items":[{"label":"Septiembre","value":46.1},{"label":"Octubre","value":43.6,"hl":True}],"source":"CPA, que cita a S&P Global (una sola fuente)"}},
"es-29n": {
 "why": "Faltan tres semanas para las elecciones generales. Lo que pase en estos días (caso Koldo, huelgas de tren, accidente de Urda) entra de lleno en la campaña.",
 "terms": [{"t":"Jornada de reflexión","d":"El día anterior a la votación, en el que no se puede hacer campaña."}],
 "visual": {"type":"timeline","title":"Calendario electoral del 29-N","items":[
   {"date":"6 nov.","label":"Hoy: precampaña","hl":True},{"date":"13 nov.","label":"Empieza la campaña oficial"},{"date":"24 nov.","label":"Se prohíbe publicar encuestas"},
   {"date":"27 nov.","label":"Termina la campaña"},{"date":"28 nov.","label":"Jornada de reflexión"},{"date":"29 nov.","label":"Votación, de 9:00 a 20:00"}],
   "source":"El Español y Uno TV (AFP)"}},
"es-koldo": {
 "why": "Es una investigación judicial sobre posibles comisiones a cambio de contratos públicos de Transportes, y afecta a un exministro a pocas semanas de las elecciones.",
 "terms": [{"t":"Pieza separada","d":"Una parte de una investigación judicial que se tramita aparte para estudiar un asunto concreto."},
           {"t":"Adif","d":"La empresa pública que gestiona las vías y estaciones de tren en España."}],
 "visual": {"type":"claims","title":"Qué se sabe y quién lo dice","items":[
   {"who":"EFE","says":"La Guardia Civil hizo el jueves una operación en una nueva pieza separada del caso Koldo.","ok":"una"},
   {"who":"EFE","says":"Registró la casa del exministro Ábalos y pidió información a Adif.","ok":"una"},
   {"who":"Euronews (solo titular)","says":"La Fiscalía Europea investiga un posible fraude con fondos de la alta velocidad.","ok":"una"}],
   "source":"No he encontrado una segunda fuente independiente"}},
"es-semaf": {
 "why": "Si no hay acuerdo, el martes 10 se paran los trenes de Renfe y el jueves 12 habrá paros parciales. Los maquinistas piden más seguridad tras el accidente de Urda.",
 "terms": [{"t":"Semaf","d":"El sindicato mayoritario de maquinistas de tren en España."},{"t":"Servicios mínimos","d":"Los trenes que deben circular aunque haya huelga. Los fija el Ministerio."}],
 "visual": {"type":"timeline","title":"Qué ha pasado y qué viene","items":[
   {"date":"28 oct.","label":"Choque de dos trenes en Urda (Toledo): 69 muertos"},{"date":"6 nov.","label":"Hoy: nueva reunión con Transportes","hl":True},
   {"date":"10 nov.","label":"Huelga total en Renfe, todo el día"},{"date":"12 nov.","label":"Paros parciales en tres franjas"},{"date":"17 nov.","label":"Huelga convocada en Adif"}],
   "source":"Euronews, Diario del Sur, Demócrata y EFE"}},
"es-bce": {
 "why": "Si saliera elegido, sería la primera vez que un español preside el Banco Central Europeo, que fija los tipos de interés de la zona euro.",
 "terms": [{"t":"BCE","d":"Banco Central Europeo: decide los tipos de interés de los países del euro."},{"t":"Eurogrupo","d":"La reunión de los ministros de Economía de la zona euro."}],
 "visual": {"type":"steps","title":"El camino de la candidatura","items":[
   {"label":"Julio 2026","text":"El Gobierno respalda a Hernández de Cos (Euronews)"},{"label":"Octubre 2026","text":"Se informa de que el PP también le apoya (Moncloa.com)"},
   {"label":"Hoy","text":"Carta al presidente del Eurogrupo para formalizarla (según EFE)","hl":True},
   {"label":"Después","text":"Los países del euro eligen entre los candidatos (contexto general)","dim":True}],
   "source":"Euronews, Moncloa.com y EFE"}},
"es-aceite": {
 "why": "Con una cosecha muy grande, el precio en origen puede caer. La retirada obligatoria quita aceite del mercado para sostener ese precio, aunque eso puede afectar a lo que paga el consumidor.",
 "terms": [{"t":"Retirada obligatoria","d":"Las almazaras tienen que guardar fuera del mercado una parte de su aceite hasta la campaña siguiente."},{"t":"Almazara","d":"El molino donde se hace el aceite."}],
 "visual": {"type":"bars","title":"Aceite 2026/27, en miles de toneladas","unit":" mil t",
   "items":[{"label":"Existencias + producción","value":1959.5},{"label":"Producción estimada","value":1602.6},{"label":"Retirada estimada (~12%)","value":189,"hl":True}],
   "source":"Cálculo de Wikifarmer con datos del Ministerio de Agricultura"}},
"int-midterms": {
 "why": "Con las dos cámaras en manos demócratas, Trump necesitará pactar para aprobar leyes y nombramientos en los dos años que le quedan.",
 "terms": [{"t":"Midterms","d":"Elecciones de mitad de mandato: se renueva toda la Cámara de Representantes y un tercio del Senado."}],
 "visual": {"type":"compare","title":"Senado: antes y después","items":[
   {"label":"Antes","a":47,"b":53,"aL":"Demócratas","bL":"Republicanos"},
   {"label":"Ahora (proyección CNN)","a":54,"b":46,"aL":"Demócratas","bL":"Republicanos y sin decidir","note":"Aún hay escaños sin decidir"}],
   "source":"NPR y Mappr (antes), CNN (proyección, no definitiva)"}},
"int-iran": {
 "why": "El estrecho de Ormuz es una ruta clave del petróleo mundial. Cualquier choque allí mueve el precio del crudo y, con él, la gasolina y la inflación.",
 "terms": [{"t":"Estrecho de Ormuz","d":"Paso marítimo entre Irán y Omán por el que circula una parte muy importante del petróleo del mundo."},{"t":"IRGC","d":"Guardia Revolucionaria de Irán, el cuerpo militar de élite del régimen."}],
 "visual": {"type":"claims","title":"Quién dice qué","items":[
   {"who":"Guardia Revolucionaria (vía IRNA y Anadolu)","says":"Derribó dos drones estadounidenses sobre la isla de Qeshm.","ok":"una"},
   {"who":"EE. UU.","says":"No he encontrado confirmación ni desmentido.","ok":"no"},
   {"who":"Exteriores de Irán (vía Oman Observer)","says":"El estrecho sigue cerrado.","ok":"una"}],
   "source":"Anadolu y Oman Observer"}},
"int-papa": {
 "why": "Es el primer gran viaje del papa a Latinoamérica tras su operación de pulmón.",
 "terms": [],
 "visual": {"type":"timeline","title":"La gira","items":[
   {"date":"6 nov.","label":"Llega a Uruguay","hl":True},{"date":"Después","label":"Argentina"},{"date":"Después","label":"Perú"},{"date":"16 nov.","label":"Fin de la gira"}],
   "source":"EFE y Religion Media Centre"}},
"eco-wallst": {
 "why": "Las empresas de inteligencia artificial pesan mucho en la bolsa. Cuando caen, arrastran a los índices y a los fondos de inversión y planes de pensiones que los siguen.",
 "terms": [{"t":"Nasdaq","d":"Índice de la bolsa de Nueva York con mucho peso de empresas tecnológicas."},{"t":"VIX","d":"El llamado índice del miedo: sube cuando los inversores esperan más turbulencias."}],
 "visual": {"type":"bars","title":"Caída del jueves en Wall Street","unit":"%",
   "items":[{"label":"Nasdaq","value":-5.52,"hl":True},{"label":"S&P 500","value":-4.36},{"label":"Dow Jones","value":-3.44}],
   "source":"IC Markets, NordFX y The Rio Times"}},
"eco-asia": {
 "why": "Muestra que la caída no se quedó en EE. UU.: las bolsas de Japón, Corea y Taiwán, con mucho peso de chips, cayeron con fuerza.",
 "terms": [{"t":"Circuit breaker","d":"Freno automático que detiene la bolsa unos minutos cuando cae demasiado de golpe."}],
 "visual": {"type":"bars","title":"Las cifras no coinciden según la fuente","unit":"%",
   "items":[{"label":"Nikkei (Tickmill)","value":-5.8},{"label":"Nikkei (NordFX)","value":-6.14},{"label":"Kospi, al saltar el freno (Herald)","value":-8.19,"hl":True},{"label":"Kospi, cierre (NordFX)","value":-6.06}],
   "source":"Herald Corp, Tickmill y NordFX. Pueden medir momentos distintos de la sesión"}},
"eco-nfp": {
 "why": "El dato de empleo ayuda a la Reserva Federal a decidir si sube o baja los tipos, y eso afecta a los mercados de todo el mundo.",
 "terms": [{"t":"Nóminas no agrícolas","d":"Los empleos creados en EE. UU. en un mes, sin contar el campo."},{"t":"Consenso","d":"La media de lo que esperan los analistas."}],
 "visual": {"type":"bars","title":"Empleos creados en EE. UU., en miles","unit":" mil",
   "items":[{"label":"Mes anterior (dato)","value":29},{"label":"Octubre (lo que se espera)","value":65,"dim":True}],
   "source":"The Rio Times e IC Markets. El dato real se publica hoy"}},
"tec-datacenters": {
 "why": "Los centros de datos de IA gastan mucha electricidad y agua. Que los vecinos los frenen en las urnas puede retrasar la expansión de la IA.",
 "terms": [{"t":"Centro de datos","d":"Edificio lleno de servidores donde funcionan los servicios de internet y la inteligencia artificial."}],
 "visual": {"type":"stat","title":"Las consultas en cifras","items":[{"value":"41","label":"consultas locales en 10 estados el 3 nov."},{"value":"21","label":"de ellas en Ohio"},{"value":"21 de 21","label":"rechazadas en Ohio, según AI Weekly (sin confirmar)","dim":True}],
   "source":"Smart Cities Dive (Ballotpedia) y AI Weekly"}},
"tec-chips-ue": {
 "why": "Europa depende de otros países para diseñar chips. Este dinero busca que surjan empresas europeas en ese segmento.",
 "terms": [{"t":"Ley Europea de Chips","d":"Plan de la UE para producir y diseñar más semiconductores dentro de Europa."}],
 "visual": {"type":"stat","title":"En cifras","items":[{"value":"525 M€","label":"para startups de diseño de chips"},{"value":"menos del 1%","label":"de los ingresos mundiales del segmento son de empresas europeas"}],
   "source":"Euronews (una sola fuente)"}},
"dep-espana": {
 "why": "Son los dos últimos partidos de la fase de grupos de la Liga de Naciones, con España e Inglaterra en el mismo grupo.",
 "terms": [{"t":"Liga de Naciones","d":"Competición de selecciones europeas de la UEFA que se juega entre torneos."}],
 "visual": {"type":"timeline","title":"La agenda de la selección","items":[{"date":"6 nov.","label":"Lista de convocados, 11:30","hl":True},{"date":"12 nov.","label":"República Checa y España, en Praga"},{"date":"15 nov.","label":"España e Inglaterra, en el Metropolitano"}],
   "source":"Flashscore y EFE"}},
"dep-cr7": {
 "why": "Ronaldo es el máximo goleador de la historia del fútbol de selecciones. Su salida cerraría una etapa de más de veinte años.",
 "terms": [],
 "visual": {"type":"claims","title":"Quién dice qué","items":[
   {"who":"Anadolu","says":"Anunció que dejará la selección tras los partidos de noviembre.","ok":"una"},
   {"who":"El propio Ronaldo (30 sept., vía beIN)","says":"Descartó retirarse de la selección.","ok":"una"},
   {"who":"Federación Portuguesa","says":"No he encontrado confirmación.","ok":"no"}],
   "source":"Anadolu, beIN Sports y Emol (AFP)"}},
}
for s in d["stories"]:
    s.update(V[s["id"]])
d["generated"] = "2026-11-06T13:05:00Z"
txt = json.dumps(d, ensure_ascii=False)
assert "–" not in txt and "—" not in txt
json.dump(d, open('edition-v5.json','w'), ensure_ascii=False, indent=1)
print("ok", len(d["stories"]))
