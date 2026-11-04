<template>
  <AppLayout>
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
  </AppLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import MembresGroupe from '@/components/MembresGroupe.vue'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'

const route = useRoute()
const router = useRouter()
const store = useGroupesStore()

const etape = computed(() => (route.name === 'group-musicians' ? 2 : 1))
const idGrp = computed(() => (route.params.id ? Number(route.params.id) : null))
const groupe = computed(() => store.groupes.find((g) => g.id_grp === idGrp.value) ?? null)

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
</script>

<style scoped>
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
  h1 {
    font-size: 1.8rem;
  }
  .actions {
    flex-direction: column;
  }
}
</style>