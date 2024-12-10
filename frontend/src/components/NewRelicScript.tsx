"use client";

import staticNewRelicScript from "src/constants/newRelicScript";

import Script from "next/script";

type NewRelicScriptProps = {
  accountID: string;
  trustKey: string;
  agentID: string;
  licenseKey: string;
  applicationID: string;
};

export default function NewRelicScript({
  accountID,
  trustKey,
  agentID,
  licenseKey,
  applicationID,
}: NewRelicScriptProps) {
  const dynamicNewRelicScript = `;window.NREUM||(NREUM={});NREUM.init={distributed_tracing:{enabled:true},privacy:{cookies_enabled:true}};
  ;NREUM.loader_config={accountID:"${accountID}",trustKey:"${trustKey}",agentID:"${agentID}",licenseKey:"${licenseKey}",applicationID:"${applicationID}"};
  ;NREUM.info={beacon:"bam.nr-data.net",errorBeacon:"bam.nr-data.net",licenseKey:"${licenseKey}",applicationID:"${applicationID}",sa:1};`;

  return (
    <Script
      id="nr-browser-agent"
      // By setting the strategy to "beforeInteractive" we guarantee that
      // the script will be added to the document's `head` element.
      // However, we cannot add this because it needs to be in the Root Layout, outside of the [locale] directory
      // And we cannot add beneath the local directory because our HTML tag needs to know about the locale
      // Come back to this to see if we can find a solution later on
      strategy="beforeInteractive"
      dangerouslySetInnerHTML={{
        __html: dynamicNewRelicScript + staticNewRelicScript,
      }}
    />
  );
}
