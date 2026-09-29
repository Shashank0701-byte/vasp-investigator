export type Transaction = {
  id: string;
  tx_hash: string;
  chain: string;
  block_number: number;
  timestamp: string;
  from_address: string;
  to_address: string;
  asset: string;
  amount: string;
  usd_value: string | null;
  direction: string;
  source: string;
  source_confidence: number;
  contract_address: string | null;
};
export type Label = {
  address: string;
  entity: string;
  entity_type: string;
  confidence: number;
  strength: string;
  source: string;
  source_reliability: number;
  observed_at: string;
  synthetic: boolean;
};
export type GraphNode = {
  id: string;
  label: string;
  type: string;
  hop: number;
  metadata: Label | null;
  in_degree: number;
  out_degree: number;
};
export type Candidate = {
  entity: string;
  score: number;
  traced_usd: number;
  value_share: number;
  shortest_hops: number;
  median_hops: number;
  independent_paths: number;
  path_count: number;
  interaction_count: number;
  addresses: string[];
  paths: string[][];
  last_seen: string;
  quality_cap: number;
  labels: Label[];
  components: Record<string, { value: number; weight: number; points: number }>;
};
export type Analysis = {
  target: string;
  chain: string;
  mode: string;
  max_hops: number;
  model_version: string;
  period: { start: string | null; end: string | null };
  graph: {
    nodes: GraphNode[];
    edges: Transaction[];
    connected_components: number;
  };
  transactions: Transaction[];
  candidates: Candidate[];
  risk: {
    score: number;
    factors: {
      name: string;
      points: number;
      evidence_ids: string[];
      explanation: string;
    }[];
  };
  metrics: Record<string, number | null>;
  limitations: string[];
};
export type Case = {
  id: string;
  title: string;
  created_at: string;
  evidence_digest: string;
  analysis: Analysis;
};
export type CaseSummary = {
  id: string;
  title: string;
  target: string;
  chain: string;
  mode: string;
  created_at: string;
};
export const short = (s: string) => `${s.slice(0, 6)}…${s.slice(-4)}`;
export const money = (n: number | null | undefined) =>
  n == null
    ? "Unavailable"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(n);
export const time = (s: string) =>
  new Date(s).toLocaleString("en-GB", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }) + " UTC";
