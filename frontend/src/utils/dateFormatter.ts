/**
 * Format a date string to human-readable format
 * Example: "2025-01-01" -> "Jan 1st, 2025"
 * Example: "2025-12-25" -> "Dec 25th, 2025"
 */
export function formatDate(dateString: string): string {
  if (!dateString) return dateString;

  // Try to parse the date
  const date = new Date(dateString);

  // Check if it's a valid date
  if (isNaN(date.getTime())) {
    // If it's not a valid date, return the original string
    return dateString;
  }

  // Get month name
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];
  const month = months[date.getMonth()];

  // Get day with ordinal suffix
  const day = date.getDate();
  const ordinal = getOrdinalSuffix(day);

  // Get year
  const year = date.getFullYear();

  return `${month} ${day}${ordinal}, ${year}`;
}

/**
 * Get ordinal suffix for a number (1st, 2nd, 3rd, 4th, etc.)
 */
function getOrdinalSuffix(day: number): string {
  if (day > 3 && day < 21) return 'th';
  switch (day % 10) {
    case 1: return 'st';
    case 2: return 'nd';
    case 3: return 'rd';
    default: return 'th';
  }
}

/**
 * Format a value if it looks like a date
 * Detects common date patterns and formats them
 */
export function formatValueIfDate(key: string, value: any): string {
  if (typeof value !== 'string') return String(value);

  // Check if the key suggests this is a date field
  const dateKeywords = ['date', 'day', 'departure', 'arrival', 'check_in', 'check_out', 'return'];
  const isDateField = dateKeywords.some(keyword => key.toLowerCase().includes(keyword));

  if (!isDateField) return value;

  // Check if value matches date patterns (YYYY-MM-DD, YYYY/MM/DD, etc.)
  const datePattern = /^\d{4}[-/]\d{1,2}[-/]\d{1,2}$/;
  if (datePattern.test(value)) {
    return formatDate(value);
  }

  return value;
}
