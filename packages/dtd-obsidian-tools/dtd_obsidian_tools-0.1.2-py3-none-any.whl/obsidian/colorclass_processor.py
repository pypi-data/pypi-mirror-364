# obsidian/colorclass_processor.py - Add unique colorclass tags with community detection

import colorsys
import json
import random
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any, Tuple

import fire
import frontmatter
import networkx as nx
import seaborn as sns
from loguru import logger
from omegaconf import DictConfig, OmegaConf

if TYPE_CHECKING:
    from .parser import ObsDoc
else:
    # Runtime imports to avoid circular dependencies
    pass

from .graph import build_graph, find_candidates, get_link_statistics, load_corpus


def hsl_to_rgb_int(hsl: Tuple[float, float, float]) -> int:
    """
    Convert HSL color to RGB integer format used by Obsidian.

    Args:
        hsl: Tuple of (hue, saturation, lightness) values between 0-1

    Returns:
        RGB integer value
    """
    h, s, l = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)  # Note: colorsys uses HLS order

    # Convert to 0-255 range and combine into single integer
    r_int = int(r * 255)
    g_int = int(g * 255)
    b_int = int(b * 255)

    # Combine RGB values into single integer (format: 0xRRGGBB)
    rgb_int = (r_int << 16) | (g_int << 8) | b_int
    return rgb_int


def strided_palette(n: int, stride: int = 5) -> list[int]:
    """Generate a strided color palette.

    Args:
        n: Number of colors to generate.
        stride: Step size for color generation.

    Returns:
        List of strided color RGB integers.
    """
    strided_wheel = []
    wheel_palette = sns.color_palette("hls", n)
    i = 0
    while True:
        if not wheel_palette:
            break
        if i > len(wheel_palette) - 1:
            i -= len(wheel_palette)
            continue
        hsl = wheel_palette.pop(i)
        rgb = hsl_to_rgb_int(hsl)
        strided_wheel.append(rgb)
        i += stride
    return strided_wheel


