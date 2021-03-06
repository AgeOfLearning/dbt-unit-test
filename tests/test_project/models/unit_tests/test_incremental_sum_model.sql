{{
    config(
        materialized='incremental',
        unique_key='grp'
    )
}}
{{
    incremental_sum(
        reference = ref('test_incremental_sum_batch'),
        metric_field = 'metric',
        group_field = 'grp',
        load_time_field = 'batch'
    )
}}