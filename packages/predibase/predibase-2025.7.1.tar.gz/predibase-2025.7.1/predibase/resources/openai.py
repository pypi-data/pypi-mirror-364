from typing import Dict, List, Optional, TYPE_CHECKING, Union

from openai import OpenAI

from predibase.pql.api import Session

if TYPE_CHECKING:
    from predibase.resources.deployment import Deployment


def openai_compatible_endpoint(session: Session, deployment_ref: Union[str, "Deployment"]) -> str:
    # Check not isinstance(deployment_ref, str) instead of
    #  isinstance(deployment_ref, Deployment) to avoid import error.
    if not isinstance(deployment_ref, str):
        deployment_ref = deployment_ref.name

    return f"https://{session.serving_http_endpoint}/{session.tenant}/deployments/v2/llms/" f"{deployment_ref}/v1"


def create_openai_client(url, session: Session):
    return


def build_extra_body(**kwargs):
    extra_body = {}
    for key, value in kwargs.items():
        if value is not None:
            extra_body[key] = value
    return extra_body


class OpenAIBase:
    def __init__(self, client):
        self._pb_client = client
        self._client = None
        self.model = None

    def init_client(self, model: str):
        if self.model != model:
            deployment = self._pb_client.deployments.get(model)
            openai_url = openai_compatible_endpoint(self._pb_client._session, deployment)
            self._client = OpenAI(api_key=self._pb_client._session.token, base_url=openai_url)
            self.model = model


class OpenAIChatCompletion(OpenAIBase):
    def __init__(self, client: OpenAI):
        super().__init__(client)

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        adapter_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        hugging_face_api_key: Optional[str] = None,
    ):
        self.init_client(model)
        extra_body = build_extra_body(api_token=hugging_face_api_key)

        return self._client.chat.completions.create(
            model=adapter_id or "",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body=extra_body,
        )


class OpenAICompletion(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(
        self,
        model: str,
        prompt: str,
        adapter_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        hugging_face_api_key: Optional[str] = None,
    ):
        self.init_client(model)
        extra_body = build_extra_body(api_token=hugging_face_api_key)

        return self._client.completions.create(
            model=adapter_id or "",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body=extra_body,
        )


class OpenAIEmbeddings(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(
        self,
        model: str,
        input: str,
        adapter_id: Optional[str] = None,
        hugging_face_api_key: Optional[str] = None,
    ):
        self.init_client(model)
        extra_body = build_extra_body(api_token=hugging_face_api_key)

        return self._client.embeddings.create(
            model=adapter_id or "",
            input=input,
            extra_body=extra_body,
        )


class OpenAIChat:
    def __init__(self, client):
        self.completion = OpenAIChatCompletion(client)
