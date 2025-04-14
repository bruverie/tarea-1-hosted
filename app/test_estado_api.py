import httpx

satellite_id = "05649b28-d506-413c-8eae-ad0f846173fc"

url = f"https://tarea-1-2025-1.tallerdeintegracion.cl/api/v10/satellites/{satellite_id}/status"

response = httpx.get(url)

print("Código de respuesta:", response.status_code)
print("Respuesta JSON:", response.json())