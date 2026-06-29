import os
from enum import Enum
from pathlib import Path

RESPONSE_TEMPLATE = """<response>
{response}
</response>
<reasoning>
{reasoning}
</reasoning>"""

class Phase(Enum):
    GROUP = "group"
    KNOCKOUT = "knockout"


class Team(Enum):
    MEXICO = "Mexico"
    SOUTH_AFRICA = "South Africa"
    SOUTH_KOREA = "South Korea"
    CZECH_REPUBLIC = "Czech Republic"
    CANADA = "Canada"
    BOSNIA_AND_HERZEGOVINA = "Bosnia and Herzegovina"
    USA = "United States"
    PARAGUAY = "Paraguay"
    QATAR = "Qatar"
    SWITZERLAND = "Switzerland"
    BRAZIL = "Brazil"
    MOROCCO = "Morocco"
    HAITI = "Haiti"
    SCOTLAND = "Scotland"
    AUSTRALIA = "Australia"
    TURKEY = "Turkey"
    GERMANY = "Germany"
    CURACAO = "Curaçao"
    IVORY_COAST = "Ivory Coast"
    ECUADOR = "Ecuador"
    NETHERLANDS = "Netherlands"
    JAPAN = "Japan"
    SWEDEN = "Sweden"
    TUNISIA = "Tunisia"
    BELGIUM = "Belgium"
    EGYPT = "Egypt"
    IRAN = "Iran"
    NEW_ZEALAND = "New Zealand"
    SPAIN = "Spain"
    CAPE_VERDE = "Cape Verde"
    SAUDI_ARABIA = "Saudi Arabia"
    URUGUAY = "Uruguay"
    FRANCE = "France"
    SENEGAL = "Senegal"
    IRAQ = "Iraq"
    NORWAY = "Norway"
    ARGENTINA = "Argentina"
    ALGERIA = "Algeria"
    AUSTRIA = "Austria"
    JORDAN = "Jordan"
    PORTUGAL = "Portugal"
    DR_CONGO = "DR Congo"
    UZBEKISTAN = "Uzbekistan"
    COLOMBIA = "Colombia"
    ENGLAND = "England"
    CROATIA = "Croatia"
    GHANA = "Ghana"
    PANAMA = "Panama"


class Host(Enum):
    USA = "United States"
    MEXICO = "Mexico"
    CANADA = "Canada"


CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "your_id")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_KEY", "your_token")

MODEL_LIST = [
    "openai/gpt-oss-20b",
    "aisingapore/gemma-sea-lion-v4-27b-it",
    "qwen/qwen3-30b-a3b-fp8",
    "openai/gpt-oss-120b",
    "mistralai/mistral-small-3.1-24b-instruct",
    "meta/llama-3.1-8b-instruct-fast",
    "meta/llama-4-scout-17b-16e-instruct",
    "meta/llama-3.2-3b-instruct"
]

TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 7000

DATA_ROOT = Path("data")
REGISTRY_PATH = DATA_ROOT / "wc_2026_teams.json"
HISTORICAL_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


PREDICTIONS_ROOT = DATA_ROOT / "predictions"
SESSIONS_ROOT = DATA_ROOT / "sessions"
