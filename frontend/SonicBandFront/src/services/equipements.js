import { apiFetch } from '@/services/api'

export const equipementsApi = {
  duGroupe: (token, idGrp) =>
    apiFetch(`/api/groupes/${idGrp}/equipements`, { token }),
  ajouterAuGroupe: (token, idGrp, nomEquipement) =>
    apiFetch(`/api/groupes/${idGrp}/equipements`, {
      method: 'POST',
      body: { nom_equipement: nomEquipement },
      token,
    }),
  retirerDuGroupe: (token, idGrp, idEquipement) =>
    apiFetch(`/api/groupes/${idGrp}/equipements/${idEquipement}`, {
      method: 'DELETE',
      token,
    }),
  personnels: (token) => apiFetch('/api/equipements/personnels', { token }),
  ajouterPersonnel: (token, nomEquipement) =>
    apiFetch('/api/equipements/personnels', {
      method: 'POST',
      body: { nom_equipement: nomEquipement },
      token,
    }),
  retirerPersonnel: (token, idEquipement) =>
    apiFetch(`/api/equipements/personnels/${idEquipement}`, {
      method: 'DELETE',
      token,
    }),
}
