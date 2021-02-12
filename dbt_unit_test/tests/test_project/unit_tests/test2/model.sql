{{
    config(
        materialized='view'
    )
}}
WITH base as (
    SELECT grp, sum(metric) AS metric, max(batch) AS batch
    FROM {{ ref('test1_batch') }} a
    GROUP BY grp
)
SELECT * FROM base
