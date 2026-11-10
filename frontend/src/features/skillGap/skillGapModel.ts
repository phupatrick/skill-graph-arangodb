type SkillRequirementRef = {
  requirementType: "essential" | "optional";
  skill: { id: string };
};

export function calculateEssentialSelfDeclaration(
  requirements: SkillRequirementRef[],
  declaredSkillIds: string[],
) {
  const essentialSkillIds = [
      ...new Set(
        requirements
          .filter((item) => item.requirementType === "essential")
          .map((item) => item.skill.id),
      ),
    ],
    essentialSet = new Set(essentialSkillIds),
    declaredSet = new Set(declaredSkillIds),
    declaredEssentialSkillIds = [...declaredSet].filter((id) =>
      essentialSet.has(id),
    ),
    missingEssentialSkillIds = essentialSkillIds.filter(
      (id) => !declaredSet.has(id),
    ),
    percentage = essentialSkillIds.length
      ? (declaredEssentialSkillIds.length / essentialSkillIds.length) * 100
      : 0;

  return {
    essentialSkillIds,
    declaredEssentialSkillIds,
    missingEssentialSkillIds,
    percentage,
  };
}
