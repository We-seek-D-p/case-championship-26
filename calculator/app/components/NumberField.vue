<script setup lang="ts">
const props = defineProps<{
  label: string
  modelValue: number | null
  min?: number
  max?: number
  step?: number
  nullable?: boolean
}>()
const emit = defineEmits<{ 'update:modelValue': [value: number | null] }>()
function update(e: Event) {
  const raw = (e.target as HTMLInputElement).value
  if (raw === '' && props.nullable) {
    emit('update:modelValue', null)
    return
  }
  let value = Math.max(props.min ?? 0, Math.min(props.max ?? Infinity, Number(raw)))
  if (props.step === 1) value = Math.round(value)
  emit('update:modelValue', Number.isFinite(value) ? value : (props.min ?? 0))
}
</script>
<template>
  <label class="field"
    ><span>{{ label }}</span
    ><input
      type="number"
      :value="modelValue"
      :min="min ?? 0"
      :max="max"
      :step="step ?? 'any'"
      :placeholder="nullable ? 'Авто / неизвестно' : ''"
      @input="update"
  /></label>
</template>
