import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

st.set_page_config(page_title="Comparativa JV - Pro", layout="wide")

# --- FUNCION PARA GENERAR PDF ---
def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Informe de Comparativa de Inversion JV", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 10)
    # Cabeceras
    col_width = 190 / (len(df.columns) + 1)
    pdf.cell(col_width + 10, 10, "Concepto", 1)
    for col in df.columns:
        pdf.cell(col_width - 2, 10, str(col), 1)
    pdf.ln()
    
    # Filas
    pdf.set_font("Arial", "", 9)
    for i in range(len(df)):
        pdf.cell(col_width + 10, 8, str(df.index[i]), 1)
        for val in df.iloc[i]:
            pdf.cell(col_width - 2, 8, str(val), 1)
        pdf.ln()
    
    return pdf.output(dest="S").encode("latin-1")

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Controles")
modo = st.sidebar.radio("Calcular por:", ["Precio de Compra", "Beneficio Objetivo"])
meses = st.sidebar.number_input("Duración (meses):", value=12, min_value=1)

st.sidebar.subheader("📊 Comparativa")
if modo == "Precio de Compra":
    l_esc, v1, v2, v3 = "Compra (€)", 185000, 200000, 215000
else:
    l_esc, v1, v2, v3 = "Beneficio (€)", 130000, 150000, 110000

esc1 = st.sidebar.number_input(f"{l_esc} 1", value=v1)
esc2 = st.sidebar.number_input(f"{l_esc} 2", value=v2)
esc3 = st.sidebar.number_input(f"{l_esc} 3", value=v3)

# --- CUERPO PRINCIPAL ---
st.title("🚀 Analizador JV: Modelo Post-Impuestos")

with st.expander("🏠 Configuración del Proyecto e Inversión", expanded=True):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Totales:", value=430)
    ref_m2 = c2.number_input("Reforma/m2:", value=1000)
    num_viv = c1.number_input("Nº Viviendas:", value=4)
    v_un = c2.number_input("P. Venta/Ud:", value=120000)
    itp = st.slider("ITP (%):", 0, 15, 7) / 100
    
    st.divider()
    inv_referencia = st.number_input("Inversión Total de Referencia (Base):", value=350000)
    compra_base = 185000
    itp_base = compra_base * itp
    reforma_base = m2 * ref_m2
    otros_gastos_def = inv_referencia - compra_base - itp_base - reforma_base
    otros_gastos = st.number_input("Otros gastos (Fijos):", value=float(otros_gastos_def))

with st.expander("🤝 Reparto e Impuestos", expanded=True):
    col_is1, col_is2 = st.columns(2)
    pct_is = col_is1.slider("% Impuesto Sociedades:", 0, 30, 25) / 100
    b_obj = col_is2.number_input("Límite Tramo 1 (Bruto):", value=130000)
    
    ap_inv_pct = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    r1_inv = st.slider("% Inversor Tramo 1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Inversor Zona Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
data_dict = {}

for i, val in enumerate(escenarios):
    v_total = v_un * num_viv
    r_total = m2 * ref_m2
    
    if modo == "Precio de Compra":
        compra = val
        ben_bruto = v_total - (compra * (1 + itp)) - r_total - otros_gastos
    else:
        ben_bruto = val
        compra = (v_total - ben_bruto - r_total - otros_gastos) / (1 + itp)

    inv_t = (compra * (1 + itp)) + r_total + otros_gastos
    
    # Impuestos
    impuesto_cuota = max(0, ben_bruto * pct_is)
    ben_neto = ben_bruto - impuesto_cuota
    
    # Capitales
    cap_inv, cap_ges = inv_t * ap_inv_pct, inv_t * (1 - ap_inv_pct)
    
    # Reparto Waterfall (Sobre Neto)
    # Si prefieres repartir el BRUTO y que cada uno pague su parte, dímelo. 
    # Aquí calculamos el reparto sobre lo que queda después de pagar el IS de la sociedad.
    b1_n, b2_n = min(ben_neto, b_obj*(1-pct_is)), max(0, ben_neto - b_obj*(1-pct_is))
    gan_inv = (b1_n * r1_inv) + (b2_n * r2_inv)
    gan_ges = ben_neto - gan_inv
    
    # ROIs Netos Anualizados
    roi_inv = (gan_inv / cap_inv) * (12/meses) if cap_inv > 0 else 0
    roi_ges = (gan_ges / cap_ges) * (12/meses) if cap_ges > 0 else 0

    col_name = f"Opción {i+1}"
    data_dict[col_name] = [
        f"{compra:,.0f} €", f"{inv_t:,.0f} €", f"{ben_bruto:,.0f} €", f"{impuesto_cuota:,.0f} €", f"{ben_neto:,.0f} €",
        "---",
        f"{cap_inv:,.0f} €", f"{gan_inv:,.0f} €", f"{(cap_inv + gan_inv):,.0f} €", f"{roi_inv*100:.2f}%",
        "---",
        f"{cap_ges:,.0f} €", f"{gan_ges:,.0f} €", f"{(cap_ges + gan_ges):,.0f} €", f"{roi_ges*100:.2f}%"
    ]

indices = [
    "Precio Compra", "Inversión Total", "Beneficio Bruto", "Impuesto Soc. (IS)", "Beneficio NETO",
    "--- REPARTO INVERSOR (NETO) ---",
    "Aportación Inv.", "Beneficio Inv.", "Capital Final Inv.", "ROI Neto Anual Inv.",
    "--- REPARTO GESTOR (NETO) ---",
    "Aportación Ges.", "Beneficio Ges.", "Capital Final Ges.", "ROI Neto Anual Ges."
]

df_vertical = pd.DataFrame(data_dict, index=indices)

st.divider()
st.subheader("📊 Comparativa Final Post-Impuestos")
st.table(df_vertical)

# --- BOTÓN PDF ---
pdf_data = create_pdf(df_vertical)
st.download_button(
    label="📥 Descargar Comparativa en PDF",
    data=pdf_data,
    file_name="comparativa_jv.pdf",
    mime="application/pdf",
    )
    
