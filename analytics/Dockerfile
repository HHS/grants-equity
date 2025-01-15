# Use the official python3 image based on Debian 11 "Bullseye".
# https://hub.docker.com/_/python

# The build stage that will be used to deploy to the various environments
# needs to be called `release` in order to integrate with the repo's
# top-level Makefile
FROM python:3.13-slim AS base

# Install poetry, the package manager.
# https://python-poetry.org
RUN pip install --no-cache-dir poetry==1.8.2 --upgrade

RUN apt-get update \
  # Remove existing packages before installing their never versions
  && apt-get remove --yes \
    build-essential \
    libc-dev \
    libpq-dev \
    postgresql \
    wget \
  # Install security updates
  # https://pythonspeed.com/articles/security-updates-in-docker/
  && apt-get upgrade --yes \
  && apt-get install --no-install-recommends --yes \
    build-essential \
    libc-dev \
    libpq-dev \
    postgresql \
    wget \
  # Reduce the image size by clear apt cached lists
  # Complies with https://github.com/codacy/codacy-hadolint/blob/master/codacy-hadolint/docs/description/DL3009.md
  && rm -fr /var/lib/apt/lists/* \
  && rm /etc/ssl/private/ssl-cert-snakeoil.key

ARG RUN_UID
ARG RUN_USER

# The following logic creates the RUN_USER home directory and the directory where
# we will be storing the application in the image. This runs when the user is not root
RUN : "${RUN_USER:?RUN_USER and RUN_UID need to be set and non-empty.}" && \
  [ "${RUN_USER}" = "root" ] || \
  (useradd --create-home --create --user-group --home "/home/${RUN_USER}" --uid ${RUN_UID} "${RUN_USER}" \
  && mkdir /analytics \
  && chown -R ${RUN_UID} "/home/${RUN_USER}" /analytics)

# Set PYTHONPATH so that the tests can find the source code.
ENV PYTHONPATH="/analytics/src/:$PYTHONPATH"

#-----------
# Dev image
#-----------

FROM base AS dev
ARG RUN_USER

# In between ARG RUN_USER and USER ${RUN_USER}, the user is still root
# If there is anything that needs to be ran as root, this is the spot

USER ${RUN_USER}
WORKDIR /analytics

COPY pyproject.toml poetry.lock ./
# Explicitly create a new virtualenv to avoid getting overridden by mounted .venv folders
RUN poetry config virtualenvs.in-project false && poetry env use python
# Install all dependencies including dev dependencies
RUN poetry install --no-root --with dev

COPY . /analytics

#---------
# Release
#---------

FROM base AS release
ARG RUN_USER

# Gunicorn requires this workaround to create writable temporary directory in
# our readonly root file system. https://github.com/aws/containers-roadmap/issues/736
RUN mkdir -p /tmp
VOLUME ["/tmp"]

# TODO(https://github.com/navapbc/template-application-flask/issues/23) Productionize the Docker image

WORKDIR /analytics

COPY . /analytics

# Remove any existing virtual environments that might exist. This
# might happen if testing out building the release image from a local machine
# that has a virtual environment within the project analytics folder.
RUN rm -fr /analytics/.venv

# Set virtualenv location to be in project to be easy to find
# This will create a virtualenv in /analytics/.venv/
# See https://python-poetry.org/docs/configuration/#virtualenvsin-project
# See https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Install production runtime dependencies only
RUN poetry install --no-root --only main

# Build the application binary (python wheel) defined in pyproject.toml
# Note that this will only copy over python files, and files stated in the
# include section in pyproject.toml.
RUN poetry build --format wheel && \
  poetry run pip install --no-cache-dir dist/*.whl

# Add project's virtual env to the PATH so we can directly run poetry scripts
# defiend in pyproject.toml
ENV PATH="/analytics/.venv/bin:$PATH"


USER ${RUN_USER}
