from math import sin, cos, sqrt, atan2, radians
from models.util import create_embedding_file
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import pickle


class MapLoader:
    """현재 GPS기반으로 반경 r km 내의 음식점 리스트를 반환해주는 Class
    """
    def __init__(self, data_dir):
        with open(data_dir+"/food.pickle", "rb") as f:
            place = pickle.load(f)
            
        place['placeID'] = place.apply(lambda x: x['placeName'] + x['placeAddress'], axis=1)
        place['placeID'] = place['placeID'].apply(lambda x: x.replace(" ", ""))
        place['map'] = place[['longitude', 'latitude']].apply(lambda x: tuple(x.values), axis=1)
        self.place = place[~place.placeType.str.contains('성급')].reset_index().copy()

        self.R = 6373.0     # the earth radius
        self.r = 1
    
    def distance_from_coord(self, o_coord, d_coord):
        """두 지점의 위경도 좌표를 받아 거리를 계산해주는 함수
        Args:
            o_coord (tuple(lon,lat)): 지점1의 경도,위도 형식의 튜플
            d_coord (tuple(lon,lat)): 지점1의 경도,위도 형식의 튜플
        Returns:
            int: 두 지점사이의 거리(km)
        """

        x1, y1 = radians(o_coord[0]), radians(o_coord[1])
        x2, y2 = radians(d_coord[0]), radians(d_coord[1])
        dlon = x2 - x1
        dlat = y2 - y1
        a = sin(dlat / 2)**2 + cos(y1) * cos(y2) * sin(dlon / 2)**2 
        c = 2 * atan2(sqrt(a), sqrt(1 - a))    
        return self.R * c

    # def filtermap(self, coor):
    #     name=[]
    #     for idx,plc in enumerate(self.place['map']):
    #         if self.distance_from_coord(coor,plc)<=self.r:
    #             name.append(self.place.loc[idx]['placeID'])
    #     return name

    def filtermap(self, coor: tuple, r=0.5):
        """현 지점 기준 반경 r km까지의 음식점 리스트 반환
        Args:
            coor (tuple): (경도,위도)
            r (float, optional): Defaults to 0.5(km)
        Returns:
            List: 음식점이름+주소(placeID)
        """
        name = []
        lon, lan = coor[0], coor[1]
        maxLon, maxlan = coor[0] + 0.00028 * r/0.028, coor[1] + 0.00028 * r/0.031
        minLon, minlan = coor[0] - 0.00028 * r/0.028, coor[1] - 0.00028 * r/0.031
        mask1 = (self.place.latitude >= minlan) & (self.place.latitude < maxlan) & (self.place.longitude >= minLon) & \
                (self.place.longitude < maxLon)
        
        return self.place.loc[mask1, :]['placeIndex'].values.tolist()


class ReviewLoader:
    """리뷰데이터를 통해 user-item matrix를 생성
    """
    def __init__(self, data_dir, place_list):
        review_df = pd.read_csv(data_dir + 'review.csv')
        review_df = review_df[review_df.placeID.isin(place_list)].reset_index(drop=True)
        review_df = review_df[['userHash', 'placeID', 'timestamp']]
        review_df = review_df.groupby('userHash').filter(lambda x: len(x) > 2)
        review_df.reset_index(drop=True, inplace=True)
        self.review = review_df
        
        self.n_place = self.review.placeID.nunique()
        
        freq_df = self.review.groupby(['userHash', 'placeID']).count().reset_index().copy()
        freq_df.rename({'timestamp': 'count'}, axis=1, inplace=True)
        self.freq_df = freq_df
    
    def get_user_ratings(self, user_id, place2id):
        """user별 방문 및 평가한 음식점의 정보
        Args:
            user_id (str): user Hash값
            place2id (int): 장소의 Index
        Returns:
            np.array: user가 방문한 음식점 행렬
        """
        visited_df = self.freq_df[self.freq_df['userHash'] == user_id]
        visited_ids = []
        ratings = []
        for i,v in visited_df.iterrows():
            visited_ids.append(place2id[v['placeID']])
            ratings.append(v['count'])
        return visited_ids, ratings


class ContentBasedRecommender:
    """음식점 metadata를 이용한 추천모델 (Content-Based)
    """
    def __init__(self, data_dir, filename):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir, filename)
        self.cossim = cosine_similarity(self.place_emb)
        self.map_loader = MapLoader(data_dir=data_dir)
        self.map_loader.place['placeIndex'] = self.map_loader.place['placeID'].apply(lambda x: self.place2id[x])


    def get_nearest_cossim(self, nearest_list, place_id, k=5):
        """metapath2vec을 통한 음식점의 embedding vector가 유사한 k개의 음식점을 추천
        Args:
            nearest_list (List): 반경 r km내의 음식점리스트
            place_id (int): 선택 음식점의 인덱스
            k (int, optional): Defaults to 5(음식점 개수)
        Returns:
            List: 해당음식점과 embedding vector 거리가 유사한 k개의 음식점리스트
        """
        nearest_cossim = self.cossim[place_id, nearest_list]
        topk = np.argsort(nearest_cossim)[-(k+1):-1]
        return [self.id2place[nearest_list[i]] for i in topk]


    def recommend(self, coor, place_id, k=5):
        """유저의 현재 위경도 좌표를 기반으로 선택한 음식점과 가장 유사한 K개의 음식점 추천(Metapath2vec 임베딩기반)
        Args:
            coor (tuple): (경도,위도)
            place_id (int): 선택 음식점의 인덱스
        Returns:
            List: k개의 음식점리스트
        """
        nearest_list = self.map_loader.filtermap(coor)
        topk = self.get_nearest_cossim(nearest_list, self.place2id[place_id], k)
        return topk


