from pathlib import Path
from typing import Optional, List, Dict, Union
import ast
from tqdm import tqdm
import json
import logging
from kstprocess.util.llm_server import request_native_llm_server
from functools import partial
from kstprocess.util.format_convert import add_system_prompt_for_train_data, convert_chosen_rejected_to_prompt
from kstprocess.preferenceDataConstruct.util import NativeChatLLMServer, convert_general_to_dialogue_str, get_random_chosen_rejected_pair
from kstprocess.util.postprocess.duplication_util import DuplicationProcesser
from kstprocess.util.postprocess.action_util import ActionProcessor

root_logger = logging.getLogger()

# 设置根日志记录器的级别为 CRITICAL，这样只有严重错误会被记录
root_logger.setLevel(logging.CRITICAL)

# 移除所有现有的处理器以防止日志输出
if root_logger.hasHandlers():
    root_logger.handlers.clear()



class DpoDatasetConstruct(object):
    def __init__(self,  enable_close_think:Optional[bool]=True, 
                        nativeChatLLM_model_path: Optional[str]="http://localhost:9990/dialog_gpt_v1",
                        openai_api_key:Optional[str]="zj", 
                        openai_api_base:Optional[str]="http://192.168.1.67:8888/v1", 
                        model:Optional[str]="llm_zj",
                        is_use_postprocess_action_model:Optional[bool]=True,
                        action_model_url:Optional[str]="http://10.14.250.11:30412/kicp-micro-common-action-service",
                        action_map:Optional[dict]=None,
                        domain:Optional[str]="paediastrics") -> None:
        self.assistant_model = NativeChatLLMServer(nativeChatLLM_model_path)
        self.requsest_llm = partial(request_native_llm_server, 
                                    enable_close_think=enable_close_think,
                                    openai_api_key=openai_api_key,
                                    openai_api_base=openai_api_base,
                                    model=model,
                                    )
        self.post_process_sim_model = DuplicationProcesser()
        self.is_use_postprocess_action_model = is_use_postprocess_action_model
        if is_use_postprocess_action_model:
            self.post_process_action_model = ActionProcessor(action_model_url=action_model_url,
                                                            action_map=action_map,
                                                            domain=domain)

    def get_candidates_scores(self, reward_prompt: Optional[str], 
                                    dialog_record_str: Optional[str], 
                                    candidates: Optional[List]) -> Optional[List]:
        new_prompt = reward_prompt.replace("dialog_record_str", str(dialog_record_str)).replace("candidates", str(candidates))
        res = self.requsest_llm(formatted_dialog=new_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        res = res.split(",")
        res = [int(s) for s in res]
        candidates_scores = {candidates[i]: res[i] for i in range(min(len(res), len(candidates)))}
        print("---"*50)
        print(res)
        print("---"*50)
        return candidates_scores

    def get_clue_by_llm(self, clue_prpmpt:Optional[str],
                              dialogure:Optional[List[Dict]], 
                              utterance:str):
        history = [h["sentence"] if  type(h)==dict else h for h in dialogure]
        cur_prompt = clue_prpmpt.replace("history", str(history)).replace("query", utterance)
        res = self.requsest_llm(formatted_dialog=cur_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        print(f"****线索服务****:\n{res}")
        return res


    def generate_candidates_by_llm_rag(self, generate_prompt:Optional[str],
                                            dialog_record_str: Optional[str], 
                                            generate_text_list: Optional[List],
                                            clue_information: Optional[List]):
        cur_prompt = generate_prompt.replace("dialog_record_str", dialog_record_str).replace("generate_text_list", str(generate_text_list)).replace("clue_information", clue_information)
        res = self.requsest_llm(formatted_dialog=cur_prompt)
        if "</think>" in res:
            res = res.split("</think>")[1]
        res = ast.literal_eval(res)
        print("****rag候选话术****:\n",  res)
        return res


    def convert_to_qwen_format(self, init_msg: List[Dict]) -> List[Dict]:
        """
        将对话记录转换为 Qwen 格式
        """
        new_format = []
        for line in init_msg:
            if line["role"] == "CLIENT":
                new_format.append({"role": "user", "content": line["sentence"]})
            else:
                new_format.append({"role": "assistant", "content": line["sentence"]})
        return new_format


    def convert_my_format_to_center(self, history):
        """
            转换成中控的形式， 从系统提示词中抽取出 搜索词，引导语。
        """
        def convert(dialog):
            new_dialog = []
            for line in dialog:
                if line["role"] == "user":
                    new_dialog.append({"role": "CLIENT", "sentence": line["content"]})
                if line["role"] == "assistant":
                    new_dialog.append({"role": "SERVER", "sentence": line["content"]})
            return new_dialog
        new_msg = history[1:-1]
        _, search_text, guide_text = history[0]["content"].replace("你是儿科高级咨询师\n你的核心目标是获取访客联系方式。 ", "").split("\n")
        new_msg.insert(0, {"role": "user", "content": search_text})
        new_msg.insert(1, {"role": "assistant", "content": guide_text})
        user_utter = history[-1]["content"]
        if "action" in user_utter:
            user_utter = user_utter.split("action")[0]
        return search_text, convert(new_msg), user_utter


    def  pipeline(self, init_data: Optional[List],
                       clue_prpmpt: Optional[str],
                       rag_generate_prompt: Optional[str],
                       reward_prompt: Optional[str],
                       dpoFormatData_save_path: Optional[Path],
                       sftFormatData_save_path: Optional[Path]):
        message_id = 0
        for item in tqdm(init_data, total=len(init_data), desc="construct:"):
            # try:
                message_id += 1
                history = item["messages"]
                prompt_info = item["prompt_info"]
                candidates = item["candidates"]
                print(item["messages"])
                print("###"*50)
                search_text, dialog_record, user_utterance = self.convert_my_format_to_center(history)

                if len(clue_prpmpt) > 0:
                    clue_informations = self.get_clue_by_llm(clue_prpmpt=clue_prpmpt,
                                                            dialogure=dialog_record, 
                                                            utterance=user_utterance)
                else:
                    clue_informations = ""

                native_dialogure_chat_llm_generate_text_list = self.assistant_model.post_server_url_test(
                    dialog_record,
                    dialogId=message_id,
                    keyword=search_text,
                    utterance=user_utterance,
                    limit=5,
                    promptInfo=prompt_info
                )

                dialog_record_str = convert_general_to_dialogue_str(dialog_record, user_utterance)

                ### 加入大模型改写部分 ###
                rag_candidates = self.generate_candidates_by_llm_rag(generate_prompt=rag_generate_prompt,
                                                                     dialog_record_str=dialog_record_str, 
                                                                     generate_text_list=native_dialogure_chat_llm_generate_text_list,
                                                                     clue_information=clue_informations)

                print("****过滤后rag候选话术****:\n", rag_candidates)
                print("****线上模型生成话术****:\n", candidates)
                print("****本地模型生成话术****:\n", native_dialogure_chat_llm_generate_text_list)
                native_dialogure_chat_llm_generate_text_list.extend(rag_candidates)
                native_dialogure_chat_llm_generate_text_list.extend(candidates)


                ### 加入后处理函数 ### 

                print(len(native_dialogure_chat_llm_generate_text_list))
                native_dialogure_chat_llm_generate_text_list = self.post_process_sim_model.deduplicate_candidates(candidates=native_dialogure_chat_llm_generate_text_list)
                print(len(native_dialogure_chat_llm_generate_text_list))
                print(f"****去重后话术****:\n{native_dialogure_chat_llm_generate_text_list}")
                if self.is_use_postprocess_action_model:
                    native_dialogure_chat_llm_generate_text_list = self.post_process_action_model.process_by_action(native_dialogure_chat_llm_generate_text_list, server_round=(len(dialog_record)-1)//2+1) 
                    print(f"****action规则过滤后话术****:\n{native_dialogure_chat_llm_generate_text_list}")
                    print(len(native_dialogure_chat_llm_generate_text_list))
                
                
     
                
                reward_res = self.get_candidates_scores(reward_prompt=reward_prompt,
                                                        dialog_record_str=dialog_record_str,
                                                        candidates=native_dialogure_chat_llm_generate_text_list)
                rft_history = dialog_record.copy()
                if reward_res and isinstance(reward_res, dict):
                    dpo_history = dialog_record.copy()
                    dialog_record.append({"role": "CLIENT", "sentence": user_utterance})
                    rft_history.append({"role": "CLIENT", "sentence": user_utterance})
                    dpo_history.append({"role": "CLIENT", "sentence": user_utterance})
                    def append_and_convert(role, sentence, history):
                        """辅助函数用于追加句子并转换"""
                        temp_history = history.copy()
                        temp_history.append({"role": role, "sentence": sentence})
                        return self.convert_to_qwen_format(temp_history)
                    # 初始化偏好对列表
                    preference_pairs = get_random_chosen_rejected_pair(reward_res, threshold=3)
                    if preference_pairs:
                        chosen_text = preference_pairs["chosen"]
                        rejected_text = preference_pairs["rejected"]
                        chosen_pair = append_and_convert("assistant", chosen_text, history=dpo_history)
                        rejected_pair = append_and_convert("assistant", rejected_text, history=dpo_history)
                        item = {"chosen": chosen_pair, "rejected":rejected_pair}
                        item = add_system_prompt_for_train_data([item])
                        item = convert_chosen_rejected_to_prompt(item)[0]
                        with open(dpoFormatData_save_path, "a") as f:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")

                    highest_score_sentence =  max(reward_res, key=reward_res.get)
                    dialog_record.append({"role": "SERVER", "sentence": highest_score_sentence})
                    rft_history.append({"role": "SERVER", "sentence": highest_score_sentence})
                    
                
                    print("---"*50)
                    print(f"当前对话：{dialog_record}")
                    print("---"*50)
                    print()
                with open(sftFormatData_save_path, "a") as file:
                    rft_history = self.convert_to_qwen_format(rft_history)
                    file.write(json.dumps({"messages": rft_history}, ensure_ascii=False) + "\n")
            # except KeyboardInterrupt:
            #     break
            # except:
            #     continue
