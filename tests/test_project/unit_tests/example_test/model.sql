{{
    config(
        materialized='view'
    )
}}
with base as (
    
    select 
        grp, 
        sum(metric) as metric,
        max(batch) as batch
    from {{ ref('example_test_batch') }} a
    group by grp
)

select * from base
