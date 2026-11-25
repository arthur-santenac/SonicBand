<template>
  <section class="repertoire-page">
    <header class="page-heading">
      <div>
        <h2>Répertoire</h2>
        <p>Les morceaux du groupe, visibles de ses seuls membres.</p>
      </div>
    </header>

    <p v-if="erreur" class="notice notice-error" role="alert">{{ erreur }}</p>
    <p v-if="message" class="notice notice-success" role="status">{{ message }}</p>

    <div class="repertoire-toolbar">
      <label class="repertoire-select">
        <span>Répertoire du groupe</span>
        <select v-model="idRepertoire" :disabled="chargement || repertoires.length === 0">
          <option v-for="rep in repertoires" :key="rep.id_rep" :value="rep.id_rep">
            {{ rep.nom_rep }} ({{ rep.morceaux.length }})
          </option>
        </select>
      </label>
      <form class="create-repertoire" @submit.prevent="creerRepertoire">
        <label class="sr-only" for="nouveau-repertoire">Nom du nouveau répertoire</label>
        <input
          id="nouveau-repertoire"
          v-model="nouveauNom"
          maxlength="255"
          placeholder="Nom du répertoire"
          required
        />
        <button type="submit" class="btn-secondary" :disabled="envoiRepertoire">
          {{ envoiRepertoire ? 'Création…' : 'Créer un répertoire' }}
        </button>
      </form>
    </div>

    <p v-if="chargement" class="empty-state">Chargement des répertoires…</p>
    <div v-else-if="repertoireActif" class="repertoire-grid">
      <section class="songs-card" :aria-label="`Morceaux de ${repertoireActif.nom_rep}`">
        <div class="songs-count">
          <strong>{{ repertoireActif.morceaux.length }} morceaux</strong>
          <span>{{ repertoireActif.nom_rep }}</span>
        </div>

        <p v-if="repertoireActif.morceaux.length === 0" class="empty-state">
          Aucun morceau pour le moment. Ajoute le premier depuis le panneau à droite.
        </p>
        <div v-else class="table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Titre</th>
                <th scope="col">Artiste</th>
                <th scope="col">Écouter</th>
                <th scope="col">Pièces jointes</th>
                <th scope="col"><span class="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="morceau in repertoireActif.morceaux" :key="morceau.id_song">
                <td class="song-title">
                  <img v-if="morceau.url_img" :src="morceau.url_img" alt="" />
                  {{ morceau.titre_song }}
                </td>
                <td class="song-artist">{{ morceau.compositeur || 'Artiste inconnu' }}</td>
                <td>
                  <a
                    v-if="morceau.lien_youtube"
                    :href="morceau.lien_youtube"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {{ libelleLien(morceau.lien_youtube) }}
                  </a>
                  <span v-else class="no-link">—</span>
                </td>
                <td class="song-files">
                  <ul v-if="morceau.pieces_jointes?.length" class="file-list">
                    <li v-for="pj in morceau.pieces_jointes" :key="pj.id_pj" class="file-chip">
                      <button
                        type="button"
                        class="file-open"
                        :title="`Télécharger ${pj.nom_fichier} (${tailleLisible(pj.taille)})`"
                        @click="telecharger(morceau, pj)"
                      >
                        <span aria-hidden="true">{{ iconeFichier(pj) }}</span>
                        {{ pj.nom_fichier }}
                      </button>
                      <button
                        type="button"
                        class="file-remove"
                        :aria-label="`Supprimer ${pj.nom_fichier}`"
                        title="Supprimer la pièce jointe"
                        @click="supprimerPieceJointe(morceau, pj)"
                      >
                        ×
                      </button>
                    </li>
                  </ul>
                  <label class="file-add" :class="{ busy: morceauEnEnvoi === morceau.id_song }">
                    <input
                      type="file"
                      multiple
                      class="sr-only"
                      :disabled="morceauEnEnvoi === morceau.id_song"
                      @change="ajouterAuMorceau(morceau, $event)"
                    />
                    {{ morceauEnEnvoi === morceau.id_song ? 'Envoi…' : '+ Joindre' }}
                  </label>
                </td>
                <td class="song-actions">
                  <button
                    type="button"
                    class="btn-delete"
                    :disabled="morceauEnSuppression === morceau.id_song"
                    @click="retirerMorceau(morceau)"
                  >
                    {{ morceauEnSuppression === morceau.id_song ? 'Suppression…' : 'Supprimer' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="add-card">
        <h3>Ajouter un morceau</h3>
        <form class="manual-form" @submit.prevent="ajouterManuellement">
          <label for="titre-morceau">Titre</label>
          <input id="titre-morceau" v-model="titreManuel" maxlength="255" required />
          <label for="artiste-morceau">Artiste</label>
          <input id="artiste-morceau" v-model="artisteManuel" maxlength="255" />
          <label for="youtube-morceau">Lien d'écoute (YouTube, Spotify…)</label>
          <input
            id="youtube-morceau"
            v-model="youtubeManuel"
            type="url"
            maxlength="255"
            placeholder="https://youtube.com/…"
          />
          <label for="pj-morceau">Pièces jointes</label>
          <div class="file-drop">
            <input
              id="pj-morceau"
              ref="champFichiers"
              type="file"
              multiple
              @change="choisirFichiers"
            />
            <p class="hint">
              Partition, tablature, maquette audio, paroles… {{ NB_MAX_PJ }} fichiers de
              {{ TAILLE_MAX_MO }} Mo maximum.
            </p>
            <ul v-if="fichiersManuels.length" class="file-list">
              <li v-for="(f, i) in fichiersManuels" :key="i" class="file-chip">
                <span class="file-open static">
                  <span aria-hidden="true">{{
                    iconeFichier({ type_mime: f.type, nom_fichier: f.name })
                  }}</span>
                  {{ f.name }}
                </span>
                <button
                  type="button"
                  class="file-remove"
                  :aria-label="`Ne pas joindre ${f.name}`"
                  @click="fichiersManuels.splice(i, 1)"
                >
                  ×
                </button>
              </li>
            </ul>
          </div>
          <button type="submit" class="btn-primary" :disabled="envoiManuel || !repertoireActif">
            {{ envoiManuel ? 'Ajout…' : 'Ajouter au répertoire' }}
          </button>
        </form>
      </aside>
    </div>
    <p v-else class="empty-state">Crée un répertoire pour commencer à ajouter des morceaux.</p>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { repertoiresApi } from '@/services/repertoires'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  idGrp: {
    type: Number,
    required: true,
  },
})

