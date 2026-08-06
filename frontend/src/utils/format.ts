/** Presentation formatting helpers. Pure functions only. */

/** Format a byte count for humans (e.g. "1.4 MB"). */
export function formatBytes(bytes: number | undefined): string {
  if (bytes === undefined || bytes < 0 || !Number.isFinite(bytes)) return "—"
  if (bytes === 0) return "0 B"
  const units = ["B", "KB", "MB", "GB", "TB"]
  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  )
  const value = bytes / 1024 ** index
  return `${value.toFixed(value >= 100 || index === 0 ? 0 : 1)} ${units[index]}`
}

/** Format an ISO timestamp as a compact clock time (UTC). */
export function formatTime(iso: string | undefined): string {
  if (!iso) return "—"
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return "—"
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })
}

/** Short relative time ("3m ago") for feed entries. */
export function timeAgo(iso: string | undefined): string {
  if (!iso) return "—"
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return "—"
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000))
  if (seconds < 5) return "now"
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

/** Uppercase an enum-ish string ("security_officer" → "Security Officer"). */
export function humanize(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
}
