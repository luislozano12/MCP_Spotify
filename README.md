Spotify MCP Server
Este proyecto implementa un servidor del Model Context Protocol (MCP) para Spotify. Permite conectar Inteligencias Artificiales (como Claude Desktop) con tu cuenta de Spotify para controlar la reproducción, gestionar playlists, analizar características de audio y descubrir música nueva usando lenguaje natural.

  Características
El servidor incluye herramientas avanzadas divididas en 4 categorías:
- Control de Reproducción: Play, Pausa, Siguiente, Volumen, Seek (saltar a segundo), Transferir a otro dispositivo.
- Gestión de Biblioteca: Guardar en "Me Gusta", Agregar a la Cola, Crear Playlists inteligentes, Agregar a Playlists existentes.
  - Análisis y Datos: Ver tus Top Canciones, Analizar audio (BPM, Energía, Bailabilidad), Información de Artistas.
- Descubrimiento: Recomendaciones por parámetros (ej. "Música triste pero bailable"), Radio de artistas similares, Búsqueda de Podcasts.

  Requisitos Previos
Python 3.10 o superior.
Una cuenta de Spotify Premium (necesaria para controlar la reproducción vía API).
Claude Desktop App instalada.

  Instalación y Configuración
1. Configurar Spotify for Developers
  1. Ve al Spotify Developer Dashboard.
  2. Crea una nueva App.
  3. En la configuración de la App, establece la Redirect URI
  4. Copia tu Client ID y Client Secret.

2. Instalación del Proyecto
Clona este repositorio o descarga los archivos y entra en la carpeta:
# Instalar dependencias
pip install mcp spotipy python-dotenv

3. Configurar Variables de Entorno
Crea un archivo llamado .env en la raíz del proyecto y agrega tus credenciales:
SPOTIPY_CLIENT_ID="tu_client_id_aqui"
SPOTIPY_CLIENT_SECRET="tu_client_secret_aqui"
SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"

4. Autenticación Inicial (Importante)
Antes de conectar con Claude, debes autorizar la aplicación manualmente una vez para generar el token.

- Ejecuta el servidor manualmente: python server.py
- Se abrirá tu navegador. Acepta los permisos de Spotify.
- Si te redirige a una página de error (localhost), copia la URL de la barra de direcciones y pégala en la terminal si te lo pide.
- Se creará un archivo .cache en tu carpeta.
- Detén el servidor (Ctrl + C).

Conectar a Claude Desktop
Para usarlo en Claude, debes editar el archivo de configuración
- Agrega tu servidor:
{
  "mcpServers": {
    "spotify": {
      "command": "C:/Ruta/A/Tu/Python/python.exe",
      "args": ["C:/Ruta/A/Tu/Proyecto/server.py"]
    }
  }
}
