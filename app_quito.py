import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

# Configuración visual
st.set_page_config(page_title="Ruta Museos Quito", layout="wide")

st.title("🏛️ Guía Interactiva de Museos - Quito")
st.markdown("Selecciona tu punto de partida, destino y cómo te moverás.")

# 1. DATOS DE LOS MUSEOS (Puedes añadir más aquí)
museos = {
    "Museo de la Ciudad": [-0.2238, -78.5138],
    "Museo Alberto Mena Caamaño": [-0.2205, -78.5118],
    "Casa del Alabado": [-0.2215, -78.5152],
    "Museo Nacional (MUNA)": [-0.2100, -78.4945],
    "Centro de Arte Contemporáneo": [-0.2165, -78.5042]
}

# 2. BARRA LATERAL (CONFIGURACIÓN)
with st.sidebar:
    st.header("Opciones de Viaje")
    transporte = st.selectbox(
        "¿Cómo viajarás?",
        ["Caminando", "Auto", "Bicicleta"]
    )
    
    # Mapeo de transporte para la IA de rutas
    modo_map = {"Caminando": "walk", "Auto": "drive", "Bicicleta": "bike"}
    modo_ox = modo_map[transporte]
    
    st.info("El mapa mostrará la ruta más corta por las calles reales.")

# 3. INTERFAZ DE SELECCIÓN
col1, col2 = st.columns([1, 2])

with col1:
    inicio = st.selectbox("Desde:", list(museos.keys()), index=0)
    destino = st.selectbox("Hacia:", list(museos.keys()), index=1)
    btn_ruta = st.button("🚀 Calcular Ruta y Tiempo")

# 4. MAPA BASE (Siempre visible)
# Centrado en el Centro Histórico de Quito
m = folium.Map(location=[-0.2202, -78.5123], zoom_start=14, control_scale=True)

# Dibujar marcadores de todos los museos
for nombre, coords in museos.items():
    folium.Marker(
        coords, 
        popup=nombre, 
        tooltip=nombre,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 5. LÓGICA DE RUTA
if btn_ruta:
    with st.spinner("Calculando ruta óptima en Quito..."):
        try:
            # Obtener coordenadas
            coord_orig = museos[inicio]
            coord_dest = museos[destino]

            # Descargar red de calles (solo el área necesaria para ahorrar memoria)
            G = ox.graph_from_point(coord_orig, dist=3000, network_type=modo_ox)
            
            # Encontrar nodos más cercanos en las calles
            orig_node = ox.nearest_nodes(G, coord_orig[1], coord_orig[0])
            dest_node = ox.nearest_nodes(G, coord_dest[1], coord_dest[0])
            
            # Algoritmo de Dijkstra para la ruta más corta
            ruta = nx.shortest_path(G, orig_node, dest_node, weight='length')
            distancia_metros = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
            
            # Calcular tiempo (Distancia / Velocidad)
            vel_kmh = {"Caminando": 4.5, "Auto": 30, "Bicicleta": 15}
            tiempo_minutos = (distancia_metros / 1000) / vel_kmh[transporte] * 60

            # Mostrar resultados
            st.success(f"**Distancia:** {distancia_metros/1000:.2f} km")
            st.warning(f"**Tiempo estimado:** {int(tiempo_minutos)} min aprox.")

            # Dibujar la línea de la ruta en el mapa
            puntos_ruta = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in ruta]
            folium.PolyLine(puntos_ruta, color="blue", weight=6, opacity=0.8).add_to(m)
            m.fit_bounds(puntos_ruta) # Ajustar zoom a la ruta
            
        except Exception as e:
            st.error("No se pudo conectar los puntos por calle. Intenta otro modo.")

# 6. MOSTRAR MAPA FINAL
with col2:
    st_folium(m, width="100%", height=600)
