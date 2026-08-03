---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# TransGraspNet: Physically and Geometrically Consistent Manipulation of Transparent Labware

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29567v1](https://arxiv.org/abs/2607.29567v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Manipulating transparent laboratory glassware that contains liquid is inherently safety-critical: even small geometric errors can cause unstable grasps and hazardous spillage. Although recent progress has been made in transparent object perception and robotic grasping, most existing systems optimize detection, depth reconstruction, and grasp planning independently, which leads to cross-stage inconsistency imperfect boundaries induce depth bleeding, distorted surfaces corrupt normal estimation, and task agnostic grasp scoring yields tilted or off-center grasps that fail under dynamic motion. In this paper, we propose TransGraspNet, a geometry physics consistent framework that explicitly enforces consistency from perception to execution through three coupled principles: boundary consistency to produce structurally reliable object contours as downstream priors, surface consistency to preserve geometric fidelity and surface normal accuracy during depth reconstruction, and physics consistency to refine grasp selection with centroid alignment and wrench-space stability for upright and dynamically robust manipulation. We evaluate TransGraspNet on public benchmarks, a dedicated transparent glassware dataset, and a real robotic platform. The results show improved boundary quality and surface normal fidelity, and demonstrate strong task-level performance in cluttered transparent scenes. Most importantly, the proposed system achieves reliable real-world operation, including high grasp success rates in clutter and zero spillage during high speed liquid transport, highlighting the effectiveness of our method.

## My Notes
