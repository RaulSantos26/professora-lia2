export interface ReadingStep { title: string; where: string; explanation: string; x: number | null; y: number | null }
export interface ReadingGuide { introduction: string; steps: ReadingStep[]; takeaway: string; caveat: string }
export const guidePrefix = 'LIA_IMAGE_GUIDE_V1:'
export function readImageGuide(labels: string[]): ReadingGuide | null {
  try {
    const raw = labels.find(s => s.startsWith(guidePrefix))
    if (!raw || raw.length > 14000) return null
    const data = JSON.parse(raw.slice(guidePrefix.length))
    if (!Array.isArray(data.steps) || !data.steps.length || data.steps.length > 5) return null
    if (![data.introduction, data.takeaway, data.caveat ?? ''].every(s => typeof s === 'string')) return null
    const steps = data.steps.map((s: any) => {
      if (![s.title, s.where, s.explanation].every(t => typeof t === 'string' && t.length <= 500)) throw Error('Invalid step')
      const valid = Number.isFinite(s.x) && Number.isFinite(s.y) && s.x >= 3 && s.x <= 97 && s.y >= 3 && s.y <= 97 && s.confidence >= .85
      return { title: s.title, where: s.where, explanation: s.explanation, x: valid ? s.x : null, y: valid ? s.y : null }
    })
    return { introduction: data.introduction, steps, takeaway: data.takeaway, caveat: data.caveat || '' }
  } catch { return null }
}
