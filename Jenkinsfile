node {
    checkout scm
    docker.image('postgres').withRun('-e "POSTGRES_PASSWORD=test -e POSTGRES_USER=test"') { c ->
        docker.withRegistry('https://gitlab.aofl.com:5001') {
            docker.image(
                'engineering-automation_tools/automation_images/dbt-unit-test-ci:latest'
            ).withRun('-v "$(pwd)":/dbt-unit-test').inside("--link ${c.id}:db") {
                pip install -e /dbt-unit-test
                tox
                sh 'while ! nc -z db 5432; do sleep 1; done;'
                dut run --log-level debug
            }
        }
    }
}