import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

#Carga del env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Obtener variables
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Verificación de seguridad
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Error: No se encontraron las credenciales en el archivo .env")

#Permisos para el correcto funcionamiento
SCOPE = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-library-modify "
    "user-top-read "
    "playlist-modify-public "
    "playlist-modify-private "
    "playlist-read-private "
    "playlist-read-collaborative"
)

#Inicializacion del server y la api de spotify
mcp = FastMCP("Spotify Ultimate Server")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))


#Control basico
@mcp.tool()
def listar_dispositivos() -> str:
    """Muestra los dispositivos activos. Útil si la música no suena."""
    try:
        devices = sp.devices()
        if not devices['devices']:
            return "No hay dispositivos activos. Abre Spotify en tu celular o PC."
        return "\n".join([f"- {d['name']} ({d['type']}) ID: {d['id']}" for d in devices['devices']])
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def reproducir_musica(busqueda: str) -> str:
    """Busca y reproduce una CANCIÓN específica."""
    try:
        results = sp.search(q=busqueda, limit=1, type='track')
        if not results['tracks']['items']: return f"No encontré: {busqueda}"
        track = results['tracks']['items'][0]
        sp.start_playback(uris=[track['uri']])
        return f"Reproduciendo: {track['name']} - {track['artists'][0]['name']}"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def pausar_musica() -> str:
    """Pausa la reproducción."""
    try:
        sp.pause_playback()
        return "Pausado."
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def siguiente_cancion() -> str:
    """Salta a la siguiente canción."""
    try:
        sp.next_track()
        return "Siguiente pista..."
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def cambiar_volumen(porcentaje: int) -> str:
    """Cambia el volumen (0-100)."""
    try:
        sp.volume(porcentaje)
        return f"Volumen al {porcentaje}%."
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def saltar_a_segundo(segundos: int) -> str:
    """Salta al segundo especificado de la canción."""
    try:
        sp.seek_track(segundos * 1000)
        return f"Saltando al segundo {segundos}."
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def transferir_musica_a_dispositivo(nombre_dispositivo: str) -> str:
    """Mueve la música a otro dispositivo (ej: 'iPhone', 'PC')."""
    try:
        devices = sp.devices()
        for d in devices['devices']:
            if nombre_dispositivo.lower() in d['name'].lower():
                sp.transfer_playback(device_id=d['id'], force_play=True)
                return f"Música movida a: {d['name']}"
        return f"No encontré '{nombre_dispositivo}'."
    except Exception as e: return f"Error: {e}"


#Gestion de queque
@mcp.tool()
def agregar_a_fila(busqueda: str) -> str:
    """Agrega una canción a la cola de espera."""
    try:
        results = sp.search(q=busqueda, limit=1, type='track')
        if not results['tracks']['items']: return "No encontrado."
        track = results['tracks']['items'][0]
        sp.add_to_queue(uri=track['uri'])
        return f"En cola: {track['name']}"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def reproducir_contexto(busqueda: str, tipo: str = "album") -> str:
    """Reproduce un ÁLBUM o ARTISTA completo. tipo='album' o 'artist'."""
    try:
        results = sp.search(q=busqueda, limit=1, type=tipo)
        items = results[f'{tipo}s']['items']
        if not items: return f"No encontré ese {tipo}."
        sp.start_playback(context_uri=items[0]['uri'])
        return f"Reproduciendo {tipo}: {items[0]['name']}"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def cambiar_modo_reproduccion(aleatorio: bool = False, repetir: str = 'off') -> str:
    """Configura Shuffle (True/False) y Repeat ('track', 'context', 'off')."""
    try:
        sp.shuffle(state=aleatorio)
        sp.repeat(state=repetir)
        return f"Modo: Shuffle={aleatorio}, Repeat={repetir}"
    except Exception as e: return f"Error: {e}"

