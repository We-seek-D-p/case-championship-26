import { profiles } from './data'
import type { Route, Scenario } from './scenario'

export function createAllocation(type: string): Scenario['fleet'][number] {
  return {
    type,
    available: 0,
    working: 0,
    reserve: 0,
    peak: 1,
    resource: type === 'SSJ100' ? 2200 : null,
    fixed: type === 'SSJ100' ? 65e6 : null,
  }
}

export function setRouteAircraft(route: Route, type: string) {
  route.type = type
  route.seats = profiles.find((profile) => profile.id === type)?.seats ?? null
  // Блок-время и стоимость относятся к прежнему типу; его профиль не переносится.
  route.bh = null
  route.cost = null
}

export function replaceFleetType(scenario: Scenario, previous: string, next: string) {
  if (previous === next || !profiles.some((profile) => profile.id === next)) return
  if (scenario.fleet.some((allocation) => allocation.type === next)) return
  const allocation = scenario.fleet.find((item) => item.type === previous)
  if (!allocation) return
  const defaults = createAllocation(next)
  allocation.type = next
  allocation.resource = defaults.resource
  allocation.fixed = defaults.fixed
  for (const route of scenario.routes.filter((item) => item.type === previous)) {
    setRouteAircraft(route, next)
  }
}
