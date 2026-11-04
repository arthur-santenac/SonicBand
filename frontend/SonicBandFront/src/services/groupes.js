// Appels à l'API des groupes, membres et invitations (voir backend/groupes.py).
import { apiFetch } from '@/services/api'

export const groupesApi = {
  mesGroupes: (token) => apiFetch('/api/groupes', { token }),
  creer: (token, nom) => apiFetch('/api/groupes', { method: 'POST', body: { nom }, token }),
  detail: (token, idGrp) => apiFetch(`/api/groupes/${idGrp}`, { token }),

  membres: (token, idGrp) => apiFetch(`/api/groupes/${idGrp}/membres`, { token }),
  retirerMembre: (token, idGrp, idUser) =>
    apiFetch(`/api/groupes/${idGrp}/membres/${idUser}`, { method: 'DELETE', token }),

  inviter: (token, idGrp, email) =>
    apiFetch(`/api/groupes/${idGrp}/invitations`, { method: 'POST', body: { email }, token }),
  annulerInvitation: (token, idGrp, idInvit) =>
    apiFetch(`/api/groupes/${idGrp}/invitations/${idInvit}`, { method: 'DELETE', token }),

  mesInvitations: (token) => apiFetch('/api/invitations', { token }),
  accepter: (token, idInvit) =>
    apiFetch(`/api/invitations/${idInvit}/accepter`, { method: 'POST', token }),
  refuser: (token, idInvit) =>
    apiFetch(`/api/invitations/${idInvit}/refuser`, { method: 'POST', token }),
}
