<template>
  <div class="mes-dispos">
    <p v-if="erreur" class="load-error" role="alert">{{ erreur }}</p>

    <CalendrierSemaine
      :lundi="lundi"
      :blocs="blocs"
      @update:lundi="emit('update:lundi', $event)"
      @bloc="cliquerBloc"
    >
      <template #actions>
        <button type="button" class="btn-outline" @click="ouvrirListe">Modifier</button>
        <button type="button" class="btn-dark" @click="ouvrirAjout">Ajouter</button>
      </template>
    </CalendrierSemaine>

    <p class="legend">
      <span class="swatch swatch-type"></span> Planning type (chaque semaine)
      <span class="swatch swatch-semaine"></span> Cette semaine seulement
      <span class="swatch swatch-retiree"></span> Retirée cette semaine (clique pour la remettre)
    </p>

    <!-- Ajouter / modifier une plage -->
    <div v-if="formulaire" class="modal-overlay" @click.self="fermerFormulaire">
      <form
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dispo-form-title"
        @submit.prevent="enregistrer"
      >
        <h2 id="dispo-form-title">
          {{ formulaire.idDispo ? 'Modifier la disponibilité' : 'Ajouter une disponibilité' }}
        </h2>
        <p class="modal-subtitle">
          Semaine du {{ libelle }}
          <template v-if="formulaire.idDispo && formulaire.recurrente">
            · planning type, modifié à partir de cette semaine
          </template>
        </p>

        <fieldset class="field">
          <legend class="field-label">{{ formulaire.idDispo ? 'Jour' : 'Jours' }}</legend>
          <div class="day-chips">
            <button
              v-for="(court, i) in JOURS_COURTS"
              :key="court"
              type="button"
              class="chip"
              :class="{ selected: formulaire.jours.includes(i) }"
              :aria-pressed="formulaire.jours.includes(i)"
              @click="basculerJour(i)"
            >
              {{ court }}
            </button>
          </div>
        </fieldset>

        <label class="check">
          <input v-model="formulaire.touteJournee" type="checkbox" />
          Toute la journée
        </label>

        <div v-if="!formulaire.touteJournee" class="time-row">
          <label class="field">
            <span class="field-label">Heure de début</span>
            <input v-model="formulaire.debut" type="time" step="900" required />
          </label>
          <label class="field">
            <span class="field-label">Heure de fin</span>
            <input v-model="formulaire.fin" type="time" step="900" required />
          </label>
        </div>

        <label v-if="!formulaire.idDispo" class="check">
          <input v-model="formulaire.repeter" type="checkbox" />
          Répéter chaque semaine (planning type)
        </label>

        <p v-if="formErreur" class="form-error" role="alert">{{ formErreur }}</p>

        <div class="modal-actions">
          <button type="button" class="btn-outline wide" @click="fermerFormulaire">Annuler</button>
          <button type="submit" class="btn-dark wide" :disabled="occupe">
            {{ formulaire.idDispo ? 'Enregistrer' : 'Ajouter' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Liste des plages de la semaine -->
    <div v-if="listeOuverte" class="modal-overlay" @click.self="listeOuverte = false">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="dispo-list-title">
        <div class="modal-head">
          <div>
            <h2 id="dispo-list-title">Mes plages de la semaine</h2>
            <p class="modal-subtitle">Semaine du {{ libelle }}</p>
          </div>
          <button type="button" class="close" aria-label="Fermer" @click="listeOuverte = false">
            ×
          </button>
        </div>

        <p v-if="listeErreur" class="form-error" role="alert">{{ listeErreur }}</p>
        <p v-if="plages.length === 0" class="empty">Aucune plage cette semaine.</p>

        <ul class="plage-list">
          <li v-for="p in plages" :key="`${p.id_dispo}-${p.date}`" class="plage-item">
            <div>
              <p class="plage-title">
                {{ JOURS_LONGS[p.jour] }} {{ numeroJour(p.date) }} · {{ horaires(p) }}
              </p>
              <p class="plage-kind">
                <template v-if="p.retiree">Planning type · retirée cette semaine</template>
                <template v-else-if="p.recurrente">Chaque semaine (planning type)</template>
                <template v-else>Cette semaine seulement</template>
              </p>
            </div>
            <div class="plage-actions">
              <template v-if="p.retiree">
                <button
                  type="button"
                  class="btn-outline small"
                  :disabled="occupe"
                  @click="remettre(p)"
                >
                  Remettre
                </button>
              </template>
              <template v-else>
                <button type="button" class="btn-outline small" @click="ouvrirEdition(p)">
                  Modifier
                </button>
                <button
                  v-if="p.recurrente"
                  type="button"
                  class="btn-outline small"
                  :disabled="occupe"
                  @click="retirer(p)"
                >
                  Retirer cette semaine
                </button>
              </template>
              <button
                type="button"
                class="btn-danger small"
                :disabled="occupe"
                :title="
                  p.recurrente
                    ? 'Retire la plage du planning type à partir de cette semaine'
                    : undefined
                "
                @click="supprimer(p)"
              >
                Supprimer
              </button>
            </div>
          </li>
        </ul>
        <p v-if="plages.some((p) => p.recurrente)" class="hint">
          Supprimer une plage du planning type la retire à partir de cette semaine, jamais des
          semaines précédentes.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import CalendrierSemaine from '@/components/CalendrierSemaine.vue'
import { disponibilitesApi } from '@/services/disponibilites'
import { useAuthStore } from '@/stores/auth'
import {
  JOURS_COURTS,
  JOURS_LONGS,
  formatPlage,
  libelleSemaine,
  parseIso,
  toIso,
  versMinutes,
} from '@/utils/semaine'

const props = defineProps({
  lundi: { type: Date, required: true },
})
const emit = defineEmits(['update:lundi', 'modifie'])

const auth = useAuthStore()

const plages = ref([])
const erreur = ref('')
const occupe = ref(false)
const formulaire = ref(null)
const formErreur = ref('')
const listeOuverte = ref(false)
const listeErreur = ref('')

const semaine = computed(() => toIso(props.lundi))
const libelle = computed(() => libelleSemaine(props.lundi))

let sequence = 0
async function charger() {
  const n = ++sequence
  erreur.value = ''
  try {
    const data = await disponibilitesApi.semaine(auth.token, semaine.value)
    if (n === sequence) plages.value = data.plages
  } catch (err) {
    if (n === sequence) erreur.value = err.message
  }
}

watch(semaine, charger, { immediate: true })

function appliquer(data) {
  plages.value = data.plages
  emit('modifie')
}

const numeroJour = (iso) => parseIso(iso).getDate()
const horaires = (p) => formatPlage(versMinutes(p.heure_debut), versMinutes(p.heure_fin, true))

const blocs = computed(() =>
  plages.value.map((p) => {
    const debut = versMinutes(p.heure_debut)
    const fin = versMinutes(p.heure_fin, true)
    const libelleBloc = p.retiree ? 'Retirée cette semaine' : formatPlage(debut, fin)
    return {
      cle: `${p.id_dispo}-${p.date}`,
      jour: p.jour,
      debut,
      fin,
      libelle: libelleBloc,
      aria: `${JOURS_LONGS[p.jour]} ${formatPlage(debut, fin)} : ${libelleBloc}`,
      classe: p.retiree ? 'bloc-retiree' : p.recurrente ? 'bloc-type' : 'bloc-semaine',
      plage: p,
    }
  }),
)

function cliquerBloc(bloc) {
  if (bloc.plage.retiree) remettre(bloc.plage)
  else ouvrirEdition(bloc.plage)
}

function ouvrirAjout() {
  formErreur.value = ''
  formulaire.value = {
    idDispo: null,
    jours: [],
    touteJournee: false,
    debut: '19:00',
    fin: '22:00',
    repeter: false,
  }
}

function ouvrirEdition(p) {
  listeOuverte.value = false
  formErreur.value = ''
  const touteJournee = p.toute_journee
  formulaire.value = {
    idDispo: p.id_dispo,
    recurrente: p.recurrente,
    jours: [p.jour],
    touteJournee,
    debut: touteJournee ? '19:00' : p.heure_debut,
    fin: touteJournee ? '22:00' : p.heure_fin,
  }
}

function fermerFormulaire() {
  formulaire.value = null
}

function basculerJour(i) {
  const f = formulaire.value
  if (f.idDispo) {
    f.jours = [i]
    return
  }
  f.jours = f.jours.includes(i) ? f.jours.filter((j) => j !== i) : [...f.jours, i]
}

async function enregistrer() {
  const f = formulaire.value
  formErreur.value = ''
  if (f.jours.length === 0) {
    formErreur.value = 'Choisis au moins un jour.'
    return
  }
  // Une fin à 00:00 veut dire « jusqu'à minuit ».
  if (!f.touteJournee && f.fin !== '00:00' && f.fin <= f.debut) {
    formErreur.value = "L'heure de fin doit être après l'heure de début."
    return
  }
  const horairesForm = f.touteJournee
    ? { toute_journee: true }
    : { toute_journee: false, heure_debut: f.debut, heure_fin: f.fin === '00:00' ? '23:59' : f.fin }

  occupe.value = true
  try {
    const data = f.idDispo
      ? await disponibilitesApi.modifier(auth.token, f.idDispo, {
          semaine: semaine.value,
          jour: f.jours[0],
          ...horairesForm,
        })
      : await disponibilitesApi.ajouter(auth.token, {
          semaine: semaine.value,
          jours: f.jours,
          repeter: f.repeter,
          ...horairesForm,
        })
    appliquer(data)
    formulaire.value = null
  } catch (err) {
    formErreur.value = err.message
  } finally {
    occupe.value = false
  }
}

function ouvrirListe() {
  listeErreur.value = ''
  listeOuverte.value = true
}

async function action(appel) {
  listeErreur.value = ''
  erreur.value = ''
  occupe.value = true
  try {
    appliquer(await appel())
  } catch (err) {
    if (listeOuverte.value) listeErreur.value = err.message
    else erreur.value = err.message
  } finally {
    occupe.value = false
  }
}

const supprimer = (p) =>
  action(() => disponibilitesApi.supprimer(auth.token, p.id_dispo, semaine.value))
const retirer = (p) =>
  action(() => disponibilitesApi.retirerCetteSemaine(auth.token, p.id_dispo, semaine.value))
const remettre = (p) =>
  action(() => disponibilitesApi.remettreCetteSemaine(auth.token, p.id_dispo, semaine.value))
</script>

<style scoped>
button {
  font-family: inherit;
}

.btn-outline,
.btn-dark,
.btn-danger {
  border-radius: 30px;
  padding: 9px 18px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-outline {
  background: white;
  color: #1c1e21;
  border: 1px solid #dcdfe4;
}

.btn-outline:hover {
  background: #f4f5f7;
}

.btn-dark {
  background: #111;
  color: white;
  border: 1px solid #111;
}

.btn-dark:hover {
  background: #000;
}

.btn-danger {
  background: white;
  color: #b3261e;
  border: 1px solid #b3261e;
}

.btn-danger:hover {
  background: #fdf0ef;
}

.small {
  padding: 7px 14px;
  font-size: 0.85rem;
}

.wide {
  flex: 1;
  padding: 12px 18px;
}

button:disabled {
  opacity: 0.6;
  cursor: default;
}

/* Blocs du calendrier (couleurs de la maquette) */
.mes-dispos :deep(.bloc-type) {
  background: #b9d0f5;
  color: #10284f;
}

.mes-dispos :deep(.bloc-semaine) {
  background: #2d62c8;
  color: white;
}

.mes-dispos :deep(.bloc-retiree) {
  background: white;
  color: #2d62c8;
  box-shadow: inset 0 0 0 1.5px #2d62c8;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 8px;
  margin: 12px 4px 0;
  font-size: 0.8rem;
  color: #65676b;
}

.swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 4px;
  margin-left: 8px;
}

.swatch:first-child {
  margin-left: 0;
}

.swatch-type {
  background: #b9d0f5;
}

.swatch-semaine {
  background: #2d62c8;
}

.swatch-retiree {
  background: white;
  box-shadow: inset 0 0 0 1.5px #2d62c8;
}

.load-error {
  background: #fdf0ef;
  color: #c0322b;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 0 12px;
  font-size: 0.9rem;
}

/* --- Modales --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 540px;
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  padding: 28px 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.modal h2 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: #000;
}

.modal-subtitle {
  margin: 6px 0 20px;
  color: #65676b;
  font-size: 0.95rem;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.close {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #eef0f3;
  font-size: 1.3rem;
  cursor: pointer;
  flex-shrink: 0;
}

fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  flex: 1;
}

.field-label {
  font-size: 0.85rem;
  color: #65676b;
  padding: 0;
  margin-bottom: 8px;
}

label.field .field-label {
  margin-bottom: 0;
}

.day-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border: 1px solid #dcdfe4;
  background: white;
  border-radius: 30px;
  padding: 9px 16px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  color: #1c1e21;
}

.chip.selected {
  background: #111;
  border-color: #111;
  color: white;
}

.check {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 4px 0 16px;
  font-size: 0.95rem;
  cursor: pointer;
}

.check input {
  width: 18px;
  height: 18px;
}

.time-row {
  display: flex;
  gap: 14px;
}

.time-row input {
  border: 1px solid #e4e6eb;
  background: #f4f5f7;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 1rem;
  font-family: inherit;
  width: 100%;
}

.form-error {
  color: #c0322b;
  font-size: 0.9rem;
  margin: 0 0 12px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.empty {
  color: #65676b;
  text-align: center;
  padding: 16px 0;
}

.plage-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.plage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: #f4f5f7;
  border-radius: 14px;
  padding: 12px 14px;
}

.plage-title {
  margin: 0;
  font-weight: 600;
  color: #000;
}

.plage-kind {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: #65676b;
}

.plage-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.hint {
  margin: 14px 0 0;
  font-size: 0.8rem;
  color: #65676b;
}

@media (max-width: 600px) {
  .plage-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .plage-actions {
    justify-content: flex-start;
  }
  .modal {
    padding: 22px;
  }
}
</style>
