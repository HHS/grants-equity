import { getConfiguredDayJs } from "src/utils/dateUtil";

import { useTranslations } from "next-intl";
import { Link, Table } from "@trussworks/react-uswds";

interface OpportunityDocument {
  opportunity_attachment_type: string;
  file_name: string;
  download_path: string;
  updated_at: string;
}

interface OpportunityDocumentsProps {
  documents: OpportunityDocument[];
}

const DocumentTable = ({ documents }: OpportunityDocumentsProps) => {
  const t = useTranslations("OpportunityListing.documents");

  return (
    <>
      <thead>
        <tr>
          <th scope="col">{t("table_col_category")}</th>
          <th scope="col">{t("table_col_file_name")}</th>
          <th scope="col">{t("table_col_last_updated")}</th>
        </tr>
      </thead>
      <tbody>
        {documents.map((document, index) => (
          <tr key={index}>
            <th data-label={t("table_col_category")} scope="row">
              {document.opportunity_attachment_type ===
              "notice_of_funding_opportunity"
                ? t("type.funding_details")
                : t("type.other")}
            </th>
            <td data-label={t("table_col_file_name")}>
              <Link target="_blank" href={document.download_path}>
                {document.file_name}
              </Link>
            </td>
            <td data-label={t("table_col_last_updated")}>
              {/* https://day.js.org/docs/en/display/format */}
              {getConfiguredDayJs()(document.updated_at).format(
                "MMM D, YYYY hh:mm A z",
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </>
  );
};

const OpportunityDocuments = ({ documents }: OpportunityDocumentsProps) => {
  const t = useTranslations("OpportunityListing.documents");

  return (
    <>
      <h2 id="opportunity_documents">{t("title")}</h2>
      {documents.length > 0 ? (
        <Table>
          <DocumentTable documents={documents} />
        </Table>
      ) : (
        <p>--</p>
      )}
    </>
  );
};

export default OpportunityDocuments;
