import json
import argparse
import sys
import re
import pandas as pd
from collections import defaultdict
from ChatBattery.LLM_agent import LLM_Agent
from ChatBattery.domain_agent import Domain_Agent
from ChatBattery.search_agent import Search_Agent
from ChatBattery.decision_agent import Decision_Agent
from ChatBattery.retrieval_agent import Retrieval_Agent

from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")

global_already_started = False

global_conversation_list = []

global_LLM_messages = []
global_condition_list = []
global_input_battery_list = []
global_generated_text_list = []
global_generated_battery_list = []
global_optimal_generated_battery_list = []
global_battery_record = defaultdict(str)
global_retrieved_battery_record = defaultdict(str)


default_color           = "black"
human_agent_color       = "#9A8EAF"
LLM_agent_color         = "#AC7572"
domain_agent_color      = "#DAB989"
search_agent_color      = "#8BA297"
decision_agent_color    = "#788BAA"
retrieval_agent_color   = "#B5C5DE"


def show_content(content, color=default_color):
    if content.startswith("[Human Agent]"):
        color = human_agent_color
    elif content.startswith("[LLM Agent]"):
        color = LLM_agent_color
    elif content.startswith("[Domain Agent]"):
        color = domain_agent_color
    elif content.startswith("[Search Agent]"):
        color = search_agent_color
    elif content.startswith("[Decision Agent]"):
        color = decision_agent_color
    elif content.startswith("[Retrieval Agent]"):
        color = retrieval_agent_color
    global_conversation_list.append({"color": color, "text": content.replace("\n", "<br>")})
    print("global_conversation_list", global_conversation_list)
    return


def load_retrieval_DB(task_index):
    if task_index == 101:
        DBfile = 'data/Li_battery/preprocessed.csv'
    elif task_index == 102:
        DBfile = 'data/Na_battery/preprocessed.csv'
    else:
        raise NotImplementedError

    DB = pd.read_csv(DBfile)
    DB = DB[['formula']]

    return DB


def problem_conceptualization(input_battery, condition, task_index):
    mode = condition[0]

    if mode == "initial":
        if task_index == 101:
            task_index_prompt_template = "We have a Li cathode material FORMULA_PLACEHOLDER. Can you optimize it to develop new cathode materials with higher capacity and improved stability? You can introduce new elements from the following groups: carbon group, alkaline earth metals group, and transition elements, excluding radioactive elements; and incorporate new elements directly into the chemical formula, rather than listing them separately; and give the ratio of each element; and adjust the ratio of existing elements. My requirements are proposing five optimized battery formulations, listing them in bullet points (in asterisk *, not - or number or any other symbol), ensuring each formula is chemically valid and realistic for battery applications, and providing reasoning for each modification."
        elif task_index == 102:
            task_index_prompt_template = "We have a Na cathode material FORMULA_PLACEHOLDER. Can you optimize it to develop new cathode materials with higher capacity and improved stability? You can introduce new elements from the following groups: carbon group, alkaline earth metals group, and transition elements, excluding radioactive elements; and incorporate new elements directly into the chemical formula, rather than listing them separately; and give the ratio of each element; and adjust the ratio of existing elements. My requirements are proposing five optimized battery formulations, listing them in bullet points (in asterisk *, not - or number or any other symbol), ensuring each formula is chemically valid and realistic for battery applications, and providing reasoning for each modification."
        prompt = task_index_prompt_template.replace('FORMULA_PLACEHOLDER', input_battery)


    elif mode == "update_with_generated_battery_list":
        generated_battery_list = condition[1] # [ battery 1, battery 2, battery 3, ...]
        prompt = "You generated some existing or invalid battery compositions that need to be replaced with valid ones (one for each).\n"

        not_novel_list, invalid_list, valid_list = [], [], []
        for generated_battery in generated_battery_list:
            if global_battery_record[generated_battery] == "not novel":
                not_novel_list.append(generated_battery)
            elif global_battery_record[generated_battery] == "invalid":
                invalid_list.append(generated_battery)
            else:
                valid_list.append(generated_battery)
        
        if len(not_novel_list) > 0:
            not_novel_list = ["* {}".format(x) for x in not_novel_list]
            prompt += "These batteries have been discovered before:\n" + "\n".join(not_novel_list)
            prompt += "\n"

        if len(invalid_list) > 0:
            prompt_list = []
            for invalid_battery in invalid_list:
                retrieved_battery = global_retrieved_battery_record[invalid_battery]
                if retrieved_battery is not None:
                    prompt_list.append(f"* {invalid_battery} (a retrieved similar and correct battery is {retrieved_battery})\n")
                else:
                    prompt_list.append(f"* {invalid_battery}\n")
            prompt += "These invalid batteries are:\n" + "".join(prompt_list)

        prompt += "When replacing the invalid or existing compositions, you can replace the newly added elements with elements of lower atomic mass; and adjust the ratio of existing elements; and introduce new elements. The new compositions must be stable and have a higher capacity. The final outputs should include newly generated valid compositions, skip the retrieved batteries, and be listed in bullet points (in asterisk *, not - or number or any other symbol)."


    else:
        raise ValueError("Mode should be in [initial, reasoning, not novel, not correct, update_with_generated_battery_list].")

    return prompt


