from logging import Logger
from confluent_kafka import Consumer, Message
from eo4eu_base_utils.typing import Callable

from ..settings import Settings


class KafkaConsumer:
    """Wrapper around confluent_kafka.Consumer

    :param topics: The kafka topic(s) to listen to
    :type topics: list[str]|str
    :param config: The kafka config to pass to the underlying confluent_kafka.Consumer. For reference, see https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-configuration
    :type config: dict
    :param handler: A function to pass the UTF-8 decoded value of each message to
    :type handler: Callable[[str],None]|None
    :param logger: Optional Python logger to use for logs
    :type logger: logging.Logger|None
    :param timeout: The poll interval to use when consuming messages
    :type timeout: float
    :param exit_after: If set, the consumer will stop polling after consuming N messages
    :type exit_after: int|None
    :param callback: A function that runs every time a message is received. It takes two parameters: The raw confluent_kafka.Message, and the UTF-8 decoded value of the message
    :type callback: Callable[[confluent_kafka.Message,str],None]|None
    """

    def __init__(
        self,
        topics: list[str]|str,
        config: dict,
        handler: Callable[[str],None]|None = None,
        logger: Logger|None = None,
        timeout: float = 1.0,
        exit_after: int|None = None,
        callback: Callable[[Message,str],None]|None = None
    ):
        if not isinstance(topics, list):
            topics = [topics]
        if logger is None:
            logger = Settings.LOGGER
        if callback is None:
            callback = lambda msg, dec_msg: logger.info(
                f"[Topic {msg.topic()}] Message received: {dec_msg}"
            )

        self._consumer = Consumer(config)
        self._topics = topics
        self._handler = handler
        self._logger = logger
        self._timeout = timeout
        self._exit_after = exit_after
        self._callback = callback

    def _consume_one(self, handler: Callable[[str],None]) -> bool:
        try:
            msg = self._consumer.poll(timeout = self._timeout)
            if msg is None or msg.error():
                return False

            decoded_msg = msg.value().decode("utf-8")
            self._callback(msg, decoded_msg)
            handler(decoded_msg)
            return True
        except Exception as e:
            self._logger.warning(f"Unhandled error: {e}")

        return False

    def _consume_unbounded(self, handler: Callable[[str],None]):
        while True:
            self._consume_one(handler)

    def _consume_bounded(self, handler: Callable[[str],None]):
        messages_received = 0
        while messages_received < self._exit_after:
            if self._consume_one(handler):
                messages_received += 1

    def consume(self, handler: Callable[[str],None]|None = None):
        """Continuously poll for new messages, either indefinitely 
        or exiting after N messages, depending on whether `exit_after` 
        is None or not

        :param handler: A function to pass the UTF-8 decoded value of each message to. If not given, the KafkaConsumer's default handler will be used
        :type handler: Callable[[str],None]|None
        """
        if handler is None:
            handler = self._handler

        try:
            self._consumer.subscribe(self._topics)

            if self._exit_after is None:
                self._consume_unbounded(handler)
            else:
                self._consume_bounded(handler)
        finally:
            self._consumer.close()
