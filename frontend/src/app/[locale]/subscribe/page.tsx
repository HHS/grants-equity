import { Metadata } from "next";
import { SUBSCRIBE_CRUMBS } from "src/constants/breadcrumbs";
import { LocalizedPageProps } from "src/types/intl";

import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { use } from "react";
import { Grid, GridContainer } from "@trussworks/react-uswds";

import BetaAlert from "src/components/BetaAlert";
import Breadcrumbs from "src/components/Breadcrumbs";
import SubscriptionForm from "src/components/subscribe/SubscriptionForm";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("Subscribe.page_title"),
    description: t("Subscribe.meta_description"),
  };

  return meta;
}

export default function Subscribe({ params }: LocalizedPageProps) {
  const { locale } = use(params);
  setRequestLocale(locale);
  const t = useTranslations("Subscribe");

  return (
    <>
      <BetaAlert containerClasses="margin-top-5" />
      <Breadcrumbs breadcrumbList={SUBSCRIBE_CRUMBS} />

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
            {t.rich("list", {
              ul: (chunks) => (
                <ul className="usa-list margin-top-0 tablet-lg:margin-top-3 font-sans-md line-height-sans-4">
                  {chunks}
                </ul>
              ),
              li: (chunks) => <li>{chunks}</li>,
            })}
          </Grid>
          <Grid tabletLg={{ col: 6 }}>
            <SubscriptionForm />
          </Grid>
        </Grid>
      </GridContainer>
      <GridContainer className="padding-bottom-5 tablet:padding-top-3 desktop-lg:padding-top-3">
        <p className="font-sans-3xs text-base-dark">{t("disclaimer")}</p>
      </GridContainer>
    </>
  );
}
