// Mes groupes et ma boîte de réception, partagés entre l'accueil, l'aperçu et l'assistant.
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { groupesApi } from '@/services/groupes'
import { useAuthStore } from '@/stores/auth'

const COULEURS = ['bg-blue', 'bg-purple', 'bg-green', 'bg-red']

// Couleur stable d'une pastille, dérivée de l'id.
export function couleur(id) {
  return COULEURS[(Number(id) || 0) % COULEURS.length]
}

export function initiale(nom) {
  return (nom?.trim().charAt(0) || '?').toUpperCase()
}

export const useGroupesStore = defineStore('groupes', () => {
  const groupes = ref([])
  const invitations = ref([])
  const charge = ref(false)
  const erreur = ref('')

  const token = () => useAuthStore().token

  async function charger() {
    erreur.value = ''
    try {
      const [mesGroupes, mesInvitations] = await Promise.all([
        groupesApi.mesGroupes(token()),
        groupesApi.mesInvitations(token()),
      ])
      groupes.value = mesGroupes
      invitations.value = mesInvitations
      charge.value = true
    } catch (err) {
      erreur.value = err.message
    }
  }

  async function creer(nom) {
    const groupe = await groupesApi.creer(token(), nom)
    groupes.value.push(groupe)
    return groupe
  }

  function mettreAJour(groupe) {
    const i = groupes.value.findIndex((g) => g.id_grp === groupe.id_grp)
    if (i === -1) groupes.value.push(groupe)
    else groupes.value[i] = groupe
  }

  async function rafraichirGroupe(idGrp) {
    mettreAJour(await groupesApi.detail(token(), idGrp))
  }

  async function accepter(invitation) {
    const groupe = await groupesApi.accepter(token(), invitation.id_invit)
    invitations.value = invitations.value.filter((i) => i.id_invit !== invitation.id_invit)
    mettreAJour(groupe)
    return groupe
  }

  async function refuser(invitation) {
    await groupesApi.refuser(token(), invitation.id_invit)
    invitations.value = invitations.value.filter((i) => i.id_invit !== invitation.id_invit)
  }

  // À la déconnexion, on oublie les données de l'utilisateur précédent.
  function vider() {
    groupes.value = []
    invitations.value = []
    charge.value = false
  }

  return {
    groupes,
    invitations,
    charge,
    erreur,
    charger,
    creer,
    rafraichirGroupe,
    accepter,
    refuser,
    vider,
  }
})
