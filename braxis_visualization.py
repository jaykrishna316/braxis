"""
Feature 9: Visual Dependency Graphs
Renders monorepo structure and dependencies as interactive diagrams.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class Package:
    """A package in a monorepo."""
    name: str
    path: str
    dependencies: List[str] = field(default_factory=list)
    internal_dependencies: List[str] = field(default_factory=list)


@dataclass
class DepGraph:
    """A dependency graph."""
    packages: Dict[str, Package]
    root_path: str


class VisualizationEngine:
    """Generates visual representations of code structure."""

    def __init__(self):
        self.graphs: Dict[str, DepGraph] = {}

    def create_dependency_graph(self, root_path: str) -> DepGraph:
        """Create a dependency graph for a monorepo."""
        graph = DepGraph(packages={}, root_path=root_path)
        self.graphs[root_path] = graph
        return graph

    def add_package(self, graph: DepGraph, package: Package) -> None:
        """Add a package to the graph."""
        graph.packages[package.name] = package

    def generate_svg(self, graph: DepGraph, max_width: int = 800) -> str:
        """Generate SVG visualization of dependency graph."""
        if not graph.packages:
            return "<svg></svg>"

        # Simple layout: arrange packages in grid
        packages = list(graph.packages.values())
        cols = min(4, len(packages))
        rows = (len(packages) + cols - 1) // cols

        cell_width = max_width // cols
        cell_height = 100

        svg = f'<svg width="{max_width}" height="{rows * cell_height + 50}" class="dep-graph">\n'

        # Draw packages
        for idx, package in enumerate(packages):
            row = idx // cols
            col = idx % cols
            x = col * cell_width + 10
            y = row * cell_height + 10

            # Package box
            svg += f'<g class="package" id="pkg-{package.name}">\n'
            svg += f'  <rect x="{x}" y="{y}" width="{cell_width-20}" height="80" '
            svg += 'fill="#e8f4f8" stroke="#0d7a99" stroke-width="2" rx="4"/>\n'
            svg += f'  <text x="{x+10}" y="{y+25}" font-weight="bold" font-size="14">{package.name}</text>\n'
            svg += f'  <text x="{x+10}" y="{y+45}" font-size="11" fill="#555">{package.path}</text>\n'

            # Dependencies count
            dep_count = len(package.internal_dependencies)
            if dep_count > 0:
                svg += f'  <text x="{x+10}" y="{y+65}" font-size="10" fill="#999">→ {dep_count} deps</text>\n'

            svg += '</g>\n'

        # Draw dependency lines
        for idx, package in enumerate(packages):
            from_row = idx // cols
            from_col = idx % cols
            from_x = from_col * cell_width + 10 + (cell_width - 20) // 2
            from_y = from_row * cell_height + 90

            for dep in package.internal_dependencies:
                if dep in graph.packages:
                    dep_idx = list(graph.packages.keys()).index(dep)
                    to_row = dep_idx // cols
                    to_col = dep_idx % cols
                    to_x = to_col * cell_width + 10 + (cell_width - 20) // 2
                    to_y = to_row * cell_height + 10

                    svg += f'<line x1="{from_x}" y1="{from_y}" x2="{to_x}" y2="{to_y}" '
                    svg += 'stroke="#666" stroke-width="1" stroke-dasharray="4" opacity="0.6"/>\n'

        svg += '</svg>\n'
        return svg

    def generate_ascii_tree(self, graph: DepGraph) -> str:
        """Generate ASCII tree visualization."""
        if not graph.packages:
            return ""

        # Find root packages (no internal dependencies from others)
        all_deps = set()
        for pkg in graph.packages.values():
            all_deps.update(pkg.internal_dependencies)

        roots = [
            name for name in graph.packages.keys()
            if name not in all_deps
        ]

        if not roots:
            roots = list(graph.packages.keys())[:1]

        output = "Dependency Tree:\n"
        output += "================\n\n"

        visited = set()

        def add_tree_node(name: str, prefix: str = "", is_last: bool = True) -> None:
            if name in visited:
                output_str = f"{prefix}{'└── ' if is_last else '├── '}{name} (circular)\n"
                return

            visited.add(name)

            pkg = graph.packages.get(name)
            if not pkg:
                return

            nonlocal output
            output += f"{prefix}{'└── ' if is_last else '├── '}{name}\n"

            if pkg.internal_dependencies:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for i, dep in enumerate(pkg.internal_dependencies):
                    is_last_dep = i == len(pkg.internal_dependencies) - 1
                    add_tree_node(dep, new_prefix, is_last_dep)

        for i, root in enumerate(roots):
            is_last = i == len(roots) - 1
            add_tree_node(root, "", is_last)

        return output

    def generate_graphql_query(self, graph: DepGraph) -> str:
        """Generate GraphQL representation of dependency graph."""
        query = "{\n  packages {\n"

        for name, pkg in graph.packages.items():
            query += f"    {name} {{\n"
            query += f'      path: "{pkg.path}"\n'

            if pkg.internal_dependencies:
                query += f"      dependsOn: [{', '.join(pkg.internal_dependencies)}]\n"

            query += "    }\n"

        query += "  }\n}\n"
        return query

    def get_circular_dependencies(self, graph: DepGraph) -> List[List[str]]:
        """Detect circular dependencies."""
        cycles = []
        visited = set()

        def dfs(node: str, path: List[str]) -> None:
            if node in path:
                cycle = path[path.index(node):] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            pkg = graph.packages.get(node)

            if pkg:
                for dep in pkg.internal_dependencies:
                    dfs(dep, path + [node])

        for pkg_name in graph.packages:
            dfs(pkg_name, [])

        return cycles
