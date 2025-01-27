import { Metadata } from "next";
import { SUBSCRIBE_CONFIRMATION_CRUMBS } from "src/constants/breadcrumbs";
import { LocalizedPageProps } from "src/types/intl";

import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import Link from "next/link";
import { use } from "react";
import { Grid, GridContainer } from "@trussworks/react-uswds";

import BetaAlert from "src/components/BetaAlert";
import Breadcrumbs from "src/components/Breadcrumbs";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("Subscribe.page_title"),
    description: t("Index.meta_description"),
  };

  return meta;
}

export default function SubscriptionConfirmation({
  params,
}: LocalizedPageProps) {
  const { locale } = use(params);
  setRequestLocale(locale);
  const t = useTranslations("Subscription_confirmation");

  return (
    <>
      <BetaAlert />
      <Breadcrumbs breadcrumbList={SUBSCRIBE_CONFIRMATION_CRUMBS} />

      <GridContainer className="padding-bottom-5 tablet:padding-top-0 desktop-lg:padding-top-0 border-bottom-2px border-base-lightest">
        <h1 className="margin-0 tablet-lg:font-sans-xl desktop-lg:font-sans-2xl">
          {t("title")}
        </h1>
        <p className="usa-intro font-sans-md tablet:font-sans-lg desktop-lg:font-sans-xl margin-bottom-0">
          {t("intro")}
        </p>
        <Grid row gap className="flex-align-start">
          <Grid tabletLg={{ col: 6 }}>
            <p className="usa-intro">{t("paragraph_1")}</p>
          </Grid>
          <Grid tabletLg={{ col: 6 }}>
            <h2 className="tablet-lg:font-sans-lg tablet-lg:margin-bottom-05">
              {t("heading")}
            </h2>
            <p className="margin-top-0 font-sans-md line-height-sans-4 desktop-lg:line-height-sans-6">
              {t.rich("paragraph_2", {
                strong: (chunks) => <strong>{chunks}</strong>,
                "process-link": (chunks) => (
                  <Link href="/process">{chunks}</Link>
                ),
                "research-link": (chunks) => (
                  <Link href="/research">{chunks}</Link>
                ),
              })}
            </p>
          </Grid>
        </Grid>
      </GridContainer>
      <GridContainer className="padding-bottom-5 tablet:padding-top-3 desktop-lg:padding-top-3">
        <p className="font-sans-3xs text-base-dark">{t("disclaimer")}</p>
      </GridContainer>
    </>
  );
}
