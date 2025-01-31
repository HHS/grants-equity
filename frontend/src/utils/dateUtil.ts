import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(timezone);
dayjs.extend(advancedFormat);

// Convert "2024-02-21" to "February 21, 2024"
export function formatDate(dateStr: string | null): string {
  if (!dateStr || dateStr.length !== 10) {
    console.warn("invalid date string provided for parse");
    return "";
  }

  const parts = dateStr.split("-");

  if (parts.length !== 3) {
    console.warn("invalid date string provided for parse");
    return "";
  }

  const [year, month, day] = parts.map(Number);
  // Create a new Date object using the local time
  const date = new Date(year, month - 1, day);

  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  return date.toLocaleDateString("en-US", options);
}

export const getConfiguredDayJs = () => dayjs;
