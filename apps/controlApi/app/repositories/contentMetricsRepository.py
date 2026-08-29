import psycopg

from app.contracts.contentMetricsContract import ContentMetricsContract


class ContentMetricsRepository:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    async def getMetrics(self) -> ContentMetricsContract:
        try:
            connection = await psycopg.AsyncConnection.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                connect_timeout=3,
            )

            query = """
                SELECT
                    (SELECT COUNT(*) FROM lia2.student) AS students,
                    (
                        SELECT COUNT(*)
                        FROM lia2.material
                        WHERE status <> 'ARCHIVED'
                    ) AS materials,
                    (
                        SELECT COUNT(*)
                        FROM lia2.document_page
                    ) AS document_pages,
                    (
                        SELECT COUNT(*)
                        FROM lia2.document_block
                        WHERE block_type = 'TEXT'
                          AND processing_status = 'READY'
                    ) AS text_blocks,
                    (
                        SELECT COUNT(*)
                        FROM lia2.document_block
                        WHERE processing_status IN (
                            'PENDING_OCR',
                            'PENDING_VISION'
                        )
                    ) AS visual_pending_blocks,
                    (
                        SELECT COUNT(*)
                        FROM lia2.document_chunk
                        WHERE status = 'EMBEDDED'
                    ) AS embedded_chunks,
                    (
                        SELECT COUNT(*)
                        FROM lia2.document_chunk
                        WHERE status = 'PENDING_EMBEDDING'
                    ) AS chunks_pending_embedding,
                    (
                        SELECT COUNT(*)
                        FROM lia2.material_processing_job
                        WHERE status IN ('QUEUED', 'RUNNING')
                    ) AS processing_jobs,
                    (
                        SELECT COUNT(*)
                        FROM lia2.material_processing_job
                        WHERE status = 'FAILED'
                    ) AS failed_jobs,
                    (
                        SELECT COUNT(*)
                        FROM lia2.learning_goal
                        WHERE status = 'ACTIVE'
                    ) AS learning_goals,
                    (
                        SELECT COUNT(*)
                        FROM lia2.study_session
                    ) AS study_sessions,
                    (
                        SELECT COUNT(*)
                        FROM lia2.pedagogical_artifact
                        WHERE status <> 'ARCHIVED'
                    ) AS pedagogical_artifacts,
                    (
                        SELECT COUNT(*)
                        FROM lia2.pedagogical_artifact
                        WHERE status IN ('QUEUED', 'RUNNING')
                    ) AS pedagogical_jobs_active,
                    (
                        SELECT COUNT(*)
                        FROM lia2.pedagogical_artifact
                        WHERE status = 'FAILED'
                    ) AS pedagogical_jobs_failed,
                    (
                        SELECT COUNT(*)
                        FROM lia2.learning_attempt
                    ) AS learning_attempts,
                    (
                        SELECT COUNT(*)
                        FROM lia2.agent_thread
                        WHERE status = 'ACTIVE'
                    ) AS agent_threads,
                    (
                        SELECT COUNT(*)
                        FROM lia2.agent_run
                        WHERE status IN ('QUEUED', 'RUNNING')
                    ) AS agent_runs_active,
                    (
                        SELECT COUNT(*)
                        FROM lia2.agent_run
                        WHERE status = 'FAILED'
                    ) AS agent_runs_failed,
                    (
                        SELECT COUNT(*)
                        FROM lia2.agent_tool_call
                    ) AS agent_tool_calls,
                    (
                        SELECT COUNT(*)
                        FROM lia2.visual_task
                        WHERE status = 'READY'
                    ) AS visual_tasks
            """

            async with connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(query)
                    row = await cursor.fetchone()

            return ContentMetricsContract(
                available=True,
                students=int(row[0]),
                materials=int(row[1]),
                documentPages=int(row[2]),
                textBlocks=int(row[3]),
                visualPendingBlocks=int(row[4]),
                embeddedChunks=int(row[5]),
                chunksPendingEmbedding=int(row[6]),
                processingJobs=int(row[7]),
                failedJobs=int(row[8]),
                learningGoals=int(row[9]),
                studySessions=int(row[10]),
                pedagogicalArtifacts=int(row[11]),
                pedagogicalJobsActive=int(row[12]),
                pedagogicalJobsFailed=int(row[13]),
                learningAttempts=int(row[14]),
                agentThreads=int(row[15]),
                agentRunsActive=int(row[16]),
                agentRunsFailed=int(row[17]),
                agentToolCalls=int(row[18]),
                visualTasks=int(row[19]),
            )

        except Exception as error:
            return ContentMetricsContract(
                available=False,
                errorType=type(error).__name__,
            )
