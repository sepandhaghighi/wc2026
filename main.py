import os
import json
import time
import pandas as pd
import requests
from enum import Enum
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from pprint import pprint
from memor import *

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


REGISTRY_PATH = "wc_2026_teams.json"
HISTORICAL_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


DATA_ROOT = Path("data")
PREDICTIONS_ROOT = DATA_ROOT / "predictions"
SESSIONS_ROOT = DATA_ROOT / "sessions"


def get_configured_session() -> requests.Session:
    """
    Initializes and configures a requests Session with a robust HTTP retry strategy.

    :return: A configured requests.Session instance.
    """
    http_session = requests.Session()
    retry_strategy = Retry(
        total=3, 
        backoff_factor=2, 
        status_forcelist=[500, 502, 503, 504]
    )
    http_session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    return http_session



network_session = get_configured_session()



def fetch_world_cup_registry() -> dict:
    """
    Fetches and parses the authoritative World Cup 2026 team registry profiles from a remote repository.

    :return: A dictionary mapping lowercased team names to their metrics (FIFA rank and confederation).
    """
    print("[INFO] Synchronizing authoritative World Cup 2026 team registration profiles...")
    try:
        raw_registry_data = json.load(open(REGISTRY_PATH, "r"))
        
        team_registry = {}
        if isinstance(raw_registry_data, dict):
            groups_source = (
                raw_registry_data.values() 
                if "groups" not in raw_registry_data 
                else raw_registry_data["groups"].values()
            )
            for group_teams in groups_source:
                if isinstance(group_teams, list):
                    for team in group_teams:
                        team_name = team.get("name", "").strip().lower()
                        if team_name:
                            team_registry[team_name] = {
                                "fifa_rank": (
                                    team.get("fifa_rank") 
                                    or team.get("rank") 
                                    or team.get("fifa") 
                                    or "Unknown"
                                ),
                                "confederation": team.get("confederation", "Unknown")
                            }
        elif isinstance(raw_registry_data, list):
            for team in raw_registry_data:
                team_name = team.get("name", "").strip().lower()
                if team_name:
                    team_registry[team_name] = {
                        "fifa_rank": team.get("fifa_rank") or team.get("rank") or "unknown",
                        "confederation": team.get("confederation", "Unknown")
                    }
        return team_registry
    except Exception as exc:
        print(f"[WARNING] Failed to process online registry ({exc}). Falling back to strict baseline metrics.")
        return {}


GLOBAL_TEAMS_REGISTRY = fetch_world_cup_registry()


def get_static_team_metrics(team_name: str) -> dict:
    """
    Retrieves static team metrics from the global registry, returning defaults if not found.

    :param team_name: The name of the national team to look up.
    :return: A dictionary containing the team's FIFA rank and confederation.
    """
    normalized_name = team_name.strip().lower()
    if normalized_name in GLOBAL_TEAMS_REGISTRY:
        return GLOBAL_TEAMS_REGISTRY[normalized_name]
    
    print(f"[WARNING] Team '{team_name}' not found in registry dataset. Applying default baseline profiles.")
    return {"fifa_rank": "Unknown", "confederation": "FIFA Baseline"}



