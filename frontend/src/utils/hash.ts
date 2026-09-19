export function shortHash(value?: string | null): string {
  return value ? `${value.slice(0, 8)}…${value.slice(-6)}` : '—';
}
