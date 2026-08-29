import math

import networkx as nx


class VisualLayoutSkill:
    """
    Deterministic Python skill used after the LLM creates semantic
    visual content. It adds geometry without asking the LLM to guess
    pixel positions.
    """

    def layoutMindMap(
        self,
        spec: dict,
    ) -> dict:
        """
        Arrange a semantic tree according to the width of every subtree.
        This avoids the fixed-column layout that made labels overlap when
        a branch had more descendants than its neighbours.
        """
        sourceNodes = list(spec.get("nodes") or [])

        if not sourceNodes:
            return spec

        nodeById = {
            str(node.get("nodeId")): {
                **node,
                "nodeId": str(node.get("nodeId")),
            }
            for node in sourceNodes
            if node.get("nodeId") is not None
        }

        if not nodeById:
            return spec

        rootId = str(spec.get("rootId") or next(iter(nodeById)))

        if rootId not in nodeById:
            rootId = next(iter(nodeById))

        children: dict[str, list[str]] = {
            nodeId: []
            for nodeId in nodeById
        }

        for nodeId, node in nodeById.items():
            parentId = node.get("parentId")

            if (
                parentId is not None
                and str(parentId) in nodeById
                and str(parentId) != nodeId
            ):
                children[str(parentId)].append(nodeId)

        # A malformed parent/cycle must not hide a concept from the map.
        reachable: set[str] = set()

        def markReachable(nodeId: str) -> None:
            if nodeId in reachable:
                return
            reachable.add(nodeId)

            for childId in children[nodeId]:
                markReachable(childId)

        markReachable(rootId)

        for nodeId in nodeById:
            if nodeId not in reachable:
                children[rootId].append(nodeId)

        levels: dict[str, int] = {}

        def assignLevels(
            nodeId: str,
            level: int,
            ancestry: set[str],
        ) -> None:
            if nodeId in ancestry:
                return

            levels[nodeId] = level
            nextAncestry = ancestry | {nodeId}

            for childId in children[nodeId]:
                assignLevels(
                    childId,
                    level + 1,
                    nextAncestry,
                )

        assignLevels(rootId, 0, set())

        def nodeSize(node: dict) -> tuple[int, int]:
            label = str(node.get("label") or "")
            lineCount = max(
                1,
                math.ceil(len(label) / 24),
            )
            longestLine = min(
                max(len(label), 12),
                30,
            )
            width = min(
                320,
                max(188, 88 + longestLine * 7),
            )
            height = max(68, 34 + lineCount * 20)
            return width, height

        sizes = {
            nodeId: nodeSize(node)
            for nodeId, node in nodeById.items()
        }
        subtreeWidths: dict[str, int] = {}
        visiting: set[str] = set()

        def subtreeWidth(nodeId: str) -> int:
            if nodeId in subtreeWidths:
                return subtreeWidths[nodeId]

            if nodeId in visiting:
                return sizes[nodeId][0]

            visiting.add(nodeId)
            childWidths = [
                subtreeWidth(childId)
                for childId in children[nodeId]
                if childId not in visiting
            ]
            visiting.discard(nodeId)

            ownWidth = sizes[nodeId][0]
            childrenWidth = (
                sum(childWidths)
                + 56 * max(len(childWidths) - 1, 0)
            )
            subtreeWidths[nodeId] = max(
                ownWidth,
                childrenWidth,
            )
            return subtreeWidths[nodeId]

        totalWidth = subtreeWidth(rootId)
        levelHeights: dict[int, int] = {}

        for nodeId, level in levels.items():
            levelHeights[level] = max(
                levelHeights.get(level, 0),
                sizes[nodeId][1],
            )

        levelCenters: dict[int, float] = {}
        cursorY = 84.0

        for level in sorted(levelHeights):
            levelCenters[level] = (
                cursorY + levelHeights[level] / 2
            )
            cursorY += levelHeights[level] + 120

        positioned: list[dict] = []

        def place(
            nodeId: str,
            left: float,
            ancestry: set[str],
        ) -> None:
            if nodeId in ancestry:
                return

            width, height = sizes[nodeId]
            level = levels.get(nodeId, 0)
            positioned.append(
                {
                    **nodeById[nodeId],
                    "x": round(
                        left + subtreeWidths[nodeId] / 2,
                        2,
                    ),
                    "y": round(levelCenters[level], 2),
                    "width": width,
                    "height": height,
                    "level": level,
                }
            )

            childCursor = left
            nextAncestry = ancestry | {nodeId}

            for childId in children[nodeId]:
                if childId in nextAncestry:
                    continue
                place(
                    childId,
                    childCursor,
                    nextAncestry,
                )
                childCursor += subtreeWidths[childId] + 56

        place(rootId, 120.0, set())

        viewportWidth = max(
            960,
            math.ceil(totalWidth + 240),
        )
        viewportHeight = max(
            560,
            math.ceil(cursorY - 36),
        )

        return {
            **spec,
            "viewport": {
                "width": viewportWidth,
                "height": viewportHeight,
            },
            "nodes": positioned,
        }

    def layoutDiagram(
        self,
        spec: dict,
    ) -> dict:
        nodes = list(spec.get("nodes") or [])
        graph = nx.DiGraph()

        for node in nodes:
            graph.add_node(str(node.get("nodeId")))

        for edge in spec.get("edges") or []:
            graph.add_edge(
                str(edge.get("sourceId")),
                str(edge.get("targetId")),
            )

        orderedIds = list(
            nx.dfs_preorder_nodes(graph)
        )

        byId = {
            str(node.get("nodeId")): node
            for node in nodes
        }

        orderedNodes = [
            byId[nodeId]
            for nodeId in orderedIds
            if nodeId in byId
        ]

        for node in nodes:
            if node not in orderedNodes:
                orderedNodes.append(node)

        count = max(len(orderedNodes), 1)

        positioned = []

        for index, node in enumerate(orderedNodes):
            angle = (
                -math.pi / 2
                + index * (2 * math.pi / count)
            )

            positioned.append(
                {
                    **node,
                    "x": round(
                        600 + math.cos(angle) * 360,
                        2,
                    ),
                    "y": round(
                        350 + math.sin(angle) * 230,
                        2,
                    ),
                }
            )

        return {
            **spec,
            "viewport": {
                "width": 1200,
                "height": 700,
            },
            "nodes": positioned,
        }

    def normalizeAnimation(
        self,
        spec: dict,
    ) -> dict:
        objects = []

        for index, item in enumerate(
            spec.get("objects") or []
        ):
            objects.append(
                {
                    "objectId": str(
                        item.get("objectId")
                        or f"obj-{index + 1}"
                    ),
                    "label": str(
                        item.get("label")
                        or f"Objeto {index + 1}"
                    ),
                    "shape": str(
                        item.get("shape")
                        or "CIRCLE"
                    ).upper(),
                    "x": float(item.get("x", 320)),
                    "y": float(item.get("y", 220)),
                    "size": max(
                        8.0,
                        float(item.get("size", 28)),
                    ),
                    "motion": str(
                        item.get("motion")
                        or "STATIC"
                    ).upper(),
                    "speed": float(
                        item.get("speed", 0.4)
                    ),
                    "orbitRadius": max(
                        0.0,
                        float(
                            item.get(
                                "orbitRadius",
                                0,
                            )
                        ),
                    ),
                    "parentId": item.get("parentId"),
                }
            )

        return {
            **spec,
            "canvas": {
                "width": 960,
                "height": 540,
            },
            "objects": objects,
        }

    def normalizeScene3d(
        self,
        spec: dict,
    ) -> dict:
        objects = []

        for index, item in enumerate(
            spec.get("objects") or []
        ):
            position = item.get("position") or {}
            scale = item.get("scale") or {}

            objects.append(
                {
                    "objectId": str(
                        item.get("objectId")
                        or f"object-{index + 1}"
                    ),
                    "label": str(
                        item.get("label")
                        or f"Objeto {index + 1}"
                    ),
                    "primitive": str(
                        item.get("primitive")
                        or "SPHERE"
                    ).upper(),
                    "position": {
                        "x": float(
                            position.get("x", 0)
                        ),
                        "y": float(
                            position.get("y", 0)
                        ),
                        "z": float(
                            position.get("z", 0)
                        ),
                    },
                    "scale": {
                        "x": max(
                            0.1,
                            float(scale.get("x", 1)),
                        ),
                        "y": max(
                            0.1,
                            float(scale.get("y", 1)),
                        ),
                        "z": max(
                            0.1,
                            float(scale.get("z", 1)),
                        ),
                    },
                    "orbit": item.get("orbit"),
                    "rotationSpeed": float(
                        item.get(
                            "rotationSpeed",
                            0.0,
                        )
                    ),
                }
            )

        return {
            **spec,
            "camera": {
                "x": 0,
                "y": 4,
                "z": 10,
            },
            "objects": objects,
        }
