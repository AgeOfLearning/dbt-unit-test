
{{
    config(
        materialized='ephemeral',
        tags=['unit_test', 'test1']
    )
}}
SELECT * FROM {{ ref('test1_input') }}
WHERE batch <= {{ var('batch', 100) }}
-- {{ ref('test1_expect') }}
