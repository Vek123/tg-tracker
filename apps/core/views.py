from aiogram.utils.text_decorations import MarkdownDecoration

from apps.core.schemas import Observer


class View:
    observer: Observer

    async def handle(self):
        raise NotImplementedError()

    def quote(self, *text: str, sep: str = " ") -> str:
        return MarkdownDecoration().quote(sep.join(map(str, text)))
