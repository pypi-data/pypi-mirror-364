from guillotina.async_util import IAsyncUtility
from guillotina.event import notify
from guillotina.events import ObjectModifiedEvent
from guillotina.utils import get_authenticated_user_id
from guillotina_nuclia.interfaces.chat import IChat
from nuclia import sdk
from nuclia.lib.nua_responses import ChatModel

import logging


logger = logging.getLogger("nuclia_utility")


class INucliaUtility(IAsyncUtility):
    pass


class NucliaUtility:
    def __init__(self, settings=None, loop=None):
        self._settings = settings
        self.loop = loop
        self._nuclia_auth = sdk.AsyncNucliaAuth()
        self._predict = sdk.AsyncNucliaPredict()
        self._upload = sdk.AsyncNucliaUpload()
        self._search = sdk.AsyncNucliaSearch()

    async def initialize(self, app):
        try:
            await self.auth()
        except Exception:
            logger.error("Error auth", exc_info=True)

    async def auth(self):
        client_id = await self._nuclia_auth.nua(token=self._settings["nua_key"])
        self._nuclia_auth._config.set_default_nua(client_id)

    async def upload(self, file_path: str):
        await self._upload.file(path=file_path)

    async def predict_chat(self, question: str, chat: IChat):
        try:
            user = get_authenticated_user_id()
        except Exception:
            user = "UNKNOWN"
        generative_model = self._settings.get("generative_model", "chatgpt4o")
        max_tokens = self._settings.get("max_tokens", 4096)

        chat_model = ChatModel(
            question=question,
            query_context=chat.context or [],
            chat_history=chat.history or [],
            user_id=user,
            generative_model=generative_model,
            max_tokens=max_tokens,
        )
        response = await self._predict.generate(text=chat_model)
        user_message = {"author": "USER", "text": question}
        nuclia_message = {"author": "NUCLIA", "text": response.answer}
        chat.history.append(user_message)
        chat.history.append(nuclia_message)
        chat.responses.append(response.answer)
        chat.register()
        await notify(
            ObjectModifiedEvent(
                chat, payload={"history": chat.history, "responses": chat.responses}
            )
        )
        return response

    async def ask(self, question: str):
        response = await self._search.ask(query=question)
        return response.answer.decode("utf-8")

    async def search(self, question: str, filters: list = []):
        response = await self._search.search(query=question, filters=filters)
        return response.fulltext.results

    async def find(self, question: str, filters: list = []):
        response = await self._search.find(query=question, filters=filters)
        return response.resources