const auth = useAuthStore()
const repertoires = ref([])
const idRepertoire = ref(null)
const chargement = ref(true)
const erreur = ref('')
const message = ref('')
const nouveauNom = ref('')
const envoiRepertoire = ref(false)
const titreManuel = ref('')
const artisteManuel = ref('')
const youtubeManuel = ref('')
const envoiManuel = ref(false)
const morceauEnSuppression = ref(null)
const morceauEnEnvoi = ref(null)
const fichiersManuels = ref([])
const champFichiers = ref(null)

// Mêmes limites que le backend (backend/repertoires.py).
const TAILLE_MAX_MO = 10
const NB_MAX_PJ = 10

const repertoireActif = computed(
  () => repertoires.value.find((repertoire) => repertoire.id_rep === idRepertoire.value) ?? null,
)

watch(
  () => props.idGrp,
  () => charger(),
  { immediate: true },
)

async function charger() {
  chargement.value = true
  erreur.value = ''
  message.value = ''
  try {
    repertoires.value = await repertoiresApi.lister(auth.token, props.idGrp)
    if (!repertoires.value.some((repertoire) => repertoire.id_rep === idRepertoire.value)) {
      idRepertoire.value = repertoires.value[0]?.id_rep ?? null
    }
  } catch (err) {
    erreur.value = err.message
  } finally {
    chargement.value = false
  }
}

async function creerRepertoire() {
  if (!nouveauNom.value.trim()) return
  envoiRepertoire.value = true
  erreur.value = ''
  message.value = ''
  try {
    const repertoire = await repertoiresApi.creer(auth.token, props.idGrp, nouveauNom.value.trim())
    repertoires.value.push(repertoire)
    idRepertoire.value = repertoire.id_rep
    nouveauNom.value = ''
    message.value = 'Répertoire créé.'
  } catch (err) {
    erreur.value = err.message
  } finally {
    envoiRepertoire.value = false
  }
}

