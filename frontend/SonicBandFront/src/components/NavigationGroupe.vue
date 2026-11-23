<template>
  <nav class="group-tabs" aria-label="Sections du groupe">
    <button
      v-for="tab in tabsBeforeEquipment"
      :key="tab.id"
      type="button"
      class="tab"
      :class="{ active: tab.id === activeTab }"
      :disabled="tab.disabled"
      :title="tab.disabled ? 'Bientôt disponible' : undefined"
      @click="$emit('select', tab.id)"
    >
      <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        stroke="currentColor"
        stroke-width="2"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path v-for="(d, i) in tab.icon" :key="i" :d="d" />
      </svg>
      {{ tab.label }}
    </button>
    <RouterLink
      :to="{ name: 'group-equipment', params: { id: idGrp } }"
      class="tab"
      :class="{ active: activeTab === 'equipement' }"
    >
      <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        stroke="currentColor"
        stroke-width="2"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path
          d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
        />
      </svg>
      Équipement
    </RouterLink>
    <button
      v-for="tab in tabsAfterEquipment"
      :key="tab.id"
      type="button"
      class="tab"
      :class="{ active: tab.id === activeTab }"
      :disabled="tab.disabled"
      :title="tab.disabled ? 'Bientôt disponible' : undefined"
      @click="$emit('select', tab.id)"
    >
      <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        stroke="currentColor"
        stroke-width="2"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path v-for="(d, i) in tab.icon" :key="i" :d="d" />
      </svg>
      {{ tab.label }}
    </button>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  idGrp: { type: [Number, String], required: true },
  activeTab: { type: String, required: true },
})

defineEmits(['select'])

const tabsBeforeEquipment = [
  {
    id: 'apercu',
    label: 'Aperçu',
    disabled: false,
    icon: ['M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z', 'M9 22V12h6v10'],
  },
  {
    id: 'dispos',
    label: 'Disponibilités',
    disabled: true,
    icon: [
      'M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z',
      'M16 2v4',
      'M8 2v4',
      'M3 10h18',
    ],
  },
  {
    id: 'repertoires',
    label: 'Répertoires',
    disabled: false,
    icon: [
      'M9 18V5l12-2v13',
      'M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
      'M18 19a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    ],
  },
]

const tabsAfterEquipment = [
  {
    id: 'membres',
    label: 'Membres',
    disabled: false,
    icon: [
      'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2',
      'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
      'M22 21v-2a4 4 0 0 0-3-3.87',
      'M16 3.13a4 4 0 0 1 0 7.75',
    ],
  },
]
</script>

<style scoped>
.group-tabs {
  display: flex;
  gap: 4px;
  background-color: #e4e6eb;
  border-radius: 30px;
  padding: 5px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: transparent;
  border-radius: 30px;
  padding: 10px 18px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #65676b;
  white-space: nowrap;
  text-decoration: none;
  font-family: inherit;
}

.tab:not(:disabled) {
  cursor: pointer;
}

.tab:disabled {
  cursor: default;
}

.tab.active {
  background: white;
  color: #1c1e21;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
</style>
