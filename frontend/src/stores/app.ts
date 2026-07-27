import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { darkTheme } from 'element-plus'

export const useAppStore = defineStore('app', () => {
  const darkMode = ref(localStorage.getItem('axhub_dark') === 'true')

  function toggleDark() {
    darkMode.value = !darkMode.value
    localStorage.setItem('axhub_dark', String(darkMode.value))
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  return { darkMode, toggleDark }
})
