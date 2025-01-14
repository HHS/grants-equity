import { LocalizedPageProps } from "src/types/intl";

import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { use } from "react";
import { GridContainer } from "@trussworks/react-uswds";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });

  return {
    title: t("Maintenance.pageTitle"),
    description: t("Maintenance.heading"),
  };
}

export default function Maintenance({ params }: LocalizedPageProps) {
  const { locale } = use(params);
  setRequestLocale(locale);
  const t = useTranslations("Maintenance");

  const body = t.rich("body", {
    LinkToGrants: (content) => <a href="https://www.grants.gov">{content}</a>,
  });

  return (
    <GridContainer className="padding-y-1 tablet:padding-y-3 desktop-lg:padding-y-6 padding-x-5 tablet:padding-x-7 desktop-lg:padding-x-10 text-center">
      <h2 className="margin-bottom-0">{t("heading")}</h2>
      <p>{body}</p>
      <p>{t("signOff")}</p>
    </GridContainer>
  );
}
