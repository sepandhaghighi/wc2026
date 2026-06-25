import json
import pandas as pd
from pprint import pprint
from params import *
from utils import *


if __name__ == "__main__":
    current_phase = Phase.GROUP.value 
    raw_match_id = "WC2026-M56"
    match_id = raw_match_id.replace("WC2026-", "") if "WC2026-" in raw_match_id else raw_match_id
    
    country_a = Team.ECUADOR.value
    country_b = Team.GERMANY.value
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