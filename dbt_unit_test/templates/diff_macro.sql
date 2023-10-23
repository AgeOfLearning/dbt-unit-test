{% macro test_diff(model, test) %}
    {{ return(adapter.dispatch('test_diff')(model, test)) }}
{% endmacro %}

{% macro default__test_diff(model, test) %}
    with extra_rows as (
        SELECT * FROM {{ model }} EXCEPT SELECT * FROM {{ test }}
    ), 
    missing_rows as (
        SELECT * FROM {{ test }} EXCEPT SELECT * FROM {{ model }}
    )
    SELECT count(*)
    FROM (SELECT * FROM extra_rows UNION ALL SELECT * FROM missing_rows) a
{% endmacro %}

{% macro bigquery__test_diff(model, test) %}
    WITH extra_rows AS (
    SELECT * FROM {{ model }} EXCEPT DISTINCT SELECT * FROM {{ test }}
    ), 
    missing_rows AS (
        SELECT * FROM {{ test }} EXCEPT DISTINCT SELECT * FROM {{ model }}
    ),
    all_missing as (
        SELECT COUNT(*) AS missing_count
        FROM (SELECT * FROM extra_rows UNION ALL SELECT * FROM missing_rows) a
    )
    SELECT missing_count FROM all_missing
    WHERE missing_count > 0
{% endmacro %}
