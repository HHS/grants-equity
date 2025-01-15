# Application Documentation

## Introduction

- This is a [Next.js](https://nextjs.org/) React web application, written in [TypeScript](https://www.typescriptlang.org/).
- [U.S. Web Design System](https://designsystem.digital.gov) provides themeable styling and a set of common components.
- [React-USWDS](https://github.com/trussworks/react-uswds) provides React components already with USWDS theming out of the box. For a reference point starting out, see `react-uswds-hello.tsx` which includes examples of react-uswds component usage.
- [Storybook](https://storybook.js.org/) is included as a frontend workshop.

## Directory structure

```
├── .storybook        # Storybook configuration
├── public            # Static assets
│   └── locales       # Internationalized content
├── src               # Source code
│   ├── components    # Reusable UI components
│   ├── app           # Page routes and data fetching
│   │   └── api       # API routes (optional)
│   └── styles        # Sass & design system settings
├── stories           # Storybook pages
└── tests             # Unit and E2E tests
```

## 💻 Local Development

[Next.js](https://nextjs.org/docs) provides the React framework for building the web application. Pages are defined in the `app/` directory. Pages are automatically routed based on the file name. For example, `pages/[locale]/page.tsx` is the home page.

[**Learn more about developing Next.js applications** ↗️](https://nextjs.org/docs)

### Running the app locally

Before running the server, duplicate the `/frontend/env.development` file and name the copy `/frontend/.env.local`, in order to avoid checking in any sensitive data to Github.

From the `/frontend` directory:

1. Install dependencies
   ```bash
   npm ci
   ```
1. Optionally, disable [telemetry data collection](https://nextjs.org/telemetry)
   ```bash
   npx next telemetry disable
   ```
1. Run the local development server
   ```bash
   npm run dev
   ```
1. Navigate to [localhost:3000](http://localhost:3000) to view the application

### Other scripts

- `npm run build` - Builds the production Next.js bundle
- `npm start` - Runs the Next.js server, after building the production bundle

## Testing and feature development

See [development.md](../documentation/frontend/development.md) for full installation and development instructions.

## Technical information

- [Architecture diagram](../documentation/architecture/README.md)
- [Authentication overview](../documentation/api/authentication.md)
- [Authentication local setup](../documentation/frontend/development.md#authentication)
- [Testing](../documentation/frontend/development.md#-testing)
- [Type checking, linting, and formatting](../documentation/frontend/development.md#-type-checking-linting-and-formatting)
- [Search and opportunity page local setup](../documentation/frontend/development.md#search-and-opportunity-pages)
