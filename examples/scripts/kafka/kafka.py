from collections import UserDict
import functools
from typing import Any, TypedDict

from confluent_kafka import (
    ConsumerGroupTopicPartitions,
    KafkaError,
    KafkaException,
    TopicCollection,
    TopicPartition,
)
from confluent_kafka.admin import AdminClient, ConfigResource, OffsetSpec
from script_runner import read, get_function_context

KAFKA_TIMEOUT = 5


class KafkaCluster(TypedDict):
    name: str
    brokers: list[str]


class KafkaConfig(TypedDict):
    clusters: list[KafkaCluster]


class HashableConfig(UserDict[str, str]):
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.items())))


@functools.lru_cache(maxsize=10)
def _get_cached_client(broker_config: HashableConfig) -> AdminClient:
    return AdminClient(broker_config)


def get_admin_client(config: KafkaConfig, cluster: str) -> AdminClient:
    broker_config = get_config(config, cluster)
    return _get_cached_client(HashableConfig(broker_config))


def get_config(config: KafkaConfig, cluster: str) -> dict[str, str]:
    cluster_spec = next((c for c in config["clusters"] if c["name"] == cluster), None)

    if cluster_spec is None:
        raise ValueError("Cluster not found")

    return {"bootstrap.servers": ",".join(cluster_spec["brokers"])}


@read
def list_clusters() -> list[Any]:
    config: KafkaConfig = get_function_context().group_config
    return [c for c in config["clusters"]]


@read
def describe_cluster(cluster: str) -> list[dict[str, Any]]:
    """
    Returns the list of nodes in a cluster.
    """
    config: KafkaConfig = get_function_context().group_config

    client = get_admin_client(config, cluster)
    res = client.describe_cluster().result(KAFKA_TIMEOUT)

    controller = res.controller

    return [
        {
            "id": node.id_string,
            "host": node.host,
            "port": node.port,
            "rack": node.rack,
            "isController": node.id == controller.id,
        }
        for node in res.nodes
    ]


@read
def describe_broker_configs(cluster: str) -> list[dict[str, Any]]:
    """
    Returns configuration for all brokers in a cluster.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)
    broker_resources = [
        ConfigResource(ConfigResource.Type.BROKER, f"{id}")
        for id in client.list_topics().brokers
    ]

    all_configs = []

    for broker_resource in broker_resources:
        configs = {
            k: v.result(KAFKA_TIMEOUT)
            for (k, v) in client.describe_configs([broker_resource]).items()
        }[broker_resource]
        for k, v in configs.items():
            config_item = {
                "config": k,
                "value": v.value,
                "isDefault": v.is_default,
                "isReadOnly": v.is_read_only,
                "broker": broker_resource.name,
            }
            all_configs.append(config_item)

    return all_configs


@read
def list_topics(cluster: str) -> list[dict[str, Any]]:
    """
    Returns the list of topics in a cluster.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)

    topics = client.list_topics().topics

    return [
        {"name": t, "partitions": len(meta.partitions)} for (t, meta) in topics.items()
    ]


@read
def list_offsets(cluster: str, topic: str) -> list[dict[str, Any]]:
    """
    Returns the earliest and latest stored offsets for every partition of a topic.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)

    topics = client.describe_topics(TopicCollection([topic]))
    topic_partitions = [
        TopicPartition(topic, p.id)
        for p in topics[topic].result(KAFKA_TIMEOUT).partitions
    ]

    earliest_offsets = client.list_offsets(
        {tp: OffsetSpec.earliest() for tp in topic_partitions}
    )
    latest_offsets = client.list_offsets(
        {tp: OffsetSpec.latest() for tp in topic_partitions}
    )

    return [
        {
            "topic": tp.topic,
            "partition": tp.partition,
            "earliest_offset": earliest_offsets[tp].result(KAFKA_TIMEOUT).offset,
            "latest_offset": latest_offsets[tp].result(KAFKA_TIMEOUT).offset,
        }
        for tp in topic_partitions
    ]


@read
def describe_topic_partitions(
    cluster: str,
    topic: str,
) -> list[dict[str, Any]]:
    """
    Returns the id, leader, replica assignments, and insync replicas
    for each partition of a topic.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)

    topics = client.describe_topics(TopicCollection([topic]))

    try:
        result = topics[topic].result(timeout=KAFKA_TIMEOUT)
    except KafkaException as e:
        if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            raise ValueError(f"Topic {topic} not found")
        else:
            raise

    return [
        {
            "topic": result.name,
            "id": p.id,
            "leader": p.leader.id,
            "replicas": [r.id for r in p.replicas],
            "isr": [r.id for r in p.isr],
        }
        for p in result.partitions
    ]


@read
def list_consumer_groups(cluster: str) -> list[dict[str, Any]]:
    """
    List the consumer groups of the specified cluster.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)
    consumer_groups = client.list_consumer_groups().result(KAFKA_TIMEOUT).valid

    return [
        {
            "group_id": cg.group_id,
            "state": cg.state.name,
            "type": cg.type.name,
        }
        for cg in consumer_groups
    ]


@read
def list_consumer_group_offsets(
    cluster: str, consumer_group: str
) -> list[dict[str, Any]]:
    """
    Returns the offsets for each topic partition of a consumer group.
    """
    config: KafkaConfig = get_function_context().group_config
    client = get_admin_client(config, cluster)
    offsets = client.list_consumer_group_offsets(
        [ConsumerGroupTopicPartitions(consumer_group)]
    )

    group_offsets = offsets[consumer_group].result(KAFKA_TIMEOUT)

    return [
        {
            "topic": tp.topic,
            "partition": tp.partition,
            "offset": tp.offset,
        }
        for tp in group_offsets.topic_partitions
    ]