async function enregistrerMorceau(morceau) {
  const ajoute = await repertoiresApi.ajouterMorceau(
    auth.token,
    props.idGrp,
    repertoireActif.value.id_rep,
    morceau,
  )
  repertoireActif.value.morceaux.push(ajoute)
  // On renvoie l'objet réactif stocké dans la liste, pour pouvoir le compléter ensuite.
  return repertoireActif.value.morceaux.at(-1)
}

function libelleLien(url) {
  try {
    const hote = new URL(url).hostname.replace(/^www\./, '')
    if (hote.includes('youtu')) return 'YouTube'
    if (hote.includes('spotify')) return 'Spotify'
    if (hote.includes('deezer')) return 'Deezer'
    if (hote.includes('soundcloud')) return 'SoundCloud'
    return hote
  } catch {
    return 'Lien'
  }
}

function tailleLisible(octets) {
  if (octets < 1024) return `${octets} o`
  if (octets < 1024 * 1024) return `${Math.round(octets / 1024)} Ko`
  return `${(octets / (1024 * 1024)).toFixed(1).replace('.', ',')} Mo`
}

function iconeFichier(pj) {
  const type = pj.type_mime || ''
  const nom = (pj.nom_fichier || '').toLowerCase()
  if (type.startsWith('audio/')) return '🎵'
  if (type.startsWith('video/')) return '🎬'
  if (type.startsWith('image/')) return '🖼️'
  if (type === 'application/pdf' || nom.endsWith('.pdf')) return '📄'
  return '📎'
}

// Vérifie les fichiers côté navigateur avant l'envoi ; renvoie un message d'erreur ou ''.
function verifierFichiers(fichiers, deja = 0) {
  if (deja + fichiers.length > NB_MAX_PJ) {
    return `Un morceau peut avoir au plus ${NB_MAX_PJ} pièces jointes.`
  }
  const tropGros = fichiers.find((f) => f.size > TAILLE_MAX_MO * 1024 * 1024)
  if (tropGros) return `« ${tropGros.name} » dépasse ${TAILLE_MAX_MO} Mo.`
  const vide = fichiers.find((f) => f.size === 0)
  if (vide) return `« ${vide.name} » est vide.`
  return ''
}

function choisirFichiers(event) {
  const nouveaux = [...fichiersManuels.value, ...event.target.files]
  event.target.value = ''
  const probleme = verifierFichiers(nouveaux)
  if (probleme) {
    erreur.value = probleme
    return
  }
  erreur.value = ''
  fichiersManuels.value = nouveaux
}

async function envoyerPiecesJointes(morceau, fichiers) {
  const ajoutees = await repertoiresApi.ajouterPiecesJointes(
    auth.token,
    props.idGrp,
    repertoireActif.value.id_rep,
    morceau.id_song,
    fichiers,
  )
  morceau.pieces_jointes = [...(morceau.pieces_jointes ?? []), ...ajoutees]
}

async function ajouterAuMorceau(morceau, event) {
  const fichiers = [...event.target.files]
  event.target.value = ''
  if (fichiers.length === 0) return
  erreur.value = ''
  message.value = ''
  const probleme = verifierFichiers(fichiers, morceau.pieces_jointes?.length ?? 0)
  if (probleme) {
    erreur.value = probleme
    return
  }
  morceauEnEnvoi.value = morceau.id_song
  try {
    await envoyerPiecesJointes(morceau, fichiers)
    message.value =
      fichiers.length > 1
        ? `${fichiers.length} fichiers joints à ${morceau.titre_song}.`
        : `${fichiers[0].name} joint à ${morceau.titre_song}.`
  } catch (err) {
    erreur.value = err.message
  } finally {
    morceauEnEnvoi.value = null
  }
}

