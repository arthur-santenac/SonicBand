<template>
  <AppLayout>
    <template #header-center>
      <NavigationGroupe
        :id-grp="route.params.id"
        active-tab="equipement"
        @select="naviguerVersOnglet"
      />
    </template>

    <main class="main-content equipment-page">
      <header class="content-header">
        <div>
          <h1>Équipement</h1>
          <p class="subtitle">
            Tout le matériel de {{ group?.nom_grp || 'ce groupe' }} et à qui il appartient.
          </p>
        </div>
        <button
          type="button"
          class="btn-primary"
          :disabled="loading || !group"
          @click="openModal('groupe')"
        >
          + Ajouter un équipement du groupe
        </button>
      </header>

      <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
      <p v-if="loading" class="empty-state" aria-live="polite">Chargement des équipements…</p>

      <template v-else-if="group">
        <section
          class="equipment-section"
          aria-labelledby="group-equipment-title"
        >
          <h2 id="group-equipment-title" class="visually-hidden">Équipements du groupe</h2>
          <div class="table-header" aria-hidden="true">
            <span class="col-name">Équipement</span>
            <span class="col-owner">Membre</span>
            <span class="col-actions"></span>
          </div>

          <div class="equipment-list">
            <div
              class="equipment-item"
              v-for="item in groupEquipment"
              :key="item.id_equipement"
            >
              <span class="item-name">{{ item.nom_equipement }}</span>
              <span class="item-owner">{{ item.proprietaire }}</span>
              <button
                v-if="item.est_equipement_groupe"
                type="button"
                class="btn-text-danger"
                :disabled="busy"
                @click="removeGroupEquipment(item.id_equipement)"
              >
                Supprimer
              </button>
            </div>
            <p v-if="groupEquipment.length === 0" class="empty-state">
              Aucun équipement enregistré pour ce groupe.
            </p>
          </div>
        </section>

        <section
          class="my-equipment-section"
          aria-labelledby="my-equipment-title"
        >
          <header class="section-header">
            <div>
              <h2 id="my-equipment-title">Mes équipements</h2>
              <p class="subtitle">Visibles par tous les membres du groupe.</p>
            </div>
          </header>

          <div class="equipment-list">
            <div
              class="equipment-item"
              v-for="item in myEquipment"
              :key="item.id_equipement"
            >
              <span class="item-name">{{ item.nom_equipement }}</span>
              <button
                type="button"
                class="btn-text-danger"
                :disabled="busy"
                @click="removeMyEquipment(item.id_equipement)"
              >
                Supprimer
              </button>
            </div>
            <p v-if="myEquipment.length === 0" class="empty-state">
              Tu n'as pas encore ajouté d'équipement personnel.
            </p>
          </div>
          <button
            type="button"
            class="btn-secondary add-personal-button"
            :disabled="busy"
            @click="openModal('personnel')"
          >
            + Ajouter un équipement
          </button>
        </section>
      </template>

      <section v-else-if="store.charge" class="equipment-section">
        <h1>Groupe introuvable</h1>
        <p class="empty-state">
          Ce groupe n'existe pas ou tu n'en fais pas partie.
          <RouterLink to="/home">Retour à l'accueil</RouterLink>
        </p>
      </section>
    </main>

    <div v-if="modalType" class="modal-overlay" @click.self="closeModal">
      <section
        class="modal-content"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="'equipment-modal-title'"
      >
        <div class="modal-header">
          <h2 id="equipment-modal-title">
            Ajouter un équipement {{ modalType === 'groupe' ? 'du groupe' : 'personnel' }}
          </h2>
        </div>
        <div class="modal-body">
          <p class="modal-subtitle">
            {{
              modalType === 'groupe'
                ? 'Il sera enregistré au nom du groupe.'
                : 'Il sera visible par tous les membres du groupe.'
            }}
          </p>

          <form @submit.prevent="addEquipment">
            <div class="form-group">
              <label for="equipment-name">Nom de l'équipement</label>
              <input
                id="equipment-name"
                v-model="newEquipmentName"
                type="text"
                maxlength="255"
                placeholder="Ex. Table de mixage 12 pistes"
                class="form-input"
                required
                autofocus
              />
            </div>

            <p v-if="modalError" class="error-message" role="alert">{{ modalError }}</p>
            <div class="modal-actions">
              <button type="button" class="btn-secondary" :disabled="busy" @click="closeModal">
                Annuler
              </button>
              <button
                type="submit"
                class="btn-primary"
                :disabled="busy || !newEquipmentName.trim()"
              >
                {{ busy ? 'Ajout…' : 'Ajouter' }}
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import NavigationGroupe from '@/components/NavigationGroupe.vue'
import { equipementsApi } from '@/services/equipements'
import { useAuthStore } from '@/stores/auth'
import { useGroupesStore } from '@/stores/groupes'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useGroupesStore()
const groupEquipment = ref([])
const myEquipment = ref([])
const loading = ref(true)
const busy = ref(false)
const errorMessage = ref('')
const modalError = ref('')
const modalType = ref(null)
const newEquipmentName = ref('')
let loadSequence = 0

const group = computed(() =>
  store.groupes.find((item) => item.id_grp === Number(route.params.id)),
)