def fetch_true_national_team_form(historical_data: pd.DataFrame, team_name: str, last_n: int = 15) -> dict:
    """
    Parses global match databases to calculate recent competitive form metrics for a specific national team.

    :param historical_data: Pandas DataFrame containing the raw international match results.
    :param team_name: The name of the target country to evaluate.
    :param last_n: The number of historical matches to analyze for the form string.
    :return: A dictionary containing calculated form data, averages, and historical match logs.
    """
    print(f"[INFO] Syncing global international match database for team: {team_name}...")
    
    try:
        df_clean = historical_data.dropna(subset=['home_score', 'away_score']).copy()
        df_clean['date'] = pd.to_datetime(df_clean['date'])
        
        team_filtered_df = df_clean[
            (df_clean['home_team'].str.lower() == team_name.lower()) | 
            (df_clean['away_team'].str.lower() == team_name.lower())
        ].copy()
        
        if team_filtered_df.empty:
            print(f"[ERROR] No historical match records located for target team: {team_name}.")
            return {"country": team_name, "error": "Team missing from registry dataset."}
            
        team_filtered_df = team_filtered_df.sort_values(by='date', ascending=False)
        recent_matches = team_filtered_df.head(last_n)
        
        form_letters = []
        total_goals_scored, total_goals_conceded = 0, 0
        wins, draws, losses = 0, 0, 0
        match_records = []
        
        for _, row in recent_matches.iterrows():
            is_home = row['home_team'].lower() == team_name.lower()
            
            home_score_int = int(row['home_score'])
            away_score_int = int(row['away_score'])
            
            team_gf = home_score_int if is_home else away_score_int
            team_ga = away_score_int if is_home else home_score_int
            
            total_goals_scored += team_gf
            total_goals_conceded += team_ga
            
            if team_gf > team_ga:
                status_string = "Win"
                form_letters.append("W")
                wins += 1
            elif team_gf < team_ga:
                status_string = "Loss"
                form_letters.append("L")
                losses += 1
            else:
                status_string = "Draw"
                form_letters.append("D")
                draws += 1
                
            match_records.append({
                "date": row['date'].strftime('%Y-%m-%d'),
                "opponent": row['away_team'] if is_home else row['home_team'],
                "venue": "Home" if is_home else "Away",
                "host_country": row['country'],  
                "neutral_venue": bool(row['neutral']),
                "score": f"{home_score_int}-{away_score_int}",
                "status": status_string,
                "tournament": row['tournament']
            })
            
        form_letters.reverse()
        actual_count = len(form_letters)
        static_metrics = get_static_team_metrics(team_name)
        
        return {
            "country": team_name,
            "fifa_rank": static_metrics["fifa_rank"],
            "confederation": static_metrics["confederation"],
            "calculated_form_string": "".join(form_letters),
            "matches_evaluated_count": actual_count,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored_avg": round(total_goals_scored / actual_count, 2) if actual_count > 0 else 0,
            "goals_conceded_avg": round(total_goals_conceded / actual_count, 2) if actual_count > 0 else 0,
            "recent_match_logs": match_records
        }
        
    except Exception as exc:
        print(f"[ERROR] Failed to process dataset pipeline cleanly for {team_name}: {exc}")
        return {"country": team_name, "status": "Fallback configuration triggered"}



def create_prediction_prompt(team_a_data: dict, team_b_data: dict, host_country_name: str, match_phase: str = "group") -> tuple:
    """
    Constructs structured system and user prompt strings tailored to the tournament phase.

    :param team_a_data: Calculated form and metrics dictionary for Team A.
    :param team_b_data: Calculated form and metrics dictionary for Team B.
    :param host_country_name: The name of the host nation where the match takes place.
    :param match_phase: Current tournament stage context (must be either 'group' or 'knockout').
    :return: A tuple containing the structural system instruction and user context strings.
    """
    assert match_phase in ["group", "knockout"], "Tournament phase must be either 'group' or 'knockout'"
        
    if match_phase == "group":
        probability_schema = (
            "  \"probabilities\": {\n"
            "    \"team_a_win\": float, # Probability of team A winning in normal time\n"
            "    \"draw\": float, # Probability of a draw outcome in normal time\n"
            "    \"team_b_win\": float # Probability of team B winning in normal time\n"
            "  },"
        )
        outcome_rules = "A group match can end in a Win, Loss, or Draw at the conclusion of normal time."
    else:
        probability_schema = (
            "  \"probabilities\": {\n"
            "    \"team_a_advance\": float, # Total cumulative probability of team A advancing\n"
            "    \"team_b_advance\": float # Total cumulative probability of team B advancing\n"
            "  },"
        )
        outcome_rules = (
            "A knockout match must determine a definite winner. If the predicted_score is a tie, "
            "you must populate the extra_time and penalties object flags to indicate how the match is resolved."
        )

    system_instruction = (
        "You are an expert football analytics engine simulating upcoming FIFA World Cup 2026 matchups.\n"
        "Analyze historical form strings, explicit context and FIFA rankings.\n\n"
        "Your output must be structured exactly in raw JSON. Do not include markdown blocks, text wrapping, "
        "or trailing explanations. Follow this exact JSON signature schema:\n"
        "{\n"
        + probability_schema + "\n"
        "  \"predicted_score\": \"string\", # e.g., \"2-1\" or \"1-1\" based on full regular + extra time score\n"
        "  \"predicted_winner\": \"string\", # The team name or \"Draw\" (Draw only valid for group stage entries)\n"
        "  \"knockout_resolution\": {\n"
        "    \"ended_in_extra_time\": bool, # true if match resolved in extra time\n"
        "    \"ended_in_penalties\": bool, # true if match resolved via penalty shootout\n"
        "    \"penalty_shootout_score\": \"string\" # e.g., \"4-3\", or null if match resolved in regular/extra time\n"
        "  },\n"
        "  \"confidence\": float\n"
        "}"
    )
        
    user_context = (
        "World Cup 2026 Match Simulator Parameters:\n"
        "Tournament Phase Context: {phase}\n"
        "Phase Resolution Rules: {rules}\n"
        "Designated Match Host Country: {host}\n\n"
        "National Team A:\n{team_a}\n\n"
        "National Team B:\n{team_b}\n\n"
        "Synthesize probabilities and output raw JSON matching the target schema."
    ).format(
        phase=match_phase.upper(),
        rules=outcome_rules,
        host=host_country_name, 
        team_a=json.dumps(team_a_data, indent=2), 
        team_b=json.dumps(team_b_data, indent=2)
    )
        
    return system_instruction, user_context


