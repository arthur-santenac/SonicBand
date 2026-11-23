<template>
  <section class="calendar-card">
    <div class="calendar-toolbar">
      <div class="week-nav">
        <button
          type="button"
          class="nav-arrow"
          aria-label="Semaine précédente"
          @click="changerSemaine(-7)"
        >
          ‹
        </button>
        <span class="week-label" aria-live="polite">{{ libelle }}</span>
        <button
          type="button"
          class="nav-arrow"
          aria-label="Semaine suivante"
          @click="changerSemaine(7)"
        >
          ›
        </button>
        <button
          type="button"
          class="current-week"
          :class="{ active: estSemaineActuelle }"
          :disabled="estSemaineActuelle"
          @click="emit('update:lundi', lundiDe())"
        >
          Semaine actuelle
        </button>
      </div>
      <div class="toolbar-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <div class="calendar-scroll">
      <div class="calendar" :style="{ '--hauteur-heure': `${HAUTEUR_HEURE}px` }">
        <div class="corner"></div>
        <div
          v-for="jour in jours"
          :key="jour.iso"
          class="day-head"
          :class="{ today: jour.iso === aujourdhui }"
        >
          {{ jour.court }} {{ jour.numero }}
        </div>

        <div class="hours" aria-hidden="true">
          <span v-for="h in 24" :key="h" class="hour-label">{{ h - 1 }}h</span>
        </div>

        <div
          v-for="jour in jours"
          :key="`col-${jour.iso}`"
          class="day-col"
          :aria-label="`${JOURS_LONGS[jour.index]} ${jour.numero}`"
          role="group"
        >
          <button
            v-for="bloc in blocsParJour[jour.index]"
            :key="bloc.cle"
            type="button"
            class="bloc"
            :class="bloc.classe"
            :style="positionner(bloc)"
            :aria-label="bloc.aria || bloc.libelle"
            @click="emit('bloc', bloc)"
            @mouseenter="survole = bloc.cle"
            @mouseleave="survole = null"
            @focus="survole = bloc.cle"
            @blur="survole = null"
          >
            <span v-if="(bloc.fin - bloc.debut) * HAUTEUR_HEURE >= 18 * 60" class="bloc-label">
              {{ bloc.libelle }}
            </span>
            <span
              v-if="survole === bloc.cle && $slots.infobulle"
              class="tooltip"
              :class="{ 'tooltip-left': bloc.jour >= 5, 'tooltip-up': bloc.debut >= 16 * 60 }"
              role="tooltip"
            >
              <slot name="infobulle" :bloc="bloc"></slot>
            </span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  JOURS_LONGS,
  ajouterJours,
  joursDeLaSemaine,
  libelleSemaine,
  lundiDe,
  toIso,
} from '@/utils/semaine'

// Hauteur (px) d'une heure dans la grille.
const HAUTEUR_HEURE = 20

const props = defineProps({
  // Lundi de la semaine affichée (Date).
  lundi: { type: Date, required: true },
  // Blocs à placer : { cle, jour (0 = lundi), debut, fin (minutes), libelle, classe?, style?, aria? }
  blocs: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:lundi', 'bloc'])

const survole = ref(null)
const aujourdhui = toIso(new Date())

const jours = computed(() => joursDeLaSemaine(props.lundi))
const libelle = computed(() => libelleSemaine(props.lundi))
const estSemaineActuelle = computed(() => toIso(props.lundi) === toIso(lundiDe()))

const blocsParJour = computed(() => {
  const parJour = [[], [], [], [], [], [], []]
  for (const bloc of props.blocs) parJour[bloc.jour]?.push(bloc)
  return parJour
})

function changerSemaine(nbJours) {
  survole.value = null
  emit('update:lundi', ajouterJours(props.lundi, nbJours))
}

function positionner(bloc) {
  return {
    top: `${(bloc.debut / 60) * HAUTEUR_HEURE}px`,
    height: `${((bloc.fin - bloc.debut) / 60) * HAUTEUR_HEURE}px`,
    ...bloc.style,
  }
}
</script>

<style scoped>
.calendar-card {
  background: white;
  border-radius: 20px;
  padding: 16px 20px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  min-width: 0;
}

.calendar-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.week-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-arrow {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #dcdfe4;
  background: white;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  color: #1c1e21;
}

.nav-arrow:hover {
  background: #f4f5f7;
}

.week-label {
  min-width: 112px;
  text-align: center;
  font-weight: 600;
  font-size: 0.95rem;
}

.current-week {
  border: none;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 0.85rem;
  font-weight: 500;
  background: #eef0f3;
  color: #1c1e21;
  cursor: pointer;
  font-family: inherit;
}

.current-week.active {
  cursor: default;
}

.current-week:not(.active):hover {
  background: #e4e6eb;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
}

.calendar-scroll {
  overflow-x: auto;
}

.calendar {
  display: grid;
  grid-template-columns: 40px repeat(7, minmax(72px, 1fr));
  grid-template-rows: auto calc(24 * var(--hauteur-heure));
  min-width: 560px;
}

.corner {
  grid-row: 1;
}

.day-head {
  text-align: center;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 6px 0 10px;
  color: #1c1e21;
}

.day-head.today {
  font-weight: 700;
  color: #2d62c8;
}

.hours {
  grid-row: 2;
  display: flex;
  flex-direction: column;
}

.hour-label {
  height: var(--hauteur-heure);
  font-size: 0.7rem;
  color: #65676b;
  text-align: right;
  padding-right: 8px;
  transform: translateY(-0.45em);
}

.hour-label:first-child {
  transform: none;
}

.day-col {
  grid-row: 2;
  position: relative;
  border-left: 1px solid #eceef1;
  background-image: linear-gradient(to bottom, #eceef1 1px, transparent 1px);
  background-size: 100% var(--hauteur-heure);
}

.day-col:last-child {
  border-right: 1px solid #eceef1;
}

.calendar .day-col {
  border-bottom: 1px solid #eceef1;
}

.bloc {
  position: absolute;
  left: 2px;
  right: 2px;
  border: none;
  border-radius: 6px;
  padding: 0 8px;
  display: flex;
  align-items: center;
  text-align: left;
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  overflow: visible;
}

.bloc:focus-visible {
  outline: 2px solid #111;
  outline-offset: 1px;
  z-index: 3;
}

.bloc:hover {
  z-index: 2;
}

.bloc-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tooltip {
  position: absolute;
  top: 0;
  left: calc(100% + 8px);
  z-index: 10;
  min-width: 200px;
  max-width: 260px;
  background: #1c1e21;
  color: white;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 0.8rem;
  font-weight: 400;
  line-height: 1.4;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  pointer-events: none;
  cursor: default;
}

.tooltip-left {
  left: auto;
  right: calc(100% + 8px);
}

.tooltip-up {
  top: auto;
  bottom: 0;
}
</style>
