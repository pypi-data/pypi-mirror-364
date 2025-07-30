from agi_med_common.models import ChatItem


class TextProcessorAPI:
    def process(self, text: str, chat: ChatItem | None = None, request_id: str = "") -> str:
        raise NotImplementedError
