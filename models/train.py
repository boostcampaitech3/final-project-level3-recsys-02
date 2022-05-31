import os
import argparse
from sys import meta_path

from metapath2vec import Metapath2VecTrainer
from sampler import construct_graph, create_metapath
from preprocess import make_data

import pandas as pd
import pickle


def train(args:argparse.ArgumentParser):
    """Metapath2Vec 학습을 위한 코드

    Args:
        args (argparse.ArgumentParser): Metapath2Vec 학습 시 필요한 변수들이 담긴 객체
    """
    if args.make_metapath:
        with open(args.data_dir + 'food.pickle', 'rb') as f :
            raw_df = pickle.load(f)
        raw_df = raw_df[~raw_df.placeType.str.contains('성급')].reset_index().copy()
        raw_df['placeID'] = raw_df.apply(lambda x : x['placeName'] + x['placeAddress'], axis = 1)
        raw_df['placeID'] = raw_df['placeID'].apply(lambda x : x.replace(" ", ""))
        
        id2place, df_list = make_data(raw_df)
        graph = construct_graph(*df_list)
        data_path = os.path.join(args.data_dir, args.metapath_filename)
        create_metapath(graph, data_path, args.num_walks_per_node, args.walk_length, id2place)

    m2v = Metapath2VecTrainer(args)
    m2v.train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--make_metapath', type=bool, default=True, help='random seed (default: 42)')
    parser.add_argument('--data_dir', type=str, default='/opt/ml/final-project-level3-recsys-02/data/', help='random seed (default: 42)')
    parser.add_argument('--metapath_filename', type=str, default='all_metapath.txt', help='random seed (default: 42)')    
    parser.add_argument('--embed_filename', type=str, default='all_metapath_embeddings', help='random seed (default: 42)')
    parser.add_argument('--num_walks_per_node', type=int, default=10, help='random seed (default: 42)')
    parser.add_argument('--walk_length', type=int, default=5, help='random seed (default: 42)')
    parser.add_argument('--iterations', type=int, default=1, help='random seed (default: 42)')
    parser.add_argument('--window_size', type=int, default=10, help='random seed (default: 42)')
    parser.add_argument('--batch_size', type=int, default=50, help='random seed (default: 42)')
    parser.add_argument('--lr', type=float, default=0.025, help='random seed (default: 42)')
    parser.add_argument('--embed_dim', type=int, default=128, help='random seed (default: 42)')
    parser.add_argument('--min_count', type=int, default=0, help='random seed (default: 42)')
    parser.add_argument('--care_type', type=int, default=0, help='random seed (default: 42)')
    
    args = parser.parse_args()
    print(args)
    
    train(args)