import pickle
import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
import time
import re

from geopy.geocoders import Nominatim
from .logger import Logger
from .config import *
from .network import *


class Util:
    def __init__(self, host, indexLogPath, errorLogPath, webdriverPath):
        self.host = host
        self.indexLogger = Logger(indexLogPath, "1")
        self.errorLogger = Logger(errorLogPath, "2")
        self.driver = self.loadDriver(webdriverPath)

    # Driver load & get place list
    def loadDriver(self, driver_path: str):
        service = Service(driver_path)
        option = webdriver.ChromeOptions()
        option.add_experimental_option("excludeSwitches", ["enable-logging"])
        option.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/101.0.4951.41 Safari/537.36')
        driver = webdriver.Chrome(service=service, options=option)
        return driver

    # loop for blocking-call
    def loop(self, func):
        tStart = time.perf_counter()
        tElapsed = 0.0
        while tElapsed <= 5.0:
            time.sleep(0.1)
            func()
            tElapsed = time.perf_counter() - tStart

    # # file log
    # def setLogger(file_name):
    #     logger = logging.getLogger()
    #     logger.setLevel(logging.ERROR)
    #     formatter = logging.Formatter(u'%(asctime)s %(message)s')
    #     fileHandler = logging.FileHandler(f'./log/{file_name}.log')
    #     fileHandler.setFormatter(formatter)
    #     logger.addHandler(fileHandler)
    #     return logger

    # element 여러개 반환
    def getElements(self, driver: webdriver, timeout: int, kind: By, value: str) -> list:
        try:
            elements = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((kind, value))
            )
            return elements
        except exceptions.TimeoutException:
            # print('')
            return []
        except Exception as error:
            print("Unexpected Exception")
            print(error)
            return []

    # element 값 하나 반환
    def getValue(self, driver: webdriver, timeout: int, kind: By, value: str) -> str:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((kind, value))
            )
            return element.text
        except exceptions.TimeoutException:
            return ""

        except Exception as error:
            print("Unexpected Exception")
            print(error)
            return ""

    # iframe 전환
    def switchToFrame(self, driver: webdriver, timeout: int, kind: By, value: str) -> bool:
        try:
            ack = WebDriverWait(driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((kind, value))
            )
            return ack
        except exceptions.TimeoutException:
            return False

        except Exception as error:
            print("Unexpected Exception")
            print(error)
            return False

    # click 하기
    def click(self, driver: webdriver, timeout: int, kind: By, value: str, index: int = 0) -> bool:
        try:
            time.sleep(1)
            fetched = self.getElements(driver, timeout, kind, value)[index]
            time.sleep(1)
            fetched.click()
            return True
        except exceptions.ElementClickInterceptedException:
            return False
        except IndexError:
            return False
        except:
            return False

    # scroll 끝까지 내리기
    def scrollDown(self, driver: webdriver):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as scrollError:
            print("scrollDown Error")
            print(traceback.format_exc())

    # 검색어 입력
    def search(self, driver: webdriver, keyword: str):
        try:
            search_path = XPath.searchPathKakao
            search_box = self.getElements(driver, 0.5, By.XPATH, search_path)
            actions = ActionChains(driver).send_keys_to_element(search_box[0], keyword).send_keys(Keys.ENTER)
            actions.perform()
        except Exception as searchError:
            print("Search Error")
            print(traceback.format_exc())

    # 도로명 주소 위도 경도 변환
    def geocoding(self, geoLocal: Nominatim, address: str) -> (float, float):
        address = " ".join(address.split(' ')[:4])
        try:
            geo = geoLocal.geocode(address)
            return (geo.latitude, geo.longitude)
        except Exception as geoError:
            return 0.0, 0.0

    # json 파일 생성
    def constructJson(self, fileName: str, data: list):
        with open(f'{fileName}.json', 'w', encoding='utf-8') as fp:
            json.dump(data, fp)

    # pickle 파일 생성
    def constructPickle(self, fileName: str, data):
        with open(f'{fileName}.pkl', 'wb') as f:
            pickle.dump(data, f)

    # subway 맛집 검색
    def getSuburl(self, driver: webdriver, sub):
        driver.get(URL.basePath)
        self.click(driver, 1, By.XPATH, XPath.sheild)
        time.sleep(1)
        self.search(driver, sub + "역 맛집")  # 검색어 입력
        self.click(driver, 1, By.XPATH, XPath.more)  ##  장소더보기 클릭 (모든 페이지 접근 위해)

    # 모든 페이지 정보 불러오기
    def getPageList(self, driver: webdriver, no):
        nameList = []
        time.sleep(1)
        self.click(driver, 1, By.XPATH, XPath.pageNo.format(no), )  # 페이지 클릭
        time.sleep(1)
        name = self.getElements(driver, 1, By.CLASS_NAME, ClassName.place_kakao)  # 페이지 내 모든 음식점 리스트 반환
        address = self.getElements(driver, 1, By.CLASS_NAME, ClassName.addr_kakao)  # 페이지 내 모든 음식점 주소 반환
        for i in range(len(name)):
            try:
                if name[i].text not in nameList:
                    nameList.append((name[i].text.replace('%', '%20'), " ".join(address[i].text.split()[:4])))
                    # print((name[i].text, " ".join(address[i].text.split()[:4])))  # 디버깅위해 출력
            except Exception as textError:
                print(textError)

        return nameList

    # 지하철 목록에서 모든 음식점이름 반환
    def getNamelist(self, sub_list):
        all_list = []
        for sub in sub_list:
            # print(sub) # 디버깅 위해 출력
            self.getSuburl(self.driver, sub)
            for _ in range(7):
                for no in range(1, 6):
                    all_list += self.getPageList(self.driver, no)
                self.click(self.driver, 5, By.XPATH, XPath.nextPage)  # 다음페이지 클릭
        return list(set(all_list))

    # div num 확인하기
    def countDivNum(self, driver: webdriver):
        divNum = 1
        if self.getElements(driver, 5, By.CLASS_NAME, ClassName.zeroClass):
            divNum += 1
        if self.getElements(driver, 5, By.CLASS_NAME, ClassName.announcementClass):
            divNum += 1
        return divNum

    # 영업 시간 더보기 버튼 클릭
    def clickTimeMoreButton(self, driver: webdriver, divNum: int, index: int):
        self.click(driver, 5, By.CLASS_NAME, ClassName.timeMoreButtonClass, 1)
        # if not self.click(driver, 5, By.XPATH, XPath.timeMoreButton.format(divNum=divNum, idx=index)):
        #     if not self.click(driver, 5, By.XPATH, XPath.timeMoreButton1.format(divNum=divNum, idx=index)):
        #         if not self.click(driver, 5, By.XPATH, XPath.timeMoreButton2.format(divNum=divNum, idx=index)):
        #             self.click(driver, 5, By.XPATH, XPath.timeMoreButton3.format(divNum=divNum, idx=index))

    # 메뉴 정보 받아오기
    def getMenuInfo(self, driver):
        while self.getElements(driver, 5, By.XPATH, XPath.menuMoreButton):
            if not self.click(driver, 5, By.XPATH, XPath.menuMoreButton):
                break

        if self.getElements(driver, 5, By.CLASS_NAME, ClassName.deliveryClass):
            menuList = self.getElements(driver, 5, By.CLASS_NAME, ClassName.deliveryMenuNameClass)
            menuPrice = self.getElements(driver, 5, By.CLASS_NAME, ClassName.deliveryMenuPriceClass)
        elif self.getElements(driver, 5, By.CLASS_NAME, ClassName.takeOutMenuNameClass):
            menuList = self.getElements(driver, 5, By.CLASS_NAME, ClassName.takeOutMenuNameClass)
            menuPrice = self.getElements(driver, 5, By.CLASS_NAME, ClassName.deliveryMenuPriceClass)
        elif self.getElements(driver, 5, By.CLASS_NAME, ClassName.menuListClass):
            menuList = self.getElements(driver, 5, By.CLASS_NAME, ClassName.menuListClass)
            menuPrice = self.getElements(driver, 5, By.CLASS_NAME, ClassName.menuPriceClass)
        else:
            return [], []
        return menuList, menuPrice

    # 리뷰 탭 클릭하기
    def clickTab(self, driver: webdriver, name: str):
        tabElements = self.getElements(driver, 5, By.CLASS_NAME, ClassName.reviewTabClass)

        for i, j in enumerate(tabElements):
            if j.text == name:
                if not self.click(driver, 2, By.XPATH, XPath.menuTabPath.format(index=i + 1)):
                    if not self.click(driver, 2, By.XPATH, XPath.menuTab1Path.format(index=i + 1)):
                        if not self.click(driver, 2, By.XPATH, XPath.menuTab2Path.format(index=i + 1)):
                            if not self.click(driver, 2, By.XPATH, XPath.menuTab3Path.format(index=i + 1)):
                                return False
                return True
        return False

    # 리뷰 최신 순으로 정렬하기 버튼
    def clickRecent(self, driver: webdriver):
        listButton = self.getElements(driver, 5, By.CLASS_NAME, ClassName.recentClass1)

        if listButton:
            for i in listButton:
                if i.text == '최신순':
                    self.click(i, 5, By.CLASS_NAME, ClassName.recentClass2)

    # 리뷰 내용 Tokenizing
    def makeTokenizing(self, content: str):
        try:
            content = re.sub('[^A-Za-z0-9가-힣]', ' ', content)
            content = " ".join(content.split())
        except:
            return ""

        return content

    # url 정보에서 user hash value 가져오기
    def getHashValue(self, driver: webdriver, timeout: int, kind: By, value1: str, value2: str) -> dict:
        userInfo = dict()
        try:
            # url-> hash value 추출
            element1 = self.getElements(driver, timeout, kind, value1)
            if element1:
                element1 = element1[0]
                userInfo['userHash'] = element1.get_attribute('href').split('/')[-2]
            element2 = self.getElements(element1, timeout, kind, value2)
            # 포함된 user의 정보 가져오기
            if element2:
                for i in element2:
                    info = i.text.split(' ')
                    # 한글 영어 매칭
                    if info[0] == '리뷰' and info[1].isdigit():
                        userInfo['reviewNum'] = int(info[1])  # ex. userInfo['리뷰'] = 1244
                    elif info[0] == '사진' and info[1].isdigit():
                        userInfo['photo'] = int(info[1])
                    elif info[0] == '팔로잉' and info[1].isdigit():
                        userInfo['following'] = int(info[1])
                    elif info[0] == '팔로워' and info[1].isdigit():
                        userInfo['follower'] = int(info[1])

        except Exception as noUserInfo:
            print(noUserInfo)

        return userInfo

    def getReviewSubInfo(self, driver: webdriver, timeout: int, kind: By, value1: str, value2: str) -> dict:
        reviewInfo = dict()

        try:
            element1 = self.getElements(driver, timeout, kind, value1)[0]
            element2 = self.getElements(element1, timeout, kind, value2)

            if element2:
                for i in element2:
                    if '방문일' in i.text:
                        reviewInfo['reviewInfoVisitDay'] = i.text.split('\n')[1]
                    if '번째' in i.text:
                        num = i.text.split('\n')[0].strip('번째 방문')
                        if num.isdigit():
                            reviewInfo['reviewInfoVisitCount'] = int(num)
                        else:
                            reviewInfo['reviewInfoVisitCount'] = -1
                    if '별점' in i.text:
                        reviewInfo['reviewInfoScore'] = i.text.split('\n')[1]
        except Exception as noreviewInfo:
            print(noreviewInfo)


        return reviewInfo

    def getReviewInfo(self, driver: webdriver, placeName: str, address: str, prevNum: int):
        # print(placeName) # 디버깅 위한 출력
        # 최신순 버튼 클릭
        self.clickRecent(driver)
        finish = False
        while True:
            # 현재 페이지 리뷰 element들 가져오기
            self.scrollDown(driver)
            reviewElements = self.getElements(driver, 10, By.CLASS_NAME, ClassName.reviewClass)
            if reviewElements:
                # 각 리뷰에서 정보 가져오기
                for i in range(prevNum, len(reviewElements)):
                    pl = Payload()
                    reviewData = pl.reviewInfo
                    # userData = pl.userInfo
                    self.click(reviewElements[i], 5, By.CLASS_NAME, ClassName.reviewMoreContentButtonClass)

                    # 리뷰 유저의 ID -> str
                    reviewUserId = self.getValue(reviewElements[i], 5, By.CLASS_NAME, ClassName.reviewUserId)
                    if not reviewUserId:
                        continue

                    # 리뷰 유저에 대한 정보 -> dict
                    reviewUserHash = self.getHashValue(reviewElements[i], 1, By.CLASS_NAME, ClassName.reviewUserHash1,ClassName.reviewUserHash2)
                    # 리뷰 내용 -> str
                    reviewContent = self.getValue(reviewElements[i], 1, By.CLASS_NAME, ClassName.reviewContent)
                    # review 별점, 방문날짜, 방문 횟수 - dict
                    reviewInfo = self.getReviewSubInfo(reviewElements[i], 1, By.CLASS_NAME, ClassName.reviewInfo1, ClassName.reviewInfo2)

                    # 올해 리뷰가 아니면 break
                    if reviewInfo:
                        if len(reviewInfo['reviewInfoVisitDay'].split('.')) != 3:
                            finish = True
                            break

                    if 'userHash' not in reviewUserHash.keys():
                        continue

                    # 중복 상관없이 유저 정보 저장
                    # userData['userID'] = reviewUserId
                    # userData.update(reviewUserHash)

                    reviewData['userHash'] = reviewUserHash['userHash']
                    reviewData['reviewUserID'] = reviewUserId
                    reviewData['placeName'] = placeName
                    reviewData['placeAddress'] = address
                    reviewData['reviewContent'] = self.makeTokenizing(reviewContent)
                    reviewData.update(reviewInfo)

                    # print("user: ", userData)
                    print("review: ", reviewData)
                    # print(reviewData) # 디버깅을 위한 출력
                    result = sendData(self.host, "ReviewInfoModel", reviewData, self.errorLogger)
                    if not result:
                        self.errorLogger.logger.error(placeName)
                    # result = sendData(self.host, "UserInfoModel", userData, self.errorLogger)
                    # if not result:
                    #     self.errorLogger.logger.error(placeName)

            prevNum = len(reviewElements)
            if finish or not self.click(driver, 2, By.CLASS_NAME, ClassName.reviewMoreButtonClass):
                break

    def loadPlacePage(self, driver: webdriver) -> bool:
        # switch to the search iframe
        self.switchToFrame(driver, 5, By.XPATH, XPath.searchIframe)

        # click the first fetched item
        self.click(driver, 5, By.XPATH, XPath.firstFetched)

        # switch to the entery iframe
        driver.switch_to.parent_frame()
        if not self.switchToFrame(driver, 5, By.XPATH, XPath.entryIframe):
            return False
        return True

    def getPlaceInfoDetails(self, geoLocal: Nominatim, name: str) -> bool:
        pl = Payload()
        data = pl.placeInfo

        # search the place
        self.driver.get(URL.baseURL.format(placeName=name))

        if not self.loadPlacePage(self.driver):
            print("No place : ", name)
            return None

        self.click(self.driver, 5, By.XPATH, XPath.homePath)
        # get place name, place type
        data['placeName'] = self.getElements(self.driver, 5, By.XPATH, XPath.placeName)[0].text
        data['placeType'] = self.getElements(self.driver, 5, By.XPATH, XPath.placeType)[0].text

        # get place mean rating
        num = 1
        placeMeanRating = self.getValue(self.driver, 5, By.XPATH, XPath.placeMeanRating)
        if placeMeanRating:
            data['placeMeanRating'] = float(placeMeanRating)
            num += 1

        # get number of reviews
        visitReviewNum = self.getValue(self.driver, 5, By.XPATH, XPath.reviewNum.format(num=num))
        if visitReviewNum and visitReviewNum.replace(',', '').isdigit():
            data['visitReviewNum'] = int(visitReviewNum.replace(',', ''))
            num += 1
        blogReviewNum = self.getValue(self.driver, 5, By.XPATH, XPath.reviewNum.format(num=num))
        if blogReviewNum and blogReviewNum.replace(',', '').isdigit():
            data['blogReviewNum'] = int(blogReviewNum.replace(',', ''))

        # get telephone
        data['telephone'] = self.getValue(self.driver, 5, By.CLASS_NAME, ClassName.telephoneClass)

        # get address
        placeAddress = self.getValue(self.driver, 5, By.CLASS_NAME, ClassName.placeAddressClass)
        if placeAddress:
            data['placeAddress'] = placeAddress
            latitude, longitude = self.geocoding(geoLocal, placeAddress)
            data['latitude'], data['longitude'] = latitude, longitude

        divNum = self.countDivNum(self.driver)

        informationList = self.getElements(self.driver, 5, By.CSS_SELECTOR, Selector.informationSelector.format(num=6))
        for index, information in enumerate(informationList, start=1):
            infoText = information.text.split('\n')
            if infoText[0] == '영업시간':
                # more buttom click
                self.clickTimeMoreButton(self.driver, divNum, index)

                dayList = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.dayClass)
                timeList = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.timeClass)
                if not dayList or not timeList:
                    continue
                for idx in range(len(dayList)):
                    data['time'][dayList[idx].text] = timeList[1:][idx].text

            elif infoText[0] == '설명':
                self.click(self.driver, 5, By.CLASS_NAME, ClassName.descriptionMoreButtonClass, -1)
                # if not self.click(self.driver, 5, By.XPATH, XPath.descriptionMoreButton.format(divNum=divNum, idx=index)):
                #     self.click(self.driver, 5, By.XPATH, XPath.descriptionMoreButton2.format(divNum=divNum, idx=index))
                description = self.getElements(self.driver, 5, By.XPATH,
                                          XPath.description.format(divNum1=5, divNum2=divNum, idx=index))
                if not description:
                    description = self.getElements(self.driver, 5, By.XPATH,
                                              XPath.description.format(divNum1=6, divNum2=divNum, idx=index))
                if description:
                    data['description'] = ' '.join(description[-1].text.split('내용 더보기')[0].split('\n'))

        self.scrollDown(self.driver)
        # get theme keyword
        if self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.themeKeywordClass):
            themeData = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.themeDataClass)
            for value in themeData:
                value = value.text.split(', ')[-1]
                if value:
                    data['themeKeywords'].append(value)

        # get popularity
        tabList = self.getElements(self.driver, 5, By.XPATH, XPath.placeTab)
        if tabList:
            tabList = tabList[0].text.replace('\n', ' ').split(' ')
            if '메뉴' in tabList: divNum += 2
            else: divNum += 1

        dataLabButtons = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.dataLabMoreButtonClass)
        for idx, button in enumerate(dataLabButtons):
            if button.text == '더보기':
                self.click(self.driver, 5, By.CLASS_NAME, ClassName.dataLabMoreButtonClass, idx)

        self.click(self.driver, 5, By.XPATH, XPath.datalabMoreButton.format(divNum=divNum))
        if self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.popularityClass):
            for idx in range(10, 70, 10):
                popularityValue = self.getValue(self.driver, 5, By.XPATH, XPath.agePopluarity.format(age=idx // 10))
                if popularityValue:
                    popularityValue = popularityValue.split('.')[0]
                if popularityValue.isdigit():
                    data['agePopularity'][f'{idx}대'] = int(popularityValue)
            genderData = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.donutGraphClass)
            if genderData:
                genderData = genderData[0]
                genderPopularity = genderData.text.split('\n')
                femaleValue = genderPopularity[0].split('%')[0]
                maleValue = genderPopularity[1].split('%')[0]
                if femaleValue.isdigit() and maleValue.isdigit():
                    data['genderPopularity']['F'] = int(femaleValue)
                    data['genderPopularity']['M'] = int(maleValue)

        if self.clickTab(self.driver, '메뉴'):
            menuList, menuPrice = self.getMenuInfo(self.driver)
            print(len(menuList), len(menuPrice))
            if menuList :
                for menu_idx in range(min(len(menuPrice), len(menuList))):
                    data['menu'][menuList[menu_idx].text] = menuPrice[menu_idx].text
            # else:
            #     menuErrorLogger.error(name)

        self.driver.refresh()
        self.loadPlacePage(self.driver)
        if self.clickTab(self.driver, '리뷰'):  # get Like
            while self.click(self.driver, 5, By.CLASS_NAME, ClassName.likeMoreClass):
                if self.getValue(self.driver, 5, By.CLASS_NAME, ClassName.likeMoreClass) != "더보기": break

            time.sleep(0.5)
            likeNum = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.likeNumClass)
            if likeNum:
                likeNum = likeNum[1:]
                likeTopic = self.getElements(self.driver, 5, By.CLASS_NAME, ClassName.likeTopicClass)
                for idx in range(len(likeNum)):
                    try:
                        data['like'][likeTopic[idx].text.split("\"")[1]] = int(likeNum[idx].text.split('\n')[-1])
                    except:
                        pass

        result = sendData(self.host, "PlaceInfoModel", data, self.errorLogger)
        print("place : ", data)
        if not result:
            self.errorLogger.logger.error(name)
        self.getReviewInfo(self.driver, data['placeName'], data['placeAddress'], len(data['like']))

        self.driver.switch_to.parent_frame()
        return True
