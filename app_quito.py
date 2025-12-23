import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

st.set_page_config(page_title="Quito Interactivo", layout="wide")

# 1. LISTA COMPLETA DE LUGARES (Sin cambios)
LUGARES = {
    "Museo de la Ciudad": [-0.2238, -78.5138], "Alberto Mena Caamaño": [-0.2205, -78.5118],
    "Casa del Alabado": [-0.2215, -78.5152], "Museo Camilo Egas": [-0.2185, -78.5085],
    "Museo Casa de Sucre": [-0.2219, -78.5111], "Museo Maria Augusta Urrutia": [-0.2212, -78.5115],
    "Museo Franciscano": [-0.2210, -78.5155], "Museo del Pasillo": [-0.2225, -78.5130],
    "Museo de la Moneda": [-0.2208, -78.5110], "Museo de Arte Colonial": [-0.2195, -78.5105],
    "Museo Manuela Sáenz": [-0.2230, -78.5125], "Centro Cultural Metropolitano": [-0.2204, -78.5116],
    "Centro de Arte Contemporáneo": [-0.2165, -78.5042], "Plaza de la Independencia": [-0.2202, -78.5123],
    "Plaza de San Francisco": [-0.2210, -78.5147], "Plaza de Santo Domingo": [-0.2235, -78.5120],
    "Plaza del Teatro": [-0.2188, -78.5100], "Calle La Ronda": [-0.2248, -78.5128],
    "Basílica del Voto Nacional": [-0.2146, -78.5074]
}

@st.cache_resource
def obtener_grafo():
    # Descarga el grafo una sola vez para evitar lentitud
    return ox.graph_from_address("Plaza de la Independencia, Quito", dist=2000, network_type='all')

G = obtener_grafo()

st.title("📍 Ruta Interactiva de Museos - Quito")

# Inicializar estados si no existen
if 'punto_inicio' not in st.session_state:
    st.session_state.punto_inicio = None

# 2. COLUMNAS
col1, col2 = st.columns([1, 2])

with col1:
    st.info("1. Toca el mapa para marcar tu inicio.\n2. Elige destino abajo.")
    transporte = st.selectbox("Modo:", ["Caminando", "Auto"])
    destino_n = st.selectbox("Destino:", sorted(LUGARES.keys()))
    
    if st.button("Limpiar Ubicación"):
        st.session_state.punto_inicio = None
        st.rerun()

# 3. CREACIÓN DEL MAPA
m = folium.Map(location=[-0.2202, -78.5123], zoom_start=16)

# Marcadores de lugares
for nom, coord in LUGARES.items():
    folium.Marker(coord, tooltip=nom, icon=folium.Icon(color="red", icon="landmark", prefix="fa")).add_to(m)

# Lógica de ruta (se calcula antes de mostrar el mapa para evitar el error de Node)
ruta_coords = []
if st.session_state.punto_inicio:
    try:
        p1 = st.session_state.punto_inicio
        p2 = LUGARES[destino_n]
        n1 = ox.nearest_nodes(G, p1[1], p1[0])
        n2 = ox.nearest_nodes(G, p2[1], p2[0])
        
        # Calcular camino
        path = nx.shortest_path(G, n1, n2, weight='length')
        dist = nx.shortest_path_length(G, n1, n2, weight='length')
        
        # Dibujar marcador de persona
        folium.Marker(p1, icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)
        
        # Crear la línea de la ruta
        ruta_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]
        folium.PolyLine(ruta_coords, color="blue", weight=5, opacity=0.7).add_to(m)
        
        # Mostrar métricas
        vel = 4 if transporte == "Caminando" else 20
        tiempo = (dist/1000) / vel * 60
        with col1:
            st.metric("Distancia", f"{dist/1000:.2f} km")
            st.metric("Tiempo", f"{int(tiempo)} min")
    except:
        st.sidebar.error("Error al trazar ruta.")

with col2:
    # Mostramos el mapa UNA SOLA VEZ al final del proceso
    salida = st_folium(m, width="100%", height=600, key="mapa_quito")
    
    # Capturar clic solo si no hay inicio marcado
    if salida.get("last_clicked") and st.session_state.punto_inicio is None:
        clic = salida["last_clicked"]
        st.session_state.punto_inicio = [clic['lat'], clic['lng']]
        st.rerun()
