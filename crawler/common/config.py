class Subway:
    sub_list = ['까치산', '시청', '을지로입구', '을지로3가', '을지로4가', '동대문역사문화공원', '신당', '상왕십리', '왕십리', '한양대', '뚝섬', '성수', '건대입구',
                '구의', '강변', '잠실나루', '잠실', '잠실새내', '종합운동장', '삼성', '선릉', '역삼', '강남', '교대', '서초', '방배', '사당', '낙성대',  '서울대입구',
                '봉천', '신림', '신대방', '구로디지털단지', '대림', '신도림', '문래', '영등포구청', '당산', '합정', '홍대입구', '신촌', '이대', '아현', '충정로',
                '용답', '신답', '신설동', '도림천', '양천구청', '신정네거리', '용두',
                '강남', '양재', '양재시민의숲', '청계산입구', '판교', '정자', '미금', '동천', '수지구청', '성복', '상현', '광교중앙', '광교']


class URL:
    baseURL = 'https://map.naver.com/v5/search/{placeName}/place'
    # kakao
    basePath = 'https://map.kakao.com/'


class Selector:
    # get place info
    informationSelector = '#app-root > div > div > div > div:nth-child({num}) > div > div.place_section.no_margin._18vYz > div > ul > li'


class XPath:
    ## kakao map
    searchPathKakao = '//*[@id="search.keyword.query"]' # search
    sheild = '//*[@id="dimmedLayer"]' # item_shield
    more = '//*[@id="info.search.place.more"]' # more
    pageNo = '//*[@id="info.search.page.no{}"]' # page_no
    nextPage =  '//*[@id="info.search.page.next"]' # nextpage

    # naver map
    searchIframe = '//*[@id="searchIframe"]'
    entryIframe = '//*[@id="entryIframe"]'
    firstFetched = '//*[@id="_pcmap_list_scroll_container"]/ul/li[1]/div[1]/a[1]'

    # place info
    menuTabPath = '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a[{index}]/span'
    menuTab1Path = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/a[{index}]'
    menuTab2Path = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/div/div[2]/div/div/a[{index}]/span'
    menuTab3Path = '//*[@id="root"]/div[2]/div/header/div[2]/div/a[{index}]/span'
    menuMoreButton = '//*[@id="app-root"]/div/div/div/div[6]/div/div[1]/div[2]/a'

    placeMeanRating = '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[1]/em'
    serviceHour = '//*[@id="app-root"]/div/div/div/div[5]/div/div[1]/div/ul/li[4]/div/a'
    summary = '//*[@id="app-root"]/div/div/div/div[5]/div/div[1]/div/ul/li[4]/div/a'
    agePopluarity = '//*[@id="bar_chart_container"]/ul/li[{age}]/div[1]/span/span[1]'
    femalePopularity = '//*[@id="_datalab_chart_donut1_0"]/svg/g[1]/g[3]/g[4]/g[2]/text[2]/text()'
    malePopularity = '//*[@id="_datalab_chart_donut1_0"]/svg/g[1]/g[3]/g[4]/g[2]/text[1]'
    telephone = '//*[@id="app-root"]/div/div/div/div[5]/div/div[1]/div/ul/li[1]/div/span[1]'
    likeMorePath = '/html/body/div[3]/div/div/div/div[5]/div[3]/div[1]/div/div/div[2]/a'

    reviewPath = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/a[3]/span'
    timePath = '//*[@id="app-root"]/div/div/div/div[5]/div/div[1]/div/ul/li[4]/div/a/div/div/span'

    placeName = '//*[@id="_title"]/span[1]'
    placeType = '//*[@id="_title"]/span[2]'

    timeMoreButton = '//*[@id="app-root"]/div/div/div/div[6]/div/div[{divNum}]/div/ul/li[{idx}]/div/div/a/span[2]'

    timeMoreButton1 = '//*[@id="app-root"]/div/div/div/div[5]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/div/div/span'
    timeMoreButton2 = '//*[@id="app-root"]/div/div/div/div[6]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/div[1]/div/span'
    timeMoreButton3= '//*[@id="app-root"]/div/div/div/div[6]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/div[1]/div/div/div/span[2]'
    descriptionMoreButton = '//*[@id="app-root"]/div/div/div/div[5]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/span[2]'
    descriptionMoreButton2 = '//*[@id="app-root"]/div/div/div/div[6]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/span[2]'

    description = '//*[@id="app-root"]/div/div/div/div[{divNum1}]/div/div[{divNum2}]/div/ul/li[{idx}]/div/a/span[1]'
    infoText = '//*[@id="app-root"]/div/div/div/div[5]/div/div[{divNum}]/div/ul/li[{idx}]/div/a/span[1]'
    datalabMoreButton = '//*[@id="app-root"]/div/div/div/div[7]/div/div[{divNum}]/div[2]/a'
    reviewNum = '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[{num}]/a/em'
    placeTab = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div'
    homePath = '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a[1]/span'

    # get review
    reviewTab = '//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div/a[{index}]/span'
    reviewCount = '//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[3]/h2/span[1]'


class ClassName:

    # kakao
    place_kakao = 'link_name' # place
    addr_kakao = 'addr' #address

    # get place info
    menuClass = '_2kAri'
    menuListClass = '_3yfZ1'
    menuPriceClass = '_3qFuX'

    themeKeywordClass = 'Z6Prg'
    themeTopicClass = '_3hvd9'
    themeDataClass = '_2irYJ'
    descriptionClass = 'M_704'
    popularityClass = '_3QHlQ'

    placeMeanRatingClass = '_2XLwD'
    telephoneClass = '_3ZA0S'
    placeAddressClass = '_2yqUQ'
    likeTopicClass = '_1lntw'
    likeNumClass = 'Nqp-s'
    likeMoreClass = '_22igH'

    dayClass = '_1v6gO'
    timeClass = '_3uEtO'
    timeMoreButtonClass = '_1aKLL'

    descriptionMoreButtonClass = '_3_09q'
    zeroClass = '_13OJC'
    announcementClass = '_3puAz'

    deliveryClass = '_3eMEwPl5IJ'
    deliveryMenuNameClass = 'name'
    deliveryMenuPriceClass = 'price'

    takeoutClass = 'desc_type ico_takeout'
    takeOutMenuNameClass = 'tit'

    femaleClass = 'c3-chart-arc c3-target c3-target-female'

    donutGraphClass = 'c3-chart'

    # get review
    reviewTabClass = '_3aXen'
    reviewCountClass = 'place_section_count'
    reviewMoreButtonClass = '_3iTUo'
    reviewClass = '_3FaRE'
    reviewMoreContentButtonClass = 'M_704' # '_3Dnsh'
    reviewMorePointButtonClass = '_1fvo3 _22igH'

    reviewUserId = '_16RxQ'
    reviewUserHash1 = '_2r43z'
    reviewUserHash2 = '_1fvo3'
    reviewContent = 'WoYOw'
    reviewPoint1 = '_3oMpH'
    reviewPoint2 = '_1fvo3'
    reviewInfo1 = '_3-LAD'
    reviewInfo2 = '_1fvo3'
    recentClass1 = '_2OZXM'
    recentClass2 = '_3WQBd'

    dataLabMoreButtonClass = '_3iTUo'

