import { z } from 'zod'
export const airportSchema = z.object({
  airport_iata: z.string(),
  airport_name: z.string(),
  city: z.string().nullable(),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  primary: z.boolean(),
  country: z.string(),
  timezone: z.string().nullable().optional(),
})
export type Airport = z.infer<typeof airportSchema>
export const dataSchema = z.object({
  schemaVersion: z.literal(1),
  gitSha: z.string(),
  dataRevision: z.string(),
  airports: z.array(airportSchema),
  fleetProfiles: z.array(
    z.object({
      id: z.string(),
      seats: z.number().nullable(),
      total: z.number(),
      range: z.number().nullable(),
    }),
  ),
  assumptions: z.record(z.string(), z.number()),
  observations: z.array(z.record(z.string(), z.string().nullable())),
  sources: z.array(z.record(z.string(), z.string().nullable())),
  statistics: z.array(z.record(z.string(), z.string().nullable())),
  lineage: z.array(z.record(z.string(), z.string().nullable())),
  qualifiers: z.array(z.record(z.string(), z.string().nullable())),
  hashes: z.record(z.string(), z.string()),
  conflicts: z.array(z.string()),
})
export type Dataset = z.infer<typeof dataSchema>
export const profiles = [
  { id: 'SSJ100', seats: 100, total: 20, range: 4200 },
  { id: 'Ту-204-100В', seats: 210, total: 2, range: 3800 },
  { id: 'Ту-214', seats: 194, total: 3, range: 5200 },
  { id: 'B777-200ER', seats: 412, total: 3, range: 9100 },
  { id: 'SJ-100 / ПД-8', seats: null, total: 0, range: null },
]
export const bases = ['AER', 'KUF', 'KZN', 'LED', 'SVX', 'MRV']
