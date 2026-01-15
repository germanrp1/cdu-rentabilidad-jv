import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="JV Analizador", layout="wide")

# CSS para optimizar el espacio
st.markdown("""
    <style>
    .stTable { font-size: 11px !important; }
    th { white-space: nowrap !important; }
    td { white-space: nowrap !important; padding: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PDF ---
def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Informe de Rentabilidad JV", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(45, 10, "Concepto", 1)
    for col in df.columns:
        pdf.cell(35, 10, str(col), 1)
    pdf.ln()
    pdf.set_font("Arial", "", 8)
    for i in range(len(df)):
        concepto = str(df.index[i]).replace("€", "Eur")
        pdf.cell(45, 8, concepto, 1)
        for val in df.iloc[i]:
            clean_val = str(val).replace("€", "E").replace("%", " pct")
            pdf.cell(35, 8, clean_val, 1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1", errors="ignore")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes")
    # Añadida la tercera opción de modo
    modo = st.radio("Calcular por:", ["Precio Compra", "Ben. Objetivo", "Precio Venta/Ud"])
    meses = st.number_input("Duración (meses):", value=12, min_value=1)
    st.divider()
    
    # Lógica de valores iniciales según el modo elegido
    if modo == "Precio Compra":
        label_esc, v1, v2, v3 = "Compra (€)", 185000, 200000, 215000
    elif modo == "Ben. Objetivo":
        label_esc, v1, v2, v3 = "Beneficio (€)", 130000, 150000, 110000
    else: # Modo Precio Venta/Ud
        label_esc, v1, v2, v3 = "Venta/Ud (€)", 120000, 125000, 130000
        
    e1 = st.number_input(f"{label_esc} 1:", value=v1)
    e2 = st.number_input(f"{label_esc} 2:", value=v2)
    e3 = st.number_input(f"{label_esc} 3:", value=v3)

# --- DATOS PROYECTO ---
with st.expander("🏠 Proyecto e Inversión", expanded=True):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Total local:", value=430)
    num_viv = c2.number_input("Nº Viviendas:", value=4)
    ref_m2 = c1.number_input("Reforma/m2:", value=1000)
    itp_pct = st.slider("ITP (%):", 0, 15, 7) / 100
    inv_ref = st.number_input("Inversión Base (350k):", value=350000)
    
    # Otros gastos fijos calculados
    gastos_fijos = inv_ref - 185000 - (185000 * itp_pct) - (m2 * ref_m2)
    otros = st.number_input("Otros Gastos:", value=float(gastos_fijos))

with st.expander("🤝 Reparto e Impuestos", expanded=False):
    pct_is = st.slider("% Sociedades (IS):", 0, 30, 25) / 100
    b_obj = st.number_input("Límite Tramo 1:", value=130000)
    ap_inv = st.slider("% Aport. Inv:", 0, 100, 90) / 100
    r1_inv = st.slider("% Reparto T1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Reparto T2:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [e1, e2, e3]
res = {}

for i, val in enumerate(escenarios):
    reforma_total = m2 * ref_m2
    
    if modo == "Precio Compra":
        compra = val
        venta_total = num_viv * 120000 # Precio venta por defecto si no es el modo activo
        bruto = venta_total - (compra * (1 + itp_pct)) - reforma_total - otros
    elif modo == "Ben. Objetivo":
        bruto = val
        venta_total = num_viv * 120000
        compra = (venta_total - bruto - reforma_total - otros) / (1 + itp_pct)
    else: # NUEVO MODO: Precio Venta/Ud (Compra fija en e1)
        compra = e1 # Usamos el valor de la Opción 1 como compra fija
        venta_total = num_viv * val # El valor del escenario es el precio de venta unitario
        bruto = venta_total - (compra * (1 + itp_pct)) - reforma_total - otros

    total_inv = (compra * (1 + itp_pct)) + reforma_total + otros
    is_pago = max(0, bruto * pct_is)
    neto = bruto - is_pago
    
    c_inv, c_ges = total_inv * ap_inv, total_inv * (1 - ap_inv)
    b1_n = min(neto, b_obj * (1 - pct_is))
    g_inv = (b1_n * r1_inv) + (max(0, neto - b1_n) * r2_inv)
    g_ges = neto - g_inv
    
    roi_inv = (g_inv/c_inv)*(12/meses)*100 if c_inv > 0 else 0
    roi_ges = (g_ges/c_ges)*(12/meses)*100 if c_ges > 0 else 0
    roi_tot = (neto/total_inv)*(12/meses)*100 if total_inv > 0 else 0

    col = f"Op. {i+1}"
    # Si estamos en modo Precio Venta, mostramos el precio de venta en la tabla para claridad
    label_venta = f"Venta: {val:,.0f}€/ud" if modo == "Precio Venta/Ud" else f"Venta: {(venta_total/num_viv):,.0f}€/ud"
    
    res[col] = [
        label_venta,
        f"{compra:,.0f}€", f"{total_inv:,.0f}€", f"{bruto:,.0f}€", f"{is_pago:,.0f}€", f"{neto:,.0f}€",
        "---",
        f"{c_inv:,.0f}€", f"{g_inv:,.0f}€", f"{(c_inv+g_inv):,.0f}€", f"{roi_inv:.1f}%",
        "---",
        f"{c_ges:,.0f}€", f"{g_ges:,.0f}€", f"{(c_ges+g_ges):,.0f}€", f"{roi_ges:.1f}%",
        "---",
        f"{total_inv:,.0f}€", f"{neto:,.0f}€", f"{(total_inv+neto):,.0f}€", f"{roi_tot:.1f}%"
    ]

indices = [
    "Escenario Venta", "P. Compra", "Inv. Total", "Ben. Bruto", "Impuesto (IS)", "Ben. NETO",
    "Result. Invers.",
    "Aport. Inv.", "Ganancia Inv.", "Total Inv.", "ROI Neto Inv.",
    "Result. Gestor",
    "Aport. Ges.", "Ganancia Ges.", "Total Ges.", "ROI Neto Ges.",
    "TOTALES PROY.",
    "Aport. Total", "Ganancia Total", "Capital Final", "ROI Neto Proy."
]

df = pd.DataFrame(res, index=indices)

st.divider()
st.subheader("📊 Tabla de Comparativa")
st.table(df)

if st.button("🚀 Generar y Descargar PDF"):
    try:
        pdf_bytes = create_pdf(df)
        st.download_button(label="✅ Descargar Archivo", data=pdf_bytes, file_name="estudio_rentabilidad.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
      
