import { TFn } from "src/types/intl";

function mockUseTranslations(translationKey: string) {
  return translationKey;
}

mockUseTranslations.rich = (translationKey: string) => translationKey;

export function useTranslationsMock() {
  return mockUseTranslations as TFn;
}

export const localeParams = new Promise<{ locale: string }>((resolve) => {
  resolve({ locale: "en" });
});

// mocking all types of messages, could split by message type in the future
export const mockMessages = {
  Process: {
    intro: {
      boxes: ["firstKey"],
    },
    progress: {
      list: [
        {
          title: "test title",
          content: "test content",
        },
      ],
    },
    next: {
      list: [
        {
          title: "test title",
          content: "test content",
        },
      ],
    },
  },
  Research: {
    impact: {
      boxes: ["firstKey"],
    },
  },
};
