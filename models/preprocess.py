import pandas as pd
import numpy as np
from util import remap_id

like_grouping = {"단체모임 하기 좋아요" : ["단체"], "인테리어가 멋져요" : ["감성"], "술이 다양해요" : ["술"], "오래 머무르기 좋아요" : ["단체"], \
                "대화하기 좋아요" : ["단체"], "혼밥하기 좋아요" : ["혼자"], "매장이 넓어요" : ["단체"], "특별한 날 가기 좋아요" : ["특별"], \
                "주차하기 편해요" : ["주차하기 편해요"], "음악이 좋아요" : ["감성"], "기본 안주가 좋아요" : ["술"], "뷰가 좋아요" : ["감성"], \
                "반찬이 잘 나와요" : ["반찬"], "혼술하기 좋아요" : ["술", "혼자"], "디저트가 맛있어요" : ["카페 관련"],  "좌석이 편해요" : ["카페관련"], \
                "커피가 맛있어요" : "카페 관련", "음료가 맛있어요" : "카페 관련", "신선해요" : "신선", "야외 공간이 멋져요" : "야외", \
                "고기 질이 좋아요": ["고기 질"], "사진이 잘 나와요" : ["감성", "야외"]}


type_grouping = \
{
    "한식" : ['한식', '국수', '냉면',  '한정식', '백반,가정식', '기사식당', '문래돼지불백', '비빔밥',],
    "찌개,전골,탕" : ['아부찌부대찌개','신의주부대찌개','찌개,전골', '감자탕','곰탕,설렁탕', '갈비탕'],
    "육류,구이" : ['돼지고기구이', '육류,고기요리', '정육식당', '고기뷔페', '고기원칙','소고기구이'],
    "중식" : ['중식당', '딤섬,중식만두', '신룽푸마라탕', '일품향'],
    "닭요리" : ['치킨,닭강정', '닭갈비', '닭요리', '오리요리','닭발', '찜닭', '닭볶음탕','일도씨닭갈비'],
    "회,생선" : ['생선회', '해물,생선요리', '생선구이', '수산물', '굴요리'],
    "일식" : ['일식당' ,'돈가스','일본식라면', '우동,소바', '일식튀김,꼬치', '오니기리', '덮밥', '초밥,롤', '카레'],
    "곱창,막창,양": ['곱창,막창,양'],
    "주류" : ['맥주,호프' ,'이자카야', '요리주점', '포장마차','전통,민속주점','오뎅,꼬치', '술집', '주류', '미친노가리'],
    "분식" : ['분식', '종합분식', '김밥', '달떡볶이', '떡볶이', '도시락,컵밥','만두'],
    "피자" : ['피자', '서오릉피자'],
    "햄버거" : ['햄버거', '후렌치후라이'],
    "족발,보쌈" : ['족발,보쌈','야식','막국수'],
    "칼국수" : ['칼국수,만두','밀겨울', '샤브샤브'],
    "죽" : ['죽'],
    "양식" : ['양식','스테이크,립', '패밀리레스토랑'],
    "이태리음식" : ['이탈리아음식', '스파게티,파스타전문', '스파게티스토리'],
    "양꼬치" : ['양꼬치','양갈비'],
    "아시아음식" :['베트남음식','아시아음식', '태국음식', '인도음식'],
    "와인,바" : ['와인', '바(BAR)'],
    "국밥" : ['국밥', '순대,순댓국', '해장국'],
    "다이어트,샐러드" : ['다이어트,샐러드','채식,샐러드뷔페'],
    "디저트" : ['샌드위치', '브런치','토스트','빙수', '핫도그', '호두과자', '도넛'],
    "장어,먹장어" : ['장어,먹장어요리'], 
    "오징어,낙지,조개" : ['주꾸미요리', '조개요리', '낙지요리', '오징어요리'],
    "아귀찜,해물찜" :['아귀찜,해물찜'],
    "복어요리" : ['복어요리'],
    "전,빈대떡" : ['전,빈대떡'],
    "서양음식" : ['멕시코,남미음식', '스페인음식', '프랑스음식', '그리스음식'],
    "몸보신" : ['추어탕', '백숙,삼계탕', '사철,영양탕', '매운탕,해물탕'],
    "퓨전음식" :['퓨전음식','두부요리'],
    "게,대게" : ['게요리', '대게요리' ,'킹크랩요리'],
    "뷔페" : ['뷔페','해산물뷔페', '일식,초밥뷔페', '한식뷔페'],
    "쌈밥" : ['쌈밥','보리밥'],
    "가공식품" : ['가공식품','반찬가게','푸드코트'],
    "향토음식" : ['향토음식', '이북음식'],
    '프랜차이즈본사' : ['프랜차이즈본사']
}


