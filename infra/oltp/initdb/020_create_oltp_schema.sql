create schema if not exists simulator_control;

create table if not exists public.product_category_translation (
    product_category_name varchar(256) primary key,
    product_category_name_english varchar(256) not null
);

create table if not exists public.customers (
    customer_id varchar(64) primary key,
    customer_unique_id varchar(64) not null,
    customer_zip_code_prefix varchar(16) not null,
    customer_city varchar(256) not null,
    customer_state varchar(2) not null check (customer_state ~ '^[A-Z]{2}$')
);
create index if not exists idx_customers_unique_id
    on public.customers (customer_unique_id);
create index if not exists idx_customers_location
    on public.customers (customer_zip_code_prefix, customer_state);

create table if not exists public.sellers (
    seller_id varchar(64) primary key,
    seller_zip_code_prefix varchar(16) not null,
    seller_city varchar(256) not null,
    seller_state varchar(2) not null check (seller_state ~ '^[A-Z]{2}$')
);
create index if not exists idx_sellers_location
    on public.sellers (seller_zip_code_prefix, seller_state);

create table if not exists public.products (
    product_id varchar(64) primary key,
    product_category_name varchar(256),
    product_name_lenght integer check (product_name_lenght >= 0),
    product_description_lenght integer check (product_description_lenght >= 0),
    product_photos_qty integer check (product_photos_qty >= 0),
    product_weight_g integer check (product_weight_g >= 0),
    product_length_cm integer check (product_length_cm >= 0),
    product_height_cm integer check (product_height_cm >= 0),
    product_width_cm integer check (product_width_cm >= 0),
    constraint fk_products_category foreign key (product_category_name)
        references public.product_category_translation (product_category_name)
        deferrable initially immediate
);
create index if not exists idx_products_category
    on public.products (product_category_name);

create table if not exists public.orders (
    order_id varchar(64) primary key,
    customer_id varchar(64) not null,
    order_status varchar(32) not null check (
        order_status in (
            'created', 'approved', 'invoiced', 'processing', 'shipped',
            'delivered', 'unavailable', 'canceled'
        )
    ),
    order_purchase_timestamp timestamp without time zone not null,
    order_approved_at timestamp without time zone,
    order_delivered_carrier_date timestamp without time zone,
    order_delivered_customer_date timestamp without time zone,
    order_estimated_delivery_date timestamp without time zone not null,
    constraint fk_orders_customer foreign key (customer_id)
        references public.customers (customer_id)
        deferrable initially immediate,
    constraint ck_orders_approval_after_purchase check (
        order_approved_at is null or order_approved_at >= order_purchase_timestamp
    ),
    constraint ck_orders_carrier_after_purchase check (
        order_delivered_carrier_date is null
        or order_delivered_carrier_date >= order_purchase_timestamp
    ),
    constraint ck_orders_customer_after_purchase check (
        order_delivered_customer_date is null
        or order_delivered_customer_date >= order_purchase_timestamp
    )
);
create index if not exists idx_orders_customer on public.orders (customer_id);
create index if not exists idx_orders_status_purchase
    on public.orders (order_status, order_purchase_timestamp);

create table if not exists public.order_items (
    order_id varchar(64) not null,
    order_item_id integer not null check (order_item_id > 0),
    product_id varchar(64) not null,
    seller_id varchar(64) not null,
    shipping_limit_date timestamp without time zone not null,
    price numeric(18, 2) not null check (price >= 0),
    freight_value numeric(18, 2) not null check (freight_value >= 0),
    primary key (order_id, order_item_id),
    constraint fk_order_items_order foreign key (order_id)
        references public.orders (order_id) deferrable initially immediate,
    constraint fk_order_items_product foreign key (product_id)
        references public.products (product_id) deferrable initially immediate,
    constraint fk_order_items_seller foreign key (seller_id)
        references public.sellers (seller_id) deferrable initially immediate
);
create index if not exists idx_order_items_product on public.order_items (product_id);
create index if not exists idx_order_items_seller on public.order_items (seller_id);

create table if not exists public.order_payments (
    order_id varchar(64) not null,
    payment_sequential integer not null check (payment_sequential > 0),
    payment_type varchar(32) not null check (
        payment_type in ('credit_card', 'boleto', 'voucher', 'debit_card', 'not_defined')
    ),
    payment_installments integer not null check (payment_installments >= 0),
    payment_value numeric(18, 2) not null check (payment_value >= 0),
    primary key (order_id, payment_sequential),
    constraint fk_order_payments_order foreign key (order_id)
        references public.orders (order_id) deferrable initially immediate
);

create table if not exists public.order_reviews (
    review_id varchar(64) not null,
    order_id varchar(64) not null,
    review_score integer not null check (review_score between 1 and 5),
    review_comment_title varchar(1024),
    review_comment_message text,
    review_creation_date timestamp without time zone not null,
    review_answer_timestamp timestamp without time zone not null,
    primary key (review_id, order_id),
    constraint fk_order_reviews_order foreign key (order_id)
        references public.orders (order_id) deferrable initially immediate,
    constraint ck_review_answer_after_creation check (
        review_answer_timestamp >= review_creation_date
    )
);
create index if not exists idx_order_reviews_order on public.order_reviews (order_id);

