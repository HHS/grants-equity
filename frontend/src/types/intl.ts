import type { useTranslations } from "next-intl";
import type { getTranslations } from "next-intl/server";

export type TFn =
  | ReturnType<typeof useTranslations<never>>
  | Awaited<ReturnType<typeof getTranslations<never>>>;

export type LocalizedPageProps = { params: Promise<{ locale: string }> };
