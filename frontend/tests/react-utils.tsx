/**
 * @file Exposes all of @testing-library/react, with one exception:
 * the exported render function is wrapped in a custom wrapper so
 * tests render within a global context that includes i18n content
 * @see https://testing-library.com/docs/react-testing-library/setup#custom-render
 */
import { render as _render, RenderOptions } from "@testing-library/react";
import { defaultLocale, formats, timeZone } from "src/i18n/config";
import { messages } from "src/i18n/messages/en";

import { NextIntlClientProvider } from "next-intl";

/**
 * Wrapper component that provides global context to all tests. Notably,
 * it allows our tests to render content when using i18n translation methods.
 *
 * Note that this functionality does not work when testing page components, use original
 * testing methods in that case.
 */
const GlobalProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <NextIntlClientProvider
      formats={formats}
      timeZone={timeZone}
      locale={defaultLocale}
      // @ts-expect-error messages
      messages={messages}
    >
      {children}
    </NextIntlClientProvider>
  );
};

// 1. Export everything in "@testing-library/react" as-is
// eslint-disable-next-line import/export
export * from "@testing-library/react";

// 2. Then override the "@testing-library/react" render method
// eslint-disable-next-line import/export
export function render(
  ui: React.ReactElement,
  options: Omit<RenderOptions, "wrapper"> = {},
) {
  return _render(ui, { wrapper: GlobalProviders, ...options });
}
