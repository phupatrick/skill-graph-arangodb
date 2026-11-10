import { describe, expect, it } from "vitest";
import { getCatalogRepository } from "../repositories/catalogRepository";
import {
  collapseBranch,
  displayName,
  mergeExpandedGraph,
  prioritizeGraph,
} from "../features/graph/graphModel";
import { calculateEssentialSelfDeclaration } from "../features/skillGap/skillGapModel";
import { validExternalHttpUrl } from "../utils/externalUrl";
const repo = getCatalogRepository();
describe("v3.55 catalog repository", () => {
  it("uses the correct release and core counts", () => {
    expect(repo.getReleaseInfo()).toMatchObject({
      version: "v3.55",
      sprint: 92,
      records: 5718,
    });
    expect(repo.getCareers()).toHaveLength(12);
    expect(repo.getSkills()).toHaveLength(420);
    expect(repo.getSkillGroups()).toHaveLength(149);
    expect(repo.getCourses()).toHaveLength(504);
    expect(repo.getProviders()).toHaveLength(179);
  });
  it("preserves Data Analyst requirements", () => {
    const c = repo.getCareers().find((x) => x.name === "data analyst")!;
    const r = repo.getCareerRequirements(c.id);
    expect(r.filter((x) => x.requirementType === "essential")).toHaveLength(36);
    expect(r.filter((x) => x.requirementType === "optional")).toHaveLength(31);
  });
  it("reports 323/343 direct topic coverage", () => {
    const rows = repo.getCoverageReport();
    expect(rows.reduce((n, x) => n + x.essential, 0)).toBe(343);
    expect(rows.reduce((n, x) => n + x.covered, 0)).toBe(323);
    expect(repo.getRemainingEssentialGaps()).toHaveLength(20);
  });
});
describe("focused graphs", () => {
  it("keeps Career to Skill direction", () => {
    const career = repo.getCareers()[0],
      graph = repo.getGraphForCareer(career.id);
    expect(graph.nodes.length).toBeGreaterThan(1);
    expect(
      graph.edges.every(
        (x) => x.source === career.id && x.target.startsWith("skills/"),
      ),
    ).toBe(true);
  });
  it("builds skill, resource and taxonomy neighborhoods", () => {
    const skill = repo
      .getSkills()
      .find((x) => repo.getCoursesForSkill(x.id).length > 0)!;
    expect(repo.getGraphForSkill(skill.id).edges.length).toBeGreaterThan(0);
    const course = repo
      .getCourses()
      .find((x) => repo.getSkillsForCourse(x.id).length > 0)!;
    expect(repo.getGraphForCourse(course.id).edges.length).toBeGreaterThan(0);
    const group = repo
      .getSkillGroups()
      .find((x) => repo.getSkillsInGroup(x.id).length > 0)!;
    expect(repo.getTaxonomyGraph(group.id).edges.length).toBeGreaterThan(0);
  });
  it("matches the Sprint 92 Ansible cases and preserves edge directions", () => {
    const ansible = repo
        .getSkills()
        .find((x) => x.name.toLowerCase() === "ansible")!,
      software = repo
        .getCareers()
        .find((x) => x.name.toLowerCase() === "software developer")!,
      web = repo
        .getCareers()
        .find((x) => x.name.toLowerCase() === "web developer")!,
      course = repo
        .getCourses()
        .find(
          (x) => x.title.toLowerCase() === "start automating with ansible",
        )!,
      provider = repo
        .getProviders()
        .find((x) => x.name.toLowerCase() === "ansible community")!;

    for (const career of [software, web]) {
      expect(
        repo
          .getGraphForCareer(career.id)
          .edges.some(
            (edge) =>
              edge.type === "requires_skill" &&
              edge.source === career.id &&
              edge.target === ansible.id,
          ),
      ).toBe(true);
    }
    const courseGraph = repo.getGraphForCourse(course.id);
    expect(
      courseGraph.edges.some(
        (edge) =>
          edge.type === "teaches" &&
          edge.source === course.id &&
          edge.target === ansible.id,
      ),
    ).toBe(true);
    expect(
      courseGraph.edges.some(
        (edge) =>
          edge.type === "offered_by" &&
          edge.source === course.id &&
          edge.target === provider.id,
      ),
    ).toBe(true);
  });
  it("uses only stored ESCO membership and broader relations", () => {
    const group = repo
        .getSkillGroups()
        .find(
          (x) =>
            x.name.toLowerCase() ===
            "interpreting technical documentation and diagrams",
        )!,
      graph = repo.getTaxonomyGraph(group.id),
      memberships = graph.edges.filter(
        (edge) => edge.type === "esco_skill_group" && edge.target === group.id,
      ),
      broader = graph.edges.filter(
        (edge) =>
          edge.type === "esco_group_broader" && edge.source === group.id,
      );
    expect(memberships).toHaveLength(2);
    expect(memberships.every((edge) => edge.source.startsWith("skills/"))).toBe(
      true,
    );
    expect(broader).toHaveLength(1);
    expect(broader[0].target.startsWith("skill_groups/")).toBe(true);
  });
});
describe("graph expansion model", () => {
  it("expands Java with its real teaches neighbor and prioritizes it under limit", () => {
    const java = repo
      .getSkills()
      .find((x) => x.name === "Java (computer programming)")!;
    const career = repo.getCareersForSkill(java.id)[0].career,
      base = repo.getGraphForCareer(career.id),
      expanded = mergeExpandedGraph(base, new Set([java.id])),
      courses = repo.getCoursesForSkill(java.id);
    expect(courses).toHaveLength(1);
    expect(expanded.nodes.some((x) => x.id === courses[0].course.id)).toBe(
      true,
    );
    expect(
      expanded.edges.some(
        (x) =>
          x.source === courses[0].course.id &&
          x.target === java.id &&
          x.type === "teaches",
      ),
    ).toBe(true);
    expect(
      prioritizeGraph(expanded, career.id, new Set([java.id]), 30).some(
        (x) => x.id === courses[0].course.id,
      ),
    ).toBe(true);
  });
  it("collapses one branch without removing another expanded branch", () => {
    const skills = repo
        .getSkills()
        .filter((x) => repo.getCoursesForSkill(x.id).length > 0)
        .slice(0, 2),
      set = new Set(skills.map((x) => x.id));
    const next = collapseBranch(set, skills[0].id);
    expect(next.has(skills[0].id)).toBe(false);
    expect(next.has(skills[1].id)).toBe(true);
  });
  it("maps valid names and reports a meaningful fallback", () => {
    expect(displayName("Java (computer programming)", "skills/java")).toEqual({
      label: "Java (computer programming)",
      fallback: false,
    });
    expect(displayName("-", "skills/missing")).toEqual({
      label: "[Thiếu tên] missing",
      fallback: true,
    });
  });
  it("keeps teaches and offered_by directions", () => {
    const course = repo
        .getCourses()
        .find((x) => repo.getSkillsForCourse(x.id).length > 0)!,
      graph = repo.getGraphForCourse(course.id);
    expect(
      graph.edges
        .filter((x) => x.type === "teaches")
        .every((x) => x.source === course.id && x.target.startsWith("skills/")),
    ).toBe(true);
    expect(
      graph.edges
        .filter((x) => x.type === "offered_by")
        .every(
          (x) => x.source === course.id && x.target.startsWith("providers/"),
        ),
    ).toBe(true);
  });
  it("expands a taxonomy group with real neighboring nodes and edges", () => {
    const root = repo.getSkillGroups()[0],
      base: ReturnType<typeof repo.getTaxonomyGraph> = {
        nodes: [{ id: root.id, type: "skillGroup", label: root.name }],
        edges: [],
      },
      expanded = mergeExpandedGraph(base, new Set([root.id])),
      expected = repo.getTaxonomyGraph(root.id);
    expect(expanded.nodes).toHaveLength(expected.nodes.length);
    expect(expanded.edges).toHaveLength(expected.edges.length);
    expect(
      expanded.edges.every((edge) =>
        expected.edges.some((x) => x.id === edge.id),
      ),
    ).toBe(true);
  });
});