function naviguerVersOnglet(onglet) {
  router.push({
    name: 'group',
    params: { id: route.params.id },
    query: { tab: onglet },
  })
}

async function loadEquipment() {
  const sequence = ++loadSequence
  if (!store.charge) {
    loading.value = !store.erreur
    errorMessage.value = store.erreur
    return
  }
  if (!group.value) {
    loading.value = false
    groupEquipment.value = []
    myEquipment.value = []
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const [groupItems, personalItems] = await Promise.all([
      equipementsApi.duGroupe(auth.token, route.params.id),
      equipementsApi.personnels(auth.token),
    ])
    if (sequence !== loadSequence) return
    groupEquipment.value = groupItems
    myEquipment.value = personalItems
  } catch (error) {
    if (sequence !== loadSequence) return
    groupEquipment.value = []
    myEquipment.value = []
    errorMessage.value = error.message
  } finally {
    if (sequence === loadSequence) loading.value = false
  }
}

watch(
  [() => route.params.id, () => store.charge, () => store.erreur],
  loadEquipment,
  { immediate: true },
)

function openModal(type) {
  modalType.value = type
  newEquipmentName.value = ''
  modalError.value = ''
}

function closeModal() {
  if (busy.value) return
  modalType.value = null
  newEquipmentName.value = ''
  modalError.value = ''
}

async function addEquipment() {
  const name = newEquipmentName.value.trim()
  if (!name || !modalType.value) return

  busy.value = true
  modalError.value = ''
  try {
    if (modalType.value === 'groupe') {
      await equipementsApi.ajouterAuGroupe(auth.token, route.params.id, name)
    } else {
      await equipementsApi.ajouterPersonnel(auth.token, name)
    }
    modalType.value = null
    await loadEquipment()
  } catch (error) {
    modalError.value = error.message
  } finally {
    busy.value = false
  }
}

async function removeGroupEquipment(idEquipement) {
  busy.value = true
  errorMessage.value = ''
  try {
    await equipementsApi.retirerDuGroupe(auth.token, route.params.id, idEquipement)
    await loadEquipment()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    busy.value = false
  }
}

async function removeMyEquipment(idEquipement) {
  busy.value = true
  errorMessage.value = ''
  try {
    await equipementsApi.retirerPersonnel(auth.token, idEquipement)
    await loadEquipment()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.main-content {
  flex: 1;
  min-width: 0;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  padding: 16px 40px 48px;
  color: #1c1e21;
}

.content-header,
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

h1,
h2 {
  margin: 0 0 8px;
  color: #000;
  font-weight: 700;
  letter-spacing: -0.5px;
}

h1 {
  font-size: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.subtitle {
  margin: 0;
  color: #65676b;
  font-size: 1rem;
}

.equipment-section,
.my-equipment-section {
  padding: 24px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.my-equipment-section {
  margin-top: 32px;
}

.table-header,
.equipment-item {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr) 100px;
  align-items: center;
}

.table-header {
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
  color: #65676b;
  font-size: 0.9rem;
  font-weight: 600;
}

.equipment-list {
  display: flex;
  flex-direction: column;
}

.equipment-item {
  min-height: 58px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.equipment-item:last-child {
  border-bottom: 0;
}

.col-name,
.item-name {
  min-width: 0;
}

.col-owner,
.item-owner {
  min-width: 0;
}

.col-actions {
  width: 100px;
  text-align: right;
}

.item-name {
  color: #1c1e21;
  font-weight: 600;
  overflow-wrap: anywhere;
}

.item-owner {
  color: #65676b;
  font-size: 0.95rem;
}

.empty-state {
  padding: 28px 12px;
  color: #65676b;
  text-align: center;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 30px;
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.btn-primary {
  border: 0;
  background: #1c1e21;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #000;
}

.btn-secondary {
  border: 1px solid #ccd0d5;
  background: transparent;
  color: #1c1e21;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #1c1e21;
  background: #fff;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-text-danger:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-text-danger {
  padding: 8px 16px;
  border: 0;
  border-radius: 20px;
  background: transparent;
  color: #e63946;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
}

.btn-text-danger:hover:not(:disabled) {
  background: #fdf0ef;
}

.add-personal-button {
  margin-top: 16px;
}

.error-message {
  margin: 0 0 16px;
  color: #b42318;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.4);
}

.modal-content {
  width: min(100%, 450px);
  padding: 32px;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.modal-header h2 {
  margin-bottom: 8px;
  font-size: 1.5rem;
}

.modal-subtitle {
  margin: 0 0 24px;
  color: #65676b;
  font-size: 0.95rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.form-group label {
  color: #1c1e21;
  font-size: 0.9rem;
  font-weight: 600;
}

.form-input {
  padding: 14px 16px;
  border: 1px solid #ccd0d5;
  border-radius: 12px;
  background: #f8f9fa;
  font: inherit;
}

.form-input:focus {
  border-color: #1c1e21;
  outline: none;
  background: #fff;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .main-content {
    padding: 12px 20px 32px;
  }

  .content-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .table-header .col-owner,
  .item-owner {
    display: none;
  }

  .table-header,
  .equipment-item {
    grid-template-columns: minmax(0, 1fr) 100px;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
