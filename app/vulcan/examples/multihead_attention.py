from vulcan.pickle_builder.pickle_builder import PickleBuilder
import random
import json


def main():
    pickle_builder = PickleBuilder({"English": "string", "German": "string"})
    pickle_builder.add_instance_by_name("English", "The fox tricked the tiger")
    pickle_builder.add_instance_by_name("German", "Der Fuchs hat den Tiger ausgetrickst")


    base_attention_scores_g2e = [[0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, .2, .7, 0, .1]]

    base_attention_scores_g2g = [[0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0],
                                 [0, .2, .5, 0.1, .2, 0]]

    num_heads = 4
    num_layers = 6

    linker_g2e_data = [get_half_random_attentions(base_attention_scores_g2e, num_heads, num_layers, False)]

    linker_g2g_data = [get_half_random_attentions(base_attention_scores_g2g, num_heads, num_layers, True)]


    final_data = pickle_builder._make_data_for_pickle()
    final_data.append({"type": "linker",
                       "name1": "German",
                       "name2": "English",
                       "scores": linker_g2e_data})

    final_data.append({"type": "linker",
                       "name1": "German",
                       "name2": "German",
                       "scores": linker_g2g_data})

    with open("theFoxTrickedTheTigerMultiheadAttention.json", "w") as f:
        json.dump(final_data, f)


def get_half_random_attentions(base_attention_scores_g2e, num_heads, num_layers, last_entry_is_0):
    linker_g2e_data = {}
    for i, row in enumerate(base_attention_scores_g2e):
        linker_g2e_data[i] = {}
        for j, score in enumerate(row):
            table = []
            for layer in range(num_layers):
                table.append([])
                for head in range(num_heads):
                    if j < len(row)-1 or not last_entry_is_0:
                        if random.random() > 0.5:
                            table[-1].append((3*score + random.random()) / 4)
                        else:
                            table[-1].append((score + random.random()) / 2)
                    else:
                        table[-1].append(0)
            linker_g2e_data[i][j] = table
    return linker_g2e_data


if __name__ == '__main__':
    main()
