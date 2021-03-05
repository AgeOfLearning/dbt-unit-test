{% macro incremental_sum(
    reference,
    metric_field,
    group_field,
    load_time_field
) %}

with base as (
    select 
        {{ group_field }},
        sum({{ metric_field }}) as {{ metric_field }},
        max({{ load_time_field }}) as {{ load_time_field }}
    from {{ reference }} a

    {% if is_incremental() %}
    where {{ load_time_field }} > (
        -- only pull new data on incremental runs
        select {{ load_time_field }} from {{ this }} order by {{ load_time_field }} desc limit 1
    )
    {% endif %}

    group by {{ group_field }}
)

{% if is_incremental() %}

select 
    {{ group_field }},
    sum({{ metric_field }}) as {{ metric_field }}, -- sum of sums
    max({{ load_time_field }}) as {{ load_time_field }}    -- update the most recent {{ load_time_field }} of the {{ group_field }}
from (

    -- find any {{ group_field }} sums that should be updated by data in the most recent {{ load_time_field }}
    select {{ group_field }}, {{ metric_field }}, {{ load_time_field }}
    from {{ this }}
    where {{ group_field }} in (select distinct {{ group_field }} from base)

    union all

    -- add on the new {{ load_time_field }} data
    select {{ group_field }}, {{ metric_field }}, {{ load_time_field }}
    from base

) as a
group by {{ group_field }}

{% else %}

-- on a full refresh, just run the old query
select * from base

{% endif %}

{% endmacro %}