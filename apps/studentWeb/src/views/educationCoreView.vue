<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import AcademicStageCreateForm from '../components/academicStageCreateForm.vue'
import AcademicStageList from '../components/academicStageList.vue'
import EducationWorkspaceContextBar from '../components/educationWorkspaceContextBar.vue'
import EducationWorkspaceNavigation from '../components/educationWorkspaceNavigation.vue'
import LearningContextCreateForm from '../components/learningContextCreateForm.vue'
import LearningGoalPanel from '../components/learningGoalPanel.vue'
import LearningProgressPanel from '../components/learningProgressPanel.vue'
import LearningGuidePanel from '../components/learningGuidePanel.vue'
import LiaTutorPanel from '../components/liaTutorPanel.vue'
import MaterialWorkspacePanel from '../components/materialWorkspacePanel.vue'
import MobileStudentNavigation from '../components/mobileStudentNavigation.vue'
import PedagogicalWorkspacePanel from '../components/pedagogicalWorkspacePanel.vue'
import StudentCreateForm from '../components/studentCreateForm.vue'
import StudentLearningContextPanel from '../components/studentLearningContextPanel.vue'
import StudentLearningUnitPanel from '../components/studentLearningUnitPanel.vue'
import StudentList from '../components/studentList.vue'
import StudentSubjectPanel from '../components/studentSubjectPanel.vue'
import StudyScopePanel from '../components/studyScopePanel.vue'
import StudySessionPanel from '../components/studySessionPanel.vue'
import type {
  AcademicStageContract,
  AcademicStageCreateContract
} from '../contracts/academicStageContract'
import type {
  LearningContextContract,
  LearningContextCreateContract
} from '../contracts/learningContextContract'
import type {
  LearningGoalContract,
  LearningGoalCreateContract
} from '../contracts/learningGoalContract'
import type {
  LearningStateStatus,
  StudentLearningStateViewContract
} from '../contracts/studentLearningStateContract'
import type { LearningGuideContract } from '../contracts/learningGuideContract'
import type { AiModelRegistryContract } from '../contracts/aiModelContract'
import type { WorkspaceSummaryContract } from '../contracts/workspaceSummaryContract'
import type {
  StudentContract,
  StudentCreateContract
} from '../contracts/studentContract'
import type {
  StudentLearningContextViewContract
} from '../contracts/studentLearningContextContract'
import type {
  StudentLearningUnitContract,
  StudentLearningUnitCreateContract
} from '../contracts/studentLearningUnitContract'
import type {
  StudentSubjectContract,
  StudentSubjectCreateContract
} from '../contracts/studentSubjectContract'
import type {
  StudyScopeContract,
  StudyScopeCreateContract
} from '../contracts/studyScopeContract'
import type {
  StudyScopeCandidateContract
} from '../contracts/studyScopeItemContract'
import type {
  StudySessionType,
  StudySessionViewContract
} from '../contracts/studySessionContract'
import type {
  EducationWorkspaceSection
} from '../types/educationWorkspaceSection'
import { AiModelApiService } from '../services/aiModelApiService'
import { LearningContextApiService } from '../services/learningContextApiService'
import { LearningGuideApiService } from '../services/learningGuideApiService'
import { LiaApiError } from '../services/materialApiService'
import { LearningWorkspaceApiService } from '../services/learningWorkspaceApiService'
import { StudentApiService } from '../services/studentApiService'
import { StudentContentApiService } from '../services/studentContentApiService'
import { useMaterialWorkspace } from '../composables/useMaterialWorkspace'
import { useAgentTutorWorkspace } from '../composables/useAgentTutorWorkspace'
import { usePedagogicalWorkspace } from '../composables/usePedagogicalWorkspace'
import { WorkspaceSummaryApiService } from '../services/workspaceSummaryApiService'
const studentApiService = new StudentApiService()
const learningContextApiService = new LearningContextApiService()
const studentContentApiService = new StudentContentApiService()
const workspaceApiService = new LearningWorkspaceApiService()
const guideApiService = new LearningGuideApiService()
const aiModelApiService = new AiModelApiService()
const workspaceSummaryApiService = new WorkspaceSummaryApiService()
const activeSection = ref<EducationWorkspaceSection>('STUDENT')
const students = ref<StudentContract[]>([])
const selectedStudent = ref<StudentContract | null>(null)
const academicStages = ref<AcademicStageContract[]>([])
const learningContexts = ref<LearningContextContract[]>([])
const assignedContexts = ref<StudentLearningContextViewContract[]>([])
const selectedStudentLearningContextId = ref<string | null>(null)
const studentSubjects = ref<StudentSubjectContract[]>([])
const selectedStudentSubject = ref<StudentSubjectContract | null>(null)
const studentLearningUnits = ref<StudentLearningUnitContract[]>([])
const learningGoals = ref<LearningGoalContract[]>([])
const selectedLearningGoal = ref<LearningGoalContract | null>(null)
const studyScopes = ref<StudyScopeContract[]>([])
const selectedStudyScope = ref<StudyScopeContract | null>(null)
const scopeCandidates = ref<StudyScopeCandidateContract[]>([])
const studySessions = ref<StudySessionViewContract[]>([])
const learningStates = ref<StudentLearningStateViewContract[]>([])
const learningGuide = ref<LearningGuideContract | null>(null)
const aiModelRegistry = ref<AiModelRegistryContract | null>(null)
const workspaceSummary = ref<WorkspaceSummaryContract | null>(null)
const errorMessage = ref('')
const successMessage = ref('')
const busy = ref(false)
const currentAcademicStage = computed(
  () => academicStages.value.find(stage => stage.status === 'CURRENT') ?? null
)
const selectedStudentLabel = computed(
  () => selectedStudent.value
    ? selectedStudent.value.preferredName || selectedStudent.value.fullName
    : 'Nenhum selecionado'
)
const selectedAcademicStageLabel = computed(
  () => currentAcademicStage.value?.stageLabel ?? 'Nenhuma atual'
)
const selectedStudentContext = computed(
  () => assignedContexts.value.find(
    item =>
      item.association.studentLearningContextId
      === selectedStudentLearningContextId.value
  ) ?? null
)
const selectedContextLabel = computed(
  () => selectedStudentContext.value?.context.name ?? 'Nenhum selecionado'
)
const selectedSubjectLabel = computed(
  () => selectedStudentSubject.value?.name ?? 'Nenhuma selecionada'
)
async function refreshWorkspaceSummary() {
  if (!selectedStudent.value) {
    workspaceSummary.value = null
    return
  }
  workspaceSummary.value =
    await workspaceSummaryApiService.getSummary(
      selectedStudent.value.studentId
    )
}
async function refreshAiModels(forceRefresh = false) {
  aiModelRegistry.value =
    await aiModelApiService.listModels(forceRefresh)
}
async function refreshGuide() {
  if (!selectedStudent.value) {
    learningGuide.value = null
    return
  }
  learningGuide.value = await guideApiService.getGuide(
    selectedStudent.value.studentId
  )
}
async function loadCatalogs() {
  const [studentItems, contextItems] = await Promise.all([
    studentApiService.listStudents(),
    learningContextApiService.listLearningContexts()
  ])
  students.value = studentItems
  learningContexts.value = contextItems
}
async function refreshLearningStates() {
  if (!selectedStudent.value) {
    learningStates.value = []
    return
  }
  learningStates.value = await workspaceApiService.listLearningStates(
    selectedStudent.value.studentId
  )
}
async function refreshGoals() {
  if (!selectedStudent.value) {
    learningGoals.value = []
    return
  }
  learningGoals.value = await workspaceApiService.listGoals(
    selectedStudent.value.studentId
  )
}
async function createStudent(payload: StudentCreateContract) {
  try {
    const created = await studentApiService.createStudent(payload)
    successMessage.value =
      `Aluno ${created.preferredName || created.fullName} cadastrado.`
    await loadCatalogs()
    await selectStudent(created)
    activeSection.value = 'ACADEMIC_STAGE'
  } catch (error) {
    showError(error)
  }
}
async function selectStudent(student: StudentContract) {
  selectedStudent.value = student
  selectedStudentLearningContextId.value = null
  studentSubjects.value = []
  selectedStudentSubject.value = null
  studentLearningUnits.value = []
  selectedLearningGoal.value = null
  studyScopes.value = []
  selectedStudyScope.value = null
  scopeCandidates.value = []
  studySessions.value = []
  resetMaterialWorkspace()
  resetPedagogicalWorkspace()
  resetAgentTutorWorkspace()
  workspaceSummary.value = null
  successMessage.value = ''
  try {
    const [
      stages,
      contexts,
      goals,
      states,
      guide,
      summary
    ] = await Promise.all([
      studentApiService.listAcademicStages(student.studentId),
      learningContextApiService.listStudentLearningContexts(student.studentId),
      workspaceApiService.listGoals(student.studentId),
      workspaceApiService.listLearningStates(student.studentId),
      guideApiService.getGuide(student.studentId),
      workspaceSummaryApiService.getSummary(student.studentId)
    ])
    academicStages.value = stages
    assignedContexts.value = contexts
    learningGoals.value = goals
    learningStates.value = states
    learningGuide.value = guide
    workspaceSummary.value = summary
    await refreshMaterials()
    await refreshProcessingJobs()
    await refreshPedagogicalArtifacts()
    if (contexts.length > 0) {
      await selectStudentLearningContext(
        contexts[0].association.studentLearningContextId
      )
    }
    errorMessage.value = ''
  } catch (error) {
    showError(error)
  }
}
async function createAcademicStage(payload: AcademicStageCreateContract) {
  if (!selectedStudent.value) return
  try {
    await studentApiService.createAcademicStage(
      selectedStudent.value.studentId,
      payload
    )
    academicStages.value = await studentApiService.listAcademicStages(
      selectedStudent.value.studentId
    )
    successMessage.value = 'Etapa acadêmica registrada.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function createLearningContext(payload: LearningContextCreateContract) {
  try {
    const created =
      await learningContextApiService.createLearningContext(payload)
    learningContexts.value =
      await learningContextApiService.listLearningContexts()
    successMessage.value = `Contexto ${created.name} criado.`
  } catch (error) {
    showError(error)
  }
}
async function assignLearningContext(
  learningContextId: string,
  academicStageId: string | null
) {
  if (!selectedStudent.value) return
  busy.value = true
  try {
    const created = await learningContextApiService.assignLearningContext(
      selectedStudent.value.studentId,
      learningContextId,
      academicStageId
    )
    assignedContexts.value =
      await learningContextApiService.listStudentLearningContexts(
        selectedStudent.value.studentId
      )
    await selectStudentLearningContext(
      created.association.studentLearningContextId
    )
    successMessage.value = 'Contexto vinculado ao aluno.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  } finally {
    busy.value = false
  }
}
async function selectStudentLearningContext(
  studentLearningContextId: string
) {
  selectedStudentLearningContextId.value = studentLearningContextId
  selectedStudentSubject.value = null
  studentLearningUnits.value = []
  try {
    studentSubjects.value =
      await studentContentApiService.listSubjects(studentLearningContextId)
  } catch (error) {
    showError(error)
  }
}
async function createStudentSubject(
  payload: StudentSubjectCreateContract
) {
  if (!selectedStudentLearningContextId.value) return
  try {
    const created = await studentContentApiService.createSubject(
      selectedStudentLearningContextId.value,
      payload
    )
    studentSubjects.value =
      await studentContentApiService.listSubjects(
        selectedStudentLearningContextId.value
      )
    await selectStudentSubject(created)
    await refreshLearningStates()
    successMessage.value =
      `Matéria ${created.name} criada para este aluno/contexto.`
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function selectStudentSubject(subject: StudentSubjectContract) {
  selectedStudentSubject.value = subject
  try {
    studentLearningUnits.value =
      await studentContentApiService.listLearningUnits(
        subject.studentSubjectId
      )
    activeSection.value = 'LEARNING_UNIT'
  } catch (error) {
    showError(error)
  }
}
async function createStudentLearningUnit(
  payload: StudentLearningUnitCreateContract
) {
  if (!selectedStudentSubject.value) return
  try {
    await studentContentApiService.createLearningUnit(
      selectedStudentSubject.value.studentSubjectId,
      payload
    )
    studentLearningUnits.value =
      await studentContentApiService.listLearningUnits(
        selectedStudentSubject.value.studentSubjectId
      )
    await refreshLearningStates()
    successMessage.value =
      'Unidade criada exclusivamente para este aluno/contexto.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function createLearningGoal(payload: LearningGoalCreateContract) {
  if (!selectedStudent.value) return
  try {
    const created = await workspaceApiService.createGoal(
      selectedStudent.value.studentId,
      payload
    )
    await refreshGoals()
    await selectLearningGoal(created)
    successMessage.value = `Objetivo ${created.title} criado.`
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function selectLearningGoal(goal: LearningGoalContract) {
  selectedLearningGoal.value = goal
  selectedStudyScope.value = null
  scopeCandidates.value = []
  studySessions.value = []
  try {
    studyScopes.value =
      await workspaceApiService.listScopes(goal.learningGoalId)
    activeSection.value = 'STUDY_SCOPE'
  } catch (error) {
    showError(error)
  }
}
async function createStudyScope(payload: StudyScopeCreateContract) {
  if (!selectedLearningGoal.value) return
  try {
    const created = await workspaceApiService.createScope(
      selectedLearningGoal.value.learningGoalId,
      payload
    )
    studyScopes.value = await workspaceApiService.listScopes(
      selectedLearningGoal.value.learningGoalId
    )
    await selectStudyScope(created)
    successMessage.value = `Escopo ${created.name} criado.`
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function refreshScopeCandidates() {
  if (!selectedLearningGoal.value || !selectedStudyScope.value) {
    scopeCandidates.value = []
    return
  }
  scopeCandidates.value = await workspaceApiService.listCandidates(
    selectedLearningGoal.value.learningGoalId,
    selectedStudyScope.value.studyScopeId
  )
}
async function selectStudyScope(scope: StudyScopeContract) {
  selectedStudyScope.value = scope
  try {
    await refreshScopeCandidates()
    studySessions.value = await workspaceApiService.listSessions(
      scope.studyScopeId
    )
  } catch (error) {
    showError(error)
  }
}
async function addScopeUnit(unitId: string) {
  if (!selectedStudyScope.value) return
  try {
    await workspaceApiService.addScopeItem(
      selectedStudyScope.value.studyScopeId,
      unitId
    )
    await refreshScopeCandidates()
    successMessage.value = 'Unidade adicionada ao escopo.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function removeScopeUnit(itemId: string) {
  if (!selectedStudyScope.value) return
  try {
    await workspaceApiService.removeScopeItem(
      selectedStudyScope.value.studyScopeId,
      itemId
    )
    await refreshScopeCandidates()
    successMessage.value = 'Unidade removida do escopo.'
  } catch (error) {
    showError(error)
  }
}
async function startStudySession(sessionType: StudySessionType) {
  if (!selectedStudyScope.value) return
  try {
    await workspaceApiService.startSession(
      selectedStudyScope.value.studyScopeId,
      sessionType
    )
    studySessions.value = await workspaceApiService.listSessions(
      selectedStudyScope.value.studyScopeId
    )
    activeSection.value = 'STUDY_SESSION'
    successMessage.value = 'Sessão de estudo iniciada.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function completeStudySession(sessionId: string) {
  if (!selectedStudyScope.value) return
  try {
    await workspaceApiService.completeSession(sessionId)
    studySessions.value = await workspaceApiService.listSessions(
      selectedStudyScope.value.studyScopeId
    )
    await refreshLearningStates()
    successMessage.value =
      'Sessão concluída e progresso atualizado.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
async function updateLearningState(
  unitId: string,
  status: LearningStateStatus,
  mastery: number,
  confidence: number
) {
  if (!selectedStudent.value) return
  try {
    await workspaceApiService.updateLearningState(
      selectedStudent.value.studentId,
      unitId,
      status,
      mastery,
      confidence
    )
    await refreshLearningStates()
    successMessage.value =
      'Estado de aprendizagem atualizado.'
    await refreshGuide()
    await refreshWorkspaceSummary()
  } catch (error) {
    showError(error)
  }
}
function showError(error: unknown) {
  if (error instanceof LiaApiError) {
    errorMessage.value =
      `${error.message}\nCódigo: ${error.code}`
      + (
        error.correlationId
          ? `\nCorrelação: ${error.correlationId}`
          : ''
      )
    return
  }
  errorMessage.value =
    error instanceof Error
      ? error.message
      : 'Erro não identificado.'
}
const {
  materials,
  selectedMaterial,
  selectedMaterialStructure,
  materialSubjects,
  materialUnits,
  materialBusy,
  materialFormVersion,
  uploadProgress,
  processingJobs,
  ragResponse,
  ragBusy,
  refreshMaterials,
  refreshProcessingJobs,
  resetMaterialWorkspace,
  selectMaterialContext,
  selectMaterialSubject,
  uploadMaterials,
  selectMaterial,
  analyzeMaterial,
  indexMaterialRag,
  updateMaterialAiPreference,
  toggleMaterialStudy,
  deleteMaterial,
  queryRag,
  isMaterialProcessing
} = useMaterialWorkspace({
  selectedStudent,
  refreshGuide,
  refreshWorkspaceSummary,
  showError,
  setSuccess: message => {
    successMessage.value = message
  },
  setError: message => {
    errorMessage.value = message
  }
})
const {
  artifacts: pedagogicalArtifacts,
  selectedArtifact: selectedPedagogicalArtifact,
  latestAttempt,
  busy: pedagogicalBusy,
  refreshArtifacts: refreshPedagogicalArtifacts,
  createArtifact: createPedagogicalArtifact,
  selectArtifact: selectPedagogicalArtifact,
  submitAttempt: submitPedagogicalAttempt,
  archiveArtifact: archivePedagogicalArtifact,
  resetPedagogicalWorkspace
} = usePedagogicalWorkspace({
  selectedStudent,
  showError,
  refreshLearningStates,
  refreshGuide,
  refreshWorkspaceSummary,
  setSuccess: message => {
    successMessage.value = message
  }
})
const tutorUnitId = computed(
  () => selectedMaterial.value?.studentLearningUnitId ?? null
)
const tutorUnitLabel = computed(() => {
  const unitId = tutorUnitId.value
  if (!unitId) {
    return 'Geral'
  }
  const unit = [
    ...studentLearningUnits.value,
    ...materialUnits.value
  ].find(
    item => item.studentLearningUnitId === unitId
  )
  return unit?.title ?? 'Unidade selecionada'
})
const tutorContext = computed(
  () => ({
    contextId: (
      selectedMaterial.value?.studentLearningContextId
      ?? selectedStudentLearningContextId.value
    ),
    subjectId: (
      selectedMaterial.value?.studentSubjectId
      ?? selectedStudentSubject.value?.studentSubjectId
      ?? null
    ),
    unitId: tutorUnitId.value,
    title: [
      'Lia',
      selectedSubjectLabel.value !== 'Nenhuma selecionada'
        ? selectedSubjectLabel.value
        : null,
      tutorUnitLabel.value !== 'Geral'
        ? tutorUnitLabel.value
        : null
    ].filter(Boolean).join(' · ')
  })
)
const tutorContextKey = computed(
  () => JSON.stringify(tutorContext.value)
)
const {
  threads: tutorThreads,
  conversation: tutorConversation,
  visualTasks: tutorVisualTasks,
  busy: tutorBusy,
  ensureContextThread,
  selectThread: selectTutorThread,
  sendMessage: sendTutorMessage,
  archiveCurrentThread: archiveTutorThread,
  reset: resetAgentTutorWorkspace
} = useAgentTutorWorkspace({
  selectedStudent,
  showError,
  refreshGuide,
  refreshWorkspaceSummary,
  setSuccess: message => {
    successMessage.value = message
  }
})
watch(
  [activeSection, tutorContextKey],
  async ([section]) => {
    if (
      section !== 'LIA_TUTOR'
      || !selectedStudent.value
    ) {
      return
    }
    try {
      await ensureContextThread(
        tutorContext.value
      )
      await refreshWorkspaceSummary()
      await refreshGuide()
    } catch (error) {
      showError(error)
    }
  }
)
async function openPedagogicalFromTutor(
  artifactId: string
) {
  await refreshPedagogicalArtifacts()
  const artifact = pedagogicalArtifacts.value.find(
    item =>
      item.pedagogicalArtifactId === artifactId
  )
  if (artifact) {
    selectPedagogicalArtifact(artifact)
  }
  activeSection.value = 'PEDAGOGICAL'
}
onMounted(async () => {
  try {
    await Promise.all([
      loadCatalogs(),
      refreshAiModels()
    ])
  } catch (error) {
    showError(error)
  }
})
</script>
<template>
  <main class="educationShell workspaceShell">
    <header class="pageHeader workspacePageHeader">
      <div>
        <p class="eyebrow">PROFESSORA LIA 2.0</p>
        <h1>Lia Learning Studio</h1>
        <p>
          Tutora agentiva, materiais multimodais, aprendizagem adaptativa e recursos visuais interativos.
        </p>
      </div>
      <span class="releaseBadge">009</span>
    </header>
    <EducationWorkspaceContextBar
      :student="selectedStudentLabel"
      :academic-stage="selectedAcademicStageLabel"
      :learning-context="selectedContextLabel"
      :subject="selectedSubjectLabel"
    />
    <LearningGuidePanel
      v-if="selectedStudent && learningGuide"
      :guide="learningGuide"
      @navigate="activeSection = $event"
    />
    <p v-if="errorMessage" class="messageCard errorCard">
      {{ errorMessage }}
    </p>
    <p v-if="successMessage" class="messageCard successCard">
      {{ successMessage }}
    </p>
    <EducationWorkspaceNavigation
      :active-section="activeSection"
      :recommended-section="learningGuide?.recommendedSection ?? null"
      :student-summary="selectedStudentLabel"
      :student-count="students.length"
      :academic-stage-summary="selectedAcademicStageLabel"
      :academic-stage-count="workspaceSummary?.academicStageCount ?? academicStages.length"
      :learning-context-summary="
        selectedStudent
          ? `${assignedContexts.length} ativo(s)`
          : 'Selecione um aluno'
      "
      :learning-context-count="workspaceSummary?.learningContextCount ?? assignedContexts.length"
      :subject-summary="selectedContextLabel"
      :subject-count="workspaceSummary?.subjectCount ?? studentSubjects.length"
      :learning-unit-summary="selectedSubjectLabel"
      :learning-unit-count="workspaceSummary?.learningUnitCount ?? studentLearningUnits.length"
      :material-summary="
        selectedMaterial?.title
          ?? (materials.length > 0 ? `${materials.length} material(is)` : 'Nenhum material')
      "
      :material-count="workspaceSummary?.materialCount ?? materials.length"
      :pedagogical-summary="
        selectedPedagogicalArtifact?.title
          ?? (
            pedagogicalArtifacts.length > 0
              ? `${pedagogicalArtifacts.length} criado(s)`
              : 'Comece a estudar'
          )
      "
      :pedagogical-count="workspaceSummary?.pedagogicalArtifactCount ?? pedagogicalArtifacts.length"
      :lia-tutor-summary="
        tutorConversation?.thread.title
          ?? (
            tutorThreads.length > 0
              ? `${tutorThreads.length} conversa(s)`
              : 'Converse com a Lia'
          )
      "
      :lia-tutor-count="workspaceSummary?.agentThreadCount ?? tutorThreads.length"
      :learning-goal-summary="
        selectedLearningGoal?.title ?? 'Nenhum selecionado'
      "
      :learning-goal-count="workspaceSummary?.learningGoalCount ?? learningGoals.length"
      :study-scope-summary="
        selectedStudyScope?.name ?? 'Nenhum selecionado'
      "
      :study-scope-count="workspaceSummary?.studyScopeCount ?? studyScopes.length"
      :study-session-summary="
        studySessions.some(item => item.session.status === 'IN_PROGRESS')
          ? 'Em andamento'
          : 'Nenhuma em andamento'
      "
      :study-session-count="workspaceSummary?.studySessionCount ?? studySessions.length"
      :learning-progress-summary="
        selectedStudent
          ? `${learningStates.length} unidade(s)`
          : 'Selecione um aluno'
      "
      :learning-progress-count="workspaceSummary?.learningProgressCount ?? learningStates.length"
      @select="activeSection = $event"
    />
    <section class="workspacePanel">
      <div
        v-if="activeSection === 'STUDENT'"
        class="workspacePanelGrid"
      >
        <StudentCreateForm @create="createStudent" />
        <StudentList
          :students="students"
          :selected-student-id="selectedStudent?.studentId ?? null"
          @select="selectStudent"
        />
      </div>
      <div v-else-if="activeSection === 'ACADEMIC_STAGE'">
        <template v-if="selectedStudent">
          <div class="workspacePanelGrid">
            <section class="selectedStudentCard">
              <p class="eyebrow">ALUNO SELECIONADO</p>
              <h2>
                {{ selectedStudent.preferredName || selectedStudent.fullName }}
              </h2>
              <p>{{ selectedStudent.fullName }}</p>
            </section>
            <AcademicStageList :stages="academicStages" />
          </div>
          <div class="workspacePanelSection">
            <AcademicStageCreateForm
              @create="createAcademicStage"
            />
          </div>
        </template>
        <section v-else class="workspaceEmptyState">
          <h2>Selecione um aluno</h2>
        </section>
      </div>
      <div
        v-else-if="activeSection === 'LEARNING_CONTEXT'"
        class="workspacePanelGrid"
      >
        <LearningContextCreateForm
          @create="createLearningContext"
        />
        <StudentLearningContextPanel
          v-if="selectedStudent"
          :available-contexts="learningContexts"
          :assigned-contexts="assignedContexts"
          :current-academic-stage="currentAcademicStage"
          :busy="busy"
          @assign="assignLearningContext"
        />
      </div>
      <StudentSubjectPanel
        v-else-if="
          activeSection === 'SUBJECT'
          && selectedStudent
        "
        :contexts="assignedContexts"
        :selected-context-id="selectedStudentLearningContextId"
        :subjects="studentSubjects"
        :selected-subject-id="
          selectedStudentSubject?.studentSubjectId ?? null
        "
        @select-context="selectStudentLearningContext"
        @create="createStudentSubject"
        @select-subject="selectStudentSubject"
      />
      <StudentLearningUnitPanel
        v-else-if="activeSection === 'LEARNING_UNIT'"
        :subject="selectedStudentSubject"
        :units="studentLearningUnits"
        @create="createStudentLearningUnit"
      />
      <MaterialWorkspacePanel
        v-else-if="
          activeSection === 'MATERIAL'
          && selectedStudent
        "
        :key="materialFormVersion"
        :contexts="assignedContexts"
        :subjects="materialSubjects"
        :units="materialUnits"
        :materials="materials"
        :selected-material="selectedMaterial"
        :structure="selectedMaterialStructure"
        :model-registry="aiModelRegistry"
        :busy="materialBusy"
        :upload-progress="uploadProgress"
        :processing-jobs="processingJobs"
        :rag-response="ragResponse"
        :rag-busy="ragBusy"
        :is-material-processing="isMaterialProcessing"
        @select-context="selectMaterialContext"
        @select-subject="selectMaterialSubject"
        @upload-batch="uploadMaterials"
        @select-material="selectMaterial"
        @analyze="analyzeMaterial"
        @index-rag="indexMaterialRag"
        @update-ai-preference="updateMaterialAiPreference"
        @toggle-study="toggleMaterialStudy"
        @delete="deleteMaterial"
        @refresh-models="refreshAiModels(true)"
        @query-rag="queryRag"
      />
      <PedagogicalWorkspacePanel
        v-else-if="
          activeSection === 'PEDAGOGICAL'
          && selectedStudent
        "
        :materials="materials"
        :selected-material="selectedMaterial"
        :model-registry="aiModelRegistry"
        :artifacts="pedagogicalArtifacts"
        :selected-artifact="selectedPedagogicalArtifact"
        :attempt="latestAttempt"
        :busy="pedagogicalBusy"
        @create="createPedagogicalArtifact"
        @select="selectPedagogicalArtifact"
        @archive="archivePedagogicalArtifact"
        @submit-attempt="submitPedagogicalAttempt"
      />
      <LiaTutorPanel
        v-else-if="
          activeSection === 'LIA_TUTOR'
          && selectedStudent
        "
        :threads="tutorThreads"
        :conversation="tutorConversation"
        :visual-tasks="tutorVisualTasks"
        :materials="materials"
        :selected-material="selectedMaterial"
        :model-registry="aiModelRegistry"
        :busy="tutorBusy"
        @select-thread="selectTutorThread"
        @send="sendTutorMessage"
        @archive-thread="archiveTutorThread"
        @open-pedagogical="openPedagogicalFromTutor"
      />
      <LearningGoalPanel
        v-else-if="
          activeSection === 'LEARNING_GOAL'
          && selectedStudent
        "
        :contexts="assignedContexts"
        :goals="learningGoals"
        :selected-goal-id="
          selectedLearningGoal?.learningGoalId ?? null
        "
        @create="createLearningGoal"
        @select="selectLearningGoal"
      />
      <StudyScopePanel
        v-else-if="activeSection === 'STUDY_SCOPE'"
        :goal="selectedLearningGoal"
        :scopes="studyScopes"
        :selected-scope-id="
          selectedStudyScope?.studyScopeId ?? null
        "
        :candidates="scopeCandidates"
        @create-scope="createStudyScope"
        @select-scope="selectStudyScope"
        @add-unit="addScopeUnit"
        @remove-unit="removeScopeUnit"
      />
      <StudySessionPanel
        v-else-if="activeSection === 'STUDY_SESSION'"
        :scope="selectedStudyScope"
        :sessions="studySessions"
        @start="startStudySession"
        @complete="completeStudySession"
      />
      <LearningProgressPanel
        v-else-if="
          activeSection === 'LEARNING_PROGRESS'
          && selectedStudent
        "
        :states="learningStates"
        @update="updateLearningState"
      />
      <section v-else class="workspaceEmptyState">
        <h2>Selecione um aluno</h2>
        <p>
          Esta área depende de um Student selecionado.
        </p>
        <button
          type="button"
          @click="activeSection = 'STUDENT'"
        >
          Ir para Alunos
        </button>
      </section>
    </section>
    <MobileStudentNavigation
      :active-section="activeSection"
      :has-student="Boolean(selectedStudent)"
      @select="activeSection = $event"
    />
  </main>
</template>
