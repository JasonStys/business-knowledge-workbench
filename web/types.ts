/* @index-begin
 * @symbol type: Role L15
 * @symbol type: Session L16
 * @symbol type: Bootstrap L22
 * @symbol type: Product L29
 * @symbol type: Measurement L37
 * @symbol type: Doc L43
 * @symbol type: DocumentResult L50
 * @symbol type: OutputStandard L66
 * @symbol type: Report L87
 * @symbol type: Config L106
 * @symbol type: Answer L118
@index-end */
/** Shared browser API shapes. Functions/variables and exact lines: docs/code-index.md. */
export type Role = "customer" | "employee" | "admin";
export interface Session {
  username: string;
  role: Role;
  workspace: string;
  csrf: string;
}
export interface Bootstrap {
  demo: boolean;
  workspaces: { id: string; title: string; context: string }[];
  formats: string[];
  exports: string[];
  units: Record<string, string[]>;
}
export interface Product {
  id: string;
  name: string;
  category: string;
  description: string;
  price_cents: number;
  specifications: Measurement[];
}
export interface Measurement {
  original: string;
  value: string;
  unit: string;
  dimension: string;
}
export interface Doc {
  id: string;
  title: string;
  visibility: string;
  category: string;
  review_status: string;
}
export interface DocumentResult {
  title: string;
  html: string;
  text: string;
  blocks: { kind: string; text?: string; review?: string }[];
  measurements: Measurement[];
  warnings: string[];
  provenance: Record<string, unknown>;
  review_status: string;
  standard?: {
    name: string;
    revision: number;
    sha256: string;
    output_standard: OutputStandard;
  };
}
export interface OutputStandard {
  name: string;
  section_titles: Record<string, string>;
  default_export: "html" | "json" | "md" | "csv" | "docx" | "pdf";
  enforce_export: boolean;
  paper: "Letter" | "A4";
  orientation: "portrait" | "landscape";
  font: "sans" | "serif" | "mono";
  font_size: number;
  accent: string;
  columns: {
    key: string;
    label: string;
    aliases: string[];
    dimension?: string | null;
    source_unit?: string | null;
    required: boolean;
  }[];
  extra_columns: "preserve" | "reject";
  table_scope: "matching" | "all";
}
export interface Report {
  standard: {
    name: string;
    revision: number;
    default_export: string;
    enforce_export: boolean;
  };
  currency: string;
  series: { month: string; quantity: number; revenue_cents: number }[];
  revenue_cents: number;
  quantity: number;
  forecast: {
    month_offset: number;
    revenue_cents: number;
    low_cents: number;
    high_cents: number;
  }[];
  method: string;
}
export interface Config {
  output_standard: OutputStandard;
  title: string;
  profile: string;
  customers: Record<string, string>;
  units: Record<string, string>;
  sections: string[];
  forecasting: boolean;
  ai_enabled: boolean;
  data_columns: Record<string, string>;
  revision: number;
}
export interface Answer {
  answer: string;
  citations: string[];
  provider: string;
  notice: string;
}
