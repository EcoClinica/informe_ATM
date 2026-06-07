import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
import datetime
import io
import re

# Configuración de página limpia y profesional
st.set_page_config(page_title="Informe Ecográfico ATM", layout="wide")

# Estilos CSS adaptados al flujo de lectura de tu informe médico
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-titulo { text-align: center; color: #475569; font-size: 14px; margin-bottom: 25px; }
    .seccion-lado { background-color: #F8FAFC; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .titulo-lado { color: #0284C7; font-size: 18px; font-weight: bold; border-bottom: 2px solid #0284C7; padding-bottom: 6px; margin-bottom: 15px; }
    .sub-bloque { font-weight: bold; color: #1E3A8A; margin-top: 10px; margin-bottom: 5px; font-size: 14px; }
    .resultado-calculo { background-color: #E0F2FE; padding: 10px; border-radius: 4px; border-left: 4px solid #0284C7; margin-top: 10px; font-size: 14px; color: #1E3A8A !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Informe Ecográfico ATM</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-titulo'>Protocolo de adquisición ecográfica de la articulación temporomandibular en posición de boca abierta y cerrada</p>", unsafe_allow_html=True)

# --- RECEPTOR DE DICTADO (COMPONENTE SEGURO IPAD) ---
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
        status.innerText = "🎙️ Escuchando... Di las 3 medidas";
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
                status.innerText = "❌ Di 3 números claros.";
                status.style.color = "#DC2626";
            }}
        }};

        recognition_{lado_id}.onerror = function(e) {{
            resetearBoton(lado, "Micro apagado.");
        }};
        
        recognition_{lado_id}.onend = function() {{
            resetearBoton(lado, status.innerText);
        }};
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
        stScript.onload = function() {{
            window.addEventListener('load', function() {{ Streamlit.setFrameHeight(60); }});
        }};
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

# --- PROCESADOR INTERNO DE NÚMEROS DICTADOS ---
def procesar_medidas_sistema(texto_dictado, manual_as, manual_lat, manual_pi):
    if texto_dictado and isinstance(texto_dictado, str) and len(texto_dictado.strip()) > 0:
        numeros = re.findall(r"[0-9]+(?:\.[0-9]+)?", texto_dictado)
        if len(numeros) >= 3:
            return numeros[0], numeros[1], numeros[2]
    return manual_as, manual_lat, manual_pi

def calcular_posicion_condilo(ant_sup_txt, post_inf_txt):
    try:
        if not ant_sup_txt or not post_inf_txt: return "Esperando datos..."
        as_val = float(str(ant_sup_txt).replace(',', '.'))
        pi_val = float(str(post_inf_txt).replace(',', '.'))
        if (pi_val + as_val) == 0: return "0.00"
        resultado = ((pi_val - as_val) / (pi_val + as_val)) * 100
        return f"{'+' if resultado > 0 else ''}{resultado:.2f}"
    except ValueError:
        return "Medidas inválidas"

# --- BLOQUE 1: DATOS GENERALES ---
st.subheader("📋 Datos Clínicos Iniciales")
cp1, cp2, cp3 = st.columns(3)
with cp1:
    nombres = st.text_input("Nombres:", value="Paciente")
    apellidos = st.text_input("Apellidos:", value="Ejemplo")
    edad = st.text_input("Edad:")
with cp2:
    fecha = st.date_input("Fecha de adquisición:", datetime.date.today(), format="DD/MM/YYYY")
    derivado = st.text_input("Paciente derivado por Dr/a:")
    motivo = st.text_input("Motivo de consulta / Síntomas:", value="Dolor ATM bilateral.")
with cp3:
    antecedentes = st.text_input("Antecedentes relacionados:")
    tratamiento_act = st.text_input("Tratamiento actual:")

st.markdown("<br>", unsafe_allow_html=True)

# --- BLOQUE 2: ESTUDIO CLÍNICO EN PARALELO ---
col_der, col_izq = st.columns(2, gap="large")

# --- LADO DERECHO ---
with col_der:
    st.markdown("<div class='seccion-lado'>", unsafe_allow_html=True)
    st.markdown("<div class='titulo-lado'>Estudio Articulación Temporomandibular Derecha</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Cóndilo Mandibular Derecho:</div>", unsafe_allow_html=True)
    morfologia_der = st.text_input("Morfología cabeza condilar (D)", value="aplanado, irregular", key="in_m_der")
    
    st.markdown("<div class='sub-bloque'>Espacio Articular (D):</div>", unsafe_allow_html=True)
    espacio_der = st.text_input("Hallazgos espacio articular (D)", value="con osteofitos. Engrosamiento sinovial superior. Presencia de derrame articular.", key="in_e_der")
    
    st.markdown("<div class='sub-bloque'>Dictar Medidas (mm):</div>", unsafe_allow_html=True)
    dictado_der = componente_microfono_visible("der")
    
    md1, md2, md3 = st.columns(3)
    with md1: manual_as_der = st.text_input("Anterosuperior (D)", value="1.98", key="m_as_der")
    with md2: manual_lat_der = st.text_input("Lateral (D)", value="1.65", key="m_la_der")
    with md3: manual_pi_der = st.text_input("Posteroinferior (D)", value="2.84", key="m_pi_der")
    
    # Sincronización del dato dictado/manual hacia las variables finales
    med_as_der, med_lat_der, med_pi_der = procesar_medidas_sistema(dictado_der, manual_as_der, manual_lat_der, manual_pi_der)
    
    # Índice de Pullinger instantáneo
    res_der = calcular_posicion_condilo(med_as_der, med_pi_der)
    st.markdown(f"<div class='resultado-calculo'>🧮 Índice de Posición Condilar (D): {res_der}%</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Disco Articular Derecho:</div>", unsafe_allow_html=True)
    eco_der = st.text_input("Ecoestructura / Situación (D)", value="Ecoestructura hipoecogénico. Situación en hora 11.", key="in_di_der")
    rel_der = st.text_input("Relación cóndilo-fosa (D)", value="Cóndilo en posición anterior.", key="in_re_der")
    
    st.markdown("<div class='sub-bloque'>Estudio Dinámico (D):</div>", unsafe_allow_html=True)
    cerrada_der = st.text_input("Boca cerrada (D)", value="en hora 11 cubre parcialmente la cabeza del cóndilo.", key="in_ce_der")
    abierta_der = st.text_input("Boca abierta (D)", value="desplazamiento anterior cubre la porción anterior de la cabeza condilar durante la apertura bucal, resto del cóndilo contacta con la cavidad glenoidea.", key="in_ab_der")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- LADO IZQUIERDO ---
