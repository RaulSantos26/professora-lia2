"""Scoped, transactional OCR repair; original blocks/chunks remain untouched.

Run with PYTHONPATH=/app in the backend. Default is a read-only preview.
Audit JSON comes from a separate orientation/quality gate, never from an LLM.
"""
import argparse
import json
from pathlib import Path
from uuid import UUID
from sqlalchemy import select, func
from app.liaBackendApplication import application
from app.database.databaseSessionFactory import DatabaseSessionFactory
from app.persistence.models.materialModel import MaterialModel as Material
from app.persistence.models.documentModel import DocumentModel as Document
from app.persistence.models.documentVersionModel import DocumentVersionModel as Version
from app.persistence.models.documentPageModel import DocumentPageModel as Page
from app.persistence.models.documentBlockModel import DocumentBlockModel as Block
from app.persistence.models.documentChunkModel import DocumentChunkModel as Chunk
from app.persistence.models.evidenceModel import EvidenceModel as Evidence
from app.services.documentIngestionService import DocumentIngestionService
from app.services.embeddingService import EmbeddingService

parser=argparse.ArgumentParser()
parser.add_argument('--audit',required=True)
parser.add_argument('--material',type=UUID,required=True)
parser.add_argument('--student',type=UUID,required=True)
parser.add_argument('--unit',type=UUID,required=True)
parser.add_argument('--manifest',required=True)
parser.add_argument('--apply',action='store_true')
parser.add_argument('--rollback',action='store_true')
args=parser.parse_args()
with DatabaseSessionFactory() as session:
    material=session.scalar(select(Material).where(Material.materialId==args.material).with_for_update())
    assert material and material.studentId==args.student and material.studentLearningUnitId==args.unit, 'Scope mismatch'
    if args.rollback:
        manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
        assert manifest['materialId']==str(args.material)
        for identifier in manifest['newEvidenceIds']:
            item=session.get(Evidence,UUID(identifier))
            assert item and item.materialId==args.material and item.locator.startswith('OCR revisado')
            item.status='ARCHIVED'
        for identifier in manifest['oldEvidenceIds']:
            item=session.get(Evidence,UUID(identifier))
            assert item and item.materialId==args.material and item.status=='SUPERSEDED'
            item.status='ACTIVE'
        if args.apply: session.commit()
        else: session.rollback()
        print('ROLLBACK', 'APPLIED' if args.apply else 'PREVIEW',flush=True)
    else:
        audit=json.loads(Path(args.audit).read_text(encoding='utf-8'))
        manifest={'materialId':str(args.material),'oldEvidenceIds':[],'newEvidenceIds':[],'newBlockIds':[]}
        chunks=[]
        for entry in audit:
            if not entry['text'].strip():
                assert entry['oldChars']==0, 'Do not replace nonempty OCR with blank text'
                continue
            assert entry['confidence']>=85, 'Capture needs manual review'
            page=session.get(Page,UUID(entry['pageId']))
            block=session.get(Block,UUID(entry['imageBlockId']))
            version=session.get(Version,page.documentVersionId)
            document=session.get(Document,version.documentId)
            assert document.materialId==args.material and block.documentPageId==page.documentPageId
            assert str(version.documentVersionId)==entry['versionId'] and page.pageNumber==entry['pageNumber']
            latest=session.scalar(select(func.max(Version.versionNumber)).where(Version.documentId==document.documentId))
            assert version.versionNumber==latest, 'Newer version exists'
            existing=session.scalars(select(Evidence).where(Evidence.materialId==args.material,Evidence.documentPageId==page.documentPageId,Evidence.status=='ACTIVE')).all()
            assert not any(e.locator.startswith('OCR revisado') for e in existing), 'Already repaired; refusing duplicate'
            old=[e for e in existing if e.locator.startswith('OCR local')]
            manifest['oldEvidenceIds'].extend(str(e.evidenceId) for e in old)
            print('PAGE',page.pageNumber,'chars',len(entry['text']),'confidence',round(entry['confidence'],2),'replaces',len(old),flush=True)
            if not args.apply: continue
            sequence=(session.scalar(select(func.max(Block.sequenceNumber)).where(Block.documentPageId==page.documentPageId)) or 0)+1
            revised=Block(documentPageId=page.documentPageId,sequenceNumber=sequence,blockType='TEXT',textContent=entry['text'],processingStatus='READY',
                structuredData={'audit':'OCR_ORIENTATION_REPAIR_V1','sourceImageBlockId':str(block.documentBlockId),'confidence':entry['confidence'],'supersedes':[str(e.evidenceId) for e in old]})
            session.add(revised); session.flush()
            evidence=Evidence(studentId=args.student,materialId=args.material,documentVersionId=version.documentVersionId,documentPageId=page.documentPageId,
                documentBlockId=revised.documentBlockId,evidenceType='TEXT',locator=f'OCR revisado · página {page.pageNumber}',excerpt=entry['text'][:1000],status='ACTIVE')
            session.add(evidence); session.flush()
            manifest['newBlockIds'].append(str(revised.documentBlockId)); manifest['newEvidenceIds'].append(str(evidence.evidenceId))
            index=(session.scalar(select(func.max(Chunk.chunkIndex)).where(Chunk.documentVersionId==version.documentVersionId)) or 0)+1
            for offset,content in enumerate(DocumentIngestionService(session)._chunks(entry['text'])):
                chunk=Chunk(documentVersionId=version.documentVersionId,documentPageId=page.documentPageId,documentBlockId=revised.documentBlockId,evidenceId=evidence.evidenceId,
                    chunkIndex=index+offset,content=content,tokenEstimate=max(1,len(content)//2),status='PENDING_EMBEDDING')
                session.add(chunk); chunks.append(chunk)
            for e in old: e.status='SUPERSEDED'
            session.flush()
        if args.apply:
            decision,count=EmbeddingService().embedChunks(chunks)
            assert count==len(chunks)
            destination=Path(args.manifest)
            assert not destination.exists(), 'Manifest already exists; refusing overwrite'
            destination.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            session.commit()
            print('REPAIR_COMMITTED',len(manifest['newEvidenceIds']),'pages',count,'chunks; original data retained',flush=True)
        else:
            session.rollback()
            print('DRY_RUN_PASS',len(manifest['oldEvidenceIds']),'old evidence records; no database writes',flush=True)
