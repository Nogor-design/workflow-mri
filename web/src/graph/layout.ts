import type { ProcessEdge, WorkflowStep } from "../bundle/types";

// Deterministic swimlane layout. Lanes = owner roles (ordered by first appearance);
// columns = sequence_index. Same Bundle → same coordinates → same pixels.

export const NODE_W = 158;
export const NODE_H = 66;
const COL_W = 212;
const LANE_H = 112;
const PAD_X = 150; // room for lane labels
const PAD_Y = 44;

export interface PositionedNode {
  step: WorkflowStep;
  x: number;
  y: number;
  cx: number;
  cy: number;
}

export interface Lane {
  role: string;
  index: number;
  y: number;
}

export interface GraphLayout {
  nodes: Map<string, PositionedNode>;
  lanes: Lane[];
  width: number;
  height: number;
}

export function computeLayout(steps: WorkflowStep[]): GraphLayout {
  const laneOrder: string[] = [];
  for (const s of [...steps].sort((a, b) => a.sequence_index - b.sequence_index)) {
    if (!laneOrder.includes(s.owner_role)) laneOrder.push(s.owner_role);
  }
  const lanes: Lane[] = laneOrder.map((role, index) => ({
    role,
    index,
    y: PAD_Y + index * LANE_H,
  }));

  const nodes = new Map<string, PositionedNode>();
  let maxCol = 0;
  for (const step of steps) {
    const col = step.sequence_index;
    maxCol = Math.max(maxCol, col);
    const laneIndex = laneOrder.indexOf(step.owner_role);
    const x = PAD_X + col * COL_W;
    const y = PAD_Y + laneIndex * LANE_H + (LANE_H - NODE_H) / 2;
    nodes.set(step.id, { step, x, y, cx: x + NODE_W / 2, cy: y + NODE_H / 2 });
  }

  return {
    nodes,
    lanes,
    width: PAD_X + (maxCol + 1) * COL_W,
    height: PAD_Y * 2 + lanes.length * LANE_H,
  };
}

// SVG path for an edge, shaped by kind. Forward edges flow left→right; loops arc below;
// bypass arcs above; duplicates run parallel and dashed.
export function edgePath(edge: ProcessEdge, layout: GraphLayout): string {
  const a = layout.nodes.get(edge.from_step);
  const b = layout.nodes.get(edge.to_step);
  if (!a || !b) return "";

  if (edge.kind === "loop") {
    const sx = a.x + NODE_W / 2;
    const ex = b.x + NODE_W / 2;
    const yb = Math.max(a.y, b.y) + NODE_H;
    const dip = yb + 56;
    return `M ${sx} ${a.y + NODE_H} C ${sx} ${dip}, ${ex} ${dip}, ${ex} ${b.y + NODE_H}`;
  }
  if (edge.kind === "bypass") {
    const sx = a.cx;
    const ex = b.cx;
    const top = Math.min(a.y, b.y) - 46;
    return `M ${sx} ${a.y} C ${sx} ${top}, ${ex} ${top}, ${ex} ${b.y}`;
  }

  // forward / exception / duplicate
  const sx = a.x + NODE_W;
  const sy = a.cy;
  const ex = b.x;
  const ey = b.cy;
  const dupOffset = edge.kind === "duplicate" ? 26 : 0;
  const mx = (sx + ex) / 2;
  return `M ${sx} ${sy} C ${mx} ${sy + dupOffset}, ${mx} ${ey + dupOffset}, ${ex} ${ey}`;
}
