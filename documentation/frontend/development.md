# Development

This [Next.js](https://nextjs.org) application can be run natively (or locally)

**Running in locally is the default**, but it can be useful to run the built images in order to troubleshoot and to connect directly with the local API application for development.

## Local (non-Docker)

### 🏗️ Development version

Run `npm install && npm run dev` to install and start the application.

### 🏛️ "Built" version

The Next.js frontend application is exported for production using [next build](https://nextjs.org/docs/app/api-reference/cli/next#next-build-options). To recreate this locally, outside of the container, run the following:

- `npm run build` - Builds the production Next.js bundle
- `npm start` - Runs the Next.js server, after building the production bundle

## Docker

### 🏗️ Development version

Alternatively, you can run the application in a Docker container.

**Note**: If you are running docker locally for the first time, you need to run the API locally through Docker as well, in order to create the required `api_grants_backend` network.

From the `/frontend` directory:

1. Run the local development server
   ```bash
   make dev
   ```
1. Navigate to [localhost:3000](http://localhost:3000) to view the application

- If installing new packages locally with npm and using `make dev` with docker to run locally, you may need to run `make build` first to bring the new packages into the container

### 🚀 Production version

The `make dev` command runs the `docker-compose.yml` which runs the `dev` target in the [Dockerfile](./Dockerfile). To run a production version in docker, run `docker compose up -d -f docker-compose-realease.yml` which targest the `release` stage in the docker build. This runs the production version, while still creating a network connection to the local API.

### Testing Release Target Locally

To test the release target locally, run:

- `make release-build OPTS="--tag [IMAGE_NAME]"` or
- `docker buildx build --target release --tag [IMAGE_NAME]` for a faster build on OSX

to build a local image. To view the site at `localhost:3000`, run: `docker run -e "HOSTNAME=0.0.0.0" -p 3000:3000 [IMAGE_NAME]`.

## 🎯 Testing

### :atom: Unit Testing

[Jest](https://jestjs.io/docs/getting-started) is used as the test runner and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro) provides React testing utilities.

Tests are manged as `.test.ts` (or `.tsx`) files in the the `tests/` directory.

To run tests:

- `npm test` - Runs all tests and outputs test coverage report
- `npm run test-update` - Updates test snapshots
- `npm run test-watch` - Runs tests in [watch](https://jestjs.io/docs/cli#--watch) mode. Tests will re-run when files are changed, and an interactive prompt will allow you to run specific tests or update snapshots.

A subset of tests can be ran by passing a pattern to the script. For example, to only run tests in `tests/pages/`:

```sh
npm run test-watch -- pages
```

### 🚦 End-to-end (E2E) testing

[Playwright](https://playwright.dev/) is a framework for web testing and its test runner is called [Playwright Test](https://playwright.dev/docs/api/class-test), which can be used to run E2E or integration tests across chromium, firefox, and webkit browsers.

E2E test filenames end with `.spec.ts` and are found in the `tests/e2e` directory.

To run E2E tests via CLI:

- `cd ../api && make init db-seed-local start` (prerequisite to start the API)
- `npx playwright install --with-deps` — Downloads playwright browsers required to run tests
- `npm run test:e2e` — Runs all E2E tests using the playwright config found at `tests/playwright.config.ts`
- `npm run test:e2e:ui` — Run specific or all E2E tests using Playwright's [UI mode](https://playwright.dev/docs/test-ui-mode), which is useful for debugging full traces of each test

To run E2E tests using VS Code:

1. Download the VS Code extension described in these [Playwright docs](https://playwright.dev/docs/running-tests#run-tests-in-vs-code)
2. Follow the [instructions](https://playwright.dev/docs/getting-started-vscode#running-tests) Playwright provides

Playwright E2E tests run "local-to-local", requiring both the frontend and the API to be running for the tests to pass - and for the database to be seeded with data.

In CI, the "Front-end Checks" workflow (`.github/workflows/ci-frontend-e2e.yml`) summary will include an "Artifacts" section where there is an attached "playwright-report". [Playwright docs](https://playwright.dev/docs/ci-intro#html-report) describe how to view HTML Report in more detail.

### 🤖 Type checking, linting, and formatting

#### Tools

- [TypeScript](https://www.typescriptlang.org/) is used for type checking.
- [ESLint](https://eslint.org/) is used for linting. This helps catch common mistakes and encourage best practices.
- [Prettier](https://prettier.io/) is used for code formatting. This reduces the need for manual formatting or nitpicking and enforces a consistent style.PRs in Github Actions, other than e2e tests

It's recommended that developers configure their code editor to auto run these tools on file save. Most code editors have plugins for these tools or provide native support.

<details>
  <summary>VSCode instructions</summary>

1. Install the [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) and [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) extensions.
2. Add the following to a `.vscode/settings.json` Workspace Settings file:

   ```json
   {
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     },
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "eslint.workingDirectories": ["./frontend"],
     "typescript.validate.enable": true
   }
   ```

   For these tools to auto run, the settings must be located in the root of your current VSCode workspace. For example, if you open the `frontend/` directory in VSCode, the settings should be located at `frontend/.vscode/settings.json`. If you then open then root repository directory in VSCode as your workspace, these tools will not auto run. (Note that adding the settings to the root repository directory may affect other parts of a monorepo.)

   You can alternatively add the settings to your User Settings, however they will apply globally to any workspace you open. See [User and Workspace Settings](https://code.visualstudio.com/docs/getstarted/settings) for more guidance.

</details>

#### NPM Scripts for type checking, linting, and formatting

- `npm run ts:check` - Type checks all files
- `npm run lint` - Lints all files and reports any errors
- `npm run lint-fix` - Lints all files and fixes any auto-fixable errors
- `npm run format`: Formats all files based on prettier rules
- `npm run format-check`: Check files for prettier formatting violations without fixing them
- `npm run all-checks`: Runs linting, typescript check, unit testing, and creates a build - simulating locally tests that are run on PRs in Github Actions, other than e2e tests

### 🖼️ Storybook

Storybook is a [frontend workshop](https://bradfrost.com/blog/post/a-frontend-workshop-environment/) for developing and documenting pages and components in isolation. It allows you to render the same React components and files in the `src/` directory in a browser, without the need for a server or database. This allows you to develop and manually test components without having to run the entire Next.js application.

See the [Storybook Next.js documentation](https://github.com/storybookjs/storybook/tree/next/code/frameworks/nextjs) for more information about using Storybook with Next.js

Similar to the Next.js application, Storybook can be ran natively or in a Docker container.

#### Native

From the `frontend/` directory:

1. `npm run storybook`
2. Navigate to [localhost:6006](http://localhost:6006) to view

#### Static

- `npm run storybook-build` - Exports a static site to `storybook-static/`

#### Docker

Alternatively, you can run Storybook in a Docker container.

From the `frontend/` directory:

1. `make storybook`
2. Navigate to [localhost:6006](http://localhost:6006) to view

### 🐛 Debugging the Next App in VSCode

- See the debug config: `./.vscode/launch.json`
  - There are several debug config targets defined there depending on if you want to debug just client components (client-side), just server components (server-side), or both (with the Full Stack option). You can also debug the built server (launched from `npm start` instead of `npm run dev`).
- Run one of these launch targets from the VSCode debug menu
- Place breakpoints in VSCode
- Visit the relevant routes in the browser and confirm you can hit these breakpoints

**Note** that debugging the server-side or full-stack here doesn't debug the API. [See the API readme for more information](../documentation/api/development.md)

## Feature setup and development

The following features require additional local setup to use.

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

### New Relic and Sendy (email)

Some functionality will not work locally without supplying the application environment variables containing secrets.

- New Relic
  - `NEW_RELIC_APP_NAME`
  - `NEW_RELIC_LICENSE_KEY`
- Email subscription form (Sendy)
  - `SENDY_API_KEY`
  - `SENDY_API_URL`
  - `SENDY_LIST_ID`

If you need to access this functionality locally, contact an engineer on the team to get access to the necessary secrets.

## Other topics

- [Internationalization](../documentation/frontend/internationalization.md)
- [Feature Flags](../documentation/frontend/featureFlags.md)
- Refer to the [architecture decision records](../documentation/decisions) for more context on technical decisions.
