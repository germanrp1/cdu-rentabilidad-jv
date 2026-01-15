import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analizador JV - CDU", layout="wide")

st.title("🚀 Analizador de Inversión y Joint Venture (CDU)")

# --- BARRA LATERAL (SLIDE) ---
with st.sidebar:
    st.header("⚙️ Configuración General")
    modo = st.radio("¿Qué quieres calcular?", 
                    ["Beneficio (fijando Compra)", "Compra Máxima (fijando Beneficio)"])
    
    meses = st.number_input("Duración estimada (meses)", value=12, min_value=1)
    
    st.divider()
    st.subheader("📊 Escenarios a comparar")
    if modo == "Beneficio (fijando Compra)":
        label_esc = "Precios de Compra"
        v1, v2, v3 = 185000, 200000, 215000
    else:
        label_esc = "Objetivos de Beneficio"
        v1, v2, v3 = 130000, 150000, 110000

    esc1 = st.number_input(f"{label_esc} 1", value=v1)
    esc2 = st.number_input(f"{label_esc} 2", value=v2)
    esc3 = st.number_input(f"{label_esc} 3", value=v3)

# --- BLOQUES DESPLEGABLES EN EL CUERPO PRINCIPAL ---
with st.expander("🏠 Datos del Inmueble y Reforma", expanded=False):
    col_a, col_b = st.columns(2)
    m2 = col_a.number_input("Metros Totales (m²)", value=120)
    reforma_m2 = col_b.number_input("Precio Reforma / m²", value=1000)
    
    col_c, col_d = st.columns(2)
    num_viv = col_c.number_input("Nº de Viviendas", value=4)
    venta_un = col_d.number_input("Precio Venta / Vivienda (Suelo)", value=120000)
    
    itp_pct = st.slider("ITP (%)", 0, 15, 7) / 100
    reforma_total = m2 * reforma_m2
    st.info(f"**Total Reforma estimado:** {reforma_total:,} €")

with st.expander("🤝 Estructura de la Joint Venture", expanded=False):
    col_e, col_f = st.columns(2)
    ap_inv_pct = col_e.slider("% Aportación Inversor", 0, 100, 90) / 100
    st.write(f"**Aportación Gestor:** {(1 - ap_inv_pct)*100:.0f}%")
    
    otros_gastos_base = st.number_input("Bolsa 'Otros Gastos' (Ajuste)", value=32050)

with st.expander("💰 Tramos de Beneficio y Bonus", expanded=False):
    ben_obj = st.number_input("Beneficio Objetivo (€)", value=130000)
    
    st.write("**Reparto Tramo 1 (Hasta objetivo):**")
    col_g, col_h = st.columns(2)
    rep1_inv = col_g.number_input("% Inversor (T1)", value=55) / 100
    st.write(f"Gestor (T1): {100-(rep1_inv*100):.0f}%")
    
    st.write("**Reparto Tramo 2 (Zona Bonus):**")
    col_i, col_j = st.columns(2)
    rep2_inv = col_i.number_input("% Inversor (Bonus)", value=40) / 100
    st.write(f"Gestor (Bonus): {100-(rep2_inv*100):.0f}%")

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
resultados = []

for val in escenarios:
    venta_total = venta_un * num_viv
    if modo == "Beneficio (fijando Compra)":
        compra = val
        beneficio = venta_total - (compra * (1 + itp_pct)) - reforma_total - otros_gastos_base
    else:
        beneficio = val
        compra = (venta_total - beneficio - reforma_total - otros_gastos_base) / (1 + itp_pct)
    
    inv_total = (compra * (1 + itp_pct)) + reforma_total + otros_gastos_base
    cap_inv = inv_total * ap_inv_pct
    cap_ges = inv_total * (1 - ap_inv_pct)
    
    b1 = min(beneficio, ben_obj)
    b2 = max(0, beneficio - ben_obj)
    
    gan_inv = (b1 * rep1_inv) + (b2 * rep2_inv)
    gan_ges = (b1 * (1 - rep1_inv)) + (b2 * (1 - rep2_inv))
    
    roi_inv = (gan_inv / cap_inv) if cap_inv > 0 else 0
    roi_ges = (gan_ges / cap_ges) if cap_ges > 0 else 0
    
    resultados.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Beneficio": f"{beneficio:,.0f} €",
        "Inversión Total": f"{inv_total:,.0f} €",
        "Inv. (Cobro)": f"{(cap_inv + gan_inv):,.0f} €",
        "        "ROI Inv. Anual": f"{(roi_inv * (12/meses))*100:.1f}%",
        "Gestor (Cobro)": f"{(cap_ges + gan_ges):,.0f} €",
        "ROI Ges. Anual": f"{(roi_ges * (12/meses))*100:.1f}%"
    })

# --- MOSTRAR RESULTADOS ---
st.divider()
st.subheader("📊 Tabla de Resultados")
df = pd.DataFrame(resultados)
st.table(df)

st.success("Cálculos realizados con éxito. Modifica los parámetros arriba o en el slide para actualizar.")
