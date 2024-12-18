import { useTranslations } from "next-intl";

import FullWidthAlert from "./FullWidthAlert";

const BetaAlert = () => {
  const t = useTranslations("Beta_alert");
  const alert = t.rich("alert", {
    LinkToGrants: (content) => <a href="https://www.grants.gov">{content}</a>,
  });

  return (
    <div data-testid="beta-alert">
      <FullWidthAlert type="info" heading={t("alert_title")}>
        {alert}
      </FullWidthAlert>
    </div>
  );
};

export default BetaAlert;
