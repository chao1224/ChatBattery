import requests
from .domain_agent import Domain_Agent

MP_api_key = 'dKIoKI0IszchF9fuOD4jSBZYYLebhleX'



class Search_Agent:
    @staticmethod
    def ICSD_search(formula, ICSD_DB):
        for ICSD_formula in ICSD_DB:
            if Domain_Agent.range_match(formula, ICSD_formula):
                return True
        return False

    @staticmethod
    def MP_search(formula):
        from mp_api.client import MPRester
        try:
            with MPRester(MP_api_key) as mpr:
                # exact match
                docs = mpr.summary.search(formula=formula)
            return len(docs) >= 1
        except:
            return False


if __name__ == "__main__":
    # MP_search("Li2V2P2O9")
    # MP_search("Li2V2P2O9111")

    first = "Li1.249Mg0.014Mn0.5Co0.037Ni0.2O2"
    second = "Li1.166Mg0.026Mn0.333Co0.075Ni0.4O2"
    last = "Li1.067Mg0.04Mn0.133Co0.12Ni0.64O2"

    output_01 = "Li1.1Mg0.05Mn0.15Co0.1Ni0.6O2"
    output_02 = "Li1.2Mg0.025Mn0.35Co0.075Ni0.4O2"
    
    # range_match(first, output_01)
    # range_match(second, output_01)
    # range_match(last, output_01)
    # print("\n")

    print(range_match(first, output_02))
    print(range_match(second, output_02))
    print(range_match(last, output_02))


# TODO:
# 然后我这里遇到一个问题，就是我们上次说的比较两个很接近的分子式，应该怎么设定相似性条件。
# 两个分子式, 以及正则化之后的count如下:



# # first = "Li1.249Mg0.014Mn0.5Co0.037Ni0.2O2"
# element_count_01 {'O': 0.5, 'Ni': 0.05, 'Co': 0.00925, 'Mn': 0.125, 'Mg': 0.0035, 'Li': 0.31225}
# # output_02 = "Li1.2Mg0.025Mn0.35Co0.075Ni0.4O2"
# element_count_02 {'O': 0.4938 'Ni': 0.099, 'Co': 0.0185, 'Mn': 0.0864, 'Mg': 0.00617, 'Li': 0.2963}




# # second = "Li1.166Mg0.026Mn0.333Co0.075Ni0.4O2"
# element_count_01 {'O': 0.5, 'Ni': 0.1, 'Co': 0.01875, 'Mn': 0.08325, 'Mg': 0.0065, 'Li': 0.2915}
# # output_02 = "Li1.2Mg0.025Mn0.35Co0.075Ni0.4O2"
# element_count_02 {'O': 0.4938 'Ni': 0.099, 'Co': 0.0185, 'Mn': 0.0864, 'Mg': 0.00617, 'Li': 0.2963}

# # abs(0.5 - 0.49) / max(0.5, 0.49) \in [0, thershold=0.1] ==> same
# # abs(0.1 - 0.099) / max(0.1, 0.099) \in [0, thershold=0.1] ==> same




# # last = "Li1.067Mg0.04Mn0.133Co0.12Ni0.64O2"
# element_count_01 {'O': 0.5, 'Ni': 0.16, 'Co': 0.03, 'Mn': 0.03325, 'Mg': 0.01, 'Li': 0.26675}
# # output_02 = "Li1.2Mg0.025Mn0.35Co0.075Ni0.4O2"
# element_count_02 {'O': 0.4938 'Ni': 0.099, 'Co': 0.0185, 'Mn': 0.0864, 'Mg': 0.00617, 'Li': 0.2963}

