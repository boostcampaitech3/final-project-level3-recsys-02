import dgl
from tqdm import trange
import os

# all features

def construct_graph(df) :
    hg = dgl.heterograph({
            ('place', 'pf', 'feature') : (list(df['placeID']), list(df['feature'])),
            ('feature', 'fp', 'place') : (list(df['feature']), list(df['placeID'])),
            })
    return hg


def create_metapath(graph, data_path, num_walks_per_node, walk_length, place_idx2id) :
    output_file = open(data_path, "w")
    for p_idx in trange(graph.number_of_nodes('place')):
        traces, _ = dgl.sampling.random_walk(
            graph, [p_idx] * num_walks_per_node, metapath=['pf', 'fp'] * walk_length)

        for tr in traces:
            tr = tr[tr[:,]!=-1]
            outline = ''
            for i in range(len(tr)) :
                # i % 2 == 1 을 통해 type도 포함해서 문장 생성 가능
                if i % 2 == 0 :
                    outline += place_idx2id[int(tr[i])] + ' '
            print(outline, file= output_file)
    output_file.close()