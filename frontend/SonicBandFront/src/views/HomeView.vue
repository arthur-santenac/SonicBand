<template>
  <AppLayout>
    <main class="main-content">
      <header class="content-header">
        <div>
          <h1>Salut {{ userName }}</h1>
          <p class="subtitle">Retrouve tous tes groupes ici.</p>
        </div>
      </header>

      <p v-if="store.erreur" class="load-error" role="alert">{{ store.erreur }}</p>

      <!-- Grille des groupes -->
      <section class="groups-section">
        <div class="groups-grid">
          <RouterLink
            class="group-card"
            v-for="group in groups"
            :key="group.id"
            :to="{ name: 'group', params: { id: group.id } }"
          >
            <div class="group-card-header">
              <div class="card-bubble" :class="group.colorClass">{{ group.initial }}</div>
            </div>
            <div class="group-details">
              <h3>{{ group.name }}</h3>
              <p>{{ group.membersCount }} musiciens · {{ prochainEvenement(group) }}</p>
            </div>
          </RouterLink>

          <RouterLink :to="{ name: 'create-group' }" class="group-card create-card">
            <div class="create-icon">+</div>
            <h3>Créer un groupe</h3>
            <p class="create-hint">Tu en seras l'administrateur.</p>
          </RouterLink>
        </div>
      </section>
    </main>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'
import { evenementsDemo, prochainEvenement } from '@/data/groupes'

const auth = useAuthStore()
const store = useGroupesStore()

const userName = computed(() => auth.user?.nom_user ?? '')

const groups = computed(() =>
  store.groupes.map((g) => ({
    id: g.id_grp,
    name: g.nom_grp,
    initial: initiale(g.nom_grp),
    colorClass: couleur(g.id_grp),
    membersCount: g.nb_membres,
    events: evenementsDemo(g.nom_grp),
  })),
)
</script>

<style scoped>
.main-content {
  flex: 1;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.content-header h1 {
  font-size: 2.5rem;
  margin: 0 0 8px 0;
  font-weight: 700;
  color: #000000;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 1rem;
  color: #65676b;
  margin: 0;
  font-weight: 400;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.group-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-decoration: none;
  color: inherit;
}

.group-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.create-card {
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 2px dashed #ccd0d5;
  background: transparent;
  box-shadow: none;
  min-height: 160px;
}

.create-card:hover {
  border-color: #1c1e21;
  background-color: rgba(0, 0, 0, 0.01);
}

.create-icon {
  font-size: 2rem;
  color: #65676b;
  margin-bottom: 8px;
  font-weight: 300;
}

.create-card h3 {
  color: #1c1e21;
  font-weight: 600;
  margin: 0;
}

.create-hint {
  margin: 0;
  font-size: 0.85rem;
  color: #65676b;
}

.load-error {
  background: #fdf0ef;
  color: #c0322b;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 0 16px 0;
  font-size: 0.9rem;
}

.card-bubble {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #000;
}

.group-details h3 {
  margin: 0 0 6px 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #000000;
  letter-spacing: -0.3px;
}

.group-details p {
  margin: 0;
  font-size: 0.9rem;
  color: #65676b;
  font-weight: 400;
}

.bg-blue {
  background-color: #aecbfa;
}
.bg-purple {
  background-color: #d7b4f3;
}
.bg-green {
  background-color: #ceead6;
}
.bg-red {
  background-color: #fad2cf;
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    gap: 16px;
    margin-bottom: 24px;
  }
  .content-header h1 {
    font-size: 2rem;
  }
}
</style>