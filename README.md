dbt-unit-test (dut)
===

_A tiny framework for testing reusable code inside of dbt models_

[DBT](www.getdbt.com) (Data Buld Tool) is a great way to maintain reusable sql code. With [macros](https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros#macros), we can build parametrizable code blocks which can be used in many places while maintaining DRYness. DBT even allows us to package macros as [modules](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) to be maintained independently and even shared with the world as open-source code like the [dbt-utils](https://github.com/fishtown-analytics/dbt-utils) project.

While reusable code has big advantages, it introduces a single point of failure, which requires careful testing.

`dbt-unit-test` makes it easy to write test cases for any code that might be reused in DBT models.

## Installation
```
$ pip install dbt-unit-test
```
or for the very latest version:
```
$ pip install git+https://github.com/AgeOfLearning/dbt-unit-test.git
```

## Setup
From the root of your dbt project run:
```
$ dut init
```
This will set up a `dbt_unit_test.yml` file right next to your `dbt_project.yml`.

Now, you will need to create a dbt profile called `unit_test`. This profile should use a database/schema on the system where the code to be tested is run. Ideally, at least the schema should be different than any schema that contains "real" DBT models.

## Quick Start
```
dut run
```
This runs all the tests. You can select which tests to run with `--tests`.

## Anatomy of a Test
The init command installs an example unit test here (the one you just ran if you did the last session).:
```
your_dbt_project_root/
    dbt_project.yml
    ...
    dbt_unit_test.yml
    unit_tests/
        example_test/
            expect.csv
            input.csv
            model.sql
```
This `example_test` is the basic setup of a unit test: A directory with 3 files: `input.csv`,  `model.sql` and `expect.csv`. The files are always named like this. The directory distinguishes one test from another. Test directories can be organized within other directories, but must have unique names.

The `input.csv` and `expect.csv` files are both DBT [seeds](https://docs.getdbt.com/docs/building-a-dbt-project/seeds). They represent data referenced by the dbt model in `model.sql` and the data that this model is expected to produce.

The `model.sql` file is just a dbt model. It should contain code that is used elsewhere like a DBT macro or a UDF.

These files are co-located in a single directory so that each test represents a discret unit of code an all of its components are easy to find. The `dut run` command will place these files in the appropriate locations (`models/`, `data/`) so that the they can be run by DBT.

After the unit test models are run, `dut` will validate that the DBT model produced by `model.sql` is identical to the dataset in `expect.csv`.

## Inside `model.sql`
The `example_test/model.sql` looks like this:
```sql
{{
    config(
        materialized='view'
    )
}}
with base as (
    select 
        grp, 
        sum(metric) as metric,
        max(batch) as batch
    from {{ ref('example_test_input') }} a
    group by grp
)
select * from base
```
Any model/seed in the test can be referenced with `{{ ref('<test_name>_<file_name>') }}`. So this test uses this rubric with `{{ ref('example_test_input') }}`.

## Incremental Models
Incremental models are often some of the trickiest to get right. This is because they rely on the state created by the previous runs to form their current run output. `dut` has a test pattern for this important use-case.

The `input.csv` file can have a column called `batch`, like this:
```sql
batch,  grp,    metric
1,      0,      10
1,      0,      10
1,      1,      10
1,      1,      10
2,      1,      10
2,      2,      10
2,      2,      10
3,      3,      10
```

`dut run` will automatically create and additional model called `<test_name>_batch` that will be available within `model.sql`. `dut run` runs the test models N (default 2) times configurable with `--batches`.

On the first dbt run in our `example_test`, the model referenced by `{{ ref('example_test_batch') }}` will only have this data:
```sql
batch,  grp,    metric
1,      0,      10
1,      0,      10
1,      1,      10
1,      1,      10
```
It only contains rows where `batch <= 1`. Subsequent dbt runs will filter less of the data where `batch <= n`, `n` being the ordinal number of the dbt run (the batch). On the final dbt run (the 2nd by default), `{{ ref('example_test_batch') }}` will always be equivalent to `{{ ref('example_test_input') }}`.

## Tutorial: Convert `example_test` into an incremental model.

If we change the model configuration to:
```sql
{{
    config(
        materialized='incremental',
        unique_key='grp'
    )
}}
with base as (
    select 
        grp, 
        sum(metric) as metric,
        max(batch) as batch
    from {{ ref('example_test_batch') }} a
    group by grp
)
select * from base
```
Our test passes, but the model is not really incremental because the entire table is replaced on the last dbt run of the `dut run`. We want our model to consume only the new data on each run, as well as the previous state of the model.

Let's change our model to this:
```sql
{{
    config(
        materialized='incremental',
        unique_key='grp'
    )
}}
with base as (
    select grp, sum(metric) as metric, max(batch) as batch
    from {{ ref('example_test_batch') }} a

    {% if is_incremental() %}
    where batch > (
        -- only pull new data on incremental runs
        select batch from {{ this }} order by batch desc limit 1
    )
    {% endif %}

    group by grp
)

{% if is_incremental() %}

select 
    grp,
    sum(metric) as metric, -- sum of sums
    max(batch) as batch    -- update the most recent batch of the grp
from (

    -- find any grp sums that should be updated by data in the most recent batch
    select grp, metric, batch
    from {{ this }}
    where grp in (select distinct grp from base)

    union all

    -- add on the new batch data
    select grp, metric, batch
    from base

) as a
group by grp

{% else %}

-- on a full refresh, just run the old query
select * from base

{% endif %}
```

Great! Now we have an incremental model that only requires the newest raw data, and the test passes.

### Wait, what are we testing?
We have just proven that this incremental model operates the way we expect, but we need to be able to reuse this code. Let's package this as a macro:

`macros/incremental_sum.sql`
```sql
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
```

The generic version of this code is not so easy on the eyes, but what is important is that the interface is nice and clean:

`example_test/model.sql`
```sql
{{
    config(
        materialized='incremental',
        unique_key='grp'
    )
}}
{{
    incremental_sum(
        reference = ref('example_test_batch'),
        metric_field = 'metric',
        group_field = 'grp',
        load_time_field = 'batch'
    )
}}
```
Now we can write many tests for this reusable code, and use it with confidence because we have tested it thoroughly!