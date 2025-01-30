"use client";

import { useUser } from "src/services/auth/useUser";

import { useTranslations } from "next-intl";
import SaveButton from "src/components/SaveButton";

export const OpportunitySaveUserControl = () => {
  const t = useTranslations("OpportunityListingLoginModal");

  const { user } = useUser();

  return (
    <>
      {!user?.token && (
        <SaveButton
        defaultText={t("title")}
        savedText="Saved"
        loadingText="Updating"
        saved
        loading
      />
      )}
      {!!user?.token && (
        <SaveButton
          defaultText="Save"
          savedText="Saved"
          loadingText="Updating"
          saved
          loading
        />
      )}
    </>
  );
};
