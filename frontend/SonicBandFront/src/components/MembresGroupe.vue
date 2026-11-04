<template>
  <div class="membres-card">
    <form v-if="peutGerer" class="invite-form" @submit.prevent="envoyerInvitation">
      <label for="invite-email" class="field-label">Inviter un musicien</label>
      <div class="invite-row">
        <input
          id="invite-email"
          v-model="email"
          type="email"
          placeholder="musicien@exemple.fr"
          autocomplete="off"
          required
        />
        <button type="submit" class="btn-dark" :disabled="envoi">
          {{ envoi ? 'Envoi…' : 'Inviter' }}
        </button>
      </div>
      <p v-if="message" class="feedback" :class="{ error: messageErreur }" role="status">
        {{ message }}
      </p>
    </form>

    <p class="list-title">Dans le groupe</p>
    <p v-if="chargement" class="muted">Chargement…</p>
    <p v-else-if="erreur" class="feedback error" role="alert">{{ erreur }}</p>

    <ul v-else class="member-list">
      <li v-for="m in membres" :key="'m' + m.id_user" class="member-row">
        <div class="member-bubble" :class="couleur(m.id_user)">{{ initiale(m.nom_user) }}</div>
        <div class="member-info">
          <strong>{{ m.nom_user }}<span v-if="m.id_user === monId"> (toi)</span></strong>
          <span>{{ m.email_user }}</span>
        </div>
        <span class="tag" :class="'tag-' + m.role">{{ libelleRole(m) }}</span>
        <button v-if="peutRetirer(m)" type="button" class="btn-remove" @click="retirerMembre(m)">
          Retirer
        </button>
      </li>

      <li v-for="inv in invitations" :key="'i' + inv.id_invit" class="member-row">
        <div class="member-bubble bg-grey">{{ initiale(inv.nom_user || inv.email_invit) }}</div>
        <div class="member-info">
          <strong>{{ inv.nom_user || inv.email_invit.split('@')[0] }}</strong>
          <span>{{ inv.email_invit }}</span>
        </div>
        <span class="tag tag-invite">Invitation envoyée</span>
        <button v-if="peutGerer" type="button" class="btn-remove" @click="annuler(inv)">
          Retirer
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { couleur, initiale, useGroupesStore } from '@/stores/groupes'
import { groupesApi } from '@/services/groupes'

const props = defineProps({
  idGrp: { type: Number, required: true },
  // Rôle de l'utilisateur connecté dans ce groupe : super_admin, admin ou membre.
  monRole: { type: String, default: 'membre' },
})

const auth = useAuthStore()
const store = useGroupesStore()

const membres = ref([])
const invitations = ref([])
const chargement = ref(true)
const erreur = ref('')

const email = ref('')
const envoi = ref(false)
const message = ref('')
const messageErreur = ref(false)

const monId = computed(() => auth.user?.id_user)
const peutGerer = computed(() => ['super_admin', 'admin'].includes(props.monRole))

function libelleRole(m) {
  if (m.role === 'super_admin') return 'Super admin'
  if (m.role === 'admin') return 'Admin'
  // Sur la maquette, les musiciens qui ont accepté l'invitation sont « A rejoint ».
  return 'A rejoint'
}

// Même règle que le backend : le super admin retire tout le monde sauf lui-même,
// un admin ne retire que les membres.
function peutRetirer(m) {
  if (m.role === 'super_admin' || m.id_user === monId.value) return false
  if (props.monRole === 'super_admin') return true
  return props.monRole === 'admin' && m.role === 'membre'
}

async function charger() {
  chargement.value = true
  erreur.value = ''
  try {
    const data = await groupesApi.membres(auth.token, props.idGrp)
    membres.value = data.membres
    invitations.value = data.invitations
  } catch (err) {
    erreur.value = err.message
  } finally {
    chargement.value = false
  }
}

async function envoyerInvitation() {
  message.value = ''
  envoi.value = true
  try {
    const inv = await groupesApi.inviter(auth.token, props.idGrp, email.value.trim())
    invitations.value.push(inv)
    message.value = `Invitation envoyée à ${inv.email_invit}.`
    messageErreur.value = false
    email.value = ''
  } catch (err) {
    message.value = err.message
    messageErreur.value = true
  } finally {
    envoi.value = false
  }
}

async function retirerMembre(m) {
  if (!window.confirm(`Retirer ${m.nom_user} du groupe ?`)) return
  try {
    await groupesApi.retirerMembre(auth.token, props.idGrp, m.id_user)
    membres.value = membres.value.filter((x) => x.id_user !== m.id_user)
    store.rafraichirGroupe(props.idGrp).catch(() => {})
  } catch (err) {
    window.alert(err.message)
  }
}

async function annuler(inv) {
  if (!window.confirm(`Annuler l'invitation envoyée à ${inv.email_invit} ?`)) return
  try {
    await groupesApi.annulerInvitation(auth.token, props.idGrp, inv.id_invit)
    invitations.value = invitations.value.filter((x) => x.id_invit !== inv.id_invit)
  } catch (err) {
    window.alert(err.message)
  }
}

onMounted(charger)
watch(() => props.idGrp, charger)
</script>

<style scoped>
.membres-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.field-label,
.list-title {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1c1e21;
  margin: 0 0 8px 0;
}

.list-title {
  margin-top: 20px;
  color: #65676b;
  font-weight: 500;
}

.invite-row {
  display: flex;
  gap: 10px;
}

.invite-row input {
  flex: 1;
  min-width: 0;
  font-family: inherit;
  font-size: 0.95rem;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #ccd0d5;
  background: #f4f5f7;
  color: #1c1e21;
}

.invite-row input:focus {
  outline: none;
  border-color: #1c1e21;
  background: white;
}

.btn-dark {
  font-family: inherit;
  background: #1c1e21;
  color: white;
  border: none;
  border-radius: 30px;
  padding: 10px 22px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-dark:disabled {
  opacity: 0.6;
  cursor: default;
}

.feedback {
  margin: 8px 0 0 0;
  font-size: 0.85rem;
  color: #1e7a3a;
}

.feedback.error {
  color: #c0322b;
}

.muted {
  color: #65676b;
  font-size: 0.9rem;
}

.member-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.member-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid #f0f2f5;
}

.member-bubble {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #000;
  flex-shrink: 0;
}

.member-info {
  display: flex;
  flex-direction: column;
  margin-right: auto;
  min-width: 0;
}

.member-info strong {
  font-size: 0.95rem;
  color: #000;
}

.member-info span {
  font-size: 0.85rem;
  color: #65676b;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
}

.tag-super_admin {
  background: #1c1e21;
  color: white;
}

.tag-admin,
.tag-membre {
  background: #d6e4fd;
  color: #1c3d7a;
}

.tag-invite {
  background: #e4e6eb;
  color: #1c1e21;
}

.btn-remove {
  font-family: inherit;
  background: white;
  border: 1px solid #e3a6a2;
  color: #c0322b;
  border-radius: 30px;
  padding: 6px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-remove:hover {
  background: #fdf0ef;
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
.bg-grey {
  background-color: #e4e6eb;
}

@media (max-width: 600px) {
  .member-row {
    flex-wrap: wrap;
  }
  .member-info {
    flex-basis: calc(100% - 52px);
  }
  .tag {
    margin-left: 52px;
  }
}
</style>
