import json
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import logging

# current
# API_URL = (
#     "https://api.open-meteo.com/v1/forecast"
#     "?latitude=59.3293"
#     "&longitude=18.0686"
#     "&current=temperature_2m,relative_humidity_2m"
# )

# hourly
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=59.3293"
    "&longitude=18.0686"
    "&hourly=temperature_2m,relative_humidity_2m"
    "&forecast_days=1"
    "&timezone=Europe%2FStockholm"
)

MAX_ATTEMPTS = 3
INITIAL_RETRY_DELAY = 1
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}

logger = logging.getLogger(__name__) # name = "open_api_data_platform.ingestion"

def validate_weather(data: dict) -> dict:
    """Validate the minimum structure expected from the weather API."""
    if not isinstance(data, dict):
        raise ValueError("Weather API response must be a JSON object")

    if "hourly" not in data or not isinstance(data["hourly"], dict):
        raise ValueError("Weather API response is missing a valid 'hourly' object")

    required_fields = (
        "time",
        "temperature_2m",
        "relative_humidity_2m",
    )

    hourly = data["hourly"]

    missing_fields = [
        field for field in required_fields
        if field not in hourly
    ]

    if missing_fields:
        raise ValueError(
            f"Weather API response is missing fields: {missing_fields}"
        )

    for field in required_fields:
        if(not isinstance(hourly[field], list)):
            raise ValueError(f"Weather API field '{field}' must be a list.")

    lengths = [len(hourly[field]) for field in required_fields]

    if not lengths[0]:
        raise ValueError("Weather API hourly data must not be empty")

    if len(set(lengths)) != 1:
        raise ValueError(
            "Weather API hourly arrays must have matching lengths"
        )
    
    return data


def fetch_weather() -> dict:
    # Exponential Backoff
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urlopen(API_URL, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                #return validate_weather(data)
                validated_data = validate_weather(data)
                logger.info(
                    "Weather API request succeeded",
                    extra={
                        "event": "api_fetch_succeeded",
                        "stage": "ingest",
                    },
                )
                return validated_data
            
        except HTTPError as error:
            if(error.code not in RETRYABLE_STATUS_CODES):
                raise
            if(attempt == MAX_ATTEMPTS):
                raise

            retry_after = error.headers.get("Retry-After")
            if(retry_after and retry_after.isdigit()):
                delay = min(int(retry_after), 60)
            else:
                delay = INITIAL_RETRY_DELAY * (2 ** (attempt - 1))
            
            logger.warning(
                "Temporary HTTP error; retrying",
                extra={
                    "event": "api_retry",
                    "stage": "ingest",
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "status_code": error.code,
                    "delay_seconds": delay,
                },
            )

        except (URLError, TimeoutError) as error:
            if(attempt == MAX_ATTEMPTS):
                raise

            delay = INITIAL_RETRY_DELAY * (2 ** (attempt - 1))

            # print(
            #     f"Temporary HTTP {error.code}. "
            #     f"Attempt {attempt}/{MAX_ATTEMPTS} failed; "
            #     f"retrying in {delay} second(s)."
            # )
            logger.warning(
                "Temporary network error; retrying",
                extra={
                    "event": "api_retry",
                    "stage": "ingest",
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "delay_seconds": delay,
                },
            )
        time.sleep(delay)
    raise RuntimeError("Weather API request failed after all attempts")
    

if __name__ == '__main__':
    weather = fetch_weather()
    print(json.dumps(weather, indent= 2))