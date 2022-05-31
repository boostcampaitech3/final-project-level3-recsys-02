from math import sin, cos, sqrt, atan2, radians
from models.util import create_embedding_file
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import pickle


class MapLoader:
    def __init__(self, data_dir):
        with open(data_dir+"/food.pickle", "rb")  as f:
            place = pickle.load(f)
            
        place['placeID'] = place.apply(lambda x : x['placeName'] + x['placeAddress'], axis = 1)
        place['placeID'] = place['placeID'].apply(lambda x : x.replace(" ", ""))
        place['map'] = place[['longitude','latitude']].apply(lambda x: tuple(x.values),axis=1)
        self.place = place[~place.placeType.str.contains('성급')].reset_index().copy()


        self.R = 6373.0
        self.r = 1
    
    
    def distance_from_coord(self, o_coord, d_coord):
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

    def filtermap(self, coor, r=0.5):
        name=[]
        lon,lan = coor[0], coor[1]
        maxLon, maxlan = coor[0] + 0.00028 * r/0.028 , coor[1] + 0.00028 * r/0.031 
        minLon, minlan = coor[0] - 0.00028 * r/0.028 , coor[1] - 0.00028 * r/0.031
        mask1 = (self.place.latitude >= minlan) & (self.place.latitude < maxlan) & (self.place.longitude >= minLon) & (self.place.longitude < maxLon)
        
        return self.place.loc[mask1,:]['placeID']

class ReviewLoader:
    def __init__(self, data_dir, place_list):
        review_df = pd.read_csv(data_dir + 'review.csv')
        review_df = review_df[review_df.placeID.isin(place_list)].reset_index(drop=True)
        review_df = review_df[['userHash', 'placeID', 'timestamp']]
        review_df = review_df.groupby('userHash').filter(lambda x : len(x)>2)
        review_df.reset_index(drop=True, inplace=True)
        self.review = review_df
        
        self.n_place = self.review.placeID.nunique()
        
        freq_df = self.review.groupby(['userHash', 'placeID']).count().reset_index().copy()
        freq_df.rename({'timestamp':'count'}, axis=1, inplace=True)
        self.freq_df = freq_df
    
    def get_user_ratings(self, user_id, place2id):
        visited_df = self.freq_df[self.freq_df['userHash'] == user_id]
        ratings = np.zeros((self.n_place,))
        for i,v in visited_df.iterrows():
            visited_id = place2id[v['placeID']]
            ratings[visited_id] = v['count']
        return ratings


class ContentBasedRecommender:
    def __init__(self, data_dir, filename):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir,filename)
        self.cossim = cosine_similarity(np.array(self.place_emb))
        self.map_loader = MapLoader(data_dir=data_dir)

    
    def get_nearest_cossim(self, nearest_list, place_id, k=5):
        nearest_ids = [self.place2id[n] for n in nearest_list]
        nearest_cossim = self.cossim[place_id, nearest_ids[:]]
        topk = np.argsort(nearest_cossim)[::-1][1:k+1]
        return [self.id2place[nearest_ids[i]] for i in topk]
    
    
    def recommend(self, coor, place_id):
        nearest_list = self.map_loader.filtermap(coor)
        topk = self.get_nearest_cossim(nearest_list, place_id)
        return topk


class CollaborativeRecommender:
    def __init__(self, data_dir, filename):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir,filename)
        self.cossim = cosine_similarity(np.array(self.place_emb))
        self.map_loader = MapLoader(data_dir=data_dir)
        self.review_loader = ReviewLoader(data_dir=data_dir, place_list=self.map_loader.place.placeID.unique())
        
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn.fit(self.place_emb)
        self.knn_distances, self.knn_indices = self.knn.kneighbors(self.place_emb, n_neighbors=30)
        
        temp = self.map_loader.place.copy()
        self.map_loader.place = temp[temp.placeID.isin(self.review_loader.review.placeID.unique())].reset_index(drop=True)


    def recommend(self, coor, user_id, k=10):
        preds = []
        topk = []

        place_list = self.map_loader.filtermap(coor)
        place_ids = [self.place2id[p] for p in place_list]
        ratings = self.review_loader.get_user_ratings(user_id, self.place2id)
        
        for pid in place_ids:
            indices = self.knn_indices[pid]
            s = 1 - self.knn_distances[pid]
            
            total_sr = np.dot(s, ratings[indices])
            total_s = np.sum(s)
            
            pred_un = total_sr/total_s
            preds.append(pred_un)

        for idx in np.argsort(preds)[::-1][:k]:
            topk.append(place_ids[idx])
        
        return [self.id2place[pid] for pid in topk]