class ColorclassProcessor:
    """Processes Obsidian vault to add unique colorclass tags with NetworkX community detection."""

    # Available NetworkX community detection algorithms
    AVAILABLE_ALGORITHMS = {
        "louvain": "louvain_communities",
        "leiden": "leiden_communities",
        "greedy_modularity": "greedy_modularity_communities",
        "girvan_newman": "girvan_newman",
        "label_propagation": "asyn_lpa_communities",
        "kernighan_lin": "kernighan_lin_bisection",
    }

    def __init__(self, config_path: str | None = None):
        """Initialize processor with optional config file."""
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str | None) -> DictConfig:
        """Load configuration from YAML file or use defaults."""
        default_config = OmegaConf.create(
            {
                "colorclass_prefix": "colorclass",
                "dry_run": False,
                "backup_originals": False,
                "generate_graph_config": True,  # New option to control graph.json generation
                "community_detection": {
                    "algorithm": "louvain",  # Default algorithm
                    "algorithm_params": {  # Parameters passed to the algorithm
                        "seed": 42,
                        "resolution": 1.0,  # For louvain/leiden
                        "threshold": 1e-07,  # For leiden
                        "max_comm_size": 0,  # For leiden (0 = no limit)
                        "weight": None,  # Edge weight attribute name
                        "max_levels": None,  # For girvan_newman (None = all levels)
                    },
                    "min_community_size": 5,  # Minimum size for a community to get colorclass
                    "naming_scheme": "largest_node",  # 'cluster_id', 'largest_node', or 'sequential'
                },
            }
        )

        if config_path:
            config_path_obj = Path(config_path)
            if config_path_obj.exists():
                file_config = OmegaConf.load(config_path_obj)
                merged = OmegaConf.merge(default_config, file_config)
                # Convert to DictConfig if it's not already
                return (
                    OmegaConf.create(merged)
                    if not isinstance(merged, DictConfig)
                    else merged
                )
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")

        return default_config

    def list_algorithms(self) -> list[str]:
        """List available community detection algorithms."""
        available = []
        for algo_name, nx_func_name in self.AVAILABLE_ALGORITHMS.items():
            if hasattr(nx.community, nx_func_name):
                available.append(algo_name)
            else:
                logger.debug(
                    f"Algorithm {algo_name} ({nx_func_name}) not available in this NetworkX version"
                )
        return available

    def process_vault(
        self,
        vault_path: str,
        dry_run: bool | None = None,
        algorithm: str | None = None,
        # generate_graph_config: bool | None = True,
    ) -> dict[str, str]:
        """Process vault to add colorclass tags using community detection.

        Args:
            vault_path: Path to Obsidian vault directory
            dry_run: If True, show what would be changed without modifying files
            algorithm: Community detection algorithm to use (overrides config)

        Returns:
            Dictionary mapping article names to their assigned colorclass tags
        """
        vault_path_obj = Path(vault_path)
        dry_run = dry_run if dry_run is not None else self.config.dry_run
        algorithm = algorithm or self.config.community_detection.algorithm

        available_algorithms = self.list_algorithms()
        if algorithm not in available_algorithms:
            raise ValueError(
                f"Unknown or unavailable algorithm: {algorithm}. Available: {available_algorithms}"
            )

        logger.info(f"Processing vault: {vault_path_obj}")
        logger.info(f"Algorithm: {algorithm}")
        logger.info(f"Dry run: {dry_run}")

        # Load all documents
        _corpus = load_corpus(vault_path_obj)

        # Prune cruft
        # WARNING: this deletes content.
        corpus = []
        for doc in _corpus:
            if doc.tags and any(["prune" in tag for tag in doc.tags]):
                if doc.fpath:
                    doc.fpath.unlink()
                    logger.warning(f"Pruned {doc.title}")
                continue
            else:
                corpus.append(doc)

        # Run community detection on all documents
        communities, undirected_graph = self._detect_communities(corpus, algorithm)
        assignments = self._process_communities(communities, undirected_graph)

        if not assignments:
            logger.warning("No community assignments generated")
            return {}

        # Generate color palette for communities
        unique_colorclasses = list(set(assignments.values()))
        n = len(unique_colorclasses)
        palette = strided_palette(n)

        # Create colorclass to color mapping
        colorclass_to_color = dict(zip(unique_colorclasses, palette))

        # Apply changes to files
        if not dry_run:
            modified_count = self._apply_assignments(
                corpus, vault_path_obj, assignments
            )
            logger.success(f"Modified {modified_count} files")

            # Generate Obsidian graph configuration
            if self.config.generate_graph_config:
                self._generate_obsidian_graph_config(
                    vault_path_obj, colorclass_to_color
                )
        else:
            logger.info("Dry run complete - no files modified")
            if self.config.generate_graph_config:
                logger.info(
                    "Graph config would be generated with the following colorclasses:"
                )
                for colorclass, color in colorclass_to_color.items():
                    logger.info(f"  {colorclass}: {color}")

        return assignments

    def _generate_obsidian_graph_config(
        self, vault_path: Path, colorclass_to_color: dict[str, int]
    ) -> None:
        """Generate or update .obsidian/graph.json with colorGroups."""
        obsidian_dir = vault_path / ".obsidian"
        graph_config_path = obsidian_dir / "graph.json"

        # Create .obsidian directory if it doesn't exist
        obsidian_dir.mkdir(exist_ok=True)

        # Default graph configuration
        default_config = {
            "collapse-filter": False,
            "search": "",
            "showTags": False,
            "showAttachments": False,
            "hideUnresolved": True,
            "showOrphans": False,
            "collapse-color-groups": True,
            "colorGroups": [],
            "collapse-display": True,
            "showArrow": False,
            "textFadeMultiplier": -2,
            "nodeSizeMultiplier": 0.64730224609375,
            "lineSizeMultiplier": 0.152437337239583,
            "collapse-forces": False,
            "centerStrength": 0.059814453125,
            "repelStrength": 15.6656901041667,
            "linkStrength": 1,
            "linkDistance": 30,
            "scale": 0.02849801640727639,
            "close": False,
        }

        # Load existing configuration if it exists
        if graph_config_path.exists():
            try:
                with open(graph_config_path, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
                # Merge with default config, preserving existing settings
                config = {**default_config, **existing_config}
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(
                    f"Could not load existing graph config: {e}, using defaults"
                )
                config = default_config
        else:
            config = default_config

        # Remove existing colorclass color groups to avoid duplicates
        prefix = f"tag:#{self.config.colorclass_prefix}/"
        existing_color_groups = config.get("colorGroups", [])
        filtered_color_groups = [
            group
            for group in existing_color_groups
            if not group.get("query", "").strip().startswith(prefix)
        ]

        # Generate new color groups for colorclasses
        new_color_groups = []
        for colorclass, rgb_color in colorclass_to_color.items():
            # Remove the prefix to get just the tag name
            tag_name = colorclass.replace(f"{self.config.colorclass_prefix}/", "")
            color_group = {
                "query": f"tag:#{self.config.colorclass_prefix}/{tag_name}",
                "color": {"a": 1, "rgb": rgb_color},
            }
            new_color_groups.append(color_group)

        # Combine filtered existing groups with new colorclass groups
        config["colorGroups"] = filtered_color_groups + new_color_groups

        # Write the updated configuration
        try:
            with open(graph_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.success(
                f"Generated Obsidian graph config with {len(new_color_groups)} colorclass groups"
            )
            logger.info(f"Graph config saved to: {graph_config_path}")

        except Exception as e:
            logger.error(f"Failed to write graph config: {e}")

    def _detect_communities(
        self, corpus: list["ObsDoc"], algorithm: str
    ) -> tuple[list[set[str]], nx.Graph]:
        """Use NetworkX community detection to assign colorclass tags."""
        logger.info(f"Starting community detection with {algorithm}...")

        # Build graph from corpus
        graph = build_graph(corpus)

        # Filter to existing documents only (no phantom nodes)
        existing_nodes = []
        for doc in corpus:
            if doc.node_name in graph.nodes:
                existing_nodes.append(doc.node_name)

        subgraph = graph.subgraph(existing_nodes).copy()
        logger.info(
            f"Clustering subgraph with {len(subgraph.nodes)} nodes, {len(subgraph.edges)} edges"
        )

        if len(subgraph.nodes) < 2:
            logger.warning("Graph too small for community detection")
            return []

        # Convert to undirected for algorithms
        undirected_graph = subgraph.to_undirected()

        # Run the selected algorithm
        communities = self._run_networkx_algorithm(undirected_graph, algorithm)

        if not communities:
            logger.error("Community detection failed to produce results")
            return []
        return communities, undirected_graph

    def _run_networkx_algorithm(
        self, graph: nx.Graph, algorithm: str
    ) -> list[set[str]]:
        """Run NetworkX community detection algorithm."""
        try:
            params = dict(self.config.community_detection.algorithm_params)
            nx_func_name = self.AVAILABLE_ALGORITHMS[algorithm]

            if not hasattr(nx.algorithms.community, nx_func_name):
                logger.error(
                    f"Algorithm {algorithm} ({nx_func_name}) not available in NetworkX"
                )
                return []

            func = getattr(nx.algorithms.community, nx_func_name)

            # Prepare parameters based on algorithm
            if algorithm == "louvain":
                nx_params = {}
                if "seed" in params and params["seed"] is not None:
                    nx_params["seed"] = params["seed"]
                if "resolution" in params and params["resolution"] is not None:
                    nx_params["resolution"] = params["resolution"]
                if "weight" in params and params["weight"] is not None:
                    nx_params["weight"] = params["weight"]

                logger.info(f"Running NetworkX Louvain with parameters: {nx_params}")
                communities = func(graph, **nx_params)

            elif algorithm == "leiden":
                nx_params = {}
                if "seed" in params and params["seed"] is not None:
                    nx_params["seed"] = params["seed"]
                if "resolution" in params and params["resolution"] is not None:
                    nx_params["resolution"] = params["resolution"]
                if "threshold" in params and params["threshold"] is not None:
                    nx_params["threshold"] = params["threshold"]
                if (
                    "max_comm_size" in params
                    and params["max_comm_size"] is not None
                    and params["max_comm_size"] > 0
                ):
                    nx_params["max_comm_size"] = params["max_comm_size"]

                logger.info(f"Running NetworkX Leiden with parameters: {nx_params}")
                communities = func(graph, **nx_params)

            elif algorithm == "greedy_modularity":
                nx_params = {}
                if "weight" in params and params["weight"] is not None:
                    nx_params["weight"] = params["weight"]
                if "resolution" in params and params["resolution"] is not None:
                    nx_params["resolution"] = params["resolution"]

                logger.info(
                    f"Running NetworkX Greedy Modularity with parameters: {nx_params}"
                )
                communities = func(graph, **nx_params)

            elif algorithm == "girvan_newman":
                nx_params = {}
                if "weight" in params and params["weight"] is not None:
                    nx_params["weight"] = params["weight"]

                logger.info(
                    f"Running NetworkX Girvan-Newman with parameters: {nx_params}"
                )
                # Girvan-Newman returns a generator of community divisions
                communities_gen = func(graph, **nx_params)

                # Get the best division (or up to max_levels)
                max_levels = params.get("max_levels", 10)  # Default to 10 levels
                if max_levels is None:
                    max_levels = 10

                best_communities = None
                best_modularity = -1

                for i, division in enumerate(communities_gen):
                    if i >= max_levels:
                        break
                    modularity = nx.algorithms.community.modularity(graph, division)
                    if modularity > best_modularity:
                        best_modularity = modularity
                        best_communities = division

                communities = best_communities if best_communities else []
                logger.info(f"Girvan-Newman best modularity: {best_modularity}")

            elif algorithm == "label_propagation":
                nx_params = {}
                if "seed" in params and params["seed"] is not None:
                    nx_params["seed"] = params["seed"]
                if "weight" in params and params["weight"] is not None:
                    nx_params["weight"] = params["weight"]

                logger.info(
                    f"Running NetworkX Label Propagation with parameters: {nx_params}"
                )
                communities = func(graph, **nx_params)

            elif algorithm == "kernighan_lin":
                # This is a bisection algorithm, so we'll apply it recursively
                logger.info("Running NetworkX Kernighan-Lin (recursive bisection)")
                communities = self._recursive_kernighan_lin(graph, params)

            else:
                logger.error(f"Unknown algorithm implementation: {algorithm}")
                return []

            if communities:
                communities_list = list(communities)
                logger.info(
                    f"NetworkX {algorithm} found {len(communities_list)} communities"
                )
                return communities_list
            else:
                logger.warning(f"NetworkX {algorithm} returned no communities")
                return []

        except Exception as e:
            logger.error(f"NetworkX {algorithm} failed: {e}")
            return []

    def _recursive_kernighan_lin(
        self, graph: nx.Graph, params: dict[str, Any], max_depth: int = 4
    ) -> list[set[str]]:
        """Apply Kernighan-Lin bisection recursively to create multiple communities."""
        communities: list[set[str]] = []

        def bisect_graph(g: nx.Graph, depth: int = 0) -> None:
            if len(g.nodes) < 4 or depth >= max_depth:  # Stop if too small or too deep
                communities.append(set(g.nodes))
                return

            try:
                # Apply Kernighan-Lin bisection
                partition = nx.algorithms.community.kernighan_lin_bisection(
                    g, seed=params.get("seed")
                )

                # If partition is successful and creates meaningful split
                if len(partition[0]) > 1 and len(partition[1]) > 1:
                    # Recursively bisect each partition
                    subgraph1 = g.subgraph(partition[0]).copy()
                    subgraph2 = g.subgraph(partition[1]).copy()
                    bisect_graph(subgraph1, depth + 1)
                    bisect_graph(subgraph2, depth + 1)
                else:
                    # Can't split meaningfully, add as single community
                    communities.append(set(g.nodes))
            except:
                # If bisection fails, add as single community
                communities.append(set(g.nodes))

        bisect_graph(graph)
        return communities

    def _process_communities(
        self, communities: list[set[str]], graph: nx.Graph
    ) -> dict[str, str]:
        """Process communities into colorclass assignments."""
        # Filter communities by minimum size
        min_size = self.config.community_detection.min_community_size
        filtered_communities = [
            community for community in communities if len(community) >= min_size
        ]

        logger.info(
            f"Found {len(communities)} communities, {len(filtered_communities)} after size filtering"
        )

        # Generate colorclass assignments
        assignments = {}
        naming_scheme = self.config.community_detection.naming_scheme

        for i, community in enumerate(filtered_communities):
            # Convert community to list if it's a set
            nodes = list(community)

            if naming_scheme == "cluster_id":
                # Use community index as colorclass name
                colorclass_tag = f"{self.config.colorclass_prefix}/cluster_{i}"

            elif naming_scheme == "largest_node":
                # Use the node with highest degree as colorclass name
                max_degree = -1
                representative_node = nodes[0]
                for node in nodes:
                    degree = graph.degree(node)
                    if degree > max_degree:
                        max_degree = degree
                        representative_node = node
                representative_node = representative_node.replace(" ", "-")

                colorclass_tag = (
                    f"{self.config.colorclass_prefix}/{representative_node}"
                )

            elif naming_scheme == "sequential":
                # Use sequential numbering
                colorclass_tag = f"{self.config.colorclass_prefix}/community_{i+1}"

            else:
                raise ValueError(f"Unknown naming scheme: {naming_scheme}")

            # Assign colorclass to all nodes in community
            for node in nodes:
                assignments[node] = colorclass_tag

            logger.info(f"Community {i} ({len(nodes)} nodes) → {colorclass_tag}")

        return assignments

    def _apply_assignments(
        self, corpus: list["ObsDoc"], vault_path: Path, assignments: dict[str, str]
    ) -> int:
        """Apply colorclass assignments to document files."""
        modified_count = 0

        for doc in corpus:
            if doc.node_name in assignments:
                colorclass_tag = assignments[doc.node_name]
                if self._add_colorclass_tag(doc, vault_path, colorclass_tag):
                    modified_count += 1

        return modified_count

    def _add_colorclass_tag(
        self, doc: "ObsDoc", vault_path: Path, colorclass_tag: str
    ) -> bool:
        """Add colorclass tag to a document's frontmatter.

        Args:
            doc: ObsDoc instance to modify
            vault_path: Path to vault directory
            colorclass_tag: The colorclass tag to add

        Returns:
            True if file was modified, False otherwise
        """
        file_path = doc.fpath if doc.fpath else vault_path / f"{doc.title}.md"

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        # Check if colorclass tag already exists
        existing_colorclass = None
        if doc.tags:
            for tag in doc.tags:
                if (tag is not None) and tag.startswith(
                    f"{self.config.colorclass_prefix}/"
                ):
                    existing_colorclass = tag
                    break

        if existing_colorclass == colorclass_tag:
            logger.debug(f"Colorclass tag already correct for {doc.title}")
            return False

        # Backup original if configured
        if self.config.backup_originals:
            backup_path = file_path.with_suffix(".md.bak")
            if not backup_path.exists():
                backup_path.write_text(file_path.read_text(encoding="utf-8"))

        # Read and parse content with python-frontmatter
        content = file_path.read_text(encoding="utf-8")
        post = frontmatter.loads(content)

        # Check if colorclass tag already exists
        existing_colorclass = None
        if post.metadata.get("tags"):
            for tag in post.metadata["tags"]:
                if (tag is not None) and tag.startswith(
                    f"{self.config.colorclass_prefix}/"
                ):
                    existing_colorclass = tag
                    break

        if existing_colorclass == colorclass_tag:
            logger.debug(f"Colorclass tag already correct for {doc.title}")
            return False

        # Backup original if configured
        if self.config.backup_originals:
            backup_path = file_path.with_suffix(".md.bak")
            if not backup_path.exists():
                backup_path.write_text(content)

        # Modify frontmatter
        if "tags" not in post.metadata:
            post.metadata["tags"] = []
        elif not isinstance(post.metadata["tags"], list):
            post.metadata["tags"] = [post.metadata["tags"]]

        # Remove existing colorclass tag if present
        post.metadata["tags"] = [
            tag
            for tag in post.metadata["tags"]
            if (tag is not None)
            and (not tag.startswith(f"{self.config.colorclass_prefix}/"))
        ]

        # Add new colorclass tag
        post.metadata["tags"].append(colorclass_tag)

        # Write modified content using frontmatter
        new_content = frontmatter.dumps(post)
        file_path.write_text(new_content, encoding="utf-8")
        logger.info(f"Added {colorclass_tag} to {doc.title}")
        return True

    def analyze_community_structure(
        self, vault_path: str, algorithm: str | None = None
    ) -> dict[str, Any]:
        """Analyze community structure that would be detected."""
        vault_path_obj = Path(vault_path)
        algorithm = algorithm or self.config.community_detection.algorithm

        available_algorithms = self.list_algorithms()
        if algorithm not in available_algorithms:
            raise ValueError(f"Unknown or unavailable algorithm: {algorithm}")

        logger.info(f"Analyzing community structure with algorithm: {algorithm}")

        corpus = load_corpus(vault_path_obj)
        graph = build_graph(corpus)

        # Filter to existing documents
        existing_nodes = [
            doc.node_name for doc in corpus if doc.node_name in graph.nodes
        ]
        subgraph = graph.subgraph(existing_nodes).to_undirected()

        if len(subgraph.nodes) < 2:
            return {"error": "Graph too small for analysis"}

        # Run community detection
        try:
            communities = self._run_networkx_algorithm(subgraph, algorithm)

            if not communities:
                return {"error": "Community detection failed"}

        except Exception as e:
            return {"error": f"Community detection failed: {e}"}

        # Calculate statistics
        community_sizes = [len(community) for community in communities]
        min_size = self.config.community_detection.min_community_size
        valid_communities = [
            community for community in communities if len(community) >= min_size
        ]

        # Calculate modularity for the detected communities
        try:
            modularity = nx.algorithms.community.modularity(subgraph, communities)
        except:
            modularity = None

        analysis = {
            "total_documents": len(corpus),
            "clustered_documents": len(existing_nodes),
            "total_communities": len(communities),
            "valid_communities": len(valid_communities),
            "modularity": modularity,
            "community_size_stats": {
                "min": min(community_sizes) if community_sizes else 0,
                "max": max(community_sizes) if community_sizes else 0,
                "mean": (
                    sum(community_sizes) / len(community_sizes)
                    if community_sizes
                    else 0
                ),
                "sizes": sorted(community_sizes, reverse=True)[:10],  # Top 10 sizes
            },
            "coverage": (
                len([n for community in valid_communities for n in community])
                / len(existing_nodes)
                if existing_nodes
                else 0
            ),
            "algorithm": algorithm,
        }

        logger.info(f"Community analysis: {analysis}")
        return analysis


def main() -> None:
    """CLI entry point for colorclass processor."""
    logger.add("colorclass_processor.log", rotation="1 MB")
    fire.Fire(ColorclassProcessor)


if __name__ == "__main__":
    main()
