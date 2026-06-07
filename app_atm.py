import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io
import re

# Configuración de la página en formato centrado para evitar que se desparrame en el iPad
st.set_page_config(page_title="Informe Ecográfico ATM", layout="centered")

# Estilos visuales limpios y ordenados en vertical para tablets
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; margin-bottom: 25px; }
    .seccion-card { background-color: #FFFFFF; padding: 25px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .titulo-seccion { color: #0284C7; font-size: 20px; font-weight: bold; border-bottom: 2px solid #0284C7; padding-bottom: 6px; margin-bottom: 20px; text-transform: uppercase; }
    .sub-bloque { font-weight: bold; color: #1E3A8A; margin-top: 15px; margin-bottom: 5px; font-size: 15px; }
    .resultado-calculo { background-color: #F0F9FF; padding: 12px; border-radius: 6px; border-left: 5px solid #0284C7; margin-top: 15px; font-size: 15px; color: #1E3A8A !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico ATM</h1>", unsafe_allow_html=True)

# --- RECEPTOR DE DICTADO POR VOZ ---
def componente_microfono_visible(lado_id):
    js_code = f"""
    <div style="font-family: sans-serif; display: flex; flex-direction: column; gap: 4px;">
        <div style="display: flex; gap: 8px; align-items: center;">
            <button id="btn_{lado_id}" class="btn-voz btn-azul" onclick="conmutarMicro('{lado_id}')" style="flex-shrink: 0;">🎙️ Dictar 3 Números</button>
            <input type="text" id="output_local_{lado_id}" placeholder="Esperando medidas por voz..." readonly 
                   style="flex-grow: 1; padding: 6px; font-size: 14px; font-weight: bold; border: 2px solid #0284C7; border-radius: 4px; background-color: #FFFFFF; color: #000000; text-align: center;">
        </div>
        <p id="status_{lado_id}" style="font-size:11px; color:#666; margin: 1px 0 0 2px; height: 14px; overflow: hidden;">Listo</p>
    </div>

    <script>
    let recognition_{lado_id} = null;
    let activo_{lado_id} = false;

    function enviarAStreamlit(textoNumeros) {{
        if (window.Streamlit) {{
            Streamlit.setComponentValue(textoNumeros);
        }}
    }}

    function conmutarMicro(lado) {{
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);
        const inputLocal = document.getElementById('output_local_' + lado);

        if (activo_{lado_id}) {{
            if (recognition_{lado_id}) recognition_{lado_id}.abort();
            resetearBoton(lado, "🛑 Cancelado.");
            return;
        }}

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.innerText = "No compatible.";
            return;
        }}

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition_{lado_id} = new SpeechRecognition();
        recognition_{lado_id}.lang = 'es-ES';
        recognition_{lado_id}.interimResults = false;

        activo_{lado_id} = true;
        btn.innerText = "🛑 Parar";
        btn.className = "btn-voz btn-rojo";
        status.innerText = "🎙️ Escuchando... Di los 3 números";
        status.style.color = "#0284C7";

        recognition_{lado_id}.start();

        recognition_{lado_id}.onresult = function(event) {{
            const texto = event.results[0][0].transcript;
            const matches = texto.replace(/,/g, '.').match(/[0-9]+(\\.[0-9]+)?/g);
            
            if (matches && matches.length >= 3) {{
                const resultadoCadena = matches[0] + " , " + matches[1] + " , " + matches[2];
                inputLocal.value = resultadoCadena;
                status.innerText = "✓ Capturadas.";
                status.style.color = "#16A34A";
                enviarAStreamlit(resultadoCadena);
            }} else {{
                status.innerText = "❌ Reintenta.";
                status.style.color = "#DC2626";
            }}
        }};

        recognition_{lado_id}.onerror = function(e) {{ resetearBoton(lado, "Reintenta."); }};
        recognition_{lado_id}.onend = function() {{ resetearBoton(lado, status.innerText); }};
    }}

    function resetearBoton(lado, msg) {{
        activo_{lado_id} = false;
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);
        btn.innerText = "🎙️ Dictar 3 Números";
        btn.className = "btn-voz btn-azul";
        if(msg) status.innerText = msg;
    }}

    (function() {{
        var stScript = document.createElement('script');
        stScript.src = "https://cdn.jsdelivr.net/npm/@streamlit/component-lib@1.4.0/dist/index.min.js";
        stScript.onload = function() {{ window.addEventListener('load', function() {{ Streamlit.setFrameHeight(60); }}); }};
        document.head.appendChild(stScript);
    }})();
    </script>

    <style>
    .btn-voz {{ border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px; height: 32px; }}
    .btn-azul {{ background-color: #0284C7; color: white; }}
    .btn-rojo {{ background-color: #DC2626; color: white; }}
    </style>
    """
    return components.html(js_code, height=60, scrolling=False)

# --- PROCESADORES INTERNOS ---
def procesar_medidas_sistema(texto_dictado, manual_as, manual_lat, manual_pi):
    if texto_dictado and isinstance(texto_dictado, str) and len(texto_dictado.strip()) > 0:
        numeros = re.findall(r"[0-9]+(?:\.[0-9]+)?", texto_dictado)
        if len(numeros) >= 3:
            return numeros[0], numeros[1], numeros[2]
    return manual_as, manual_lat, manual_pi

def calcular_posicion_condilo(ant_sup_txt, post_inf_txt):
    try:
        if not ant_sup_txt or not post_inf_txt: return "0.00"
        as_val = float(str(ant_sup_txt).replace(',', '.'))
        pi_val = float(str(post_inf_txt).replace(',', '.'))
        if (pi_val + as_val) == 0: return "0.00"
        resultado = ((pi_val - as_val) / (pi_val + as_val)) * 100
        return f"{'+' if resultado > 0 else ''}{resultado:.2f}"
    except ValueError:
        return "0.00"

# --- OPCIONES DE LOS MENÚS DESPLEGABLES ---
opts_morfologia = [
    "aplanado, irregular.", 
    "irregular, estrecho, con cresta lateral.",
    "redondeado, regular.", 
    "en pico de pájaro."
]
opts_espacio = [
    "con osteofitos. Engrosamiento sinovial superior.",
    "con osteofitos.",
    "libre, sin hallazgos patológicos.",
    "con engrosamiento sinovial y presencia de derrame articular."
]
opts_derrame = [
    "Presencia de derrame articular.",
    "Sin presencia de derrame articular."
]
opts_ecoestructura = ["Ecoestructura hipoecogénico.", "Ecoestructura homogénea.", "Ecoestructura heterogénea."]
opts_horas = ["hora 11", "hora 12", "hora 10", "hora 1"]
opts_relacion = ["Cóndilo en posición anterior.", "Cóndilo en posición central.", "Cóndilo en posición posterior."]
opts_cerrada = [
    "en hora 11 cubre parcialmente la cabeza del cóndilo.",
    "cubre totalmente la cabeza del cóndilo.",
    "desplazamiento, no cubre la cabeza condilar."
]
opts_abierta = [
    "desplazamiento anterior cubre la porción anterior de la cabeza condilar durante la apertura bucal, resto del cóndilo contacta con la cavidad glenoidea.",
    "desplazamiento discal normal, cubre por completo la cabeza del cóndilo."
]

# --- CASILLA: MOTIVO ---
st.markdown("<div class='seccion-card'>", unsafe_allow_html=True)
motivo = st.text_input("Motivo de consulta:", value="Dolor ATM bilateral.")
st.markdown("</div>", unsafe_allow_html=True)

# --- ESTUDIO ATM DERECHA ---
st.markdown("<div class='seccion-card'>", unsafe_allow_html=True)
st.markdown("<div class='titulo-seccion'>Estudio Articulación Temporomandibular Derecha</div>", unsafe_allow_html=True)

morf_der = st.selectbox("Morfología cabeza condilar (D):", opts_morfologia, index=0, key="s_m_der")
esp_der = st.selectbox("Espacio articular (D):", opts_espacio, index=0, key="s_e_der")
derrame_der = st.selectbox("Presencia de derrame (D):", opts_derrame, index=0, key="s_d_der")

st.markdown("<div class='sub-bloque'>Medidas del Cóndilo Derecho (mm):</div>", unsafe_allow_html=True)
dictado_der = componente_microfono_visible("der")
md1, md2, md3 = st.columns(3)
with md1: manual_as_der = st.text_input("Anterosuperior (D)", value="1.98", key="n_as_der")
with md2: manual_lat_der = st.text_input("Lateral (D)", value="1.65", key="n_la_der")
with md3: manual_pi_der = st.text_input("Posteroinferior (D)", value="2.84", key="n_pi_der")

med_as_der, med_lat_der, med_pi_der = procesar_medidas_sistema(dictado_der, manual_as_der, manual_lat_der, manual_pi_der)
res_der = calcular_posicion_condilo(med_as_der, med_pi_der)
st.markdown(f"<div class='resultado-calculo'>🧮 Índice de Pullinger (D): {res_der}%</div>", unsafe_allow_html=True)

st.markdown("<div class='sub-bloque'>Disco Articular Derecho:</div>", unsafe_allow_html=True)
eco_der = st.selectbox("Ecoestructura (D):", opts_ecoestructura, index=0, key="s_ec_der")
hora_der = st.selectbox("Situación (D):", opts_horas, index=0, key="s_h_der")
rel_der = st.selectbox("Relación cóndilo-fosa (D):", opts_relacion, index=0, key="s_r_der")

st.markdown("<div class='sub-bloque'>Estudio Dinámico Derecho:</div>", unsafe_allow_html=True)
c_der = st.selectbox("Boca cerrada (D):", opts_cerrada, index=0, key="s_c_der")
a_der = st.selectbox("Boca abierta (D):", opts_abierta, index=0, key="s_a_der")
st.markdown("</div>", unsafe_allow_html=True)

# --- ESTUDIO ATM IZQUIERDA ---
st.markdown("<div class='seccion-card'>", unsafe_allow_html=True)
st.markdown("<div class='titulo-seccion'>Estudio Articulación Temporomandibular Izquierda</div>", unsafe_allow_html=True)

morf_izq = st.selectbox("Morfología cabeza condilar (I):", opts_morfologia, index=1, key="s_m_izq")
esp_izq = st.selectbox("Espacio articular (I):", opts_espacio, index=1, key="s_e_izq")
derrame_izq = st.selectbox("Presencia de derrame (I):", opts_derrame, index=0, key="s_d_izq")

st.markdown("<div class='sub-bloque'>Medidas del Cóndilo Izquierdo (mm):</div>", unsafe_allow_html=True)
dictado_izq = componente_microfono_visible("izq")
mi1, mi2, mi3 = st.columns(3)
with mi1: manual_as_izq = st.text_input("Anterosuperior (I)", value="2.37", key="n_as_izq")
with mi2: manual_lat_izq = st.text_input("Lateral (I)", value="1.14", key="n_la_izq")
with mi3: manual_pi_izq = st.text_input("Posteroinferior (I)", value="2.92", key="n_pi_izq")

med_as_izq, med_lat_izq, med_pi_izq = procesar_medidas_sistema(dictado_izq, manual_as_izq, manual_lat_izq, manual_pi_izq)
res_izq = calcular_posicion_condilo(med_as_izq, med_pi_izq)
st.markdown(f"<div class='resultado-calculo'>🧮 Índice de Pullinger (I): {res_izq}%</div>", unsafe_allow_html=True)

st.markdown("<div class='sub-bloque'>Disco Articular Izquierdo:</div>", unsafe_allow_html=True)
eco_izq = st.selectbox("Ecoestructura (I):", opts_ecoestructura, index=0, key="s_ec_izq")
hora_izq = st.selectbox("Situación (I):", opts_horas, index=0, key="s_h_izq")
rel_izq = st.selectbox("Relación cóndilo-fosa (I):", opts_relacion, index=1, key="s_r_izq")

st.markdown("<div class='sub-bloque'>Estudio Dinámico Izquierdo:</div>", unsafe_allow_html=True)
c_izq = st.selectbox("Boca cerrada (I):", opts_cerrada, index=0, key="s_c_izq")
a_izq = st.selectbox("Boca abierta (I):", opts_abierta, index=0, key="s_a_izq")
st.markdown("</div>", unsafe_allow_html=True)

# --- CONCLUSIÓN ---
st.markdown("<div class='seccion-card'>", unsafe_allow_html=True)
conclusion = st.text_area("📝 CONCLUSIÓN:", value="Signos ecográficos compatibles con...")
st.markdown("</div>", unsafe_allow_html=True)

# --- ENLAZAR CON EL ARCHIVO WORD ---
if st.button("🚀 PREPARAR INFORME EN WORD"):
    try:
        doc = DocxTemplate("plantilla_atm.docx")
        
        contexto = {
            'motivo': motivo,
            
            # Construcción de frases del lado Derecho igual que tu ejemplo
            'condilo_der': f"{morf_der}",
            'espacio_der': f"{esp_der}",
            'medidas_der': f"Medidas anterosuperior: {med_as_der} mm. Lateral: {med_lat_der} mm. Posteroinferior: {med_pi_der} mm. {derrame_der} (Índice Pullinger: {res_der}%)",
            'disco_der': f"{eco_der} Situación en {hora_der}.",
            'relacion_der': f"{rel_der}",
            'cerrada_der': f"Boca cerrada: en {hora_der} {c_der}",
            'abierta_der': f"Boca abierta: {a_der}",
            
            # Construcción de frases del lado Izquierdo igual que tu ejemplo
            'condilo_izq': f"{morf_izq}",
            'espacio_izq': f"{esp_izq}",
            'medidas_izq': f"Medidas Anterosuperior: {med_as_izq} mm. Lateral: {med_lat_izq} mm. Posteroinferior: {med_pi_izq} mm. {derrame_izq} (Índice Pullinger: {res_izq}%)",
            'disco_izq': f"{eco_izq} Situado en {hora_izq}.",
            'relacion_izq': f"{rel_izq}",
            'cerrada_izq': f"Boca cerrada: en {hora_izq} {c_izq}",
            'abierta_izq': f"Boca abierta: {a_izq}",
            
            'conclusion': conclusion
        }
        
        doc.render(contexto)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.download_button(
            label="⬇️ DESCARGAR DOCUMENTO WORD COMPLETO",
            data=bio,
            file_name="Informe_ATM.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.success("¡Hecho! Pulsa el botón de arriba para descargar.")
    except Exception as e:
        st.error(f"Error al procesar la plantilla de Word: {e}")
