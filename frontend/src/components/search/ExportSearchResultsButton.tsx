"use client";

import { downloadSearchResultsCSV } from "src/services/fetch/fetchers/clientSearchResultsDownloadFetcher";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { Button } from "@trussworks/react-uswds";

import { USWDSIcon } from "src/components/USWDSIcon";

export function ExportSearchResultsButton() {
  const t = useTranslations("Search.exportButton");
  const searchParams = useSearchParams();

  const downloadSearchResults = useCallback(() => {
    // catch included here to satisfy linter
    downloadSearchResultsCSV(searchParams).catch((e) => {
      throw e;
    });
  }, [searchParams]);

  return (
    <div
      className="desktop:grid-col-4 desktop:display-flex flex-align-self-center"
      data-testid="search-download-button-container"
    >
      <Button
        outline={true}
        type={"submit"}
        className="width-auto margin-top-2 tablet:width-100 tablet-lg:margin-top-0"
        onClick={downloadSearchResults}
      >
        <USWDSIcon name="file_download" className="usa-icon--size-3" />
        {t("title")}
      </Button>
    </div>
  );
}
