import nats
from nats.errors import TimeoutError
from nats.js.errors import NotFoundError
import pickle


class Broker:
    def __init__(self, host: str):
        """
        Nats client 클래스입니다.

        :param host: a kubernetes service IP:port string
        """
        self.host = host
        self.client = None
        self.jetstream = None
        self.subscriber = None

    async def connect(self, durable: str, stream: str, subject: str) -> tuple:
        """
        Nats Jetstream 파이썬 API 가 현재 비동기 클라이언트만 지원하므로 비동기 호출해야 합니다.

        :param durable: a consumer identifier with which the Nats server identifies the queue
        :param stream: a stream name to which the subject belongs
        :param subject: a subject to subscribe to
        :return: a tuple of object ( True if the connection succeeded | False if the connection timed out &&
        message )
        """
        try:
            self.client = await nats.connect(self.host)
            self.jetstream = self.client.jetstream()
            await self.jetstream.add_stream(name=stream, subjects=[subject])
            self.subscriber = await self.jetstream.pull_subscribe(subject, durable, stream)
            return True, await self.subscriber.consumer_info()
        except TimeoutError:
            return False, 'timed out on a connection'

    async def publish(
            self,
            subject: str,
            data,
            timeout: float,
            stream: str,
            headers: dict,
    ) -> tuple:
        """
        메시지브로커에 데이터를 publish 하는 함수; Payload agnostic
        데이터 타입 상관 없이 파이썬 객체면 됩니다.

        :param subject: a subject to publish to
        :param payload: data bytes
        :param timeout: timeout
        :param stream: a stream name to which the subject belongs
        :param headers: a json header for additional information
        :return: a tuple of object ( True if the publishing succeeded | False if the publishing timed out &&
        message )
        """
        try:
            payload = pickle.dumps(data)
            return True, await self.jetstream.publish(subject, payload, timeout, stream, headers)
        except TimeoutError:
            return False, 'timed out on publishing a message'

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
            pass
