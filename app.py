# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

# main.py

import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc

# Configuración de la página
st.set_page_config(page_title="Información Académica", layout="wide")

# 1. Función para cargar datos con caché (Optimiza memoria para 100k registros)
@st.cache_data

def cargar_data():
    # En un escenario real, aquí cargarías tu CSV o base de datos
    # df = pd.read_csv("tus_datos.csv")
    #df = pd.read_excel('data/Consulta8.xlsx', sheet_name='Consulta8')
    df = pd.read_excel('data/Consulta10.xlsx', sheet_name='Consulta10')
    return pd.DataFrame(df)

df = cargar_data()

# --- INTERFAZ DE USUARIO (SIDEBAR) ---
st.sidebar.header("Filtros del Cubo")

with st.sidebar:
    periodo_sel = st.selectbox("Seleccione Periodo", df['Descripcion_Periodo'].unique())
    nivel_sel = st.selectbox("Seleccione Nivel", df['Descripcion_Nivel'].unique())
    
    # Filtros dinámicos basados en la selección anterior
    materias_disp = df[df['Descripcion_Nivel'] == nivel_sel]['Descripcion_Materia'].unique()
    materia_sel = st.selectbox("Seleccione Materia", materias_disp)
    paralelo_sel = st.selectbox("Seleccione Paralelo", df['Paralelo'].unique())
     
    umbral = st.slider("Umbral de bajo rendimiento", 0.0, 10.0, 7.0)

# --- LÓGICA DE FILTRADO (EL CUBO) ---
df_filtrado = df[
    (df['Descripcion_Periodo'] == periodo_sel) &
    (df['Descripcion_Nivel'] == nivel_sel) &
    (df['Descripcion_Materia'] == materia_sel) & 
    (df['Paralelo'] == paralelo_sel) 
]

# Estudiantes bajo el umbral
bajo_rendimiento = df_filtrado[df_filtrado['Nota1'] < umbral].sort_values('Nota1')
# --- VISUALIZACIÓN PRINCIPAL ---
st.title("📊 Dashboard de Rendimiento Académico")
st.markdown(f"Análisis para **{materia_sel}** - Paralelo **{paralelo_sel}**")

# Métricas rápidas
col1, col2, col3 = st.columns(3)
col1.metric("Total Estudiantes", len(df_filtrado))
col2.metric("En Riesgo", len(bajo_rendimiento), delta=len(bajo_rendimiento), delta_color="inverse")
col3.metric("Promedio Grupal", round(df_filtrado['Nota1'].mean(), 2))

# Layout de gráficos
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("Distribución de Notas")
    if not bajo_rendimiento.empty:
        fig = px.bar(
            bajo_rendimiento,
            x='Codigo_Estudiante',
            y='Nota1',
            color='Nota1',
            color_continuous_scale='Reds_r',
            text_auto='.2f'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("¡Felicidades! No hay estudiantes bajo el umbral seleccionado.")

with col_der:
    st.subheader("Lista de Estudiantes en Riesgo")
    st.dataframe(
        bajo_rendimiento[['Codigo_Estudiante', 'Nota1']],
        hide_index=True,
        use_container_width=True
    )

# Opción para descargar reporte
csv = bajo_rendimiento.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Descargar Lista en CSV",
    data=csv,
    file_name=f'bajo_rendimiento_{materia_sel}_{paralelo_sel}.csv',
    mime='text/csv',
)