def clean_llm_response(raw_text: str) -> str:
    """
    Strips markdown wrappers and isolating block codes from raw LLM text payloads.

    :param raw_text: The incoming text string or parsed payload directly from the LLM endpoint.
    :return: A cleaned, stripped string ready for native JSON parsing.
    """
    if isinstance(raw_text, dict):
        return raw_text
            
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
    return cleaned_text



def call_cloudflare_llm(model_name: str, session_memor: Session, temp: float, top_p: float) -> str:
    """
    Dispatches an operational inference call to Cloudflare's workers AI API payload system.

    :param model_name: The repository string path targeting the model identifier.
    :param session_memor: Active Memor framework container managing history state.
    :param temp: Temperature hyperparameter regulating generation variance.
    :param top_p: Top-p hyperparameter regulating nucleus sampling thresholds.
    :return: The generated string response from the remote LLM engine.
    """
    api_endpoint = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/{model_name}"
    request_headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    request_payload = {
        "messages": session_memor.render(RenderFormat.OPENAI),
        "temperature": temp,
        "top_p": top_p,
        "max_tokens": MAX_TOKENS
    }

    #print(f"[DEBUG] Dispatching Cloudflare Payload: {request_payload}")
    
    response = network_session.post(api_endpoint, headers=request_headers, json=request_payload, timeout=100)
    response.raise_for_status()
    execution_result = response.json()
    
    if execution_result.get("success"):
        #print(execution_result["result"])
        if "choices" in execution_result["result"].keys():
            llm_message = execution_result["result"]["choices"][0]["message"]
            llm_response_text = llm_message["content"]
            llm_reasoning_text = llm_message.get("reasoning_content", None) or llm_message.get("reasoning", None)
        else:
            llm_response_text = execution_result["result"]["response"]
            llm_reasoning_text = None
        response_memor_object = Response(message=RESPONSE_TEMPLATE.format(response=llm_response_text, reasoning=llm_reasoning_text), temperature=TEMPERATURE, top_p=TOP_P, model=model_name)
        session_memor.add_message(response_memor_object)
        return llm_response_text
    else:
        raise Exception(f"Cloudflare Engine Error: {execution_result.get('errors')}")



def check_match_id_exists(match_id: str, model_name: str) -> bool:
    """
    Checks if historical predictions or execution sessions already exist for a given match ID and model.

    :param match_id: Clean parsed alphanumeric identifier for the simulation.
    :param model_name: Name of the active LLM being evaluated.
    :return: True if either the prediction or session archive file already exists, False otherwise.
    """
    safe_model_name = model_name.replace("@", "").replace("/", "_").replace("-", "_")
    pred_file = PREDICTIONS_ROOT / safe_model_name / f"{match_id}.json"
    sess_file = SESSIONS_ROOT / safe_model_name / f"{match_id}.json"
    return pred_file.exists() or sess_file.exists()


