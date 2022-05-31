
{% raw %}
{{
    config(
        materialized='ephemeral',
        tags=['unit_test', '{% endraw %}{{ test_name }}{% raw %}']
    )
}}

select *
from {{ ref('{% endraw %}{{ test_name }}{% raw %}_input') }}
where batch = {{ var('batch') }}
{% endraw %}
