import { getConfiguredDayJs } from "src/utils/dateUtil";

import { ReadonlyURLSearchParams } from "next/navigation";

// downloads csv, then blobs it out to allow browser to download it
// note that this could be handled by just pointing the browser location at the URL
// but we'd lose any ability for graceful error handling that way
export const downloadSearchResultsCSV = async (
  searchParams: ReadonlyURLSearchParams,
) => {
  try {
    const response = await fetch(
      `/api/search/export?${searchParams.toString()}`,
    );

    if (!response.ok) {
      throw new Error(`Unsuccessful csv download. ${response.status}`);
    }
    const csvBlob = await response.blob();
    location.assign(
      URL.createObjectURL(
        new File(
          [csvBlob],
          `grants-search-${getConfiguredDayJs()(new Date()).format("YYYYMMDDHHmm")}.csv`,
          {
            type: "data:text/csv",
          },
        ),
      ),
    );
  } catch (e) {
    console.error(e);
  }
};
