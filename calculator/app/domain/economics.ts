import type { Airport } from './data'
import { profiles } from './data'
import type { Scenario } from './scenario'
import { distance } from './geography'
export function calculate(s: Scenario, airports: Airport[], axisLF?: number) {
  const base = airports.find((a) => a.airport_iata === s.base)
  const rows = s.routes
    .filter((r) => r.enabled && r.destination !== s.base)
    .map((r) => {
      const dest = airports.find((a) => a.airport_iata === r.destination),
        km = base && dest ? distance(base, dest) : 0,
        ssj = r.type === 'SSJ100'
      const bh = r.bh ?? (ssj ? 0.45 + km / 650 : null),
        cost = r.cost ?? (ssj && bh !== null ? 110000 + 120000 * bh : null)
      const fare = (r.fare ?? 7000 + 3.5 * km) * s.tariff * (s.transfers ? 1 - s.discount : 1),
        legs = 2 * r.frequency * s.weeks,
        capacity = legs * (r.seats ?? 0),
        p = Math.min(
          capacity * (axisLF ?? r.lf ?? s.lf),
          r.od === null ? Infinity : r.od * r.capture,
        )
      const revenue = p * (fare + s.ancillary),
        variable = cost === null ? null : legs * cost * s.expense + p * s.passengerCost,
        lostP = p * s.cannibalization,
        lostCM = lostP * s.lostMargin
      const range = profiles.find((p) => p.id === r.type)?.range
      return {
        ...r,
        km,
        bh,
        cost,
        fare,
        legs,
        capacity,
        p,
        revenue,
        variable,
        lostP,
        lostCM,
        hours: bh === null ? null : legs * bh,
        contribution: variable === null ? null : revenue - variable - lostCM,
        warning:
          range && km > range
            ? 'Превышен справочный радиус'
            : km < 600 || km > 2200
              ? 'Вне диапазона теста gg'
              : '',
      }
    })
  const sum = (f: (r: (typeof rows)[number]) => number) => rows.reduce((a, r) => a + f(r), 0)
  const fleet = s.fleet.map((f) => {
    const rs = rows.filter((r) => r.type === f.type),
      hours = rs.reduce((a, r) => a + (r.hours ?? 0), 0),
      required = !rs.some((r) => r.legs > 0)
        ? 0
        : f.resource && f.resource > 0
          ? Math.max(
              Math.ceil(hours / ((f.resource * s.weeks) / 52)),
              rs.some((r) => r.legs > 0) ? f.peak : 0,
            )
          : null
    return {
      ...f,
      hours,
      required,
      deficit:
        required === null
          ? null
          : Math.max(0, required - f.working, f.working + f.reserve - f.available),
      hourDeficit:
        f.resource === null ? null : Math.max(0, hours - (f.working * f.resource * s.weeks) / 52),
    }
  })
  const complete =
    rows.every(
      (r) =>
        r.legs === 0 ||
        (r.variable !== null &&
          r.hours !== null &&
          r.seats !== null &&
          s.fleet.some((f) => f.type === r.type)),
    ) &&
    fleet.every(
      (f) =>
        (f.working + f.reserve === 0 || f.fixed !== null) &&
        (!rows.some((r) => r.type === f.type && r.legs > 0) || f.resource !== null),
    )
  const fixed =
    ((fleet.reduce((a, f) => a + (f.working + f.reserve) * (f.fixed ?? 0), 0) +
      s.baseCost +
      s.personnel +
      s.infrastructure) *
      s.weeks) /
    52
  const revenue = sum((r) => r.revenue),
    variable = sum((r) => r.variable ?? 0),
    lostCM = sum((r) => r.lostCM),
    p = sum((r) => r.p),
    legs = sum((r) => r.legs),
    capacity = sum((r) => r.capacity),
    net = p - sum((r) => r.lostP) - s.displacedP
  const passenger = complete ? revenue - variable - lostCM - s.displacedCM - fixed : null
  const kg = legs * Math.min(s.cargo.kg, s.cargo.limit ?? Infinity),
    cargo = s.cargo.enabled
      ? kg * (s.cargo.tariff * (1 - s.cargo.commission) - s.cargo.handling - s.cargo.weight) -
        s.cargo.fixed
      : 0
  const result = passenger === null ? null : passenger + cargo
  return {
    rows: rows.map((r) => ({
      ...r,
      fixed: capacity > 0 ? (fixed * r.capacity) / capacity : 0,
      result:
        r.contribution === null
          ? null
          : r.contribution - (capacity > 0 ? (fixed * r.capacity) / capacity : 0),
    })),
    fleet,
    complete,
    fixed,
    revenue,
    variable,
    lostCM,
    p,
    net,
    legs,
    capacity,
    passenger,
    cargo,
    result,
    first: result === null ? null : result - s.launch,
    hours: sum((r) => r.hours ?? 0),
    share: (net / 108850000) * 100,
    transferSegments: s.transfers ? p * s.transferShare : 0,
    transferJourneys: s.transfers ? (p * s.transferShare) / 2 : 0,
    feasible: complete && fleet.every((f) => f.deficit === 0),
  }
}
export function breakEven(s: Scenario, a: Airport[]) {
  if (calculate(s, a, 1).result === null) return null
  if ((calculate(s, a, 0).result ?? 0) >= 0) return 0
  if ((calculate(s, a, 1).result ?? 0) < 0) return null
  let lo = 0,
    hi = 1
  for (let i = 0; i < 45; i++) {
    const mid = (lo + hi) / 2
    if ((calculate(s, a, mid).result ?? 0) >= 0) hi = mid
    else lo = mid
  }
  return hi
}
export function rotationCheck(s: Scenario, a: Airport[]) {
  const r = calculate(s, a)
  return (
    r.rows.length === 4 &&
    r.rows.every(
      (x) =>
        x.type === 'SSJ100' &&
        x.frequency === 4 &&
        x.bh !== null &&
        6 + 2 * x.bh + 0.75 + s.mct / 60 <= 14 &&
        14 + 2 * x.bh + 0.75 <= 22,
    )
  )
}
