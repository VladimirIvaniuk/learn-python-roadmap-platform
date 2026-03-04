<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useProgressStore } from './stores/progress'
import { useAuthStore } from './stores/auth'

const progress = useProgressStore()
const auth = useAuthStore()

onMounted(async () => {
  await auth.validateSession()
  await progress.load()
})
</script>

<template>
  <RouterView />
</template>
