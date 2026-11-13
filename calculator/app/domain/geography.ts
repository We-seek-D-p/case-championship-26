import type { Airport } from './data'
export function distance(a: Airport, b: Airport) {
  const r = Math.PI / 180,
    p = a.latitude * r,
    q = b.latitude * r,
    d = (b.longitude - a.longitude) * r
  return (
    6371 *
    2 *
    Math.asin(
      Math.min(
        1,
        Math.sqrt(Math.sin((q - p) / 2) ** 2 + Math.cos(p) * Math.cos(q) * Math.sin(d / 2) ** 2),
      ),
    )
  )
}
export function arc(a: Airport, b: Airport): number[][] {
  const vector = (p: Airport) => {
    const t = (p.latitude * Math.PI) / 180,
      l = (p.longitude * Math.PI) / 180
    return [Math.cos(t) * Math.cos(l), Math.cos(t) * Math.sin(l), Math.sin(t)]
  }
  const u = vector(a),
    v = vector(b),
    angle = distance(a, b) / 6371
  let previous = a.longitude
  return Array.from({ length: 65 }, (_, i) => {
    const t = i / 64,
      s = Math.sin(angle)
    const k = s < 1e-8 ? 1 - t : Math.sin((1 - t) * angle) / s,
      h = s < 1e-8 ? t : Math.sin(t * angle) / s
    const x = (u[0] ?? 0) * k + (v[0] ?? 0) * h,
      y = (u[1] ?? 0) * k + (v[1] ?? 0) * h,
      z = (u[2] ?? 0) * k + (v[2] ?? 0) * h
    let lon = (Math.atan2(y, x) * 180) / Math.PI
    while (lon - previous > 180) lon -= 360
    while (lon - previous < -180) lon += 360
    previous = lon
    return [lon, (Math.atan2(z, Math.hypot(x, y)) * 180) / Math.PI]
  })
}
