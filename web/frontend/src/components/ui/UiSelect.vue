<script setup lang="ts">
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue'

type Option = { value: string; label: string }

const model = defineModel<string>({ required: true })
defineProps<{
  options: Option[]
}>()
</script>

<template>
  <Listbox v-model="model">
    <div class="ui-select-wrap">
      <ListboxButton class="ui-select-btn">
        <span>{{ options.find(o => o.value === model)?.label }}</span>
      </ListboxButton>
      <ListboxOptions class="ui-select-options">
        <ListboxOption
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          v-slot="{ active, selected }"
          as="template"
        >
          <li
            class="ui-select-option"
            :class="active ? 'ui-select-option--active' : 'ui-select-option--idle'"
          >
            <span :class="selected ? 'ui-select-option--selected' : ''">{{ option.label }}</span>
          </li>
        </ListboxOption>
      </ListboxOptions>
    </div>
  </Listbox>
</template>

<style scoped>
.ui-select-wrap { position: relative; }
.ui-select-btn {
  height: 2.25rem;
  width: 100%;
  border-radius: 0.4rem;
  border: 1px solid var(--border);
  background: var(--bg-tertiary);
  padding: 0 0.75rem;
  text-align: left;
  font-size: 0.875rem;
  color: var(--text-primary);
}
.ui-select-options {
  position: absolute;
  z-index: 30;
  margin-top: 0.25rem;
  max-height: 14rem;
  width: 100%;
  overflow: auto;
  border-radius: 0.4rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  padding: 0.25rem 0;
}
.ui-select-option { cursor: pointer; padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.ui-select-option--idle { color: var(--text-secondary); }
.ui-select-option--active { background: var(--bg-tertiary); color: var(--text-primary); }
.ui-select-option--selected { font-weight: 600; color: var(--text-primary); }
</style>