#Manejo de playlists y bibliotecas
@mcp.tool()
def guardar_en_favoritos() -> str:
    """Guarda (Like) la canción actual en tu biblioteca."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        sp.current_user_saved_tracks_add(tracks=[current['item']['id']])
        return f"Guardada: {current['item']['name']}"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def crear_playlist_basada_en_actual(nombre_playlist: str) -> str:
    """Crea una playlist NUEVA con recomendaciones de lo que suena ahora."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        seed = current['item']['id']
        user_id = sp.current_user()['id']
        recs = sp.recommendations(seed_tracks=[seed], limit=10)
        uris = [t['uri'] for t in recs['tracks']]
        
        pl = sp.user_playlist_create(user=user_id, name=nombre_playlist)
        sp.playlist_add_items(playlist_id=pl['id'], items=uris)
        return f"Playlist '{nombre_playlist}' creada con éxito."
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def agregar_a_playlist_existente(nombre_playlist: str) -> str:
    """Busca una playlist tuya por nombre y le agrega la canción actual."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        track_uri = current['item']['uri']
        
        # Buscar playlist en las del usuario (límite 50)
        playlists = sp.current_user_playlists(limit=50)
        target_id = None
        found_name = ""
        
        for pl in playlists['items']:
            if nombre_playlist.lower() in pl['name'].lower():
                target_id = pl['id']
                found_name = pl['name']
                break
        
        if not target_id: return f"No encontré playlist llamada '{nombre_playlist}'."
        
        sp.playlist_add_items(playlist_id=target_id, items=[track_uri])
        return f"Agregada a '{found_name}'."
    except Exception as e: return f"Error: {e}"

#Analisis de datos 
@mcp.tool()
def mis_top_canciones(plazo: str = "short_term") -> str:
    """Tus canciones más escuchadas (short_term, medium_term, long_term)."""
    try:
        results = sp.current_user_top_tracks(limit=10, time_range=plazo)
        lines = [f"Top Tracks ({plazo}):"]
        for i, item in enumerate(results['items']):
            lines.append(f"{i+1}. {item['name']} - {item['artists'][0]['name']}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def obtener_analisis_cancion() -> str:
    """Datos técnicos: BPM, Energía, Bailabilidad."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        f = sp.audio_features([current['item']['id']])[0]
        return (f"Análisis '{current['item']['name']}':\n"
                f"BPM: {f['tempo']}, Energía: {f['energy']}, "
                f"Dance: {f['danceability']}, Valence: {f['valence']}")
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def obtener_info_artista() -> str:
    """Información del artista actual (Popularidad, Géneros)."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        artist_id = current['item']['artists'][0]['id']
        artist = sp.artist(artist_id)
        genres = ", ".join(artist['genres']) if artist['genres'] else "N/A"
        return (f"Artista: {artist['name']}\nSeguidores: {artist['followers']['total']:,}\n"
                f"Pop: {artist['popularity']}/100\nGéneros: {genres}")
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def radio_artistas_similares() -> str:
    """Crea una sesión con artistas similares al actual."""
    try:
        current = sp.current_playback()
        if not current: return "Nada sonando."
        artist = current['item']['artists'][0]
        
        related = sp.artist_related_artists(artist['id'])
        if not related['artists']: return "No hay artistas relacionados."
        
        uris = []
        names = []
        # Tomar top tracks de los 5 primeros relacionados
        for art in related['artists'][:5]:
            names.append(art['name'])
            top = sp.artist_top_tracks(art['id'])
            uris.extend([t['uri'] for t in top['tracks'][:2]])
            
        sp.start_playback(uris=uris)
        return f"Radio basada en {artist['name']} (Similares: {', '.join(names)})"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def reproducir_podcast(busqueda: str) -> str:
    """Busca y reproduce un episodio de Podcast."""
    try:
        results = sp.search(q=busqueda, limit=1, type='episode')
        if not results['episodes']['items']: return "No encontré podcasts."
        ep = results['episodes']['items'][0]
        sp.start_playback(uris=[ep['uri']])
        return f"Podcast: {ep['name']} ({ep['show']['name']})"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def recomendar_por_parametros(genero: str, energia: float = None, felicidad: float = None) -> str:
    """Recomienda por parámetros (0.0 a 1.0). Ej: energia=0.9, felicidad=0.2."""
    try:
        kwargs = {'seed_genres': [genero], 'limit': 20}
        if energia: kwargs['target_energy'] = energia
        if felicidad: kwargs['target_valence'] = felicidad
        
        res = sp.recommendations(**kwargs)
        if not res['tracks']: return "Sin resultados."
        sp.start_playback(uris=[t['uri'] for t in res['tracks']])
        return f"Mix {genero} personalizado."
    except Exception as e: return f"Error: {e}"

if __name__ == "__main__":

    mcp.run()
