import os
import requests
from flask import Flask, Response, request, redirect, render_template_string, jsonify

app = Flask(__name__)

# Tu enlace real de GitHub listo para producción
URL_LISTA_GITHUB = "https://appsstudios-oficial.github.io/list/list.m3u"

# --- CREDENCIALES DE ACCESO ---
USUARIO_VALIDO = "vip2026"
CLAVE_VALIDA = "9876"

# --- TU LANDING PAGE ---
HTML_INDEX = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Seguro</title>
    <style>
        body { margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #111424 0%, #311432 100%); font-family: sans-serif; color: white; text-align: center; }
        .contenedor { background: rgba(255, 255, 255, 0.08); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); width: 80%; max-width: 500px; }
        #contador { font-size: 5rem; display: block; margin: 20px 0; color: #00ffaa; }
        .enlace { display: block; margin-top: 20px; padding: 15px; background: #fff; color: #333; text-decoration: none; border-radius: 10px; font-weight: bold; cursor: pointer; word-break: break-all; }
    </style>
</head>
<body>
    <div class="contenedor">
        <div id="pantalla"><p>Generando acceso privado en...</p><span id="contador">5</span></div>
        <div id="contenido" style="display:none;">
            <h2>Tu enlace de acceso privado:</h2>
            <div class="enlace" id="url-lista" onclick="navigator.clipboard.writeText(this.innerText); alert('¡Copiado!');">{{ link_protegido }}</div>
        </div>
    </div>
    <script>
        var seg = 5; var elContador = document.getElementById('contador');
        var intervalo = setInterval(function() { seg--; elContador.innerHTML = seg; if (seg <= 0) { clearInterval(intervalo); document.getElementById('pantalla').style.display = 'none'; document.getElementById('contenido').style.display = 'block'; } }, 1000);
    </script>
</body>
</html>
"""

def parsear_m3u_a_xtream():
    """Función interna para convertir tu M3U en formato de canales para las Apps"""
    try:
        respuesta = requests.get(URL_LISTA_GITHUB, timeout=10)
        if respuesta.status_code != 200:
            return [], []
        
        lineas = respuesta.text.splitlines()
        canales = []
        categorias = set()
        
        info_canal = {}
        id_canal = 1
        
        for linea in lineas:
            linea = linea.strip()
            if linea.startswith("#EXTINF:"):
                # Intentamos extraer el nombre del canal y la categoría
                info_canal = {"num": id_canal, "category_id": "1", "stream_type": "live"}
                nombre = linea.split(",")[-1] if "," in linea else f"Canal {id_canal}"
                info_canal["name"] = nombre
                
                # Buscar categoría si existe en el tag group-title
                if 'group-title="' in linea:
                    cat = linea.split('group-title="')[1].split('"')[0]
                    categorias.add(cat)
                    info_canal["category_name"] = cat
                else:
                    categorias.add("General")
                    info_canal["category_name"] = "General"
                    
            elif linea.startswith("http://") or linea.startswith("https://"):
                if info_canal:
                    info_canal["url"] = linea
                    info_canal["stream_id"] = id_canal
                    canales.append(info_canal)
                    id_canal += 1
                    info_canal = {}
                    
        # Formatear las categorías para la app
        cats_json = [{"category_id": str(i+1), "category_name": cat, "parent_id": 0} for i, cat in enumerate(categorias)]
        
        # Mapear los canales a su ID de categoría correspondiente
        for canal in canales:
            for i, cat in enumerate(categorias):
                if canal.get("category_name") == cat:
                    canal["category_id"] = str(i+1)
                    
        return cats_json, canales
    except:
        return [], []

@app.route('/')
def inicio():
    host_actual = request.host_url.rstrip('/')
    link_final = f"{host_actual}/get.php?username={USUARIO_VALIDO}&password={CLAVE_VALIDA}"
    return render_template_string(HTML_INDEX, link_protegido=link_final)

@app.route('/get.php')
def obtener_lista_directa():
    user = request.args.get('username')
    password = request.args.get('password')
    
    if user != USUARIO_VALIDO or password != CLAVE_VALIDA:
        return "Acceso denegado", 403

    user_agent = request.headers.get('User-Agent', '').lower()
    navegadores_web = ['chrome', 'firefox', 'safari', 'brave', 'opera']
    if any(nav in user_agent for nav in navegadores_web):
        return redirect("/", code=302)

    try:
        respuesta = requests.get(URL_LISTA_GITHUB, timeout=10)
        return Response(respuesta.text, mimetype='application/x-mpegurl')
    except:
        return "Error interno", 500

@app.route('/player_api.php')
def api_xtream_codes():
    user = request.args.get('username')
    password = request.args.get('password')
    action = request.args.get('action')

    if user != USUARIO_VALIDO or password != CLAVE_VALIDA:
        return jsonify({"user_info": {"auth": 0}}), 403

    if not action:
        return jsonify({
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": user,
                "password": password,
                "expiry_date": "1798761600",
                "is_trial": "0",
                "active_cons": "1",
                "max_connections": "5"
            },
            "server_info": {"url": request.host, "port": "80", "server_protocol": "http"}
        })
    
    cats, canales = parsear_m3u_a_xtream()
    
    if action == "get_live_categories":
        return jsonify(cats)
        
    if action == "get_live_streams":
        # Formateamos la respuesta de canales que exige la API Xtream
        streams = []
        for c in canales:
            streams.append({
                "num": c["num"],
                "name": c["name"],
                "stream_type": "live",
                "stream_id": c["stream_id"],
                "stream_icon": "",
                "epg_channel_id": None,
                "added": "1625443200",
                "category_id": c["category_id"],
                "custom_sid": "",
                "tv_archive": 0,
                "direct_source": c["url"],
                "tv_archive_duration": 0
            })
        return jsonify(streams)
        
    return jsonify([])

# Esta ruta ataja la reproducción directa cuando la app pide el stream por ID
@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def reproducir_stream_xtream(username, password, stream_id):
    if username != USUARIO_VALIDO or password != CLAVE_VALIDA:
        return "No autorizado", 403
    
    _, canales = parsear_m3u_a_xtream()
    for c in canales:
        if c["stream_id"] == stream_id:
            return redirect(c["url"], code=302)
            
    return "Canal no encontrado", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
