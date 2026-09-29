# @index-begin
# @symbol variable/parameter: SCENARIOS L63
# @symbol variable/parameter: password L160
# @symbol function/class: password_hash L160
# @symbol variable/parameter: salt L160
# @symbol variable/parameter: digest L163
# @symbol variable/parameter: encoded L167
# @symbol function/class: verify_password L167
# @symbol function/class: connect L174
# @symbol variable/parameter: path L174
# @symbol variable/parameter: database L176
# @symbol variable/parameter: demo L186
# @symbol function/class: initialize L186
# @symbol variable/parameter: version L190
# @symbol variable/parameter: scenario L194
# @symbol variable/parameter: config L195
# @symbol variable/parameter: role L201
# @symbol variable/parameter: username L201
# @symbol variable/parameter: customer L218
# @symbol variable/parameter: description L218
# @symbol variable/parameter: name L218
# @symbol variable/parameter: price L218
# @symbol variable/parameter: product_id L218
# @symbol variable/parameter: specifications L218
# @symbol variable/parameter: normalized L221
# @symbol variable/parameter: month L237
# @symbol variable/parameter: quantity L238
# @symbol variable/parameter: suffix L250
# @symbol variable/parameter: text L250
# @symbol variable/parameter: visibility L250
# @symbol variable/parameter: name_file L267
# @symbol variable/parameter: content L268
# @symbol variable/parameter: result L269
# @symbol function/class: acl L287
# @symbol variable/parameter: user L287
# @symbol variable/parameter: workspace L287
# @symbol function/class: documents L301
# @symbol variable/parameter: query L305
# @symbol variable/parameter: category L306
# @symbol variable/parameter: sort L307
# @symbol variable/parameter: predicate L310
# @symbol variable/parameter: values L310
# @symbol variable/parameter: pattern L315
# @symbol variable/parameter: order L321
# @symbol variable/parameter: rows L328
# @symbol variable/parameter: row L336
# @symbol function/class: audit L339
# @symbol variable/parameter: detail L339
# @symbol variable/parameter: event L339
# @index-end
"""SQLite lifecycle, deterministic synthetic scenarios and ACL queries. Index: docs/code-index.md."""

import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .conversion import ingest
from .models import WorkspaceConfig

SCENARIOS = {
    "industrial": {
        "title": "Meridian Controls",
        "category": "Industrial automation",
        "products": [
            (
                "MC-240",
                "Edge controller",
                "Linux-based monitoring gateway, Ethernet I/O and MQTT integration.",
                74900,
                "north",
                "Width 4.25 in; input 24 V; operating temperature 45 C",
            ),
            (
                "IO-16",
                "Remote I/O module",
                "Sixteen-channel isolated input module for production monitoring.",
                28900,
                "north",
                "Width 8.2 cm; input 24000 mV",
            ),
            (
                "PS-24",
                "Power supply",
                "DIN-rail regulated power supply for cabinet installations.",
                8900,
                "south",
                "Width 1.8 in; output 24 V",
            ),
        ],
        "context": "A pump integrator standardizes supplier manuals, I/O specifications, commissioning evidence and sales.",
    },
    "renewable": {
        "title": "Solstice Energy Supply",
        "category": "Renewable equipment",
        "products": [
            (
                "SE-410",
                "Solar panel",
                "410-watt rooftop module for commercial arrays.",
                18900,
                "north",
                "Width 113.4 cm; mass 48.5 lb",
            ),
            (
                "BAT-5",
                "Storage pack",
                "Modular battery storage for commercial backup power.",
                245000,
                "north",
                "Energy 5000 Wh; mass 52 kg",
            ),
            (
                "INV-6",
                "Hybrid inverter",
                "Six-kilowatt hybrid inverter with remote health reporting.",
                115000,
                "south",
                "Width 18 in; mass 15 kg",
            ),
        ],
        "context": "An installer compares equipment dimensions, warranty documents, shipment records and seasonal sales.",
    },
    "laboratory": {
        "title": "Atlas Laboratory Supply",
        "category": "Laboratory equipment",
        "products": [
            (
                "AT-220",
                "Precision balance",
                "Bench balance for routine laboratory preparation.",
                129000,
                "north",
                "Width 22 cm; mass 3.5 kg",
            ),
            (
                "TC-40",
                "Thermal chamber",
                "Controlled temperature chamber for nonclinical materials testing.",
                449000,
                "north",
                "Temperature 104 F; width 1.5 ft",
            ),
            (
                "PG-8",
                "Pressure gauge",
                "Calibration gauge for pneumatic bench testing.",
                34900,
                "south",
                "Pressure 14.503774 psi; width 90 mm",
            ),
        ],
        "context": "A distributor unifies calibration records, customer equipment documentation and product performance summaries.",
    },
}


