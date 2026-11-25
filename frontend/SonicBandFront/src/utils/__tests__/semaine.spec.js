import { describe, expect, it } from 'vitest'
import {
  couleurHeatmap,
  formatMinutes,
  formatPlage,
  joursDeLaSemaine,
  libelleSemaine,
  lundiDe,
  toIso,
  versMinutes,
} from '../semaine'

describe('semaine', () => {
  it('trouve le lundi de la semaine', () => {
    expect(toIso(lundiDe(new Date(2026, 10, 15)))).toBe('2026-11-09') // dimanche
    expect(toIso(lundiDe(new Date(2026, 10, 9)))).toBe('2026-11-09') // lundi
  })

  it('nomme la semaine comme la maquette', () => {
    expect(libelleSemaine(new Date(2026, 10, 9))).toBe('9 – 15 nov')
    expect(libelleSemaine(new Date(2026, 10, 30))).toBe('30 nov – 6 déc')
  })

  it('liste les 7 jours', () => {
    const jours = joursDeLaSemaine(new Date(2026, 10, 9))
    expect(jours.map((j) => `${j.court} ${j.numero}`)).toEqual([
      'Lun 9',
      'Mar 10',
      'Mer 11',
      'Jeu 12',
      'Ven 13',
      'Sam 14',
      'Dim 15',
    ])
  })

  it('convertit et affiche les heures', () => {
    expect(versMinutes('19:30')).toBe(1170)
    expect(versMinutes('23:59', true)).toBe(1440)
    expect(formatMinutes(1140)).toBe('19h')
    expect(formatPlage(1170, 1350)).toBe('19h30 – 22h30')
    expect(formatPlage(0, 1440)).toBe('Toute la journée')
  })

  it('fonce le bleu avec le nombre de musiciens libres', () => {
    const clair = couleurHeatmap(1, 4).background
    const moyen = couleurHeatmap(2, 4).background
    const fonce = couleurHeatmap(4, 4).background
    expect(fonce).toBe('rgb(45, 98, 200)')
    const bleu = (c) => Number(c.match(/\d+/g)[0])
    expect(bleu(clair)).toBeGreaterThan(bleu(moyen))
    expect(bleu(moyen)).toBeGreaterThan(bleu(fonce))
  })
})
