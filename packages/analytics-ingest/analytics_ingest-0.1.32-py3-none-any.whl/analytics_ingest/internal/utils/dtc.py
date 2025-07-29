from datetime import datetime

from analytics_ingest.internal.schemas.dtc_schema import DTCSchema
from analytics_ingest.internal.schemas.inputs.dtc_input import make_dtc_input
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import get_cached_message_id
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from analytics_ingest.internal.utils.serialization import serialize_payload


def create_dtc(
    executor: GraphQLExecutor,
    config_id: str,
    variables_list: list[dict],
    batch_size: int,
):
    all_messages_with_dtcs = {}

    for variables in variables_list:
        file_id = variables.get("fileId", "")
        message_date = variables.get("messageDate", "")
        message = MessageSchema.from_variables(variables)
        message_key = message.cache_key()
        message_id = get_cached_message_id(message_key)

        if not message_id:
            raise RuntimeError(f"No message ID found for key: {message_key}")

        dtc_items = DTCSchema.from_variables(variables)
        batches = Batcher.create_batches(dtc_items, batch_size)

        for batch in batches:
            if message_id not in all_messages_with_dtcs:
                all_messages_with_dtcs[message_id] = {
                    "fileId": file_id,
                    "messageId": message_id,
                    "messageDate": message_date,
                    "dtcs": [],
                }
            all_messages_with_dtcs[message_id]["dtcs"].extend(
                [item.model_dump() for item in batch]
            )

    sorted_dtcs_data = [
        {
            "configurationId": config_id,
            "fileId": str(msg["fileId"]),
            "messageId": msg["messageId"],
            "messageDate": msg["messageDate"],
            "data": msg["dtcs"],
        }
        for msg in sorted(
            all_messages_with_dtcs.values(),
            key=lambda x: datetime.fromisoformat(x["messageDate"]),
        )
    ]

    payload = serialize_payload(make_dtc_input(sorted_dtcs_data))
    executor.execute(GraphQLMutations.upsert_dtc_mutation(), payload)


def build_batched_dtc_inputs(
    config_id, variables, message_id, fileId, messageDate, batch_size
):
    dtc_items = DTCSchema.from_variables(variables)
    batches = Batcher.create_batches(dtc_items, batch_size)
    return [
        make_dtc_input(config_id, batch, message_id, fileId, messageDate)
        for batch in batches
    ]
