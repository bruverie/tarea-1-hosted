import time
import httpx
import uuid
from app.utils import nueva_posicion
from app.models import CachedPosition, CachedStatus

POSITION_TTL = 5
STATUS_TTL = 10

def get_or_update_position(sat, t_actual, t_creado):
    if sat.position and (t_actual - sat.position.timestamp) <= POSITION_TTL:
        sat.position.cache = "hit"
        return sat.position

    lat_actual, lon_actual = nueva_posicion(
        sat.position.value.lat,
        sat.position.value.lon,
        sat.speed,
        sat.direction,
        t_actual - t_creado
    )

    new_position = CachedPosition(
        value={"lat": lat_actual, "lon": lon_actual},
        timestamp=t_actual,
        cache="miss"
    )

    sat.position = new_position
    return new_position

async def get_or_update_status(sat, t_actual):
    t_actual_int = int(t_actual)
    if sat.status and (t_actual_int - sat.status.timestamp) <= STATUS_TTL:
        sat.status.cache = "hit"
        return sat.status

    try:
        headers = {
            "X-Request-ID": str(uuid.uuid4()),
            "X-Timestamp": str(t_actual_int)
        }

        url = (
            f"https://tarea-1-2025-1.tallerdeintegracion.cl/api/v10/satellites/"
            f"{sat.id}/status?timestamp={t_actual_int}"
        )

        print(f"🛰️ Consultando estado de {sat.id}")
        print(f"➡️ Timestamp actual (float): {t_actual}")
        print(f"➡️ Timestamp redondeado enviado: {t_actual_int}")
        print(f"➡️ URL: {url}")

        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)

        if res.status_code == 200:
            data = res.json()
            estado = data["status"]
            print(f"✅ Estado recibido de {sat.id}: {estado}")
        else:
            print(f"⚠️ Estado no recibido, status HTTP: {res.status_code}")
            estado = "mantenimiento"

    except Exception as e:
        print(f"⚠️ Error al consultar estado del satélite {sat.id}: {e}")
        estado = "mantenimiento"

    sat.status = CachedStatus(
        value=estado,
        timestamp=t_actual_int,
        cache="miss"
    )

    print(f"🗃️ Estado en caché actual: {sat.status.value} con timestamp: {sat.status.timestamp}")

    return sat.status