with col_izq:
    st.markdown("<div class='seccion-lado'>", unsafe_allow_html=True)
    st.markdown("<div class='titulo-lado'>Estudio Articulación Temporomandibular Izquierda</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Cóndilo Mandibular Izquierdo:</div>", unsafe_allow_html=True)
    morfologia_izq = st.text_input("Morfología cabeza condilar (I)", value="irregular, estrecho, con cresta lateral", key="in_m_izq")
    
    st.markdown("<div class='sub-bloque'>Espacio Articular (I):</div>", unsafe_allow_html=True)
    espacio_izq = st.text_input("Hallazgos espacio articular (I)", value="con osteofitos. Presencia de derrame articular.", key="in_e_izq")
    
    st.markdown("<div class='sub-bloque'>Dictar Medidas (mm):</div>", unsafe_allow_html=True)
    dictado_izq = componente_microfono_visible("izq")
    
    mi1, mi2, mi3 = st.columns(3)
    with mi1: manual_as_izq = st.text_input("Anterosuperior (I)", value="2.37", key="m_as_izq")
    with mi2: manual_lat_izq = st.text_input("Lateral (I)", value="1.14", key="m_la_izq")
    with mi3: manual_pi_izq = st.text_input("Posteroinferior (I)", value="2.92", key="m_pi_izq")
    
    # Sincronización del dato dictado/manual hacia las variables finales
    med_as_izq, med_lat_izq, med_pi_izq = procesar_medidas_sistema(dictado_izq, manual_as_izq, manual_lat_izq, manual_pi_izq)
    
    # Índice de Pullinger instantáneo
    res_izq = calcular_posicion_condilo(med_as_izq, med_pi_izq)
    st.markdown(f"<div class='resultado-calculo'>🧮 Índice de Posición Condilar (I): {res_izq}%</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-bloque'>Disco Articular Izquierdo:</div>", unsafe_allow_html=True)
    eco_izq = st.text_input("Ecoestructura / Situación (I)", value="Ecoestructura hipoecogénico. Situado en hora 11.", key="in_di_izq")
    rel_izq = st.text_input("Relación cóndilo-fosa (I)", value="Cóndilo en posición central", key="in_re_izq")
    
    st.markdown("<div class='sub-bloque'>Estudio Dinámico (I):</div>", unsafe_allow_html=True)
    cerrada_izq = st.text_input("Boca cerrada (I)", value="en hora 11 cubre parcialmente la cabeza del cóndilo.", key="in_ce_izq")
    abierta_izq = st.text_input("Boca abierta (I)", value="desplazamiento anterior cubre la porción anterior de la cabeza condilar durante la apertura bucal, resto del cóndilo contacta con la cavidad glenoidea.", key="in_ab_izq")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- CONCLUSIÓN GENERAL ---
st.markdown("<br>", unsafe_allow_html=True)
conclusion = st.text_area("📝 CONCLUSIÓN:", value="Signos ecográficos compatibles con...")

# --- PROCESAMIENTO FINAL Y COMPRESIÓN DEL WORD ---
st.subheader("💾 Guardar y Exportar Documento")

try:
    doc = DocxTemplate("plantilla_atm.docx")
    
    # Este diccionario mapea exactamente las variables que se inyectan en tu archivo Word
    contexto = {
        'nombres': nombres, 'apellidos': apellidos, 'edad': edad, 'derivado': derivado,
        'fecha': fecha.strftime("%d/%m/%Y") if fecha else "", 'motivo': motivo, 
        'antecedentes': antecedentes, 'tratamiento_act': tratamiento_act,
        
        # Datos brazo derecho
        'morfologia_der': morfologia_der, 'espacio_der': espacio_der,
        'med_as_der': med_as_der, 'med_lat_der': med_lat_der, 'med_pi_der': med_pi_der,
        'eco_der': eco_der, 'rel_der': rel_der, 'calculo_der': res_der,
        'cerrada_der': cerrada_der, 'abierta_der': abierta_der,
        
        # Datos brazo izquierdo
        'morfologia_izq': morfologia_izq, 'espacio_izq': espacio_izq,
        'med_as_izq': med_as_izq, 'med_lat_izq': med_lat_izq, 'med_pi_izq': med_pi_izq,
        'eco_izq': eco_izq, 'rel_izq': rel_izq, 'calculo_izq': res_izq,
        'cerrada_izq': cerrada_izq, 'abierta_izq': abierta_izq,
        
        'conclusion': conclusion
    }
    
    doc.render(contexto)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    st.download_button(
        label="🚀 DESCARGAR INFORME COMPLETADO (.DOCX)",
        data=bio,
        file_name=f"Informe_ATM_{apellidos}.docx".replace(" ", "_"),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
except Exception as e:
    st.error(f"Aviso del sistema de archivos: {e}")
