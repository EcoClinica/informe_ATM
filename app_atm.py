import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io

# Configuración de página ancha profesional
st.set_page_config(page_title="Informe Ecográfico ATM", layout="wide")

# Estilo CSS unificado en azul clínico
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; }
    .sub-seccion { color: #0284C7; border-bottom: 2px solid #0284C7; padding-bottom: 5px; margin-bottom: 15px; }
    .resultado-calculo { background-color: #E0F2FE; padding: 10px; border-radius: 5px; border-left: 4px solid #0284C7; margin-top: 10px; font-size: 14px; color: #1E3A8A !important; }
    .esfera { font-size: 16px; vertical-align: middle; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico de la Articulación Temporomandibular (ATM)</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #1E3A8A;'>", unsafe_allow_html=True)

# --- COMPONENTE INTEGRADO: MICROFÓNO + CASILLAS PROFESIONALES ---
def bloque_medidas_voz(lado, val_as, val_lat, val_pi):
    # Generamos los IDs únicos según el lado
    id_as = f"as_{lado}"
    id_lat = f"lat_{lado}"
    id_pi = f"pi_{lado}"
    
    html_code = f"""
    <div class="contenedor-medidas">
        <button class="btn-voz" onclick="iniciarDictado('{lado}')">🎙️ Dictar 3 Medidas seguidas</button>
        <span id="status_{lado}" class="status-texto">Micro apagado</span>
        
        <div class="grid-casillas">
            <div class="col-casilla">
                <label class="titulo-medidas">Anterosuperior ({lado.upper()})</label>
                <input type="text" id="{id_as}" class="input-gris" value="{val_as}" oninput="actualizarPython('{lado}')">
            </div>
            <div class="col-casilla">
                <label class="titulo-medidas">Lateral ({lado.upper()})</label>
                <input type="text" id="{id_lat}" class="input-gris" value="{val_lat}" oninput="actualizarPython('{lado}')">
            </div>
            <div class="col-casilla">
                <label class="titulo-medidas">Posteroinferior ({lado.upper()})</label>
                <input type="text" id="{id_pi}" class="input-gris" value="{val_pi}" oninput="actualizarPython('{lado}')">
            </div>
        </div>
    </div>

    <script>
    function iniciarDictado(lado) {{
        const status = document.getElementById('status_' + lado);
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.innerText = "❌ Navegador no compatible";
            return;
        }}
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-ES';
        recognition.interimResults = false;
        
        status.innerText = "🎙️ Escuchando...";
        status.style.color = "#0284C7";
        recognition.start();

        recognition.onresult = function(event) {{
            const texto = event.results[0][0].transcript;
            // Limpiamos el texto y extraemos los números sueltos
            const matches = texto.replace(/,/g, '.').match(/[0-9]+(\\.[0-9]+)?/g);
            
            if (matches && matches.length >= 3) {{
                // Colocar los números DIRECTAMENTE dentro de las casillas grises
                document.getElementById('as_' + lado).value = matches[0];
                document.getElementById('lat_' + lado).value = matches[1];
                document.getElementById('pi_' + lado).value = matches[2];
                
                status.innerText = "✓ Medidas insertadas";
                status.style.color = "#16A34A";
                
                // Avisar a Streamlit para que recalcule las fórmulas
                enviarASystem(lado, matches[0], matches[1], matches[2]);
            }} else {{
                status.innerText = "❌ Di 3 números. Detectó: " + texto;
                status.style.color = "#DC2626";
            }}
        }};

        recognition.onerror = function() {{
            status.innerText = "❌ Error micro";
            status.style.color = "#DC2626";
        }};
    }}

    function actualizarPython(lado) {{
        const v_as = document.getElementById('as_' + lado).value;
        const v_lat = document.getElementById('lat_' + lado).value;
        const v_pi = document.getElementById('pi_' + lado).value;
        enviarASystem(lado, v_as, v_lat, v_pi);
    }}

    function enviarASystem(lado, as_val, lat_val, pi_val) {{
        window.parent.postMessage({{
            tipo: 'ACTUALIZAR_MEDIDAS',
            lado: lado,
            as: as_val,
            lat: lat_val,
            pi: pi_val
        }}, '*');
    }}
    </script>

    <style>
    body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    .contenedor-medidas {{ padding: 2px 0; }}
    .btn-voz {{ background-color: #0284C7; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }}
    .btn-voz:hover {{ background-color: #0369A1; }}
    .status-texto {{ font-size: 13px; color: #666; margin-left: 10px; font-weight: 500; }}
    
    .grid-casillas {{ display: flex; gap: 15px; margin-top: 12px; }}
    .col-casilla {{ flex: 1; display: flex; flex-direction: column; }}
    
    /* Títulos idénticos: Letra en blanco y estilizada */
    .titulo-medidas {{ font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #FFFFFF !important; }}
    
    /* Casillas grises perfectas con letra blanca */
    .input-gris {{ 
        background-color: #31333F; 
        color: #FFFFFF; 
        border: 1px solid rgba(250, 250, 250, 0.2); 
        padding: 10px; 
        border-radius: 6px; 
        font-size: 16px; 
        outline: none;
    }}
    .input-gris:focus {{ border-color: #0284C7; }}
    </style>
    """
    components.html(html_code, height=145, scrolling=False)

# --- INICIALIZACIÓN DE VALORES EN MEMORIA ---
if 'as_der' not in st.session_state: st.session_state.as_der = ""
if 'lat_der' not in st.session_state: st.session_state.lat_der = ""
if 'pi_der' not in st.session_state: st.session_state.pi_der = ""

if 'as_izq' not in st.session_state: st.session_state.as_izq = ""
if 'lat_izq' not in st.session_state: st.session_state.lat_izq = ""
if 'pi_izq' not in st.session_state: st.session_state.pi_izq = ""

# --- FUNCIÓN PARA CALCULAR LA FÓRMULA DE PULLINGER ---
def calcular_posicion_condilo(ant_sup_txt, post_inf_txt):
    try:
        as_val = float(ant_sup_txt.replace(',', '.')) if ant_sup_txt else 0.0
        pi_val = float(post_inf_txt.replace(',', '.')) if post_inf_txt else 0.0
        if (pi_val + as_val) == 0: 
            return "Esperando medidas..."
        resultado = ((pi_val - as_val) / (pi_val + as_val)) * 100
        return f"{resultado:.1f}%"
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
opts_boca_cerrada = ["Cubre totalmente la cabeza del cóndilo", "Cubre parcialmente la cabeza del cóndilo", "Desplazado, no cubre la cabeza condilar"]
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
    
    # Renderizado del bloque integrado para el lado Derecho
    bloque_medidas_voz("der", st.session_state.as_der, st.session_state.lat_der, st.session_state.pi_der)
    
    st.subheader("Disco Articular Derecho")
    ecoestructura_der = st.selectbox("Ecoestructura (D):", opts_ecoestructura, key="eco_der")
    situacion_der = st.selectbox("Situación (D):", opts_situacion, key="sit_der")
    relacion_der = st.selectbox("Relación cóndilo-cavidad glenoidea (D):", opts_relacion, key="rel_der")
    
    res_der = calcular_posicion_condilo(st.session_state.as_der, st.session_state.pi_der)
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
    
    # Renderizado del bloque integrado para el lado Izquierdo
    bloque_medidas_voz("izq", st.session_state.as_izq, st.session_state.lat_izq, st.session_state.pi_izq)
    
    st.subheader("Disco Articular Izquierdo")
    ecoestructura_izq = st.selectbox("Ecoestructura (I):", opts_ecoestructura, key="eco_izq")
    situacion_izq = st.selectbox("Situación (I):", opts_situacion, key="sit_izq")
    relacion_izq = st.selectbox("Relación cóndilo-cavidad glenoidea (I):", opts_relacion, key="rel_izq")
    
    res_izq = calcular_posicion_condilo(st.session_state.as_izq, st.session_state.pi_izq)
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

# --- RECEPTOR AUTOMÁTICO EN DETRÁS DE ESCENA ---
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data.tipo === 'ACTUALIZAR_MEDIDAS') {
        // Enviar silenciosamente los datos a la memoria de Streamlit para cálculos y descarga Word
        const url = new URL(window.location.href);
        window.parent.postMessage({tipo: 'streamlit:setComponentValue', value: event.data}, '*');
    }
});
</script>
""", unsafe_allow_html=True)

# Lógica para asimilar los datos dictados en las variables de descarga
# Usamos un truco limpio de Query Params para refrescar los datos sin romper nada
query_params = st.query_params
if "lado" in query_params:
    ld = query_params["lado"]
    if ld == "der":
        st.session_state.as_der = query_params.get("as", "")
        st.session_state.lat_der = query_params.get("lat", "")
        st.session_state.pi_der = query_params.get("pi", "")
    elif ld == "izq":
        st.session_state.as_izq = query_params.get("as", "")
        st.session_state.lat_izq = query_params.get("lat", "")
        st.session_state.pi_izq = query_params.get("pi", "")

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
        'med_as_der': st.session_state.as_der, 'med_lat_der': st.session_state.lat_der, 'med_pi_der': st.session_state.pi_der,
        'ecoestructura_der': ecoestructura_der, 'situacion_der': situacion_der, 'relacion_der': relacion_der,
        'calculo_relacion_der': res_der,
        'hora_cerrada_der': hora_cerrada_der, 'cerrada_txt_der': cerrada_txt_der, 'abierta_txt_der': open_txt_der,
        'repo_forma_der': repo_forma_der, 'repo_tipo_der': repo_tipo_der,
        
        'morfologia_izq': morfologia_izq_txt, 'cartilago_izq': cartilago_izq, 'espacio_izq': espacio_izq_txt, 
        'med_as_izq': st.session_state.as_izq, 'med_lat_izq': st.session_state.lat_izq, 'med_pi_izq': st.session_state.pi_izq,
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
