
{{
    config(
        materialized='ephemeral',
        tags=['unit_test', 'test2']
    )
}}
SELECT * FROM {{ ref('test2_input') }}
WHERE batch <= {{ var('batch', 100) }}
-- {{ ref('test2_expect') }}