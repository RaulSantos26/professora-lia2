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

    assert spec["viewport"]["width"] >= 960
    assert spec["viewport"]["height"] >= 560
    assert spec["nodes"][0]["level"] == 0
    assert all(
        {
            "x",
            "y",
            "width",
            "height",
        }.issubset(node)
        for node in spec["nodes"]
    )
    left, right = spec["nodes"][1:]
    assert abs(left["x"] - right["x"]) >= (
        (left["width"] + right["width"]) / 2
    )


def testMindMapLayoutPreventsOverlapInDeepBranches():
    nodes = [
        {
            "nodeId": "root",
            "parentId": None,
            "label": "O dia em que vi Pégaso nascer",
        }
    ]
    nodes.extend(
        [
            {
                "nodeId": f"page-{index}",
                "parentId": "root",
                "label": f"Página {index}",
            }
            for index in range(1, 4)
        ]
    )

    for pageIndex in range(1, 4):
        for childIndex in range(1, 4):
            nodes.append(
                {
                    "nodeId": (
                        f"page-{pageIndex}-item-{childIndex}"
                    ),
                    "parentId": f"page-{pageIndex}",
                    "label": (
                        "Conceito importante com explicação "
                        f"{pageIndex}-{childIndex}"
                    ),
                }
            )

    spec = VisualLayoutSkill().layoutMindMap(
        {
            "rootId": "root",
            "nodes": nodes,
        }
    )
    positioned = spec["nodes"]

    for level in {node["level"] for node in positioned}:
        row = sorted(
            (
                node
                for node in positioned
                if node["level"] == level
            ),
            key=lambda node: node["x"],
        )

        for left, right in zip(row, row[1:]):
            assert (
                right["x"] - left["x"]
                >= (left["width"] + right["width"]) / 2
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
