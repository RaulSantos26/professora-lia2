"""Scoped, idempotent image jobs. The map is usable independently of image success."""
import hashlib
import logging
from copy import deepcopy
from uuid import UUID
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from app.persistence.models.imageGenerationTaskModel import ImageGenerationTaskModel as Image
from app.services.imageBriefService import ImageBriefService
from app.services.studentContentOwnershipService import StudentContentOwnershipService

logger = logging.getLogger(__name__)

class MindMapAssetService:
    def __init__(self, session):
        self.session = session

    def attach(self, content, *, studentId, unitId, materialIds, evidence,
               artifactId=None, visualTaskId=None):
        try:
            with self.session.begin_nested():
                return self._attach(content, studentId=studentId, unitId=unitId, materialIds=materialIds,
                    evidence=evidence, artifactId=artifactId, visualTaskId=visualTaskId)
        except SQLAlchemyError:
            logger.exception('mindmap_asset_queue_unavailable artifact=%s visual=%s', artifactId, visualTaskId)
            result = deepcopy(content)
            for node in result.get('nodes', []):
                node.pop('imageTaskId', None)
            result['assetWarning'] = 'As figuras não puderam ser preparadas. O conteúdo do mapa está disponível.'
            return result

    def _attach(self, content, *, studentId, unitId, materialIds, evidence,
               artifactId=None, visualTaskId=None):
        # Callers have resolved the material scope; verify ownership again at this boundary.
        unit, subject, _ = StudentContentOwnershipService(self.session).assertUnitBelongsToStudent(unitId, studentId)
        result = deepcopy(content)
        nodes = result.get('nodes', [])
        root = result.get('rootId')
        sources = sorted(str(i) for i in materialIds)
        reused = generated = 0
        for node in nodes:
            # Never trust task identifiers returned by a model or copied from another artifact.
            node.pop('imageTaskId', None)
            description = str(node.get('visualDescription') or '').strip()
            if not description or not (node.get('nodeId') == root or node.get('parentId') == root):
                continue
            if generated + reused >= 8:
                break
            scene = ('One coherent educational textbook illustration. ' + description[:600] +
                ' Soft natural colors, recognizable objects, clear focal subject, uncluttered light background. '
                'Scene only, no letters, numbers, captions, labels, logos, watermarks, poster, frame, infographic or text panels.')
            prompt = ImageBriefService.marker + 'NO_TEXT\n' + scene
            fingerprint = hashlib.sha256((str(unitId) + '|' + '|'.join(sources) + '|' + prompt).encode()).hexdigest()
            key = 'LIA_MINDMAP_ASSET_V1:' + fingerprint
            # Serialize identical scope/descriptor requests across workers, without a schema migration.
            self.session.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': int(fingerprint[:15], 16)})
            existing = self.session.scalar(select(Image).where(
                Image.studentId == studentId, Image.imageMode == 'MIND_MAP_COMPANION',
                Image.labelsJson.contains([key]), Image.status.in_(['QUEUED','PREPARING','GENERATING','LABELING','READY'])
            ).order_by(Image.createdAt.desc()).limit(1))
            if existing:
                node['imageTaskId'] = str(existing.imageTaskId); reused += 1
                continue
            task = Image(studentId=studentId, relatedPedagogicalArtifactId=artifactId,
                relatedVisualTaskId=visualTaskId, imageMode='MIND_MAP_COMPANION',
                title=('Ilustração do mapa: ' + str(node.get('label') or result.get('title')))[:250],
                prompt=prompt, labelsJson=[key, 'Matéria: ' + subject.name, 'Lição: ' + unit.title],
                evidenceJson=evidence, sourceMaterialIds=sources)
            self.session.add(task); self.session.flush()
            node['imageTaskId'] = str(task.imageTaskId); generated += 1
        result['assetPolicy'] = 'SCOPED_BRANCH_IMAGES_V1'
        logger.info('mindmap_assets_enqueued artifact=%s visual=%s generated=%s reused=%s', artifactId, visualTaskId, generated, reused)
        return result
