import { GoogleAnalytics } from "@next/third-parties/google";
import * as newrelic from "newrelic";
/**
 * Root layout component, wraps all pages.
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/layout
 */
import { Metadata } from "next";
import { environment } from "src/constants/environments";

import Script from "next/script";

import "src/styles/styles.scss";

import { NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";

import Layout from "src/components/Layout";

export const metadata: Metadata = {
  icons: [`${environment.NEXT_PUBLIC_BASE_PATH}/img/favicon.ico`],
};

interface Props {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

type NRType = typeof newrelic;

// see https://github.com/newrelic/node-newrelic/blob/40aea36320d15b201800431268be2c3d4c794a7b/api.js#L752
// types library does not expose a type for the options here, so building from scratch
interface typedGetBrowserTimingHeaderOptions {
  nonce?: string;
  hasToRemoveScriptWrapper?: boolean;
  allowTransactionlessInjection?: boolean; // tho jsdoc in nr code types this as "options"
}

interface NewRelicWithCorrectTypes extends NRType {
  agent: {
    collector: {
      isConnected: () => boolean;
    };
    on: (event: string, callback: (value: unknown) => void) => void;
  };
  getBrowserTimingHeader: (
    options?: typedGetBrowserTimingHeaderOptions,
  ) => string;
}

const locales = ["en", "es"];

const typedNewRelic = newrelic as NewRelicWithCorrectTypes;

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;
  // Enable static rendering
  setRequestLocale(locale);

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();

  // see https://github.com/newrelic/newrelic-node-examples/blob/58f760e828c45d90391bda3f66764d4420ba4990/nextjs-app-router/app/layout.js
  if (typedNewRelic?.agent?.collector?.isConnected() === false) {
    await new Promise((resolve) => {
      typedNewRelic.agent.on("connected", resolve);
    });
  }

  const browserTimingHeader = typedNewRelic
    ? typedNewRelic.getBrowserTimingHeader({
        hasToRemoveScriptWrapper: true,
        allowTransactionlessInjection: true,
      })
    : "";

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <GoogleAnalytics gaId={environment.GOOGLE_TAG_MANAGER_ID} />
        <meta
          name="google-site-verification"
          content="jFShzxCTiLzv8gvEW4ft7fCaQkluH229-B-tJKteYJY"
        />
      </head>
      <body>
        <NextIntlClientProvider messages={messages}>
          <Layout locale={locale}>{children}</Layout>
        </NextIntlClientProvider>
        <Script
          id="nr-browser-agent"
          // By setting the strategy to "beforeInteractive" we guarantee that
          // the script will be added to the document's `head` element.
          // However, we cannot add this because it needs to be in the Root Layout, outside of the [locale] directory
          // And we cannot add beneath the local directory because our HTML tag needs to know about the locale
          // Come back to this to see if we can find a solution later on
          // strategy="beforeInteractive"

          dangerouslySetInnerHTML={{ __html: browserTimingHeader }}
        />
      </body>
    </html>
  );
}