@app.route("/", methods=["GET", "POST"])
def index():
    render_in_textarea = False
    default_textarea = "No need to enter prompt."
    
    if request.method == "POST":
        print("request.form", request.form)

        print("===== messages =====")
        global global_LLM_messages
        for message in global_LLM_messages:
            print(message)
        print()
        
        if "button0" in request.form:
            global_LLM_messages = []
            global global_condition_list
            global_condition_list = []
            global global_input_battery_list
            global_input_battery_list = []
            global global_generated_text_list
            global_generated_text_list = []
            global global_generated_battery_list
            global_generated_battery_list = []
            global global_optimal_generated_battery_list
            global_optimal_generated_battery_list = []
            global global_battery_record
            global_battery_record = defaultdict(str)
            global global_retrieved_battery_record
            global_retrieved_battery_record = defaultdict(str)

            condition = ("initial",)
            global_condition_list.append(condition)

            global global_already_started
            color = "black"
            
            print("global_already_started", global_already_started)
            if global_already_started:
                show_content("<br><br><br>")

            show_content("=====" * 10)
            response_message = "[ChatBattery]\nStart editing. Please enter the input battery, and press button Step 1.1 to start.\n\n"
            show_content(response_message)

            if args['LLM_type'] in ["chatgpt_3.5"]:
                global_LLM_messages = [{"role": "system", "content": "You are an expert in the field of material and chemistry."}]
            else:
                global_LLM_messages = []

            default_textarea = "Please enter in your input battery."
            
            global_already_started = True



        elif "button1.1" in request.form:
            color = "#B7B2D0"
            show_content("========== Step 1. Problem Conceptualization ==========")
            color = "black"

            condition = global_condition_list[-1]
            if condition[0] == "initial":  # only add input_battery at the initial step
                input_battery = request.form.get("content_input").strip()
                global_input_battery_list.append(input_battery)
            else:
                input_battery = global_input_battery_list[-1]
                generated_battery_list = condition[1]
                valid_list = [x for x in generated_battery_list if global_battery_record[x] == "valid"]
                        
                if len(valid_list) > 0:
                    valid_list = ["* {}".format(x) for x in valid_list]
                    content = "[ChatBattery]\nThese are the valid batteries from previous round:\n" + "\n".join(valid_list)
                    content += "\n\n"
                    show_content(content)

            prompt = problem_conceptualization(condition=condition, input_battery=input_battery, task_index=task_index)
            content = "[Human Agent]\n{}\n\n".format(prompt)
            show_content(content)

            render_in_textarea = True
            default_textarea = prompt



        elif "button1.2" in request.form:
            next_step_instruction = "Next double-check or move to Step 2.1."

            prompt = request.form.get("content_input").replace(next_step_instruction, "").strip()
            content = "[Human Agent]\n{}\n\n".format(prompt)
            show_content(content)

            render_in_textarea = True
            default_textarea = prompt
            default_textarea = default_textarea + "\n\n" + next_step_instruction


        elif "button2.1" in request.form:
            show_content("========== Step 2. Hypothesis Generation ==========")

            content = request.form.get("content_input").strip()
            global_LLM_messages.append({"role": "user", "content": content})


            # NOTE: valid from previous round
            if len(global_generated_battery_list) > 0:
                generated_battery_list = global_generated_battery_list[-1]
                previous_valid_battery_list = [x for x in generated_battery_list if global_battery_record[x] == "valid"]
            else:
                previous_valid_battery_list = []
            
            # NOTE: valid from this round
            generated_text, generated_battery_list = LLM_Agent.optimize_batteries(global_LLM_messages, args['LLM_type'])
            global_LLM_messages.append({"role": "assistant", "content": generated_text})

            current_generated_battery_list = generated_battery_list
            if len(previous_valid_battery_list) > 0:
                current_generated_battery_list.extend([""] + previous_valid_battery_list)
            global_generated_battery_list.append(current_generated_battery_list)

            content = "[LLM Agent]\n{}\n\n".format(generated_text)
            show_content(content)

            default_textarea = "Next move to Step 2.2."


        elif "button2.2" in request.form:
            input_battery = global_input_battery_list[-1]
            generated_battery_list = global_generated_battery_list[-1]

            content = "[ChatBattery]\nPlease confirm if the following formula matches with the LLM (current and last rounds) replies."
            textarea_content = "Please confirm if the following formula matches with the LLM (current and last) replies."
            for idx, battery in enumerate(generated_battery_list):
                content = "{}\n* {}".format(content, battery)
                textarea_content = "{}\n* {}".format(textarea_content, battery)
            show_content(content + "\n\n")
            
            render_in_textarea = True
            default_textarea = textarea_content + "\n"



        elif "button2.3" in request.form:
            next_step_instruction = "Next double-check or move to Step 3.1."
            generated_battery_list = []


            textarea_content = "Confirmed: the following formula matches with the LLM (current and last) replies."
            previous_content = request.form.get("content_input").strip()
            content = "[ChatBattery]\nPlease confirm if the following formula matches with the LLM (current and last rounds) replies."
            for line in previous_content.split("\n"):
                if line.startswith("*"):
                    battery = line.replace("*", "").strip()
                    if len(battery) == 0:
                        continue
                    textarea_content = "{}\n* {}".format(textarea_content, battery)
                    content = "{}\n* {}".format(content, battery)
                    generated_battery_list.append(battery)
            show_content(content + "\n\n")
            
            render_in_textarea = True
            default_textarea = textarea_content
            default_textarea = default_textarea + "\n\n" + next_step_instruction

            global_generated_battery_list[-1] = generated_battery_list




        elif "button3.1" in request.form:
            show_content("========== Step 3. Hypothesis Feasibility Validation ==========")

            content = "[Search Agent]"
            generated_battery_list = global_generated_battery_list[-1]

            for generated_battery in generated_battery_list:
                global_battery_record[generated_battery] = "novel"

                content += "\n********** searching {} in DB **********\n".format(generated_battery)

                generated_battery_exist_ICSD = Search_Agent.ICSD_search(generated_battery, retrieval_DB["formula"].tolist())  # retrieval DB is ICSD DB
                if generated_battery_exist_ICSD:
                    global_battery_record[generated_battery] = "not novel"
                    content += "exists in ICSD database\n"
                else:
                    content += "does not exist in ICSD database\n"

                generated_battery_exist_MP = Search_Agent.MP_search(generated_battery)
                if generated_battery_exist_MP:
                    global_battery_record[generated_battery] = "not novel"
                    content += "exists in MP database"
                else:
                    content += "does not exist in MP database"
            
            show_content(content + "\n\n")
            default_textarea = default_textarea + "\nNext move to Step 4.1."



        elif "button4.1" in request.form:
            show_content("========== Step 4. Hypothesis Testing ==========")

            input_battery = global_input_battery_list[-1]
            generated_battery_list = global_generated_battery_list[-1]

            input_value = Domain_Agent.calculate_theoretical_capacity(input_battery, task_index)
            content = "[Domain Agent] Input battery is {} with capacity {:.3f}".format(input_battery, input_value)
            show_content(content)

            content = "[Decision Agent]"
            show_content(content)

            answer_list = Decision_Agent.decide_pairs(input_battery, generated_battery_list, task_index)
            for generated_battery, output_value, answer in answer_list:
                if global_battery_record[generated_battery] == "not novel":
                    content = "* Candidate optimized battery {} is not novel".format(generated_battery)
                else:
                    content = "* Candidate optimized battery {} is novel".format(generated_battery)

                if answer:
                    content += " and valid, <span style=\"color:{}\">with capacity {:.3f}</span>\n".format(domain_agent_color, output_value)
                else:
                    content += " and invalid, <span style=\"color:{}\">with capacity {:.3f}</span>\n".format(domain_agent_color, output_value)

                show_content(content, color=decision_agent_color)

                if global_battery_record[generated_battery] == "novel":
                    if answer:
                        global_battery_record[generated_battery] = "valid"

                    else:
                        global_battery_record[generated_battery] = "invalid"

                        try:
                            retrieved_battery, retrieved_capacity = Retrieval_Agent.retrieve_with_domain_feedback(task_index, retrieval_DB, input_battery, generated_battery)
                            retrieved_content = "[Retrieval Agent] Retrieved battery {} <span style=\"color:{}\">with capacity {:.3f}</span> is the most similar to the candidate optimized battery and serves as a valid optimization to the input battery.".format(
                                retrieved_battery, domain_agent_color, retrieved_capacity)
                        except:
                            retrieved_battery = None
                            retrieved_content = "[Retrieval Agent] No valid battery is retrieved."
                        
                        global_retrieved_battery_record[generated_battery] = retrieved_battery
                        show_content(retrieved_content)


            all_pass = True
            for generated_battery in generated_battery_list:
                if global_battery_record[generated_battery] == "valid":
                    continue
                else:
                    all_pass = False
                
            if all_pass:
                default_textarea = "Answer found! Please move to Step 5.1."
            else:
                condition = ("update_with_generated_battery_list", generated_battery_list)
                global_condition_list.append(condition)
                default_textarea = "Answers not correct. Please go back to Step 1.1."
            
            show_content("\n\n")


        else:
            response_message = "Please enter your next input battery for editing:"

    return render_template(
        "index.html",
        content_list=global_conversation_list,
        render_in_textarea=render_in_textarea,
        default_textarea=default_textarea,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task_index', required=False, type=int, default=101)
    parser.add_argument('--LLM_type', required=False, type=str, default='chatgpt_3.5', choices=["chatgpt_3.5", "chatgpt_o1", "chatgpt_o3"], help='only support chatgpt now')
    args = parser.parse_args()
    args = vars(args)

    task_index = args['task_index']

    retrieval_DB = load_retrieval_DB(task_index)

    app.run(debug=True)
