import { apiBlob, apiFetch } from '@/services/api'

const morceauUrl = (idGrp, idRep, idSong) =>
  `/api/groupes/${idGrp}/repertoires/${idRep}/morceaux/${idSong}`

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
  ajouterPiecesJointes: (token, idGrp, idRep, idSong, fichiers) => {
    const body = new FormData()
    for (const fichier of fichiers) body.append('fichiers', fichier)
    return apiFetch(`${morceauUrl(idGrp, idRep, idSong)}/pieces-jointes`, {
      method: 'POST',
      body,
      token,
    })
  },
  telechargerPieceJointe: (token, idGrp, idRep, idSong, idPj) =>
    apiBlob(`${morceauUrl(idGrp, idRep, idSong)}/pieces-jointes/${idPj}`, { token }),
  supprimerPieceJointe: (token, idGrp, idRep, idSong, idPj) =>
    apiFetch(`${morceauUrl(idGrp, idRep, idSong)}/pieces-jointes/${idPj}`, {
      method: 'DELETE',
      token,
    }),
}
