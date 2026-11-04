import { reactive } from 'vue'

const evenementsParNom = reactive({
  nirvana: [
    {
      id: 1,
      day: 'Ven 13 nov',
      time: '19h – 22h',
      type: 'Répétition',
      place: 'Studio Nord',
      present: 1,
      absent: 0,
      myAnswer: 'present',
    },
    {
      id: 2,
      day: 'Sam 14 nov',
      time: '21h – 23h30',
      type: 'Concert',
      place: 'La Cave',
      present: 0,
      absent: 0,
      myAnswer: null,
    },
    {
      id: 3,
      day: 'Ven 20 nov',
      time: '19h – 22h',
      type: 'Répétition',
      place: 'Studio Nord',
      present: 0,
      absent: 0,
      myAnswer: null,
    },
  ],
})

export function evenementsDemo(nomGroupe) {
  return evenementsParNom[nomGroupe?.trim().toLowerCase()] ?? []
}

// Texte court affiché sous le nom du groupe sur l'accueil.
export function prochainEvenement(groupe) {
  const event = groupe.events[0]
  if (!event) return 'Aucun événement'
  const [jour, ...reste] = event.day.split(' ')
  return `${event.type} ${jour.toLowerCase()}. ${reste.join(' ')}`
}