class CollaborativeRecommender:
    """User 방문정보를 이용한 추천모델(Item-Based Collaborating Filtering)
    """
    def __init__(self, data_dir, filename):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir, filename)
        self.cossim = cosine_similarity(self.place_emb)
        self.map_loader = MapLoader(data_dir=data_dir)
        self.review_loader = ReviewLoader(data_dir=data_dir, place_list=self.map_loader.place.placeID.unique())
        
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn.fit(self.place_emb)
        self.knn_distances, self.knn_indices = self.knn.kneighbors(self.place_emb, n_neighbors=30)
        
        
        temp = self.map_loader.place.copy()
        self.map_loader.place = temp[temp.placeID.isin(self.review_loader.review.placeID.unique())].reset_index(drop=True)
        self.map_loader.place['placeIndex'] = self.map_loader.place['placeID'].apply(lambda x: self.place2id[x])


    def recommend(self, coor, user_id, k=5):
        """_summary_
        Args:
            coor (tuple): (경도,위도)
            user_id (str): user Hash값
            k (int, optional): Defaults to 5(개)
        Returns:
            List: k개의 음식점리스트
        """
        preds = dict()
        topk = []

        place_list = self.map_loader.filtermap(coor)
        visited_ids, ratings = self.review_loader.get_user_ratings(user_id, self.place2id)
        
        for pid in place_list:
            s = self.cossim[pid]
            total_sr = np.dot(s[visited_ids], ratings)
            total_s = np.sum(s[visited_ids])

            pred_un = total_sr / total_s
            preds[self.id2place[pid]] = pred_un

        topk = sorted(preds.items(), key= lambda x: x[1], reverse=True)
        topk = [_[0] for _ in topk][:k]
        return topk


class PopularityRecommender:
    def __init__(self, data_dir: str, filename: str):
        """Cold User를 위한 인기도 기반 추천 모델입니다.
        Args:
            data_dir (str): 데이터 폴더 위치
            filename (str): 임베딩 파일 이름
        """
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir, filename)
        self.map_loader = MapLoader(data_dir=data_dir)
        self.review_loader = ReviewLoader(data_dir=data_dir, place_list=self.map_loader.place.placeID.unique())
        
        review_count = self.review_loader.review.value_counts('placeID')
        self.review_loader.review['count'] = self.review_loader.review['placeID'].apply(lambda x: review_count[x])
        self.review_loader.review = self.review_loader.review.drop_duplicates(['placeID'])
        
        temp = self.map_loader.place.copy()
        self.map_loader.place = temp[temp.placeID.isin(self.review_loader.review.placeID.unique())].reset_index(drop=True)

        self.map_loader.place['placeIndex'] = self.map_loader.place['placeID'].apply(lambda x: self.place2id[x])
        self.map_loader.place = pd.merge(self.map_loader.place, self.review_loader.review[['placeID', 'count']], how='left', on='placeID')
        
        self.map_loader.place.sort_values('count', ascending=False, inplace=True)


    def recommend(self, coor: tuple, k:int =10) -> list:
        """인기도 기반 추천 함수
        Args:
            coor (tuple): (경도,위도)
            k (int, optional): 추천할 음식점 개수
        Returns:
            list: k개의 음식점 리스트
        """
        place_list = self.map_loader.filtermap(coor)[:k]
        topk = [self.id2place[p_id] for p_id in place_list]
        return topk


class NoRatingCollaborativeRecommender:
    """User 방문정보를 이용한 추천모델(Item-Based Collaborating Filtering)
    """
    def __init__(self, data_dir, filename):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir, filename)
        self.cossim = cosine_similarity(self.place_emb)
        self.map_loader = MapLoader(data_dir=data_dir)
        self.review_loader = ReviewLoader(data_dir=data_dir, place_list=self.map_loader.place.placeID.unique())
        
        temp = self.map_loader.place.copy()
        self.map_loader.place = temp[temp.placeID.isin(self.review_loader.review.placeID.unique())].reset_index(drop=True)
        self.map_loader.place['placeIndex'] = self.map_loader.place['placeID'].apply(lambda x: self.place2id[x])


    def recommend(self, coor, visited_list, k=5):
        """_summary_
        Args:
            coor (tuple): (경도,위도)
            user_id (str): user Hash값
            k (int, optional): Defaults to 5(개)
        Returns:
            List: k개의 음식점리스트
        """
        place_list = self.map_loader.filtermap(coor)
        visited_ids = [self.place2id[v] for v in visited_list if v in self.place2id.keys()]
        
        preds = dict()
        
        for pid in place_list:
            s = self.cossim[pid]
            total_s = np.sum(s[visited_ids])
    
            preds[self.id2place[pid]] = total_s

        topk = sorted(preds.items(), key= lambda x: x[1], reverse=True)
        topk = [_[0] for _ in topk][:k]
        
        return topk
