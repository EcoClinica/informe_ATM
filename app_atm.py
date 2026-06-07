import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io

# Configuración de página ancha profesional
st.set_page_config(page_title="Informe Ecográfico ATM", layout="wide")

# Estilo CSS original, limpio y adaptado para iPad
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; }
    .sub-seccion { color: #0284C7; border-bottom: 2px solid #0284C7; padding-bottom: 5px; margin-bottom: 15px; }
    .titulo-medidas { font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #FFFFFF !important; }
    .esfera { font-size: 16px; vertical-align: middle; margin-right: 5px; }
    .resultado-calculo { background-color: #E0F2FE; padding: 10px; border-radius: 5px; border-left: 4px solid #0284C7; margin-top: 10px; font-size: 14px; color: #1E3A8A !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico de la Articulación Temporomandibular (ATM)</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #1E3A8A;'>", unsafe_allow_html=True)

# --- FUNCIÓN DEL MICRÓFONO INTELIGENTE ON/OFF ---
def componente_microfono(lado_id):
    # Generamos identificadores únicos para los campos de texto según el lado
    id_as = f"input_as_{lado_id}"
    id_lat = f"input_lat_{lado_id}"
    id_pi = f"input_pi_{lado_id}"
    
    js_code = f"""
    <div style="font-family: sans-serif; margin-bottom: 10px;">
        <button id="btn_{lado_id}" class="btn-voz btn-azul" onclick="conmutarMicro('{lado_id}')">🎙️ Dictar 3 Medidas</button>
        <p id="status_{lado_id}" style="font-size:11px; color:#666; margin:4px 0 0 2px;">Micro listo</p>
    </div>

    <script>
    let recognition_{lado_id} = null;
    let activo_{lado_id} = false;

    function conmutarMicro(lado) {{
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);

        if (activo_{lado_id}) {{
            // FUNCIÓN: Si está activo, apagar inmediatamente al pulsar de nuevo
            if (recognition_{lado_id}) {{
                recognition_{lado_id}.abort();
            }}
            resetearBoton(lado, "🛑 Dictado cancelado por el usuario.");
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

        // Cambiar estado a encendido (Botón Rojo de stop)
        activo_{lado_id} = true;
        btn.innerText = "🛑 Detener / Cancelar";
        btn.className = "btn-voz btn-rojo";
        status.innerText = "🎙️ Escuchando... Di los 3 números seguidos";
        status.style.color = "#0284C7";

        recognition_{lado_id}.start();

        recognition_{lado_id}.onresult = function(event) {{
            const texto = event.results[0][0].transcript;
            const matches = texto.replace(/,/g, '.').match(/[0-9]+(\\.[0-9]+)?/g);
            
            if (matches && matches.length >= 3) {{
                status.innerText = "✓ Medidas introducidas con éxito.";
                status.style.color = "#16A34A";
                
                // INYECTOR DIRECTO AL DOM DEL IPAD (Fuerza la inserción interna y dispara los cálculos)
                inyectarValor('{id_as}', matches[0]);
                inyectarValor('{id_lat}', matches[1]);
                inyectarValor('{id_pi}', matches[2]);
            }} else {{
                status.innerText = "❌ No se capturaron 3 números. Inténtalo de nuevo.";
                status.style.color = "#DC2626";
            }}
        }};

        recognition_{lado_id}.onerror = function(e) {{
            if (e.error !== 'aborted') {{
                status.innerText = "❌ Error de micro o silencio prolongado.";
                status.style.color = "#DC2626";
            }}
            resetearBoton(lado, status.innerText);
        }};
        
        recognition_{lado_id}.onend = function() {{
            resetearBoton(lado, status.innerText);
        }};
    }}

    function inyectarValor(idCampo, valor) {{
        // Buscamos la casilla en la ventana principal del iPad
        const el = window.parent.document.getElementById(idCampo);
        if (el) {{
            el.value = valor;
            // Disparar eventos nativos para que el motor matemático calcule al instante
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
    }}

    function resetearBoton(lado, msg) {{
        activo_{lado_id} = false;
        const btn = document.getElementById('btn_' + lado);
        const status = document.getElementById('status_' + lado);
        btn.innerText = "🎙️ Dictar 3 Medidas";
        btn.className = "btn-voz btn-azul";
        if(msg) {{
            status.innerText = msg;
        }} else {{
            status.innerText = "Micro listo";
            status.style.color = "#666";
        }}
    }}
    </script>

    <style>
    .btn-voz {{ border: none; padding: 7px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px; transition: background 0.2s; }}
    .btn-azul {{ background-color: #0284C7; color: white; }}
    .btn-azul:hover {{ background-color: #0369A1; }}
    .btn-rojo {{ background-color: #DC2626; color: white; }}
    .btn-rojo:hover {{ background-color: #B91C1C; }}
    </style>
    """
    components.html(js_code, height=52, scrolling=False)

# --- FUNCIÓN CORREGIDA PARA EL ÍNDICE DE PULLINGER (NÚMERO ABSOLUTO CON SIGNO) ---
def calcular_posicion_condilo(ant_sup_txt, post_inf_txt):
    try:
        if not ant_sup_txt or not post_inf_txt:
            return "Esperando medidas..."
        as_val = float(str(ant_sup_txt).replace(',', '.'))
        pi_val = float(str(post_inf_txt).replace(',', '.'))
        if (pi_val + as_val) == 0: 
            return "0.00"
        # Fórmula matemática Pullinger original (*100 es parte del índice absoluto)
        resultado = ((pi_val - as_val) / (pi_val + as_val)) * 100
        signo = "+" if resultado > 0 else ""
        return f"{signo}{resultado:.2f}"
    except ValueError:
        return "Medidas no válidas"

# --- DATOS GENERALES DEL PACIENTE ---
st.subheader("📋 Datos del Paciente")
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

st.markdown("<br>", unsafe_allow_html=True)

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

# --- COLUMNAS PARALELAS ---
col_der, col_izq = st.columns(2)

# --- ARTICULACIÓN DERECHA ---
with col_der:
    st.markdown("<h2 class='sub-seccion'><span class='esfera'>🔹</span>Estudio ATM Derecha</h2>", unsafe_allow_html=True)
    
    st.subheader("Cóndilo Mandibular Derecho")
    morfologia_der = st.multiselect("Morfología cabeza condilar (D):", opts_morfologia, default=["Redondeado"], key="m_der")
    cartilago_der = st.selectbox("Cartílago articular (D):", opts_cartilago, key="ca_der")
    espacio_der = st.multiselect("Espacio articular (D):", opts_espacio, default=["Libre"], key="es_der")
    
    st.markdown("<p class='titulo-medidas'>Medidas (mm):</p>", unsafe_allow_html=True)
    
    # Renderizamos el botón con el conmutador ON/OFF integrado
    componente_microfono("der")
    
    # Fila de casillas original con IDs explícitos para el inyector rápido
    m1, m2, m3 = st.columns(3)
    with m1: med_as_der = st.text_input("Anterosuperior (D)", key="input_as_der")
    with m2: med_lat_der = st.text_input("Lateral (D)", key="input_lat_der")
    with m3: med_pi_der = st.text_input("Posteroinferior (D)", key="input_pi_der")
    
    st.subheader("Disco Articular Derecho")
    ecoestructura_der = st.selectbox("Ecoestructura (D):", opts_ecoestructura, key="eco_der")
    situacion_der = st.selectbox("Situación (D):", opts_situacion, key="sit_der")
    relacion_der = st.selectbox("Relación cóndilo-cavidad glenoidea (D):", opts_relacion, key="rel_der")
    
    res_der = calcular_posicion_condilo(med_as_der, med_pi_der)
    st.markdown(f"<div class='resultado-calculo'><strong>🧮 Índice de posición condilar (D):</strong> {res_der}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>**Posición con Boca Cerrada (D):**", unsafe_allow_html=True)
    hora_cerrada_der = st.selectbox("En hora", opts_horas, key="h_c_der")
    cerrada_txt_der = st.selectbox("Estado (D):", opts_boca_cerrada, key="c_txt_der", label_visibility="collapsed")
    
    st.subheader("Estudio Dinámico Derecho")
    open_txt_der = st.selectbox("Boca abierta (D):", opts_boca_abierta, key="a_txt_der")
    
    st.subheader("Reposición del Disco Articular (D)")
    repo_forma_der = st.selectbox("Forma de producirse (D):", opts_repo_forma, key="rf_der")
    repo_tipo_der = st.selectbox("Tipo de reposición (D):", opts_repo_tipo, key="rt_der")

# --- ARTICULACIÓN IZQUIERDA ---
with col_izq:
    st.markdown("<h2 class='sub-seccion'><span class='esfera'>🔹</span>Estudio ATM Izquierda</h2>", unsafe_allow_html=True)
    
    st.subheader("Cóndilo Mandibular Izquierdo")
    morfologia_izq = st.multiselect("Morfología cabeza condilar (I):", opts_morfologia, default=["Redondeado"], key="m_izq")
    cartilago_izq = st.selectbox("Cartílago articular (I):", opts_cartilago, key="ca_izq")
    espacio_izq = st.multiselect("Espacio articular (I):", opts_espacio, default=["Libre"], key="es_izq")
    
    st.markdown("<p class='titulo-medidas'>Medidas (mm):</p>", unsafe_allow_html=True)
    
    # Renderizamos el botón con el conmutador ON/OFF integrado
    componente_microfono("izq")
    
    # Fila de casillas original con IDs explícitos para el inyector rápido
    m4, m5, m6 = st.columns(3)
    with m4: med_as_izq = st.text_input("Anterosuperior (I)", key="input_as_izq")
    with m5: med_lat_izq = st.text_input("Lateral (I)", key="input_lat_izq")
    with m6: med_pi_izq = st.text_input("Posteroinferior (I)", key="input_pi_izq")
    
    st.subheader("Disco Articular Izquierdo")
    ecoestructura_izq = st.selectbox("Ecoestructura (I):", opts_ecoestructura, key="eco_izq")
    situacion_izq = st.selectbox("Situación (I):", opts_situacion, key="sit_izq")
    relacion_izq = st.selectbox("Relación cóndilo-cavidad glenoidea (I):", opts_relacion, key="rel_izq")
    
    res_izq = calcular_posicion_condilo(med_as_izq, med_pi_izq)
    st.markdown(f"<div class='resultado-calculo'><strong>🧮 Índice de posición condilar (I):</strong> {res_izq}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>**Posición con Boca Cerrada (I):**", unsafe_allow_html=True)
    hora_cerrada_izq = st.selectbox("En hora", opts_horas, key="h_c_izq")
    cerrada_txt_izq = st.selectbox("Estado (I):", opts_boca_cerrada, key="c_txt_izq", label_visibility="collapsed")
    
    st.subheader("Estudio Dinámico Izquierdo")
    open_txt_izq = st.selectbox("Boca abierta (I):", opts_boca_abierta, key="a_txt_izq")
    
    st.subheader("Reposición del Disco Articular (I)")
    repo_forma_izq = st.selectbox("Forma de producirse (I):", opts_repo_forma, key="rf_izq")
    repo_tipo_izq = st.selectbox("Tipo de reposición (I):", opts_repo_tipo, key="rt_izq")

st.markdown("<br><hr style='border: 1px solid #1E3A8A;'>", unsafe_allow_html=True)
conclusion = st.text_area("📝 CONCLUSIÓN / OBSERVACIONES:")

# --- SECCIÓN DE DESCARGA ---
st.subheader("💾 Finalizar Informe")

try:
    doc = DocxTemplate("plantilla_atm.docx")
    morfologia_der_txt = ", ".join(morfologia_der)
    espacio_der_txt = ", ".join(espacio_der)
    morfologia_izq_txt = ", ".join(morfologia_izq)
    espacio_izq_txt = ", ".join(espacio_izq)
    
    contexto = {
        'nombres': nombres, 'apellidos': apellidos, 'edad': edad, 'derivado': derivado,
        'fecha': fecha.strftime("%d/%m/%Y"), 'motivo': motivo, 'antecedentes': antecedentes, 'tratamiento_act': tratamiento_act,
        'morfologia_der': morfologia_der_txt, 'cartilago_der': cartilago_der, 'espacio_der': espacio_der_txt, 
        'med_as_der': med_as_der, 'med_lat_der': med_lat_der, 'med_pi_der': med_pi_der,
        'ecoestructura_der': ecoestructura_der, 'situacion_der': situacion_der, 'relacion_der': relacion_der,
        'calculo_relacion_der': res_der,
        'hora_cerrada_der': hora_cerrada_der, 'cerrada_txt_der': cerrada_txt_der, 'abierta_txt_der': open_txt_der,
        'repo_forma_der': repo_forma_der, 'repo_tipo_der': repo_tipo_der,
        
        'morfologia_izq': morfologia_izq_txt, 'cartilago_izq': cartilago_izq, 'espacio_izq': espacio_izq_txt, 
        'med_as_izq': med_as_izq, 'med_lat_izq': med_lat_izq, 'med_pi_izq': med_pi_izq,
        'ecoestructura_izq': ecoestructura_izq, 'situacion_izq': situacion_izq, 'relacion_izq': relacion_izq,
        'calculo_relacion_izq': res_izq,
        'hora_cerrada_izq': hora_cerrada_izq, 'cerrada_txt_izq': cerrada_txt_izq, 'abierta_txt_izq': open_txt_izq,
        'repo_forma_izq': repo_forma_izq, 'repo_tipo_izq': repo_tipo_izq,
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
    st.error(f"Error al preparar el documento: {e}")
