import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { parse } from 'csv-parse/sync'
import { z } from 'zod'
import { dataSchema, profiles } from '../app/domain/data'
const root = fileURLToPath(new URL('../../', import.meta.url))
const hashes: Record<string, string> = {}
const rowsSchema = z.array(z.record(z.string(), z.string()))
async function csv(path: string) {
  const raw = await readFile(resolve(root, path), 'utf8')
  hashes[path] = createHash('sha256').update(raw).digest('hex')
  return rowsSchema
    .parse(parse(raw, { columns: true, bom: true, skip_empty_lines: true }))
    .map((r) =>
      Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v.trim() === '' ? null : v])),
    )
}
const base = 'data/airport_research/'
const main = await csv(base + 'processed/airports.csv'),
  extra = await csv(base + 'processed/route_airports.csv')
const conflicts: string[] = []
const airports = new Map<string, Record<string, string | number | boolean | null>>()
for (const r of [...extra, ...main]) {
  if (!r.latitude || !r.longitude || !r.airport_iata) throw new Error('Missing airport coordinates')
  const previous = airports.get(r.airport_iata)
  if (
    previous &&
    (previous.latitude !== Number(r.latitude) || previous.longitude !== Number(r.longitude))
  )
    conflicts.push(r.airport_iata)
  airports.set(r.airport_iata, {
    ...r,
    latitude: Number(r.latitude),
    longitude: Number(r.longitude),
    primary: main.some((a) => a.airport_iata === r.airport_iata),
  })
}
const routeKeys = await csv(base + 'documentation/ROUTE_KEYS.csv')
const observations = (await csv(base + 'processed/airport_routes.csv')).map((r) => ({
  ...r,
  route_id:
    routeKeys.find((k) =>
      [
        'origin_iata',
        'destination_iata',
        'year',
        'season',
        'valid_from',
        'valid_to',
        'carrier',
        'source_id',
      ].every((field) => k[field] === r[field]),
    )?.route_id ?? null,
}))
const statistics = [
  ...(await csv(base + 'processed/airport_annual.csv')),
  ...(await csv(base + 'processed/airport_monthly.csv')),
]
const lineage = (await csv(base + 'documentation/DATA_LINEAGE.csv')).filter(
  (r) =>
    ['route', 'airport'].includes(r.entity_type ?? '') &&
    [
      'passengers_total',
      'weekly_departures',
      'seats_per_departure',
      'latitude',
      'longitude',
    ].includes(r.metric ?? ''),
)
const qualifiers = await csv(base + 'documentation/ROUTE_QUALIFIERS.csv')
await csv(base + 'documentation/ROUTE_KEYS.csv')
const sources = await csv(base + 'sources/sources.csv')
sources.push(
  {
    source_id: 'RW_FLEET',
    title: 'Официальный каталог ВС · 13.11.2026',
    url: 'https://flyredwings.com/about/park/',
  },
  {
    source_id: 'GG',
    title: 'Сценарные параметры gg / calculate.py; SSJ100 исправлен на 100 кресел',
    url: 'analysis/calculate.py',
  },
)
for (const path of [
  'calculator/app/domain/data.ts',
  'calculator/app/domain/scenario.ts',
  'calculator/app/domain/economics.ts',
  'analysis/calculate.py',
  'analysis/HUB_STRATEGY.md',
  'presentation/slides.md',
  'data/cargo_research/estimates/assumptions.csv',
  'data/cargo_research/estimates/scenarios.csv',
]) {
  const raw = await readFile(resolve(root, path))
  hashes[path] = createHash('sha256').update(raw).digest('hex')
}
const gitSha = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim()
const dataRevision = createHash('sha256').update(JSON.stringify(hashes)).digest('hex').slice(0, 16)
const data = dataSchema.parse({
  schemaVersion: 1,
  fleetProfiles: profiles,
  assumptions: {
    ssjSeats: 100,
    ancillary: 900,
    passengerCost: 650,
    market2025: 108850000,
    rw2025: 2700000,
  },
  gitSha,
  dataRevision,
  airports: [...airports.values()],
  observations,
  sources,
  statistics,
  lineage,
  qualifiers,
  hashes,
  conflicts,
})
const out = resolve(root, 'calculator/public/data')
await mkdir(out, { recursive: true })
await writeFile(resolve(out, 'network.json'), JSON.stringify(data))
console.log(
  `${data.airports.length} airports; ${observations.length} observations; ${gitSha}; revision ${dataRevision}`,
)
