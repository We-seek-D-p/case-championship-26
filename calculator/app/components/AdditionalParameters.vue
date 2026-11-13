<script setup lang="ts">
import type { Scenario } from '../domain/scenario'
import type { Dataset } from '../domain/data'
import type { calculate } from '../domain/economics'
import { rotationCheck } from '../domain/economics'
import { number, money } from '../utils/format'
const s = defineModel<Scenario>({ required: true })
defineProps<{ result: ReturnType<typeof calculate>; data: Dataset }>()
</script>
<template>
  <section class="panel">
    <details>
      <summary>Дополнительные параметры · затраты, пересадки, груз</summary>
      <div class="parameter-grid">
        <NumberField
          v-model="s.cannibalization"
          label="Каннибализация, доля 0–1"
          :max="1"
        /><NumberField v-model="s.lostMargin" label="Потерянная маржа, ₽/сегмент" /><NumberField
          v-model="s.displacedP"
          label="Вытесненные сегменты за период"
        /><NumberField v-model="s.displacedCM" label="Вытесненный CM за период, ₽" /><NumberField
          v-model="s.baseCost"
          label="База, ₽/год"
        /><NumberField v-model="s.personnel" label="Персонал, ₽/год" /><NumberField
          v-model="s.infrastructure"
          label="Инфраструктура, ₽/год"
        /><NumberField v-model="s.launch" label="Разовые затраты запуска, ₽" /><NumberField
          v-model="s.expense"
          label="Множитель стоимости вылета"
        /><NumberField
          v-model="s.discount"
          label="Пересадочная скидка всему тарифу, 0–1"
          :max="1"
        /><NumberField
          v-model="s.transferShare"
          label="Пересадочные сегменты, доля 0–1"
          :max="1"
        /><NumberField v-model="s.mct" label="Плановое MCT, минут" />
      </div>
      <p>
        Операционный: {{ money(result.result) }} · Первый период после запуска:
        {{ money(result.first) }}
      </p>
      <p>
        Местные сегменты: {{ number(result.p - result.transferSegments) }} · Пересадочные сегменты:
        {{ number(result.transferSegments) }} / O&D-поездки: {{ number(result.transferJourneys) }}.
        Уже внутри загрузки.
        {{
          rotationCheck(s, data.airports)
            ? 'Геометрия эталонных ротаций проходит проверку времени.'
            : 'Стыковки и расписание не проверены.'
        }}
      </p>
      <p v-if="s.transfers">
        Потенциальные связи:
        {{ s.routes.map((r) => r.destination).join(' ↔ ' + s.base + ' ↔ ') }}. Нужны слоты,
        согласование багажа и MCT.
      </p>
      <hr />
      <label class="check"
        ><input v-model="s.cargo.enabled" type="checkbox" /> Груз в БГО · сценарная оценка</label
      >
      <p>Свободная ёмкость после багажа, спрос и договоры не подтверждены.</p>
      <div v-if="s.cargo.enabled" class="parameter-grid">
        <NumberField v-model="s.cargo.kg" label="кг на вылет" /><NumberField
          v-model="s.cargo.tariff"
          label="Тариф, ₽/кг"
        /><NumberField v-model="s.cargo.handling" label="Handling, ₽/кг" /><NumberField
          v-model="s.cargo.weight"
          label="Масса, ₽/кг"
        /><NumberField
          v-model="s.cargo.commission"
          label="Комиссия, доля 0–1"
          :max="1"
        /><NumberField
          v-model="s.cargo.fixed"
          label="Фиксированные расходы за период, ₽"
        /><NumberField v-model="s.cargo.limit" label="Подтверждённый лимит, кг/вылет" nullable />
      </div>
      <p v-if="s.cargo.enabled">
        Пассажирский результат {{ money(result.passenger) }} · Грузовой эффект
        {{ money(result.cargo) }} · Суммарно {{ money(result.result) }}
      </p>
    </details>
  </section>
</template>
