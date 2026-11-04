// Données de démonstration, en attendant les routes groupes / événements du backend.
// Partagées entre l'accueil (HomeView) et l'aperçu d'un groupe (GroupView).
// reactive() garde les réponses « Je viens » le temps de la session.
import { reactive } from 'vue'

export const groupes = reactive([
  {
    id: 1,
    name: 'Nirvana',
    initial: 'N',
    colorClass: 'bg-blue',
    membersCount: 4,
    events: [
      {
        id: 1,
        day: 'Ven 13 nov',
        time: '19h – 22h',
        type: 'Répétition',
        place: 'Studio Nord',
        present: 2,
        absent: 1,
        myAnswer: 'present',
      },
      {
        id: 2,
        day: 'Sam 14 nov',
        time: '21h – 23h30',
        type: 'Concert',
        place: 'La Cave',
        present: 2,
        absent: 0,
        myAnswer: null,
      },
      {
        id: 3,
        day: 'Ven 20 nov',
        time: '19h – 22h',
        type: 'Répétition',
        place: 'Studio Nord',
        present: 1,
        absent: 1,
        myAnswer: null,
      },
    ],
  },
  {
    id: 2,
    name: 'U2',
    initial: 'U',
    colorClass: 'bg-purple',
    membersCount: 2,
    events: [],
  },
])

// Texte court affiché sous le nom du groupe sur l'accueil.
export function prochainEvenement(groupe) {
  const event = groupe.events[0]
  if (!event) return 'Aucun événement'
  const [jour, ...reste] = event.day.split(' ')
  return `${event.type} ${jour.toLowerCase()}. ${reste.join(' ')}`
}