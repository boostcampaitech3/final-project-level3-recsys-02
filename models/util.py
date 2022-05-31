import numpy as np
import pickle


def remap_id(id_lst: list) -> tuple:
    """ id_list을 sorting하여 순서대로 Re-Indexing

    Args:
        id_list(list): 원본 데이터 list

    Returns:
        tuple:
            id_to_idx(dict): key -> 원본 데이터, value -> 새로운 id인 dictionary
            idx_to_id(dict): key -> 새로운 id, value -> 원본 데이터인 dictionary
    """
    id_lst.sort()
    id_to_idx, idx_to_id = dict(), dict()
    for index, value in enumerate(id_lst):
        id_to_idx[value] = index
        idx_to_id[index] = value
    return id_to_idx, idx_to_id 


def create_embedding_file(data_dir: str, filename: str) -> tuple:
    """ embedding numpy 파일과 pickle 파일을 Load

    Args:
        data_dir(str): embedding 파일이 저장된 directory 위치
        filename(str): embedding 파일 이름

    Returns:
        tuple: 
            id2word(dict): key -> embedding numpy index / value -> 장소인 dictionary
            word2id(dict): key -> 장소 / value -> embedding numpy index인 dictionary
            embeddings(numpy.array): metapath2vec을 통해 나온 장소 embedding
    """
    embed_path = data_dir + filename
    embeddings = np.load(embed_path+'.npy')
    with open(embed_path + '_id2word.pkl', 'rb') as f:
        id2word = pickle.load(f)
    
    word2id = {v: k for k, v in id2word.items()}
    return id2word, word2id, embeddings
