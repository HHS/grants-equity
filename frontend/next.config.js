// @ts-check

const withNextIntl = require("next-intl/plugin")();
const sassOptions = require("./scripts/sassOptions");
const nrExternals = require("@newrelic/next/load-externals");

/**
 * Configure the base path for the app. Useful if you're deploying to a subdirectory (like GitHub Pages).
 * If this is defined, you'll need to set the base path anywhere you use relative paths, like in
 * `<a>`, `<img>`, or `<Image>` tags. Next.js handles this for you automatically in `<Link>` tags.
 * @see https://nextjs.org/docs/api-reference/next.config.js/basepath
 * @example "/test" results in "localhost:3000/test" as the index page for the app
 */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH;
const appSassOptions = sassOptions(basePath);

/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        // static pages are stored for 6 hours, refreshed in the background for
        // up to 10 minutes, and up to 12 hours if there is an error
        source: "/:path*",
        headers: [
          {
            key: "Cache-Control",
            value:
              "s-maxage=21600, stale-while-revalidate=600, stale-if-error=43200",
          },
          {
            key: "Vary",
            value: "Accept-Language",
          },
        ],
      },
      // search page is stored 1 hour, stale 1 min, stale if error 5 mins
      {
        source: "/search",
        headers: [
          {
            key: "Cache-Control",
            value:
              "s-maxage=3600, stale-while-revalidate=60, stale-if-error=300",
          },
        ],
      },
      // opportunity pages are stored 10 mins, stale 1 min, stale if error 5 mins
      {
        source: "/opportunity/:id(\\d{1,})",
        headers: [
          {
            key: "Cache-Control",
            value:
              "s-maxage=600, stale-while-revalidate=60, stale-if-error=300",
          },
        ],
      },
      // don't cache the form
      {
        source: "/subscribe/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, must-revalidate",
          },
        ],
      },
      // don't cache the api
      {
        source: "/api/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, must-revalidate",
          },
        ],
      },
    ];
  },
  basePath,
  reactStrictMode: true,
  // Output only the necessary files for a deployment, excluding irrelevant node_modules
  // https://nextjs.org/docs/app/api-reference/next-config-js/output
  output: "standalone",
  sassOptions: appSassOptions,
  serverExternalPackages: ["newrelic"],
  webpack: (config) => {
    nrExternals(config);
    return config;
  },
  eslint: {
    dirs: [
      "src",
      "stories",
      ".storybook",
      "tests",
      "scripts",
      "frontend",
      "lib",
      "types",
    ],
  },
};

module.exports = withNextIntl(nextConfig);
