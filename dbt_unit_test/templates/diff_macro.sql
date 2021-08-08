{%- macro print_list(list_to_print=none, indent=4) -%}

    {%- for col_name in list_to_print -%}
        {{- col_name | indent(indent) -}}{{ ",\n    " if not loop.last }}
    {%- endfor -%}

{%- endmacro -%}

{% macro test_diff(model, test) %}

{# converts all varchars to binary if necessary #}
{%- set columns = adapter.get_columns_in_relation(model) -%}
{%- set model_columns_to_select = [] -%}
{%- set test_columns_to_select = [] -%}

{% for column in columns %}
    {% if column.dtype == 'BINARY' %}  
        {% do test_columns_to_select.append("to_binary("~column.name~")") %}
    {% else %}  
        {% do test_columns_to_select.append(column.name) %}
    {% endif %}  
    {% do model_columns_to_select.append(column.name) %}
{% endfor %}

with extra_rows as (
    SELECT {{ print_list(model_columns_to_select) }}
    FROM {{ model }} 
    EXCEPT 
    SELECT {{ print_list(test_columns_to_select) }}
    FROM {{ test }}
), 
missing_rows as (
    SELECT {{ print_list(test_columns_to_select) }}
    FROM {{ test }} 
    EXCEPT 
    SELECT {{ print_list(model_columns_to_select) }}
    FROM {{ model }}
)
SELECT * FROM extra_rows 
UNION ALL 
SELECT * FROM missing_rows
{% endmacro %}
