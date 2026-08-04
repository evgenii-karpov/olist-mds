from unittest.mock import MagicMock, patch

from scripts.serving.control import ServingControlRepository


def _repository_with_table_results(*results: tuple[int, ...] | None):
    cursor = MagicMock()
    cursor.fetchone.side_effect = results
    context = MagicMock()
    context.__enter__.return_value = cursor
    return cursor, context


def test_schema_assertions_verify_only_target_serving_tables():
    cursor, context = _repository_with_table_results(
        (1,),
        (1,),
        (1,),
        (1,),
    )

    with patch("scripts.serving.control.control_db_cursor", return_value=context):
        result = ServingControlRepository.verify_schema_assertions()

    assert result["status"] == "PASS"
    assert result["verified_tables"] == [
        "serving.sync_runs",
        "serving.sync_entity_results",
        "serving.runtime_state",
    ]
    assert all("cdc_audit" not in str(call) for call in cursor.execute.call_args_list)
    assert result["target_migrations"] == [
        "005_create_serving_control_tables.sql",
        "999_grant_control_role.sql",
    ]


def test_schema_assertions_fail_when_a_target_table_is_missing():
    _, context = _repository_with_table_results(None, (1,), (1,), (1,))

    with patch("scripts.serving.control.control_db_cursor", return_value=context):
        result = ServingControlRepository.verify_schema_assertions()

    assert result["status"] == "FAIL"
