import argparse
from ChatBattery.domain_agent import Domain_Agent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="input_materials.csv")
    parser.add_argument('--output_file', type=str, default="output_materials.csv")
    args = parser.parse_args()
    
    f_in = open(args.input_file, "r")
    formula_list = []
    for line in f_in.readlines():
        line = line.strip()
        if len(line) == 0:
            continue

        flag = False
        for current_formula in formula_list:
            if Domain_Agent.range_match(current_formula, line):
                flag = True
                continue
        if not flag:
            formula_list.append(line)
        else:
            print(f"{line}\\\\")
    
    print("len of formula", len(formula_list))
    f_out = open(args.output_file, "w")
    for formula in formula_list:
        print(formula, file=f_out)