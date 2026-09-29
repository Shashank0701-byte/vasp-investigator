"use client";
import { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  type Analysis,
  type Candidate,
  type GraphNode,
  type Transaction,
  short,
  money,
} from "@/lib/types";

const colors: Record<string, string> = {
  target: "#6959de",
  wallet: "#71839b",
  vasp: "#159575",
  exchange: "#159575",
  mixer: "#d89126",
  bridge: "#497dcc",
  dex: "#497dcc",
  scam: "#da5e5e",
  sanctioned: "#da5e5e",
};
export default function FlowGraph({
  analysis,
  candidate,
  onSelect,
}: {
  analysis: Analysis;
  candidate: Candidate | null;
  onSelect: (item: GraphNode | Transaction) => void;
}) {
  const [hops, setHops] = useState(analysis.max_hops);
  const [minimum, setMinimum] = useState(0);
  const [date, setDate] = useState("");
  const [kind, setKind] = useState("all");
  const [risky, setRisky] = useState(false);
  const [expanded, setExpanded] = useState<string[]>([]);
  const highlighted = new Set(candidate?.paths.flat() || []);
  const { nodes, edges } = useMemo(() => {
    const extras = new Set(
      analysis.graph.edges
        .filter((t) => expanded.includes(t.from_address))
        .map((t) => t.to_address),
    );
    const eligible = analysis.graph.nodes.filter(
      (n) =>
        (n.hop <= hops || extras.has(n.id)) &&
        (kind === "all" || n.type === kind || n.type === "target"),
    );
    const ids = new Set(eligible.map((n) => n.id));
    const txs = analysis.graph.edges.filter(
      (t) =>
        ids.has(t.from_address) &&
        ids.has(t.to_address) &&
        (minimum === 0 ||
          (t.usd_value !== null && Number(t.usd_value) >= minimum)) &&
        (!date || t.timestamp.slice(0, 10) >= date),
    );
    const connected = new Set(
      txs.flatMap((t) => [t.from_address, t.to_address]),
    );
    const columns: Record<number, number> = {};
    const counts: Record<number, number> = {};
    const shown = eligible.filter(
      (n) => n.type === "target" || connected.has(n.id),
    );
    shown.forEach((n) => {
      counts[n.hop] = (counts[n.hop] || 0) + 1;
    });
    const nodes: Node[] = shown.map((n) => {
      const row = columns[n.hop] || 0;
      columns[n.hop] = row + 1;
      const color = colors[n.type] || colors.wallet;
      const isRisk = ["mixer", "bridge", "scam", "sanctioned"].includes(n.type);
      return {
        id: n.id,
        position: {
          x: (n.hop + 1) * 235,
          y: row * 120 - (counts[n.hop] - 1) * 60 + 200,
        },
        data: {
          label: (
            <div className="flow-node">
              <span className="node-kind" style={{ color }}>
                {n.type === "target"
                  ? "INVESTIGATED WALLET"
                  : n.type.toUpperCase()}
              </span>
              <strong>{n.type === "wallet" ? short(n.id) : n.label}</strong>
              <span>
                {short(n.id)} <b>↗</b>
              </span>
            </div>
          ),
        },
        sourcePosition: "right" as Node["sourcePosition"],
        targetPosition: "left" as Node["targetPosition"],
        style: {
          border: `1.5px solid ${color}`,
          background: "#fff",
          borderRadius: 10,
          width: 185,
          boxShadow:
            risky && isRisk ? `0 0 0 5px ${color}25` : "0 3px 12px #1a294309",
          opacity: risky && !isRisk && n.type !== "target" ? 0.45 : 1,
        },
      };
    });
    const edges: Edge[] = txs.map((t) => ({
      id: t.id,
      source: t.from_address,
      target: t.to_address,
      label:
        t.usd_value === null
          ? `${t.amount} ${t.asset}`
          : money(Number(t.usd_value)),
      animated: highlighted.has(t.id),
      style: {
        stroke: highlighted.has(t.id) ? "#6c5ce7" : "#bdc7d7",
        strokeWidth: highlighted.has(t.id) ? 2.5 : 1.4,
        opacity: candidate && !highlighted.has(t.id) ? 0.3 : 1,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: highlighted.has(t.id) ? "#6c5ce7" : "#bdc7d7",
      },
      labelStyle: { fontSize: 10, fill: "#66758a" },
      labelBgStyle: { fill: "#fbfcfe" },
      labelBgPadding: [6, 4],
    }));
    return { nodes, edges };
  }, [analysis, hops, minimum, date, kind, risky, expanded, candidate]); // highlight follows the selected candidate
  return (
    <>
      <div className="graph-toolbar">
        <label>
          Depth{" "}
          <select
            aria-label="Graph hop depth"
            value={hops}
            onChange={(e) => {
              setHops(Number(e.target.value));
              setExpanded([]);
            }}
          >
            {Array.from({ length: analysis.max_hops }, (_, i) => (
              <option key={i} value={i + 1}>
                {i + 1} hops
              </option>
            ))}
          </select>
        </label>
        <label>
          Min. USD{" "}
          <input
            aria-label="Minimum transfer value"
            type="number"
            min="0"
            value={minimum}
            onChange={(e) => setMinimum(Math.max(0, Number(e.target.value)))}
          />
        </label>
        <label>
          From{" "}
          <input
            aria-label="Graph start date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </label>
        <select
          aria-label="Entity type"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          <option value="all">All entities</option>
          <option value="vasp">VASPs</option>
          <option value="wallet">Wallets</option>
          <option value="mixer">Mixers</option>
          <option value="bridge">Bridges</option>
        </select>
        <button
          className={risky ? "chip active" : "chip"}
          onClick={() => setRisky(!risky)}
        >
          Risk highlights
        </button>
      </div>
      <div className="flow-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          fitViewOptions={{ padding: 0.15 }}
          minZoom={0.2}
          maxZoom={2}
          nodesDraggable={false}
          onNodeClick={(_, n) => {
            const item = analysis.graph.nodes.find((x) => x.id === n.id);
            if (item) onSelect(item);
          }}
          onNodeDoubleClick={(_, n) => setExpanded((v) => [...v, n.id])}
          onEdgeClick={(_, e) => {
            const item = analysis.transactions.find((t) => t.id === e.id);
            if (item) onSelect(item);
          }}
          proOptions={{ hideAttribution: false }}
        >
          <Background color="#dce2ed" gap={22} />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(n) =>
              colors[
                analysis.graph.nodes.find((x) => x.id === n.id)?.type ||
                  "wallet"
              ] || "#aaa"
            }
            pannable
            zoomable
          />
        </ReactFlow>
      </div>
      <div className="graph-legend">
        <span>
          <i style={{ background: colors.target }} />
          Target
        </span>
        <span>
          <i style={{ background: colors.wallet }} />
          Wallet
        </span>
        <span>
          <i style={{ background: colors.vasp }} />
          VASP
        </span>
        <span>
          <i style={{ background: colors.mixer }} />
          Mixer
        </span>
        <span>
          <i style={{ background: colors.bridge }} />
          Bridge
        </span>
        <small>
          Click for evidence · Double-click to expand loaded neighbors
        </small>
      </div>
    </>
  );
}
