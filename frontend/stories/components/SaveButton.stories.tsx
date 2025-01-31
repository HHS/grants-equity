import { Meta } from "@storybook/react";

import SaveButton from "src/components/SaveButton";

const meta: Meta<typeof SaveButton> = {
  title: "Components/SaveButton",
  component: SaveButton,
  args: {
    defaultText: "Save",
    savedText: "Saved",
    loadingText: "Updating",
  },
};
export default meta;

export const Default = {};
