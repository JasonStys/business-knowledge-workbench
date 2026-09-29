/* @index-begin
 * @symbol variable/parameter: file L12
 * @symbol variable/parameter: source L13
 * @symbol variable/parameter: records L19
 * @symbol variable/parameter: node L21
 * @symbol function/class: visit L21
 * @symbol variable/parameter: line L22
@index-end */
/** Parse TypeScript/JavaScript symbols for documentation without executing source. Index: docs/code-index.md. */
import ts from "typescript";
import { readFileSync } from "node:fs";
const file = process.argv[2];
const source = ts.createSourceFile(
  file,
  readFileSync(0, "utf8"),
  ts.ScriptTarget.Latest,
  true,
);
const records = [];
/** Recursively record declarations and parameter names using compiler source locations. */
function visit(node) {
  const line =
    source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
  if (
    ts.isFunctionDeclaration(node) ||
    ts.isClassDeclaration(node) ||
    ts.isMethodDeclaration(node) ||
    ts.isInterfaceDeclaration(node) ||
    ts.isTypeAliasDeclaration(node)
  )
    records.push({
      kind:
        ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node)
          ? "type"
          : "function/class",
      name: node.name?.getText(source) || "<anonymous>",
      line,
    });
  if (ts.isVariableDeclaration(node) || ts.isParameter(node))
    records.push({
      kind: "variable/parameter",
      name: node.name.getText(source).replace(/\s+/g, " "),
      line,
    });
  ts.forEachChild(node, visit);
}
visit(source);
process.stdout.write(JSON.stringify(records));
