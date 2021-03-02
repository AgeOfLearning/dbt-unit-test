{% raw %}{{
    config(
        materialized='ephemeral',
        tags=['unit_test', '{% endraw %}{{ test_name }}{% raw %}']
    )
}}
SELECT * FROM {{ ref('{% endraw %}{{ test_name }}{% raw %}_input') }}
WHERE batch <= {{ var('batch', 100) }}{% endraw %}
-- {% raw %}{{ ref('{% endraw %}{{ test_name }}{% raw %}_expect') }}{% endraw %}
