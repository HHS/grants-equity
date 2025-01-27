import path from "path";

/**
 * @file Storybook's main configuration file that controls the generation of Storybook.
 * Handles things like config for location of story files and managing presets (which configure webpack and babel).
 * @see https://storybook.js.org/docs/configurations/default-config/
 */
// @ts-check
// Support deploying to a subdirectory, such as GitHub Pages.
const NEXT_PUBLIC_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/**
 * Most projects use Storybook for internal purposes, and partners may be
 * sensitive to the Storybook showing up in Google results.
 * @param {string} head
 * @returns string
 */
function blockSearchEnginesInHead(head) {
  return `
    ${head}
    <meta name="robots" content="none" />
  `;
}

/**
 * @type {import("@storybook/nextjs").StorybookConfig}
 */
const config = {
  stories: ["../stories/**/*.@(mdx|stories.@(js|jsx|ts|tsx))"],
  addons: ["@storybook/addon-essentials", "@chromatic-com/storybook"],

  framework: {
    name: "@storybook/nextjs",
    options: {
      nextConfigPath: path.resolve(__dirname, "../next.config.js"),
      builder: {
        // Cache build output between runs, to speed up subsequent startup times
        fsCache: true,
        // lazyCompilation breaks Storybook when running from within Docker
        // Google Translate this page for context: https://zenn.dev/yutaosawa/scraps/7764e5f17173d1
        lazyCompilation: false,
      },
    },
  },

  core: {
    disableTelemetry: true,
  },

  staticDirs: ["../public"],

  // Support deploying Storybook to a subdirectory (like GitHub Pages).
  // This makes `process.env.NEXT_PUBLIC_BASE_PATH` available to our source code.
  env: (config) => ({
    ...config,
    NEXT_PUBLIC_BASE_PATH,
  }),

  managerHead: blockSearchEnginesInHead,

  docs: {},

  typescript: {
    reactDocgen: "react-docgen-typescript",
  },
};
export default config;
