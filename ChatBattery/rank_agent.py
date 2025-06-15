import os
from ChatBattery.domain_agent import Domain_Agent, parse_formula
from ChatBattery.LLM_agent import LLM_Agent


class Rank_Agent:
    @staticmethod
    def rank_total_charge(formula_list):
        record_list = []
        for formula in formula_list:
            compound = parse_formula(formula)
            total_charge = Domain_Agent.calculate_total_charge(compound)
            record_list.append([formula, total_charge])

        record_list.sort(key=lambda x: abs(x[1]), reverse=False)

        return record_list

    @staticmethod
    def rank_preparation_complexity(formula_list):
        record_list = []
        for formula in formula_list:
            compound = parse_formula(formula)
            preparation_complexity = len(compound)
            record_list.append([formula, preparation_complexity])

        record_list.sort(key=lambda x: abs(x[1]), reverse=False)
        return record_list


    def rank_voltage(formula_list, args):
        total_formula_to_index = {}
        for idx, formula in enumerate(formula_list):
            total_formula_to_index[formula] = idx

        def compare_first_better_than_second(formula_01, formula_02):
            template = """
        Could you compare the two Li cathode materials, {} and {}, and identify which one has a higher voltage vs. Li+/Li (V)?
        List the better one in the last line, marked by '*'.
            """
            i, j = total_formula_to_index[formula_01], total_formula_to_index[formula_02]
            prompt = template.format(formula_01, formula_02).strip()

            if args.LLM_type in ["chatgpt_3.5"]:
                global_LLM_messages = [{"role": "system", "content": "You are an expert in the field of material and chemistry."}]
            else:
                global_LLM_messages = []
            global_LLM_messages.append({"role": "user", "content": prompt})

            found = None
            while found is None:
                print("comparing [{}, {}] .....".format(i, j))
                log_file = os.path.join(args.log_folder, "pair_{}_{}.log".format(i, j))

                if os.path.exists(log_file):
                    answer = open(log_file, "r").readlines()
                    answer = "\n".join(answer).strip()
                    found = parse_LLM_voltage_ranking(answer, formula_01, formula_02)
                else:
                    answer = LLM_Agent.rank_batteries(global_LLM_messages, LLM_type=args.LLM_type, temperature=args.temperature)
                    found = parse_LLM_voltage_ranking(answer, formula_01, formula_02)
                    if found is not None:
                        f_ = open(log_file, "w")
                        print("========== Prompt ==========", file=f_)
                        print(prompt, file=f_)
                        print("\n\n\n\n\n", file=f_)
                        print("========== LLM ==========", file=f_)
                        print(answer, file=f_)
                        break
            
            if found == formula_list[i]:
                return True
            else:
                return False

        def merge(left, right):
            sorted_list = []
            i = j = 0
            while i < len(left) and j < len(right):
                if compare_first_better_than_second(left[i], right[j]):
                    sorted_list.append(left[i])
                    i += 1
                else:
                    sorted_list.append(right[j])
                    j += 1
            sorted_list.extend(left[i:])
            sorted_list.extend(right[j:])
            return sorted_list

        def merge_sort(arr):
            if len(arr) <= 1:
                return arr
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return merge(left, right)

        sorted_formula_list = merge_sort(formula_list)

        return sorted_formula_list


def parse_LLM_voltage_ranking(answer, formula_01, formula_02):
    answer = answer.split("\n")[-1].replace("*", "")
    if answer == formula_01:
        return answer
    elif answer == formula_02:
        return answer
    return None
