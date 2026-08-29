from app.contracts.contentMetricsContract import ContentMetricsContract


def testContentMetricsContractDefaultsToZero():
    contract = ContentMetricsContract(available=False)

    assert contract.materials == 0
    assert contract.visualPendingBlocks == 0
    assert contract.chunksPendingEmbedding == 0

    assert contract.pedagogicalArtifacts == 0
    assert contract.pedagogicalJobsActive == 0
    assert contract.learningAttempts == 0
    assert contract.contractName == "ContentMetrics.v3"
