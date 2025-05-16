import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import json
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.3888,
	"longitude": 2.159,
	"hourly": "temperature_2m"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

#-------------------

# Convertim a una llista per treballar amb bucles for
temperature_list = list(hourly_temperature_2m) # hourly_temperature_2m es un array de Numpy

# Calcular màxima i mínima
temp_max = temperature_list[0]
temp_min = temperature_list[0]

# Inicialitzem total i comptador per a la mitjana
total = 0
contador = 0

for temperatura in temperature_list:
    total += temperatura
    contador += 1

    if temperatura > temp_max:
        temp_max = temperatura
    if temperatura < temp_min:
        temp_min = temperatura

mitjana = total / contador

# Mostrar resultats
print("\n--- Resum de temperatures del dia (calcul manual) ---")
print(f"🌡️ Temperatura màxima: {temp_max:.2f} °C")
print(f"🌡️ Temperatura mínima: {temp_min:.2f} °C")
print(f"🌡️ Temperatura mitjana: {mitjana:.2f} °C")

#-------------------

# Crear diccionari amb les dades
resum_temperatures = {
    "temp_max": float(round(temp_max, 2)),
    "temp_min": float(round(temp_min, 2)),
    "temp_mitjana": float(round(mitjana, 2))
}

#-------------------

# Obtenir la data actual en format YYYYMMDD
data_actual = datetime.now().strftime("%Y%m%d")

# Nom del fitxer JSON
nom_fitxer = f"temp_{data_actual}.json"

#-------------------

# Escriure les dades al fitxer JSON amb identació
with open(nom_fitxer, "w") as fitxer_json:
    json.dump(resum_temperatures, fitxer_json, indent=4)
    
print(f"\nFitxer JSON creat: {nom_fitxer}")