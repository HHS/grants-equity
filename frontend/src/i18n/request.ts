import { defaultLocale, formats, locales, timeZone } from "src/i18n/config";
import { getMessagesWithFallbacks } from "src/i18n/getMessagesWithFallbacks";

import { getRequestConfig } from "next-intl/server";

/**
 * Make locale messages available to all server components.
 * This method is used behind the scenes by `next-intl/plugin`, which is setup in next.config.js.
 * @see https://next-intl-docs.vercel.app/docs/usage/configuration#nextconfigjs
 */

// @ts-expect-error TS2345: Argument of type error is expected behavior by next-intl maintainer: https://github.com/amannn/next-intl/issues/991#issuecomment-2050087509
export default getRequestConfig(async ({ requestLocale }) => {
  let locale = (await requestLocale) || "";

  const isValidLocale = locales.includes(locale); // https://github.com/microsoft/TypeScript/issues/26255
  if (!isValidLocale) {
    console.error(
      `Unsupported locale (${locale}) was requested. Falling back to the default locale.`,
    );
    locale = defaultLocale;
  }
  return {
    locale,
    formats,
    messages: await getMessagesWithFallbacks(locale),
    timeZone,
  };
});