def make_type_data(raw_df):
    t_df = raw_df[['placeID', 'placeType']].copy()
    t_df.columns = ['placeID', 'type']
    
    t_df['type'] = t_df['type'].apply(lambda x : x.split(','))
    
    t_df = pd.DataFrame([
        [place_id, feature] for place_id, features in t_df.itertuples(index=False)
        for feature in features
    ], columns=t_df.columns)
    
    return t_df


def make_new_type_data(raw_df):
    
    def newcate(x):
        for _ in type_grouping.items():
            if x in _[1]:
                return _[0]
            
    raw_df['newType'] = raw_df['placeType'].apply(newcate)
    nt_df = raw_df[['placeID', 'newType']].copy()
    
    return nt_df


def make_like_data(df):
    like_df = pd.DataFrame([
        [p_id, like, cnt] for p_id, likes in df[['placeID', 'like']].itertuples(index=False)
        for like, cnt in likes.items()
    ], columns=['placeID', 'likeTopic', 'cnt'])

    topic_list = like_df['likeTopic'].value_counts().keys()[7:]
    like_df = like_df[like_df.likeTopic.isin(topic_list)]
    like_df = like_df[like_df.cnt>1]
    topic_mean = like_df.groupby('placeID').agg({"cnt":"mean"})
    topic_mean.rename(columns={"cnt":"cntMean"}, inplace=True)
    like_df = pd.merge(like_df, topic_mean, how='left', on='placeID')
    like_df = like_df[like_df.cnt > like_df.cntMean]

    except_topic_list = like_df['likeTopic'].unique()
    except_topic_list = list(set(like_df['likeTopic'].unique()) - set(like_grouping.keys()))

    like_df = like_df[~like_df.likeTopic.isin(except_topic_list)]
    like_df['likeTopic'] = like_df.apply(lambda x : like_grouping[x['likeTopic']], axis=1)

    like_df = pd.DataFrame([
        [p_id, topic] for p_id, topics in like_df[['placeID', 'likeTopic']].itertuples(index=False)
        for topic in topics
    ], columns=['placeID', 'like'])
    
    return like_df


def make_meta_data(raw_df,meta_df_col):
    # metadata 1개 컬럼으로
    
    raw_df['meta'] = raw_df[meta_df_col[1]]
    for col in meta_df_col[2:]:
        raw_df['meta'] += raw_df[col].astype(str)

    meta_df = raw_df[['placeID','meta']]
    meta_df = meta_df.dropna()
    
    return meta_df


def make_data(raw_df, meta_df_col= ['placeID', 'menulabel','ageLabel', 'ratingLabel', 'visitLabel', 'blogLabel']):
    t_df = make_type_data(raw_df)
    
    nt_df = make_new_type_data(raw_df)
    nt_df.rename(columns={'newType':'type'}, inplace=True)
    
    t_df = pd.concat([t_df, nt_df], axis=0)
    l_df = make_like_data(raw_df)
    
    m_df = make_meta_data(raw_df, meta_df_col)
    
    place2id, id2place = remap_id(raw_df['placeID'].unique())
    type2id, id2type = remap_id(t_df['type'].unique())
    like2id, id2like = remap_id(l_df['like'].unique())
    meta2id, id2meta = remap_id(m_df['meta'].unique())

    t_df['placeID'] = t_df['placeID'].apply(lambda x : place2id[x])
    t_df['type'] = t_df['type'].apply(lambda x: type2id[x])
    
    l_df['placeID'] = l_df['placeID'].apply(lambda x : place2id[x])
    l_df['like'] = l_df['like'].apply(lambda x: like2id[x])
    
    m_df['placeID'] = m_df['placeID'].apply(lambda x : place2id[x])
    m_df['meta'] = m_df['meta'].apply(lambda x: meta2id[x])
    
    return id2place, [t_df, l_df, m_df]