<template>
  <AppLayout>
    <template #header-center>
      <NavigationGroupe
        :id-grp="route.params.id"
        active-tab="dispos"
        @select="naviguerVersOnglet"
      />
    </template>

    <main class="main-content">
      <template v-if="groupe">
        <header class="content-header">
          <div>
            <h1>{{ vue === 'groupe' ? 'Disponibilités du groupe' : 'Disponibilités' }}</h1>
            <p class="subtitle">
              <template v-if="vue === 'groupe'">
                Plus le bleu est foncé, plus il y a de musiciens libres. Passe la souris sur une
                plage pour voir qui est libre.
              </template>
              <template v-else>
                Ajoute tes plages horaires libres pour chaque jour. Elles sont les mêmes dans tous
                tes groupes.
              </template>
            </p>
          </div>
          <div class="toggle" role="tablist" aria-label="Affichage">
            <button
              type="button"
              role="tab"
              :aria-selected="vue === 'moi'"
              :class="{ active: vue === 'moi' }"
              @click="choisirVue('moi')"
            >
              Mes dispos
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="vue === 'groupe'"
              :class="{ active: vue === 'groupe' }"
              @click="choisirVue('groupe')"
            >
              Le groupe
            </button>
          </div>
        </header>

        <MesDisponibilites v-if="vue === 'moi'" v-model:lundi="lundi" />
        <DisponibilitesGroupe v-else v-model:lundi="lundi" :id-grp="groupe.id_grp" />
      </template>

      <p v-else-if="!store.charge" class="empty-state">{{ store.erreur || 'Chargement…' }}</p>

      <template v-else>
        <h1>Groupe introuvable</h1>
        <p class="empty-state">
          Ce groupe n'existe pas ou tu n'en fais pas partie.
          <RouterLink to="/home">Retour à l'accueil</RouterLink>
        </p>
      </template>
    </main>
  </AppLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import NavigationGroupe from '@/components/NavigationGroupe.vue'
import MesDisponibilites from '@/components/MesDisponibilites.vue'
import DisponibilitesGroupe from '@/components/DisponibilitesGroupe.vue'
import { useGroupesStore } from '@/stores/groupes'
import { lundiDe } from '@/utils/semaine'

const route = useRoute()
const router = useRouter()
const store = useGroupesStore()

// Semaine affichée, partagée entre « Mes dispos » et « Le groupe ».
const lundi = ref(lundiDe())

const groupe = computed(() => store.groupes.find((g) => g.id_grp === Number(route.params.id)))
const vue = computed(() => (route.query.vue === 'groupe' ? 'groupe' : 'moi'))

function choisirVue(v) {
  router.replace({ query: { ...route.query, vue: v === 'groupe' ? 'groupe' : undefined } })
}

function naviguerVersOnglet(onglet) {
  router.push({ name: 'group', params: { id: route.params.id }, query: { tab: onglet } })
}
</script>

<style scoped>
button {
  font-family: inherit;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

h1 {
  font-size: 2rem;
  margin: 0;
  font-weight: 700;
  color: #000;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 4px 0 0;
  color: #65676b;
  font-size: 0.95rem;
  max-width: 640px;
}

.toggle {
  display: flex;
  gap: 4px;
  background: #e4e6eb;
  border-radius: 30px;
  padding: 5px;
}

.toggle button {
  border: none;
  background: transparent;
  border-radius: 30px;
  padding: 9px 16px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #65676b;
  cursor: pointer;
}

.toggle button.active {
  background: white;
  color: #1c1e21;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.empty-state {
  color: #65676b;
}
</style>
