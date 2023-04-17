export function buildURL(...path) {
  return [API_URL_BASE ?? document.location, ...path].reduce(
    (acc, segment) => new URL(segment, acc)
  );
}
