<template>
  <div class="app-wrapper">
    <!-- En-tête global avec le logo -->
    <header class="top-header">
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo-icon" />
        <span class="logo-text">sonicBand</span>
      </div>
    </header>

    <div class="main-layout">
      <!-- Barre de navigation flottante -->
      <nav class="floating-sidebar">
        <div class="nav-item active">
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="home-icon">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
        </div>
        <div class="sidebar-bubble bg-blue">N</div>
        <div class="sidebar-bubble bg-purple">U</div>
        <div class="sidebar-bubble create-dashed">+</div>
      </nav>

      <!-- Contenu principal -->
      <main class="main-content">
        <header class="content-header">
          <div>
            <h1>Salut {{ userName }}</h1>
            <p class="subtitle">Retrouve tous tes groupes ici.</p>
          </div>
          
          <button class="inbox-btn" @click="isInboxOpen = true">
            <span class="icon">🔔</span> Boîte de réception
            <span class="badge" v-if="invitations.length > 0">{{ invitations.length }}</span>
          </button>
        </header>

        <!-- Grille des groupes -->
        <section class="groups-section">
          <div class="groups-grid">
            
            <div class="group-card create-card">
              <div class="create-icon">+</div>
              <h3>Créer un groupe</h3>
            </div>

            <div class="group-card" v-for="group in groups" :key="group.id">
              <div class="group-card-header">
                <div class="card-bubble" :class="group.colorClass">{{ group.initial }}</div>
              </div>
              <div class="group-details">
                <h3>{{ group.name }}</h3>
                <p>{{ group.membersCount }} musiciens · {{ group.nextEvent }}</p>
              </div>
            </div>
            
          </div>
        </section>
      </main>
    </div>

    <!-- Modale Boîte de réception -->
    <div class="modal-overlay" v-if="isInboxOpen" @click.self="isInboxOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Invitations à rejoindre un groupe</h2>
          <button class="close-btn" @click="isInboxOpen = false">×</button>
        </div>
        <div class="modal-body">
          <p v-if="invitations.length === 0" class="empty-inbox">Aucune nouvelle invitation.</p>
          <div class="invitation-card" v-for="invit in invitations" :key="invit.id">
            <div class="invit-info">
              <div class="card-bubble" :class="invit.colorClass">{{ invit.initial }}</div>
              <div>
                <h3>{{ invit.groupName }}</h3>
                <p>Invité par {{ invit.invitedBy }}</p>
              </div>
            </div>
            <div class="invit-actions">
              <button class="btn-accept">Accepter</button>
              <button class="btn-decline">Supprimer</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const userName = ref('Paul')
const isInboxOpen = ref(false)

const invitations = ref([
  { id: 1, groupName: 'Oasis', initial: 'O', colorClass: 'bg-green', invitedBy: 'Arthur' }
])

const groups = ref([
  { id: 1, name: 'Nirvana', initial: 'N', colorClass: 'bg-blue', membersCount: 4, nextEvent: 'Répétition ven. 13 nov' },
  { id: 2, name: 'U2', initial: 'U', colorClass: 'bg-purple', membersCount: 2, nextEvent: 'Aucun événement' }
])
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  background-color: #F4F5F7; /* Gris très clair similaire au fond de connexion */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  color: #1C1E21; /* Couleur de texte principale foncée */
}

/* --- En-tête global (Logo) --- */
.top-header {
  padding: 24px 40px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  height: 28px;
}

.logo-text {
  font-weight: 700; /* Gras prononcé comme sur la page de connexion */
  font-size: 1.5rem;
  letter-spacing: -0.5px;
  color: #000000;
}

/* --- Layout Principal --- */
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
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.nav-item.active {
  background-color: #111;
  color: white;
  width: 56px;
  height: 56px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 0 2px white, 0 0 0 4px #E4E6EB;
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
  transition: opacity 0.2s;
}

.sidebar-bubble:hover {
  opacity: 0.8;
}

.create-dashed {
  background: transparent;
  border: 2px dashed #CCD0D5;
  color: #65676B;
}

