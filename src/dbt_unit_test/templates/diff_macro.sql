{% macro test_diff(model, test) %}
with extra_rows as (
    SELECT * FROM {{ model }} EXCEPT SELECT * FROM {{ test }}
), 
missing_rows as (
    SELECT * FROM {{ test }} EXCEPT SELECT * FROM {{ model }}
)
SELECT count(*)
FROM (SELECT * FROM extra_rows UNION ALL SELECT * FROM missing_rows) a
{% endmacro %}
