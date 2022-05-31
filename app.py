import argparse
import asyncio
import json
# from tkinter import _PlaceInfo
from modules.broker import Broker
from modules.events import ServerLog
from models.model import ContentBasedRecommender, PopularityRecommender
from models.model import NoRatingCollaborativeRecommender


async def main(kwargs: argparse.Namespace):
    logger = ServerLog()
    broker = Broker(kwargs.host, logger)
    await broker.connect()
    await broker.subscribe(kwargs.durable, kwargs.stream, kwargs.subject)
    await broker.createBucket('inference')

    pp = PopularityRecommender('/opt/ml/final-project-level3-recsys-02/data/', 'pu_embeddings_1km') 
    cb = ContentBasedRecommender('/opt/ml/final-project-level3-recsys-02/data/', 'final_embeddings')
    cf = NoRatingCollaborativeRecommender('/opt/ml/final-project-level3-recsys-02/data/', 'pu_embeddings_1km')

    while True:
        try:
            batch = await broker.pull(kwargs.batch, timeout=0.5)

            """
            여기 inference logic 넣어주세요.
            아래 if batch 이하 코드는 echo return 입니다.
            """

            if batch:
                for headers, data in batch:
                    # ~ 유저 아이디
                    key = headers.get('key')
                    payload = {}

                    """
                    유저 아이디 가져오는 부분이랑 결과 리턴 사이에서 inference logic 이 실행
                    """
                    
                    coor = (data['longitude'], data['latitude'])
                    if len(data['preferences']) == 0:
                        topk = pp.recommend(coor, k=10)
                    elif len(data['preferences']) < 3:
                        for preference in data['preferences']:
                            topk = cb.recommend(coor, preference, k=int(10/len(data['preferenes'])))
                    else :
                        topk = cb.recommend(coor, data['preferences'][-1], k=5)
                        cf_topk = cf.recommend(coor, data['preferences'], k=5)
                        topk.extend(cf_topk)

                    for place in topk:
                        # print(place)
                        PlaceInfo = {}
                        PlaceInfo['name'] = place
                        lon, lat = pp.map_loader.place[pp.map_loader.place['placeID'] == place]['map'].values[0]
                        PlaceInfo['latitude'] = lat
                        PlaceInfo['longitude'] = lon
                        payload[place] = PlaceInfo

                    # 결과 리턴
                    print(payload)
                    data = json.dumps(payload, ensure_ascii=False).encode()

                    await broker.createKey(key=key, value=data)
        except:
            import traceback
            print(traceback.format_exc())


if __name__ == '__main__':
    config = argparse.ArgumentParser(description='How to run an Inference Server')
    config.add_argument('--host', type=str, required=True, help='host "IP:port" formatted string')
    config.add_argument('--durable', type=str, required=True, help='an inference server identifier')
    config.add_argument('--stream', type=str, required=True, help='a stream name')
    config.add_argument('--subject', type=str, required=True, help='a subject name to subscribe to')
    config.add_argument('--batch', default=100, type=int, help='determine a batch size to be inferred at a time')
    args = config.parse_args()
    print(type(args))
    asyncio.run(main(args))
