import torch
import torch.nn as nn
from torch.nn import init
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torch.optim as optim
import pickle
import numpy as np

from tqdm import tqdm
from reading_data import DataReader, Metapath2vecDataset


class SkipGramModel(nn.Module):

    def __init__(self, emb_size, emb_dimension):
        super(SkipGramModel, self).__init__()
        self.emb_size = emb_size
        self.emb_dimension = emb_dimension
        self.u_embeddings = nn.Embedding(emb_size, emb_dimension, sparse=True)
        self.v_embeddings = nn.Embedding(emb_size, emb_dimension, sparse=True)

        initrange = 1.0 / self.emb_dimension
        init.uniform_(self.u_embeddings.weight.data, -initrange, initrange)
        init.constant_(self.v_embeddings.weight.data, 0)

    def forward(self, pos_u, pos_v, neg_v):
        emb_u = self.u_embeddings(pos_u)
        emb_v = self.v_embeddings(pos_v)
        emb_neg_v = self.v_embeddings(neg_v)

        score = torch.sum(torch.mul(emb_u, emb_v), dim=1)
        score = torch.clamp(score, max=10, min=-10)
        score = -F.logsigmoid(score)

        neg_score = torch.bmm(emb_neg_v, emb_u.unsqueeze(2)).squeeze()
        neg_score = torch.clamp(neg_score, max=10, min=-10)
        neg_score = -torch.sum(F.logsigmoid(-neg_score), dim=1)

        return torch.mean(score + neg_score)
                

# Metapath2vec 
class Metapath2VecTrainer:
    def __init__(self, args):
        min_count, care_type = args.min_count, args.care_type
        batch_size, iterations = args.batch_size, args.iterations
        window_size, dim, initial_lr = args.window_size, args.embed_dim, args.lr
        
        self.data_dir = args.data_dir
        self.metapath_filename = args.metapath_filename
        self.embed_filename = args.embed_filename
        self.data = DataReader(self.data_dir+self.metapath_filename, min_count, care_type)
        dataset = Metapath2vecDataset(self.data, window_size)
        self.dataloader = DataLoader(dataset, batch_size=batch_size,
                                     shuffle=True, collate_fn=dataset.collate)
        self.emb_size = len(self.data.word2id)
        self.emb_dimension = dim
        self.batch_size = batch_size
        self.iterations = iterations
        self.initial_lr = initial_lr
        self.skip_gram_model = SkipGramModel(self.emb_size, self.emb_dimension)

        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        if self.use_cuda:
            self.skip_gram_model.cuda()


    def train(self):
        optimizer = optim.SparseAdam(list(self.skip_gram_model.parameters()), lr=self.initial_lr)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, len(self.dataloader))

        for iteration in range(self.iterations):
            print("\n\n\nIteration: " + str(iteration + 1))
            running_loss = 0.0
            for i, sample_batched in enumerate(tqdm(self.dataloader)):
                
                if len(sample_batched[0]) > 1:
                    pos_u = sample_batched[0].to(self.device)
                    pos_v = sample_batched[1].to(self.device)
                    neg_v = sample_batched[2].to(self.device)

                    optimizer.zero_grad()
                    loss = self.skip_gram_model.forward(pos_u, pos_v, neg_v)
                    loss.backward()
                    optimizer.step()

                    running_loss = running_loss * 0.9 + loss.item() * 0.1
                    if i > 0 and i % 50000 == 0:
                        print(" Loss: " + str(running_loss))
                
                    scheduler.step()
        
        embed_path = self.data_dir+self.embed_filename
        np.save(embed_path, self.skip_gram_model.u_embeddings.weight.detach().cpu().numpy())
        with open(embed_path+'_id2word.pkl', 'wb') as f:
            pickle.dump(self.data.id2word, f)