def save_match_prediction_and_session(
    match_id: str, 
    model_name: str, 
    match_meta: dict, 
    prediction_data: dict, 
    session_memor: Session
):
    """
    Saves clean prediction responses and stateful Memor sessions into isolated, reproducible directories.

    :param match_id: Clean parsed alphanumeric identifier for the simulation.
    :param model_name: Name of the active LLM being evaluated.
    :param match_meta: Metadata contextual tracking parameters.
    :param prediction_data: Structured JSON output block delivered by the LLM pipeline.
    :param session_memor: Current active state Memor session instance being stored.
    """
    safe_model_name = model_name.replace("@", "").replace("/", "_").replace("-", "_")
    target_prediction_directory = PREDICTIONS_ROOT / safe_model_name
    target_prediction_directory.mkdir(parents=True, exist_ok=True)
    destination_prediction_file = target_prediction_directory / f"{match_id}.json"
    
    output_payload = {
        "match_id": match_id,
        "simulation_env": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": model_name,
            "hyperparameters": {
                "temperature": match_meta["temperature"],
                "top_p": match_meta["top_p"],
                "max_tokens": match_meta["max_tokens"]
            },
        },
        "match_context": {
            "tournament": match_meta["tournament"],
            "phase": match_meta["match_phase"],
            "team_a": match_meta["team_a"],
            "team_b": match_meta["team_b"],
            "host_country": match_meta["host_country"]
        },
        "prediction": prediction_data
    }
    
    with open(destination_prediction_file, 'w', encoding='utf-8') as pred_file:
        json.dump(output_payload, pred_file, indent=4, ensure_ascii=False)
        
    print(f"[SUCCESS] Clean inference output archived at: {destination_prediction_file}")
    target_session_directory = SESSIONS_ROOT / safe_model_name
    target_session_directory.mkdir(parents=True, exist_ok=True)
    destination_session_file = target_session_directory / f"{match_id}.json"
    
    session_memor.save(str(destination_session_file))
    print(f"[SUCCESS] Authoritative execution session archived at: {destination_session_file}")



if __name__ == "__main__":
    current_phase = Phase.GROUP.value 
    raw_match_id = "WC2026-M20"
    match_id = raw_match_id.replace("WC2026-", "") if "WC2026-" in raw_match_id else raw_match_id
    
    country_a = Team.AUSTRIA.value
    country_b = Team.JORDAN.value
    match_host = Host.USA.value
    international_results_df = pd.read_csv(HISTORICAL_RESULTS_URL)
    team_a_metrics = fetch_true_national_team_form(international_results_df, country_a, last_n=15)
    team_b_metrics = fetch_true_national_team_form(international_results_df, country_b, last_n=15)

    print("Team A Metrics:")
    pprint(team_a_metrics)
    print("Team B Metrics:")
    pprint(team_b_metrics)
    system_prompt_text, user_prompt_text = create_prediction_prompt(
        team_a_data=team_a_metrics, 
        team_b_data=team_b_metrics, 
        host_country_name=match_host,
        match_phase=current_phase
    )
    
    prompt_payload = {
        "system_prompt": system_prompt_text,
        "user_prompt": user_prompt_text
    }

    for current_model in MODEL_LIST:
        print(f"\n--- [START] Starting Evaluation Loop for: {current_model} ---")
        if check_match_id_exists(match_id, current_model):
            print(f"[WARNING] Simulation records for Match ID '{match_id}' using model '{current_model}' already exist. Existing logs will be overwritten.")

        try:
            system_prompt_obj = Prompt(message=system_prompt_text, role=Role.SYSTEM)
            user_prompt_obj = Prompt(message=user_prompt_text, role=Role.USER)
            active_session_memor = Session(messages=[system_prompt_obj, user_prompt_obj])
            
            raw_llm_output = call_cloudflare_llm(
                model_name=current_model,
                session_memor=active_session_memor,
                temp=TEMPERATURE,
                top_p=TOP_P
            )

            print("[SUCCESS] Response received")
            
            cleaned_response = clean_llm_response(raw_llm_output)
            
            if isinstance(cleaned_response, dict):
                final_json_data = cleaned_response
            else:
                final_json_data = json.loads(cleaned_response)
            
            match_metadata_summary = {
                "tournament": "FIFA World Cup 2026",
                "match_phase": current_phase,
                "team_a": country_a,
                "team_b": country_b,
                "host_country": match_host,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "max_tokens": MAX_TOKENS
            }
            
            save_match_prediction_and_session(
                match_id=match_id,
                model_name=current_model,
                match_meta=match_metadata_summary,
                prediction_data=final_json_data,
                session_memor=active_session_memor
            )
            
        except Exception as pipeline_error:
            print(f"[CRITICAL] Pipeline crashed during execution for model {current_model}: {pipeline_error}")