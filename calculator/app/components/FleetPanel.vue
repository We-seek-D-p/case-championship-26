<script setup lang="ts">
import { computed, ref } from 'vue'
import { profiles } from '../domain/data'
import { createAllocation, replaceFleetType } from '../domain/fleet'
import type { Scenario } from '../domain/scenario'
import type { calculate } from '../domain/economics'
import { number } from '../utils/format'
const s = defineModel<Scenario>({ required: true })
defineProps<{ result: ReturnType<typeof calculate> }>()
const nextType = ref('')
const availableTypes = computed(() =>
  profiles.filter((profile) => !s.value.fleet.some((item) => item.type === profile.id)),
)
function addType() {
  if (!availableTypes.value.some((profile) => profile.id === nextType.value)) return
  s.value.fleet.push(createAllocation(nextType.value))
  nextType.value = ''
}
function assignedRoutes(type: string) {
  return s.value.routes.filter((route) => route.type === type).length
}
function removeType(type: string) {
  if (assignedRoutes(type)) return
  s.value.fleet = s.value.fleet.filter((item) => item.type !== type)
}
</script>
<template>
  <section class="panel">
    <h2>Ресурс программы</h2>
    <p>
      2+1 SSJ100 — сценарное распределение. Каталог не подтверждает свободные исправные борта.
      Резерв оплачивается, плановый налёт не производит.
    </p>
    <div class="add-route">
      <select v-model="nextType" aria-label="Добавить тип самолёта во флот">
        <option disabled value="">Выберите тип самолёта</option>
        <option v-for="profile in availableTypes" :key="profile.id" :value="profile.id">
          {{ profile.id }} · {{ profile.seats ?? 'неизвестно' }} мест
        </option>
      </select>
      <button class="primary" :disabled="!nextType" @click="addType">+ Тип ВС</button>
    </div>
    <p>
      Смена типа в карточке обновляет самолёт и кресла на назначенных ему маршрутах. Число бортов
      сохраняется; блок-время и затраты прежнего типа сбрасываются. Для других типов нужен
      собственный профиль затрат.
    </p>
    <div v-for="f in s.fleet" :key="f.type" class="fleet-row">
      <div class="section-title">
        <label class="field"
          >Тип самолёта
          <select
            :value="f.type"
            :aria-label="`Тип самолёта вместо ${f.type}`"
            @change="replaceFleetType(s, f.type, ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="profile in profiles"
              :key="profile.id"
              :value="profile.id"
              :disabled="profile.id !== f.type && s.fleet.some((item) => item.type === profile.id)"
            >
              {{ profile.id }} · {{ profile.seats ?? 'неизвестно' }} мест
            </option>
          </select>
        </label>
        <button
          :disabled="assignedRoutes(f.type) > 0"
          :title="
            assignedRoutes(f.type)
              ? 'Сначала переназначьте маршруты на другой тип'
              : 'Снять выделение бортов и их расходы'
          "
          @click="removeType(f.type)"
        >
          Удалить тип
        </button>
      </div>
      <p>
        В каталоге {{ profiles.find((p) => p.id === f.type)?.total }} бортов · назначено маршрутов:
        {{ assignedRoutes(f.type) }}. Кресла:
        {{ profiles.find((p) => p.id === f.type)?.seats ?? 'нужны данные' }}.
      </p>
      <div class="parameter-grid">
        <NumberField v-model="f.available" label="Доступно программе" :step="1" /><NumberField
          v-model="f.working"
          label="Рабочих выделено"
          :step="1"
        /><NumberField v-model="f.reserve" label="Резервных выделено" :step="1" /><NumberField
          v-model="f.peak"
          label="Минимум по пику"
          :step="1"
        /><NumberField v-model="f.resource" label="Ресурс, BH/борт/год" nullable /><NumberField
          v-model="f.fixed"
          label="Владение, ₽/выделенный борт/год"
          nullable
        />
      </div>
      <p v-for="check in result.fleet.filter((x) => x.type === f.type)" :key="check.type">
        Налёт {{ number(check.hours) }} BH · требуется {{ check.required ?? 'Нужен профиль' }} ·
        дефицит {{ check.deficit ?? 'неизвестен' }} бортов / {{ number(check.hourDeficit) }} BH
      </p>
    </div>
    <details>
      <summary>Сценарий будущих поставок · не распределён в программу</summary>
      <p>
        IV кв. 2027: +1 SJ-100 / +1 Ту-214; 2028: +4/+2; 2029: +6/+3; 2030: +4/+5. Не
        гарантированный исправный парк; выбытие не определено. Распределение — вручную, ресурс и
        затраты отдельно.
      </p>
    </details>
  </section>
</template>
