<script setup lang="ts">
import {
  onBeforeUnmount,
  onMounted,
  ref,
  watch
} from 'vue'
import * as THREE from 'three'
import {
  OrbitControls
} from 'three/addons/controls/OrbitControls.js'

const props = defineProps<{
  spec: Record<string, unknown>
}>()

interface SceneObject {
  objectId: string
  label: string
  primitive: 'SPHERE' | 'BOX' | 'CYLINDER'
  position: {
    x: number
    y: number
    z: number
  }
  scale: {
    x: number
    y: number
    z: number
  }
  orbit: {
    radius: number
    speed: number
    centerObjectId: string | null
  } | null
  rotationSpeed: number
}

const host = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let frameId = 0
let startedAt = performance.now()
const meshes = new Map<string, THREE.Mesh>()

function createGeometry(
  primitive: SceneObject['primitive']
): THREE.BufferGeometry {
  if (primitive === 'BOX') {
    return new THREE.BoxGeometry(1, 1, 1)
  }

  if (primitive === 'CYLINDER') {
    return new THREE.CylinderGeometry(
      0.5,
      0.5,
      1,
      32
    )
  }

  return new THREE.SphereGeometry(
    0.5,
    32,
    24
  )
}

function rebuild() {
  if (!scene) {
    return
  }

  for (const mesh of meshes.values()) {
    scene.remove(mesh)
    mesh.geometry.dispose()
    ;(mesh.material as THREE.Material).dispose()
  }

  meshes.clear()

  const objects = Array.isArray(props.spec.objects)
    ? props.spec.objects as SceneObject[]
    : []

  objects.forEach((item, index) => {
    const color = new THREE.Color()
    color.setHSL(
      (index * 0.17) % 1,
      0.55,
      0.55
    )

    const material = new THREE.MeshStandardMaterial({
      roughness: 0.65,
      metalness: 0.05,
      color
    })

    const mesh = new THREE.Mesh(
      createGeometry(item.primitive),
      material
    )

    mesh.position.set(
      item.position.x,
      item.position.y,
      item.position.z
    )
    mesh.scale.set(
      item.scale.x,
      item.scale.y,
      item.scale.z
    )

    scene?.add(mesh)
    meshes.set(item.objectId, mesh)
  })

  startedAt = performance.now()
}

function animate(time: number) {
  if (
    !renderer
    || !scene
    || !camera
  ) {
    return
  }

  const elapsed = (time - startedAt) / 1000
  const objects = Array.isArray(props.spec.objects)
    ? props.spec.objects as SceneObject[]
    : []

  for (const item of objects) {
    const mesh = meshes.get(item.objectId)

    if (!mesh) {
      continue
    }

    mesh.rotation.y += item.rotationSpeed * 0.01

    if (item.orbit) {
      const centerMesh = item.orbit.centerObjectId
        ? meshes.get(item.orbit.centerObjectId)
        : null

      const center = centerMesh?.position
        ?? new THREE.Vector3(0, 0, 0)

      mesh.position.x = (
        center.x
        + Math.cos(
          elapsed * item.orbit.speed
        ) * item.orbit.radius
      )

      mesh.position.z = (
        center.z
        + Math.sin(
          elapsed * item.orbit.speed
        ) * item.orbit.radius
      )
    }
  }

  controls?.update()
  renderer.render(scene, camera)
  frameId = requestAnimationFrame(animate)
}

function resize() {
  if (
    !host.value
    || !renderer
    || !camera
  ) {
    return
  }

  const width = Math.max(
    320,
    host.value.clientWidth
  )
  const height = Math.min(
    620,
    Math.max(360, width * 0.58)
  )

  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

let observer: ResizeObserver | null = null

onMounted(() => {
  if (!host.value) {
    return
  }

  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(
    50,
    1,
    0.1,
    1000
  )
  camera.position.set(0, 4, 10)

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
  })
  renderer.setPixelRatio(
    Math.min(window.devicePixelRatio || 1, 2)
  )

  host.value.appendChild(renderer.domElement)

  controls = new OrbitControls(
    camera,
    renderer.domElement
  )
  controls.enableDamping = true
  controls.enablePan = true

  scene.add(new THREE.AmbientLight(0xffffff, 1.8))

  const directional = new THREE.DirectionalLight(
    0xffffff,
    2.4
  )
  directional.position.set(4, 8, 5)
  scene.add(directional)

  const grid = new THREE.GridHelper(
    20,
    20
  )
  scene.add(grid)

  rebuild()
  resize()

  observer = new ResizeObserver(resize)
  observer.observe(host.value)

  frameId = requestAnimationFrame(animate)
})

watch(() => props.spec, rebuild, { deep: true })

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  observer?.disconnect()
  controls?.dispose()

  if (renderer) {
    renderer.dispose()
    renderer.domElement.remove()
  }

  renderer = null
  scene = null
  camera = null
  controls = null
})
</script>

<template>
  <section class="threeVisual">
    <div
      ref="host"
      class="threeVisualHost"
      aria-label="Cena educacional 3D interativa"
    />
    <small>
      Arraste para girar · pinça/roda para aproximar
    </small>
  </section>
</template>
