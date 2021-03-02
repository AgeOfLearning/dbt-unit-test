{% macro drop_schema(name) %}
{% set sql %}
DROP SCHEMA IF EXISTS {{ name }}
{% endset %}
{% do run_query(sql) %}
{% endmacro %}
