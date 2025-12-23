import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

st.set_page_config(page_title="Quito Ruta Completa", layout="wide")

# 1. BASE DE DATOS COMPLETA (Museos, Plazas y Calles)
LUGARES_COMPLETOS = {
    "Museo de la Ciudad": [-0.2238, -78.5138],
    "Alberto Mena Caamaño (Museo de Cera)": [-0.2205, -78.5118],
    "Casa del Alabado Pre‑Columbian Art": [-0.2215, -78.5152],
    "Museo Camilo Egas": [-0.2185, -78.5085],
    "Museo Casa de Sucre": [-0.2219, -78.5111],
    "Museum Of Maria Augusta Urrutia": [-0.2212, -78.5115],
    "Museo Franciscano Fray Pedro Gocial": [-0.2210, -78.5155],
    "Museo del Pasillo": [-0.2225, -78.5130],
    "Museo de la Moneda": [-0.2208, -78.5110],
    "Museo de Arte Colonial": [-0.2195, -78.5105],
    "Manuela Sáenz Museum": [-0.2230, -78.5125],
    "Centro Cultural Metropolitano": [-0.2204, -78.5116],
    "Contemporary Art Center (CAC)": [-0.2165, -78.5042],
    "Museo Antiguo Banco Central": [-0.2218, -78.5120],
    "Plaza de la Independencia (Grande)": [-0.2202, -78.5123],
    "Plaza de San Francisco": [-0.2210, -78.5147],
    "Plaza de Santo Domingo": [-0.2235, -78.5120],
    "Plaza del Teatro (Plaza Sucre)": [-0.2188, -78.5100],
    "Plaza de San Blas": [-0.2168, -78.5065],
    "Plaza de Santa Clara": [-0.2245, -78.5140],
    "Plaza de San Agustín": [-0.2208, -78.5100],
    "Plaza de La Merced": [-0.2195, -78.5135],
    "Plaza del Carmen Alto": [-0.2235, -78.5145],
    "Plaza del Hospital San Juan de Dios": [-0.2240, -78.5135],
    "Calle La Ronda": [-0.2248, -78.5128],
    "Basílica del Voto Nacional": [-0.2146, -78.5074]
}

@st.cache_resource
def obtener_grafo():
    # Descargamos el mapa del Centro Histórico
    return ox.graph_from_address("Plaza de la Independencia, Quito", dist=2000, network_type='all')

G = obtener_grafo()

st.title("🏛️ Ruta Maestra del Centro Histórico de Quito")
st.markdown("Puedes seleccionar lugares de la lista o **tocar directamente el mapa**.")

# Inicializar estados
if 'punto_a' not in st.session_state: st.session_state.punto_a = None
if 'punto_b' not in st.session_state: st.session_state.punto_b = None

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Opciones")
    if st.button("🗑️ Limpiar Puntos"):
        st.session_state.punto_a = None
        st.session_state.punto_b = None
        st.rerun()
    
    # Buscador de ayuda
    seleccion_rapida = st.selectbox("Ver ubicación de:", ["-- Selecciona --"] + sorted(LUGARES_COMPLETOS.keys()))
    if seleccion_rapida != "-- Selecciona --":
        coords = LUGARES_COMPLETOS[seleccion_rapida]
        st.info(f"📍 {seleccion_rapida} está en: {coords}")

# Crear el Mapa
m = folium.Map(location=[-0.2202, -78.5123], zoom_start=16)

# Dibujar todos los puntos de la lista como referencia
for nom, coord in LUGARES_COMPLETOS.items():
    folium.CircleMarker(
        location=coord, radius=3, color="red", fill=True, popup=nom
    ).add_to(m)

# Dibujar Marcadores de selección
if st.session_state.punto_a:
    folium.Marker(st.session_state.punto_a, popup="INICIO", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)
if st.session_state.punto_b:
    folium.Marker(st.session_state.punto_b, popup="DESTINO", icon=folium.Icon(color="green", icon="flag", prefix="fa")).add_to(m)

# Calcular Ruta
if st.session_state.punto_a and st.session_state.punto_b:
    try:
        n1 = ox.nearest_nodes(G, st.session_state.punto_a[1], st.session_state.punto_a[0])
        n2 = ox.nearest_nodes(G, st.session_state.punto_b[1], st.session_state.punto_b[0])
        path = nx.shortest_path(G, n1, n2, weight='length')
        dist = nx.shortest_path_length(G, n1, n2, weight='length')
        
        # Dibujar la línea
        puntos_ruta = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]
        folium.PolyLine(puntos_ruta, color="blue", weight=6, opacity=0.7).add_to(m)
        
        with col1:
            st.metric("Distancia", f"{dist/1000:.2f} km")
            st.metric("Caminando", f"{int((dist/1000)/4*60)} min")
    except:
        st.error("Error al conectar los puntos.")

with col2:
    salida = st_folium(m, width="100%", height=650, key="mapa_final_quito")
    
    # Lógica de captura de clics
    if salida.get("last_clicked"):
        clic = [salida["last_clicked"]['lat'], salida["last_clicked"]['lng']]
        if st.session_state.punto_a is None:
            st.session_state.punto_a = clic
            st.rerun()
        elif st.session_state.punto_b is None and clic != st.session_state.punto_a:
            st.session_state.punto_b = clic
            st.rerun()
