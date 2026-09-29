/* @index-begin
 * @symbol type: Role L14
 * @symbol type: Session L15
 * @symbol type: Bootstrap L21
 * @symbol type: Product L28
 * @symbol type: Measurement L36
 * @symbol type: Doc L42
 * @symbol type: DocumentResult L49
 * @symbol type: Report L59
 * @symbol type: Config L72
 * @symbol type: Answer L83
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
}
export interface Report {
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
