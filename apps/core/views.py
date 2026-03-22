from apps.core.schemas import Observer


class View:
    observer: Observer

    async def handle(self):
        raise NotImplementedError()
