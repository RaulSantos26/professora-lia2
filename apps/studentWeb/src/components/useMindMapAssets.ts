import { ref, watch, onBeforeUnmount } from 'vue'

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
const maxBytes = 8 * 1024 * 1024
export function useMindMapAssets(studentId: () => string | undefined, spec: () => Record<string, unknown>) {
  const images = ref<Record<string, string>>({})
  const states = ref<Record<string, string>>({})
  let epoch = 0, disposed = false
  let timer: ReturnType<typeof setTimeout> | undefined
  const controllers = new Set<AbortController>()
  function stop() {
    epoch++; clearTimeout(timer); controllers.forEach(c => c.abort()); controllers.clear()
  }
  async function request(url: string, binary: boolean) {
    const controller = new AbortController(); controllers.add(controller)
    const timeout = setTimeout(() => controller.abort(), 15000)
    try {
      const response = await fetch(url, { method: 'GET', credentials: 'same-origin', signal: controller.signal, redirect: 'error' })
      if (!response.ok) throw new Error('HTTP')
      if (!binary) return await response.json()
      const mime = (response.headers.get('content-type') || '').split(';')[0].trim().toLowerCase()
      if (!['image/png', 'image/jpeg'].includes(mime) || Number(response.headers.get('content-length') || 0) > maxBytes) throw new Error('INVALID_ASSET')
      if (!response.body) throw new Error('EMPTY_ASSET')
      const reader = response.body.getReader(); const chunks: Uint8Array[] = []; let size = 0
      try {
        while (true) {
          const chunk = await reader.read(); if (chunk.done) break
          size += chunk.value.byteLength
          if (size > maxBytes) { await reader.cancel(); throw new Error('ASSET_TOO_LARGE') }
          chunks.push(chunk.value)
        }
      } finally { reader.releaseLock() }
      const bytes = new Uint8Array(size); let offset = 0
      for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length }
      const png = [137, 80, 78, 71, 13, 10, 26, 10].every((v, i) => bytes[i] === v)
      const jpeg = bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255
      if (!(mime === 'image/png' ? png : jpeg)) throw new Error('INVALID_SIGNATURE')
      let encoded = ''
      for (let i = 0; i < bytes.length; i += 8192) encoded += String.fromCharCode(...bytes.subarray(i, i + 8192))
      return `data:${mime};base64,${btoa(encoded)}`
    } finally { clearTimeout(timeout); controllers.delete(controller) }
  }
  async function refresh() {
    stop(); images.value = {}; states.value = {}
    if (disposed) return
    const current = epoch, student = studentId()
    if (!student || !uuid.test(student)) return
    const source = spec().nodes
    const entries: { node: string; id: string }[] = []
    for (const item of Array.isArray(source) ? source : []) {
      if (!item || typeof item !== 'object') continue
      const node = String(item.nodeId ?? ''), id = String(item.imageTaskId ?? '')
      if (!node || !uuid.test(id) || entries.some(e => e.node === node)) continue
      if (entries.length >= 8) { states.value[node] = 'LIMIT'; continue }
      entries.push({ node, id }); states.value[node] = 'QUEUED'
    }
    const failures = new Map<string, number>()
    const active = () => !disposed && current === epoch
    async function poll() {
      for (const entry of entries) {
        if (!active()) return
        if (['READY', 'ERROR', 'CANCELLED'].includes(states.value[entry.node])) continue
        try {
          const path = `/api/students/${student}/image-tasks/${entry.id}`
          const task = await request(path, false)
          if (!active()) return
          if (task.imageTaskId !== entry.id || task.studentId !== student) throw new Error('ASSET_SCOPE')
          const status = String(task.status)
          if (!['QUEUED', 'PREPARING', 'GENERATING', 'LABELING', 'READY', 'ERROR', 'CANCELLED'].includes(status)) throw new Error('ASSET_STATUS')
          if (status === 'READY') {
            const data = await request(path + '/asset', true)
            if (!active()) return
            images.value[entry.node] = data
          }
          states.value[entry.node] = status
          failures.delete(entry.node)
        } catch (error) {
          if (!active()) return
          if (/^(INVALID_|EMPTY_|ASSET_)/.test(error instanceof Error ? error.message : '')) {
            states.value[entry.node] = 'ERROR'; continue
          }
          const count = (failures.get(entry.node) || 0) + 1; failures.set(entry.node, count)
          states.value[entry.node] = count >= 3 ? 'ERROR' : 'RETRYING'
        }
      }
      if (active() && entries.some(e => !['READY', 'ERROR', 'CANCELLED'].includes(states.value[e.node]))) timer = setTimeout(() => { void poll() }, 2500)
    }
    await poll()
  }
  watch(() => JSON.stringify([studentId(), spec()]), () => { void refresh() }, { immediate: true })
  onBeforeUnmount(() => { disposed = true; stop() })
  return { images, states, refresh }
}
