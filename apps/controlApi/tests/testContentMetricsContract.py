from app.contracts.contentMetricsContract import ContentMetricsContract


def testContentMetricsContractDefaultsAgenticFields():
    contract = ContentMetricsContract(
        available=True,
    )

    assert contract.contractName == "ContentMetrics.v4"
    assert contract.pedagogicalArtifacts == 0
    assert contract.pedagogicalJobsActive == 0
    assert contract.learningAttempts == 0
    assert contract.agentThreads == 0
    assert contract.agentRunsActive == 0
    assert contract.agentRunsFailed == 0
    assert contract.agentToolCalls == 0
    assert contract.visualTasks == 0
