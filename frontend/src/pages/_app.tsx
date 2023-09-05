import { PUBLIC_ENV } from "src/constants/environments";

import { appWithTranslation } from "next-i18next";
import type { AppProps } from "next/app";
import Head from "next/head";
import Script from "next/script";

import Layout from "../components/Layout";

import "../styles/styles.scss";

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <link
          rel="icon"
          href={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/img/logo.svg`}
        />
      </Head>
      <Script id="google-tag-manager">
        {`
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl+ '&gtm_auth=${PUBLIC_ENV.GTM_AUTH}&gtm_preview=${PUBLIC_ENV.GTM_PREVIEW}&gtm_cookies_win=x';f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','${PUBLIC_ENV.GOOGLE_ANALYTICS_ID}');
      `}
      </Script>

      <Layout>
        <noscript
          id="gtm-iframe"
          dangerouslySetInnerHTML={{
            __html: `<iframe src="https://www.googletagmanager.com/ns.html?id=${PUBLIC_ENV.GOOGLE_ANALYTICS_ID}&gtm_auth=${PUBLIC_ENV.GTM_AUTH}&gtm_preview=${PUBLIC_ENV.GTM_PREVIEW}&gtm_cookies_win=x"
            height="0" width="0" style="display:none;visibility:hidden" />`,
          }}
        />
        <Component {...pageProps} />
      </Layout>
    </>
  );
}

export default appWithTranslation(MyApp);
