import { entetesAuthentifiees } from "@/lib/auth";

export function apiFetch(
  input: RequestInfo | URL,
  init: RequestInit = {}
) {
  const headers = new Headers(init.headers ?? {});
  const authHeaders = entetesAuthentifiees();

  Object.entries(authHeaders as Record<string, string>).forEach(
    ([key, value]) => {
      if (!headers.has(key)) {
        headers.set(key, value);
      }
    }
  );

  return fetch(input, {
    ...init,
    headers,
  });
}
