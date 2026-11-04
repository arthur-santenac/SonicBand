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
                    YouTube
                  </a>
                  <span v-else class="no-link">—</span>
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
          <label for="youtube-morceau">Lien YouTube</label>
          <input
            id="youtube-morceau"
            v-model="youtubeManuel"
            type="url"
            maxlength="255"
            placeholder="https://youtube.com/…"
          />
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
}

async function ajouterManuellement() {
  if (!titreManuel.value.trim() || !repertoireActif.value) return
  envoiManuel.value = true
  erreur.value = ''
  message.value = ''
  try {
    await enregistrerMorceau({
      titre_song: titreManuel.value.trim(),
      compositeur: artisteManuel.value.trim() || null,
      lien_youtube: youtubeManuel.value.trim() || null,
      url_img: null,
    })
    message.value = `${titreManuel.value.trim()} ajouté au répertoire.`
    titreManuel.value = ''
    artisteManuel.value = ''
    youtubeManuel.value = ''
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
