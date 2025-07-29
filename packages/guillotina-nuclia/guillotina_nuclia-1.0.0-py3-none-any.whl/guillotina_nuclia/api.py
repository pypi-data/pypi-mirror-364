from guillotina import configure
from guillotina.api.service import Service
from guillotina.component import query_utility
from guillotina.interfaces import IContainer
from guillotina_nuclia.interfaces.chat import IChat
from guillotina_nuclia.utility import INucliaUtility


@configure.service(
    context=IChat,
    method="POST",
    permission="nuclia.Predict",
    name="@NucliaPredict",
    summary="Get a response",
    responses={"200": {"description": "Get a response", "schema": {"properties": {}}}},
    requestBody={
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Question",
                            "required": True,
                        },
                    }
                }
            }
        },
    },
)
class PredictChat(Service):
    async def __call__(self):
        nuclia_utility = query_utility(INucliaUtility)
        payload = await self.request.json()
        return await nuclia_utility.predict_chat(
            question=payload["question"], chat=self.context
        )


@configure.service(
    context=IContainer,
    method="GET",
    permission="nuclia.Ask",
    name="@NucliaAsk",
    summary="Get a response",
    responses={"200": {"description": "Get a response", "schema": {"properties": {}}}},
)
class Ask(Service):
    async def __call__(self):
        nuclia_utility = query_utility(INucliaUtility)
        question = self.request.query.get("question")
        return await nuclia_utility.ask(question=question)


@configure.service(
    context=IContainer,
    method="GET",
    permission="nuclia.Search",
    name="@NucliaSearch",
    summary="Get a response",
    responses={"200": {"description": "Get a response", "schema": {"properties": {}}}},
)
class Search(Service):
    async def __call__(self):
        nuclia_utility = query_utility(INucliaUtility)
        question = self.request.query.get("question")
        return await nuclia_utility.search(question=question)


@configure.service(
    context=IContainer,
    method="GET",
    permission="nuclia.Find",
    name="@NucliaFind",
    summary="Get a response",
    responses={"200": {"description": "Get a response", "schema": {"properties": {}}}},
)
class Find(Service):
    async def __call__(self):
        nuclia_utility = query_utility(INucliaUtility)
        question = self.request.query.get("question")
        return await nuclia_utility.find(question=question)
