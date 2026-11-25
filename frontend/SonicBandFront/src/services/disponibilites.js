import { apiFetch } from '@/services/api'

// Les disponibilités sont celles de l'utilisateur, communes à tous ses groupes.
export const disponibilitesApi = {
  semaine: (token, semaine) => apiFetch(`/api/disponibilites?semaine=${semaine}`, { token }),
  ajouter: (token, data) => apiFetch('/api/disponibilites', { method: 'POST', body: data, token }),
  modifier: (token, idDispo, data) =>
    apiFetch(`/api/disponibilites/${idDispo}`, { method: 'PUT', body: data, token }),
  supprimer: (token, idDispo, semaine) =>
    apiFetch(`/api/disponibilites/${idDispo}?semaine=${semaine}`, { method: 'DELETE', token }),
  retirerCetteSemaine: (token, idDispo, semaine) =>
    apiFetch(`/api/disponibilites/${idDispo}/retrait?semaine=${semaine}`, {
      method: 'POST',
      token,
    }),
  remettreCetteSemaine: (token, idDispo, semaine) =>
    apiFetch(`/api/disponibilites/${idDispo}/retrait?semaine=${semaine}`, {
      method: 'DELETE',
      token,
    }),
  duGroupe: (token, idGrp, semaine) =>
    apiFetch(`/api/groupes/${idGrp}/disponibilites?semaine=${semaine}`, { token }),
}
