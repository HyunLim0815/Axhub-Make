import { defineStore } from 'pinia'
import { darkTheme } from 'naive-ui'

export const useAppStore = defineStore('app', () => {
  const darkMode = ref(false)
  const sidebarCollapsed = ref(false)
  const currentProject = ref('')

  const naiveTheme = computed(() => (darkMode.value ? darkTheme : null))

  function toggleDark() {
    darkMode.value = !darkMode.value
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return { darkMode, sidebarCollapsed, currentProject, naiveTheme, toggleDark, toggleSidebar }
})
