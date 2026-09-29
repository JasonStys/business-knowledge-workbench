-- @index-begin
-- @symbol schema: workspaces L15
-- @symbol schema: users L16
-- @symbol schema: sessions L21
-- @symbol schema: products L24
-- @symbol schema: sales L29
-- @symbol schema: sales_scope L34
-- @symbol schema: sales_imports L35
-- @symbol schema: documents L36
-- @symbol schema: documents_scope L42
-- @symbol schema: audit L43
-- @index-end
-- Relational records, scoped documents and auditable events. Index: docs/code-index.md.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS workspaces (id TEXT PRIMARY KEY, config TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, workspace TEXT NOT NULL REFERENCES workspaces(id),
 username TEXT NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('customer','employee','admin')),
 customer TEXT, UNIQUE(workspace,username)
);
CREATE TABLE IF NOT EXISTS sessions (
 token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), csrf TEXT NOT NULL, expires REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
 id TEXT NOT NULL, workspace TEXT NOT NULL REFERENCES workspaces(id), name TEXT NOT NULL,
 category TEXT NOT NULL, description TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
 customer TEXT NOT NULL, specifications TEXT NOT NULL, PRIMARY KEY(workspace,id)
);
CREATE TABLE IF NOT EXISTS sales (
 id INTEGER PRIMARY KEY, workspace TEXT NOT NULL, product TEXT NOT NULL, customer TEXT NOT NULL,
 month TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>=0), revenue_cents INTEGER NOT NULL CHECK(revenue_cents>=0),
 FOREIGN KEY(workspace,product) REFERENCES products(workspace,id)
);
CREATE INDEX IF NOT EXISTS sales_scope ON sales(workspace,customer,month);
CREATE TABLE IF NOT EXISTS sales_imports(workspace TEXT NOT NULL, source_hash TEXT NOT NULL, PRIMARY KEY(workspace,source_hash));
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY, workspace TEXT NOT NULL REFERENCES workspaces(id), title TEXT NOT NULL,
 visibility TEXT NOT NULL CHECK(visibility IN ('public','customer','internal')), customer TEXT,
 product TEXT, category TEXT NOT NULL DEFAULT 'General', result TEXT NOT NULL, source BLOB,
 source_hash TEXT, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS documents_scope ON documents(workspace,visibility,customer);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY, workspace TEXT NOT NULL, actor TEXT NOT NULL, event TEXT NOT NULL,
 detail TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
PRAGMA user_version = 1;
