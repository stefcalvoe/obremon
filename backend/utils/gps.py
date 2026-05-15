import math

def dentro_del_radio(lat1: float, lon1: float, lat2: float, lon2: float, radio_metros: float) -> tuple:
    """
    Calcula la distancia entre dos puntos GPS usando la fórmula de Haversine.
    Retorna (dentro_del_radio: bool, distancia_metros: float)
    """
    R = 6371000  # Radio de la Tierra en metros

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    distancia = R * c

    dentro = distancia <= radio_metros
    return (dentro, distancia)
