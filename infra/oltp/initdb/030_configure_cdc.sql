alter table public.customers replica identity full;
alter table public.orders replica identity full;
alter table public.order_items replica identity full;
alter table public.order_payments replica identity full;
alter table public.order_reviews replica identity full;
alter table public.products replica identity full;
alter table public.sellers replica identity full;
alter table public.product_category_translation replica identity full;

do $$
begin
    if not exists (
        select 1 from pg_publication where pubname = 'olist_cdc_publication'
    ) then
        create publication olist_cdc_publication for table
            public.customers,
            public.orders,
            public.order_items,
            public.order_payments,
            public.order_reviews,
            public.products,
            public.sellers,
            public.product_category_translation;
    end if;
end
$$;

alter publication olist_cdc_publication set table
    public.customers,
    public.orders,
    public.order_items,
    public.order_payments,
    public.order_reviews,
    public.products,
    public.sellers,
    public.product_category_translation;

grant usage on schema simulator_control to olist_cdc_reader;
grant select, insert, update on simulator_control.heartbeats to olist_cdc_reader;
