// Outils de dates pour le calendrier des disponibilités (semaine du lundi au dimanche).

export const JOURS_COURTS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
export const JOURS_LONGS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
const MOIS = [
  'janv',
  'févr',
  'mars',
  'avr',
  'mai',
  'juin',
  'juil',
  'août',
  'sept',
  'oct',
  'nov',
  'déc',
]

// « 2026-11-09 » -> Date locale (sans décalage de fuseau).
export function parseIso(iso) {
  const [a, m, j] = iso.split('-').map(Number)
  return new Date(a, m - 1, j)
}

export function toIso(date) {
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const j = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${m}-${j}`
}

export function ajouterJours(date, n) {
  const copie = new Date(date)
  copie.setDate(copie.getDate() + n)
  return copie
}

// Lundi de la semaine contenant `date`.
export function lundiDe(date = new Date()) {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  return ajouterJours(d, -((d.getDay() + 6) % 7))
}

export function joursDeLaSemaine(lundi) {
  return JOURS_COURTS.map((court, i) => {
    const date = ajouterJours(lundi, i)
    return { index: i, court, numero: date.getDate(), iso: toIso(date) }
  })
}

// « 9 – 15 nov », ou « 30 nov – 6 déc » quand la semaine change de mois.
export function libelleSemaine(lundi) {
  const dimanche = ajouterJours(lundi, 6)
  const fin = `${dimanche.getDate()} ${MOIS[dimanche.getMonth()]}`
  if (lundi.getMonth() === dimanche.getMonth()) return `${lundi.getDate()} – ${fin}`
  return `${lundi.getDate()} ${MOIS[lundi.getMonth()]} – ${fin}`
}

// « 19:30 » -> minutes depuis minuit ; une fin à 23:59 compte jusqu'à minuit.
export function versMinutes(hhmm, fin = false) {
  const [h, m] = hhmm.split(':').map(Number)
  const total = h * 60 + m
  return fin && total >= 23 * 60 + 59 ? 24 * 60 : total
}

// 1170 -> « 19h30 », 1140 -> « 19h », 1440 -> « 24h »
export function formatMinutes(total) {
  const h = Math.floor(total / 60)
  const m = total % 60
  return m === 0 ? `${h}h` : `${h}h${String(m).padStart(2, '0')}`
}

export function formatPlage(debut, fin) {
  if (debut === 0 && fin === 24 * 60) return 'Toute la journée'
  return `${formatMinutes(debut)} – ${formatMinutes(fin)}`
}

// Heat map du groupe : du bleu le plus clair (1 musicien libre) au bleu foncé de la
// maquette (tout le groupe libre).
const BLEU_CLAIR = [220, 232, 251]
const BLEU_FONCE = [45, 98, 200]

export function couleurHeatmap(nbLibres, nbMembres) {
  const t = nbMembres <= 1 ? 1 : Math.min(1, Math.max(0, (nbLibres - 1) / (nbMembres - 1)))
  const rgb = BLEU_CLAIR.map((c, i) => Math.round(c + (BLEU_FONCE[i] - c) * t))
  return { background: `rgb(${rgb.join(', ')})`, color: t > 0.5 ? 'white' : '#10284f' }
}

export function degradeHeatmap() {
  return `linear-gradient(to right, rgb(${BLEU_CLAIR.join(', ')}), rgb(${BLEU_FONCE.join(', ')}))`
}
