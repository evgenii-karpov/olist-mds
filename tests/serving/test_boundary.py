from scripts.serving.boundary import ServingBoundaryPlanner


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
