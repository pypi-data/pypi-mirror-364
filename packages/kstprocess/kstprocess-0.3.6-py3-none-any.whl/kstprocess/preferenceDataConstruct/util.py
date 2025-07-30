from pathlib import Path
from typing import Optional, List, Dict, Union
import requests
import json
import random


def convert_general_to_dialogue_str(dialog_record, user_utterance):
    new_dialog_str = ""
    for i, line in enumerate(dialog_record):
        if i == 0:
            new_dialog_str += f"访客搜索词:{line['sentence']}\n"    
        elif line["role"] == "CLIENT":
            new_dialog_str += f"(round {(i+1)//2})user:{line['sentence']}\n"
        else:
            new_dialog_str += f"(round {(i+1)//2})assistant:{line['sentence']}\n"
    new_dialog_str += f"(round {(len(dialog_record)+1)//2})user:{user_utterance}"
    return new_dialog_str


class NativeChatLLMServer(object):
    def __init__(self, dialogue_model_path) -> None:
        self.dialogue_model_url = dialogue_model_path
    
    def post_server_url_test(self,
                             dialogrecord: Optional[List], 
                             dialogId: Optional[str],
                             keyword: Optional[str],
                             utterance: Optional[str],
                             promptInfo: Optional[Dict], 
                             limit: Optional[int]):
        post_data = {
            "robotId": "0000",
            "dialogId": dialogId,
            "keyword":keyword,
            "utterance": utterance,
            "faqAnswers": {},
            "dialogRecord": dialogrecord,
            "promptInfo": promptInfo,
            "limit": limit,
            "task_type": "dialog"
        }
        response = requests.post(self.dialogue_model_url, json=post_data)
        generate_text_list = json.loads(response.text)["data"]
        return generate_text_list
    


def get_random_chosen_rejected_pair(score_dict: dict, threshold: int = 2) -> dict:
    if not score_dict or len(score_dict) < 1:
        return None
    highest_score = max(score_dict.values())
    lowest_score = min(score_dict.values())
    if highest_score - lowest_score < threshold:
        return None
    chosen_candidates = [s for s, sc in score_dict.items() if sc == highest_score]
    rejected_candidates = [s for s, sc in score_dict.items() if sc == lowest_score]
    chosen = random.choice(chosen_candidates)
    rejected = random.choice(rejected_candidates)
    return {
        "chosen": chosen,
        "rejected": rejected,
        "chosen_score": highest_score,
        "rejected_score": lowest_score
    }