<script setup lang="ts">
import type { Dataset } from '../domain/data'
defineProps<{ data: Dataset }>()
</script>
<template>
  <section class="panel sources">
    <h2>Откуда взяты числа</h2>
    <p>
      Данные {{ data.gitSha }} · ревизия {{ data.dataRevision }}.
      {{ data.airports.filter((a) => a.primary).length }} основных площадки,
      {{ data.observations.length }} исторических наблюдения.
    </p>
    <p>
      Параметры экономики — scenario из analysis/calculate.py; вместимость SSJ100 исправлена на 100.
      Исторические наблюдения сохраняют исходные кресла. Полный поток аэропорта не является O&D
      пары. observed — опубликованное значение по реестру, без новой независимой проверки.
    </p>
    <p>
      При коротком периоде регулярные годовые расходы и ресурс масштабируются на недели / 52.
      Разовые затраты запуска не масштабируются. Год сам по себе не включает инфляцию и поставки.
    </p>
    <p>
      MRV — летняя база по источнику; круглогодичная работа — допущение. Геометрия ВПП и каталожная
      дальность не подтверждают эксплуатационный допуск. SJ-100/ПД-8 не равен SSJ100/SaM146. Пустой
      RED_WINGS_FLEET.md не использован как доказательство.
    </p>
    <p>
      Исторический слой: одна линия на неориентированную пару за выбранный год, первое наблюдение в
      CSV; частоты зеркал и пересекающихся окон не суммируются. Исходные наблюдения остаются
      доступны ниже.
    </p>
    <details>
      <summary>Реестр источников ({{ data.sources.length }})</summary>
      <p v-for="source in data.sources" :key="source.source_id ?? ''">
        <a
          v-if="source.url?.startsWith('https:')"
          :href="source.url"
          target="_blank"
          rel="noopener noreferrer"
          >{{ source.source_id }} · {{ source.title }}</a
        ><span v-else>{{ source.source_id }} · {{ source.title }}</span>
      </p>
    </details>
    <details>
      <summary>Исторические наблюдения и оговорки</summary>
      <p v-for="(r, i) in data.observations" :key="i">
        {{ r.origin_iata }}–{{ r.destination_iata }} · {{ r.year }} · {{ r.valid_from ?? '?' }} /
        {{ r.valid_to ?? '?' }} · {{ r.carrier ?? 'Неизвестный перевозчик' }} · {{ r.source_id }} ·
        {{ r.source_locator }} · {{ r.notes }}
      </p>
    </details>
    <details>
      <summary>Происхождение отдельных мер</summary>
      <p v-for="(r, i) in data.lineage" :key="i">
        {{ r.entity_id }} · {{ r.period }} · {{ r.metric }} · {{ r.value_origin }} ·
        {{ r.source_ids }} · {{ r.method }}
      </p>
    </details>
    <p>
      Конфликты координат при объединении: {{ data.conflicts.join(', ') || 'нет' }}. Приоритет
      airports.csv.
    </p>
    <a href="https://flyredwings.com/about/park/" target="_blank" rel="noopener"
      >Каталог ВС · проверка 13.11.2026</a
    >
  </section>
</template>