describe("skill gap self-declaration", () => {
  it("uses the ID intersection of Essential skills only", () => {
    const result = calculateEssentialSelfDeclaration(
      [
        { requirementType: "essential", skill: { id: "skills/a" } },
        { requirementType: "essential", skill: { id: "skills/b" } },
        { requirementType: "optional", skill: { id: "skills/c" } },
      ],
      ["skills/a", "skills/c", "skills/outside"],
    );

    expect(result.essentialSkillIds).toEqual(["skills/a", "skills/b"]);
    expect(result.declaredEssentialSkillIds).toEqual(["skills/a"]);
    expect(result.missingEssentialSkillIds).toEqual(["skills/b"]);
    expect(result.percentage).toBe(50);
  });

  it("deduplicates IDs in requirements and declarations", () => {
    const result = calculateEssentialSelfDeclaration(
      [
        { requirementType: "essential", skill: { id: "skills/a" } },
        { requirementType: "essential", skill: { id: "skills/a" } },
      ],
      ["skills/a", "skills/a"],
    );

    expect(result.essentialSkillIds).toHaveLength(1);
    expect(result.declaredEssentialSkillIds).toHaveLength(1);
    expect(result.percentage).toBe(100);
  });
});

describe("external resource URLs", () => {
  it("accepts only absolute HTTP and HTTPS source URLs", () => {
    expect(validExternalHttpUrl("https://example.com/course")).toBe(
      "https://example.com/course",
    );
    expect(validExternalHttpUrl("http://example.com/course")).toBe(
      "http://example.com/course",
    );
    expect(validExternalHttpUrl("javascript:alert(1)")).toBeNull();
    expect(validExternalHttpUrl("/invented-source")).toBeNull();
    expect(validExternalHttpUrl("")).toBeNull();
  });
});
