import datetime
from typing import TYPE_CHECKING

from aiobotocore.session import AioSession, get_session

from fastapi_cache.types import Backend

if TYPE_CHECKING:
    from types_aiobotocore_dynamodb import DynamoDBClient


class DynamoBackend(Backend):
    """
    Amazon DynamoDB backend provider

    This backend requires an existing table within your AWS environment to be passed during
    backend init. If ttl is going to be used, this needs to be manually enabled on the table
    using the `ttl` key. Dynamo will take care of deleting outdated objects, but this is not
    instant so don't be alarmed when they linger around for a bit.

    As with all AWS clients, credentials will be taken from the environment. Check the AWS SDK
    for more information.

    Usage:
        >> dynamodb = DynamoBackend(table_name="your-cache", region="eu-west-1")
        >> await dynamodb.init()
        >> FastAPICache.init(dynamodb)
    """

    session: AioSession
    table_name: str
    region: str | None

    def __init__(self, table_name: str, region: str | None = None) -> None:
        self.session: AioSession = get_session()
        self.table_name = table_name
        self.region = region
        self._client: DynamoDBClient | None = None

    @property
    def client(self) -> "DynamoDBClient":
        if not self._client:
            raise Exception("Backend not initiated!")
        return self._client

    async def init(self) -> None:
        self._client = await self.session.create_client(  # pyright: ignore[reportUnknownMemberType]
            "dynamodb",
            region_name=self.region,
        ).__aenter__()

    async def close(self) -> None:
        await self.client.__aexit__(None, None, None)
        self._client = None

    async def get_with_ttl(self, key: str) -> tuple[int, bytes | None]:
        response = await self.client.get_item(TableName=self.table_name, Key={"key": {"S": key}})

        if "Item" in response:
            value = response["Item"].get("value", {}).get("B")
            ttl = response["Item"].get("ttl", {}).get("N")

            if not ttl:
                return -1, value

            # It's only eventually consistent so we need to check ourselves
            expire = int(ttl) - int(datetime.datetime.now().timestamp())
            if expire > 0:
                return expire, value

        return 0, None

    async def get(self, key: str) -> bytes | None:
        response = await self.client.get_item(TableName=self.table_name, Key={"key": {"S": key}})
        if "Item" in response:
            return response["Item"].get("value", {}).get("B")
        return None

    async def set(self, key: str, value: bytes, expire: int | None = None) -> None:
        ttl = (
            {"ttl": {"N": str(int((datetime.datetime.now() + datetime.timedelta(seconds=expire)).timestamp()))}}
            if expire
            else {}
        )

        await self.client.put_item(
            TableName=self.table_name,
            Item={
                "key": {"S": key},
                "value": {"B": value},
                **ttl,
            },
        )

    async def clear(self, namespace: str | None = None, key: str | None = None) -> int:
        raise NotImplementedError
