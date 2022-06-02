from common.util import *
from common.network import *


# 파일 읽기
def loadList(listPath: str) -> list:
    with open(listPath, 'rb') as fp:
        return pickle.load(fp)

# 장소 이름
def getPlaceName(util: Util):
    name = set(util.getNamelist(sub_list=Subway))
    util.constructPickle('name_list', name)


# 장소 & 리뷰 정보
def getPlaceInfo(util:Util, startidx: int, finalidx: int):
    geoLocal = Nominatim(user_agent='South Korea')
    placeList = loadList('./data/name_list_final.pkl')

    for idx, (name, address) in enumerate(placeList[startidx:finalidx], start=startidx):
        placeName = name + " " + address
        result = util.getPlaceInfoDetails(geoLocal, placeName)
        if not result:
            util.errorLogger.logger.error(f"{idx} {placeName}")
        util.indexLogger.logger.error(f"{idx} {placeName}")


    # # constructPickle('./data/no_place', noPlace)
    # util.constructPickle('./data/resend_place', resend.PlaceInfoModel)
    # util.constructPickle('./data/resend_review', resend.ReviewInfoModel)
    # util.constructPickle('./data/resend_user', resend.UserInfoModel)


if __name__ == '__main__':
    # 서버 http://ip:port
    host = ''
    
    # 로그 파일 & 웹드라이버 경로
    indexLogPath = ''
    errorLogPath = ''
    webdriverPath = ''

    # 장소 index
    startIndex = 0
    endIndex = 22000
    util = Util(host, indexLogPath, errorLogPath, webdriverPath)
    getPlaceInfo(util, startIndex, endIndex)
