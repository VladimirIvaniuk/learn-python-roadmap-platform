<script setup lang="ts">
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from '@headlessui/vue'

defineProps<{
  tabs: Array<{ id: string; label: string }>
  selectedIndex?: number
  testIdPrefix?: string
}>()

const emit = defineEmits<{
  change: [index: number]
}>()
</script>

<template>
  <TabGroup as="div" class="ui-tabs-root" :selected-index="selectedIndex ?? 0" @change="(index) => emit('change', index)">
    <TabList class="tabs ui-tabs-list">
      <Tab
        v-for="tab in tabs"
        :key="tab.id"
        v-slot="{ selected }"
        as="template"
      >
        <button
          :data-testid="testIdPrefix ? `${testIdPrefix}-${tab.id}` : undefined"
          class="tab ui-tab-btn"
          :class="selected ? 'active ui-tab-btn--active' : 'ui-tab-btn--idle'"
        >
          {{ tab.label }}
        </button>
      </Tab>
    </TabList>
    <TabPanels class="ui-tab-panels">
      <TabPanel v-for="tab in tabs" :key="tab.id" class="tab-content ui-tab-panel">
        <slot :name="tab.id" />
      </TabPanel>
    </TabPanels>
  </TabGroup>
</template>

<style scoped>
.ui-tabs-root {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}
.ui-tabs-list {
  display: flex;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  padding: 0.25rem;
}
.ui-tab-panels {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.ui-tab-btn {
  flex: 1;
  border: none;
  background: transparent;
  border-radius: 0.4rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  transition: color 0.15s ease, background-color 0.15s ease;
}
.ui-tab-btn--idle { color: var(--text-secondary); }
.ui-tab-btn--active { background: var(--accent); color: #fff; }
.ui-tab-panel {
  padding-top: 0.75rem;
  min-height: 0;
}
</style>
