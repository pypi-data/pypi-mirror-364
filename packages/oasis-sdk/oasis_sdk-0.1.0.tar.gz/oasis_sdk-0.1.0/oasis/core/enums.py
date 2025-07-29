from enum import StrEnum


class Provider(StrEnum):
    OPENAI = "openai"
    AZURE = "aoai"


class ClientType(StrEnum):
    SDK = "sdk"
    LANGCHAIN = "langchain"