import dgl
from tqdm import trange
import os
import pandas as pd

# all features

def construct_graph(t_df: pd.core.frame.DataFrame, l_df: pd.core.frame.DataFrame, m_df: pd.core.frame.DataFrame) -> dgl.DGLGraph:
    """DGL을 통해 Node type이 여러개인 heterograph 구성

    Args:
        t_df (pd.core.frame.DataFrame): 장소별 타입이 담긴 DataFrame
        l_df (pd.core.frame.DataFrame): 장소별 이런점이 좋았어요 정보가 담긴 DataFrame
        m_df (pd.core.frame.DataFrame): 장소별 나이/연령대별 선호도와 같은 다양한 metadata가 담긴 DataFrame

    Returns:
        dgl.DGLGraph: 여러 노드 타입으로 구성된 Graph
    """
    hg = dgl.heterograph({
            ('place', 'pt', 'type') : (list(t_df['placeID']), list(t_df['type'])),
            ('type', 'tp', 'place') : (list(t_df['type']), list(t_df['placeID'])),
            ('place', 'pl', 'like') : (list(l_df['placeID']), list(l_df['like'])),
            ('like', 'lp', 'place') : (list(l_df['like']), list(l_df['placeID'])),
            ('place', 'pm', 'meta') : (list(m_df['placeID']), list(m_df['meta'])),
            ('meta', 'mp', 'place') : (list(m_df['meta']), list(m_df['placeID'])),
        })
    return hg
    
    
def create_metapath(graph, data_path: str, num_walks_per_node: int, walk_length: int, place_idx2id: dict) :
    """구성된 graph를 기반으로 Random Walk를 진행해 여러 metapath 생성

    Args:
        graph (dgl.DGLGraph): 앞서 정의된 노드로 구성된 Graph
        data_path (str): 생성된 여러 metapath를 저장할 파일 경로
        num_walks_per_node (int): Node 별 metapath(sentence) 개수
        walk_length (int): metapath(sentence) 별 최대 길이
        place_idx2id (dict): key -> 장소별 고유 ID, value -> 장소 이름인 dictionary
    """
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