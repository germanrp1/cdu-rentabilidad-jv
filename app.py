import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparativa JV - CDU", layout="wide")

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
st.title("🚀 Analizador JV: Comparativa Vertical")

with st.expander("🏠 Configuración del Proyecto e Inversión", expanded=True):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Totales:", value=430) # Valor inicial según depuración
    ref_m2 = c2.number_input("Reforma/m2:", value=1000)
    num_viv = c1.number_input("Nº Viviendas:", value=4)
    v_un = c2.number_input("P. Venta/Ud:", value=120000)
    itp = st.slider("ITP (%):", 0, 15, 7) / 100
    
    st.divider()
    inv_referencia = st.number_input("Inversión Total de Referencia (Base):", value=350000)
    
    # Cálculo de "Otros gastos" automático para cuadrar con la compra base (185k)
    compra_base = 185000
    itp_base = compra_base * itp
    reforma_base = m2 * ref_m2
    otros_gastos_def = inv_referencia - compra_base - itp_base - reforma_base
    
    otros_gastos = st.number_input("Otros gastos (Fijos para todas las opciones):", value=float(otros_gastos_def))

with st.expander("🤝 Reparto JV", expanded=False):
    ap_inv_pct = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    b_obj = st.number_input("Límite Tramo 1 (Beneficio Obj):", value=130000)
    r1_inv = st.slider("% Inversor Tramo 1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Inversor Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
data_dict = {}

for i, val in enumerate(escenarios):
    v_total = v_un * num_viv
    r_total = m2 * ref_m2
    
    if modo == "Precio de Compra":
        compra = val
        ben_total = v_total - (compra * (1 + itp)) - r_total - otros_gastos
    else:
        ben_total = val
        compra = (v_total - ben_total - r_total - otros_gastos) / (1 + itp)

    inv_t = (compra * (1 + itp)) + r_total + otros_gastos
    
    # Capitales (Aportación)
    cap_inv = inv_t * ap_inv_pct
    cap_ges = inv_t * (1 - ap_inv_pct)
    
    # Beneficios (Reparto)
    b1, b2 = min(ben_total, b_obj), max(0, ben_total - b_obj)
    gan_inv = (b1 * r1_inv) + (b2 * r2_inv)
    gan_ges = (b1 * (1 - r1_inv)) + (b2 * (1 - r1_inv))
    
    # ROI Anualizado
    roi_inv = (gan_inv / cap_inv) * (12/meses) if cap_inv > 0 else 0
    roi_ges = (gan_ges / cap_ges) * (12/meses) if cap_ges > 0 else 0
    roi_tot = (ben_total / inv_t) * (12/meses) if inv_t > 0 else 0

    col_name = f"Opción {i+1} ({val:,} €)"
    data_dict[col_name] = [
        f"{compra:,.0f} €",
        f"{inv_t:,.0f} €",
        f"{ben_total:,.0f} €",
        "---", # Separador visual
        f"{cap_inv:,.0f} €",
        f"{gan_inv:,.0f} €",
        f"{(cap_inv + gan_inv):,.0f} €",
        f"{roi_inv*100:.2f}%",
        "---",
        f"{cap_ges:,.0f} €",
        f"{gan_ges:,.0f} €",
        f"{(cap_ges + gan_ges):,.0f} €",
        f"{roi_ges*100:.2f}%",
        "---",
        f"{inv_t:,.0f} €",
        f"{ben_total:,.0f} €",
        f"{(inv_t + ben_total):,.0f} €",
        f"{roi_tot*100:.2f}%"
    ]

# Crear DataFrame con índices claros
indices = [
    "Precio Compra", "Inversión Total", "Beneficio Proyecto",
    "--- REPARTO INVERSOR ---",
    "Aportación Inversor", "Beneficio Inversor", "Capital Final Inv.", "ROI Anual Inv.",
    "--- REPARTO GESTOR ---",
    "Aportación Gestor", "Beneficio Gestor", "Capital Final Ges.", "ROI Anual Ges.",
    "--- TOTALES (SUMA) ---",
    "Aportación Total", "Beneficio Total", "Capital Final Total", "ROI Anual Total"
]

df_vertical = pd.DataFrame(data_dict, index=indices)

st.divider()
st.subheader("📊 Tabla Comparativa de Escenarios")
st.table(df_vertical)
  
