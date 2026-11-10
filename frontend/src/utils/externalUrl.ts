export function validExternalHttpUrl(value: string | null | undefined) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return (url.protocol === "http:" || url.protocol === "https:") &&
      url.hostname
      ? url.href
      : null;
  } catch {
    return null;
  }
}
