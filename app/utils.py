# app/utils.py
import math
from app.models import Position

def nueva_posicion(lat, lon, velocidad_kmh, direccion_deg, tiempo_segundos):
    if tiempo_segundos <= 0:
        return lat, lon

    velocidad_kms = velocidad_kmh / 3600  # km/h → km/s
    distancia = velocidad_kms * tiempo_segundos

    direccion_rad = math.radians(direccion_deg)
    lat_rad = math.radians(lat)

    delta_lat = (distancia * math.cos(direccion_rad)) / 111
    delta_lon = (distancia * math.sin(direccion_rad)) / (111 * math.cos(lat_rad))

    nueva_lat = lat + delta_lat
    nueva_lon = lon + delta_lon

    return normalize_lat_lon(nueva_lat, nueva_lon)

def normalize_lat_lon(lat, lon):
    # Reflejo en polos
    if lat > 90:
        lat = 180 - lat
        lon += 180
    elif lat < -90:
        lat = -180 - lat
        lon += 180

    # Normalización longitud [-180, 180]
    lon = (lon + 180) % 360 - 180

    return round(lat, 6), round(lon, 6)