def password_hash(password: str, salt: str | None = None) -> str:
    """Store an independently salted scrypt hash, never the plaintext password."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return f"{salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    """Constant-time verification against a stored salted password hash."""
    salt = encoded.split("$", 1)[0]
    return secrets.compare_digest(password_hash(password, salt), encoded)


@contextmanager
def connect(path: Path):
    """Open one transaction per operation, with foreign keys and a bounded lock wait."""
    database = sqlite3.connect(path, timeout=5)
    database.row_factory = sqlite3.Row
    database.execute("PRAGMA foreign_keys = ON")
    try:
        with database:
            yield database
    finally:
        database.close()


def initialize(path: Path, demo: bool) -> None:
    """Create version-one schema and idempotently seed clearly labeled synthetic records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as database:
        version = database.execute("PRAGMA user_version").fetchone()[0]
        if version not in {0, 1}:
            raise ValueError("Unknown database schema version; restore a compatible backup")
        database.executescript(Path(__file__).with_name("schema.sql").read_text())
        for workspace, scenario in SCENARIOS.items():
            config = WorkspaceConfig(title=scenario["title"], profile=workspace)
            database.execute(
                "INSERT OR IGNORE INTO workspaces VALUES (?,?)",
                (workspace, config.model_dump_json()),
            )
            if demo:
                for username, role, customer in [
                    ("customer", "customer", "north"),
                    ("customer-south", "customer", "south"),
                    ("employee", "employee", None),
                    ("admin", "admin", None),
                ]:
                    database.execute(
                        "INSERT OR IGNORE INTO users(workspace,username,password,role,customer) VALUES (?,?,?,?,?)",
                        (workspace, username, password_hash("workbench-demo"), role, customer),
                    )
            if (
                not demo
                or database.execute(
                    "SELECT 1 FROM products WHERE workspace=? LIMIT 1", (workspace,)
                ).fetchone()
            ):
                continue
            for product_id, name, description, price, customer, specifications in scenario[
                "products"
            ]:
                normalized = ingest(
                    f"{product_id}-specification.txt", specifications.encode(), config
                )
                database.execute(
                    "INSERT INTO products VALUES (?,?,?,?,?,?,?,?)",
                    (
                        product_id,
                        workspace,
                        name,
                        scenario["category"],
                        description,
                        price,
                        customer,
                        json.dumps(normalized["measurements"]),
                    ),
                )
                for month in range(1, 13):
                    quantity = 9 + month * 2 + len(product_id) + (month % 3) * 3
                    database.execute(
                        "INSERT INTO sales(workspace,product,customer,month,quantity,revenue_cents) VALUES (?,?,?,?,?,?)",
                        (
                            workspace,
                            product_id,
                            customer,
                            f"2025-{month:02}",
                            quantity,
                            quantity * price,
                        ),
                    )
                for visibility, suffix, text in [
                    (
                        "public",
                        "overview",
                        f"{name}. {description}\n\n{specifications}\n\nSynthetic specifications, not approved for physical installations.",
                    ),
                    (
                        "customer",
                        "service",
                        f"Customer {customer} service record for {product_id}.\n\nQuarterly inspection: passed. Case reference SYN-{product_id}.\n\n{specifications}",
                    ),
                    (
                        "internal",
                        "operations",
                        f"Internal operations for {product_id}.\n\nSupplier lead time 21 days. Margin estimate: 28 percent. Synthetic only.",
                    ),
                ]:
                    name_file = f"{product_id}-{suffix}.txt"
                    content = text.encode()
                    result = ingest(name_file, content, config)
                    database.execute(
                        "INSERT INTO documents(id,workspace,title,visibility,customer,product,category,result,source,source_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (
                            f"{workspace}-{product_id}-{suffix}",
                            workspace,
                            name_file,
                            visibility,
                            customer if visibility == "customer" else None,
                            product_id,
                            suffix.title(),
                            json.dumps(result),
                            content,
                            result["provenance"]["sha256"],
                        ),
                    )


def acl(user: dict | None, workspace: str) -> tuple[str, list]:
    """SQL document predicate; caller may never broaden a user's workspace or customer scope."""
    if user and user["workspace"] != workspace:
        raise PermissionError("Workspace mismatch")
    if not user:
        return "workspace=? AND visibility='public'", [workspace]
    if user["role"] == "customer":
        return "workspace=? AND (visibility='public' OR (visibility='customer' AND customer=?))", [
            workspace,
            user["customer"],
        ]
    return "workspace=?", [workspace]


def documents(
    database: sqlite3.Connection,
    user: dict | None,
    workspace: str,
    query: str = "",
    category: str = "",
    sort: str = "title",
) -> list[dict]:
    """Bounded lexical substring search with ACL-before-result; stable allowlisted ordering."""
    predicate, values = acl(user, workspace)
    if query:
        predicate += (
            " AND (title LIKE ? ESCAPE '\\' OR json_extract(result,'$.text') LIKE ? ESCAPE '\\')"
        )
        pattern = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        values.extend([pattern, pattern])
    if category:
        predicate += " AND category=?"
        values.append(category)
    # Never interpolate request-provided identifiers; the selected fragment is constant.
    order = (
        "created DESC,id"
        if sort == "newest"
        else "category,title,id"
        if sort == "category"
        else "title,id"
    )
    rows = database.execute(
        "SELECT id,title,visibility,customer,product,category,created,result FROM documents WHERE "
        + predicate
        + " ORDER BY "
        + order
        + " LIMIT 200",
        values,
    ).fetchall()
    return [dict(row) for row in rows]


def audit(database: sqlite3.Connection, user: dict, event: str, detail: str) -> None:
    """Record immutable operational evidence without secrets or source text."""
    database.execute(
        "INSERT INTO audit(workspace,actor,event,detail) VALUES (?,?,?,?)",
        (user["workspace"], user["username"], event, detail[:300]),
    )
