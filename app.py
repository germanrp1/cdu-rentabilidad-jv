import streamlit as st
import pandas as pd

st.set_page_config(page_title="Optimizador JV - CDU", layout="wide")

st.title("🚀 Analizador de Inversión y Joint Venture (CDU)")

# --- SIDEBAR: PARÁMETROS FIJOS ---
st.sidebar.header("Configuración del Proyecto")
m2 = st.sidebar.number_input("Metros Totales (m²)", value=120)
reforma_m2 = st.sidebar.number_input("Precio Reforma / m²", value=1000)
reforma_total = m2 * reforma_m2
st.sidebar.info(f"Total Reforma: {reforma_total:,} €")

num_viv = st.sidebar.number_input("Nº de Viviendas", value=4)
venta_un = st.sidebar.number_input("Precio Venta / Vivienda (Suelo)", value=120000)
itp_pct = st.sidebar.slider("ITP (%)", 0, 15, 7) / 100

st.sidebar.header("Reparto Joint Venture")
ap_inv_pct = st.sidebar.slider("% Aportación Inversor", 0, 100, 90) / 100
ap_ges_pct = 1 - ap_inv_pct

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Tramos de Beneficio")
    ben_obj = st.number_input("Beneficio Objetivo (€)", value=130000)
    
    st.write("**Tramo 1 (Hasta objetivo):**")
    c1, c2 = st.columns(2)
    rep1_inv = c1.number_input("% Inv. (T1)", value=55) / 100
    st.write(f"Gestor: {100-(rep1_inv*100):.0f}%")
    
    st.write("**Tramo 2 (Zona Bonus):**")
    c3, c4 = st.columns(2)
    rep2_inv = c3.number_input("% Inv. (Bonus)", value=40) / 100
    st.write(f"Gestor: {100-(rep2_inv*100):.0f}%")

with col2:
    st.subheader("⚙️ Modo de Cálculo")
    modo = st.radio("¿Qué quieres calcular?", 
                    ["Beneficio (fijando Compra)", "Compra Máxima (fijando Beneficio)"])
    
    meses = st.number_input("Duración estimada (meses)", value=12, min_value=1)

# --- ESCENARIOS ---
st.divider()
st.subheader("📊 Comparativa de Escenarios")

if modo == "Beneficio (fijando Compra)":
    label_esc = "Introduce 3 Precios de Compra"
    v1, v2, v3 = 185000, 200000, 215000
else:
    label_esc = "Introduce 3 Objetivos de Beneficio"
    v1, v2, v3 = 130000, 150000, 110000

c_esc1, c_esc2, c_esc3 = st.columns(3)
esc1 = c_esc1.number_input(f"{label_esc} (1)", value=v1)
esc2 = c_esc2.number_input(f"{label_esc} (2)", value=v2)
esc3 = c_esc3.number_input(f"{label_esc} (3)", value=v3)

escenarios = [esc1, esc2, esc3]
resultados = []

# Otros gastos fijos según tu CDU (ajuste a 350k)
otros_gastos_base = 32050 

for val in escenarios:
    if modo == "Beneficio (fijando Compra)":
        compra = val
        venta_total = venta_un * num_viv
        beneficio = venta_total - (compra * (1 + itp_pct)) - reforma_total - otros_gastos_base
    else:
        beneficio = val
        venta_total = venta_un * num_viv
        compra = (venta_total - beneficio - reforma_total - otros_gastos_base) / (1 + itp_pct)
    
    inv_total = (compra * (1 + itp_pct)) + reforma_total + otros_gastos_base
    cap_inv = inv_total * ap_inv_pct
    cap_ges = inv_total * ap_ges_pct
    
    # Waterfall
    b1 = min(beneficio, ben_obj)
    b2 = max(0, beneficio - ben_obj)
    
    gan_inv = (b1 * rep1_inv) + (b2 * rep2_inv)
    gan_ges = (b1 * (1 - rep1_inv)) + (b2 * (1 - rep2_inv))
    
    roi_inv = (gan_inv / cap_inv) if cap_inv > 0 else 0
    roi_ges = (gan_ges / cap_ges) if cap_ges > 0 else 0
    
    resultados.append({
        "Variable": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Beneficio Total": f"{beneficio:,.0f} €",
        "Inv. Total": f"{inv_total:,.0f} €",
        "Inversor (Cobro)": f"{(cap_inv + gan_inv):,.0f} €",
        "ROI Inv.": f"{roi_inv*100:.1f}%",
        "ROI Inv. Anual": f"{(roi_inv * (12/meses))*100:.1f}%",
        "Gestor (Cobro)": f"{(cap_ges + gan_ges):,.0f} €",
        "ROI Ges. Anual": f"{(roi_ges * (12/meses))*100:.1f}%"
    })

df = pd.DataFrame(resultados)
st.table(df)

st.caption(f"Nota: 'Otros gastos' ajustados a {otros_gastos_base:,} € para cuadrar con el presupuesto de 350k €.")
