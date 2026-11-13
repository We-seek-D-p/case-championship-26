<script setup lang="ts">
import { profiles } from '../domain/data'
import { createAllocation, setRouteAircraft } from '../domain/fleet'
import type { Scenario, Route } from '../domain/scenario'
import type { calculate } from '../domain/economics'
import { number, money } from '../utils/format'
const s = defineModel<Scenario>({ required: true })
const selected = defineModel<string>('selected', { required: true })
defineProps<{ result: ReturnType<typeof calculate> }>()
const emit = defineEmits<{ export: [] }>()
function aircraft(r: Route) {
  setRouteAircraft(r, r.type)
  if (!s.value.fleet.some((f) => f.type === r.type)) s.value.fleet.push(createAllocation(r.type))
}
</script>
<template>
  <section class="panel route-panel">
    <div class="section-title">
      <div>
        <h2>
          Маршруты <span class="muted">/ {{ s.routes.length }}</span>
        </h2>
        <p>
          Один оборот = туда и обратно = два сегмента. Override сохраняется при изменении общих
          настроек.
        </p>
      </div>
      <button @click="emit('export')">Экспорт CSV ↓</button>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Пара / активность</th>
            <th>Самолёт · кресла</th>
            <th>Обороты / нед.</th>
            <th>LF, % / общее</th>
            <th>Тариф ₽ / gg</th>
            <th>BH / стоимость вылета ₽</th>
            <th>Сегменты</th>
            <th>Результат</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in s.routes"
            :key="r.id"
            :class="{ selected: selected === r.id }"
            @click="selected = r.id"
          >
            <td>
              <label
                ><input v-model="r.enabled" type="checkbox" /> {{ s.base }}–{{
                  r.destination
                }}</label
              ><small>{{ result.rows.find((x) => x.id === r.id)?.warning }}</small>
            </td>
            <td>
              <select v-model="r.type" aria-label="Тип ВС" @change="aircraft(r)">
                <option v-for="p in profiles" :key="p.id">
                  {{ p.id }}
                </option></select
              ><NumberField v-model="r.seats" label="Кресла" :nullable="true" :step="1" />
            </td>
            <td>
              <NumberField v-model="r.frequency" label="Обороты" :max="14" :step="1" />
            </td>
            <td>
              <input
                :value="r.lf === null ? '' : r.lf * 100"
                aria-label="LF маршрута, %"
                type="number"
                min="0"
                max="100"
                :placeholder="number(s.lf * 100)"
                @input="
                  r.lf =
                    ($event.target as HTMLInputElement).value === ''
                      ? null
                      : Math.max(
                          0,
                          Math.min(100, Number(($event.target as HTMLInputElement).value)),
                        ) / 100
                "
              /><button @click="r.lf = null">Вернуть общее</button>
            </td>
            <td>
              <NumberField v-model="r.fare" label="₽/сегмент" nullable /><button
                @click="r.fare = null"
              >
                По формуле gg
              </button>
            </td>
            <td>
              <NumberField v-model="r.bh" label="Блок-время, ч" nullable /><NumberField
                v-model="r.cost"
                label="Полная стоимость, ₽"
                nullable
              />
              <details>
                <summary>O&D лимит</summary>
                <NumberField v-model="r.od" label="Поездки за период" nullable /><NumberField
                  v-model="r.capture"
                  label="Доля освоения, 0–1"
                  :max="1"
                />
              </details>
            </td>
            <td>{{ number(result.rows.find((x) => x.id === r.id)?.p ?? 0) }}</td>
            <td>{{ money(result.rows.find((x) => x.id === r.id)?.result ?? null) }}</td>
            <td>
              <button
                aria-label="Удалить маршрут"
                @click.stop="s.routes = s.routes.filter((x) => x.id !== r.id)"
              >
                ×
              </button>
            </td>
          </tr>
          <tr v-if="!s.routes.length">
            <td colspan="9">
              Дополнительная программа отсутствует. Выделенные борта продолжают создавать расходы.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
