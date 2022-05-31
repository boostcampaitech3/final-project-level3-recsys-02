import json
import nats
from nats.errors import TimeoutError
from nats.js.errors import BadRequestError
from nats.js.errors import NotFoundError
from nats.js.errors import KeyDeletedError


class Broker:
    def __init__(self, host: str, logger):
        """
        Nats client 클래스입니다.
        createStream() 과 subscribe() 에서 인자로 전달되는 stream 은 논리적으로 분리된 공간이고
        subject 가 메시지 큐라고 생각하시면 됩니다.

        :param host: a kubernetes service IP:port string
        """
        self.logger = logger
        self.host = host
        self.__client = None
        self.__jetstream = None
        self.__subscriber = None
        self.__bucket = None

    async def connect(self):
        """
        Jetstream 파이썬 API 가 비동기 클라이언트만 지원하므로 비동기 접속
        __init__() 에서 호출 불가능합니다.
        FastAPI 가 uvloop 을 레버리징하므로 파이썬 asyncio event loop 에서 호출하지 마시고
        아래 예시와 같이 호출해주세요.
        
        # 예시
        @app.on_event('startup')
        async def init():
            await broker.connect()

        :return:
        """
        try:
            self.__client = await nats.connect(self.host)
            self.__jetstream = self.__client.jetstream()
            self.logger.formatter('Successfully connected to the Nats server.')
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on connecting to the Nats server.'))

    async def createStream(self, stream: str, subjects: list):
        """
        stream 이름과 subjects 들을 생성합니다.

        :param stream: a stream name to which subject belongs
        :param subjects: a list of subjects on which messages persist
        :return:
        """
        try:
            response = await self.__jetstream.add_stream(name=stream, subjects=subjects)
            self.logger.formatter(response)
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on creating a stream'))
        except BadRequestError:
            raise Exception(self.logger.formatter('Stream name already exists.'))

    async def removeStream(self, stream: str):
        """
        stream 을 삭제합니다.

        :param stream:
        :return:
        """
        try:
            response = await self.__jetstream.delete_stream(stream)
            self.logger.formatter(response)
        except TimeoutError:
            raise Exception(self.logger.formattter('Timed out on removing a stream'))

    async def subscribe(self, durable: str, stream: str, subject: str):
        """
        subscribe() 이후 pull() 가능합니다.

        :param durable: a consumer identifier with which the Nats server identifies the queue
        :param stream: a stream name to which the subject belongs
        :param subject: a subject to subscribe to
        :return:
        """
        try:
            self.__subscriber = await self.__jetstream.pull_subscribe(subject, durable, stream)
            self.logger.formatter(await self.__subscriber.consumer_info())
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on a subscription.'))

    async def publish(
            self,
            subject: str,
            payload: bytes,
            timeout: float,
            stream: str,
            headers: dict,
    ) -> bool:
        """
        client hashing 을 통해 나온 key 값을 key-value 스토어에 생성하고 Nats server 에 데이터를 publish 합니다.
        Payload agnostic => 데이터 타입에 상관 없이 publish

        :param subject: a subject to publish to
        :param payload: data bytes
        :param timeout: timeout
        :param stream: a stream name to which the subject belongs
        :param headers: a json header for additional information
        :return: True if the publishing succeeded | False if timed out on publishing
        """
        try:
            await self.createKey(key=headers.get('key'), value=b'')
            await self.__jetstream.publish(subject, payload, timeout, stream, headers)
            return True
        except TimeoutError:
            return False

    async def pull(self, batchSize: int, timeout: float = 0.5) -> list:
        """
        캐싱된 Payload 를 배치 사이즈만큼 가져옵니다.

        :param batchSize: determines the size of a list to pull
        :param timeout: timeout
        :return: a list of user request to be inferred
        """
        try:
            pulled = await self.__subscriber.fetch(batchSize, timeout)
            batch = []
            for message in pulled:
                data = json.loads(message.data)
                batch.append((message.headers, data))
                await message.ack()
            return batch
        except TimeoutError:
            pass

    async def createBucket(self, name: str):
        """
        Bucket 생성합니다.

        :param name: a bucket name to be created
        :return:
        """
        try:
            self.__bucket = await self.__jetstream.create_key_value(bucket=name)
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on creating a bucket.'))

    async def fetchResult(self, key: str) -> object:
        """
        key 에서 값 가져오기

        :param key:
        :return:
        """
        try:
            result = await self.__bucket.get(key=key)
            return result.value
        except NotFoundError:
            return None
        except KeyDeletedError:
            return None

    async def createKey(self, key: str, value: bytes):
        """
        Bucket 에 key 생성하고 value 추가
        :param key:
        :param value: bytes
        :return: 
        """
        try:
            return await self.__bucket.put(key=key, value=value)
        except:
            self.logger.formatter('Timed out on creating and assigning a key-value item.')
            return None

    async def removeKey(self, key: str):
        """
        Bucket 에서 key 삭제
        :param key:
        :return:
        """
        try:
            await self.__bucket.delete(key)
        except:
            self.logger.formatter('Timed out on removing a key-value item.')
