from collections import defaultdict
import re


def parse_formula(formula):
    def multiply_counts(base_counts, multiplier):
        for element in base_counts:
            base_counts[element] *= multiplier
        return base_counts

    def merge_counts(total_counts, new_counts):
        for element, count in new_counts.items():
            total_counts[element] += count

    def parse_segment(segment):
        pattern = r'([A-Z][a-z]*)(\d*\.\d+|\d*)'
        matches = re.findall(pattern, segment)
        segment_counts = defaultdict(int)
        for element, count in matches:
            count = float(count) if count else 1
            segment_counts[element] += count
        return segment_counts

    def parse_hydrate(formula):
        # 匹配水合物部分及其系数和误差
        match = re.search(r'(\d*\.?\d*)\((\d*)\)H2O', formula)
        if match:
            coefficient = float(match.group(1))
            error = float(match.group(2))
            return coefficient, error

        match = re.search(r'(\d*\.?\d*)H2O', formula)
        if match:
            if match.group(1) == "":
                coefficient = 1
            else:
                coefficient = float(match.group(1))
            return coefficient, 0

        else:
            return None, None

    def recursive_parse(formula):
        stack = []
        index = 0
        while index < len(formula):
            if formula[index] == '(':
                stack.append('(')
                index += 1
            elif formula[index] == ')':
                sub_formula = []
                while stack and stack[-1] != '(':
                    sub_formula.append(stack.pop())
                stack.pop()  # remove '('
                sub_formula.reverse()
                sub_formula = ''.join(sub_formula)
                multiplier_match = re.match(r'(\d*\.\d+|\d+)', formula[index+1:])
                if multiplier_match:
                    multiplier = float(multiplier_match.group())
                    index += len(multiplier_match.group())
                else:
                    multiplier = 1
                sub_counts = recursive_parse(sub_formula)
                multiplied_counts = multiply_counts(sub_counts, multiplier)
                stack.append(multiplied_counts)
                index += 1
            else:
                element_match = re.match(r'[A-Z][a-z]*(\d*\.\d+|\d*)', formula[index:])
                if element_match:
                    element_str = element_match.group()
                    stack.append(element_str)
                    index += len(element_str)
                else:
                    index += 1

        combined_counts = defaultdict(int)
        while stack:
            item = stack.pop()
            if isinstance(item, str):
                segment_counts = parse_segment(item)
                merge_counts(combined_counts, segment_counts)
            elif isinstance(item, dict):
                merge_counts(combined_counts, item)

        return combined_counts

    # remove "[]"
    formula = formula.replace("[", "")
    formula = formula.replace("]", "")

    # only consider the first element
    if "/" in formula:
        formula_split = formula.split("/")
        formula = formula_split[0]

    # count hydrate
    parsed_hydrate_results = {}
    if "·" in formula:
        formula_split = formula.split("·")
        hydrate_component = formula_split[1]
        formula = formula_split[0]
        coefficient, error = parse_hydrate(hydrate_component)
        parsed_hydrate_results = {
            "H": 2 * (coefficient + error * 0.01),
            "O": coefficient + error * 0.01,
        }

    parsed_results = recursive_parse(formula)
    for element in ["H", "O"]:
        if element in parsed_results and element in parsed_hydrate_results:
            parsed_results[element] += parsed_hydrate_results[element]
        elif element in parsed_hydrate_results:
            parsed_results[element] = parsed_hydrate_results[element]

    return parsed_results


