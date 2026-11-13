<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import type { ECharts } from 'echarts'
import type { Scenario } from '../domain/scenario'
import type { Airport } from '../domain/data'
import { calculate, breakEven } from '../domain/economics'
const props = defineProps<{ scenario: Scenario; airports: Airport[] }>()
const left = ref<HTMLElement>(),
  right = ref<HTMLElement>()
let charts: ECharts[] = [],
  observer: ResizeObserver | undefined
function update() {
  const r = calculate(props.scenario, props.airports),
    be = breakEven(props.scenario, props.airports)
  charts[0]?.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 65, right: 20, bottom: 80, top: 30 },
    xAxis: {
      type: 'category',
      data: ['Выручка', 'Переменные', 'Каннибал.', 'Вытеснение', 'Постоянные', 'Результат'],
      axisLabel: { rotate: 25 },
    },
    yAxis: { type: 'value', name: 'млн ₽' },
    series: [
      {
        type: 'bar',
        stack: 'bridge',
        silent: true,
        itemStyle: { color: 'transparent' },
        data: [
          0,
          r.revenue - r.variable,
          r.revenue - r.variable - r.lostCM,
          r.revenue - r.variable - r.lostCM - props.scenario.displacedCM,
          r.passenger ?? 0,
          0,
        ].map((v) => v / 1e6),
      },
      {
        type: 'bar',
        stack: 'bridge',
        data: [
          r.revenue,
          -r.variable,
          -r.lostCM,
          -props.scenario.displacedCM,
          -r.fixed,
          r.passenger,
        ].map((v, i) =>
          v === null
            ? null
            : {
                value: (i > 0 && i < 5 ? Math.abs(v) : v) / 1e6,
                itemStyle: { color: v >= 0 ? '#24715a' : '#c8102e' },
              },
        ),
      },
    ],
  })
  charts[1]?.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 65, right: 25, bottom: 40, top: 30 },
    xAxis: { type: 'value', min: 0, max: 100, name: 'LF, %' },
    yAxis: { type: 'value', name: 'млн ₽' },
    series: [
      {
        type: 'line',
        showSymbol: false,
        data: Array.from({ length: 51 }, (_, i) => [
          i * 2,
          (calculate(props.scenario, props.airports, i / 50).result ?? 0) / 1e6,
        ]),
        lineStyle: { color: '#c8102e', width: 3 },
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: 0 },
            ...(be === null ? [] : [{ xAxis: be * 100, label: { formatter: 'Безубыточность' } }]),
          ],
        },
        markPoint: {
          data: [
            {
              coord: [
                props.scenario.lf * 100,
                (calculate(props.scenario, props.airports, props.scenario.lf).result ?? 0) / 1e6,
              ],
              name: 'Общий LF',
              value: `${Math.round(props.scenario.lf * 100)}%`,
            },
          ],
        },
      },
    ],
  })
}
onMounted(async () => {
  const e = await import('echarts')
  if (left.value && right.value) {
    charts = [e.init(left.value), e.init(right.value)]
    observer = new ResizeObserver(() => charts.forEach((c) => c.resize()))
    observer.observe(left.value)
    observer.observe(right.value)
    update()
  }
})
watch(() => props.scenario, update, { deep: true })
onBeforeUnmount(() => {
  observer?.disconnect()
  charts.forEach((c) => c.dispose())
})
</script>
<template>
  <div class="charts">
    <section class="panel">
      <h2>От выручки к результату</h2>
      <p>Пассажирская программа · млн ₽</p>
      <div ref="left" class="chart" />
    </section>
    <section class="panel">
      <h2>Чувствительность к загрузке</h2>
      <p>Общий LF для всех строк; заданный парк и тариф. При неполном профиле кривая недоступна.</p>
      <div ref="right" class="chart" />
    </section>
  </div>
</template>
