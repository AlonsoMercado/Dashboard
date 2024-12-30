import streamlit as st
import pandas as pd
import plotly.express as px

link_compras="https://usmcl-my.sharepoint.com/:x:/g/personal/alonso_mercado_usm_cl/Ecer7Lg47YZKsEC5fpJN0_ABRe1n88BFforXfUVWmXATsA?e=KUOLbz"
link_ventas="https://usmcl-my.sharepoint.com/:x:/g/personal/alonso_mercado_usm_cl/EX65eEllakdNrwI8FdShcNMBW0mPbK8XQ_EX0HHBWOEyQw?e=1ybHLh"
# Configuración de la página
st.set_page_config(layout="wide", page_title="Dashboard de Ventas y Compras", page_icon="📊")

# Cargar datos
@st.cache_data
def cargar_datos():
    df_ventas = pd.read_excel('KEYPROCESS_REPORTE_VENTA_20241216152610.xlsx')
    df_compras = pd.read_excel('KEYPROCESS_REPORTE_COMPRA_20241216153042.xlsx')
    return df_ventas, df_compras

df_ventas, df_compras = cargar_datos()
meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
# Preparar datos
def preparar_datos(df):
    df = df.rename(columns={'FECHA': 'FECHA_TRANSACCION', 'FECHA DOCUMENTO': 'FECHA_TRANSACCION',
                            'TOTAL': 'MONTO', 'RAZON SOCIAL': 'CLIENTE/PROVEEDOR', 'FORMA DE PAGO': 'FORMA_DE_PAGO'})
    df['FECHA_TRANSACCION'] = pd.to_datetime(df['FECHA_TRANSACCION'], dayfirst=True)
    df['FORMA_DE_PAGO'] = df['FORMA_DE_PAGO'].fillna("No indica medio").str.strip().str.lower()
    df['FORMA_DE_PAGO'] = df['FORMA_DE_PAGO'].replace({'credito': 'crédito'})
    df['AÑO'] = df['FECHA_TRANSACCION'].dt.year
    df['MES'] = df['FECHA_TRANSACCION'].dt.month.map(meses)
    return df

df_ventas = preparar_datos(df_ventas)
df_compras = preparar_datos(df_compras)

# Sidebar: filtros
st.sidebar.header("Filtros")
rango_fecha = st.sidebar.date_input("Rango de Fechas", 
    [df_ventas['FECHA_TRANSACCION'].min(), df_ventas['FECHA_TRANSACCION'].max()]
)
años_seleccionados = st.sidebar.multiselect("Años", sorted(df_ventas['AÑO'].unique()), default=None)
meses_seleccionados = st.sidebar.multiselect("Meses", sorted(df_ventas['MES'].unique()), default=None)
forma_pago = st.sidebar.multiselect("Forma de Pago", df_ventas['FORMA_DE_PAGO'].unique(), default=None)

# Función de filtrado
def filtrar_datos(df):
    df_filtrado = df[
        (df['FECHA_TRANSACCION'] >= pd.to_datetime(rango_fecha[0])) &
        (df['FECHA_TRANSACCION'] <= pd.to_datetime(rango_fecha[1]))
    ]
    if años_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['AÑO'].isin(años_seleccionados)]
    if meses_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['MES'].isin(meses_seleccionados)]
    if forma_pago:
        df_filtrado = df_filtrado[df_filtrado['FORMA_DE_PAGO'].isin(forma_pago)]
    return df_filtrado

# Filtrar datos
ventas_filtradas = filtrar_datos(df_ventas)
compras_filtradas = filtrar_datos(df_compras)

# Filtrar datos
ventas_filtradas = filtrar_datos(df_ventas)
compras_filtradas = filtrar_datos(df_compras)

# Layout: Secciones principales
st.title("📊 Dashboard de Ventas y Compras")

# Gráficos de Ventas
st.header("📈 Ventas")
col1, col2, col3 = st.columns(3)

# Gráfico 1: Top 10 Clientes por monto
with col1:
    if not ventas_filtradas.empty:
        top_clientes = ventas_filtradas.groupby('CLIENTE/PROVEEDOR')['MONTO'].sum().nlargest(10).reset_index()
        fig1 = px.bar(top_clientes, x='MONTO', y='CLIENTE/PROVEEDOR', orientation='h', title="Top 10 Clientes por Monto")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")

# Gráfico 2: Acumulado mensual
with col2:
    if not ventas_filtradas.empty:
        ventas_acumuladas = ventas_filtradas.groupby(ventas_filtradas['FECHA_TRANSACCION'].dt.to_period('M')).sum().reset_index()
        ventas_acumuladas['FECHA_TRANSACCION'] = ventas_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
        fig2 = px.line(ventas_acumuladas, x='FECHA_TRANSACCION', y='MONTO', title="Acumulado Mensual de Ventas")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")

# Gráfico 3: Distribución por forma de pago
with col3:
    if not ventas_filtradas.empty:
        forma_pago_ventas = ventas_filtradas['FORMA_DE_PAGO'].value_counts().reset_index()
        forma_pago_ventas.columns = ['FORMA_DE_PAGO', 'Cantidad']
        fig3 = px.pie(forma_pago_ventas, names='FORMA_DE_PAGO', values='Cantidad', title="Distribución por Forma de Pago (Ventas)")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")

# Gráficos de Compras
st.header("📉 Compras")
col4, col5, col6 = st.columns(3)

# Gráfico 4: Top 10 Proveedores por monto
with col4:
    if not compras_filtradas.empty:
        top_proveedores = compras_filtradas.groupby('CLIENTE/PROVEEDOR')['MONTO'].sum().nlargest(10).reset_index()
        fig4 = px.bar(top_proveedores, x='MONTO', y='CLIENTE/PROVEEDOR', orientation='h', title="Top 10 Proveedores por Monto")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")

# Gráfico 5: Acumulado mensual
with col5:
    if not compras_filtradas.empty:
        compras_acumuladas = compras_filtradas.groupby(compras_filtradas['FECHA_TRANSACCION'].dt.to_period('M')).sum().reset_index()
        compras_acumuladas['FECHA_TRANSACCION'] = compras_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
        fig5 = px.line(compras_acumuladas, x='FECHA_TRANSACCION', y='MONTO', title="Acumulado Mensual de Compras")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")

# Gráfico 6: Distribución por forma de pago
with col6:
    if not compras_filtradas.empty:
        forma_pago_compras = compras_filtradas['FORMA_DE_PAGO'].value_counts().reset_index()
        forma_pago_compras.columns = ['FORMA_DE_PAGO', 'Cantidad']
        fig6 = px.pie(forma_pago_compras, names='FORMA_DE_PAGO', values='Cantidad', title="Distribución por Forma de Pago (Compras)")
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en este gráfico.")
