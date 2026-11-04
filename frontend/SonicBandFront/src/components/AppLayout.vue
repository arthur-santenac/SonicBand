<template>
  <div class="app-wrapper">
    <!-- En-tête global -->
    <header class="top-header">
      <RouterLink to="/home" class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo-icon" />
        <span class="logo-text">sonicBand</span>
      </RouterLink>

      <!-- Emplacement central optionnel (ex: onglets dans GroupView) -->
      <div class="header-center">
        <slot name="header-center"></slot>
      </div>

      <!-- Actions récurrentes : Boîte de réception + Profil -->
      <div class="header-actions">
        <button
          type="button"
          class="icon-btn"
          aria-label="Boîte de réception"
          title="Boîte de réception"
          @click="isInboxOpen = true"
        >
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
          <span class="badge" v-if="invitations.length > 0">{{ invitations.length }}</span>
        </button>

        <div class="profile">
          <button
            type="button"
            class="avatar"
            :aria-expanded="isProfileOpen"
            aria-label="Mon profil"
            :title="userName"
            @click="isProfileOpen = !isProfileOpen"
          >
            {{ userInitial }}
          </button>
          <div class="profile-menu" v-if="isProfileOpen">
            <p class="profile-name">{{ userName }}</p>
            <button type="button" class="profile-item" @click="handleLogout">
              Se déconnecter
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="main-layout">
      <!-- Barre de navigation flottante unique -->
      <nav class="floating-sidebar" aria-label="Mes groupes">
        <RouterLink
          to="/home"
          class="nav-home"
          :class="{ active: route.path === '/home' }"
          aria-label="Accueil"
          title="Accueil"
        >
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
          :class="[couleur(g.id_grp), { active: activeGroupId === g.id_grp }]"
          :title="g.nom_grp"
        >
          {{ initiale(g.nom_grp) }}
        </RouterLink>

        <RouterLink
          :to="{ name: 'create-group' }"
          class="sidebar-bubble create-dashed"
          :class="{ active: route.name === 'create-group' }"
          title="Créer un groupe"
        >
          +
        </RouterLink>
      </nav>

      <!-- Contenu spécifique à chaque page -->
      <slot></slot>
    </div>

    <!-- Modale Boîte de réception globale -->
    <div class="modal-overlay" v-if="isInboxOpen" @click.self="isInboxOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Invitations à rejoindre un groupe</h2>
          <button class="close-btn" @click="isInboxOpen = false">×</button>
        </div>
        <div class="modal-body">
          <p v-if="inboxError" class="load-error" role="alert">{{ inboxError }}</p>
          <p v-if="invitations.length === 0" class="empty-inbox">Aucune nouvelle invitation.</p>
          <div class="invitation-card" v-for="invit in invitations" :key="invit.id_invit">
            <div class="invit-info">
              <div class="card-bubble" :class="couleur(invit.id_grp)">
                {{ initiale(invit.nom_grp) }}
              </div>
              <div>
                <h3>{{ invit.nom_grp }}</h3>
                <p>Invité par {{ invit.invite_par || 'un ancien membre' }}</p>
              </div>
            </div>
            <div class="invit-actions">
              <button
                class="btn-accept"
                :disabled="busyId === invit.id_invit"
                @click="accepter(invit)"
              >
                Accepter
              </button>
              <button
                class="btn-decline"
                :disabled="busyId === invit.id_invit"
                @click="refuser(invit)"
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useGroupesStore()

const isProfileOpen = ref(false)
const isInboxOpen = ref(false)
const busyId = ref(null)
const inboxError = ref('')

const userName = computed(() => auth.user?.nom_user ?? '')
const userInitial = computed(() => initiale(userName.value))
const invitations = computed(() => store.invitations)

const activeGroupId = computed(() => {
  if (route.name === 'group' || route.name === 'group-musicians') {
    return Number(route.params.id)
  }
  return null
})

const handleLogout = () => {
  auth.logout()
  router.push('/')
}

async function accepter(invit) {
  inboxError.value = ''
  busyId.value = invit.id_invit
  try {
    const groupe = await store.accepter(invit)
    isInboxOpen.value = false
    router.push({ name: 'group', params: { id: groupe.id_grp } })
  } catch (err) {
    inboxError.value = err.message
  } finally {
    busyId.value = null
  }
}

async function refuser(invit) {
  inboxError.value = ''
  busyId.value = invit.id_invit
  try {
    await store.refuser(invit)
  } catch (err) {
    inboxError.value = err.message
  } finally {
    busyId.value = null
  }
}

// Permet d'ouvrir la modale depuis un composant parent si besoin
defineExpose({
  openInbox: () => {
    isInboxOpen.value = true
  },
})

onMounted(() => {
  if (!store.charge) store.charger()
})
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

/* --- En-tête global --- */
.top-header {
  padding: 24px 40px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  grid-template-rows: minmax(50px, auto); /* Force la même hauteur avec ou sans les onglets */
  align-items: center;
  gap: 24px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  justify-self: start;
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

.header-center {
  display: flex;
  justify-content: center;
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
  position: relative;
}

.icon-btn {
  background-color: #e4e6eb;
  color: #1c1e21;
  transition: background-color 0.2s;
}

.icon-btn:hover {
  background-color: #d8dadf;
}

.badge {
  background-color: #e63946;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  position: absolute;
  top: -4px;
  right: -4px;
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
  z-index: 100;
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

/* --- Layout principal & Sidebar --- */
.main-layout {
  display: flex;
  flex: 1;
  padding: 0 40px 40px 40px;
  gap: 40px;
}

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
  transition: box-shadow 0.2s;
}

.nav-home.active {
  box-shadow:
    0 0 0 2px white,
    0 0 0 4px #111;
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

/* --- Modale Boîte de réception --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 20px;
  width: 90%;
  max-width: 550px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #000;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #65676b;
  line-height: 1;
}

.empty-inbox {
  text-align: center;
  color: #65676b;
  padding: 20px 0;
  font-size: 0.95rem;
}

.invitation-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
}

.invitation-card:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.invit-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.invit-info h3 {
  margin: 0 0 4px 0;
  font-weight: 700;
  font-size: 1.1rem;
  color: #000;
}

.invit-info p {
  margin: 0;
  color: #65676b;
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

.invit-actions {
  display: flex;
  gap: 10px;
}

.btn-accept,
.btn-decline {
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 30px;
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-accept {
  background-color: #1c1e21;
  color: white;
  border: none;
}

.btn-accept:hover {
  background-color: #000000;
}

.btn-decline {
  background-color: transparent;
  color: #1c1e21;
  border: 1px solid #ccd0d5;
}

.btn-decline:hover {
  background-color: #f4f5f7;
  border-color: #1c1e21;
}

.btn-accept:disabled,
.btn-decline:disabled {
  opacity: 0.6;
  cursor: default;
}

.load-error {
  background: #fdf0ef;
  color: #c0322b;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 0 16px 0;
  font-size: 0.9rem;
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

/* --- Responsivité --- */
@media (max-width: 1024px) {
  .top-header {
    grid-template-columns: 1fr auto;
  }
  .header-center {
    grid-column: 1 / -1;
    grid-row: 2;
    justify-content: flex-start;
    overflow-x: auto;
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
  .invitation-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .invit-actions {
    width: 100%;
    justify-content: flex-start;
  }
  .modal-content {
    padding: 24px;
  }
}
</style>