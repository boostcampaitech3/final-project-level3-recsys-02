# 위치 기반 개인화 장소 추천

## 시연 영상
<div align="center">

|Popularity Recommend|Content-based Recommend|Collaborative Filtering Recommend|
|<img src="https://user-images.githubusercontent.com/33798183/172856840-12d7b434-44bf-4579-8ae9-b3cb4d5eb8ea.gif">|<img src="https://user-images.githubusercontent.com/33798183/172857765-cbee7468-5cb2-4d74-9aea-56fd6cb76384.gif">|<img src="https://user-images.githubusercontent.com/33798183/172857805-af7ba33d-6783-4b4a-b066-142ff3726d5d.gif">|
|------|---|---|
  
</div>

## 발표 영상


## 프로젝트 계기 및 소개
1. ”아 오늘 뭐 먹지”란 고민없이 버튼만 누르면 바로바로 추천할 수 없을까?
2. 회원가입없이도 그때 그때 내 취향을 반영한 추천할 수 없을까?

&rarr; 검색 없이 **클릭**만으로 사용자의 기호를 반영하고 그 기호를 토대로 **현재 위치의 주변 맛집을 추천하는 서비스**입니다.

## 모델 설명
### a. 데이터 수집
#### 1) 어디서 수집해야할까?
- 카카오 지도에서 ‘ㅇㅇ역 맛집’ 리스트 크롤링
- 네이버 지도에서 장소의 세부적인 내용 및 리뷰 데이터 크롤링

#### 2) 범위는 얼만큼?
- 가장 사람들의 활동이 활발하고 장소가 많은 서울 지하철 2호선, 신분당선으로 범위를 한정

#### 3) 데이터는 어디에 저장?
- MongoDB에 수집하기 위하여 크롤링한 후 데이터를 하나의 서버로 전달하는 코드 작성
- 중복되는 데이터를 방지하기 위하여 주요 column에는 unique index 처리


### b. 모델
#### 1) 모델 선정 과정
* 기존 개인화 추천을 위한 모델들은 대부분 유저에 대해 Transductive함
  - 유저에 대한 정의 및, 이해(User Embedding)가 필요
  - Incremental Learning을 통해 지속적인 유저 유입을 처리가 가능한 서비스를 만들자
  - 충분하지 못한 데이터, 유저에 대한 정보를 얻기가 어려움, 서비스 구축 시간 한계 등의 한계점 존재
  - 현실적으로 Transductive Model 운영이 어려움

* 유저에 대한 정의 없이 Interaction만으로 개인화 추천을 하자
  - 오직 Session에 기반해 유저가 남긴 음식점에 대한 선호도만을 가지고 개인화 추천이 가능할 것 같다
  - 그런데 유저와 음식점 간 Interaction 데이터가 적으면(Sparse Ratio가 높아)  기존 모델들은 낮은 성능을 보임
  - 그럼 음식점에 대해 미리 정의해두고 유입된 유저의 선호도를 받아 비슷한 음식점들을 추천할 수 있는 모델을 만들자
  - **Metapath2Vec**으로 음식점 Embedding을 구하자

#### 2) Metapath2vec이란?
- 노드 타입이 여러 개인 그래프 구조를 학습하기 위한 skip-gram 모델
<div align="center"><img src="https://user-images.githubusercontent.com/33798183/172850031-e5283db0-fe69-4012-bf2d-65910b968bc6.png" width=700></div>


#### 3) Cold Start 문제 해결을 위해 Hybrid Recommendation System 구축
<div align="center"><img src="https://user-images.githubusercontent.com/33798183/172846679-1299d304-9ad0-4b77-b5d0-21b82adab65e.png" width=700></div>

