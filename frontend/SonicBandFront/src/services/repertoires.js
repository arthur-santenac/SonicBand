import { apiFetch } from '@/services/api'

export const repertoiresApi = {
  lister: (token, idGrp) => apiFetch(`/api/groupes/${idGrp}/repertoires`, { token }),
  creer: (token, idGrp, nomRep) =>
    apiFetch(`/api/groupes/${idGrp}/repertoires`, {
      method: 'POST',
      body: { nom_rep: nomRep },
      token,
    }),
  ajouterMorceau: (token, idGrp, idRep, morceau) =>
    apiFetch(`/api/groupes/${idGrp}/repertoires/${idRep}/morceaux`, {
      method: 'POST',
      body: morceau,
      token,
    }),
  retirerMorceau: (token, idGrp, idRep, idSong) =>
    apiFetch(`/api/groupes/${idGrp}/repertoires/${idRep}/morceaux/${idSong}`, {
      method: 'DELETE',
      token,
    }),
}
