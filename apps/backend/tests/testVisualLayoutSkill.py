from app.skills.visualLayoutSkill import VisualLayoutSkill


def testMindMapLayoutAddsDeterministicCoordinates():
    skill = VisualLayoutSkill()

    spec = skill.layoutMindMap(
        {
            "title": "Tecidos",
            "rootId": "root",
            "nodes": [
                {
                    "nodeId": "root",
                    "parentId": None,
                    "label": "Tecidos",
                    "detail": "raiz",
                },
                {
                    "nodeId": "a",
                    "parentId": "root",
                    "label": "Conjuntivo",
                    "detail": "ramo",
                },
                {
                    "nodeId": "b",
                    "parentId": "root",
                    "label": "Nervoso",
                    "detail": "ramo",
                },
            ],
        }
    )

    assert spec["viewport"] == {
        "width": 1200,
        "height": 760,
    }
    assert spec["nodes"][0]["x"] == 600
    assert spec["nodes"][0]["y"] == 90
    assert all(
        "x" in node and "y" in node
        for node in spec["nodes"]
    )


def testDiagramLayoutDoesNotAskModelForPixelGeometry():
    skill = VisualLayoutSkill()
    spec = skill.layoutDiagram(
        {
            "nodes": [
                {"nodeId": "a", "label": "A"},
                {"nodeId": "b", "label": "B"},
            ],
            "edges": [
                {
                    "sourceId": "a",
                    "targetId": "b",
                    "label": "liga",
                }
            ],
        }
    )

    assert len(spec["nodes"]) == 2
    assert all(
        isinstance(node["x"], float)
        for node in spec["nodes"]
    )


def testScene3dNormalizerUsesSupportedPrimitives():
    spec = VisualLayoutSkill().normalizeScene3d(
        {
            "objects": [
                {
                    "objectId": "terra",
                    "label": "Terra",
                    "primitive": "SPHERE",
                    "position": {"x": 0, "y": 0, "z": 0},
                    "scale": {"x": 1, "y": 1, "z": 1},
                    "rotationSpeed": 0.1,
                    "orbit": None,
                }
            ]
        }
    )

    assert spec["objects"][0]["primitive"] == "SPHERE"
    assert spec["camera"]["z"] == 10
