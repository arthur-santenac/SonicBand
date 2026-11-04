<template>
  <div class="app-wrapper">
    <!-- En-tête : logo, onglets du groupe, notifications et profil -->
    <header class="top-header">
      <RouterLink to="/home" class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo-icon" />
        <span class="logo-text">sonicBand</span>
      </RouterLink>

      <nav class="group-tabs" aria-label="Sections du groupe">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="tab"
          :class="{ active: tab.id === activeTab }"
          :disabled="!ONGLETS_DISPONIBLES.includes(tab.id)"
          :title="!ONGLETS_DISPONIBLES.includes(tab.id) ? 'Bientôt disponible' : undefined"
          @click="activeTab = tab.id"
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

      <div class="header-actions">
        <button type="button" class="icon-btn" aria-label="Notifications">
          <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
          </svg>
        </button>
        <div class="profile">
          <button
            type="button"
            class="avatar"
            :aria-expanded="isProfileOpen"
            aria-label="Mon profil"
            @click="isProfileOpen = !isProfileOpen"
          >
            {{ userInitial }}
          </button>
          <div class="profile-menu" v-if="isProfileOpen">
            <p class="profile-name">{{ userName }}</p>
            <button type="button" class="profile-item" @click="handleLogout">Se déconnecter</button>
          </div>
        </div>
      </div>
    </header>

    <div class="main-layout">
      <!-- Barre de navigation flottante (même style que l'accueil) -->
      <nav class="floating-sidebar" aria-label="Mes groupes">
        <RouterLink to="/home" class="nav-home" aria-label="Accueil">
          <svg
            viewBox="0 0 24 24"
            width="24"
            height="24"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
        </RouterLink>
        <div class="sidebar-separator"></div>
        <RouterLink
          v-for="g in store.groupes"
          :key="g.id_grp"
          :to="{ name: 'group', params: { id: g.id_grp } }"
          class="sidebar-bubble"
          :class="[couleur(g.id_grp), { active: group && g.id_grp === group.id }]"
          :title="g.nom_grp"
        >
          {{ initiale(g.nom_grp) }}
        </RouterLink>
        <RouterLink
          :to="{ name: 'create-group' }"
          class="sidebar-bubble create-dashed"
          title="Créer un groupe"
        >
          +
        </RouterLink>
      </nav>

      <!-- Contenu principal -->
      <main class="main-content" v-if="group">
        <header class="group-header">
          <div class="group-bubble" :class="group.colorClass">{{ group.initial }}</div>
          <h1>{{ group.name }}</h1>
        </header>

        <!-- Onglet Membres : inviter et retirer des musiciens -->
        <section v-if="activeTab === 'membres'" class="members-section">
          <h2 class="section-title">Membres</h2>
          <MembresGroupe :id-grp="group.id" :mon-role="group.role" />
        </section>

        <section v-else>
          <h2 class="section-title">Prochains événements</h2>

          <p v-if="group.events.length === 0" class="empty-state">
            Aucun événement prévu pour le moment.
          </p>

          <ul v-else class="events-list">
            <li class="event-card" v-for="event in group.events" :key="event.id">
              <div class="event-date">
                <strong>{{ event.day }}</strong>
                <span>{{ event.time }}</span>
              </div>

              <div class="event-info">
                <span class="event-type" :class="typeClass(event.type)">{{ event.type }}</span>
                <span class="event-place">{{ event.place }}</span>
              </div>

              <div class="event-links" v-if="event.type === 'Concert'">
                <button type="button" class="btn-outline">Voir la setlist</button>
                <button type="button" class="btn-outline">Listes de matériel</button>
              </div>

              <div class="event-stats">
                <span class="stat">
                  <span class="dot dot-present"></span>
                  <strong>{{ event.present }}/{{ group.membersCount }}</strong> Présents
                </span>
                <span class="stat">
                  <span class="dot dot-absent"></span>
                  <strong>{{ event.absent }}/{{ group.membersCount }}</strong> Absents
                </span>
                <span class="stat">
                  <span class="dot dot-none"></span>
                  <strong>{{ sansReponse(event) }}/{{ group.membersCount }}</strong> Sans rép.
                </span>
              </div>

              <div class="event-actions">
                <button
                  type="button"
                  class="btn-answer"
                  :class="{ selected: event.myAnswer === 'present' }"
                  :aria-pressed="event.myAnswer === 'present'"
                  @click="repondre(event, 'present')"
                >
                  Je viens
                </button>
                <button
                  type="button"
                  class="btn-answer"
                  :class="{ selected: event.myAnswer === 'absent' }"
                  :aria-pressed="event.myAnswer === 'absent'"
                  @click="repondre(event, 'absent')"
                >
                  Je ne peux pas
                </button>
              </div>
            </li>
          </ul>
        </section>
      </main>

      <main class="main-content" v-else-if="!store.charge">
        <p class="empty-state">{{ store.erreur || 'Chargement…' }}</p>
      </main>

      <!-- Groupe introuvable -->
      <main class="main-content" v-else>
        <h1 class="not-found-title">Groupe introuvable</h1>
        <p class="empty-state">
          Ce groupe n'existe pas ou tu n'en fais pas partie.
          <RouterLink to="/home">Retour à l'accueil</RouterLink>
        </p>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import MembresGroupe from '@/components/MembresGroupe.vue'
import { useAuthStore } from '@/stores/auth'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'
import { evenementsDemo } from '@/data/groupes'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useGroupesStore()

const isProfileOpen = ref(false)

// Groupe affiché, d'après l'id dans l'URL (/groups/:id), parmi mes groupes (API).
// Les événements sont encore des données de démonstration (data/groupes.js).
const group = computed(() => {
  const g = store.groupes.find((x) => x.id_grp === Number(route.params.id))
  if (!g) return null
  return {
    id: g.id_grp,
    name: g.nom_grp,
    initial: initiale(g.nom_grp),
    colorClass: couleur(g.id_grp),
    membersCount: g.nb_membres,
    role: g.mon_role,
    events: evenementsDemo(g.nom_grp),
  }
})

// Onglets utilisables pour l'instant : Aperçu et Membres
const ONGLETS_DISPONIBLES = ['apercu', 'membres']
const activeTab = ref('apercu')
watch(
  () => route.params.id,
  () => (activeTab.value = 'apercu'),
)

onMounted(() => store.charger())

const userName = computed(() => auth.user?.nom_user ?? '')
const userInitial = computed(() => (userName.value.charAt(0) || '?').toUpperCase())

// Onglets du groupe : seul l'aperçu existe pour l'instant
const tabs = [
  {
    id: 'apercu',
    label: 'Aperçu',
    icon: ['M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z', 'M9 22V12h6v10'],
  },
  {
    id: 'dispos',
    label: 'Disponibilités',
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
    icon: [
      'M9 18V5l12-2v13',
      'M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
      'M18 19a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    ],
  },
  {
    id: 'equipement',
    label: 'Équipement',
    icon: [
      'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
    ],
  },
  {
    id: 'membres',
    label: 'Membres',
    icon: [
      'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2',
      'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
      'M22 21v-2a4 4 0 0 0-3-3.87',
      'M16 3.13a4 4 0 0 1 0 7.75',
    ],
  },
]

function typeClass(type) {
  return type === 'Concert' ? 'type-concert' : 'type-repetition'
}

function sansReponse(event) {
  return Math.max(0, group.value.membersCount - event.present - event.absent)
}

// Enregistre (localement) la réponse de l'utilisateur ; un 2e clic annule la réponse.
function repondre(event, reponse) {
  if (event.myAnswer === 'present') event.present--
  if (event.myAnswer === 'absent') event.absent--

  event.myAnswer = event.myAnswer === reponse ? null : reponse

  if (event.myAnswer === 'present') event.present++
  if (event.myAnswer === 'absent') event.absent++
}

const handleLogout = () => {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  background-color: #f4f5f7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  color: #1c1e21;
}

button {
  font-family: inherit;
}

/* --- En-tête --- */
.top-header {
  padding: 24px 40px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 24px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-icon {
  height: 28px;
}

.logo-text {
  font-weight: 700;
  font-size: 1.5rem;
  letter-spacing: -0.5px;
  color: #000000;
}

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
}

.tab:not(:disabled) {
  cursor: pointer;
}

.tab:disabled {
  cursor: default;
}

.members-section {
  max-width: 720px;
}

.tab.active {
  background: white;
  color: #1c1e21;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.header-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.icon-btn,
.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.icon-btn {
  background-color: #e4e6eb;
  color: #1c1e21;
}

.icon-btn:hover {
  background-color: #d8dadf;
}

.avatar {
  background-color: #aecbfa;
  color: #000;
  font-size: 1rem;
  font-weight: 700;
}

.profile {
  position: relative;
}

.profile-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  background: white;
  border-radius: 16px;
  padding: 8px;
  min-width: 180px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  z-index: 10;
}

.profile-name {
  margin: 0;
  padding: 8px 12px;
  font-weight: 700;
  color: #000;
}

.profile-item {
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.95rem;
  color: #1c1e21;
  cursor: pointer;
}

.profile-item:hover {
  background-color: #f4f5f7;
}

/* --- Layout principal --- */
.main-layout {
  display: flex;
  flex: 1;
  padding: 0 40px 40px 40px;
  gap: 40px;
}

/* --- Barre de navigation flottante --- */
.floating-sidebar {
  background: white;
  border-radius: 40px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  height: max-content;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

.nav-home {
  background-color: #111;
  color: white;
  width: 56px;
  height: 56px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-separator {
  width: 32px;
  height: 3px;
  border-radius: 2px;
  background-color: #e4e6eb;
  margin: -4px 0;
}

.sidebar-bubble {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #000;
  cursor: pointer;
  text-decoration: none;
  transition:
    opacity 0.2s,
    border-radius 0.2s;
}

.sidebar-bubble:hover {
  opacity: 0.8;
}

/* Groupe affiché : bulle carrée arrondie entourée de noir */
.sidebar-bubble.active {
  border-radius: 18px;
  box-shadow:
    0 0 0 2px white,
    0 0 0 4px #111;
}

.create-dashed {
  background: transparent;
  border: 2px dashed #ccd0d5;
  color: #65676b;
}

/* --- Contenu principal --- */
.main-content {
  flex: 1;
  min-width: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
}

.group-header h1 {
  font-size: 2.5rem;
  margin: 0;
  font-weight: 700;
  color: #000000;
  letter-spacing: -0.5px;
}

.group-bubble {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  font-weight: 700;
  color: #000;
  flex-shrink: 0;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #000;
  margin: 0 0 16px 0;
}

.empty-state {
  color: #65676b;
  font-size: 0.95rem;
}

.empty-state a {
  color: #1c1e21;
  font-weight: 600;
}

.not-found-title {
  font-size: 2rem;
  margin: 0 0 8px 0;
  color: #000;
}

/* --- Liste des événements --- */
.events-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-card {
  background: white;
  border-radius: 20px;
  padding: 14px 16px 14px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.event-date {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 110px;
  flex-shrink: 0;
}

.event-date strong {
  font-size: 1rem;
  font-weight: 700;
  color: #000;
}

.event-date span {
  font-size: 0.85rem;
  color: #65676b;
}

.event-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  margin-right: auto;
}

.event-type {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}

.type-repetition {
  background-color: #d6e4fd;
  color: #1c3d7a;
}

.type-concert {
  background-color: #ead9f9;
  color: #4b2a6b;
}

.event-place {
  font-size: 0.95rem;
  font-weight: 500;
  color: #1c1e21;
}

.event-links {
  display: flex;
  gap: 8px;
}

.btn-outline {
  background: white;
  border: 1px solid #1c1e21;
  color: #1c1e21;
  border-radius: 30px;
  padding: 7px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-outline:hover {
  background-color: #f4f5f7;
}

.event-stats {
  display: flex;
  align-items: center;
  gap: 14px;
  background-color: #f4f5f7;
  border-radius: 14px;
  padding: 8px 14px;
  font-size: 0.85rem;
  color: #65676b;
  white-space: nowrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat strong {
  color: #000;
  font-weight: 700;
  font-size: 0.95rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-present {
  background-color: #2f6fe0;
}

.dot-absent {
  background-color: #c0322b;
}

.dot-none {
  background-color: #8a8d93;
}

.event-actions {
  display: flex;
  gap: 8px;
}

.btn-answer {
  background: white;
  border: 1px solid #ccd0d5;
  color: #1c1e21;
  border-radius: 30px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition:
    background-color 0.2s,
    border-color 0.2s;
}

.btn-answer:hover {
  border-color: #1c1e21;
}

.btn-answer.selected {
  background-color: #111;
  border-color: #111;
  color: white;
}

/* --- Responsivité --- */
@media (max-width: 1200px) {
  .event-card {
    flex-wrap: wrap;
  }
  .event-links,
  .event-stats {
    order: 1;
  }
  .event-actions {
    order: 2;
    margin-left: auto;
  }
}

@media (max-width: 1024px) {
  .top-header {
    grid-template-columns: 1fr auto;
  }
  .group-tabs {
    grid-column: 1 / -1;
    grid-row: 2;
    overflow-x: auto;
    justify-self: start;
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .top-header {
    padding: 20px;
    gap: 16px;
  }
  .main-layout {
    flex-direction: column;
    padding: 0 20px 20px 20px;
    gap: 24px;
  }
  .floating-sidebar {
    flex-direction: row;
    border-radius: 20px;
    overflow-x: auto;
    padding: 12px 20px;
    justify-content: flex-start;
  }
  .sidebar-separator {
    width: 3px;
    height: 32px;
    margin: 0 -4px;
  }
  .group-header h1 {
    font-size: 2rem;
  }
  .event-card {
    padding: 16px;
  }
  .event-stats {
    flex-wrap: wrap;
    white-space: normal;
  }
  .event-actions {
    width: 100%;
    margin-left: 0;
  }
  .btn-answer {
    flex: 1;
  }
}

/* Couleurs partagées */
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
</style>
