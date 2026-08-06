import { useEffect, useState } from "react"

/**
 * Subscribe to a CSS media query and return whether it currently matches.
 * Used for responsive behavior that Tailwind classes can't express
 * (e.g. locking the sidebar open on first paint).
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === "undefined") return false
    return window.matchMedia(query).matches
  })

  useEffect(() => {
    const media = window.matchMedia(query)
    const onChange = () => setMatches(media.matches)
    onChange()
    media.addEventListener("change", onChange)
    return () => media.removeEventListener("change", onChange)
  }, [query])

  return matches
}
