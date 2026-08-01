import pytest
from scripts.serving.entities import ALL_SERVING_ENTITIES, get_entity_spec


def test_entity_registry_count():
    assert len(ALL_SERVING_ENTITIES) == 8


def test_get_entity_spec():
    customers = get_entity_spec("customers")
    assert customers.entity == "customers"
    assert customers.primary_key == ("customer_id",)
    assert customers.ch_events_table == "serving_cdc.customers_events"


def test_unknown_entity():
    with pytest.raises(KeyError):
        get_entity_spec("non_existent")
