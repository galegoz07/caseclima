import logging
import azure.functions as func
import requests
from azure.eventhub import EventHubProducerClient, EventData
import json
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')


    EVENT_HUB_NAME = "eventhubwheather"

    EVENT_HUB_NAMESPACE = "hub-weather-project.servicebus.windows.net"

    credential = DefaultAzureCredential()

    producer = EventHubProducerClient(
        fully_qualified_namespace=EVENT_HUB_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=credential
    )

    def send_event(event):
        try:
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(json.dumps(event)))
            producer.send_batch(event_data_batch)
            print("Evento enviado com sucesso:", event)
        except Exception as e:
            print("Erro ao enviar evento:", e)

    def handle_response(response):
        if response.status_code == 200:
            return response.json()

        else:
            return f"Error: {response.status_code}, {response.text}"

    def get_current_weather(base_url, api_key, location):
        current_weather_url = f"{base_url}/current.json"
        params = {
            "key": api_key,
            "q": location,
            "aqi": "yes"
        }
        response = requests.get(current_weather_url, params=params)
        return handle_response(response)

    def get_forecast(base_url, api_key, location, days):
        forecast_url = f"{base_url}/forecast.json"
        params = {
            "key": api_key,
            "q": location,
            "days": days,
        }
        response = requests.get(forecast_url, params=params)
        return handle_response(response)

    def get_alerts(base_url, api_key, location):
        alerts_url = f"{base_url}/alerts.json"
        params = {
            "key": api_key,
            "q": location,
            "alerts": "yes",
        }
        response = requests.get(alerts_url, params=params)
        return handle_response(response)

    def flatten_data(current_weather, forecast_weather, alerts):
        location_data = current_weather.get("location", {})
        current = current_weather.get("current", {})
        condition = current.get("condition", {})
        air_quality = current.get("air_quality", {})
        forecast = forecast_weather.get("forecast", {}).get("forecastday", [])
        alerts_list = alerts.get("alerts", []).get("alert", [])

        flatten_data = {
            "name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "lat": location_data.get("lat"),
            "lon": location_data.get("lon"),
            "localtime": location_data.get("localtime"),
            "temp_c": current.get("temp_c"),
            "temp_f": current.get("temp_f"),
            "is_day": current.get("is_day"),
            "condition_text": condition.get("text"),
            "condition_icon": condition.get("icon"),
            "wind_mph": current.get("wind_mph"),
            "wind_kph": current.get("wind_kph"),
            "wind_degree": current.get("wind_degree"),
            "wind_dir": current.get("wind_dir"),
            "pressure_mb": current.get("pressure_mb"),
            "pressure_in": current.get("pressure_in"),
            "precip_mm": current.get("precip_mm"),
            "precip_in": current.get("precip_in"),
            "humidity": current.get("humidity"),
            "cloud": current.get("cloud"),
            "feelslike_c": current.get("feelslike_c"),
            "feelslike_f": current.get("feelslike_f"),
            "vis_km": current.get("vis_km"),
            "vis_miles": current.get("vis_miles"),
            "uv": current.get("uv"),
            "air_quality": {
                "co": air_quality.get("co"),
                "no2": air_quality.get("no2"),
                "o3": air_quality.get("o3"),
                "so2": air_quality.get("so2"),
                "pm2_5": air_quality.get("pm2_5"),
                "pm10": air_quality.get("pm10"),
                "us-epa-index": air_quality.get("us-epa-index"),
                "gb-defra-index": air_quality.get("gb-defra-index")
            },
            "alerts": [
                {
                    "headline": alert.get("headline"),
                    "severity": alert.get("severity"),
                    "description": alert.get("description"),
                    "instruction": alert.get("instruction")
                }
                for alert in alerts_list
            ],
            "forecast": [
                {
                    "date": day.get("date"),
                    "date_epoch": day.get("date_epoch"),
                    "maxtemp_c": day.get("day", {}).get("maxtemp_c"),
                    "mintemp_c": day.get("day", {}).get("mintemp_c"),
                    "condition": day.get("day", {}).get("condition", {}).get("text"),
                }
                for day in forecast
            ]
        }
        return flatten_data
    

    def get_secret_from_keyvault(vault_url, secret_name):
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url,credential=credential)
        retrieved_secret = secret_client.get_secret(secret_name)
        return retrieved_secret.value

    def fetch_weather_data():
        base_url = "http://api.weatherapi.com/v1"
        location = "Osasco"

        VAULT_URL = "https://key-weather-project.vault.azure.net/"
        API_KEY_SECRET_NAME = "weatherapikey"
        weatherapikey = get_secret_from_keyvault(VAULT_URL, API_KEY_SECRET_NAME)

        capitais_estados = [
            {"cidade": "Rio Branco", "estado": "AC", "regiao": "Norte"},
            {"cidade": "Maceió", "estado": "AL", "regiao": "Nordeste"},
            {"cidade": "Macapá", "estado": "AP", "regiao": "Norte"},
            {"cidade": "Manaus", "estado": "AM", "regiao": "Norte"},
            {"cidade": "Salvador", "estado": "BA", "regiao": "Nordeste"},
            {"cidade": "Fortaleza", "estado": "CE", "regiao": "Nordeste"},
            {"cidade": "Brasília", "estado": "DF", "regiao": "Centro-Oeste"},
            {"cidade": "Vitória", "estado": "ES", "regiao": "Sudeste"},
            {"cidade": "Goiânia", "estado": "GO", "regiao": "Centro-Oeste"},
            {"cidade": "São Luís", "estado": "MA", "regiao": "Nordeste"},
            {"cidade": "Cuiabá", "estado": "MT", "regiao": "Centro-Oeste"},
            {"cidade": "Campo Grande", "estado": "MS", "regiao": "Centro-Oeste"},
            {"cidade": "Belo Horizonte", "estado": "MG", "regiao": "Sudeste"},
            {"cidade": "Belém", "estado": "PA", "regiao": "Norte"},
            {"cidade": "João Pessoa", "estado": "PB", "regiao": "Nordeste"},
            {"cidade": "Curitiba", "estado": "PR", "regiao": "Sul"},
            {"cidade": "Recife", "estado": "PE", "regiao": "Nordeste"},
            {"cidade": "Teresina", "estado": "PI", "regiao": "Nordeste"},
            {"cidade": "Rio de Janeiro", "estado": "RJ", "regiao": "Sudeste"},
            {"cidade": "Natal", "estado": "RN", "regiao": "Nordeste"},
            {"cidade": "Porto Alegre", "estado": "RS", "regiao": "Sul"},
            {"cidade": "Porto Velho", "estado": "RO", "regiao": "Norte"},
            {"cidade": "Boa Vista", "estado": "RR", "regiao": "Norte"},
            {"cidade": "Florianópolis", "estado": "SC", "regiao": "Sul"},
            {"cidade": "São Paulo", "estado": "SP", "regiao": "Sudeste"},
            {"cidade": "Aracaju", "estado": "SE", "regiao": "Nordeste"},
            {"cidade": "Palmas", "estado": "TO", "regiao": "Norte"},
        ]
        for local in capitais_estados:
            cidade = local["cidade"]
            estado = local["estado"]
            regiao = local["regiao"]
            try:
                current = get_current_weather(base_url, weatherapikey, cidade)
                forecast = get_forecast(base_url, weatherapikey, cidade, 3)
                alerts = get_alerts(base_url, weatherapikey, cidade)
                evento = flatten_data(current, forecast, alerts)
                evento["sigla_estado"] = estado
                evento["regiao"] = regiao
                send_event(evento)
            except Exception as e:
                logging.error(f"Erro ao processar {cidade} - {estado}: {e}")

    fetch_weather_data()