from math import sin, cos, sqrt, atan2, radians
from models.util import create_embedding_file
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


    def filtermap(self, coor):
        name=[]
        for idx,plc in enumerate(self.place['map']):
            if self.distance_from_coord(coor,plc)<=self.r:
                name.append(self.place.loc[idx]['placeID'])
        return name


class CossimRecommender:
    def __init__(self, data_dir):
        self.id2place, self.place2id, self.place_emb = create_embedding_file(data_dir)
        self.cossim = cosine_similarity(np.array(self.place_emb))
        self.map_loader = MapLoader(data_dir=data_dir)
        
    
    def get_nearest_cossim(self, nearest_list, place_id, k=5):
        print(self.id2place[place_id])
        nearest_ids = [self.place2id[n] for n in nearest_list]
        nearest_cossim = self.cossim[place_id, nearest_ids[:]]
        topk = np.argsort(nearest_cossim)[::-1][1:k+1]
        return [self.id2place[nearest_ids[i]] for i in topk]
    
    
    def recommend(self, coor, place_id):
        nearest_list = self.map_loader.filtermap(coor)
        topk = self.get_nearest_cossim(nearest_list, place_id)
        return topk