import torch
import numpy as np

from torch.utils.data import Dataset

### 문장으로 만들어 저장한 metapath2vec.txt를 불러오는 과정
class DataReader:
    """여러 metapath들을 읽어오는 클래스
    """
    NEGATIVE_TABLE_SIZE = 1e8

    def __init__(self, file_name: str, min_count: int, care_type: int):
        """ 여러 metapath들이 담긴 파일 Loading 및 Negative Sampling

        Args:
            file_name (str): 여러 metapath들이 담긴 파일의 이름
            min_count (int): 파일 내 단어의 최소 빈도수
            care_type (int): Negative Sampling을 위한 변수
        """
        self.negatives = []
        self.discards = []
        self.negpos = 0
        self.care_type = care_type
        self.word2id = dict() # 임베딩 생성할 단어와 학습과정에 사용할 인덱스
        self.id2word = dict() # 임베딩 생성할 단어와 학습과정에 사용할 인덱스
        self.sentences_count = 0
        self.token_count = 0
        self.word_frequency = dict()
        self.inputFileName = file_name
        self.read_words(min_count)
        self.initTableNegatives()
        self.initTableDiscards()

    def read_words(self, min_count: int): 
        """텍스트 파일 읽으면서 각각 단어 등장 빈도 세기를 측정
        
        Args:
            min_count (int): 파일 내 단어의 최소 빈도수
        """
        print("Read Words...")
        word_frequency = dict()
        for line in open(self.inputFileName):
            line = line.split()
            if len(line) > 1:
                self.sentences_count += 1
                for word in line:
                    if len(word) > 0:
                        self.token_count += 1
                        word_frequency[word] = word_frequency.get(word, 0) + 1 # get(key, default)

                        if self.token_count % 1000000 == 0:
                            print("Read " + str(int(self.token_count / 1000000)) + "M words.")

        wid = 0
        for w, c in word_frequency.items(): # min_count 미만인 단어는 제외하고 단어 dictionary 생성
            if c < min_count:
                continue
            self.word2id[w] = wid
            self.id2word[wid] = w
            self.word_frequency[wid] = c
            wid += 1

        self.word_count = len(self.word2id)
        print("Total embeddings: " + str(len(self.word2id)))

    def initTableDiscards(self):
        """sub-sampling을 위해 frequency를 구하는 함수
        """
        t = 0.0001
        f = np.array(list(self.word_frequency.values())) / self.token_count
        self.discards = np.sqrt(t / f) + (t / f)

    def initTableNegatives(self):
        """Negative Sampling을 위해 Table을 미리 만들어두는 함수
        """
        pow_frequency = np.array(list(self.word_frequency.values())) ** 0.75
        words_pow = sum(pow_frequency)
        ratio = pow_frequency / words_pow
        count = np.round(ratio * DataReader.NEGATIVE_TABLE_SIZE)
        for wid, c in enumerate(count):
            self.negatives += [wid] * int(c)
        self.negatives = np.array(self.negatives)
        np.random.shuffle(self.negatives)
        self.sampling_prob = ratio

    def getNegatives(self, size: int) -> np.array:  # TODO check equality with target
        """호출 시 앞서 만들어둔 Negatives table에서 sampling

        Args:
            size (int): Negative Sample 개수

        Returns:
            numpy.array: Negative Sample들이 담긴 numpy array
        """
        if self.care_type == 0:
            response = self.negatives[self.negpos:self.negpos + size]
            self.negpos = (self.negpos + size) % len(self.negatives)
            if len(response) != size:
                return np.concatenate((response, self.negatives[0:self.negpos]))
        return response


# Metapath2vec Dataset
class Metapath2vecDataset(Dataset):
    """Metapath2Vec 학습 데이터 클래스
    """
    def __init__(self, data:DataReader, window_size:int):
        """Metapath2Vec 학습 데이터 생성을 위한 변수 설정

        Args:
            data (DataReader): Metapath들이 담긴 파일을 불러오고 Negative Sampling을 수행하는 instance
            window_size (int): 학습 시 타겟 단어 중심으로 볼 단어의 개수
        """
        self.data = data
        self.window_size = window_size
        self.input_file = open(data.inputFileName)

    def __len__(self) -> int:
        """Dataset의 총 길이

        Returns:
            int: 총 Metapath 개수
        """
        return self.data.sentences_count

    def __getitem__(self, idx:int) -> list:
        # return the list of pairs (center, context, 5 negatives)
        """Metapath2Vec 학습에 사용되는 Data Return

        Args:
            idx (int): DataLoader가 Dataset 호출을 위해 사용하는 index

        Returns:
            list: 중심단어, 주변단어, Negative Sample들이 담긴 list
        """
        while True:
            line = self.input_file.readline()
            if not line:
                self.input_file.seek(0, 0)
                line = self.input_file.readline()

            if len(line) > 1:
                words = line.split()

                if len(words) > 1:
                    word_ids = [self.data.word2id[w] for w in words if
                                w in self.data.word2id and np.random.rand() < self.data.discards[self.data.word2id[w]]]

                    pair_catch = []
                    for i, u in enumerate(word_ids):
                        for j, v in enumerate(
                                word_ids[max(i - self.window_size, 0):i + self.window_size]):
                            assert u < self.data.word_count
                            assert v < self.data.word_count
                            if i == j:
                                continue
                            pair_catch.append((u, v, self.data.getNegatives(v,5)))
                    return pair_catch


    @staticmethod
    def collate(batches:list) -> tuple:
        """Batch에 담긴 list들을 모델에 맞게 변환

        Args:
            batches (list): 중심 단어, 주변단어, Negative Sample들이 담긴 list들의 list

        Returns:
            tuple:
                torch.LogTensor(all_u): Batch 내 중심 단어들만 담긴 Tensor
                torch.LogTensor(all_v): Batch 내 주변 단어들만 담긴 Tensor
                torch.LogTensor(all_neg_v): Batch 내 Negative Sample들만 담긴 Tensor
        """
        all_u = np.array([u for batch in batches for u, _, _ in batch if len(batch) > 0])
        all_v = np.array([v for batch in batches for _, v, _ in batch if len(batch) > 0])
        all_neg_v = np.array([neg_v for batch in batches for _, _, neg_v in batch if len(batch) > 0])

        return torch.LongTensor(all_u), torch.LongTensor(all_v), torch.LongTensor(all_neg_v)