# class CossimRecommender:
#     def __init__(self, data_dir, filename):

#         self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir,filename)
#         self.cossim = cosine_similarity(np.array(self.place_emb))
#         self.map_loader = MapLoader(data_dir=data_dir)
        
    
#     def get_nearest_cossim(self, nearest_list, place_id, k=5):
#         # print(self.id2place[place_id])
#         nearest_ids = [self.place2id[n] for n in nearest_list]
#         nearest_cossim = self.cossim[place_id, nearest_ids[:]]
#         topk = np.argsort(nearest_cossim)[::-1][1:k+1]
#         return [self.id2place[nearest_ids[i]] for i in topk]
    
    
#     def recommend(self, coor, place_id):
#         nearest_list = self.map_loader.filtermap(coor)
#         topk = self.get_nearest_cossim(nearest_list, place_id)
#         return topk
    

#     def user_recommend(self, coor, user_emb, history_list, k=10):
#         result = []
#         nearest_list = self.map_loader.filtermap(coor)
#         nearest_ids = [self.place2id[n] for n in nearest_list]
#         user_embedding = user_emb.reshape(1,-1)
#         cossim = cosine_similarity(user_embedding, self.place_emb)
#         cossim = cossim.squeeze()
#         cossim[history_list] = -1
#         cossim = cossim[nearest_ids]

#         for idx in np.argsort(cossim)[::-1][:k]:
#             result.append(self.id2place[idx])
#         return result

# class Recommender:
#     def __init__(self, data_dir, filename):
#         self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir,filename)
#         self.cossim = cosine_similarity(np.array(self.place_emb))
#         self.map_loader = MapLoader(data_dir=data_dir)
        
#         self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
#         self.knn.fit(self.place_emb)
#         self.knn_distances, self.knn_indices = self.knn.kneighbors(self.place_emb, n_neighbors=30)
        
#         review_df = pd.read_csv(data_dir + 'review.csv')
#         review_df = review_df[review_df.placeID.isin(self.map_loader.place.placeID.unique())].reset_index(drop=True)
#         review_df = review_df[['userHash', 'placeID', 'timestamp']]
#         review_df = review_df.groupby('userHash').filter(lambda x : len(x)>2)
#         review_df.reset_index(drop=True, inplace=True)
#         self.review = review_df
        
#         self.n_place = self.review.placeID.nunique()
        
#         freq_df = self.review.groupby(['userHash', 'placeID']).count().reset_index().copy()
#         freq_df.rename({'timestamp':'count'}, axis=1, inplace=True)
#         self.freq_df = freq_df
        
#         temp = self.map_loader.place.copy()
#         self.map_loader.place = temp[temp.placeID.isin(self.review.placeID.unique())].reset_index(drop=True)



#     def get_user_ratings(self, user_id):
#         visited_df = self.freq_df[self.freq_df['userHash'] == user_id]
#         ratings = np.zeros((self.n_place,))
#         for i,v in visited_df.iterrows():
#             visited_id = self.place2id[v['placeID']]
#             ratings[visited_id] = v['count']
#         return ratings


#     def recommend(self, coor, user_id, k=10):
#         preds = []
#         topk = []

#         place_list = self.map_loader.filtermap(coor)
#         place_ids = [self.place2id[p] for p in place_list]
#         ratings = self.get_user_ratings(user_id)
        
#         for pid in place_ids:
#             indices = self.knn_indices[pid]
#             s = 1 - self.knn_distances[pid]
            
#             total_sr = np.dot(s, ratings[indices])
#             total_s = np.sum(s)
            
#             pred_un = total_sr/total_s
#             preds.append(pred_un)

#         for idx in np.argsort(preds)[::-1][:k]:
#             topk.append(place_ids[idx])
        
#         return [self.id2place[pid] for pid in topk]