import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const darkMode = ref(localStorage.getItem('axhub_dark') === 'true')
  const sidebarCollapsed = ref(false)
  const currentProject = ref('')

  function toggleDark() {
    darkMode.value = !darkMode.value
    localStorage.setItem('axhub_dark', String(darkMode.value))
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return { darkMode, sidebarCollapsed, currentProject, toggleDark, toggleSidebar }
})
