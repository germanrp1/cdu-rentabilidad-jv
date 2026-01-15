import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="JV Analizador", layout="wide")

# CSS para forzar la cabecera en dos líneas y celdas compactas
st.markdown("""
    <style>
    .stTable { font-size: 11px !important; }
    th { white-space: pre-line !important; text-align: center !important; }
    td { white-space: nowrap !important; padding: 2px 5px !important; }
    </style>
    """, unsafe_allow_html=True)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Informe de Rentabilidad JV", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(45, 10, "Concepto", 1)
    for col in df.columns:
        pdf.cell(35, 10, str(col).replace('\n', ' '), 1)
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
    modo = st.radio("Calcular por:", ["Precio Compra", "Ben. Objetivo", "Precio Venta/Ud"])
    meses = st.number_input("Duración (meses):", value=12, min_value=1)
    st.divider()
    
    if modo == "Precio Venta/Ud":
        compra_fija = st.number_input("P. Compra Fijo (€):", value=185000)
        label_esc, v1, v2, v3 = "Venta/Ud (€)", 120000, 125000, 130000
    elif modo == "Precio Compra":
        label_esc, v1, v2, v3 = "Compra (€)", 185000, 200000, 215000
        compra_fija = 185000 
    else:
        label_esc, v1, v2, v3 = "Beneficio (€)", 130000, 150000, 110000
        compra_fija = 185000

    e1 = st.number_input(f"{label_esc} 1:", value=v1)
    e2 = st.number_input(f"{label_esc} 2:", value=v2)
    e3 = st.number_input(f"{label_esc} 3:", value=v3)

# --- PROYECTO ---
with st.expander("🏠 Configuración del Proyecto", expanded=True):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Total local:", value=430)
    num_viv = c2.number_input("Nº Viviendas:", value=4)
    ref_m2 = c1.number_input("Reforma/m2:", value=1000)
    itp_pct = st.slider("ITP (%):", 0, 15, 7) / 100
    
    # Cálculo por defecto para inversión de 350.000€
    compra_ref = compra_fija if modo == "Precio Venta/Ud" else 185000
    otros_def = 350000 - (compra_ref * (1 + itp_pct)) - (m2 * ref_m2)
    
    otros = st.number_input("Otros Gastos (Manual/Auto):", value=float(otros_def))

with st.expander("🤝 Reparto e Impuestos", expanded=False):
    pct_is = st.slider("% Sociedades (IS):", 0, 30, 25) / 100
    b_obj = st.number_input("Límite Tramo 1:", value=130000)
    ap_inv = st.slider("% Aport. Inv:", 0, 100, 90) / 100
    r1_inv = st.slider("% Reparto T1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Reparto T2:", 0, 100, 40) / 100

# --- LÓGICA ---
escenarios = [e1, e2, e3]
res = {}

for i, val in enumerate(escenarios):
    reforma_t = m2 * ref_m2
    if modo == "Precio Compra":
        compra, v_total = val, num_viv * 120000
        bruto = v_total - (compra * (1 + itp_pct)) - reforma_t - otros
    elif modo == "Ben. Objetivo":
        bruto, v_total = val, num_viv * 120000
        compra = (v_total - bruto - reforma_t - otros) / (1 + itp_pct)
    else:
        compra, v_total = compra_fija, num_viv * val
        bruto = v_total - (compra * (1 + itp_pct)) - reforma_t - otros

    inv_t = (compra * (1 + itp_pct)) + reforma_t + otros
    neto = bruto - max(0, bruto * pct_is)
    c_inv, c_ges = inv_t * ap_inv, inv_t * (1 - ap_inv)
    b1_n = min(neto, b_obj * (1 - pct_is))
    g_inv = (b1_n * r1_inv) + (max(0, neto - b1_n) * r2_inv)
    g_ges = neto - g_inv

    # Cabecera en dos líneas usando \n
    col_head = f"Precio Venta\n{ (v_total/num_viv):,.0f} €"
    res[col_head] = [
        f"{compra:,.0f}€", f"{inv_t:,.0f}€", f"{bruto:,.0f}€", f"{neto:,.0f}€",
        "---",
        f"{c_inv:,.0f}€", f"{g_inv:,.0f}€", f"{(c_inv+g_inv):,.0f}€", f"{(g_inv/c_inv)*(12/meses)*100:.1f}%",
        "---",
        f"{c_ges:,.0f}€", f"{g_ges:,.0f}€", f"{(c_ges+g_ges):,.0f}€", f"{(g_ges/c_ges)*(12/meses)*100:.1f}%",
        "---",
        f"{inv_t:,.0f}€", f"{neto:,.0f}€", f"{(inv_t+neto):,.0f}€", f"{(neto/inv_t)*(12/meses)*100:.1f}%"
    ]

indices = [
    "P. Compra", "Inv. Total", "Ben. Bruto", "Ben. NETO",
    "Result. Invers.", "Aport. Inv.", "Ganancia Inv.", "Total Inv.", "ROI Neto Inv.",
    "Result. Gestor", "Aport. Ges.", "Ganancia Ges.", "Total Ges.", "ROI Neto Ges.",
    "TOTALES PROY.", "Aport. Total", "Ganancia Total", "Capital Final", "ROI Neto Proy."
]

df = pd.DataFrame(res, index=indices)
st.divider()
st.table(df)

if st.button("🚀 Descargar PDF"):
    try:
        st.download_button("✅ Click para bajar", create_pdf(df), "estudio_jv.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
