<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue'
import type { Map as GLMap, GeoJSONSource, StyleSpecification } from 'maplibre-gl'
import type { FeatureCollection } from 'geojson'
import type { Airport, Dataset } from '../domain/data'
import { bases } from '../domain/data'
import { arc } from '../domain/geography'
import type { calculate } from '../domain/economics'
const props = defineProps<{
  data: Dataset
  base: string
  rows: ReturnType<typeof calculate>['rows']
  selected: string
  compareRoutes?: { base: string; destination: string; label: string }[]
  fitKey: string
}>()
const emit = defineEmits<{ select: [id: string]; base: [iata: string]; add: [iata: string] }>()
const container = ref<HTMLElement>(),
  picked = ref<Airport>(),
  error = ref(''),
  historical = ref(false),
  others = ref(false),
  year = ref('2025'),
  color = ref(false),
  project = ref(true)
let map: GLMap | undefined,
  observer: ResizeObserver | undefined,
  timer: ReturnType<typeof setTimeout> | undefined
const fallback: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#eeefeb' } }],
}
const config = useRuntimeConfig()
const chosenRoute = computed(() => props.rows.find((r) => r.id === props.selected))
const historicInfo = ref('')
const fallbackUsed = ref(false)
function airport(iata: string) {
  return props.data.airports.find((a) => a.airport_iata === iata)
}
function features(): FeatureCollection {
  const origin = airport(props.base)
  const lines =
    origin && project.value
      ? props.rows.flatMap((r) => {
          const d = airport(r.destination)
          return d
            ? [
                {
                  type: 'Feature' as const,
                  properties: {
                    id: r.id,
                    label: `${props.base}–${r.destination}`,
                    width: Math.max(2, Math.min(8, r.capacity / 10000)),
                    color: color.value
                      ? r.result === null
                        ? '#747a80'
                        : r.result >= 0
                          ? '#24715a'
                          : '#c8102e'
                      : '#c8102e',
                  },
                  geometry: { type: 'LineString' as const, coordinates: arc(origin, d) },
                },
              ]
            : []
        })
      : []
  const seen = new Set<string>()
  const history = historical.value
    ? props.data.observations
        .filter((r) => r.year === year.value && (r.carrier === 'Red Wings' || others.value))
        .flatMap((r) => {
          const a = airport(r.origin_iata ?? ''),
            b = airport(r.destination_iata ?? ''),
            key = [r.origin_iata, r.destination_iata].sort().join('-')
          if (!a || !b || seen.has(key)) return []
          seen.add(key)
          return [
            {
              type: 'Feature' as const,
              properties: {
                id: 'history:' + key,
                label: `${key} · ${r.year} · ${r.valid_from ?? '?'} — ${r.valid_to ?? '?'} · ${r.carrier ?? 'Перевозчик неизвестен'} · ${r.weekly_departures ?? 'частота неизвестна'} · ${r.source_id}`,
                width: 1,
                color: '#a8adb0',
              },
              geometry: { type: 'LineString' as const, coordinates: arc(a, b) },
            },
          ]
        })
    : []
  const comparison = (props.compareRoutes ?? []).flatMap((r) => {
    const a = airport(r.base),
      b = airport(r.destination)
    return a && b
      ? [
          {
            type: 'Feature' as const,
            properties: {
              id: 'compare:' + r.destination,
              label: r.label,
              width: 3,
              color: '#426f98',
            },
            geometry: { type: 'LineString' as const, coordinates: arc(a, b) },
          },
        ]
      : []
  })
  return { type: 'FeatureCollection', features: [...history, ...lines, ...comparison] }
}
function update() {
  if (!map?.getSource('routes')) return
  ;(map.getSource('routes') as GeoJSONSource).setData(features())
  map.setPaintProperty('airport-points', 'circle-radius', [
    'case',
    ['==', ['get', 'iata'], props.base],
    9,
    ['get', 'base'],
    6,
    4,
  ])
  map.setPaintProperty('route-lines', 'line-opacity', [
    'case',
    ['==', ['get', 'id'], props.selected],
    1,
    0.7,
  ])
}
function fit() {
  const a = airport(props.base),
    points = [
      a,
      ...props.rows.map((r) => airport(r.destination)),
      ...(props.compareRoutes ?? []).flatMap((r) => [airport(r.base), airport(r.destination)]),
    ].filter((x): x is Airport => !!x)
  if (!map || !points.length) return
  map.fitBounds(
    [
      [
        Math.min(...points.map((p) => p.longitude)) - 2,
        Math.min(...points.map((p) => p.latitude)) - 2,
      ],
      [
        Math.max(...points.map((p) => p.longitude)) + 2,
        Math.max(...points.map((p) => p.latitude)) + 2,
      ],
    ],
    { padding: 55, maxZoom: 6, duration: 500 },
  )
}
function layers() {
  if (!map || map.getSource('routes')) return
  map.addSource('routes', { type: 'geojson', data: features() })
  map.addLayer({
    id: 'route-lines',
    type: 'line',
    source: 'routes',
    paint: { 'line-color': ['get', 'color'], 'line-width': ['get', 'width'], 'line-opacity': 0.7 },
  })
  map.addSource('airports', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: props.data.airports.map((a) => ({
        type: 'Feature',
        properties: { iata: a.airport_iata, base: bases.includes(a.airport_iata) },
        geometry: { type: 'Point', coordinates: [a.longitude, a.latitude] },
      })),
    },
  })
  map.addLayer({
    id: 'airport-points',
    type: 'circle',
    source: 'airports',
    paint: {
      'circle-radius': ['case', ['==', ['get', 'iata'], props.base], 9, ['get', 'base'], 6, 4],
      'circle-color': '#fff',
      'circle-stroke-width': ['case', ['==', ['get', 'iata'], props.base], 4, 2],
      'circle-stroke-color': '#c8102e',
    },
  })
  // Labels are painted by the map engine, without DOM markers or unsafe HTML.
  if (!fallbackUsed.value)
    map.addLayer({
      id: 'labels',
      type: 'symbol',
      source: 'airports',
      layout: {
        'text-field': ['get', 'iata'],
        'text-font': ['Noto Sans Regular'],
        'text-size': 11,
        'text-offset': [0, 1.3],
      },
      paint: { 'text-color': '#353b40', 'text-halo-color': '#fff', 'text-halo-width': 2 },
    })
  fit()
}
onMounted(async () => {
  try {
    const gl = await import('maplibre-gl')
    if (!container.value) return
    map = new gl.Map({
      container: container.value,
      style: config.public.mapStyle,
      center: [50, 53],
      zoom: 3,
      attributionControl: { compact: true },
    })
    map.addControl(new gl.NavigationControl(), 'top-right')
    map.addControl(new gl.FullscreenControl(), 'top-right')
    map.on('load', layers)
    map.on('style.load', layers)
    map.on('error', () => {
      if (map && !map.getSource('routes') && !fallbackUsed.value) {
        fallbackUsed.value = true
        error.value = 'Схемный режим · внешний стиль недоступен'
        map.setStyle(fallback)
      }
    })
    map.on('click', 'airport-points', (e) => {
      const i = e.features?.[0]?.properties?.iata
      picked.value = airport(String(i))
    })
    map.on('click', 'route-lines', (e) => {
      const p = e.features?.[0]?.properties
      if (String(p?.id).startsWith('history:') || String(p?.id).startsWith('compare:'))
        historicInfo.value = String(p?.label)
      else emit('select', String(p?.id))
    })
    observer = new ResizeObserver(() => map?.resize())
    observer.observe(container.value)
    timer = setTimeout(() => {
      if (map && !map.getSource('routes') && !fallbackUsed.value) {
        fallbackUsed.value = true
        error.value = 'Схемный режим · без сетевой подложки'
        map.setStyle(fallback)
      }
    }, 12000)
  } catch {
    error.value = 'WebGL недоступен. Маршруты и расчёт доступны в таблице.'
  }
})
watch(
  () => [
    props.rows,
    props.base,
    props.selected,
    historical.value,
    others.value,
    year.value,
    color.value,
    project.value,
  ],
  update,
  { deep: true },
)
watch(() => props.fitKey, fit)
onBeforeUnmount(() => {
  if (timer) clearTimeout(timer)
  observer?.disconnect()
  map?.remove()
})
</script>
<template>
  <section class="map-panel">
    <div class="map-toolbar">
      <strong>География программы</strong><button @click="fit">Вся программа ↗</button>
    </div>
    <div ref="container" class="map-canvas" />
    <div class="map-filters">
      <label><input v-model="project" type="checkbox" /> Проект</label
      ><label><input v-model="historical" type="checkbox" /> Исторические Red Wings</label
      ><label v-if="historical"
        ><input v-model="others" type="checkbox" /> Другие / неизвестные</label
      ><select v-if="historical" v-model="year" aria-label="Год наблюдений">
        <option>2024</option>
        <option>2025</option></select
      ><label><input v-model="color" type="checkbox" /> Цвет: результат</label
      ><span>Толщина — креслоёмкость · кольцо — база по gg</span>
    </div>
    <div v-if="picked" class="map-card">
      <button class="close" @click="picked = undefined">×</button
      ><strong>{{ picked.airport_iata }} · {{ picked.city }}</strong>
      <p>{{ picked.airport_name }} · {{ picked.timezone ?? 'Часовой пояс неизвестен' }}</p>
      <p
        v-for="(stat, i) in data.statistics.filter(
          (r) => r.airport_iata === picked?.airport_iata && !r.month,
        )"
        :key="i"
      >
        {{ stat.year }}:
        {{
          stat.passengers_total === null
            ? 'нет данных'
            : Number(stat.passengers_total).toLocaleString('ru-RU')
        }}
        пассажиров всего · источник в реестре / не O&amp;D
      </p>
      <button @click="emit('base', picked.airport_iata)">Сделать базой</button
      ><button @click="emit('add', picked.airport_iata)">Добавить маршрут</button>
    </div>
    <div v-if="chosenRoute" class="map-card route-card">
      <strong>{{ base }}–{{ chosenRoute.destination }}</strong>
      <p>
        {{ chosenRoute.type }} · {{ chosenRoute.seats ?? '?' }} мест ·
        {{ chosenRoute.frequency }} об./нед.<br />Тариф
        {{ Math.round(chosenRoute.fare).toLocaleString('ru-RU') }} ₽ · LF
        {{
          Math.round(chosenRoute.capacity ? (chosenRoute.p / chosenRoute.capacity) * 100 : 0)
        }}%<br />Результат
        {{
          chosenRoute.result === null
            ? 'нужен профиль'
            : (chosenRoute.result / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 }) +
              ' млн ₽'
        }}
      </p>
    </div>
    <p v-if="historicInfo" class="map-message">{{ historicInfo }}</p>
    <p v-if="error" class="map-message">
      {{ error }}
    </p>
    <div class="map-caption">
      <span v-if="compareRoutes?.length">S1 MRV — красный · S2 NUX — синий / </span> {{ base }} ·
      проект / исторические наблюдения 2024–2025 ≠ расписание 2026
    </div>
  </section>
</template>
