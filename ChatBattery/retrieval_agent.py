from .decision_agent import Decision_Agent
from .domain_agent import Domain_Agent


class Retrieval_Agent:
    @staticmethod
    def retrieve_with_domain_feedback(task_index, DB, input_battery, generated_battery):
        distance_DB = DB.copy()
        distance_list = []
        for index, row in distance_DB.iterrows():
            formula = row['formula']
            distance = Domain_Agent.distance_function(task_index, formula, generated_battery)
            distance_list.append(distance)
        distance_DB['distance'] = distance_list
        
        distance_DB = distance_DB.sort_values(by=['distance'], ascending=True)
        print("head")
        print(distance_DB.head(20))
        print("tail")
        print(distance_DB.tail(20))
        print()

        for index, row in distance_DB.iterrows():
            retrieved_battery = row['formula']
            if generated_battery == retrieved_battery:
                continue
            input_value, output_value, answer = Decision_Agent.decide_one_pair(input_battery, retrieved_battery, task_index)
            print("input battery: {} ({:.3f})\tretrieved battery: {} ({:.3f})".format(input_battery, input_value, retrieved_battery, output_value))

            if answer:
                print()
                return retrieved_battery, output_value
        raise Exception("Sorry, cannot fined a good formula.")

