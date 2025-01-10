# Development

This application is dockerized. Take a look at [Dockerfile](../../api/Dockerfile) to see how it works.

A very simple [docker-compose.yml](../../docker-compose.yml) has been included to support local development and deployment.

Several components like tests, linting, and scripts can be run either inside of the Docker container, or outside on your  machine.

**Running in Docker is the default**, but on some machines like the M1 Mac, running natively may be desirable for performance reasons.

## Docker

This section covers development using Docker. There are a number of Docker commands included in the [Makefile](../../api/Makefile) which are helpful for local development. Run `make help` for a list of commands.

### Setup

Run `make init && make run logs` to start the local containers. The application will be available at `http://localhost:8080/docs`.

This stands up the following services:

* Flask API (http://localhost:8080)
* Postgres database
* OpenSearch node
* OpenSearchdashboard (http://localhost:5601)
* localstack
* mock oauth server (http://localhost:5001)

### Seed data

Run `make db-seed-local && populate-search-opportunities` to create local data in the database and make it available in the API.

### API Authenticaion

This API uses a very simple [ApiKey authentication approach](https://apiflask.com/authentication/#use-external-authentication-library) which requires the caller to provide a static key. This is specified with the `API_AUTH_TOKEN` environment variable.

### User Authentication

Run `make setup-env-override-file` to create the `override.env` file which will include the necessary JWT keys for running the user.

### Environment Variables

Most configuration options are managed by environment variables.

Environment variables for local development are stored in the [local.env](../../api/local.env) file. This file is automatically loaded when running. If running within Docker, this file is specified as an `env_file` in the [docker-compose](../../docker-compose.yml) file, and loaded [by a script](../../api/src/util/local.py) automatically when running most other components outside the container.

Any environment variables specified directly in the [docker-compose](../../docker-compose.yml) file will take precedent over those specified in the [local.env](../../api/local.env) file.

### Troubleshooting

Errors in standing up the API can originate from an out of date container, database syncronization, or other issues with previously created services. Helper functions are available to rebuild:

* **db-check-migrations** - check if migrations are out of sync
* **volume-recreate** - delete all existing volumes and data
* **remake-backend** - delete all data (`volume-recreate`) and load data (`db-seed-local` and `populate-search-opportunities`)

### VSCode Remote Attach Container Debugging

The API can be run in debug mode that allows for remote attach debugging (currently only supported from VSCode) to the container.

- Requirements:

  - VSCode Python extension
  - Updated Poetry with the `debugpy` dev package in `pyproject.toml`

- See `./vscode/launch.json` which has the debug config. (Named `API Remote Attach`)

- Start the server in debug mode via `make start-debug` or `make start-debug run-logs`.

  - This will start the `main-app` service with port 5678 exposed.

- The server will start in waiting mode, waiting for you to attach the debugger (see `/src/app.py`) before continuing to run.

- Go to your VSCode debugger window and run the `API Remote Attach` option

- You should now be able to hit set breakpoints throughout the API

## Local (non-Docker)

Run `export PY_RUN_APPROACH=local` to run API and test functions locally when running commands in the Makefile. For example, `make test` or `make format` will run outside of Docker.

**Note:** even with the native mode, many components like the DB and API will only ever run in Docker, and you should always make sure that any implementations work within docker.

Running in the native/local approach may require additional packages to be installed on your machine to get working.

### Prerequisites

1. Install the version of Python specified in [pyproject.toml](../../api/pyproject.toml)
   [pyenv](https://github.com/pyenv/pyenv#installation) is one popular option for installing Python,
   or [asdf](https://asdf-vm.com/).
   - If using pyenv run `pyenv local <version>` to ensure that version will be used in subsequent steps
2. Ensure that `python -V` and `python3 -V` are picking up that version.
   - If not, run `pyenv init -` and/or restart your shell to ensure it was run automatically
3. After installing and activating the right version of Python, install
   [poetry](https://python-poetry.org/docs/#installation) and follow the instructions to add poetry to your path if necessary.

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. You'll also need [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**Note:** All the following commands should be run from the `/api` directory.

### Database setup: Run Migrations/Seeds

If you haven't done local development before you'll need to execute the migrations and seed the DB with data using the steps in [database-local-usage.md](database/database-local-usage.md)

### Services

Individual services can be run through Docker, which can be useful in concert with non-Docker application development:

* **OpenSearch**
  * Run `make init-opensearch` setup the OpenSearch Container
  * Run `make populate-search-opportunities` to push data previously seeded in the DB into the search index

  If your DB or OpenSearch end up in an odd place, you can reset all the persistent storage using `make volume-recreate`.

* **Localstack (local s3)**
   * Run `make init-localstack`
* **Mock OAuth server**
   * Run `make init-mock-oath2`

## Next steps

Now that you're up and running, read the [application docs](../../api/README.md) to familiarize yourself with the application.
