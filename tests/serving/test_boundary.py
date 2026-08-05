from scripts.serving.boundary import (
    ServingBoundaryPlanner,
    collapse_transaction_history,
    transaction_boundary_state,
)


def test_transaction_history_collapses_split_begin_end_and_duplicate_end():
    rows = collapse_transaction_history(
        [
            {
                "transaction_id": "tx-1",
                "status": "OPEN",
                "begin_kafka_offset": 10,
                "end_kafka_offset": None,
                "recorded_at": "2026-08-04T00:00:01Z",
            },
            {
                "transaction_id": "tx-1",
                "status": "COMPLETE",
                "begin_kafka_offset": 10,
                "end_kafka_offset": 11,
                "recorded_at": "2026-08-04T00:00:02Z",
            },
            {
                "transaction_id": "tx-1",
                "status": "COMPLETE",
                "begin_kafka_offset": 10,
                "end_kafka_offset": 11,
                "recorded_at": "2026-08-04T00:00:03Z",
            },
        ]
    )

    assert len(rows) == 1
    assert rows[0]["status"] == "COMPLETE"
    assert rows[0]["end_kafka_offset"] == 11


def test_unresolved_open_transaction_is_visible_to_planner():
    rows = [
        {
            "transaction_id": "tx-open",
            "status": "OPEN",
            "begin_kafka_offset": 20,
            "end_kafka_offset": None,
            "event_count": None,
            "recorded_at": "2026-08-04T00:00:01Z",
        }
    ]

    assert transaction_boundary_state(rows) == "READY"
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=rows,
        iceberg_snapshots={},
    )
    assert plan.status == "WAITING"
    assert plan.status_reason == "OPEN_TRANSACTION"


def test_rejected_observation_can_become_complete():
    rows = collapse_transaction_history(
        [
            {
                "transaction_id": "tx-retry",
                "status": "REJECTED",
                "begin_kafka_offset": 30,
                "end_kafka_offset": None,
                "recorded_at": "2026-08-04T00:00:01Z",
            },
            {
                "transaction_id": "tx-retry",
                "status": "COMPLETE",
                "begin_kafka_offset": 30,
                "end_kafka_offset": 31,
                "event_count": 1,
                "recorded_at": "2026-08-04T00:00:02Z",
            },
        ]
    )

    assert transaction_boundary_state(rows) == "READY"
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=rows,
        iceberg_snapshots={},
    )
    assert plan.status == "MATERIALIZING"
    assert plan.target_transaction_id == "tx-retry"


def test_unknown_transaction_state_fails_closed():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=[
            {
                "transaction_id": "tx-invalid",
                "status": "UNKNOWN",
                "begin_kafka_offset": 40,
                "end_kafka_offset": None,
            }
        ],
        iceberg_snapshots={},
    )

    assert plan.status == "BLOCKED"
    assert plan.status_reason == "INVARIANT_FAILURE"


def test_boundary_planner_not_caught_up():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={},
        transaction_rows=[],
        iceberg_snapshots={},
        coverage_state="NOT_CAUGHT_UP",
    )
    assert plan.is_noop is True
    assert plan.status == "WAITING"
    assert plan.status_reason == "SOURCE_NOT_CAUGHT_UP"


def test_boundary_planner_rejected_boundary():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={},
        transaction_rows=[],
        iceberg_snapshots={},
        boundary_state="REJECTED",
    )
    assert plan.is_noop is True
    assert plan.status == "BLOCKED"
    assert plan.status_reason == "REJECTED_TRANSACTION"


def test_boundary_planner_complete_transactions():
    txs = [
        {
            "transaction_id": "tx_1",
            "status": "COMPLETE",
            "end_kafka_offset": 100,
            "event_count": 5,
        },
        {
            "transaction_id": "tx_2",
            "status": "COMPLETE",
            "end_kafka_offset": 200,
            "event_count": 3,
        },
    ]
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=txs,
        iceberg_snapshots={"customers": 10},
    )
    assert plan.is_noop is False
    assert plan.status == "MATERIALIZING"
    assert plan.target_transaction_id == "tx_2"
    assert plan.target_transaction_end_offset == 200
    assert plan.expected_event_count == 8


def test_boundary_planner_initial_snapshot_without_transaction_boundary():
    metrics = {
        entity: {
            "event_count": count,
            "target_offsets": {
                f"olist_cdc.olist_oltp.{entity}:0": count - 1,
            },
        }
        for entity, count in {
            "customers": 8,
            "orders": 12,
            "order_items": 16,
            "order_payments": 14,
            "order_reviews": 12,
            "products": 8,
            "sellers": 4,
            "product_category_translation": 5,
        }.items()
    }
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": False},
        transaction_rows=[],
        iceberg_snapshots={
            entity: 10
            for entity in (
                "customers",
                "orders",
                "order_items",
                "order_payments",
                "order_reviews",
                "products",
                "sellers",
                "product_category_translation",
            )
        },
        entity_metrics=metrics,
    )

    assert plan.status == "MATERIALIZING"
    assert plan.is_noop is False
    assert plan.target_transaction_id is None
    assert plan.target_transaction_end_offset is None
    assert plan.source_snapshot_completed is True
    assert plan.expected_event_count == 79
    assert plan.expected_entity_counts == {
        entity: metrics[entity]["event_count"] for entity in metrics
    }


def test_boundary_planner_ignores_empty_complete_transactions():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=[
            {
                "transaction_id": "tx_business",
                "status": "COMPLETE",
                "end_kafka_offset": 100,
                "event_count": 5,
            },
            {
                "transaction_id": "tx_empty_heartbeat",
                "status": "COMPLETE",
                "end_kafka_offset": 200,
                "event_count": 0,
            },
        ],
        iceberg_snapshots={"customers": 10},
    )
    assert plan.is_noop is False
    assert plan.target_transaction_id == "tx_business"
    assert plan.target_transaction_end_offset == 100
    assert plan.expected_event_count == 5


def test_boundary_planner_empty_complete_transactions_are_noop():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={
            "source_snapshot_completed": True,
            "last_published_transaction_id": "tx_business",
            "last_published_transaction_end_offset": 100,
        },
        transaction_rows=[
            {
                "transaction_id": "tx_empty_heartbeat",
                "status": "COMPLETE",
                "end_kafka_offset": 200,
                "event_count": 0,
            }
        ],
        iceberg_snapshots={"customers": 10},
    )
    assert plan.is_noop is True
    assert plan.status == "NOOP"


def test_boundary_planner_blocks_incomplete_complete_row():
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=[
            {
                "transaction_id": None,
                "status": "COMPLETE",
                "end_kafka_offset": 100,
                "event_count": 1,
            }
        ],
        iceberg_snapshots={},
    )
    assert plan.is_noop is True
    assert plan.status == "BLOCKED"
    assert plan.status_reason == "INVARIANT_FAILURE"


def test_boundary_planner_requires_all_entity_offsets_for_materialization():
    metrics = {
        "customers": {
            "event_count": 1,
            "target_offsets": {"olist_cdc.olist_oltp.customers:0": 2},
        },
    }
    plan = ServingBoundaryPlanner.plan_next_sync_run(
        sync_run_seq=1,
        runtime_state={"source_snapshot_completed": True},
        transaction_rows=[
            {
                "transaction_id": "tx_1",
                "status": "COMPLETE",
                "end_kafka_offset": 100,
                "event_count": 1,
            }
        ],
        iceberg_snapshots={},
        entity_metrics=metrics,
    )
    assert plan.is_noop is True
    assert plan.status == "BLOCKED"
    assert plan.status_reason == "INVARIANT_FAILURE"