async function telecharger(morceau, pj) {
  erreur.value = ''
  try {
    const blob = await repertoiresApi.telechargerPieceJointe(
      auth.token,
      props.idGrp,
      repertoireActif.value.id_rep,
      morceau.id_song,
      pj.id_pj,
    )
    const url = URL.createObjectURL(blob)
    const lien = document.createElement('a')
    lien.href = url
    lien.download = pj.nom_fichier
    document.body.appendChild(lien)
    lien.click()
    lien.remove()
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  } catch (err) {
    erreur.value = err.message
  }
}

async function supprimerPieceJointe(morceau, pj) {
  if (!window.confirm(`Supprimer la pièce jointe « ${pj.nom_fichier} » ?`)) return
  erreur.value = ''
  message.value = ''
  try {
    await repertoiresApi.supprimerPieceJointe(
      auth.token,
      props.idGrp,
      repertoireActif.value.id_rep,
      morceau.id_song,
      pj.id_pj,
    )
    morceau.pieces_jointes = morceau.pieces_jointes.filter((x) => x.id_pj !== pj.id_pj)
    message.value = `${pj.nom_fichier} supprimé.`
  } catch (err) {
    erreur.value = err.message
  }
}

async function ajouterManuellement() {
  if (!titreManuel.value.trim() || !repertoireActif.value) return
  envoiManuel.value = true
  erreur.value = ''
  message.value = ''
  const titre = titreManuel.value.trim()
  const fichiers = [...fichiersManuels.value]
  try {
    const morceau = await enregistrerMorceau({
      titre_song: titre,
      compositeur: artisteManuel.value.trim() || null,
      lien_youtube: youtubeManuel.value.trim() || null,
      url_img: null,
    })
    titreManuel.value = ''
    artisteManuel.value = ''
    youtubeManuel.value = ''
    fichiersManuels.value = []
    if (fichiers.length > 0) {
      try {
        await envoyerPiecesJointes(morceau, fichiers)
      } catch (err) {
        erreur.value = `${titre} a été ajouté, mais pas ses pièces jointes : ${err.message}`
        return
      }
    }
    message.value =
      fichiers.length > 0
        ? `${titre} ajouté au répertoire avec ${fichiers.length} pièce${fichiers.length > 1 ? 's' : ''} jointe${fichiers.length > 1 ? 's' : ''}.`
        : `${titre} ajouté au répertoire.`
  } catch (err) {
    erreur.value = err.message
  } finally {
    envoiManuel.value = false
  }
}

async function retirerMorceau(morceau) {
  morceauEnSuppression.value = morceau.id_song
  erreur.value = ''
  message.value = ''
  try {
    await repertoiresApi.retirerMorceau(
      auth.token,
      props.idGrp,
      repertoireActif.value.id_rep,
      morceau.id_song,
    )
    repertoireActif.value.morceaux = repertoireActif.value.morceaux.filter(
      (item) => item.id_song !== morceau.id_song,
    )
    message.value = `${morceau.titre_song} retiré du répertoire.`
  } catch (err) {
    erreur.value = err.message
  } finally {
    morceauEnSuppression.value = null
  }
}
</script>

<style scoped>
.repertoire-page {
  min-width: 0;
}

.page-heading {
  margin-bottom: 24px;
}

.page-heading h2 {
  margin: 0 0 8px;
  color: #15151a;
  font-size: 1.8rem;
}

.page-heading p,
.empty-state {
  margin: 0;
  color: #747987;
}

.notice {
  padding: 12px 16px;
  border-radius: 12px;
  margin: 0 0 16px;
}

.notice-error {
  color: #a92c24;
  background: #fdf0ef;
}

.notice-success {
  color: #22623a;
  background: #eaf6ed;
}