class Domain_Agent:

    @staticmethod
    def distance_function(task_index, formula_01, formula_02):
        count_01 = parse_formula(formula_01)
        count_02 = parse_formula(formula_02) #这里可能不需要解析了，我把PO4拆成P和O了

        # total_count_01 = sum(count_01.values())
        # for k, v in count_01.items():
        #     count_01[k] = count_01[k] / total_count_01
        # total_count_02 = sum(count_02.values())
        # for k, v in count_02.items():
        #     count_02[k] = count_02[k] / total_count_02

        # TODO: need to discuss the weights
        coefficient_01 = 3   # for Li or Na
        coefficient_02 = 7   # for Mn, Co, Ni
        coefficient_03 = 5   # for Fe, Cu, Zn, V, Cr, Ti, Mo
        coefficient_04 = 10   # for O, P, F, S, Cl, Br, I
        coefficient_05 = 5   # for Mg, Al, Si, B, Zr, C, Be, Ca, Na, K, Sn, Sr
        coefficient_06 = 1   # for others
        # transition_metal_penalty = 50 # New_1 无过渡金属加重惩罚

        element_level_01_set = set(["Li"])
        element_level_02_set = set(["Mn", "Co", "Ni"])
        element_level_03_set = set(["Fe", "Cu", "Zn", "V", "Cr", "Ti", "Mo"])
        element_level_04_set = set(["O", "P", "F", "S", "Cl", "Br", "I"])
        element_level_05_set = set(["Mg", "Al", "Si", "B", "Zr", "C", "Be", "Ca", "Na", "K", "Sn", "Sr"])
        element_level_06_set = set(list(atomic_weights.keys())) - element_level_01_set - element_level_02_set - element_level_03_set - element_level_04_set - element_level_05_set
        
        distance = 0
        
        for element in element_level_01_set:
            count_01[element] = count_01.get(element, 0) # New_2 
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_01 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_01 # New_2

        for element in element_level_02_set:
            count_01[element] = count_01.get(element, 0) # New_2 
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_02 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_02 # New_2

        for element in element_level_03_set:
            count_01[element] = count_01.get(element, 0) # New_2
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_03 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_03 # New_2

        for element in element_level_04_set:
            count_01[element] = count_01.get(element, 0) # New_2
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_04 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_04 # New_2

        for element in element_level_05_set:
            count_01[element] = count_01.get(element, 0) # New_2
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_05 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_05 # New_2

        for element in element_level_06_set:
            count_01[element] = count_01.get(element, 0) # New_2
            count_02[element] = count_02.get(element, 0) # New_2
            distance += coefficient_06 * abs(count_01[element] - count_02[element])
            # total_weight += coefficient_06 # New_2

        # 元素个数差异 * 10
        distance += 10 * abs(len(count_01) - len(count_02))

        return distance

    @staticmethod
    def normalize_composition(comp_dict):
        total = sum(comp_dict.values())
        return {element: count / total for element, count in comp_dict.items()}

    @staticmethod
    def range_match(formula_01, formula_02, tolerance_threshold=0.1):
        element_count_01 = parse_formula(formula_01)
        element_count_02 = parse_formula(formula_02)

        # if elements are different, return False
        if element_count_01.keys() != element_count_02.keys():
            return False

        element_count_01 = Domain_Agent.normalize_composition(element_count_01)
        element_count_02 = Domain_Agent.normalize_composition(element_count_02)

        for element in element_count_01.keys():
            count_01 = element_count_01[element]
            count_02 = element_count_02[element]

            normalized_diff = abs(count_01 - count_02) / max(count_01, count_02)
            if normalized_diff > tolerance_threshold:
                return False
        
        return True

    @staticmethod
    def calculate_molecular_weight(elements_count):
        weight = 0
        for element, count in elements_count.items():
            weight += atomic_weights[element] * count
        return weight

    @staticmethod
    def calculate_theoretical_capacity(formula, task_id):
        elements_count = parse_formula(formula)
        if task_id == 101:
            target_element_count = elements_count['Li']
        elif task_id == 102:
            target_element_count = elements_count['Na']
        molecular_weight = Domain_Agent.calculate_molecular_weight(elements_count)
        theoretical_capacity = 96500 * target_element_count * (1 / molecular_weight) * (1 / 3.6)
        return theoretical_capacity

    @staticmethod
    def calculate_total_charge(compound):
        if isinstance(compound, str):
            compound = parse_formula(compound)
        total_charge = 0
        for element, count in compound.items():
            # NOTE: double-check
            if element not in highest_oxidation_states:
                continue
            total_charge += count * highest_oxidation_states[element]
        return total_charge



