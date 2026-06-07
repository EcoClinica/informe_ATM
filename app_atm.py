import streamlit as st
from docxtpl import DocxTemplate
import datetime
import io

# Configuración de la página (Fuerza el modo claro para evitar fallos en el iPad)
st.set_page_config(page_title="Generador de Informes ATM", page_icon="🦷", layout="centered")

# Estilos CSS para asegurar legibilidad en el iPad (Fondo limpio y texto oscuro)
st.markdown("""
    <style>
    .reportview-container, .main {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
    }
    h1, h2, h3, label, p {
        color: #1A365D !important;
    }
    .stButton>button {
        background-color: #2B6CB0 !important;
        color: white !important;
        border-radius: 8px;
    }
    /* Estilo especial para la tarjeta del cálculo del cóndilo */
    .resultado-calculo {
        background-color: #F7FAFC !important;
        padding: 15px;
        border-left: 5px solid #2B6CB0;
        border-radius: 4px;
        margin: 15px 0;
    }
    </style>
""", unsafe_gradient=True)

st.title("📋 Generador de Informes Ecográficos ATM")
st.subheader("Clínica de Ecografía")

# --- DATOS DEL PACIENTE ---
st.markdown("### 👤 Datos del Paciente")
nombre = st.text_input("Nombre Completo del Paciente:")
fecha_nac = st.date_input("Fecha de Nacimiento:", min_value=datetime.date(1920, 1, 1))
fecha_eco = st.date_input("Fecha de la Ecografía:", datetime.date.today())

# --- EXPLORACIÓN CLÍNICA ---
st.markdown("### 🔍 Exploración Clínica de la ATM")
apertura = st.number_input("Apertura bucal máxima (mm):", min_value=0.0, max_value=100.0, step=0.1)

# --- MEDIDAS ECOGRÁFICAS ---
st.markdown("### 📊 Medidas Ecográficas (Lado Derecho)")
boca_cerrada_d = st.number_input("Derecho - Boca Cerrada (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bcd")
boca_abierta_d = st.number_input("Derecho - Boca Abierta (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bad")

st.markdown("### 📊 Medidas Ecográficas (Lado Izquierdo)")
boca_cerrada_i = st.number_input("Izquierdo - Boca Cerrada (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bci")
boca_abierta_i = st.number_input("Izquierdo - Boca Abierta (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bai")

# --- CÁLCULO DE LA POSICIÓN DEL CÓNDILO ---
st.markdown("### 📐 Cálculo de la Posición del Cóndilo")
# Fórmula: Traslación Condilar = Boca Cerrada - Boca Abierta
traslacion_d = boca_cerrada_d - boca_abierta_d
traslacion_i = boca_cerrada_i - boca_abierta_i

# Mostrar el resultado de forma impecable en el iPad
st.markdown(f"""
<div class="resultado-calculo">
    <h4 style="margin:0 0 10px 0; color:#2B6CB0;">📍 Resultados del Desplazamiento Condilar:</h4>
    <p style="margin:5px 0; font-size:11pt; color:#2D3748;"><b>Lado Derecho:</b> {traslacion_d:.1st} mm</p>
    <p style="margin:5px 0; font-size:11pt; color:#2D3748;"><b>Lado Izquierdo:</b> {traslacion_i:.1st} mm</p>
</div>
""", unsafe_allow_html=True)

# --- COMENTARIOS / OBSERVACIONES ---
st.markdown("### ✍️ Conclusiones y Observaciones")
observaciones = st.text_area("Escriba aquí los hallazgos adicionales:", height=100)

# --- GENERACIÓN DEL ARCHIVO WORD ---
if st.button("🚀 DESCARGAR INFORME EN WORD"):
    if not nombre:
        st.error("⚠️ Por favor, introduzca el nombre del paciente antes de generar el informe.")
    else:
        try:
            # Cargar la plantilla cargada en GitHub
            doc = DocxTemplate("plantilla_atm.docx")
            
            # Formatear fechas
            f_nac_str = fecha_nac.strftime("%d/%m/%Y")
            f_eco_str = fecha_eco.strftime("%d/%m/%Y")
            
            # Crear el diccionario con los datos exactos para el Word
            context = {
                'nombre': nombre,
                'fecha_nac': f_nac_str,
                'fecha_eco': f_eco_str,
                'apertura': f"{apertura:.1f}",
                'boca_cerrada_d': f"{boca_cerrada_d:.1f}",
                'boca_abierta_d': f"{boca_abierta_d:.1f}",
                'traslacion_d': f"{traslacion_d:.1f}",
                'boca_cerrada_i': f"{boca_cerrada_i:.1f}",
                'boca_abierta_i': f"{boca_abierta_i:.1f}",
                'traslacion_i': f"{traslacion_i:.1f}",
                'observaciones': observaciones
            }
            
            # Fusionar datos con la plantilla
            doc.render(context)
            
            # Guardar el documento en memoria para descargarlo
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            # Nombre de archivo limpio
            nombre_archivo = f"Informe_ATM_{nombre.replace(' ', '_')}.docx"
            
            st.download_button(
                label="💾 Confirmar Descarga de Word",
                data=bio,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.success("¡Informe listo! Haz clic arriba para guardarlo.")
            
        except Exception as e:
            st.error(f"Error al generar el Word: {e}. Asegúrate de tener el archivo 'plantilla_atm.docx' subido a GitHub.")
