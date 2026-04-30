import sqlite3
from datetime import datetime, timedelta

DB_PATH = "glass_tube_manufacturing_runall.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def drop_objects(conn):
    cur = conn.cursor()
    cur.executescript("""
    DROP VIEW IF EXISTS v_trace_key_full_flow;
    DROP VIEW IF EXISTS v_trace_key_dashboard;

    DROP TABLE IF EXISTS equipment_master;

    DROP TABLE IF EXISTS app_module_option_config;
    DROP TABLE IF EXISTS app_module_field_config;
    DROP TABLE IF EXISTS app_module_config;

    DROP TABLE IF EXISTS inventory_transaction_log;
    DROP TABLE IF EXISTS shipment_item;
    DROP TABLE IF EXISTS shipment;
    DROP TABLE IF EXISTS inventory_lot;
    DROP TABLE IF EXISTS production_process_log;
    DROP TABLE IF EXISTS production_measurement;
    DROP TABLE IF EXISTS production_schedule;
    DROP TABLE IF EXISTS production_batch;
    DROP TABLE IF EXISTS delivery_plan;
    DROP TABLE IF EXISTS order_requirement;
    DROP TABLE IF EXISTS order_item;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS product_spec;
    DROP TABLE IF EXISTS product;
    DROP TABLE IF EXISTS customer;
    """)
    conn.commit()


