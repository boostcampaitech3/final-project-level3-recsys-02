import nats
from nats.errors import TimeoutError
import pickle


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
        self.client = None
        self.jetstream = None
        self.subscriber = None

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
            self.client = await nats.connect(self.host)
            self.jetstream = self.client.jetstream()
            self.logger.formatter('Successfully connected to the Nats server.')
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on connecting to the Nats server.'))

    async def createStream(self, stream: str, subjects: list):
        """
        스트림 이름과 subjects 들을 생성합니다.

        :param stream: a stream name to which subject belongs
        :param subjects: a list of subjects on which messages persist
        :return:
        """
        try:
            response = await self.jetstream.add_stream(name=stream, subjects=subjects)
            self.logger.formatter(response)
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on connecting to the server'))

    async def subscribe(self, durable: str, stream: str, subject: str):
        """
        subscribe() 이후 pull() 가능합니다.

        :param durable: a consumer identifier with which the Nats server identifies the queue
        :param stream: a stream name to which the subject belongs
        :param subject: a subject to subscribe to
        :return:
        """
        try:
            self.subscriber = await self.jetstream.pull_subscribe(subject, durable, stream)
            self.logger.formatter(await self.subscriber.consumer_info())
        except TimeoutError:
            raise Exception(self.logger.formatter('Timed out on a subscription.'))

    async def publish(
            self,
            subject: str,
            data,
            timeout: float,
            stream: str,
            headers: dict,
    ) -> bool:
        """
        브로커에 데이터를 publish 하는 함수
        Payload agnostic => 데이터 타입 상관 없이 파이썬 오브젝트를 캐싱합니다.

        :param subject: a subject to publish to
        :param payload: data bytes
        :param timeout: timeout
        :param stream: a stream name to which the subject belongs
        :param headers: a json header for additional information
        :return: True if the publishing succeeded | False if timed out on publishing
        """
        try:
            payload = pickle.dumps(data)
            ack = await self.jetstream.publish(subject, payload, timeout, stream, headers)
            return True
        except TimeoutError:
            return False

    async def pull(self, batchSize: int, timeout: float = 60.0) -> list:
        """
        캐싱된 Payload 를 배치 사이즈만큼 가져옵니다.

        :param batchSize: determines the size of a list to pull
        :param timeout: timeout
        :return: a list of user request to be inferred
        """
        try:
            pulled = await self.subscriber.fetch(batchSize, timeout)
            batch = []
            for message in pulled:
                batch.append(pickle.loads(message.data))
                message.ack()
            return batch
        except TimeoutError:
            message = 'The broker client has not received any message in the last {timeout} seconds.'.format(
                timeout=timeout
            )
            self.logger.formatter(message)