/* --- Contenu Principal --- */
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
  font-weight: 700; /* Titre très gras calqué sur le "Connexion" de la maquette */
  color: #000000;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 1rem;
  color: #65676B; /* Gris standard pour les textes secondaires */
  margin: 0;
  font-weight: 400;
}

/* Style des boutons calqué sur "Se connecter" */
.inbox-btn, .btn-accept, .btn-decline {
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600; /* Texte de bouton semi-gras */
  border-radius: 30px; /* Bordures très arrondies (pill-shape) */
  padding: 12px 24px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.inbox-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border: 1px solid #E4E6EB;
  color: #1C1E21;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: relative;
  font-size: 0.95rem;
  padding: 10px 20px;
}

.inbox-btn:hover {
  background-color: #F4F5F7;
}

.badge {
  background-color: #E63946;
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
  top: -6px;
  right: -6px;
}

/* --- Grille et Cartes --- */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.group-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.group-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.create-card {
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 2px dashed #CCD0D5;
  background: transparent;
  box-shadow: none;
  min-height: 160px;
}

.create-card:hover {
  border-color: #1C1E21;
  background-color: rgba(0,0,0,0.01);
}

.create-icon {
  font-size: 2rem;
  color: #65676B;
  margin-bottom: 8px;
  font-weight: 300;
}

.create-card h3 {
  color: #1C1E21;
  font-weight: 600;
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
  font-weight: 700; /* Nom du groupe bien gras */
  color: #000000;
  letter-spacing: -0.3px;
}

.group-details p {
  margin: 0;
  font-size: 0.9rem;
  color: #65676B;
  font-weight: 400;
}

/* Couleurs partagées */
.bg-blue { background-color: #AECBFA; }
.bg-purple { background-color: #D7B4F3; }
.bg-green { background-color: #CEEAD6; }
.bg-red { background-color: #FAD2CF; }

/* --- Pop-up Modale --- */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white; border-radius: 20px;
  width: 90%; max-width: 550px; padding: 32px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
}

.modal-header h2 { 
  margin: 0; 
  font-size: 1.4rem; 
  font-weight: 700;
  color: #000;
}

.close-btn { 
  background: none; border: none; font-size: 2rem; 
  cursor: pointer; color: #65676B; line-height: 1;
}

.empty-inbox { text-align: center; color: #65676B; padding: 20px 0; font-size: 0.95rem; }

.invitation-card {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 0; border-bottom: 1px solid #F0F2F5;
}

.invitation-card:last-child { border-bottom: none; padding-bottom: 0; }
.invit-info { display: flex; align-items: center; gap: 16px; }
.invit-info h3 { margin: 0 0 4px 0; font-weight: 700; font-size: 1.1rem; color: #000; }
.invit-info p { margin: 0; color: #65676B; font-size: 0.9rem; }

.invit-actions { display: flex; gap: 10px; }

/* Style du bouton Accepter (primaire, fond noir) */
.btn-accept { 
  background-color: #1C1E21; 
  color: white; 
  border: none;
  font-size: 0.95rem;
  padding: 10px 20px;
}
.btn-accept:hover { background-color: #000000; }

/* Style du bouton Supprimer (secondaire, bordure grise) */
.btn-decline { 
  background-color: transparent; 
  color: #1C1E21; 
  border: 1px solid #CCD0D5; 
  font-size: 0.95rem;
  padding: 10px 20px;
}
.btn-decline:hover { background-color: #F4F5F7; border-color: #1C1E21; }

/* --- Responsivité --- */
@media (max-width: 768px) {
  .top-header { padding: 20px; }
  .main-layout { flex-direction: column; padding: 0 20px 20px 20px; gap: 24px; }
  .floating-sidebar { flex-direction: row; border-radius: 20px; overflow-x: auto; padding: 12px 20px; justify-content: flex-start; }
  .content-header { flex-direction: column; gap: 16px; margin-bottom: 24px; }
  .content-header h1 { font-size: 2rem; }
  .invitation-card { flex-direction: column; align-items: flex-start; gap: 16px; }
  .invit-actions { width: 100%; justify-content: flex-start; }
  .modal-content { padding: 24px; }
}
</style>