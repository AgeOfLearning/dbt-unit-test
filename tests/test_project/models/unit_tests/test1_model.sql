{{
    config(
        materialized='incremental',
        unique_key='grp'
    )
}}
WITH base as (
    SELECT grp, sum(metric) AS metric, max(batch) AS batch
    FROM {{ ref('test1_batch') }} a
    {% if is_incremental() %}
    WHERE batch > (SELECT batch FROM {{ this }} ORDER BY batch DESC LIMIT 1)
    {% endif %}
    GROUP BY grp
)
{% if is_incremental() %}
SELECT grp, sum(metric) metric, max(batch) AS batch
FROM (
    SELECT grp, metric, batch
    FROM {{ this }}
    WHERE grp in (SELECT DISTINCT grp FROM base)
    UNION ALL
    SELECT grp, metric, batch
    FROM base
) AS a
GROUP BY grp
{% else %}
SELECT * FROM base
{% endif %}


-- WITH base as (
--     SELECT grp, sum(metric) AS metric, max(batch) AS batch
--     FROM {{ ref('test1_batch') }} a
--     {% if is_incremental() %}
--     WHERE batch > (SELECT batch FROM {{ this }} ORDER BY batch DESC LIMIT 1)
--     {% endif %}
--     GROUP BY grp
-- )

-- SELECT * FROM base
