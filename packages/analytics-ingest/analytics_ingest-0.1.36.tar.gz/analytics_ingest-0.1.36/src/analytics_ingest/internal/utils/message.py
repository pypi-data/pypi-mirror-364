from analytics_ingest.internal.schemas.inputs.message_input import (
    make_create_message_input,
)
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations

_message_cache = {}


def get_cached_message_id(key: str) -> str | None:
    print("Create Key:", key)
    return _message_cache.get(key)


def create_message(executor: GraphQLExecutor, variables: list[dict]) -> list[str]:
    message_ids = []
    uncached_messages = []
    comparison_keys = []

    for var in variables:
        key = generate_message_cache_key(var)

        if key in _message_cache:
            message_ids.append(_message_cache[key])
        else:
            input_dict = {
                "arbId": var.get("arbId"),
                "name": var.get("name"),
                "networkName": var.get("networkName"),
                "ecuName": var.get("ecuName"),
                "ecuId": var.get("ecuId"),
                "requestCode": var.get("requestCode"),
                "fileId": var.get("fileId"),
                "messageDate": var.get("messageDate"),
            }
            comparison_keys.append(key)
            uncached_messages.append(input_dict)

    if uncached_messages:
        response = executor.execute(
            GraphQLMutations.create_message(),
            make_create_message_input(uncached_messages),
        )
        if "errors" in response:
            error_message = f"Error in create_message response: {response['errors']}"
            raise RuntimeError("Error in create_message_response: %s", error_message)

        messages = response["data"].get("createMessage", [])
        if not messages:
            raise RuntimeError("No messages created")

        for idx, input_dict in enumerate(uncached_messages):
            key = comparison_keys[idx]
            matching = next(
                (
                    m
                    for m in messages
                    if all(
                        m.get(k) == input_dict.get(k)
                        for k in input_dict.keys()
                        if k != "requestCode"  # requestCode not returned
                    )
                ),
                None,
            )
            if matching:
                _message_cache[key] = str(matching["id"])
                message_ids.append(str(matching["id"]))

    return message_ids


def generate_message_cache_key(data: dict) -> str:
    """Consistent key used for message caching and lookup."""
    return f"{data.get('arbId')}|{data.get('name')}|{data.get('networkName')}|{data.get('ecuName')}|{data.get('ecuId')}|{data.get('fileId')}|{data.get('messageDate')}"
