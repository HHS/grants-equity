import { ExternalRoutes } from "src/constants/routes";

import { useMessages, useTranslations } from "next-intl";
import Link from "next/link";
import { ReactNode } from "react";
import {
  Grid,
  GridContainer,
  IconList,
  IconListContent,
  IconListIcon,
  IconListItem,
} from "@trussworks/react-uswds";

import { USWDSIcon } from "src/components/USWDSIcon";

const GithubIssueLink = ({
  issueNumber,
  chunks,
}: {
  issueNumber: number;
  chunks: ReactNode;
}) => (
  <Link
    target="_blank"
    className="usa-link--external text-bold"
    href={`${ExternalRoutes.GITHUB_REPO}/issues/${issueNumber}`}
  >
    {chunks}
  </Link>
);

export const gitHubLinkForIssue = (issueNumber: number) => {
  const PartialIssueLink = (chunks: ReactNode) => (
    <GithubIssueLink issueNumber={issueNumber} chunks={chunks} />
  );
  PartialIssueLink.displayName = "GithubIssueLink";
  return PartialIssueLink;
};

const ProcessNext = () => {
  const t = useTranslations("Process.next");
  const messages = useMessages() as unknown as IntlMessages;

  const keys = Object.keys(messages.Process.next.list);

  return (
    <GridContainer className="grid-container padding-y-1 tablet:padding-y-3 desktop-lg:padding-y-6 padding-top-0 tablet:padding-top-0 desktop-lg:padding-top-0">
      <h2 className="margin-bottom-0 tablet-lg:font-sans-l desktop-lg:font-sans-xl margin-top-0">
        {t("title")}
      </h2>
      <Grid row gap>
        <Grid className="tablet:grid-col">
          <IconList className="usa-icon-list--size-md grid-row">
            {keys.map((key) => {
              const title = t(`list.${key}.title`);
              const content = t.rich(`list.${key}.content`, {
                p: (chunks) => (
                  <p className="font-sans-md line-height-sans-4 desktop-lg:line-height-sans-6">
                    {chunks}
                  </p>
                ),
                linkGithub3045: gitHubLinkForIssue(3045),
                linkGithub2875: gitHubLinkForIssue(2875),
                linkGithub2640: gitHubLinkForIssue(2640),
                linkGithub3348: gitHubLinkForIssue(3348),
              });
              return (
                <IconListItem
                  key={title + "-key"}
                  className="margin-top-4 tablet-lg:grid-col-6"
                >
                  <IconListIcon>
                    <USWDSIcon
                      className="text-base"
                      name="check_circle_outline"
                    />
                  </IconListIcon>
                  <IconListContent className="tablet:padding-right-7">
                    <h3 className="margin-bottom-2 usa-icon-list__title">
                      {title}
                    </h3>
                    <div className="font-sans-md line-height-sans-4 desktop-lg:line-height-sans-6">
                      {content}
                    </div>
                  </IconListContent>
                </IconListItem>
              );
            })}
          </IconList>
          <h3>
            <Link
              target="_blank"
              className="usa-link--external"
              href={`${ExternalRoutes.GITHUB_REPO}/issues?q=is%3Aissue%20type%3ADeliverable%20`}
            >
              {t("link")}
            </Link>
          </h3>
        </Grid>
      </Grid>
    </GridContainer>
  );
};

export default ProcessNext;
