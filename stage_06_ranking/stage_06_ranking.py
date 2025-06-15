import os
import argparse
from ChatBattery.rank_agent import Rank_Agent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", type=str, default="voltage")
    parser.add_argument("--top_k", type=int, default=3)
    parser.add_argument("--input_file", type=str, default="output_02.txt")
    parser.add_argument("--output_file", type=str, default="output_03.txt")
    parser.add_argument("--log_file", type=str, default=None)
    parser.add_argument("--log_folder", type=str, default=None)
    parser.add_argument("--LLM_type", type=str, default="chatgpt_4o")
    parser.add_argument("--temperature", type=float, default=1)
    args = parser.parse_args()

    if args.log_folder is not None:
        os.makedirs(args.log_folder, exist_ok=True)

    input_f_ = open(args.input_file, "r")
    formula_list = []
    for line in input_f_:
        formula_list.append(line.strip())

    if args.metric == "total_charge":
        record_list = Rank_Agent.rank_total_charge(formula_list)

        log_f_ = open(args.log_file, "w")
        for formula, total_charge in record_list:
            print("{}\t{}".format(formula.ljust(50), total_charge), file=log_f_)

        output_f = open(args.output_file, "w")
        for formula, _ in record_list[:args.top_k]:
            print(formula, file=output_f)

    elif args.metric == "preparation_complexity":
        record_list = Rank_Agent.rank_preparation_complexity(formula_list)

        log_f_ = open(args.log_file, "w")
        for formula, total_charge in record_list:
            print("{}&{}\\\\".format(formula.ljust(50), total_charge), file=log_f_)

        output_f = open(args.output_file, "w")
        for formula, _ in record_list[:args.top_k]:
            print(formula, file=output_f)

    elif args.metric == "voltage":
        sorted_formula_list = Rank_Agent.rank_voltage(formula_list, args)

        log_f_ = open(args.log_file, "w")
        for formula in sorted_formula_list:
            print(formula, file=log_f_)

        output_f_ = open(args.output_file, "w")
        for formula in sorted_formula_list[:args.top_k]:
            print(formula, file=output_f_)
