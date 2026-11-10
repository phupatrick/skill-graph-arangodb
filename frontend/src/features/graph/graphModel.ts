import { getCatalogRepository } from "../../repositories/catalogRepository";
import type { GraphData } from "../../types/catalog";
const repo = getCatalogRepository();
export function displayName(value: unknown, id: string) {
  const text = typeof value === "string" ? value.trim() : "";
  if (text && !/^[-–—]+$/.test(text)) return { label: text, fallback: false };
  const key = id.includes("/") ? id.split("/").pop()! : id;
  return { label: `[Thiếu tên] ${key}`, fallback: true };
}
export function mergeExpandedGraph(
  base: GraphData,
  expanded: Set<string>,
): GraphData {
  const nodes = new Map(base.nodes.map((n) => [n.id, n])),
    edges = new Map(base.edges.map((e) => [e.id, e]));
  for (const id of expanded) {
    if (id.startsWith("skills/"))
      for (const { course, evidence } of repo.getCoursesForSkill(id)) {
        nodes.set(course.id, {
          id: course.id,
          type: "course",
          label: course.title,
        });
        const edgeId = `expanded-teaches-${course.key}-${id.split("/")[1]}`;
        edges.set(edgeId, {
          id: edgeId,
          source: course.id,
          target: id,
          type: "teaches",
          data: evidence,
        });
      }
    if (id.startsWith("courses/")) {
      const graph = repo.getGraphForCourse(id);
      graph.nodes
        .filter((n) => n.type === "provider")
        .forEach((n) => nodes.set(n.id, n));
      graph.edges
        .filter((e) => e.type === "offered_by")
        .forEach((e) => edges.set(e.id, e));
    }
    if (id.startsWith("skill_groups/")) {
      const graph = repo.getTaxonomyGraph(id);
      graph.nodes.forEach((node) => nodes.set(node.id, node));
      graph.edges.forEach((edge) => edges.set(edge.id, edge));
    }
  }
  return { nodes: [...nodes.values()], edges: [...edges.values()] };
}
export function prioritizeGraph(
  data: GraphData,
  focus: string,
  expanded: Set<string>,
  limit: number,
) {
  const expandedNeighbors = new Set<string>(),
    focusNeighbors = new Set<string>([focus]);
  for (const e of data.edges) {
    if (expanded.has(e.source) || expanded.has(e.target)) {
      expandedNeighbors.add(e.source);
      expandedNeighbors.add(e.target);
    }
    if (e.source === focus || e.target === focus) {
      focusNeighbors.add(e.source);
      focusNeighbors.add(e.target);
    }
  }
  return data.nodes
    .map((node, index) => ({
      node,
      index,
      score:
        node.id === focus
          ? 10000
          : expanded.has(node.id)
            ? 9000
            : expandedNeighbors.has(node.id)
              ? 8000
              : focusNeighbors.has(node.id)
                ? 5000
                : 0,
    }))
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .slice(0, limit)
    .map((x) => x.node);
}
export function collapseBranch(expanded: Set<string>, id: string) {
  const next = new Set(expanded);
  next.delete(id);
  if (!id.startsWith("skills/")) return next;
  const related = new Set(repo.getCoursesForSkill(id).map((x) => x.course.id)),
    shared = new Set<string>();
  for (const other of next)
    if (other.startsWith("skills/"))
      repo.getCoursesForSkill(other).forEach((x) => shared.add(x.course.id));
  related.forEach((courseId) => {
    if (!shared.has(courseId)) next.delete(courseId);
  });
  return next;
}
