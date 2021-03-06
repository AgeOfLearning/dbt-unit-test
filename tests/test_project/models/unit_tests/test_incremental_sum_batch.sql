{{
    config(
        materialized='ephemeral',
        tags=['unit_test', 'test_incremental_sum']
    )
}}
SELECT * FROM {{ ref('test_incremental_sum_input') }}
WHERE batch <= {{ var('batch', 100) }}
-- {{ ref('test_incremental_sum_expect') }}