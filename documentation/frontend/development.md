# Development

This [Next.js](https://nextjs.org) application can be run natively (or locally)

**Running in locally is the default**, but it can be useful to run the built images in order to troubleshoot and to connect directly with the local API application for development.

## Local (non-Docker)

Run `npm install && npm run dev` to start the application.

### Testing "built" version locally

The Next.js frontend application is exported for production using [next build](https://nextjs.org/docs/app/api-reference/cli/next#next-build-options). To recreate this locally, outside of the container, run the following:

- `npm run build` - Builds the production Next.js bundle
- `npm start` - Runs the Next.js server, after building the production bundle

### Search and Opportunity Pages

The `/search` and opportunity pages rely on the application API. The API endpoint and authenticaion token are defined in `.env.development` and can be overwritten in an `.env.ocal` file.

Update the `API_URL` can be set to connect to prod (`https://api.simpler.grants.gov`) or lower environment URLs to quickly develop using production or development data. This requires the correct `API_AUTH_TOKEN` variable to be set correctly.

To connect to the development version of the API, run `make init && db-seed-local && populate-search-opportunities` in the `/api` folder.

See [documentation/api/development.md](../api/development.md) for more details.

### Authentication

Running authentication locally requires running the API, directing the API redirect to the frontend, and sharing the correct JWT keys.

1. Run `make setup-env-override-file` to create the `override.env` file in the `/api` folder
2. Copy the `API_JWT_PUBLIC_KEY` value from `/api/override.env` file to `/frontend/.env.local` file which creates the necessary keys
3. Add `LOGIN_FINAL_DESTINATION=http://localhost:3000/api/auth/callback` to the `api/override.env` so the API redirects to the correct callback route
4. Start the API and frontend for development

#### Secrets

Some functionality will not work locally without supplying the application environment variables containing secrets.

- New Relic
  - `NEW_RELIC_APP_NAME`
  - `NEW_RELIC_LICENSE_KEY`
- Email subscription form (Sendy)
  - `SENDY_API_KEY`
  - `SENDY_API_URL`
  - `SENDY_LIST_ID`

If you need to access this functionality locally, contact an engineer on the team to get access to the necessary secrets.

### +Docker

#### Development version

Alternatively, you can run the application in a Docker container.

**Note**: If you are running docker locally for the first time, you need to run the API locally through Docker as well, in order to create the required `api_grants_backend` network.

From the `/frontend` directory:

1. Run the local development server
   ```bash
   make dev
   ```
1. Navigate to [localhost:3000](http://localhost:3000) to view the application

- If installing new packages locally with npm and using `make dev` with docker to run locally, you may need to run `make build` first to bring the new packages into the container

#### Production version

The `make dev` command runs the `docker-compose.yml` which runs the `dev` target in the [Dockerfile](./Dockerfile). To run a production version in docker, run `docker compose up -d -f docker-compose-realease.yml` which targest the `release` stage in the docker build. This runs the production version, while still creating a network connection to the local API.

#### Testing Release Target Locally

To test the release target locally, run:

- `make release-build OPTS="--tag [IMAGE_NAME]"` or
- `docker buildx build --target release --tag [IMAGE_NAME]` for a faster build on OSX

to build a local image. To view the site at `localhost:3000`, run: `docker run -e "HOSTNAME=0.0.0.0" -p 3000:3000 [IMAGE_NAME]`.

### Search and Opportunity Pages

The search page and opportunity pages needs additional setup to test locally.

To 
