import dgl
from tqdm import trange
import os

# all features

def construct_graph(t_df, l_df, m_df) :
    hg = dgl.heterograph({
            ('place', 'pt', 'type') : (list(t_df['placeID']), list(t_df['type'])),
            ('type', 'tp', 'place') : (list(t_df['type']), list(t_df['placeID'])),
            ('place', 'pl', 'like') : (list(l_df['placeID']), list(l_df['like'])),
            ('like', 'lp', 'place') : (list(l_df['like']), list(l_df['placeID'])),
            ('place', 'pm', 'meta') : (list(m_df['placeID']), list(m_df['meta'])),
            ('meta', 'mp', 'place') : (list(m_df['meta']), list(m_df['placeID'])),
        })
    return hg
    
    
def create_metapath(graph, data_path, num_walks_per_node, walk_length, place_idx2id) :
    output_file = open(data_path, "w")
    for p_idx in trange(graph.number_of_nodes('place')):
        for metapath in [['pt', 'tp'], ['pl', 'lp'], ['pm', 'mp']]:
            traces, _ = dgl.sampling.random_walk(
                graph, [p_idx] * num_walks_per_node, metapath=metapath*walk_length)

            for tr in traces:
                tr = tr[tr[:,]!=-1]
                outline = ''
                for i in range(len(tr)) :
                    # i % 2 == 1 을 통해 type도 포함해서 문장 생성 가능
                    if i % 2 == 0 :
                        outline += place_idx2id[int(tr[i])] + ' '
                print(outline, file= output_file)
    output_file.close()