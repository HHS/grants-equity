"use client";

import { useGlobalState } from "src/services/globalState/GlobalStateProvider";
import { Opportunity } from "src/types/search/searchResponseTypes";
import { formatDate } from "src/utils/dateUtil";
import { lookUpAgencyName } from "src/utils/search/searchUtils";

import { useTranslations } from "next-intl";
import Link from "next/link";

interface SearchResultsListItemProps {
  opportunity: Opportunity;
}

const metadataBorderClasses = `
  display-block
  tablet:display-inline-block
  tablet:border-left-1px
  tablet:padding-x-1
  tablet:margin-left-neg-1
  tablet:margin-right-1
  tablet:border-base-lighter
  `;

const resultBorderClasses = `
  border-1px
  border-base-lighter
  padding-x-2
  padding-y-105
  margin-bottom-2
  text-base-darker
  `;

export default function SearchResultsListItem({
  opportunity,
}: SearchResultsListItemProps) {
  const t = useTranslations("Search");
  const { flattenedAgencyOptions } = useGlobalState(
    ({ flattenedAgencyOptions }) => ({
      flattenedAgencyOptions,
    }),
  );
  return (
    <div className={resultBorderClasses}>
      <div className="grid-row grid-gap">
        <div className="desktop:grid-col-fill">
          <div className="grid-row flex-column">
            <div className="grid-col tablet:order-2">
              <h2 className="margin-y-105 line-height-sans-2">
                <Link
                  href={`/opportunity/${opportunity?.opportunity_id}`}
                  className="usa-link usa-link"
                >
                  {opportunity?.opportunity_title}
                </Link>
              </h2>
            </div>
            <div className="grid-col tablet:order-1 overflow-hidden font-body-xs">
              {opportunity.opportunity_status === "archived" && (
                <span className={metadataBorderClasses}>
                  <strong>{t("resultsListItem.status.archived")}</strong>
                  {opportunity?.summary?.archive_date
                    ? formatDate(opportunity?.summary?.archive_date)
                    : "--"}
                </span>
              )}
              {(opportunity?.opportunity_status === "archived" ||
                opportunity?.opportunity_status === "closed") &&
                opportunity?.summary?.close_date && (
                  <span className={metadataBorderClasses}>
                    <strong>{t("resultsListItem.status.closed")}</strong>
                    {opportunity?.summary?.close_date
                      ? formatDate(opportunity?.summary?.close_date)
                      : "--"}
                  </span>
                )}
              {opportunity?.opportunity_status === "posted" && (
                <span className={metadataBorderClasses}>
                  <span className="usa-tag bg-accent-warm-dark">
                    <strong>{t("resultsListItem.status.posted")}</strong>
                    <span className="text-no-uppercase">
                      {opportunity?.summary?.close_date
                        ? formatDate(opportunity?.summary?.close_date)
                        : "--"}
                    </span>
                  </span>
                </span>
              )}
              {opportunity?.opportunity_status === "forecasted" && (
                <span className={metadataBorderClasses}>
                  <span className="usa-tag">
                    <strong>{t("resultsListItem.status.forecasted")}</strong>
                  </span>
                </span>
              )}
              <span className={metadataBorderClasses}>
                <strong>{t("resultsListItem.summary.posted")}</strong>
                {opportunity?.summary?.post_date
                  ? formatDate(opportunity?.summary?.post_date)
                  : "--"}
              </span>
            </div>
            <div className="grid-col tablet:order-3 overflow-hidden font-body-xs">
              <span className={metadataBorderClasses}>
                <strong>{t("resultsListItem.summary.agency")}</strong>
                {lookUpAgencyName(opportunity, flattenedAgencyOptions)}
              </span>
              <span className={metadataBorderClasses}>
                <strong>{t("resultsListItem.opportunity_number")}</strong>
                {opportunity?.opportunity_number}
              </span>
            </div>
          </div>
        </div>
        <div className="desktop:grid-col-auto">
          <div className="overflow-hidden font-body-xs">
            {/* TODO: Better way to format as a dollar amounts */}
            <span
              className={`${metadataBorderClasses} desktop:display-block text-right desktop:margin-right-0 desktop:padding-right-0`}
            >
              <strong>{t("resultsListItem.award_ceiling")}</strong>
              <span className="desktop:display-block desktop:font-sans-lg text-ls-neg-3 text-right">
                ${opportunity?.summary?.award_ceiling?.toLocaleString() || "--"}
              </span>
            </span>
            <span
              className={`${metadataBorderClasses} desktop:display-block text-right desktop:margin-right-0 desktop:padding-right-0`}
            >
              <strong>{t("resultsListItem.floor")}</strong>
              {opportunity?.summary?.award_floor?.toLocaleString() || "--"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
