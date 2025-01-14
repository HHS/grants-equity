import { Metadata } from "next";
import { LocalizedPageProps } from "src/types/intl";

import { getTranslations } from "next-intl/server";
import { notFound } from "next/navigation";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("ErrorPages.page_not_found.title"),
    description: t("Index.meta_description"),
  };
  return meta;
}

export default function NotFoundDummy() {
  notFound();
}
