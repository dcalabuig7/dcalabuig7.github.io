import json, re, sys

# Fichas de medios. "lean" usa: izq, cizq, centro, cder, der, oficial, empresa, nd (sin valoración).
# "rating" solo recoge valoraciones encontradas en AllSides / Media Bias Fact Check (MBFC) / Ad Fontes.
OUT = {
 "boe":   {"name":"Bank of England","lean":"oficial","about":"Banco central del Reino Unido. Es la fuente oficial primaria de la decisión de tipos.","rating":""},
 "caixa": {"name":"CaixaBank Research","lean":"empresa","about":"Servicio de análisis económico del banco español CaixaBank. Es análisis de mercado, no periodismo.","rating":""},
 "cpa":   {"name":"CPA","lean":"empresa","about":"Blog de una empresa británica que se dirige a pymes que venden a crédito, según su propio texto. No es un medio de comunicación.","rating":""},
 "tickmill":{"name":"Tickmill","lean":"empresa","about":"Bróker de divisas y CFD. Sus notas de mercado tienen fin comercial.","rating":""},
 "efe":   {"name":"Agencia EFE","lean":"centro","about":"Agencia de noticias pública española, propiedad de la SEPI (Estado).","rating":"MBFC: menos sesgado, fiabilidad alta"},
 "infobae":{"name":"Infobae","lean":"cizq","about":"Diario digital argentino. Aquí republica despachos de EFE, así que la fuente real es EFE.","rating":"MBFC: centro izquierda, fiabilidad alta"},
 "elespanol":{"name":"El Español","lean":"cder","about":"Diario digital español fundado en 2015 por Pedro J. Ramírez.","rating":"MBFC: centro derecha"},
 "unotv": {"name":"Uno TV","lean":"nd","about":"Medio digital mexicano. Aquí reproduce información de AFP.","rating":""},
 "euronews":{"name":"Euronews","lean":"cizq","about":"Canal y web paneuropeos con sede en Francia. Ha recibido subvenciones de la UE, según MBFC.","rating":"MBFC: centro izquierda, mayormente fiable. AllSides: centro (confianza baja)"},
 "dtarragona":{"name":"Diari de Tarragona","lean":"nd","about":"Diario regional catalán.","rating":""},
 "dsur":  {"name":"Diario del Sur","lean":"nd","about":"Diario regional colombiano.","rating":""},
 "democrata":{"name":"Demócrata","lean":"nd","about":"Medio digital español especializado en política e instituciones.","rating":""},
 "xataka":{"name":"Xataka","lean":"nd","about":"Web española de tecnología.","rating":""},
 "moncloa":{"name":"Moncloa.com","lean":"nd","about":"Medio digital privado. No es la web oficial del Gobierno, aunque el nombre lo sugiera.","rating":""},
 "art14": {"name":"Artículo 14","lean":"nd","about":"Diario digital español.","rating":""},
 "publico":{"name":"Público","lean":"cizq","about":"Diario digital español fundado en 2007. Aquí solo se ha visto el titular a través de un agregador.","rating":"MBFC: centro izquierda, fiabilidad alta"},
 "wikifarmer":{"name":"Wikifarmer","lean":"nd","about":"Plataforma de información agrícola. El cálculo del 12% es suyo, hecho con datos del Ministerio.","rating":""},
 "cnmc":  {"name":"CNMC","lean":"oficial","about":"Comisión Nacional de los Mercados y la Competencia, el regulador español.","rating":""},
 "ap":    {"name":"AP (vía PBS)","lean":"centro","about":"Agencia de noticias estadounidense, aquí publicada por la televisión pública PBS. AP es quien da por ganadas las elecciones en EE. UU.","rating":"AllSides: centro para AP, con encuestas que lo situaron a veces en centro izquierda"},
 "npr":   {"name":"NPR","lean":"cizq","about":"Radio pública estadounidense sin ánimo de lucro.","rating":"AllSides: entre centro y centro izquierda según la encuesta"},
 "time":  {"name":"Time","lean":"cizq","about":"Revista estadounidense de actualidad.","rating":"AllSides: centro izquierda (encuesta de 2023)"},
 "cnn":   {"name":"CNN","lean":"cizq","about":"Cadena de noticias estadounidense.","rating":"AllSides: centro izquierda (web)"},
 "anadolu":{"name":"Anadolu","lean":"der","about":"Agencia estatal de Turquía. En temas de Oriente Próximo conviene contrastarla.","rating":"MBFC: derecha, fiabilidad mixta, progubernamental. AllSides: centro (revisión inicial de 2026)"},
 "oman":  {"name":"Oman Observer","lean":"nd","about":"Diario omaní en inglés. Aquí cita al portavoz del Gobierno iraní.","rating":""},
 "rmc":   {"name":"Religion Media Centre","lean":"nd","about":"Organización británica que informa sobre religión.","rating":""},
 "ic":    {"name":"IC Markets","lean":"empresa","about":"Bróker de divisas y CFD. Sus notas de mercado tienen fin comercial.","rating":""},
 "nordfx":{"name":"NordFX","lean":"empresa","about":"Bróker de divisas. Sus notas de mercado tienen fin comercial.","rating":""},
 "riotimes":{"name":"The Rio Times","lean":"nd","about":"Medio en inglés centrado en Brasil y Latinoamérica.","rating":""},
 "herald":{"name":"Herald Corp","lean":"nd","about":"Grupo de prensa surcoreano.","rating":""},
 "nst":   {"name":"New Straits Times","lean":"nd","about":"Diario malasio en inglés.","rating":""},
 "aiweekly":{"name":"AI Weekly","lean":"nd","about":"Boletín que recopila noticias de inteligencia artificial. No hace información propia.","rating":""},
 "techstartups":{"name":"Tech Startups","lean":"nd","about":"Blog de noticias de tecnología y startups.","rating":""},
 "scd":   {"name":"Smart Cities Dive","lean":"nd","about":"Publicación especializada en gestión urbana e infraestructuras.","rating":""},
 "spg":   {"name":"S&P Global","lean":"empresa","about":"Empresa de datos y análisis financiero.","rating":""},
 "flashscore":{"name":"Flashscore","lean":"nd","about":"Web de resultados y noticias deportivas.","rating":""},
 "bein":  {"name":"beIN Sports","lean":"nd","about":"Cadena deportiva del grupo catarí beIN Media.","rating":""},
 "emol":  {"name":"Emol","lean":"nd","about":"Web del diario chileno El Mercurio. Aquí reproduce información de AFP.","rating":""},
 "fichajes":{"name":"Fichajes.com","lean":"nd","about":"Web de rumores y noticias de fútbol.","rating":""},
}
MATCH = [("bankofengland","boe"),("caixabank","caixa"),("cpa.co.uk","cpa"),("tickmill","tickmill"),("infobae","infobae"),
 ("elespanol","elespanol"),("unotv","unotv"),("euronews","euronews"),("diaridetarragona","dtarragona"),("diariodelsur","dsur"),
 ("democrata","democrata"),("xataka","xataka"),("moncloa.com","moncloa"),("articulo14","art14"),("headtopics","publico"),
 ("wikifarmer","wikifarmer"),("cnmc","cnmc"),("pbs.org","ap"),("npr.org","npr"),("time.com","time"),("cnn.com","cnn"),
 ("aa.com.tr","anadolu"),("omanobserver","oman"),("religionmediacentre","rmc"),("ic.com","ic"),("nordfx","nordfx"),
 ("riotimes","riotimes"),("heraldcorp","herald"),("nst.com.my","nst"),("aiweekly","aiweekly"),("techstartups","techstartups"),
 ("smartcitiesdive","scd"),("spglobal","spg"),("flashscore","flashscore"),("beinsports","bein"),("emol.com","emol"),("fichajes","fichajes")]

