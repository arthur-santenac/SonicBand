<template>
  <div class="app-wrapper">
    <header class="top-header">
      <RouterLink to="/home" class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo-icon" />
        <span class="logo-text">sonicBand</span>
      </RouterLink>
      <div class="avatar" :title="userName">{{ initiale(userName) }}</div>
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
        <RouterLink
          v-for="g in store.groupes"
          :key="g.id_grp"
          :to="{ name: 'group', params: { id: g.id_grp } }"
          class="sidebar-bubble"
          :class="[couleur(g.id_grp), { active: g.id_grp === idGrp }]"
          :title="g.nom_grp"
        >
          {{ initiale(g.nom_grp) }}
        </RouterLink>
        <RouterLink
          :to="{ name: 'create-group' }"
          class="sidebar-bubble create-dashed"
          :class="{ active: etape === 1 }"
          title="Créer un groupe"
        >
          +
        </RouterLink>
      </nav>

      <main class="wizard">
        <!-- Étapes -->
        <ol class="stepper">
          <li class="step" :class="{ current: etape === 1, done: etape > 1 }">
            <span class="step-dot">{{ etape > 1 ? '✓' : '1' }}</span> Ton groupe
          </li>
          <li class="step-line" aria-hidden="true"></li>
          <li class="step" :class="{ current: etape === 2 }">
            <span class="step-dot">2</span> Tes musiciens
          </li>
        </ol>

        <!-- Étape 1 : nom du groupe -->
        <template v-if="etape === 1">
          <h1>Crée ton groupe</h1>
          <p class="subtitle">
            Tu en seras le super admin. Tu pourras inviter les musiciens à l'étape suivante.
          </p>

          <form id="create-form" class="card" @submit.prevent="creerGroupe">
            <p v-if="erreur" class="form-error" role="alert">{{ erreur }}</p>
            <label for="nom-groupe" class="field-label">Nom du groupe</label>
            <input
              id="nom-groupe"
              v-model="nom"
              type="text"
              maxlength="255"
              placeholder="Nirvana"
              autocomplete="off"
              required
            />
            <div class="photo-row">
              <div class="photo-preview" :class="couleur(store.groupes.length + 1)">
                {{ initiale(nom) }}
              </div>
              <div>
                <p class="field-label">Photo du groupe</p>
                <p class="hint">Pour l'instant, la pastille affiche l'initiale du groupe.</p>
              </div>
            </div>
          </form>

          <div class="actions">
            <button type="submit" form="create-form" class="btn-primary" :disabled="envoi">
              {{ envoi ? 'Création…' : 'Créer le groupe' }}
            </button>
            <RouterLink to="/home" class="btn-secondary">Annuler</RouterLink>
          </div>
        </template>

        <!-- Étape 2 : inviter les musiciens -->
        <template v-else>
          <h1>Gère les musiciens</h1>
          <p class="subtitle">
            Invite un musicien par e-mail : il recevra l'invitation dans sa boîte de réception. Tu
            peux retirer quelqu'un à tout moment.
          </p>

          <MembresGroupe :id-grp="idGrp" :mon-role="groupe?.mon_role ?? 'membre'" />

          <div class="actions">
            <RouterLink :to="{ name: 'group', params: { id: idGrp } }" class="btn-primary">
              Terminer
            </RouterLink>
            <RouterLink to="/home" class="btn-secondary">Plus tard</RouterLink>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import MembresGroupe from '@/components/MembresGroupe.vue'
import { useAuthStore } from '@/stores/auth'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useGroupesStore()

// /groups/new → étape 1 ; /groups/:id/musiciens → étape 2
const etape = computed(() => (route.name === 'group-musicians' ? 2 : 1))
const idGrp = computed(() => (route.params.id ? Number(route.params.id) : null))
const groupe = computed(() => store.groupes.find((g) => g.id_grp === idGrp.value) ?? null)
const userName = computed(() => auth.user?.nom_user ?? '')

const nom = ref('')
const erreur = ref('')
const envoi = ref(false)

async function creerGroupe() {
  erreur.value = ''
  if (!nom.value.trim()) {
    erreur.value = 'Le nom du groupe est obligatoire.'
    return
  }
  envoi.value = true
  try {
    const g = await store.creer(nom.value.trim())
    router.push({ name: 'group-musicians', params: { id: g.id_grp } })
  } catch (err) {
    erreur.value = err.message
  } finally {
    envoi.value = false
  }
}

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

.top-header {
  padding: 24px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: #aecbfa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #000;
}

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
  text-decoration: none;
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

/* --- Assistant --- */
.wizard {
  flex: 1;
  max-width: 620px;
  margin: 0 auto;
  min-width: 0;
}

.stepper {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  color: #65676b;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step.current {
  color: #1c1e21;
  font-weight: 600;
}

.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid #ccd0d5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  background: white;
}

.step.current .step-dot {
  background: #1c1e21;
  border-color: #1c1e21;
  color: white;
}

.step.done .step-dot {
  background: #aecbfa;
  border-color: #aecbfa;
  color: #1c3d7a;
}

.step-line {
  width: 40px;
  height: 1px;
  background: #ccd0d5;
}

h1 {
  font-size: 2.2rem;
  margin: 0 0 8px 0;
  font-weight: 700;
  color: #000;
  letter-spacing: -0.5px;
}

.subtitle {
  color: #65676b;
  margin: 0 0 24px 0;
}

.card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.field-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.card input {
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 1rem;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #1c1e21;
  color: #1c1e21;
}

.photo-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.photo-preview {
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

.hint {
  margin: 0;
  font-size: 0.85rem;
  color: #65676b;
}

.form-error {
  background: #fdf0ef;
  color: #c0322b;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 0 16px 0;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  line-height: 1.2;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 30px;
  padding: 14px 24px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
}

.btn-primary {
  background: #1c1e21;
  color: white;
  border: none;
}

.btn-primary:disabled {
  opacity: 0.6;
}

.btn-secondary {
  background: white;
  color: #1c1e21;
  border: 1px solid #ccd0d5;
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
  .top-header {
    padding: 20px;
  }
  .main-layout {
    flex-direction: column;
    padding: 0 16px 20px 16px;
    gap: 24px;
  }
  .floating-sidebar {
    flex-direction: row;
    border-radius: 20px;
    overflow-x: auto;
    padding: 12px 20px;
  }
  h1 {
    font-size: 1.8rem;
  }
  .actions {
    flex-direction: column;
  }
}
</style>
