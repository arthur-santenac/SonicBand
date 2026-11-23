<template>
  <div class="dispos-groupe">
    <p v-if="erreur" class="load-error" role="alert">{{ erreur }}</p>

    <CalendrierSemaine :lundi="lundi" :blocs="blocs" @update:lundi="emit('update:lundi', $event)">
      <template #infobulle="{ bloc }">
        <strong class="tip-title">
          {{ JOURS_LONGS[bloc.jour] }} · {{ formatPlage(bloc.debut, bloc.fin) }}
        </strong>
        <span class="tip-line">
          <span class="tip-dot dot-free"></span>
          Libres ({{ bloc.libres.length }}/{{ membres.length }}) : {{ noms(bloc.libres) }}
        </span>
        <span v-if="bloc.pasLibres.length" class="tip-line">
          <span class="tip-dot dot-busy"></span>
          Pas libres : {{ noms(bloc.pasLibres) }}
        </span>
        <span v-if="bloc.nonRenseignes.length" class="tip-line">
          <span class="tip-dot dot-none"></span>
          Pas encore renseigné : {{ noms(bloc.nonRenseignes) }}
        </span>
      </template>
    </CalendrierSemaine>

    <div class="legend" aria-hidden="true">
      <span>1 musicien libre</span>
      <span class="gradient" :style="{ background: degrade }"></span>
      <span>Tout le groupe ({{ membres.length }})</span>
    </div>
    <p v-if="nonRenseignes.length" class="missing">
      Pas encore de disponibilités : {{ noms(nonRenseignes.map((m) => m.id_user)) }}
    </p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import CalendrierSemaine from '@/components/CalendrierSemaine.vue'
import { disponibilitesApi } from '@/services/disponibilites'
import { useAuthStore } from '@/stores/auth'
import { JOURS_LONGS, couleurHeatmap, degradeHeatmap, formatPlage, toIso } from '@/utils/semaine'

const props = defineProps({
  idGrp: { type: Number, required: true },
  lundi: { type: Date, required: true },
  // Incrémenté par le parent quand mes disponibilités changent.
  version: { type: Number, default: 0 },
})
const emit = defineEmits(['update:lundi'])

const auth = useAuthStore()
const membres = ref([])
const creneaux = ref([])
const erreur = ref('')

const degrade = degradeHeatmap()

let sequence = 0
async function charger() {
  const n = ++sequence
  erreur.value = ''
  try {
    const data = await disponibilitesApi.duGroupe(auth.token, props.idGrp, toIso(props.lundi))
    if (n !== sequence) return
    membres.value = data.membres
    creneaux.value = data.creneaux
  } catch (err) {
    if (n === sequence) erreur.value = err.message
  }
}

watch(() => [props.idGrp, toIso(props.lundi), props.version], charger, { immediate: true })

const nomsParId = computed(() => new Map(membres.value.map((m) => [m.id_user, m.nom_user])))
const nonRenseignes = computed(() => membres.value.filter((m) => !m.renseigne))

function noms(ids) {
  return ids.map((id) => nomsParId.value.get(id) ?? '?').join(', ')
}

const blocs = computed(() =>
  creneaux.value.map((c) => {
    const libres = new Set(c.disponibles)
    const pasLibres = membres.value.filter((m) => m.renseigne && !libres.has(m.id_user))
    const total = membres.value.length
    return {
      cle: `${c.date}-${c.debut}`,
      jour: c.jour,
      debut: c.debut,
      fin: c.fin,
      libelle: `${c.disponibles.length}/${total}`,
      aria: `${JOURS_LONGS[c.jour]} ${formatPlage(c.debut, c.fin)} : ${c.disponibles.length} sur ${total} libres (${noms(c.disponibles)})`,
      style: couleurHeatmap(c.disponibles.length, total),
      libres: c.disponibles,
      pasLibres: pasLibres.map((m) => m.id_user),
      nonRenseignes: nonRenseignes.value.map((m) => m.id_user),
    }
  }),
)
</script>

<style scoped>
.dispos-groupe :deep(.bloc) {
  border-radius: 4px;
  cursor: default;
  justify-content: center;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  white-space: nowrap;
  align-items: center;
  gap: 10px;
  margin: 12px 4px 0;
  font-size: 0.8rem;
  color: #65676b;
}

.gradient {
  width: 140px;
  height: 10px;
  border-radius: 5px;
}

.missing {
  margin: 8px 4px 0;
  font-size: 0.8rem;
  color: #65676b;
}

.tip-title {
  display: block;
  margin-bottom: 6px;
}

.tip-line {
  display: block;
  margin-top: 2px;
}

.tip-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dot-free {
  background: #6f9cf0;
}

.dot-busy {
  background: #e98b84;
}

.dot-none {
  background: #9aa0a6;
}

.load-error {
  background: #fdf0ef;
  color: #c0322b;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 0 12px;
  font-size: 0.9rem;
}
</style>