# https://eels.info/atlas
atomic_weights = {
    'H': 1.008,
    'He': 4.0026,
    'Li': 6.94,
    'Be': 9.0122,
    'B': 10.81,
    'C': 12.01,
    'N': 14.01,
    'O': 16.00,
    'F': 19.00,
    'Ne': 20.18,
    'Na': 22.99,
    'Mg': 24.305,
    'Al': 26.98,
    'Si': 28.085,
    'P': 30.974,
    'S': 32.06,
    'Cl': 35.45,
    'K': 39.10,
    'Ar': 39.95,
    'Ca': 40.08,
    'Sc': 44.96,
    'Ti': 47.867,
    'V': 50.94,
    'Cr': 52.00,
    'Mn': 54.94,
    'Fe': 55.845,
    'Co': 58.93,
    'Ni': 58.693,
    'Cu': 63.546,
    'Zn': 65.38,
    'Ga': 69.723,
    'Ge': 72.63,
    'As': 74.922,
    'Se': 78.96,
    'Br': 79.904,
    'Kr': 83.798,
    'Rb': 85.468,
    'Sr': 87.62,
    'Y': 88.906,
    'Zr': 91.224,
    'Nb': 92.906,
    'Mo': 95.95,
    'Tc': 98.00,
    'Ru': 101.07,
    'Rh': 102.91,
    'Pd': 106.42,
    'Ag': 107.87,
    'Cd': 112.41,
    'In': 114.82,
    'Sn': 118.71,
    'Sb': 121.76,
    'Te': 127.60,
    'I': 126.90,
    'Xe': 131.29,
    'Cs': 132.91,
    'Ba': 137.33,
    'Ra': 226,
    'Fl': 289,
    'La': 138.91,
    'Ce': 140.12,
    'Pr': 140.91,
    'Nd': 144.24,
    'Pm': 145.00,
    'Sm': 150.36,
    'Eu': 151.96,
    'Gd': 157.25,
    'Tb': 158.93,
    'Dy': 162.50,
    'Ho': 164.93,
    'Er': 167.26,
    'Tm': 168.93,
    'Yb': 173.05,
    'Lu': 174.97,
    'Hf': 178.49,
    'Ta': 180.95,
    'W': 183.84,
    'Re': 186.21,
    'Os': 190.23,
    'Ir': 192.22,
    'Pt': 195.08,
    'Au': 196.97,
    'Hg': 200.59,
    'Tl': 204.38,
    'Pb': 207.2,
    'Bi': 208.98,
    'Th': 232.04,
    'Pa': 231.04,
    'U': 238.03,
    'Pu': 244.06,
    'Np': 237.05,
    'Po': 209.00,
    'At': 210.00,
}


highest_oxidation_states = {
    "C": 4, "Si": 4, "Ge": 4, "Sn": 4, "Pb": 4,
    "Be": 2, "Mg": 2, "Ca": 2, "Sr": 2, "Ba": 2,
    "Sc": 3, "Ti": 4, "V": 3, "Cr": 3, "Mn": 3, "Fe": 3, "Co": 3, "Ni": 3, "Cu": 2, "Zn": 2, "Mo": 6, "Zr":4, "Y": 3,
    "Li": 1, "O": -2, "Na": 1, "K": 1,
    "B": 3, "Al": 3, "Ga": 3,
}


if __name__ == "__main__":
    formula_list = [
        "Li2CoPO4F",
        "LiCoPO4",
        # "LiVPO4F",
        # "LiVPO4OH",
        # "LiVP2O7",
        # "Li3V2(PO4)3",
        # "LiFePO4",
        # "LiCoO2",
        # "LiNiO2",
        # "LiMnO2",
        "LiNi0.8Mn0.1Co0.1O2",
        "LiNiMnAlO2",
        "Na4Fe(CN)6/NaCl",
        "Na1.88(5)Fe[Fe(CN)6]·0.18(9)H2O",
        "NaFe[Fe(CN)6]",

    ]
    for formula in formula_list:
        print(formula)
        result_01 = parse_formula(formula)
        print(result_01)
        # result_02 = parse_formula(formula)
        # print(result_02)
        print()

    formulat_list = [
        "Li1.249Mg0.014Mn0.5Co0.037Ni0.2O2",
        "Li1.166Mg0.026Mn0.333Co0.075Ni0.4O2",
        "Li1.116Mg0.033Mn0.233Co0.098Ni0.52O2",
        "Li1.067Mg0.04Mn0.133Co0.12Ni0.64O2",
        
        "Li1.2Mg0.091Si0.13Mn0.2Co0.04Ni0.23O2",
        "Li1.2Mg0.087Si0.08Mn0.25Co0.05Ni0.28O2",
    ]
    for formula in formulat_list:
        capacity = calculate_theoretical_capacity(formula, 101)
        print(formula, capacity)

    """
    Li1.249Mg0.014Mn0.5Co0.037Ni0.2O2 406.32548197416196
    Li1.166Mg0.026Mn0.333Co0.075Ni0.4O2 359.60351781017135
    Li1.116Mg0.033Mn0.233Co0.098Ni0.52O2 333.7102889357721
    Li1.067Mg0.04Mn0.133Co0.12Ni0.64O2 309.8108584181272
    
    Li1.2Mg0.091Si0.13Mn0.2Co0.04Ni0.23O2 440.42572326290104
    Li1.2Mg0.087Si0.08Mn0.25Co0.05Ni0.28O2 413.4273934206137
    """

    distance_function(101, "Li1.249Mg0.014Mn0.5Co0.037Ni0.2O2PO4", "Li1.166Mg0.026Mn0.333Co0.075Ni0.4O2")