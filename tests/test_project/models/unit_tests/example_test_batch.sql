{{
    config(
        materialized='ephemeral',
        tags=['unit_test', 'example_test']
    )
}}
SELECT * FROM {{ ref('example_test_input') }}
WHERE batch <= {{ var('batch', 100) }}
-- {{ ref('example_test_expect') }}