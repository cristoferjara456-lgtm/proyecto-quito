import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

st.set_page_config(page_title="Ruta Histórica Quito", layout="wide")

# BASE DE DATOS COMPLETA (Museos, Plazas y Sitios)
LUGARES = {
    "Museo de la Ciudad": [-0.2238, -78.5138],
    "Alberto Mena Caamaño (Museo de Cera)": [-0.2205, -78.5118],
    "Casa del Alabado": [-0.2215, -78.5152],
    "Museo Camilo Egas": [-0.2185, -78.5085],
    "Museo Casa de Sucre": [-0.2219, -78.5111],
    "Museo Maria Augusta Urrutia": [-0.2212, -78.5115],
    "Museo Franciscano Pedro Gocial": [-0.2210, -78.5155],
    "Museo del Pasillo": [-0.2225, -78.5130],
    "Museo de la Moneda": [-0.2208, -78.5110],
    "Museo de Arte Colonial": [-0.2195, -78.5105],
    "Museo Manuela Sáenz": [-0.2230, -78.5125],
    "Centro Cultural Metropolitano": [-0.2204, -78.5116],
    "Centro de Arte Contemporáneo": [-0.2165, -78.5042],
    "Museo Antiguo Banco Central": [-0.2218, -78.5120],
    "Plaza de la Independencia": [-0.2202, -78.5123],
    "Plaza de San Francisco": [-0.2210, -78.5147],
    "Plaza de Santo Domingo": [-0.2235, -78.5120],
    "Plaza del Teatro": [-0.2188, -78.5100],
    "Plaza de San Blas": [-0.2168, -78.5065],
    "Plaza de Santa Clara": [-0.2245, -78.5140],
    "Plaza de San Agustín": [-0.2208, -78.5100],
    "Plaza de La Merced": [-0.2195, -78.5135],
    "Plaza del Carmen Alto": [-0.2235, -78.5145],
    "Plaza del Hospital San Juan de Dios": [-0.2240, -78.5135],
    "Calle La Ronda": [-0.2248, -78.5128],
    "Basílica del Voto Nacional": [-0.2146, -78.5074]
}

st.title("🗺️ Guía de Museos y Plazas del Centro Histórico")
st.markdown("Haz **clic en el mapa** para marcar dónde estás y selecciona tu destino.")

# Estado de la sesión para recordar el clic
if 'mi_ubicacion' not in st.session_state:
    st.session_state.mi_ubicacion = None

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configuración")
    transporte = st.selectbox("¿Cómo te mueves?", ["Caminando", "Auto", "Bicicleta"])
    destino = st.selectbox("Selecciona lugar de llegada:", sorted(LUGARES.keys()))
    
    if st.session_state.mi_ubicacion:
        st.success("✅ Tu posición ha sido marcada")
    else:
        st.info("📍 Toca cualquier calle en el mapa para indicar tu posición actual.")

# Crear el Mapa
m = folium.Map(location=[-0.2202, -78.5123], zoom_start=15)

# Añadir todos los lugares al mapa
for nombre, coords in LUGARES.items():
    folium.Marker(
        coords, 
        popup=nombre, 
        icon=folium.Icon(color="red", icon="landmark", prefix="fa")
    ).add_to(m)

# Si ya hizo clic, poner icono de persona
if st.session_state.mi_ubicacion:
    folium.Marker(
        [st.session_state.mi_ubicacion['lat'], st.session_state.mi_ubicacion['lng']],
        popup="Tú estás aquí",
        icon=folium.Icon(color="blue", icon="street-view", prefix="fa")
    ).add_to(m)

with col2:
    # Mostrar mapa y capturar clic
    mapa_interactivo = st_folium(m, width="100%", height=600)
    
    if mapa_interactivo.get("last_clicked"):
        nuevo_clic = mapa_interactivo["last_clicked"]
        if st.session_state.mi_ubicacion != nuevo_clic:
            st.session_state.mi_ubicacion = nuevo_clic
            st.rerun()

# LÓGICA DE CÁLCULO DE RUTA
if st.session_state.mi_ubicacion:
    try:
        with st.spinner("Calculando camino por las calles de Quito..."):
            punto_a = (st.session_state.mi_ubicacion['lat'], st.session_state.mi_ubicacion['lng'])
            punto_b = LUGARES[destino]
            
            modo_ox = {"Caminando": "walk", "Auto": "drive", "Bicicleta": "bike"}[transporte]
            
            # Descarga de red local
            G = ox.graph_from_point(punto_a, dist=1500, network_type=modo_ox)
            n_orig = ox.nearest_nodes(G, punto_a[1], punto_a[0])
            n_dest = ox.nearest_nodes(G, punto_b[1], punto_b[0])
            
            # Dijkstra
            ruta = nx.shortest_path(G, n_orig, n_dest, weight='length')
            distancia = nx.shortest_path_length(G, n_orig, n_dest, weight='length')
            
            # Velocidades promedio
            v = {"Caminando": 4, "Auto": 25, "Bicicleta": 12}
            tiempo = (distancia/1000) / v[transporte] * 60

            with col1:
                st.metric("Distancia Real", f"{distancia/1000:.2f} km")
                st.metric("Tiempo Estimado", f"{int(tiempo)} min")
                
    except Exception:
        st.error("Ruta difícil de encontrar. Intenta marcar un punto en una calle principal.")