def create_tables(conn):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE customer (
        customer_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name    TEXT NOT NULL,
        customer_code    TEXT,
        contact_person   TEXT,
        phone            TEXT,
        email            TEXT,
        address          TEXT,
        created_at       TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE product (
        product_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name     TEXT NOT NULL,
        product_code     TEXT,
        category         TEXT,
        created_at       TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE product_spec (
        spec_id             INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id          INTEGER NOT NULL,
        spec_code           TEXT NOT NULL,
        spec_desc           TEXT,
        outer_diameter_mm   REAL,
        wall_thickness_mm   REAL,
        length_mm           REAL,
        created_at          TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES product(product_id)
    );

    CREATE TABLE orders (
        order_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id        INTEGER NOT NULL,
        order_date         TEXT,
        order_status       TEXT,
        overall_deadline   TEXT,
        priority_level     TEXT,
        created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    );

    CREATE TABLE order_item (
        order_item_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id             INTEGER NOT NULL,
        product_id           INTEGER NOT NULL,
        spec_id              INTEGER,
        ordered_qty          REAL DEFAULT 0,
        reserved_qty         REAL DEFAULT 0,
        fulfilled_qty        REAL DEFAULT 0,
        shipped_qty          REAL DEFAULT 0,
        allocatable_qty      REAL DEFAULT 0,
        item_status          TEXT,
        po_no                TEXT,
        customer_pn          TEXT,
        drawing_version      TEXT,
        factory_part_no      TEXT,
        product_type_text    TEXT,
        product_spec_text    TEXT,
        item_note            TEXT,
        trace_key            TEXT,
        created_at           TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES product(product_id),
        FOREIGN KEY (spec_id) REFERENCES product_spec(spec_id)
    );

    CREATE TABLE order_requirement (
        requirement_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        order_item_id         INTEGER NOT NULL,
        quality_requirement   TEXT,
        created_at            TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id)
    );

    CREATE TABLE delivery_plan (
        delivery_plan_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        order_item_id           INTEGER NOT NULL,
        planned_delivery_date   TEXT,
        planned_delivery_qty    REAL,
        actual_delivery_date    TEXT,
        actual_delivery_qty     REAL,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id)
    );

    CREATE TABLE production_batch (
        production_batch_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_code              TEXT NOT NULL,
        trace_key               TEXT,
        special_process         TEXT,
        common_gauge_size       TEXT,
        stop_gauge_size         TEXT,
        production_flow_status  TEXT,
        required_production_qty REAL DEFAULT 0,
        actual_qty              REAL DEFAULT 0,
        semi_finished_wh_qty    REAL DEFAULT 0,
        finished_wh_qty         REAL DEFAULT 0,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE production_schedule (
        production_schedule_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        order_item_id           INTEGER NOT NULL,
        production_batch_id     INTEGER NOT NULL,
        scheduled_start_date    TEXT,
        scheduled_end_date      TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id),
        FOREIGN KEY (production_batch_id) REFERENCES production_batch(production_batch_id)
    );

    CREATE TABLE production_measurement (
        measurement_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        production_batch_id     INTEGER NOT NULL,
        quality_status          TEXT,
        release_status          TEXT,
        inspected_at            TEXT,
        release_by              TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (production_batch_id) REFERENCES production_batch(production_batch_id)
    );

    CREATE TABLE production_process_log (
        process_log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        production_batch_id     INTEGER NOT NULL,
        process_step            TEXT,
        equipment_code          TEXT,
        operator_name           TEXT,
        input_qty               REAL DEFAULT 0,
        output_qty              REAL DEFAULT 0,
        scrap_qty               REAL DEFAULT 0,
        process_status          TEXT,
        start_time              TEXT,
        end_time                TEXT,
        remark                  TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (production_batch_id) REFERENCES production_batch(production_batch_id)
    );

    CREATE TABLE inventory_lot (
        inventory_lot_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        production_batch_id     INTEGER,
        product_id              INTEGER NOT NULL,
        spec_id                 INTEGER,
        lot_code                TEXT NOT NULL,
        trace_key               TEXT,
        location                TEXT,
        available_qty           REAL DEFAULT 0,
        reserved_qty            REAL DEFAULT 0,
        lot_status              TEXT,
        release_status          TEXT,
        exclusive_customer      TEXT,
        forbidden_customer      TEXT,
        last_out_qty            REAL DEFAULT 0,
        last_out_time           TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (production_batch_id) REFERENCES production_batch(production_batch_id),
        FOREIGN KEY (product_id) REFERENCES product(product_id),
        FOREIGN KEY (spec_id) REFERENCES product_spec(spec_id)
    );

    CREATE TABLE shipment (
        shipment_id             INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_no             TEXT NOT NULL,
        customer_id             INTEGER NOT NULL,
        ship_date               TEXT,
        carrier                 TEXT,
        destination             TEXT,
        created_by              TEXT,
        shipment_status         TEXT,
        notes                   TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    );

    CREATE TABLE shipment_item (
        shipment_item_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id             INTEGER NOT NULL,
        order_item_id           INTEGER,
        inventory_lot_id        INTEGER,
        shipped_qty             REAL DEFAULT 0,
        packaging_label_code    TEXT,
        trace_key               TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shipment_id) REFERENCES shipment(shipment_id),
        FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id),
        FOREIGN KEY (inventory_lot_id) REFERENCES inventory_lot(inventory_lot_id)
    );

    CREATE TABLE inventory_transaction_log (
        txn_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_lot_id        INTEGER NOT NULL,
        txn_type                TEXT,
        qty                     REAL,
        txn_time                TEXT,
        txn_reason              TEXT,
        reference_no            TEXT,
        created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inventory_lot_id) REFERENCES inventory_lot(inventory_lot_id)
    );

    CREATE TABLE app_module_config (
        module_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        module_code          TEXT UNIQUE NOT NULL,
        module_name          TEXT NOT NULL,
        table_name           TEXT UNIQUE NOT NULL,
        page_mode            TEXT DEFAULT 'form_list',
        is_enabled           INTEGER DEFAULT 1,
        sort_order           INTEGER DEFAULT 100,
        created_at           TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE app_module_field_config (
        field_id             INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id            INTEGER NOT NULL,
        field_name           TEXT NOT NULL,
        field_label          TEXT NOT NULL,
        field_type           TEXT DEFAULT 'text',
        is_required          INTEGER DEFAULT 0,
        is_visible_list      INTEGER DEFAULT 1,
        is_visible_form      INTEGER DEFAULT 1,
        is_editable          INTEGER DEFAULT 1,
        default_value        TEXT,
        option_source_type   TEXT,
        option_source_value  TEXT,
        field_order          INTEGER DEFAULT 100,
        created_at           TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (module_id) REFERENCES app_module_config(module_id)
    );

    CREATE TABLE app_module_option_config (
        option_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id            INTEGER NOT NULL,
        field_name           TEXT NOT NULL,
        option_label         TEXT NOT NULL,
        option_value         TEXT NOT NULL,
        option_order         INTEGER DEFAULT 100,
        created_at           TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (module_id) REFERENCES app_module_config(module_id)
    );

    CREATE TABLE equipment_master (
        record_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_code   TEXT,
        equipment_name   TEXT,
        location         TEXT,
        status           TEXT,
        owner_name       TEXT,
        created_at       TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()


def insert_master_data(conn):
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    customers = [
        ("Alpha Medical Glass", "CUST001", "Lily Chen", "0400000001", "alpha@example.com", "Sydney", now),
        ("Beta Lab Supplies", "CUST002", "Tom Wang", "0400000002", "beta@example.com", "Melbourne", now),
        ("Gamma Pharma Pack", "CUST003", "Eric Liu", "0400000003", "gamma@example.com", "Brisbane", now),
    ]
    cur.executemany("""
        INSERT INTO customer
        (customer_name, customer_code, contact_person, phone, email, address, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, customers)

    products = [
        ("Glass Tube A", "P001", "Medical Tube", now),
        ("Glass Tube B", "P002", "Lab Tube", now),
        ("Glass Tube C", "P003", "Pharma Tube", now),
    ]
    cur.executemany("""
        INSERT INTO product
        (product_name, product_code, category, created_at)
        VALUES (?, ?, ?, ?)
    """, products)

    product_specs = [
        (1, "SPEC-A-20x2x1500", "OD 20 / WT 2 / L 1500", 20.0, 2.0, 1500.0, now),
        (2, "SPEC-B-25x2.5x1200", "OD 25 / WT 2.5 / L 1200", 25.0, 2.5, 1200.0, now),
        (3, "SPEC-C-30x3x1000", "OD 30 / WT 3 / L 1000", 30.0, 3.0, 1000.0, now),
    ]
    cur.executemany("""
        INSERT INTO product_spec
        (product_id, spec_code, spec_desc, outer_diameter_mm, wall_thickness_mm, length_mm, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, product_specs)

    conn.commit()


def insert_business_data(conn):
    cur = conn.cursor()
    now = datetime.now()

    scenarios = [
        {
            "customer_id": 1,
            "product_id": 1,
            "spec_id": 1,
            "po_no": "PO-001",
            "customer_pn": "CPN-A001",
            "drawing_version": "DRW-A-V1",
            "factory_part_no": "PART-A-001",
            "product_type_text": "Glass Tube A",
            "product_spec_text": "SPEC-A-20x2x1500",
            "quality_requirement": "医用级，需附检测报告",
            "special_process": "LASER",
            "trace_key": "PO-001_SPEC-A-20x2x1500_LASER_DRW-A-V1",
            "ordered_qty": 1000,
            "planned_delivery_qty": 500,
            "actual_delivery_qty": 500,
            "order_status": "confirmed",
            "item_status": "open",
            "batch_code": "BATCH-001",
            "production_flow_status": "done",
            "required_production_qty": 1000,
            "actual_qty": 980,
            "semi_finished_wh_qty": 120,
            "finished_wh_qty": 980,
            "quality_status": "A",
            "release_status": "released",
            "lot_code": "LOT-001",
            "location": "WH-A1",
            "available_qty": 480,
            "reserved_qty": 0,
            "lot_status": "available",
            "exclusive_customer": "Alpha Medical Glass",
            "forbidden_customer": "",
            "has_shipment": True,
            "shipment_no": "SHP-001",
            "ship_qty": 500,
            "process_logs": [
                ("Cutting", "EQ-CUT-001", "Operator A", 1000, 995, 5, "done"),
                ("Polishing", "EQ-POL-001", "Operator B", 995, 988, 7, "done"),
                ("Packing", "EQ-PKG-001", "Operator C", 988, 980, 8, "done"),
            ],
        },
        {
            "customer_id": 2,
            "product_id": 2,
            "spec_id": 2,
            "po_no": "PO-002",
            "customer_pn": "CPN-B001",
            "drawing_version": "DRW-B-V2",
            "factory_part_no": "PART-B-001",
            "product_type_text": "Glass Tube B",
            "product_spec_text": "SPEC-B-25x2.5x1200",
            "quality_requirement": "常规产品",
            "special_process": "CHAMFER",
            "trace_key": "PO-002_SPEC-B-25x2.5x1200_CHAMFER_DRW-B-V2",
            "ordered_qty": 800,
            "planned_delivery_qty": 400,
            "actual_delivery_qty": None,
            "order_status": "confirmed",
            "item_status": "open",
            "batch_code": "BATCH-002",
            "production_flow_status": "done",
            "required_production_qty": 800,
            "actual_qty": 790,
            "semi_finished_wh_qty": 80,
            "finished_wh_qty": 790,
            "quality_status": "A",
            "release_status": "released",
            "lot_code": "LOT-002",
            "location": "WH-B1",
            "available_qty": 790,
            "reserved_qty": 0,
            "lot_status": "available",
            "exclusive_customer": "",
            "forbidden_customer": "",
            "has_shipment": False,
            "shipment_no": None,
            "ship_qty": 0,
            "process_logs": [
                ("Cutting", "EQ-CUT-002", "Operator D", 800, 798, 2, "done"),
                ("Forming", "EQ-FRM-002", "Operator E", 798, 794, 4, "done"),
                ("Packing", "EQ-PKG-002", "Operator F", 794, 790, 4, "done"),
            ],
        },
        {
            "customer_id": 3,
            "product_id": 3,
            "spec_id": 3,
            "po_no": "PO-003",
            "customer_pn": "CPN-C001",
            "drawing_version": "DRW-C-V3",
            "factory_part_no": "PART-C-001",
            "product_type_text": "Glass Tube C",
            "product_spec_text": "SPEC-C-30x3x1000",
            "quality_requirement": "尺寸严格，异常禁止放行",
            "special_process": "DRILLING",
            "trace_key": "PO-003_SPEC-C-30x3x1000_DRILLING_DRW-C-V3",
            "ordered_qty": 600,
            "planned_delivery_qty": 300,
            "actual_delivery_qty": None,
            "order_status": "confirmed",
            "item_status": "open",
            "batch_code": "BATCH-003",
            "production_flow_status": "hold",
            "required_production_qty": 600,
            "actual_qty": 580,
            "semi_finished_wh_qty": 60,
            "finished_wh_qty": 580,
            "quality_status": "C",
            "release_status": "hold",
            "lot_code": "LOT-003",
            "location": "WH-HOLD",
            "available_qty": 580,
            "reserved_qty": 0,
            "lot_status": "hold",
            "exclusive_customer": "",
            "forbidden_customer": "All",
            "has_shipment": False,
            "shipment_no": None,
            "ship_qty": 0,
            "process_logs": [
                ("Cutting", "EQ-CUT-003", "Operator G", 600, 595, 5, "done"),
                ("Drilling", "EQ-DRL-003", "Operator H", 595, 586, 9, "done"),
                ("Inspection Hold", "EQ-QC-003", "QC User", 586, 580, 6, "hold"),
            ],
        },
        {
            "customer_id": 1,
            "product_id": 2,
            "spec_id": 2,
            "po_no": "PO-004",
            "customer_pn": "CPN-B002",
            "drawing_version": "DRW-B-V1",
            "factory_part_no": "PART-B-002",
            "product_type_text": "Glass Tube B",
            "product_spec_text": "SPEC-B-25x2.5x1200",
            "quality_requirement": "Standard",
            "special_process": "STANDARD",
            "trace_key": "PO-004_SPEC-B-25x2.5x1200_STANDARD_DRW-B-V1",
            "ordered_qty": 500,
            "planned_delivery_qty": 200,
            "actual_delivery_qty": None,
            "order_status": "confirmed",
            "item_status": "open",
            "batch_code": "BATCH-004",
            "production_flow_status": "planned",
            "required_production_qty": 500,
            "actual_qty": 0,
            "semi_finished_wh_qty": 0,
            "finished_wh_qty": 0,
            "quality_status": None,
            "release_status": None,
            "lot_code": None,
            "location": None,
            "available_qty": 0,
            "reserved_qty": 0,
            "lot_status": None,
            "exclusive_customer": "",
            "forbidden_customer": "",
            "has_shipment": False,
            "shipment_no": None,
            "ship_qty": 0,
            "process_logs": [
                ("Cutting", "EQ-CUT-004", "Operator I", 0, 0, 0, "planned"),
            ],
        },
    ]

    for i, s in enumerate(scenarios, start=1):
        order_date = (now - timedelta(days=10 - i)).strftime("%Y-%m-%d")
        deadline = (now + timedelta(days=7 + i)).strftime("%Y-%m-%d")
        created_at = (now - timedelta(days=10 - i)).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO orders
            (customer_id, order_date, order_status, overall_deadline, priority_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            s["customer_id"], order_date, s["order_status"], deadline, "Medium", created_at
        ))
        order_id = cur.lastrowid

        fulfilled_qty = s["actual_delivery_qty"] if s["actual_delivery_qty"] is not None else 0

        cur.execute("""
            INSERT INTO order_item
            (order_id, product_id, spec_id, ordered_qty, reserved_qty, fulfilled_qty, shipped_qty,
             allocatable_qty, item_status, po_no, customer_pn, drawing_version, factory_part_no,
             product_type_text, product_spec_text, item_note, trace_key, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            s["product_id"],
            s["spec_id"],
            s["ordered_qty"],
            0,
            fulfilled_qty,
            s["ship_qty"],
            s["available_qty"],
            s["item_status"],
            s["po_no"],
            s["customer_pn"],
            s["drawing_version"],
            s["factory_part_no"],
            s["product_type_text"],
            s["product_spec_text"],
            f"测试场景 {i}",
            s["trace_key"],
            created_at
        ))
        order_item_id = cur.lastrowid

        cur.execute("""
            INSERT INTO order_requirement
            (order_item_id, quality_requirement, created_at)
            VALUES (?, ?, ?)
        """, (
            order_item_id, s["quality_requirement"], created_at
        ))

        cur.execute("""
            INSERT INTO delivery_plan
            (order_item_id, planned_delivery_date, planned_delivery_qty, actual_delivery_date, actual_delivery_qty, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_item_id,
            (now + timedelta(days=i)).strftime("%Y-%m-%d"),
            s["planned_delivery_qty"],
            (now + timedelta(days=i + 1)).strftime("%Y-%m-%d") if s["actual_delivery_qty"] is not None else None,
            s["actual_delivery_qty"],
            created_at
        ))

        common_gauge = "20.00" if s["spec_id"] == 1 else ("25.00" if s["spec_id"] == 2 else "30.00")
        stop_gauge = "19.95" if s["spec_id"] == 1 else ("24.95" if s["spec_id"] == 2 else "29.95")

        cur.execute("""
            INSERT INTO production_batch
            (batch_code, trace_key, special_process, common_gauge_size, stop_gauge_size,
             production_flow_status, required_production_qty, actual_qty,
             semi_finished_wh_qty, finished_wh_qty, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["batch_code"],
            s["trace_key"],
            s["special_process"],
            common_gauge,
            stop_gauge,
            s["production_flow_status"],
            s["required_production_qty"],
            s["actual_qty"],
            s["semi_finished_wh_qty"],
            s["finished_wh_qty"],
            created_at
        ))
        production_batch_id = cur.lastrowid

        cur.execute("""
            INSERT INTO production_schedule
            (order_item_id, production_batch_id, scheduled_start_date, scheduled_end_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_item_id,
            production_batch_id,
            (now - timedelta(days=3)).strftime("%Y-%m-%d"),
            (now + timedelta(days=2)).strftime("%Y-%m-%d"),
            created_at
        ))

        for step_idx, log in enumerate(s["process_logs"], start=1):
            step_name, equipment_code, operator_name, input_qty, output_qty, scrap_qty, process_status = log
            start_time = (now - timedelta(days=max(1, 4 - step_idx), hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = None if process_status == "planned" else (now - timedelta(days=max(1, 4 - step_idx))).strftime("%Y-%m-%d %H:%M:%S")

            cur.execute("""
                INSERT INTO production_process_log
                (production_batch_id, process_step, equipment_code, operator_name,
                 input_qty, output_qty, scrap_qty, process_status,
                 start_time, end_time, remark, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                production_batch_id,
                step_name,
                equipment_code,
                operator_name,
                input_qty,
                output_qty,
                scrap_qty,
                process_status,
                start_time,
                end_time,
                f"{s['batch_code']} - {step_name}",
                created_at
            ))

        if s["quality_status"] is not None:
            cur.execute("""
                INSERT INTO production_measurement
                (production_batch_id, quality_status, release_status, inspected_at, release_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                production_batch_id,
                s["quality_status"],
                s["release_status"],
                (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                "QC User",
                created_at
            ))

        lot_id = None
        if s["lot_code"] is not None:
            last_out_time = now.strftime("%Y-%m-%d %H:%M:%S") if s["has_shipment"] else None
            cur.execute("""
                INSERT INTO inventory_lot
                (production_batch_id, product_id, spec_id, lot_code, trace_key, location,
                 available_qty, reserved_qty, lot_status, release_status,
                 exclusive_customer, forbidden_customer, last_out_qty, last_out_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                production_batch_id,
                s["product_id"],
                s["spec_id"],
                s["lot_code"],
                s["trace_key"],
                s["location"],
                s["available_qty"],
                s["reserved_qty"],
                s["lot_status"],
                s["release_status"],
                s["exclusive_customer"],
                s["forbidden_customer"],
                s["ship_qty"] if s["has_shipment"] else 0,
                last_out_time,
                created_at
            ))
            lot_id = cur.lastrowid

        if s["has_shipment"] and lot_id is not None:
            cur.execute("""
                INSERT INTO shipment
                (shipment_no, customer_id, ship_date, carrier, destination, created_by, shipment_status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["shipment_no"],
                s["customer_id"],
                now.strftime("%Y-%m-%d"),
                "DHL",
                "Customer Warehouse",
                "Init Script",
                "shipped",
                f"Shipment for {s['trace_key']}",
                created_at
            ))
            shipment_id = cur.lastrowid

            cur.execute("""
                INSERT INTO shipment_item
                (shipment_id, order_item_id, inventory_lot_id, shipped_qty, packaging_label_code, trace_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                shipment_id,
                order_item_id,
                lot_id,
                s["ship_qty"],
                f"PKG-{i:03d}",
                s["trace_key"],
                created_at
            ))

            cur.execute("""
                INSERT INTO inventory_transaction_log
                (inventory_lot_id, txn_type, qty, txn_time, txn_reason, reference_no, created_at)
                VALUES (?, 'outbound', ?, ?, 'shipment', ?, ?)
            """, (
                lot_id,
                s["ship_qty"],
                now.strftime("%Y-%m-%d %H:%M:%S"),
                s["shipment_no"],
                created_at
            ))

    conn.commit()


def insert_dynamic_module_demo(conn):
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO app_module_config
        (module_code, module_name, table_name, page_mode, is_enabled, sort_order)
        VALUES ('equipment_master', '设备管理', 'equipment_master', 'form_list', 1, 10)
    """)

    cur.execute("""
        SELECT module_id FROM app_module_config WHERE module_code = 'equipment_master'
    """)
    module_id = cur.fetchone()[0]

    field_rows = [
        (module_id, "equipment_code", "设备编号", "text", 1, 1, 1, 1, "", None, None, 10),
        (module_id, "equipment_name", "设备名称", "text", 1, 1, 1, 1, "", None, None, 20),
        (module_id, "location", "位置", "text", 0, 1, 1, 1, "", None, None, 30),
        (module_id, "status", "状态", "select", 1, 1, 1, 1, "active", "static", "status_options", 40),
        (module_id, "owner_name", "负责人", "text", 0, 1, 1, 1, "", None, None, 50),
    ]

    for row in field_rows:
        cur.execute("""
            INSERT INTO app_module_field_config
            (module_id, field_name, field_label, field_type, is_required,
             is_visible_list, is_visible_form, is_editable, default_value,
             option_source_type, option_source_value, field_order)
            SELECT ?,?,?,?,?,?,?,?,?,?,?,?
            WHERE NOT EXISTS (
                SELECT 1 FROM app_module_field_config
                WHERE module_id = ? AND field_name = ?
            )
        """, row + (module_id, row[1]))

    option_rows = [
        (module_id, "status", "启用", "active", 10),
        (module_id, "status", "停用", "inactive", 20),
        (module_id, "status", "维修中", "maintenance", 30),
    ]

    for row in option_rows:
        cur.execute("""
            INSERT INTO app_module_option_config
            (module_id, field_name, option_label, option_value, option_order)
            SELECT ?,?,?,?,?
            WHERE NOT EXISTS (
                SELECT 1 FROM app_module_option_config
                WHERE module_id = ? AND field_name = ? AND option_value = ?
            )
        """, row + (module_id, row[1], row[3]))

    equipment_rows = [
        ("EQ-001", "切割机-1", "车间A", "active", "张三"),
        ("EQ-002", "抛光机-1", "车间B", "maintenance", "李四"),
        ("EQ-003", "清洗机-1", "车间C", "active", "王五"),
        ("EQ-004", "包装机-1", "车间D", "inactive", "赵六"),
        ("EQ-005", "钻孔机-1", "车间E", "active", "陈七"),
    ]

    for row in equipment_rows:
        cur.execute("""
            INSERT INTO equipment_master
            (equipment_code, equipment_name, location, status, owner_name)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM equipment_master WHERE equipment_code = ?
            )
        """, row + (row[0],))

    conn.commit()


def print_summary(conn):
    cur = conn.cursor()
    tables = [
        "customer",
        "product",
        "product_spec",
        "orders",
        "order_item",
        "order_requirement",
        "delivery_plan",
        "production_batch",
        "production_schedule",
        "production_measurement",
        "production_process_log",
        "inventory_lot",
        "shipment",
        "shipment_item",
        "inventory_transaction_log",
        "app_module_config",
        "app_module_field_config",
        "app_module_option_config",
        "equipment_master",
    ]

    print("\n===== 数据初始化完成 =====")
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = cur.fetchone()[0]
        print(f"{table:25s}: {cnt}")

    print("\n===== 推荐测试 Trace Key =====")
    print("1. PO-001_SPEC-A-20x2x1500_LASER_DRW-A-V1      -> 正常完成 + 已发货")
    print("2. PO-002_SPEC-B-25x2.5x1200_CHAMFER_DRW-B-V2  -> 已完工 + 未发货")
    print("3. PO-003_SPEC-C-30x3x1000_DRILLING_DRW-C-V3   -> Hold 拦截")
    print("4. PO-004_SPEC-B-25x2.5x1200_STANDARD_DRW-B-V1 -> 计划阶段")

    print("\n===== 默认动态模块 =====")
    print("设备管理 -> equipment_master")
    print("主键字段（导入更新依据）: equipment_code")
    print("默认测试记录: EQ-001 ~ EQ-005")

    print("\n===== 动态模块导入测试表头 =====")
    print("英文表头: equipment_code,equipment_name,location,status,owner_name")
    print("中文表头: 设备编号,设备名称,位置,状态,负责人")

    print("\n===== 动态模块导入更新示例 =====")
    print("若导入中包含相同 equipment_code，将更新现有记录而非重复新增。")

    print(f"\n数据库文件: {DB_PATH}")


def main():
    conn = get_conn()
    try:
        drop_objects(conn)
        create_tables(conn)
        insert_master_data(conn)
        insert_business_data(conn)
        insert_dynamic_module_demo(conn)
        print_summary(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()