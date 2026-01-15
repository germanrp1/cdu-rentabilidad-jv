import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analizador JV", layout="wide")

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
st.title("🚀 Analizador JV - CDU")

with st.expander("🏠 Datos Proyecto", expanded=False):
    m2 = st.number_input("Metros Totales:", value=120)
    ref_m2 = st.number_input("Reforma/m2:", value=1000)
    num_viv = st.number_input("Nº Viviendas:", value=4)
    v_un = st.number_input("P. Venta/Ud:", value=120000)
    itp = st.slider("ITP (%):", 0, 15, 7) / 100

with st.expander("🤝 Estructura y Reparto", expanded=True):
    ap_inv = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    otros = st.number_input("Otros Gastos:", value=32050)
    b_obj = st.number_input("Límite Tramo 1 (Beneficio Obj):", value=130000)
    r1_inv = st.slider("% Inversor Tramo 1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Inversor Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
filas = []

for val in escenarios:
    v_total = v_un * num_viv
    r_total = m2 * ref_m2
    
    if modo == "Precio de Compra":
        compra = val
        ben = v_total - (compra * (1 + itp)) - r_total - otros
    else:
        ben = val
        compra = (v_total - ben - r_total - otros) / (1 + itp)
    
    # Inversión y Capitales
    inv_t = (compra * (1 + itp)) + r_total + otros
    cap_inv = inv_t * ap_inv
    cap_ges = inv_t * (1 - ap_inv)
    
    # Reparto Waterfall
    b1 = min(ben, b_obj)
    b2 = max(0, ben - b_obj)
    
    gan_inv = (b1 * r1_inv) + (b2 * r2_inv)
    gan_ges = (b1 * (1 - r1_inv)) + (b2 * (1 - r1_inv))
    
    # Cobros Totales (Capital + Ganancia)
    cobro_inv = cap_inv + gan_inv
    cobro_ges = cap_ges + gan_ges
    
    # ROIs Anualizados
    roi_an_inv = (gan_inv / cap_inv) * (12/meses) if cap_inv > 0 else 0
    roi_an_ges = (gan_ges / cap_ges) * (12/meses) if cap_ges > 0 else 0
    
    filas.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Beneficio": f"{ben:,.0f} €",
        "ROI Inv. Anual": f"{roi_an_inv*100:.1f}%",
        "ROI Ges. Anual": f"{roi_an_ges*100:.1f}%",
        "Total Inversor": f"{cobro_inv:,.0f} €",
        "Total Gestor": f"{cobro_ges:,.0f} €"
    })

st.divider()
st.subheader("📊 Tabla Comparativa Final")
st.table(pd.DataFrame(filas))

# Mensaje de confirmación
st.info(f"Capital aportado Inversor: {cap_inv:,.0f} € | Gestor: {cap_ges:,.0f} €")
