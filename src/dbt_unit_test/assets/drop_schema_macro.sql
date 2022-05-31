{% macro drop_schema(name) %}

    {% set sql %}
        drop schema if exists {{ name }}
    {% endset %}

    {% do run_query(sql) %}

{% endmacro %}
