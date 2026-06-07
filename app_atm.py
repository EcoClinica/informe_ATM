import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io
import re

# Configuración de pantalla ancha para visualización en paralelo (Ideal para iPad en horizontal)
st.set_page_config(page_title="Informe Ecográfico ATM", layout="wide")

# Estilos CSS Profesionales para la interfaz web
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-titulo { text-align: center; color: #475569; font-size: 14px; margin-bottom: 25px; }
    .titulo-lado { color: #0284C7; font-size: 18px; font-weight: bold; border-bottom: 2px solid #0284C7; padding-bottom: 6px; margin-bottom: 15px; text-transform: uppercase; }
    .sub-bloque { font-weight: bold; color: #1E3A8A; margin-top: 10px; margin-bottom: 5px; font-size: 14px; }
    .resultado-calculo { background-color: #E0F2FE; padding: 10px; border-radius: 4px; border-left: 4px solid #0284C7; margin-top: 10px; font-size: 14px; color: #1E3A8A !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico de la Articulación Temporomandibular (ATM)</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-titulo'>Protocolo de adquisición ecográfica en posición de boca abierta y cerrada</p>", unsafe_allow_html=True)

# --- RECEPTOR DE DICTADO POR VOZ (CAJA BLANCA) ---
def componente_microfono_visible(lado_id):
    js_code = f"""
    <div style="font-family: sans-serif; display: flex; flex-direction: column; gap: 4px;">
        <div style="display: flex; gap: 8px; align-items: center;">
            <button id="btn_{lado_id}" class="btn-voz btn-azul" onclick="conmutarMicro('{lado_id}')" style="flex-shrink: 0;">🎙️ Dictar 3 Medidas</button>
            <input type="text" id="output_local_{lado_id}" placeholder="Esperando dictado..." readonly 
                   style="flex-grow: 1; padding: 6px; font-size: 14px; font-weight: bold; border: 2px solid #0284C7; border-radius: 4px; background-color: #FFFFFF; color: #000000; text-align: center;">
        </div>
        <p id="status_{lado_id}" style="font-size:11px; color:#666; margin: 1px 0 0 2px; height: 14px; overflow: hidden;">Listo</p>
    </div>

    <script>
    let recognition_{lado_id} = null;
    let activo_{lado_id} = false;

    function enviarAStreamlit(textoNumeros) {{
        if (window.Streamlit) {{ Streamlit.setComponentValue(textoNumeros); }}
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
        status.innerText = "🎙️ Escuchando...";

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

        recognition_{lado_id}.onerror = function() {{ resetearBoton(lado, "Reintenta."); }};
        recognition_{lado_id}.onend = function() {{ resetearBoton(lado, status.innerText); }};
    }}

    function resetearBoton(lado, msg) {{
        activo_{lado_id} = false;
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);
        btn.innerText = "🎙️ Dictar 3 Medidas";
        btn.className = "btn-voz btn-azul";
        if(msg) status.innerText = msg;
    }}
    </script>
    <style>
    .btn-voz {{ border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px; height: 32px; }}
    .btn-azul {{ background-color: #0284C7; color: white; }}
    .btn-rojo {{ background-color: #DC2626; color: white; }}
    </style>
    """
    return components.html(js_code, height=60, scrolling=False)

# --- PROCESADORES MATEMÁTICOS ---
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

# --- RECUPERACIÓN DE DATOS DEL PACIENTE ---
st.subheader("📋 Datos Generales del Paciente")
cp1, cp2, cp3, cp4 = st.columns(4)
with cp1:
    nombres = st.text_input("Nombres:", value="")
    apellidos = st.text_input("Apellidos:", value="")
with cp2:
    edad = st.text_input("Edad:")
    derivado = st.text_input("Paciente derivado por Dr/a:")
with cp3:
    fecha = st.date_input("Fecha de adquisición:", datetime.date.today(), format="DD/MM/YYYY")
    motivo = st.text_input("Motivo de consulta:", value="Dolor ATM bilateral.")
with cp4:
    antecedentes = st.text_input("Antecedentes relacionados:")
    tratamiento_act = st.text_input("Tratamiento actual:")

st.markdown("<br>", unsafe_allow_html=True)

# --- MENÚS DESPLEGABLES ASIGNADOS ---
opts_morfologia = ["aplanado, irregular", "irregular, estrecho, con cresta lateral", "redondeado, regular", "en pico de pájaro"]
opts_espacio = ["con osteofitos. Engrosamiento sinovial superior", "con osteofitos", "libre, sin hallazgos patológicos"]
opts_derrame = ["Presencia de derrame articular.", "Sin presencia de derrame articular."]
opts_ecoestructura = ["Ecoestructura hipoecogénico.", "Ecoestructura homogénea.", "Ecoestructura heterogénea."]
opts_horas = ["hora 11", "hora 12", "hora 10", "hora 1"]
opts_relacion = ["Cóndilo en posición anterior.", "Cóndilo en posición central.", "Cóndilo en posición posterior."]
opts_cerrada = ["en hora 11 cubre parcialmente la cabeza del cóndilo.", "cubre totalmente la cabeza del cóndilo.", "desplazamiento, no cubre la cabeza condilar."]
opts_abierta = ["desplazamiento anterior cubre la porción anterior de la cabeza condilar durante la apertura bucal, resto del cóndilo contacta con la cavidad glenoidea.", "desplazamiento discal normal, cubre por completo la cabeza del cóndilo."]

# --- VISTA EN PARALELO DE LAS DOS ARTICULACIONES ---
col_der, col_izq = st.columns(2, gap="large")

# --- ARTICULACIÓN DERECHA ---
with col_der:
    st.markdown("<div class='titulo-lado'>Estudio ATM Derecha</div>", unsafe_allow_html=True)
    
    morf_der = st.selectbox("Morfología cabeza condilar (D):", opts_morfologia, index=0, key="v_m_der")
    esp_der = st.selectbox("Espacio articular (D):", opts_espacio, index=0, key="v_e_der")
    derrame_der = st.selectbox("Derrame articular (D):", opts_derrame, index=0, key="v_d_der")
    
    st.markdown("<div class='sub-bloque'>Medidas del Cóndilo Derecho (mm):</div>", unsafe_allow_html=True)
    dictado_der = componente_microfono_visible("der")
    md1, md2, md3 = st.columns(3)
    with md1: manual_as_der = st.text_input("Antersup (D)", value="1.98", key="k_as_der")
    with md2: manual_lat_der = st.text_input("Lateral (D)", value="1.65", key="k_la_der")
    with md3: manual_pi_der = st.text_input("Postinf (D)", value="2.84", key="k_pi_der")
    
    med_as_der, med_lat_der, med_pi_der = procesar_medidas_sistema(dictado_der, manual_as_der, manual_lat_der, manual_pi_der)
    res_der = calcular_posicion_condilo(med_as_der, med_pi_der)
    st.markdown(f"<div class='resultado-calculo'>🧮 Índice Condilar (D): {res_der}%</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Disco Articular Derecho:</div>", unsafe_allow_html=True)
    eco_der = st.selectbox("Ecoestructura (D):", opts_ecoestructura, index=0, key="v_ec_der")
    hora_der = st.selectbox("Situación (D):", opts_horas, index=0, key="v_h_der")
    rel_der = st.selectbox("Relación cóndilo-fosa (D):", opts_relacion, index=0, key="v_r_der")
    
    st.markdown("<div class='sub-bloque'>Estudio Dinámico (D):</div>", unsafe_allow_html=True)
    c_der = st.selectbox("Boca cerrada (D):", opts_cerrada, index=0, key="v_c_der")
    a_der = st.selectbox("Boca abierta (D):", opts_abierta, index=0, key="v_a_der")

# --- ARTICULACIÓN IZQUIERDA ---
with col_izq:
    st.markdown("<div class='titulo-lado'>Estudio ATM Izquierda</div>", unsafe_allow_html=True)
    
    morf_izq = st.selectbox("Morfología cabeza condilar (I):", opts_morfologia, index=1, key="v_m_izq")
    esp_izq = st.selectbox("Espacio articular (I):", opts_espacio, index=1, key="v_e_izq")
    derrame_izq = st.selectbox("Derrame articular (I):", opts_derrame, index=0, key="v_d_izq")
    
    st.markdown("<div class='sub-bloque'>Medidas del Cóndilo Izquierdo (mm):</div>", unsafe_allow_html=True)
    dictado_izq = componente_microfono_visible("izq")
    mi1, mi2, mi3 = st.columns(3)
    with mi1: manual_as_izq = st.text_input("Antersup (I)", value="2.37", key="k_as_izq")
    with mi2: manual_lat_izq = st.text_input("Lateral (I)", value="1.14", key="k_la_izq")
    with mi3: manual_pi_izq = st.text_input("Postinf (I)", value="2.92", key="k_pi_izq")
    
    med_as_izq, med_lat_izq, med_pi_izq = procesar_medidas_sistema(dictado_izq, manual_as_izq, manual_lat_izq, manual_pi_izq)
    res_izq = calcular_posicion_condilo(med_as_izq, med_pi_izq)
    st.markdown(f"<div class='resultado-calculo'>🧮 Índice Condilar (I): {res_izq}%</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Disco Articular Izquierdo:</div>", unsafe_allow_html=True)
    eco_izq = st.selectbox("Ecoestructura (I):", opts_ecoestructura, index=0, key="v_ec_izq")
    hora_izq = st.selectbox("Situación (I):", opts_horas, index=0, key="v_h_izq")
    rel_izq = st.selectbox("Relación cóndilo-fosa (I):", opts_relacion, index=1, key="v_r_izq")
    
    st.markdown("<div class='sub-bloque'>Estudio Dinámico (I):</div>", unsafe_allow_html=True)
    c_izq = st.selectbox("Boca cerrada (I):", opts_cerrada, index=0, key="v_c_izq")
    a_izq = st.selectbox("Boca abierta (I):", opts_abierta, index=0, key="v_a_izq")

# --- CONCLUSIÓN ---
st.markdown("<br><hr>", unsafe_allow_html=True)
conclusion = st.text_area("📝 CONCLUSIÓN / OBSERVACIONES GENERALES:", value="Signos ecográficos compatibles con...")

# --- PROCESAMIENTO SEGURO DEL DOCUMENTO WORD ---
st.subheader("💾 Guardar y Exportar Informe")

if st.button("🚀 INYECTAR DATOS Y GENERAR INFORME"):
    try:
        doc = DocxTemplate("plantilla_atm.docx")
        
        # Mapeo exhaustivo de variables organizadas y pre-formateadas según tu modelo clínico
        contexto = {
            'nombres': nombres, 'apellidos': apellidos, 'edad': edad, 'derivado': derivado,
            'fecha': fecha.strftime("%d/%m/%Y") if fecha else "", 'motivo': motivo, 
            'antecedentes': antecedentes, 'tratamiento_act': tratamiento_act,
            
            # Bloque Derecho Formateado
            'condilo_der': f"morfología cabeza condilar {morf_der}.",
            'espacio_der': f"{esp_der}.",
            'medidas_der': f"Medidas anterosuperior: {med_as_der} mm. Lateral: {med_lat_der} mm. Posteroinferior: {med_pi_der} mm. \n{derrame_der} (Índice Condilar de Pullinger: {res_der}%)",
            'disco_der': f"{eco_der} Situación en {hora_der}.",
            'relacion_der': f"{rel_der}",
            'cerrada_der': f"Boca cerrada: en {hora_der} {c_der}",
            'abierta_der': f"Boca abierta: {a_der}",
            
            # Bloque Izquierdo Formateado
            'condilo_izq': f"la morfología de la cabeza condilar {morf_izq}.",
            'espacio_izq': f"{esp_izq}.",
            'medidas_izq': f"Medidas Anterosuperior: {med_as_izq} mm. Lateral: {med_lat_izq} mm. Posteroinferior: {med_pi_izq} mm. \n{derrame_izq} (Índice Condilar de Pullinger: {res_izq}%)",
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
            label="⬇️ DESCARGAR DOCUMENTO (.DOCX)",
            data=bio,
            file_name=f"Informe_ATM_{apellidos}.docx".replace(" ", "_"),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.success("¡Estructura sincronizada correctamente! Pulsa el botón para guardar.")
    except Exception as e:
        st.error(f"Error de sincronización con la plantilla Word: {e}")
