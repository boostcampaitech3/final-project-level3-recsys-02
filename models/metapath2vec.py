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

    def __init__(self, emb_size: int, emb_dimension: int):
        """SkipGram 모델 클래스
        metapath를 skipgram 방식으로 loss를 계산합니다.

        Args:
            emb_size (int): 아이템 수
            emb_dimension (int): 임베딩 차원 크기
        """
        super(SkipGramModel, self).__init__()
        self.emb_size = emb_size
        self.emb_dimension = emb_dimension
        self.u_embeddings = nn.Embedding(emb_size, emb_dimension, sparse=True)
        self.v_embeddings = nn.Embedding(emb_size, emb_dimension, sparse=True)

        initrange = 1.0 / self.emb_dimension
        init.uniform_(self.u_embeddings.weight.data, -initrange, initrange)
        init.constant_(self.v_embeddings.weight.data, 0)

    def forward(self, pos_u: int, pos_v: int, neg_v: np.ndarray) -> torch.Tensor:
        """Skipgram 학습을 위한 forward 함수

        Args:
            pos_u (int): 학습할 타겟 대상
            pos_v (int): 학습할 타겟 대상의 positive 항목
            neg_v (np.ndarray): 학습할 타겟 대상의 negative 항목

        Returns:
            torch.Tensor: positive 항목과의 임베딩 차이 - negative 항목과의 임베딩 차이의 평균
        """
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
        """각 장소의 임베딩을 학습하기 위한 Metapath2vec 클래스 입니다.

        한 번 이상이라도 등장한 장소에 대해서는 모두 임베딩을 생성합니다.
        관련 초기 값들은 train.py 실행 시 입력 인자를 통해 변경 가능합니다.
        """
        min_count, care_type = args.min_count, args.care_type # 임베딩 생성 기준 최소 등장 횟수
        batch_size, iterations = args.batch_size, args.iterations # 배치 사이즈, iter 횟수(1 권장)
        window_size, dim, initial_lr = args.window_size, args.embed_dim, args.lr # window size, 임베딩 dimension 크기, 학습률
        
        self.data_dir = args.data_dir
        self.metapath_filename = args.metapath_filename # metapath 파일 이름
        self.embed_filename = args.embed_filename # 임베딩 파일 이름
        self.data = DataReader(self.data_dir+self.metapath_filename, min_count, care_type)
        dataset = Metapath2vecDataset(self.data, window_size)
        self.dataloader = DataLoader(dataset, batch_size=batch_size,
                                     shuffle=True, collate_fn=dataset.collate)
        self.emb_size = len(self.data.word2id) # 임베딩 수 (장소 수)
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
        """Metapath2vec 학습 함수입니다.
        random walk를 통해 생성한 metapath를 Skipgram 클래스를 사용하여 loss를 계산합니다.
        타겟 임베딩과 postive 항목의 임베딩은 가깝게, negative 항목의 임베딩은 멀어지게 업데이트 하여 장소 임베딩을 학습합니다.

        생성된 임베딩은 numpy.array 형태로 저장을 하며
        장소와 임베딩의 index를 mapping하기 위한 dictionary 형태로 저장합니다.
        """
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