def nodash(s):
    if not isinstance(s,str): return s
    s = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 a \2", s)   # rangos 13–27 -> 13 a 27
    s = s.replace(" – ", ": ").replace(" — ", ", ").replace("–","-").replace("—","-").replace("−","-")
    return s

def walk(o):
    if isinstance(o,dict): return {k:walk(v) for k,v in o.items()}
    if isinstance(o,list): return [walk(v) for v in o]
    return nodash(o)

src = json.load(open(sys.argv[1]))
d = walk(src)
for s in d["stories"]:
    for x in s["sources"]:
        u = x["url"]
        key = next((k for m,k in MATCH if m in u), None)
        if "infobae" in u: key = "efe" if "efe" in x["name"].lower() else "infobae"
        if key:
            o = OUT[key]; x["outlet"]=o["name"]; x["lean"]=o["lean"]; x["about"]=o["about"]; x["rating"]=o["rating"]
        else:
            print("SIN FICHA:", x["name"], u)
d["note"] = "Verificación por cruce de fuentes independientes. La tendencia de cada medio viene de AllSides o Media Bias Fact Check cuando existe; si no, se indica."
bad = [c for c in json.dumps(d,ensure_ascii=False) if c in "–—"]
assert not bad, bad
json.dump(d, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
print("ok", sum(len(s["sources"]) for s in d["stories"]), "fuentes")
