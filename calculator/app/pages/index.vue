<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { dataSchema, bases } from '../domain/data'
import { preset, scenarioSchema } from '../domain/scenario'
import { calculate, breakEven } from '../domain/economics'
const { data: raw, error: loadError } = await useFetch('/data/network.json')
const parsedData = computed(() => dataSchema.safeParse(raw.value))
const data = computed(() => (parsedData.value.success ? parsedData.value.data : null))
const s = ref(preset('S1')),
  presetId = ref('S1'),
  lastPresetId = ref('S1'),
  tab = ref('Программа'),
  selected = ref(''),
  message = ref(''),
  search = ref(''),
  destination = ref('OMS'),
  saved = ref<string[]>([]),
  fitKey = ref('0')
import { number, money } from '../utils/format'
const result = computed(() => calculate(s.value, data.value?.airports ?? [])),
  be = computed(() => breakEven(s.value, data.value?.airports ?? []))
const airports = computed(() =>
  (data.value?.airports ?? []).filter((a) =>
    `${a.airport_iata} ${a.city} ${a.airport_name}`
      .toLowerCase()
      .includes(search.value.toLowerCase()),
  ),
)
const comparisonIds = ref(['S1', 'S2'])
const comparisons = computed(() =>
  comparisonIds.value.map((id) => {
    const stored = id.startsWith('rw:')
      ? scenarioSchema.safeParse(JSON.parse(localStorage.getItem(id) ?? 'null'))
      : null
    const scenario = id === 'current' ? s.value : stored?.success ? stored.data : preset(id)
    return { scenario, result: calculate(scenario, data.value?.airports ?? []) }
  }),
)
function reset() {
  if (presetId.value !== 'custom') lastPresetId.value = presetId.value
  presetId.value = lastPresetId.value
  s.value = preset(lastPresetId.value, data.value?.dataRevision)
  fitKey.value = String(Date.now())
}
function setBase(code: string) {
  if (!data.value?.airports.some((a) => a.airport_iata === code)) return
  tab.value = 'Программа'
  s.value.base = code
  if (presetId.value !== 'custom' || s.value.name.startsWith('Пользовательский')) {
    s.value.name = `Пользовательский · ${code}`
  }
  presetId.value = 'custom'
  s.value.routes = s.value.routes.filter((r) => r.destination !== code)
  fitKey.value = String(Date.now())
}
function mode() {
  s.value.cannibalization = s.value.hub ? 0.06 : 0.12
  s.value.baseCost = s.value.hub ? 120e6 : 20e6
  s.value.personnel = s.value.hub ? 45e6 : 20e6
  s.value.infrastructure = s.value.hub ? 35e6 : 10e6
}
function add(code = destination.value) {
  tab.value = 'Программа'
  if (code === s.value.base || s.value.routes.some((r) => r.destination === code)) {
    message.value = 'Эта пара уже есть или совпадает с базой'
    return
  }
  fitKey.value = String(Date.now())
  s.value.routes.push({
    id: crypto.randomUUID(),
    destination: code,
    enabled: true,
    type: 'SSJ100',
    seats: 100,
    frequency: 4,
    lf: null,
    fare: null,
    bh: null,
    cost: null,
    od: null,
    capture: 1,
  })
}
function save() {
  try {
    const valid = scenarioSchema.parse(s.value)
    localStorage.setItem('rw:' + valid.name, JSON.stringify(valid))
    refreshSaved()
    message.value = 'Сценарий сохранён в этом браузере'
  } catch {
    message.value = 'Исправьте пустые или недопустимые поля перед сохранением'
  }
}
function refreshSaved() {
  try {
    saved.value = Object.keys(localStorage).filter((k) => k.startsWith('rw:'))
  } catch {
    saved.value = []
    message.value = 'Хранилище браузера недоступно. Используйте экспорт JSON.'
  }
}
function loadSaved(key: string) {
  load(localStorage.getItem(key) ?? '')
  tab.value = 'Программа'
}
function load(text: string) {
  try {
    const v = scenarioSchema.parse(JSON.parse(text))
    if (
      !data.value?.airports.some((a) => a.airport_iata === v.base) ||
      v.routes.some((r) => !data.value?.airports.some((a) => a.airport_iata === r.destination))
    )
      throw Error()
    s.value = v
    message.value =
      v.dataRevision !== data.value?.dataRevision
        ? 'Срез данных отличается; пользовательские параметры сохранены'
        : 'Сценарий загружен'
    fitKey.value = String(Date.now())
  } catch {
    message.value = 'Некорректный JSON: текущий сценарий сохранён'
  }
}
function download(content: string, name: string, type = 'application/json') {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}
function exportJSON() {
  const v = scenarioSchema.safeParse(s.value)
  if (!v.success) {
    message.value = 'Исправьте поля перед экспортом'
    return
  }
  download(
    JSON.stringify({ ...v.data, gitSha: data.value?.gitSha }, null, 2),
    'red-wings-scenario.json',
  )
}
async function importJSON(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) load(await file.text())
}
function exportCSV() {
  const rows = [
    [
      'origin_iata',
      'destination_iata',
      'aircraft',
      'seats',
      'legs',
      'passenger_segments',
      'revenue_rub',
      'variable_rub',
      'fixed_rub',
      'result_rub',
    ],
    ...result.value.rows.map((r) => [
      s.value.base,
      r.destination,
      r.type,
      r.seats,
      r.legs,
      r.p,
      r.revenue,
      r.variable,
      r.fixed,
      r.result,
    ]),
  ]
  download(
    '\ufeff' +
      rows
        .map((r) => r.map((v) => '"' + String(v ?? '').replaceAll('"', '""') + '"').join(','))
        .join('\r\n'),
    'routes.csv',
    'text/csv;charset=utf-8',
  )
}
onMounted(() => {
  s.value.dataRevision = data.value?.dataRevision ?? ''
  refreshSaved()
})
</script>
<template>
  <div v-if="!data" class="panel">
    {{
      loadError || raw
        ? 'Ошибка версии данных. Обновите страницу; при необходимости выполните pnpm data:prepare.'
        : 'Загружаем данные…'
    }}
  </div>
  <main v-else>
    <header>
      <div class="brand">RED WINGS<span>Маршрутный калькулятор</span></div>
      <div class="header-actions">
        <label class="header-airport"
          >Аэропорт · {{ data.airports.length }} из CSV
          <select
            :value="s.base"
            aria-label="Аэропорт программы из CSV"
            @change="setBase(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="a in data.airports" :key="a.airport_iata" :value="a.airport_iata">
              {{ a.airport_iata }} · {{ a.city ?? a.airport_name }}
            </option>
          </select>
        </label>
        <label class="header-airport"
          >Готовый пресет
          <select v-model="presetId" aria-label="Сценарий" @change="reset">
            <option v-if="presetId === 'custom'" value="custom">Пользовательский</option>
            <option value="S1">S1 · MRV</option>
            <option value="S2">S2 · NUX</option>
            <option value="stress">S1 · Осторожный</option>
          </select></label
        ><button @click="save">Сохранить</button
        ><button class="primary" @click="tab = 'Сравнение'">Сравнить ↗</button>
      </div>
    </header>
    <div class="intro">
      <div>
        <p class="eyebrow">ПЛАНИРОВАНИЕ СЕТИ / {{ s.year }}</p>
        <h1>Региональная программа</h1>
        <p>От маршрута к экономике. Сценарные продажи, заданный парк, прозрачные допущения.</p>
      </div>
      <span class="badge">gg · {{ data.gitSha.slice(0, 7) }} / SSJ100 · 100 мест</span>
    </div>
    <div v-if="message" class="notice" role="status">
      {{ message }} <button @click="message = ''">Закрыть</button>
    </div>
    <div class="kpis">
      <article>
        <span>Дополнительные сегменты</span><strong>{{ number(result.net) }}</strong
        ><small>Валовые: {{ number(result.p) }}</small>
      </article>
      <article>
        <span>Выручка программы</span><strong>{{ money(result.revenue) }}</strong
        ><small>Тариф + дополнительные услуги</small>
      </article>
      <article>
        <span>Расчётный результат</span
        ><strong :class="{ negative: (result.result ?? 0) < 0 }">{{ money(result.result) }}</strong
        ><small>После регулярных расходов · {{ s.weeks }} нед.</small>
      </article>
      <article>
        <span>Рабочие / выделенные борта</span
        ><strong
          >{{ result.fleet.reduce((a, f) => a + f.working, 0) }} /
          {{ result.fleet.reduce((a, f) => a + f.working + f.reserve, 0) }}</strong
        ><small>{{
          result.feasible ? 'Годовой ресурс обеспечен' : 'Не обеспечен флотом / нужен профиль'
        }}</small>
      </article>
    </div>
    <div class="submetrics">
      <span
        >LF безубыточности:
        <b>{{
          be === null ? 'Не достигается / нужен профиль' : number(be * 100, 1) + '%'
        }}</b></span
      ><span
        >Прирост доли: <b>{{ number(result.share, 3) }} п.п.</b> · при фиксированном рынке
        2025</span
      ><span>Расписание и спрос не подтверждены</span>
    </div>
    <nav>
      <button
        v-for="t in ['Программа', 'Флот', 'Сравнение', 'Источники и допущения']"
        :key="t"
        :class="{ active: tab === t }"
        @click="tab = t"
      >
        {{ t }}
      </button>
    </nav>
    <template v-if="tab === 'Программа'">
      <div class="workspace">
        <section class="panel editor">
          <div class="section-title">
            <h2>Параметры программы</h2>
            <span class="badge">Допущение</span>
          </div>
          <label class="field">Название<input v-model="s.name" /></label>
          <div class="two">
            <NumberField v-model="s.year" label="Расчётный год" :min="2026" :step="1" /><NumberField
              v-model="s.weeks"
              label="Период, недель"
              :min="1"
              :max="53"
              :step="1"
            />
          </div>
          <label class="field"
            >Поиск аэропорта<input v-model="search" placeholder="IATA, город или название" /></label
          ><label class="field"
            >База<select
              :value="s.base"
              @change="setBase(($event.target as HTMLSelectElement).value)"
            >
              <option v-for="a in airports" :key="a.airport_iata" :value="a.airport_iata">
                {{ a.airport_iata }} · {{ a.city }}
              </option>
            </select></label
          ><small>{{
            bases.includes(s.base)
              ? 'База по gg; MRV — летняя, годовая работа сценарная'
              : 'Новая площадка · статус базы не подтверждён'
          }}</small
          ><label class="field"
            >Экономический режим<select v-model="s.hub" @change="mode">
              <option :value="false">Развитие действующей базы</option>
              <option :value="true">Новый хаб</option>
            </select></label
          ><label class="check"
            ><input v-model="s.transfers" type="checkbox" /> Моделировать пересадки</label
          ><label class="field"
            >Общая загрузка · {{ number(s.lf * 100) }}%<input
              :value="s.lf * 100"
              type="range"
              min="0"
              max="100"
              @input="s.lf = Number(($event.target as HTMLInputElement).value) / 100" /><input
              :value="s.lf * 100"
              aria-label="Загрузка, %"
              type="number"
              min="0"
              max="100"
              @input="
                s.lf =
                  Math.max(0, Math.min(100, Number(($event.target as HTMLInputElement).value))) /
                  100
              " /></label
          ><NumberField v-model="s.tariff" label="Множитель чистого тарифа gg" /><small
            >₽ за пассажира на одном сегменте. Ручной тариф — в строке маршрута.</small
          >
          <div class="two">
            <NumberField v-model="s.ancillary" label="Допуслуги, ₽/пасс." /><NumberField
              v-model="s.passengerCost"
              label="Затраты, ₽/пасс."
            />
          </div>
          <div class="add-route">
            <select v-model="destination" aria-label="Добавить направление">
              <option v-for="a in data.airports" :key="a.airport_iata" :value="a.airport_iata">
                {{ a.airport_iata }} · {{ a.city }}
              </option></select
            ><button class="primary" @click="add()">+ Маршрут</button>
          </div>
          <button @click="reset">Сбросить к пресету</button>
        </section>
        <ClientOnly>
          <NetworkMap
            :data="data"
            :base="s.base"
            :rows="result.rows"
            :selected="selected"
            :fit-key="fitKey"
            @base="setBase"
            @add="add"
            @select="selected = $event"
          />
        </ClientOnly>
      </div>
      <RouteTable v-model="s" v-model:selected="selected" :result="result" @export="exportCSV" />
      <ClientOnly>
        <FinanceCharts v-if="result.complete" :scenario="s" :airports="data.airports" />
      </ClientOnly>
      <AdditionalParameters v-model="s" :result="result" :data="data" />
    </template>
    <FleetPanel v-if="tab === 'Флот'" v-model="s" :result="result" />
    <section v-if="tab === 'Сравнение'" class="panel">
      <h2>S1 / S2</h2>
      <p>
        Независимые пресеты при 100 креслах; текущие изменения остаются в редакторе.
      </p>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Показатель</th>
              <th v-for="(c, i) in comparisons" :key="i">
                <select v-model="comparisonIds[i]" :aria-label="'Сценарий сравнения ' + (i + 1)">
                  <option v-for="id in ['S1', 'S2', 'stress']" :key="id" :value="id">
                    {{ id }}
                  </option>
                  <option value="current">Текущий</option>
                  <option v-for="key in saved" :key="key" :value="key">{{ key.slice(3) }}</option>
                </select>
                <p>{{ c.scenario.name }}</p>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="metric in [
                'p',
                'net',
                'revenue',
                'variable',
                'lostCM',
                'fixed',
                'result',
                'hours',
                'share',
              ] as const"
              :key="metric"
            >
              <th>
                {{
                  {
                    p: 'Валовые сегменты',
                    net: 'Дополнительные сегменты',
                    revenue: 'Выручка, ₽',
                    variable: 'Переменные, ₽',
                    lostCM: 'Потерянный CM, ₽',
                    fixed: 'Постоянные, ₽',
                    result: 'Результат, ₽',
                    hours: 'Налёт, BH',
                    share: 'Прирост доли, п.п.',
                  }[metric]
                }}
              </th>
              <td v-for="c in comparisons" :key="c.scenario.name">
                {{ number(c.result[metric], 3) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <ClientOnly
        ><NetworkMap
          :data="data"
          base="MRV"
          :rows="calculate(preset('S1'), data.airports).rows"
          :selected="selected"
          fit-key="comparison"
          @base="setBase"
          @add="add"
          @select="selected = $event"
          :compare-routes="
            preset('S2').routes.map((r) => ({
              base: 'NUX',
              destination: r.destination,
              label: 'S2 · NUX–' + r.destination,
            }))
          "
      /></ClientOnly>
      <div class="table-scroll">
        <table>
          <tbody>
            <tr>
              <th>Флот / резерв / статус</th>
              <td v-for="(c, i) in comparisons" :key="i">
                {{ c.result.fleet.reduce((a, f) => a + f.working, 0) }} +
                {{ c.result.fleet.reduce((a, f) => a + f.reserve, 0) }} ·
                {{ c.result.feasible ? 'Ресурс обеспечен' : 'Не обеспечен / нужен профиль' }}
              </td>
            </tr>
            <tr>
              <th>LF безубыточности</th>
              <td v-for="(c, i) in comparisons" :key="i">
                {{
                  breakEven(c.scenario, data.airports) === null
                    ? 'Не достигается / неизвестно'
                    : number((breakEven(c.scenario, data.airports) ?? 0) * 100, 1) + '%'
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <h3>Именованные сценарии</h3>
      <button v-for="key in saved" :key="key" @click="loadSaved(key)">
        {{ key.slice(3) }}
      </button>
      <div class="actions">
        <button @click="exportJSON">Экспорт JSON ↓</button
        ><label class="button"
          >Импорт JSON<input type="file" accept="application/json" @change="importJSON"
        /></label>
      </div>
    </section>
    <SourceDetails v-if="tab === 'Источники и допущения'" :data="data" />
    <footer>
      RED WINGS / WeSeekDp <span>Инструмент сценарного планирования · не прогноз спроса</span>
    </footer>
  </main>
</template>
