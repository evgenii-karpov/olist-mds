SET NAMES utf8mb4 COLLATE utf8mb4_0900_bin;
SET time_zone = '+00:00';

CREATE TABLE IF NOT EXISTS olist_simulator.simulation_runs (
    run_id VARCHAR(64) NOT NULL,
    command VARCHAR(16) NOT NULL,
    random_seed BIGINT NOT NULL,
    target_rate DECIMAL(12, 4) NOT NULL,
    configuration JSON NOT NULL,
    state VARCHAR(24) NOT NULL,
    started_at DATETIME(6) NOT NULL,
    heartbeat_at DATETIME(6) NOT NULL,
    last_committed_source_timestamp DATETIME(6) NULL,
    stop_requested_at DATETIME(6) NULL,
    finished_at DATETIME(6) NULL,
    counters JSON NOT NULL DEFAULT (JSON_OBJECT()),
    error_message TEXT NULL,
    CONSTRAINT pk_simulation_runs PRIMARY KEY (run_id),
    CONSTRAINT ck_simulation_runs_command CHECK (
        command IN ('seed', 'run', 'replay')
    ),
    CONSTRAINT ck_simulation_runs_rate CHECK (target_rate >= 0),
    CONSTRAINT ck_simulation_runs_state CHECK (
        state IN (
            'starting', 'running', 'stop_requested',
            'stopped', 'completed', 'failed'
        )
    ),
    INDEX idx_simulation_runs_state (state, heartbeat_at)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.generated_ids (
    run_id VARCHAR(64) NOT NULL,
    entity_type VARCHAR(32) NOT NULL,
    sequence_number BIGINT NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    CONSTRAINT pk_generated_ids PRIMARY KEY (
        run_id,
        entity_type,
        sequence_number
    ),
    CONSTRAINT uq_generated_ids_entity UNIQUE (entity_type, entity_id),
    CONSTRAINT ck_generated_ids_sequence CHECK (sequence_number >= 0),
    CONSTRAINT fk_generated_ids_run FOREIGN KEY (run_id)
        REFERENCES olist_simulator.simulation_runs (run_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.synthetic_entities (
    entity_type VARCHAR(32) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    run_id VARCHAR(64) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    CONSTRAINT pk_synthetic_entities PRIMARY KEY (entity_type, entity_id),
    CONSTRAINT fk_synthetic_entities_run FOREIGN KEY (run_id)
        REFERENCES olist_simulator.simulation_runs (run_id),
    INDEX idx_synthetic_entities_run (run_id, entity_type)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.pending_transitions (
    transition_id VARCHAR(64) NOT NULL,
    run_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    transition_type VARCHAR(32) NOT NULL,
    due_at DATETIME(6) NOT NULL,
    sequence_number INT NOT NULL,
    payload JSON NOT NULL DEFAULT (JSON_OBJECT()),
    state VARCHAR(16) NOT NULL DEFAULT 'pending',
    applied_at DATETIME(6) NULL,
    CONSTRAINT pk_pending_transitions PRIMARY KEY (transition_id),
    CONSTRAINT uq_pending_transitions_order UNIQUE (
        run_id,
        order_id,
        sequence_number
    ),
    CONSTRAINT ck_pending_transitions_sequence CHECK (sequence_number > 0),
    CONSTRAINT ck_pending_transitions_state CHECK (
        state IN ('pending', 'applied', 'skipped', 'failed')
    ),
    CONSTRAINT fk_pending_transitions_run FOREIGN KEY (run_id)
        REFERENCES olist_simulator.simulation_runs (run_id),
    INDEX idx_pending_transitions_due (state, due_at)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.replay_timestamp_mappings (
    run_id VARCHAR(64) NOT NULL,
    entity_type VARCHAR(32) NOT NULL,
    source_entity_id VARCHAR(64) NOT NULL,
    source_timestamp DATETIME(6) NOT NULL,
    replay_timestamp DATETIME(6) NOT NULL,
    speed_multiplier DECIMAL(12, 4) NOT NULL,
    CONSTRAINT pk_replay_timestamp_mappings PRIMARY KEY (
        run_id,
        entity_type,
        source_entity_id,
        source_timestamp
    ),
    CONSTRAINT ck_replay_timestamp_mappings_speed CHECK (speed_multiplier > 0),
    CONSTRAINT fk_replay_timestamp_mappings_run FOREIGN KEY (run_id)
        REFERENCES olist_simulator.simulation_runs (run_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.seed_rows (
    seed_identity VARCHAR(64) NOT NULL,
    entity_name VARCHAR(64) NOT NULL,
    source_row_number BIGINT NOT NULL,
    business_key VARCHAR(256) NULL,
    loaded_at DATETIME(6) NOT NULL,
    CONSTRAINT pk_seed_rows PRIMARY KEY (
        seed_identity,
        entity_name,
        source_row_number
    ),
    CONSTRAINT ck_seed_rows_source_row CHECK (source_row_number > 1)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_simulator.heartbeats (
    heartbeat_id BIGINT NOT NULL,
    heartbeat_ts DATETIME(6) NOT NULL,
    CONSTRAINT pk_heartbeats PRIMARY KEY (heartbeat_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;
