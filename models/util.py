def remap_id(id_lst) :
    id_lst.sort()
    id_to_idx, idx_to_id = dict(), dict()
    for index, value in enumerate(id_lst) :
        id_to_idx[value] = index
        idx_to_id[index] = value
    return id_to_idx, idx_to_id 


def create_embedding_file(data_dir) :
    with open(data_dir + 'metapath_embeddings', 'r') as f:
        id2word_len, emb_dimension = f.readline().split()
        id2word = {}
        word2id = {}
        embeddings = []
        idx = 0
        while True :
            z = f.readline()
            if not z :
                break
            z = z.split()
            word = z[0]
            embedding = list(map(float, z[1:]))
            embeddings.append(embedding)
            id2word[idx] = word
            word2id[word] = idx
            idx += 1
    return id2word, word2id, embeddings