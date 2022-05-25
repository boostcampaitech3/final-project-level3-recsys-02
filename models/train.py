import os
import argparse
from sys import meta_path

from metapath2vec import Metapath2VecTrainer
from sampler import construct_graph, create_metapath
from util import remap_id

import pandas as pd


def train(args):

    if args.csv_filename:
        df = pd.read_csv(args.data_dir + args.csv_filename)
        place_id2idx, place_idx2id = remap_id(df['placeID'].unique())
        feature_id2idx, feature_idx2id = remap_id(df['feature'].unique())

        df['placeID'] = df['placeID'].apply(lambda x : place_id2idx[x])
        df['feature'] = df['feature'].apply(lambda x: feature_id2idx[x])
        
        graph = construct_graph(df)
        data_path = os.path.join(args.data_dir, args.metapath_filename)
        create_metapath(graph, data_path, args.num_walks_per_node, args.walk_length, place_idx2id)

    m2v = Metapath2VecTrainer(args)
    m2v.train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--csv_filename', type=str, default='', help='random seed (default: 42)')
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