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
        nodes = list(spec.get("nodes") or [])

        if not nodes:
            return spec

        rootId = str(
            spec.get("rootId")
            or nodes[0].get("nodeId")
        )

        graph = nx.DiGraph()

        for node in nodes:
            nodeId = str(node.get("nodeId"))
            graph.add_node(nodeId)

            parentId = node.get("parentId")

            if parentId is not None:
                graph.add_edge(
                    str(parentId),
                    nodeId,
                )

        levels = nx.single_source_shortest_path_length(
            graph,
            rootId,
        )

        byParent: dict[str | None, list[dict]] = {}

        for node in nodes:
            byParent.setdefault(
                node.get("parentId"),
                [],
            ).append(node)

        positioned = []
        root = next(
            (
                node
                for node in nodes
                if str(node.get("nodeId")) == rootId
            ),
            nodes[0],
        )
        positioned.append(
            {
                **root,
                "x": 600,
                "y": 90,
                "level": int(levels.get(str(root.get("nodeId")), 0)),
            }
        )

        branches = byParent.get(root.get("nodeId"), [])

        for branchIndex, branch in enumerate(branches):
            x = (
                130
                + branchIndex
                * (
                    940
                    / max(len(branches) - 1, 1)
                )
            )
            positioned.append(
                {
                    **branch,
                    "x": round(x, 2),
                    "y": 250,
                    "level": int(levels.get(str(branch.get("nodeId")), 1)),
                }
            )

            children = byParent.get(
                branch.get("nodeId"),
                [],
            )

            for childIndex, child in enumerate(children):
                offset = (
                    childIndex
                    - (len(children) - 1) / 2
                ) * 150

                positioned.append(
                    {
                        **child,
                        "x": round(x + offset, 2),
                        "y": 430,
                        "level": int(levels.get(str(child.get("nodeId")), 2)),
                    }
                )

                grandchildren = byParent.get(
                    child.get("nodeId"),
                    [],
                )

                for grandIndex, grand in enumerate(
                    grandchildren
                ):
                    positioned.append(
                        {
                            **grand,
                            "x": round(
                                x
                                + offset
                                + (
                                    grandIndex
                                    - (
                                        len(grandchildren)
                                        - 1
                                    )
                                    / 2
                                )
                                * 110,
                                2,
                            ),
                            "y": 590,
                            "level": int(levels.get(str(grand.get("nodeId")), 3)),
                        }
                    )

        known = {
            str(item.get("nodeId"))
            for item in positioned
        }

        for node in nodes:
            if str(node.get("nodeId")) not in known:
                positioned.append(
                    {
                        **node,
                        "x": 600,
                        "y": 680,
                        "level": 4,
                    }
                )

        return {
            **spec,
            "viewport": {
                "width": 1200,
                "height": 760,
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
