dbt-unit-test (dut)
===

_A tiny framework for testing reusable code inside of dbt models_

[DBT](www.getdbt.com) (Data Buld Tool) is a great way to maintain reusable sql code. With [macros](https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros#macros), we can build parametrizable code blocks which can be used in many places while maintaining DRYness. DBT even allows us to package macros as [modules](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) to be maintained independently and even shared with the world as open-source code like the [dbt-utils](https://github.com/fishtown-analytics/dbt-utils) project.

While reusable code has big advantages, it introduces a single point of failure, which requires careful testing.

`dbt-unit-test` makes it easy to write test cases for any code that might be reused in DBT models.