- 유저에 대한 정보가 아예 없이는 개인화 추천 불가능한(cold-start) 문제가 존재
- 유저 첫 유입시 (Session 생성시) 인기도 기반 추천을 통해 유저의 선호도 파악
- 적은 수의 Interaction만으로는 완벽한 개인화 추천에는 어려움이 있어 초기 (일정 수 이하의 Interaction을 가진 유저의 경우)에는 Content-based Recommendation 진행)
- 이후 Hybrid Recommendation System, CB와 CF의 결과를 합쳐서 추천


### c. 모델 성능
#### 1) 장소를 잘 이해했는가?
<div align="center">
  
|TSNE 시각화|Jaccard Similarity|
|------|---|
|<img src="https://user-images.githubusercontent.com/33798183/172851107-a1947331-da07-4212-b396-83edb706f1e0.png" width=300>|<img src="https://user-images.githubusercontent.com/33798183/172851104-d0343f06-8fc0-4096-8fcc-ced70273c7c8.png" width=300>|

</div>

- 임베딩된 장소를 TSNE시각화
- 유저에게 추천해준 장소와 유저가 선호하는 장소가 얼마나 비슷한지 판단하기 위해 Jaccard Similarity 계산

#### 2) 잘 이해한 장소들을 바탕으로 추천을 잘 하고 있는가?

<div align="center">

|nDCG@10|
|------|
|<img src="https://user-images.githubusercontent.com/33798183/172851657-ac644c7e-fbbe-4113-9454-6c7123e13f2a.png" width=300>|

 </div>
- 랭킹 기반 추천에 주로 사용이 되는 nDCG로 측정

## 프로젝트 구조 설명

### a. 서비스 흐름도
<div align="center"><img src="https://user-images.githubusercontent.com/33798183/172838218-d8ab343b-c43e-4eb5-8883-f08edf2032e5.png" width=600>

유저가 장소 추천을 요청하면 웹 서버를 통해 메시지 브로커에 요청을 publish 하고 {유저 엔드포인트 해시값 : 요청 결과} 형태의 해시테이블을 생성합니다.  
이후 웹 서버는 timeout(5초)까지 연결을 끊지 않고 0.5초마다 해시테이블에 결과값을 요청해서  
결과가 존재하면 클라이언트에게 반환하고 그렇지 않다면 예외를 반환합니다(=Long Polling).

<img src="https://user-images.githubusercontent.com/33798183/172838228-c2acf443-f5a5-4c9f-a29d-06cfc712ba0d.png" width=600>

인퍼런스 서버에서 일정 주기(0.2초)마다 메시지 브로커로부터 유저 요청을 배치 처리합니다.  
요청 결과를 메시지 브로커에 생성된 해시 테이블에 저장합니다. 

  
<img src="https://user-images.githubusercontent.com/33798183/172838230-0518368c-60fe-4b91-84a8-32eeb737ecac.png" width=600> 

웹 서버에서 클라이언트에 결과를 반환하면서 커넥션을 종료합니다. 
</div>

### b. Framework 선택과 이유
열거된 장점과 단점은 개발도중 다른 프레임워크와의 비교를 통해 느낀 상대적인 부분이며 개인적인 의견임을 말씀드립니다.

#### 1) Web Application Server - FastAPI

* 장점
  - Native Async Support : Python built-in 비동기 런타임이 아닌 uvloop 위에서 동작하므로 성능상의 이점을 가지며 Flask 와 다르게 비동기 처리를 위해서 Celery 와 같은 task-queue 를 따로 쓸 필요가 없어서 편리.
  - 잘 된 문서화, 쉽고 편리한 API 제공.
  - 풍부한 Starlette 써드-파티 파이썬 패키지. Rate-limiting 은 slowapi 가 구현하고 Server-Sent Event 는 sse-starlette 이 제공.
  - Built-in 데이터 유효성 검사 (빠른 타이핑).

* 단점
  - 개발 당시 HTTP/2 지원의 부재.
  - Flask 와 고민했으나 배우기 더 쉽고 비동기 지원이 너무 잘 되어서 선택했음.

