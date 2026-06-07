import streamlit as st
from docxtpl import DocxTemplate
import datetime
import io

# Configuración de la página original
st.set_page_config(page_title="Generador de Informes ATM", page_icon="🦷", layout="centered")

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

# --- MEDIDAS ECOGRÁFICAS EN PARALELO ---
st.markdown("### 📊 Medidas Ecográficas")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Lado Derecho")
    boca_cerrada_d = st.number_input("Boca Cerrada (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bcd")
    boca_abierta_d = st.number_input("Boca Abierta (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bad")

with col2:
    st.markdown("##### Lado Izquierdo")
    boca_cerrada_i = st.number_input("Boca Cerrada (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bci")
    boca_abierta_i = st.number_input("Boca Abierta (mm):", min_value=0.0, max_value=50.0, step=0.1, key="bai")

# --- CÁLCULO DE LA POSICIÓN DEL CÓNDILO ---
st.markdown("### 📐 Cálculo de la Posición del Cóndilo")
traslacion_d = boca_cerrada_d - boca_abierta_d
traslacion_i = boca_cerrada_i - boca_abierta_i

st.write(f"**Lado Derecho (Desplazamiento):** {traslacion_d:.1f} mm")
st.write(f"**Lado Izquierdo (Desplazamiento):** {traslacion_i:.1f} mm")

# --- COMENTARIOS / OBSERVACIONES ---
st.markdown("### ✍️ Conclusiones y Observaciones")
observaciones = st.text_area("Escriba aquí los hallazgos adicionales:", height=100)

# --- GENERACIÓN DEL ARCHIVO WORD ---
if st.button("🚀 DESCARGAR INFORME EN WORD"):
    if not nombre:
        st.error("⚠️ Por favor, introduzca el nombre del paciente antes de generar el informe.")
    else:
        try:
            doc = DocxTemplate("plantilla_atm.docx")
            
            f_nac_str = fecha_nac.strftime("%d/%m/%Y")
            f_eco_str = fecha_eco.strftime("%d/%m/%Y")
            
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
            
            doc.render(context)
            
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            nombre_archivo = f"Informe_ATM_{nombre.replace(' ', '_')}.docx"
            
            st.download_button(
                label="💾 Confirmar Descarga de Word",
                data=bio,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.success("¡Informe listo! Haz clic arriba para guardarlo.")
            
        except Exception as e:
            st.error(f"Error al generar el Word: {e}. Asegúrate de tener el archivo 'plantilla_atm.docx' en GitHub.")