.repertoire-toolbar {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.repertoire-select {
  display: grid;
  gap: 6px;
  color: #5f6470;
  font-size: 0.85rem;
  font-weight: 600;
}

.repertoire-select select,
.create-repertoire input,
.manual-form input {
  box-sizing: border-box;
  min-height: 44px;
  padding: 10px 14px;
  border: 1px solid #e1e4eb;
  border-radius: 12px;
  color: #202127;
  background: #f6f7fa;
  font: inherit;
}

.repertoire-select select {
  min-width: 220px;
}

.create-repertoire {
  display: flex;
  gap: 8px;
}

.create-repertoire input {
  width: min(230px, 30vw);
}

.btn-secondary,
.btn-primary {
  min-height: 42px;
  padding: 9px 16px;
  border: 0;
  border-radius: 22px;
  color: white;
  background: #17171c;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.repertoire-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(300px, 1fr);
  align-items: start;
  gap: 16px;
}

.songs-card,
.add-card {
  min-width: 0;
  padding: 24px;
  border: 1px solid #e6e8ed;
  border-radius: 20px;
  background: white;
  box-shadow: 0 1px 4px rgb(0 0 0 / 3%);
}

.songs-count {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  color: #707582;
  font-size: 0.9rem;
}

.songs-count strong {
  color: #25262c;
}

.table-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 12px 8px;
  border-bottom: 1px solid #eceef2;
  font-size: 0.9rem;
}

th {
  color: #777d89;
  font-size: 0.82rem;
  font-weight: 600;
}

.song-title {
  min-width: 140px;
  color: #292a30;
  font-weight: 600;
}

.song-title img {
  width: 38px;
  height: 38px;
  margin-right: 8px;
  border-radius: 6px;
  object-fit: cover;
  vertical-align: middle;
}

.song-artist,
.no-link {
  color: #737986;
}

td a {
  color: #292a30;
  text-decoration: underline;
}

.song-actions {
  text-align: right;
}

.song-files {
  min-width: 150px;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 6px;
  padding: 0;
  list-style: none;
}

.file-chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  border: 1px solid #e1e4eb;
  border-radius: 16px;
  background: #f6f7fa;
}

.file-open {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  max-width: 190px;
  overflow: hidden;
  padding: 4px 4px 4px 10px;
  border: 0;
  color: #292a30;
  background: none;
  font: inherit;
  font-size: 0.8rem;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.file-open:hover {
  text-decoration: underline;
}

.file-open.static {
  cursor: default;
  text-decoration: none;
}

.file-remove {
  padding: 2px 9px 2px 4px;
  border: 0;
  color: #8a8f9b;
  background: none;
  font: inherit;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
}

.file-remove:hover {
  color: #c53930;
}

.file-add {
  display: inline-block;
  padding: 4px 10px;
  border: 1px dashed #c8ccd5;
  border-radius: 16px;
  color: #5f6470;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.file-add:hover {
  border-color: #17171c;
  color: #17171c;
}

.file-add.busy {
  cursor: wait;
  opacity: 0.6;
}

.file-drop {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px dashed #d4d8e0;
  border-radius: 12px;
  background: #fafbfc;
}

.file-drop input[type='file'] {
  min-height: 0;
  padding: 2px;
  border: 0;
  background: none;
  font-size: 0.85rem;
}

.file-drop .hint {
  margin: 0;
  color: #747987;
  font-size: 0.78rem;
}

.file-drop .file-list {
  margin: 0;
}

.btn-delete {
  padding: 7px 12px;
  border: 1px solid #d84339;
  border-radius: 22px;
  color: #c53930;
  background: white;
  font: inherit;
  font-size: 0.82rem;
  cursor: pointer;
}

.add-card h3 {
  margin: 0 0 16px;
  color: #22232a;
  font-size: 1.05rem;
}

.manual-form {
  display: grid;
  gap: 8px;
}

.manual-form label {
  margin-top: 4px;
  color: #34353b;
  font-size: 0.86rem;
  font-weight: 600;
}

.manual-form .btn-primary {
  width: 100%;
  margin-top: 4px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

@media (max-width: 1000px) {
  .repertoire-grid {
    grid-template-columns: 1fr;
  }

  .add-card {
    max-width: none;
  }
}

@media (max-width: 640px) {
  .repertoire-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .repertoire-select select,
  .create-repertoire input {
    width: 100%;
  }

  .create-repertoire {
    flex-direction: column;
  }

  .songs-card,
  .add-card {
    padding: 16px;
  }

  th,
  td {
    padding-inline: 6px;
  }

  .btn-delete {
    padding: 6px 9px;
  }
}
</style>