#### 2) Message Queue - NATS
* 장점
  - Message Persistence Layer 의 이중화 지원 (RAM, Disk or Both)
  - Built-in key-value store 를 지원해서 dictionary server 로 활용 가능했음. 덕분에 웹 서버와 인퍼런스 서버를 publisher/subscriber 로 분리시키고 나서도 Redis 서버 배포 없이 Long - Polling 방식으로 request-reply 패턴 구현이 가능했음.
  - Active Community : Pull-based consumer 를 구현할 때 fetch 함수가 모든 메시지가 도착하기 전에 block 하는 문제가 있었는데 개발 도중 해결될 정도로 활성화된 커뮤니티 보유.
  - Raft Consensus Algorithm : 매우 쉬운 HA 구성.
  - 컨테이너 크기 약 17mb

* 단점
  - Golang 으로 작성된 비교적 최신 프레임워크라 Python API 가 비동기 API 만 지원하고 타 언어 API 에 비해 coverage 가 떨어짐.
  - Kafka 와 Nats 둘 다 사용해본 결과 기능은 크게 다르지 않았고 Nats 가 사용이 훨씬 편했음. Kafka streams api 를 사용할 필요가 없었고 오히려 zookeeper 를 statefulset 으로 추가적으로 배포해줘야 하는 것과 달리 Nats 의 HA 구성이 비교도 안 되게 쉬워서 선택하게 됨.

#### 3) 애플리케이션 관리 및 배포 - Kubernetes
* 장점
  - yaml 파일 작성만 익숙해지면 선언적 API 를 통해 구현할 수 있는 모든 기능들을 편하게 부담없이 구현할 수 있음.

* 단점
  - 필요를 느끼고 배워야지만 제대로 활용할 수 있음. 그 전엔 오히려 사용이 부담스럽고 학습 커브가 생각만큼 얕지 않아서 고생함.

#### 4) Service Mesh - Istio
* 장점
  - 기존엔 웹서버 배포시 Nginx 를 리버스 프록시 서버로 배포하고 upstream 설정을 해줘야 했음. 그리고 추가로 Kubernetes Ingress 설정을 별도로 해줘야 했는데 이렇게 복잡하게 할 필요 없이 Istio 를 설치하고 Istio-Ingressgateway, gateway 그리고 virtualservice yaml 파일만 작성하면 Ingress 설정이 끝나서 배포 난이도를 확 낮춰줬음.
  - 오픈소스 모니터링 툴들 (e.g. Grafana) 과 잘 조합됨.
  - 쿠버네티스만 사용했을 때 구현할 수 없었던 다양한 방식의 트래픽 관리 (e.g. Canary Releases, Client-Based Routing) 를 쉽게 가능하게 함.

#### 5) MongoDB
* 장점
  - Python API 로 지원하는 거의 모든 기능들을 사용 가능.
  - RDB를 쓸 수 없는 환경에서 최고의 선택지 제공.
  - 자체 GUI 클라이언트 (Compass) 의 활용도가 매우 높고 사용이 편리함.
  
* 단점
  - 적어도 현재 진행하는 규모의 프로젝트에선 못 느꼈음.


### c. 아쉬운 점 
* 시간이 부족해서 프로토타이핑 이후에 웹 서버를 actix 로 바꾸고 로드테스트까지 마친 후 서빙하고 싶었는데 못 하게 되어서 매우 아쉬움.
* 사용자 데이터를 모아서 db에 저장하고 활용하고 개인화된 추천 서비스 제공에 활용하고 싶었지만 시간이 부족했음.
* 자동 학습을 구현할 수 있었고 로드맵까지 있었지만 시간 부족으로 폐기됨.
* 로그 서버의 부재

### d. 개선할 점
* 사용자 explicit data (좋아요 클릭) 저장하고 추천 시 활용할 수 있게 데이터베이스 애플리케이션 구성 필요.
* 사용자 로그와 시스템 로그도 메시지 큐를 통해서 따로 저장하는 애플리케이션 필요.
