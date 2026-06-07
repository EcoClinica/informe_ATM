import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io
import re

# Configuración de página ancha profesional y título de pestaña
st.set_page_config(page_title="Informe Ecográfico ATM", layout="wide")

# --- DISEÑO Y ESTILOS AVANZADOS PARA EVITAR APILAMIENTO EN IPAD ---
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .sub-seccion { color: #0284C7; border-bottom: 3px solid #0284C7; padding-bottom: 8px; margin-top: 25px; margin-bottom: 15px; font-size: 20px; font-weight: bold; }
    .titulo-medidas { font-size: 14px; font-weight: bold; margin-bottom: 8px; color: #475569 !important; }
    .esfera { font-size: 18px; vertical-align: middle; margin-right: 6px; }
    .resultado-calculo { background-color: #F0F9FF; padding: 12px; border-radius: 6px; border-left: 5px solid #0284C7; margin-top: 15px; margin-bottom: 15px; font-size: 15px; color: #1E3A8A !important; font-weight: bold; }
    .bloque-clinico { background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico de la Articulación Temporomandibular (ATM)</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #1E3A8A; margin-bottom: 30px;'>", unsafe_allow_html=True)

# --- COMPONENTE DEL MICRÓFONO CON CAJA BLANCA INTEGRADA ---
def componente_microfono_visible(lado_id):
    js_code = f"""
    <div style="font-family: sans-serif; display: flex; flex-direction: column; gap: 5px;">
        <div style="display: flex; gap: 10px; align-items: center;">
            <button id="btn_{lado_id}" class="btn-voz btn-azul" onclick="conmutarMicro('{lado_id}')" style="flex-shrink: 0;">🎙️ Dictar 3 Medidas</button>
            <input type="text" id="output_local_{lado_id}" placeholder="Esperando dictado de voz..." readonly 
                   style="flex-grow: 1; padding: 8px; font-size: 15px; font-weight: bold; border: 2px solid #0284C7; border-radius: 4px; background-color: #FFFFFF; color: #000000; text-align: center;">
        </div>
        <p id="status_{lado_id}" style="font-size:11px; color:#666; margin: 2px 0 0 2px; height: 14px; overflow: hidden;">Micro listo</p>
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
            if (recognition_{lado_id}) {{
                recognition_{lado_id}.abort();
            }}
            resetearBoton(lado, "🛑 Dictado cancelado.");
            return;
        }}

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.innerText = "Navegador no compatible.";
            return;
        }}

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition_{lado_id} = new SpeechRecognition();
        recognition_{lado_id}.lang = 'es-ES';
        recognition_{lado_id}.interimResults = false;
        recognition_{lado_id}.maxAlternatives = 1;

        activo_{lado_id} = true;
        btn.innerText = "🛑 Cancelar";
        btn.className = "btn-voz btn-rojo";
        status.innerText = "🎙️ Escuchando... Di los 3 números seguidos";
        status.style.color = "#0284C7";
        inputLocal.value = "";

        recognition_{lado_id}.start();

        recognition_{lado_id}.onresult = function(event) {{
            const texto = event.results[0][0].transcript;
            const matches = texto.replace(/,/g, '.').match(/[0-9]+(\\.[0-9]+)?/g);
            
            if (matches && matches.length >= 3) {{
                const resultadoCadena = matches[0] + " , " + matches[1] + " , " + matches[2];
                inputLocal.value = resultadoCadena;
                status.innerText = "✓ Medidas capturadas correctamente.";
                status.style.color = "#16A34A";
                
                enviarAStreamlit(resultadoCadena);
            }} else {{
                status.innerText = "❌ Reintenta: Di 3 números claros.";
                status.style.color = "#DC2626";
            }}
        }};

        recognition_{lado_id}.onerror = function(e) {{
            if (e.error !== 'aborted') {{
                status.innerText = "❌ Error de micro o silencio.";
                status.style.color = "#DC2626";
            }}
            resetearBoton(lado, status.innerText);
        }};
        
        recognition_{lado_id}.onend = function() {{
            resetearBoton(lado, status.innerText);
        }};
    }}

    function resetearBoton(lado, msg) {{
        activo_{lado_id} = false;
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);
        btn.innerText = "🎙️ Dictar 3 Medidas";
        btn.className = "btn-voz btn-azul";
        if(msg) status.innerText = msg;
    }}

    (function() {{
        var stScript = document.createElement('script');
        stScript.src = "https://cdn.jsdelivr.net/npm/@streamlit/component-lib@1.4.0/dist/index.min.js";
        stScript.onload = function() {{
            window.addEventListener('load', function() {{
                Streamlit.setFrameHeight(65);
            }});
        }};
        document.head.appendChild(stScript);
    }})();
    </script>

    <style>
    .btn-voz {{ border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px; transition: background 0.2s; height: 35px; }}
    .btn-azul {{ background-color: #0284C7; color: white; }}
    .btn-azul:hover {{ background-color: #0369A1; }}
    .btn-rojo {{ background-color: #DC2626; color: white; }}
    .btn-rojo:hover {{ background-color: #B91C1C; }}
    </style>
    """
    return components.html(js_code, height=65, scrolling=False)

# --- EXTRACCIÓN Y SEGURIDAD DE DATOS ---
def procesar_medidas_sistema(texto_dictado, manual_as, manual_lat, manual_pi):
    if texto_dictado and isinstance(texto_dictado, str) and len(texto_dictado).strip() > 0:
        numeros = re.findall(r"[0-9]+(?:\.[0-9]+)?", texto_dictado)
        if len(numeros) >= 3:
            return numeros[0], numeros[1], numeros[2]
    return manual_as, manual_lat, manual_pi

def calcular_posicion_condilo(ant_sup_txt, post_inf_txt):
    try:
        if not ant_sup_txt or not post_inf_txt:
            return "Esperando medidas..."
        as_val = float(str(ant_sup_txt).replace(',', '.'))
        pi_val = float(str(post_inf_txt).replace(',', '.'))
        if (pi_val + as_val) == 0: 
            return "0.00"
        resultado = ((pi_val - as_val) / (pi_val + as_val)) * 100
        signo = "+" if resultado > 0 else ""
        return f"{signo}{resultado:.2f}"
    except ValueError:
        return "Medidas no válidas"

# --- DATOS GENERALES DEL PACIENTE ---
st.markdown("<h3 style='color: #1E3A8A;'>📋 Datos Generales del Paciente</h3>", unsafe_allow_html=True)
cp1, cp2, cp3, cp4 = st.columns(4)
with cp1:
    nombres = st.text_input("Nombres:")
    apellidos = st.text_input("Apellidos:")
with cp2:
    edad = st.text_input("Edad:")
    derivado = st.text_input("Paciente derivado por Dr/a:")
with cp3:
    fecha = st.date_input("Fecha:", datetime.date.today(), format="DD/MM/YYYY")
    motivo = st.text_input("Motivo de consulta:")
with cp4:
    antecedentes = st.text_input("Antecedentes relacionados:")
    tratamiento_act = st.text_input("Tratamiento actual:")

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- OPCIONES MÉDICAS ---
opts_morfologia = ["Redondeado", "Aplanado", "En pico de pájaro (en punta)", "Con cresta central", "Con cresta marginal"]
opts_cartilago = ["Regular", "Irregular", "Fragmentado, sin exposición del hueso subyacente", "Fragmentado con exposición del hueso subyacente"]
opts_espacio = ["Libre", "Sin derrame articular", "Con engrosamiento sinovial", "Con derrame anecoico", "Con derrame articular y con partículas ecogénicas", "Osteofitos"]
opts_ecoestructura = ["Homogénea, hipoecogénico", "Heterogénea", "Irregular"]
opts_situacion = ["Central, cubre la cabeza condilar", "Cubre parcialmente la cabeza condilar", "Desplazamiento, no cubre la cabeza condilar"]
opts_relacion = ["Central", "Anterior", "Posterior"]
opts_horas = ["", "12", "11", "10", "1", "2", "otra"]
opts_boca_cerrada = ["Cubre totalmente la cabeza del cóndilo", "Cubre parcialmente la cabeza del cóndilo", "Desplazamiento, no cubre la cabeza condilar"]
opts_boca_abierta = [
    "Desplazamiento discal normal, cubre la cabeza del cóndilo",
    "Desplazamiento anterior, el disco cubre parcialmente la cabeza del cóndilo",
    "Desplazamiento anterior con subluxación discal, el cóndilo contacta con la cavidad glenoidea",
    "Desplazamiento anterior con luxación discal, el cóndilo contacta con la cavidad glenoidea",
    "Desplazamiento posterior, el disco cubre parcialmente la cabeza del cóndilo",
    "Desplazamiento posterior con subluxación discal, el cóndilo contacta con la cavidad glenoidea",
    "Desplazamiento posterior con luxación discal, el cóndilo contacta con la cavidad glenoidea"
]
opts_repo_forma = ["Espontánea", "Requiere maniobras mandibulares para su recaptación por parte del paciente", "Requiere maniobras mandibulares para su recaptación por parte del médico"]
opts_repo_tipo = ["Completa, cubre la cabeza del cóndilo", "Incompleta, vuelve a posicionarse en anterior", "Incompleta, vuelve a posicionarse en posterior", "No se reposiciona"]

# --- COLUMNAS PARALELAS AMPLIADAS PARA PANTALLAS TÁCTILES ---
col_der, col_izq = st.columns(2, gap="large")

# --- ARTICULACIÓN DERECHA ---
with col_der:
    st.markdown("<h2 class='sub-seccion'><span class='esfera'>🔹</span>Estudio ATM Derecha</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Cóndilo Mandibular Derecho")
        morfologia_der = st.multiselect("Morfología cabeza condilar (D):", opts_morfologia, default=["Redondeado"], key="m_der")
        cartilago_der = st.selectbox("Cartílago articular (D):", opts_cartilago, key="ca_der")
        espacio_der = st.multiselect("Espacio articular (D):", opts_espacio, default=["Libre"], key="es_der")
        
        st.markdown("<p class='titulo-medidas'>Captura de Medidas (mm):</p>", unsafe_allow_html=True)
        dictado_der = componente_microfono_visible("der")
        
        m1, m2, m3 = st.columns(3)
        with m1: manual_as_der = st.text_input("Anterosuperior (D)", key="man_as_der")
        with m2: manual_lat_der = st.text_input("Lateral (D)", key="man_lat_der")
        with m3: manual_pi_der = st.text_input("Posteroinferior (D)", key="man_pi_der")
        
        med_as_der, med_lat_der, med_pi_der = procesar_medidas_sistema(dictado_der, manual_as_der, manual_lat_der, manual_pi_der)
        
        res_der = calcular_posicion_condilo(med_as_der, med_pi_der)
        st.markdown(f"<div class='resultado-calculo'><strong>🧮 Índice de posición condilar (D):</strong> {res_der}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Disco Articular Derecho")
        ecoestructura_der = st.selectbox("Ecoestructura (D):", opts_ecoestructura, key="eco_der")
        situacion_der = st.selectbox("Situación (D):", opts_situacion, key="sit_der")
        relacion_der = st.selectbox("Relación cóndilo-cavidad glenoidea (D):", opts_relacion, key="rel_der")
        
        st.markdown("**Posición con Boca Cerrada (D):**")
        hora_cerrada_der = st.selectbox("En hora", opts_horas, key="h_c_der")
        cerrada_txt_der = st.selectbox("Estado (D):", opts_boca_cerrada, key="c_txt_der", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Estudio Dinámico y Reposición (D)")
        open_txt_der = st.selectbox("Boca abierta (D):", opts_boca_abierta, key="a_txt_der")
        repo_forma_der = st.selectbox("Forma de producirse (D):", opts_repo_forma, key="rf_der")
        repo_tipo_der = st.selectbox("Tipo de reposición (D):", opts_repo_tipo, key="rt_der")
        st.markdown("</div>", unsafe_allow_html=True)

# --- ARTICULACIÓN IZQUIERDA ---
with col_izq:
    st.markdown("<h2 class='sub-seccion'><span class='esfera'>🔹</span>Estudio ATM Izquierda</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Cóndilo Mandibular Izquierdo")
        morfologia_izq = st.multiselect("Morfología cabeza condilar (I):", opts_morfologia, default=["Redondeado"], key="m_izq")
        cartilago_izq = st.selectbox("Cartílago articular (I):", opts_cartilago, key="ca_izq")
        espacio_izq = st.multiselect("Espacio articular (I):", opts_espacio, default=["Libre"], key="es_izq")
        
        st.markdown("<p class='titulo-medidas'>Captura de Medidas (mm):</p>", unsafe_allow_html=True)
        dictado_izq = componente_microfono_visible("izq")
        
        m4, m5, m6 = st.columns(3)
        with m4: manual_as_izq = st.text_input("Anterosuperior (I)", key="man_as_izq")
        with m5: manual_lat_izq = st.text_input("Lateral (I)", key="man_lat_izq")
        with m6: manual_pi_izq = st.text_input("Posteroinferior (I)", key="man_pi_izq")
        
        med_as_izq, med_lat_izq, med_pi_izq = procesar_medidas_sistema(dictado_izq, manual_as_izq, manual_lat_izq, manual_pi_izq)
        
        res_izq = calcular_posicion_condilo(med_as_izq, med_pi_izq)
        st.markdown(f"<div class='resultado-calculo'><strong>🧮 Índice de posición condilar (I):</strong> {res_izq}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Disco Articular Izquierdo")
        ecoestructura_izq = st.selectbox("Ecoestructura (I):", opts_ecoestructura, key="eco_izq")
        situacion_izq = st.selectbox("Situación (I):", opts_situacion, key="sit_izq")
        relacion_izq = st.selectbox("Relación cóndilo-cavidad glenoidea (I):", opts_relacion, key="rel_izq")
        
        st.markdown("**Posición con Boca Cerrada (I):**")
        hora_cerrada_izq = st.selectbox("En hora", opts_horas, key="h_c_izq")
        cerrada_txt_izq = st.selectbox("Estado (I):", opts_boca_cerrada, key="c_txt_izq", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bloque-clinico'>", unsafe_allow_html=True)
        st.subheader("Estudio Dinámico y Reposición (I)")
        open_txt_izq = st.selectbox("Boca abierta (I):", opts_boca_abierta, key="a_txt_izq")
        repo_forma_izq = st.selectbox("Forma de producirse (I):", opts_repo_forma, key="rf_izq")
        repo_tipo_izq = st.selectbox("Tipo de reposición (I):", opts_repo_tipo, key="rt_izq")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid #1E3A8A;'>", unsafe_allow_html=True)
conclusion = st.text_area("📝 CONCLUSIÓN / OBSERVACIONES:")

# --- SECCIÓN DE ENLACE SEGURO Y GENERACIÓN DOCX ---
st.subheader("💾 Finalizar Informe")

try:
    doc = DocxTemplate("plantilla_atm.docx")
    morfologia_der_txt = ", ".join(morfologia_der)
    espacio_der_txt = ", ".join(espacio_der)
    morfologia_izq_txt = ", ".join(morfologia_izq)
    espacio_izq_txt = ", ".join(espacio_izq)
    
    # CONTROL DE SEGURIDAD ABSOLUTO: Vinculamos los datos definitivos mapeados del dictado o manuales
    contexto = {
        'nombres': nombres, 
        'apellidos': apellidos, 
        'edad': edad, 
        'derivado': derivado,
        'fecha': fecha.strftime("%d/%m/%Y") if fecha else "", 
        'motivo': motivo, 
        'antecedentes': antecedentes, 
        'tratamiento_act': tratamiento_act,
        
        'morfologia_der': morfologia_der_txt, 
        'cartilago_der': cartilago_der, 
        'espacio_der': espacio_der_txt, 
        'med_as_der': med_as_der if med_as_der else "", 
        'med_lat_der': med_lat_der if med_lat_der else "", 
        'med_pi_der': med_pi_der if med_pi_der else "",
        'ecoestructura_der': ecoestructura_der, 
        'situacion_der': situacion_der, 
        'relacion_der': relacion_der,
        'calculo_relacion_der': res_der,
        'hora_cerrada_der': hora_cerrada_der, 
        'cerrada_txt_der': cerrada_txt_der, 
        'abierta_txt_der': open_txt_der,
        'repo_forma_der': repo_forma_der, 
        'repo_tipo_der': repo_tipo_der,
        
        'morfologia_izq': morfologia_izq_txt, 
        'cartilago_izq': cartilago_izq, 
        'espacio_izq': espacio_izq_txt, 
        'med_as_izq': med_as_izq if med_as_izq else "", 
        'med_lat_izq': med_lat_izq if med_lat_izq else "", 
        'med_pi_izq': med_pi_izq if med_pi_izq else "",
        'ecoestructura_izq': ecoestructura_izq, 
        'situacion_izq': situacion_izq, 
        'relacion_izq': relacion_izq,
        'calculo_relacion_izq': res_izq,
        'hora_cerrada_izq': hora_cerrada_izq, 
        'cerrada_txt_izq': cerrada_txt_izq, 
        'abierta_txt_izq': open_txt_izq,
        'repo_forma_izq': repo_forma_izq, 
        'repo_tipo_izq': repo_tipo_izq,
        
        'conclusion': conclusion
    }
    
    doc.render(contexto)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    nombre_archivo = f"Informe_ATM_{apellidos}_{nombres}.docx".replace(" ", "_")
    
    st.download_button(
        label="🚀 DESCARGAR INFORME EN WORD",
        data=bio,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
except Exception as e:
    st.error(f"Error interno al empaquetar los datos del informe: {e}")
