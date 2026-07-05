import os
import requests
from flask import Flask, Response, request, redirect, render_template_string

app = Flask(__name__)

# Tu enlace real de GitHub listo para producción
URL_LISTA_GITHUB = "https://appsstudios-oficial.github.io/list/list.m3u"

# --- CREDENCIALES DE ACCESO (Podés cambiarlas cuando quieras) ---
USUARIO_VALIDO = "vip2026"
CLAVE_VALIDA = "9876"

# --- TU LANDING PAGE DIRECTA DESDE RENDER ---
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

@app.route('/')
def inicio():
    """Muestra la Landing Page con el formato estructurado de credenciales"""
    host_actual = request.host_url.rstrip('/')
    link_final = f"{host_actual}/get.php?username={USUARIO_VALIDO}&password={CLAVE_VALIDA}"
    return render_template_string(HTML_INDEX, link_protegido=link_final)

@app.route('/get.php')
def obtener_lista_directa():
    user = request.args.get('username')
    password = request.args.get('password')
    
    # Validación de usuario y contraseña
    if user != USUARIO_VALIDO or password != CLAVE_VALIDA:
        return "Acceso denegado: Credenciales inválidas", 403

    # Bloqueo estricto de navegadores comunes
    user_agent = request.headers.get('User-Agent', '').lower()
    navegadores_web = ['chrome', 'firefox', 'safari', 'brave', 'opera']
    if any(nav in user_agent for nav in navegadores_web):
        return redirect("/", code=302)

    try:
        # Descarga la lista tal cual está en tu GitHub (con enlaces directos)
        respuesta = requests.get(URL_LISTA_GITHUB, timeout=10)
        if respuesta.status_code != 200:
            return "Error al conectar con la base de datos externa", 500
        
        # Le entrega el contenido limpio a las aplicaciones (SSIPTV, IPTV Smarters, etc.)
        return Response(respuesta.text, mimetype='application/x-mpegurl')
        
    except Exception as e:
        return "Error interno del servidor", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