create table if not exists public.geolocation (
    geolocation_id bigint generated always as identity primary key,
    geolocation_zip_code_prefix varchar(16) not null,
    geolocation_lat numeric(18, 14) not null check (
        geolocation_lat between -90 and 90
    ),
    geolocation_lng numeric(18, 14) not null check (
        geolocation_lng between -180 and 180
    ),
    geolocation_city varchar(256) not null,
    geolocation_state varchar(2) not null check (geolocation_state ~ '^[A-Z]{2}$')
);
create index if not exists idx_geolocation_lookup
    on public.geolocation (geolocation_zip_code_prefix, geolocation_state);

create table if not exists simulator_control.simulation_runs (
    run_id varchar(64) primary key,
    command varchar(16) not null check (command in ('seed', 'run', 'replay')),
    random_seed bigint not null,
    target_rate numeric(12, 4) not null check (target_rate >= 0),
    configuration jsonb not null,
    state varchar(24) not null check (
        state in ('starting', 'running', 'stop_requested', 'stopped', 'completed', 'failed')
    ),
    started_at timestamp without time zone not null,
    heartbeat_at timestamp without time zone not null,
    last_committed_source_timestamp timestamp without time zone,
    stop_requested_at timestamp without time zone,
    finished_at timestamp without time zone,
    counters jsonb not null default '{}'::jsonb,
    error_message text
);
create index if not exists idx_simulation_runs_state
    on simulator_control.simulation_runs (state, heartbeat_at);

create table if not exists simulator_control.generated_ids (
    run_id varchar(64) not null references simulator_control.simulation_runs (run_id),
    entity_type varchar(32) not null,
    sequence_number bigint not null check (sequence_number >= 0),
    entity_id varchar(64) not null,
    primary key (run_id, entity_type, sequence_number),
    unique (entity_type, entity_id)
);

create table if not exists simulator_control.synthetic_entities (
    entity_type varchar(32) not null,
    entity_id varchar(64) not null,
    run_id varchar(64) not null references simulator_control.simulation_runs (run_id),
    created_at timestamp without time zone not null,
    primary key (entity_type, entity_id)
);
create index if not exists idx_synthetic_entities_run
    on simulator_control.synthetic_entities (run_id, entity_type);

create table if not exists simulator_control.pending_transitions (
    transition_id varchar(64) primary key,
    run_id varchar(64) not null references simulator_control.simulation_runs (run_id),
    order_id varchar(64) not null,
    transition_type varchar(32) not null,
    due_at timestamp without time zone not null,
    sequence_number integer not null check (sequence_number > 0),
    payload jsonb not null default '{}'::jsonb,
    state varchar(16) not null default 'pending' check (
        state in ('pending', 'applied', 'skipped', 'failed')
    ),
    applied_at timestamp without time zone,
    unique (run_id, order_id, sequence_number)
);
create index if not exists idx_pending_transitions_due
    on simulator_control.pending_transitions (state, due_at);

create table if not exists simulator_control.replay_timestamp_mappings (
    run_id varchar(64) not null references simulator_control.simulation_runs (run_id),
    entity_type varchar(32) not null,
    source_entity_id varchar(64) not null,
    source_timestamp timestamp without time zone not null,
    replay_timestamp timestamp without time zone not null,
    speed_multiplier numeric(12, 4) not null check (speed_multiplier > 0),
    primary key (run_id, entity_type, source_entity_id, source_timestamp)
);

create table if not exists simulator_control.seed_rows (
    seed_identity varchar(64) not null,
    entity_name varchar(64) not null,
    source_row_number bigint not null check (source_row_number > 1),
    business_key varchar(256),
    loaded_at timestamp without time zone not null,
    primary key (seed_identity, entity_name, source_row_number)
);

create table if not exists simulator_control.heartbeats (
    component_name varchar(64) primary key,
    run_id varchar(64),
    observed_at timestamp without time zone not null,
    state jsonb not null default '{}'::jsonb
);

grant usage on schema public, simulator_control to olist_simulator;
grant select, insert, update, delete on all tables in schema public to olist_simulator;
grant usage, select on all sequences in schema public to olist_simulator;
grant select, insert, update, delete on all tables in schema simulator_control
    to olist_simulator;

grant usage on schema public to olist_cdc_reader;
grant select on all tables in schema public to olist_cdc_reader;

alter default privileges in schema public
    grant select, insert, update, delete on tables to olist_simulator;
alter default privileges in schema public
    grant usage, select on sequences to olist_simulator;
alter default privileges in schema public grant select on tables to olist_cdc_reader;
alter default privileges in schema simulator_control
    grant select, insert, update, delete on tables to olist_simulator;

