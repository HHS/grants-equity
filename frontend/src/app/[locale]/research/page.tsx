import { Metadata } from "next";
import ResearchArchetypes from "src/app/[locale]/research/ResearchArchetypes";
import ResearchImpact from "src/app/[locale]/research/ResearchImpact";
import ResearchIntro from "src/app/[locale]/research/ResearchIntro";
import ResearchMethodology from "src/app/[locale]/research/ResearchMethodology";
import ResearchThemes from "src/app/[locale]/research/ResearchThemes";
import { RESEARCH_CRUMBS } from "src/constants/breadcrumbs";
import { LocalizedPageProps } from "src/types/intl";

import { getTranslations, setRequestLocale } from "next-intl/server";

import BetaAlert from "src/components/BetaAlert";
import Breadcrumbs from "src/components/Breadcrumbs";

export async function generateMetadata({
  params: { locale },
}: LocalizedPageProps) {
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("Research.page_title"),
    description: t("Research.meta_description"),
  };
  return meta;
}

export default function Research({ params: { locale } }: LocalizedPageProps) {
  setRequestLocale(locale);
  return (
    <>
      <BetaAlert containerClasses="margin-top-5" />
      <Breadcrumbs breadcrumbList={RESEARCH_CRUMBS} />
      <ResearchIntro />
      <ResearchMethodology />
      <div className="padding-top-4 bg-base-lightest">
        <ResearchArchetypes />
        <ResearchThemes />
      </div>
      <ResearchImpact />
    </>
  );
}
