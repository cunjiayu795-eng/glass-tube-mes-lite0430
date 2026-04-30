import os
import sqlite3
from datetime import date, datetime
from io import BytesIO, StringIO

import pandas as pd
import streamlit as st

# =========================
# 基础配置
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "glass_tube_manufacturing_runall.db")

st.set_page_config(
    page_title="Glass Tube MES Lite",
    layout="wide"
)

# =========================
# 数据库连接
# =========================
def get_conn():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30
    )

    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    return conn


def list_db_objects(conn):
    return pd.read_sql_query("""
        SELECT type, name
        FROM sqlite_master
        WHERE type IN ('table', 'view')
        ORDER BY type, name
    """, conn)


def find_missing_tables(conn, required_tables):
    objs = list_db_objects(conn)
    existing = set(objs.loc[objs["type"] == "table", "name"].tolist())
    return [t for t in required_tables if t not in existing]


REQUIRED_TABLES = [
    "customer",
    "orders",
    "order_item",
    "product",
    "product_spec",
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
]

# =========================
# 全局中文显示映射
# =========================
TABLE_LABELS = {
    "customer": "客户主数据",
    "product": "产品主数据",
    "product_spec": "产品规格",
    "orders": "订单主表",
    "order_item": "订单明细",
    "order_requirement": "订单要求",
    "delivery_plan": "交付计划",
    "production_batch": "生产批次",
    "production_schedule": "生产排程",
    "production_measurement": "生产检测",
    "production_process_log": "生产过程日志",
    "inventory_lot": "库存批次",
    "shipment": "出货主表",
    "shipment_item": "出货明细",
    "inventory_transaction_log": "库存交易日志",
    "trace_dashboard": "追溯汇总",
    "trace_full_flow": "追溯全流程",
    "equipment_master": "设备管理",
    "app_module_config": "模块配置",
    "app_module_field_config": "模块字段配置",
    "app_module_option_config": "模块选项配置",
    "v_trace_key_dashboard": "Trace汇总视图",
    "v_trace_key_full_flow": "Trace全流程视图",
}

COLUMN_LABELS = {
    "record_id": "记录编号",
    "created_at": "创建时间",

    "customer_id": "客户编号",
    "customer_name": "客户名称",
    "customer_code": "客户编码",
    "contact_person": "联系人",
    "phone": "电话",
    "email": "邮箱",
    "address": "地址",

    "product_id": "产品编号",
    "product_name": "产品名称",
    "product_code": "产品编码",
    "category": "产品分类",

    "spec_id": "规格编号",
    "spec_code": "规格编码",
    "spec_desc": "规格描述",
    "outer_diameter_mm": "外径(mm)",
    "wall_thickness_mm": "壁厚(mm)",
    "length_mm": "长度(mm)",

    "order_id": "订单编号",
    "order_date": "订单日期",
    "order_status": "订单状态",
    "overall_deadline": "总交期",
    "priority_level": "优先级",

    "order_item_id": "订单明细编号",
    "ordered_qty": "订单数量",
    "reserved_qty": "预留数量",
    "fulfilled_qty": "已完成数量",
    "shipped_qty": "已出货数量",
    "allocatable_qty": "可分配数量",
    "item_status": "明细状态",
    "po_no": "订单号",
    "customer_pn": "客户料号",
    "drawing_version": "图纸版本",
    "factory_part_no": "本厂料号",
    "product_type_text": "产品类型",
    "product_spec_text": "产品规格文本",
    "item_note": "备注",
    "trace_key": "追溯键",

    "requirement_id": "要求编号",
    "quality_requirement": "质量要求",

    "delivery_plan_id": "交付计划编号",
    "planned_delivery_date": "计划交付日期",
    "planned_delivery_qty": "计划交付数量",
    "actual_delivery_date": "实际交付日期",
    "actual_delivery_qty": "实际交付数量",
    "planned_delivery_plan": "计划交付汇总",
    "actual_delivery_plan": "实际交付汇总",

    "production_batch_id": "生产批次编号",
    "batch_code": "批次号",
    "special_process": "特殊工艺",
    "material": "材质",
    "common_gauge_size": "通规尺寸",
    "stop_gauge_size": "止规尺寸",
    "production_flow_status": "生产状态",
    "required_production_qty": "应生产数量",
    "actual_qty": "实际数量",
    "semi_finished_wh_qty": "半成品库存",
    "finished_wh_qty": "成品库存",

    "production_schedule_id": "排程编号",
    "scheduled_start_date": "计划开始日期",
    "scheduled_end_date": "计划结束日期",

    "measurement_id": "检测编号",
    "quality_status": "质量等级",
    "release_status": "放行状态",
    "inspected_at": "检测时间",
    "release_by": "放行人",

    "process_log_id": "过程日志编号",
    "process_step": "工序",
    "equipment_code": "设备编号",
    "operator_name": "操作员",
    "input_qty": "投入数量",
    "output_qty": "产出数量",
    "scrap_qty": "报废数量",
    "process_status": "工序状态",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "remark": "备注",

    "inventory_lot_id": "Lot编号",
    "lot_code": "Lot号",
    "location": "库位",
    "available_qty": "可用数量",
    "reserved_qty": "预留数量",
    "lot_status": "Lot状态",
    "exclusive_customer": "专供客户",
    "forbidden_customer": "禁用客户",
    "last_out_qty": "最近出库数量",
    "last_out_time": "最近出库时间",

    "shipment_id": "出货编号",
    "shipment_no": "出货单号",
    "ship_date": "出货日期",
    "carrier": "承运商",
    "destination": "目的地",
    "created_by": "创建人",
    "shipment_status": "出货状态",
    "notes": "备注",

    "shipment_item_id": "出货明细编号",
    "packaging_label_code": "包装标签号",

    "txn_id": "交易编号",
    "txn_type": "交易类型",
    "qty": "数量",
    "txn_time": "交易时间",
    "txn_reason": "交易原因",
    "reference_no": "参考单号",

    "module_id": "模块编号",
    "module_code": "模块编码",
    "module_name": "模块名称",
    "table_name": "数据表名",
    "page_mode": "页面模式",
    "is_enabled": "是否启用",
    "sort_order": "排序",

    "field_id": "字段编号",
    "field_name": "字段名",
    "field_label": "字段中文名",
    "field_type": "字段类型",
    "is_required": "是否必填",
    "is_visible_list": "列表可见",
    "is_visible_form": "表单可见",
    "is_editable": "是否可编辑",
    "default_value": "默认值",
    "option_source_type": "选项来源类型",
    "option_source_value": "选项来源值",
    "field_order": "字段顺序",

    "option_id": "选项编号",
    "option_label": "选项显示名",
    "option_value": "选项值",
    "option_order": "选项顺序",

    "batch_count": "批次数",
    "lot_count": "Lot数",
    "shipment_count": "出货次数",
    "total_shipped_qty": "总出货量",
    "latest_release_status": "最新放行状态",

    "equipment_name": "设备名称",
    "owner_name": "负责人",
}

# =========================
# 初始化 trace 视图
# =========================

def ensure_trace_key_columns(conn):
    """
    为四重 Trace Key 增加订单端 / 生产端字段。
    字段已存在时不会重复添加。
    """
    cursor = conn.cursor()

    order_item_cols = pd.read_sql_query("PRAGMA table_info(order_item)", conn)["name"].tolist()
    if "special_process" not in order_item_cols:
        cursor.execute("ALTER TABLE order_item ADD COLUMN special_process TEXT DEFAULT 'STANDARD'")
    if "material" not in order_item_cols:
        cursor.execute("ALTER TABLE order_item ADD COLUMN material TEXT DEFAULT 'UNKNOWN_MATERIAL'")

    production_batch_cols = pd.read_sql_query("PRAGMA table_info(production_batch)", conn)["name"].tolist()
    if "material" not in production_batch_cols:
        cursor.execute("ALTER TABLE production_batch ADD COLUMN material TEXT DEFAULT 'UNKNOWN_MATERIAL'")

    conn.commit()

def init_trace_views(conn):
    cursor = conn.cursor()

    cursor.executescript("""
    DROP VIEW IF EXISTS v_trace_key_full_flow;
    DROP VIEW IF EXISTS v_trace_key_dashboard;

    CREATE VIEW v_trace_key_full_flow AS
    WITH delivery_agg AS (
        SELECT
            order_item_id,
            GROUP_CONCAT(
                planned_delivery_date || ' / ' || planned_delivery_qty,
                ' ; '
            ) AS planned_delivery_plan,
            GROUP_CONCAT(
                CASE
                    WHEN actual_delivery_date IS NOT NULL
                    THEN actual_delivery_date || ' / ' || COALESCE(actual_delivery_qty, 0)
                    ELSE NULL
                END,
                ' ; '
            ) AS actual_delivery_plan
        FROM delivery_plan
        GROUP BY order_item_id
    )
    SELECT
        oi.trace_key,
        o.order_id,
        oi.order_item_id,
        c.customer_name,
        oi.po_no,
        oi.customer_pn,
        oi.drawing_version,
        oi.factory_part_no,
        p.product_name,
        COALESCE(ps.spec_code, oi.product_spec_text) AS spec_code,
        oi.product_type_text,
        oi.product_spec_text,
        oi.item_note,
        orq.quality_requirement,
        pb.production_batch_id,
        pb.batch_code,
        COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material,
        pb.special_process,
        pb.common_gauge_size,
        pb.stop_gauge_size,
        pb.production_flow_status,
        pb.required_production_qty,
        pb.actual_qty,
        pm.quality_status,
        pm.release_status,
        il.inventory_lot_id,
        il.lot_code,
        il.location,
        il.available_qty,
        il.reserved_qty,
        il.lot_status,
        il.exclusive_customer,
        il.forbidden_customer,
        s.shipment_id,
        s.shipment_no,
        s.ship_date,
        si.shipped_qty,
        da.planned_delivery_plan,
        da.actual_delivery_plan,
        o.order_status,
        oi.item_status
    FROM order_item oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customer c ON o.customer_id = c.customer_id
    JOIN product p ON oi.product_id = p.product_id
    LEFT JOIN product_spec ps ON oi.spec_id = ps.spec_id
    LEFT JOIN order_requirement orq ON oi.order_item_id = orq.order_item_id
    LEFT JOIN production_schedule sch ON oi.order_item_id = sch.order_item_id
    LEFT JOIN production_batch pb ON sch.production_batch_id = pb.production_batch_id
    LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
    LEFT JOIN inventory_lot il ON il.trace_key = oi.trace_key
    LEFT JOIN shipment_item si ON si.trace_key = oi.trace_key
    LEFT JOIN shipment s ON si.shipment_id = s.shipment_id
    LEFT JOIN delivery_agg da ON oi.order_item_id = da.order_item_id
    WHERE oi.trace_key IS NOT NULL;

    CREATE VIEW v_trace_key_dashboard AS
    SELECT
        trace_key,
        customer_name,
        po_no,
        spec_code,
        special_process,
        material,
        COUNT(DISTINCT production_batch_id) AS batch_count,
        COUNT(DISTINCT inventory_lot_id) AS lot_count,
        COUNT(DISTINCT shipment_id) AS shipment_count,
        COALESCE(SUM(shipped_qty), 0) AS total_shipped_qty,
        MAX(release_status) AS latest_release_status,
        MAX(order_status) AS order_status,
        MAX(item_status) AS item_status,
        MAX(product_name) AS product_name
    FROM v_trace_key_full_flow
    GROUP BY trace_key, customer_name, po_no, spec_code, special_process, material;
    """)

    conn.commit()


def ensure_delivery_plan_batch_fields(conn):
    """
    确保 delivery_plan 表有：
    1. delivery_batch_no：交付批次号
    2. delivery_status：交付状态

    这个版本增加了：
    - busy_timeout 防止 database is locked
    - try / rollback 防止半途失败后一直锁库
    - 只在需要时更新历史空值
    """
    cur = conn.cursor()

    try:
        conn.execute("PRAGMA busy_timeout = 30000")

        cols_df = pd.read_sql_query("PRAGMA table_info(delivery_plan)", conn)
        existing_cols = cols_df["name"].tolist() if not cols_df.empty else []

        if "delivery_batch_no" not in existing_cols:
            cur.execute("""
                ALTER TABLE delivery_plan
                ADD COLUMN delivery_batch_no INTEGER
            """)
            conn.commit()

        if "delivery_status" not in existing_cols:
            cur.execute("""
                ALTER TABLE delivery_plan
                ADD COLUMN delivery_status TEXT DEFAULT '未排产'
            """)
            conn.commit()

        rows = pd.read_sql_query("""
            SELECT
                delivery_plan_id,
                order_item_id,
                planned_delivery_date,
                delivery_batch_no,
                delivery_status
            FROM delivery_plan
            WHERE delivery_batch_no IS NULL
               OR delivery_status IS NULL
            ORDER BY order_item_id, planned_delivery_date, delivery_plan_id
        """, conn)

        if not rows.empty:
            for order_item_id, group in rows.groupby("order_item_id"):
                full_group = pd.read_sql_query("""
                    SELECT
                        delivery_plan_id,
                        order_item_id,
                        planned_delivery_date,
                        delivery_batch_no,
                        delivery_status
                    FROM delivery_plan
                    WHERE order_item_id = ?
                    ORDER BY planned_delivery_date, delivery_plan_id
                """, conn, params=[order_item_id])

                for idx, (_, row) in enumerate(full_group.reset_index(drop=True).iterrows(), start=1):
                    cur.execute("""
                        UPDATE delivery_plan
                        SET delivery_batch_no = COALESCE(delivery_batch_no, ?),
                            delivery_status = COALESCE(delivery_status, '未排产')
                        WHERE delivery_plan_id = ?
                    """, (
                        idx,
                        int(row["delivery_plan_id"])
                    ))

            conn.commit()

    except sqlite3.OperationalError as e:
        conn.rollback()

        if "database is locked" in str(e).lower():
            st.error("数据库当前被锁定。请停止其他正在运行的 Streamlit 进程后重新运行。")
            st.stop()

        raise e

def ensure_production_schedule_delivery_plan_field(conn):
    """
    确保 production_schedule 表有 delivery_plan_id 字段。
    """
    cur = conn.cursor()

    try:
        conn.execute("PRAGMA busy_timeout = 30000")

        cols_df = pd.read_sql_query("PRAGMA table_info(production_schedule)", conn)
        existing_cols = cols_df["name"].tolist() if not cols_df.empty else []

        if "delivery_plan_id" not in existing_cols:
            cur.execute("""
                ALTER TABLE production_schedule
                ADD COLUMN delivery_plan_id INTEGER
            """)
            conn.commit()

    except sqlite3.OperationalError as e:
        conn.rollback()

        if "database is locked" in str(e).lower():
            st.error("数据库当前被锁定。请停止其他正在运行的 Streamlit 进程后重新运行。")
            st.stop()

        raise e

def apply_global_ui_style():
    st.markdown("""
    <style>
    /* ========= 全局基础字体 ========= */
    html, body, [class*="css"] {
        font-size: 20px;
    }

    /* ========= 页面主标题 ========= */
    h1 {
        font-size: 34px !important;
        font-weight: 700 !important;
    }

    /* ========= 二级标题 ========= */
    h2 {
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* ========= 三级标题 ========= */
    h3 {
        font-size: 22px !important;
        font-weight: 600 !important;
    }

    /* ========= 普通文本 ========= */
    p, li, div, span, label {
        font-size: 20px !important;
    }

    /* ========= Streamlit metric 标题 ========= */
    div[data-testid="stMetricLabel"] {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ========= Streamlit metric 数值 ========= */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* ========= 按钮 ========= */
    .stButton > button {
        font-size: 18px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.45rem 1rem !important;
    }

    /* ========= 输入框 / 下拉框 / 文本区 ========= */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    .stTextArea label,
    .stRadio label {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ========= expander 标题 ========= */
    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ========= Tabs 标题 ========= */
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ========= 侧边栏 ========= */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 20px !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {
        font-size: 16px !important;
    }

    /* ========= dataframe 表格字体 ========= */
    [data-testid="stDataFrame"] div {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =========================
# 通用函数
# =========================
def metric_count(conn, table_name):
    return int(pd.read_sql_query(f"SELECT COUNT(*) AS cnt FROM {table_name}", conn)["cnt"].iloc[0])


def get_trace_keys(conn):
    return pd.read_sql_query("""
        SELECT DISTINCT trace_key
        FROM order_item
        WHERE trace_key IS NOT NULL
        ORDER BY trace_key
    """, conn)


def safe_float(v, default=0.0):
    try:
        if pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default


def normalize_text(v):
    if pd.isna(v):
        return ""
    return str(v).strip()

def normalize_trace_part(v, default="NA"):
    """
    Trace Key 组件标准化：
    - 去除前后空格
    - 空值用默认值
    - 内部空格改为短横线
    - 统一大写
    - 避免双下划线破坏分隔结构
    """
    text = normalize_text(v)
    if text == "":
        text = default

    text = text.replace("__", "-")
    text = text.replace(" ", "-")
    text = text.upper()

    return text


def build_trace_key(po_no, spec_code, special_process, material):
    """
    四重限制 Trace Key：
    PO + 规格 + 特殊工艺 + 材质
    """
    return "__".join([
        normalize_trace_part(po_no, "NOPO"),
        normalize_trace_part(spec_code, "NOSPEC"),
        normalize_trace_part(special_process, "STANDARD"),
        normalize_trace_part(material, "UNKNOWN_MATERIAL"),
    ])





def validate_excel_df(df, required_columns):
    missing = [c for c in required_columns if c not in df.columns]
    return missing

def render_delivery_schedule_editor(prefix, ordered_qty):
    st.markdown("## 交货方式")

    delivery_mode = st.radio(
        "请选择交货方式",
        ["一次性交货", "分批交货"],
        horizontal=True,
        key=f"{prefix}_delivery_mode"
    )

    schedules = []

    if delivery_mode == "一次性交货":
        st.markdown("### 单次交货计划")
        c1, c2 = st.columns(2)
        with c1:
            d1 = st.date_input("交货日期", value=date.today(), key=f"{prefix}_single_date")
        with c2:
            q1 = st.number_input(
                "交货数量",
                min_value=0.0,
                value=float(ordered_qty) if ordered_qty else 0.0,
                step=1.0,
                key=f"{prefix}_single_qty"
            )

        schedules.append({
            "planned_delivery_date": str(d1),
            "planned_delivery_qty": float(q1)
        })

    else:
        batch_count_key = f"{prefix}_batch_count"

        if batch_count_key not in st.session_state:
            st.session_state[batch_count_key] = 2

        st.markdown("### 分批交货计划")

        b1, b2, b3, b4 = st.columns([1, 1, 1, 2])

        with b1:
            if st.button("＋ 新增一批", key=f"{prefix}_add_batch"):
                st.session_state[batch_count_key] += 1

        with b2:
            if st.button("－ 删除一批", key=f"{prefix}_remove_batch"):
                if st.session_state[batch_count_key] > 2:
                    st.session_state[batch_count_key] -= 1

        with b3:
            current_batch_count = st.session_state[batch_count_key]
            st.metric("当前分批数", current_batch_count)

        with b4:
            auto_split_clicked = st.button("自动平均拆分", key=f"{prefix}_auto_split")

        batch_count = int(st.session_state[batch_count_key])

        if auto_split_clicked and ordered_qty > 0:
            base_qty = int(ordered_qty) // batch_count
            remainder = int(ordered_qty) % batch_count
            for i in range(batch_count):
                auto_qty = base_qty + (1 if i < remainder else 0)
                st.session_state[f"{prefix}_qty_{i}"] = float(auto_qty)

        for i in range(batch_count):
            st.markdown(f"### 第 {i+1} 批")

            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input(
                    f"交货日期 {i+1}",
                    value=date.today(),
                    key=f"{prefix}_date_{i}"
                )
            with c2:
                q = st.number_input(
                    f"交货数量 {i+1}",
                    min_value=0.0,
                    value=float(st.session_state.get(f"{prefix}_qty_{i}", 0.0)),
                    step=1.0,
                    key=f"{prefix}_qty_{i}"
                )

            schedules.append({
                "planned_delivery_date": str(d),
                "planned_delivery_qty": float(q)
            })

            st.caption(f"第 {i+1} 批：日期 {d} / 数量 {float(q):.0f}")
            st.markdown("---")

    planned_total = sum(x["planned_delivery_qty"] for x in schedules)
    remain_qty = float(ordered_qty) - float(planned_total)

    st.markdown("## 交货计划汇总")
    c1, c2, c3 = st.columns(3)
    c1.metric("订单数量", f"{float(ordered_qty):.0f}")
    c2.metric("当前计划总量", f"{float(planned_total):.0f}")
    c3.metric("剩余待分配", f"{float(remain_qty):.0f}")

    progress_ratio = 0.0
    if float(ordered_qty) > 0:
        progress_ratio = max(0.0, min(planned_total / float(ordered_qty), 1.0))
    st.progress(progress_ratio)

    if abs(remain_qty) < 0.000001:
        st.success("√ 交货计划数量已平衡")
    elif remain_qty > 0:
        st.warning("当前交货计划数量不足，请继续分配")
    else:
        st.error("交货计划数量超过订单数量，请调整")

    return delivery_mode, schedules, remain_qty

def table_label(name: str) -> str:
    return TABLE_LABELS.get(name, name)


def column_label(name: str) -> str:
    return COLUMN_LABELS.get(name, name)


def beautify_df_for_display(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    rename_map = {col: column_label(col) for col in df.columns}
    return df.rename(columns=rename_map)

def format_delivery_detail_multiline(detail_text):
    if pd.isna(detail_text) or str(detail_text).strip() == "":
        return ""

    parts = [x.strip() for x in str(detail_text).split(";") if x.strip()]
    lines = []
    for i, part in enumerate(parts, start=1):
        lines.append(f"第{i}批：{part}")
    return "\n".join(lines)

def render_sales_delivery_detail_card(conn, order_item_id):
    detail_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.po_no,
            oi.customer_pn,
            oi.product_spec_text,
            oi.ordered_qty,
            c.customer_name,
            dp.delivery_plan_id,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            dp.actual_delivery_date,
            dp.actual_delivery_qty
        FROM order_item oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN delivery_plan dp ON oi.order_item_id = dp.order_item_id
        WHERE oi.order_item_id = ?
        ORDER BY dp.planned_delivery_date, dp.delivery_plan_id
    """, conn, params=[order_item_id])

    if detail_df.empty:
        st.info("当前订单明细没有交货计划。")
        return

    order_head = detail_df.iloc[0]

    st.markdown("## 订单交货计划明细")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("订单明细编号", int(order_head["order_item_id"]))
    c2.metric("客户", str(order_head["customer_name"]))
    c3.metric("PO", str(order_head["po_no"]))
    c4.metric("订单数量", f"{float(order_head['ordered_qty']):.0f}")

    st.caption(f"客户料号：{order_head['customer_pn']} ｜ 产品规格：{order_head['product_spec_text']}")

    plan_rows = detail_df[detail_df["delivery_plan_id"].notna()].copy()
    if plan_rows.empty:
        st.warning("该订单明细尚未生成任何 delivery_plan。")
        return

    total_planned = pd.to_numeric(plan_rows["planned_delivery_qty"], errors="coerce").fillna(0).sum()
    total_actual = pd.to_numeric(plan_rows["actual_delivery_qty"], errors="coerce").fillna(0).sum()
    ordered_qty = float(order_head["ordered_qty"]) if pd.notna(order_head["ordered_qty"]) else 0.0
    remain_qty = ordered_qty - total_planned

    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("分批次数", int(len(plan_rows)))
    s2.metric("计划总量", f"{float(total_planned):.0f}")
    s3.metric("实际交付总量", f"{float(total_actual):.0f}")
    s4.metric("计划差额", f"{float(remain_qty):.0f}")

    if abs(remain_qty) < 0.000001:
        st.success("√ 当前交货计划总量与订单数量一致")
    elif remain_qty > 0:
        st.warning("当前交货计划总量小于订单数量")
    else:
        st.error("当前交货计划总量大于订单数量")

    st.markdown("---")

    for idx, row in plan_rows.reset_index(drop=True).iterrows():
        planned_date = row["planned_delivery_date"] if pd.notna(row["planned_delivery_date"]) else ""
        planned_qty = float(row["planned_delivery_qty"]) if pd.notna(row["planned_delivery_qty"]) else 0.0
        actual_date = row["actual_delivery_date"] if pd.notna(row["actual_delivery_date"]) else ""
        actual_qty = float(row["actual_delivery_qty"]) if pd.notna(row["actual_delivery_qty"]) else 0.0

        st.markdown(f"### 第 {idx + 1} 批")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("计划交货日期", str(planned_date))
        a2.metric("计划交货数量", f"{planned_qty:.0f}")
        a3.metric("实际交货日期", str(actual_date) if str(actual_date).strip() else "未交货")
        a4.metric("实际交货数量", f"{actual_qty:.0f}")

        if actual_qty >= planned_qty and planned_qty > 0:
            st.success("该批次交付状态：已满足计划")
        elif actual_qty > 0:
            st.warning("该批次交付状态：部分完成")
        else:
            st.info("该批次交付状态：尚未交付")

        st.markdown("---")

def render_sales_process_flow(current_status):
    flow_steps = ["未排产", "已排产", "切割", "清洗", "质检", "已入库"]

    if current_status not in flow_steps:
        current_status = "未排产"

    current_index = flow_steps.index(current_status)

    st.markdown("### 订单处理流程")

    cols = st.columns(len(flow_steps))
    for i, step in enumerate(flow_steps):
        if i < current_index:
            cols[i].success(step)
        elif i == current_index:
            cols[i].info(f"当前：{step}")
        else:
            cols[i].caption(step)


def render_current_order_trace_detail(conn, order_item_id):
    st.markdown("## 当前订单追踪明细区")

    # =========================
    # 1. 订单基础信息
    # =========================
    order_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.po_no,
            oi.customer_pn,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
            oi.trace_key,
            oi.ordered_qty,
            oi.shipped_qty,
            oi.item_status,
            o.order_date,
            o.order_status,
            o.overall_deadline,
            c.customer_name
        FROM order_item oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        WHERE oi.order_item_id = ?
    """, conn, params=[order_item_id])

    if order_df.empty:
        st.warning("未找到该订单明细。")
        return

    base = order_df.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("订单明细编号", int(base["order_item_id"]))
    c2.metric("客户", str(base["customer_name"]))
    c3.metric("PO", str(base["po_no"]))
    c4.metric("Trace Key", str(base["trace_key"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("订单数量", f"{float(base['ordered_qty']) if pd.notna(base['ordered_qty']) else 0:.0f}")
    c6.metric("已出货量", f"{float(base['shipped_qty']) if pd.notna(base['shipped_qty']) else 0:.0f}")
    c7.metric("订单状态", str(base["order_status"]))
    c8.metric("明细状态", str(base["item_status"]))

    st.caption(
        f"客户料号：{base['customer_pn']} ｜ 产品规格：{base['product_spec_text']} ｜ "
        f"特殊工艺：{base['special_process']} ｜ 材质：{base['material']} ｜ "
        f"订单日期：{base['order_date']} ｜ 总交期：{base['overall_deadline']}"
    )

    st.markdown("---")

    # =========================
    # 2. 交付批次总览（新增）
    # =========================
    st.markdown("### 交付批次总览")

    delivery_plan_df = pd.read_sql_query("""
        WITH batch_status AS (
            SELECT
                dp.delivery_plan_id,
                CASE
                    WHEN MAX(CASE WHEN il.inventory_lot_id IS NOT NULL
                                   AND lower(COALESCE(il.release_status, 'pending')) = 'released'
                                  THEN 1 ELSE 0 END) = 1 THEN '已入库'
                    WHEN MAX(CASE WHEN pm.measurement_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '质检'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cleaning' THEN 1 ELSE 0 END) = 1 THEN '清洗'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cutting' THEN 1 ELSE 0 END) = 1 THEN '切割'
                    WHEN MAX(CASE WHEN ps.production_schedule_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '已排产'
                    ELSE COALESCE(MAX(dp.delivery_status), '未排产')
                END AS real_process_status
            FROM delivery_plan dp
            LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
            LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN production_process_log ppl ON pb.production_batch_id = ppl.production_batch_id
            LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
            GROUP BY dp.delivery_plan_id
        )
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            dp.actual_delivery_date,
            dp.actual_delivery_qty,
            COALESCE(bs.real_process_status, dp.delivery_status, '未排产') AS delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN batch_status bs ON dp.delivery_plan_id = bs.delivery_plan_id
        WHERE dp.order_item_id = ?
        ORDER BY dp.delivery_batch_no, dp.planned_delivery_date, dp.delivery_plan_id
    """, conn, params=[order_item_id])

    if delivery_plan_df.empty:
        st.info("当前订单没有交付批次数据。")
    else:
        delivery_plan_display_df = delivery_plan_df.rename(columns={
            "delivery_batch_no": "交付批次",
            "planned_delivery_date": "计划交付日期",
            "planned_delivery_qty": "计划交付数量",
            "actual_delivery_date": "实际交付日期",
            "actual_delivery_qty": "实际交付数量",
            "delivery_status": "交付状态",
            "batch_code": "对应批次号",
            "required_production_qty": "应生产数量",
            "actual_qty": "实际生产数量",
            "production_flow_status": "生产状态"
        })
        show_df(delivery_plan_display_df, hide_index=True)

        st.markdown("---")
        st.markdown("### 交付批次卡片")

        selected_delivery_plan_id = st.selectbox(
            "选择一条交付批次查看明细",
            delivery_plan_df["delivery_plan_id"].tolist(),
            format_func=lambda x: (
                f"{x} | 第{int(delivery_plan_df.loc[delivery_plan_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])}批 | "
                f"{delivery_plan_df.loc[delivery_plan_df['delivery_plan_id'] == x, 'planned_delivery_date'].iloc[0]}"
            ),
            key=f"trace_delivery_plan_select_{order_item_id}"
        )

        selected_dp = delivery_plan_df[delivery_plan_df["delivery_plan_id"] == selected_delivery_plan_id].iloc[0]
        current_dp_status = str(selected_dp["delivery_status"]) if pd.notna(selected_dp["delivery_status"]) else "未排产"

        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("交付批次", f"第 {int(selected_dp['delivery_batch_no'])} 批")
        d2.metric("计划交付日期", str(selected_dp["planned_delivery_date"]))
        d3.metric("计划交付数量", f"{float(selected_dp['planned_delivery_qty'] or 0):.0f}")
        d4.metric("实际交付数量", f"{float(selected_dp['actual_delivery_qty'] or 0):.0f}")
        d5.metric("当前批次状态", current_dp_status)

        d6, d7, d8 = st.columns(3)
        d6.metric("对应生产批次", str(selected_dp["batch_code"]) if pd.notna(selected_dp["batch_code"]) else "-")
        d7.metric("应生产数量", f"{float(selected_dp['required_production_qty'] or 0):.0f}")
        d8.metric("实际生产数量", f"{float(selected_dp['actual_qty'] or 0):.0f}")

        render_sales_process_flow(
            current_dp_status if current_dp_status in ["未排产", "已排产", "切割", "清洗", "质检", "已入库"] else "未排产"
        )

    st.markdown("---")

    # =========================
    # 3. 查询订单级全链路数据（保留原来的 tabs）
    # =========================
    schedule_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.order_item_id,
            ps.production_batch_id,
            ps.delivery_plan_id,
            ps.scheduled_start_date,
            ps.scheduled_end_date
        FROM production_schedule ps
        WHERE ps.order_item_id = ?
        ORDER BY ps.production_schedule_id
    """, conn, params=[order_item_id])

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.special_process,
            pb.common_gauge_size,
            pb.stop_gauge_size,
            pb.production_flow_status,
            pb.required_production_qty,
            pb.actual_qty,
            pb.semi_finished_wh_qty,
            pb.finished_wh_qty
        FROM production_schedule ps
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        WHERE ps.order_item_id = ?
        ORDER BY pb.production_batch_id
    """, conn, params=[order_item_id])

    process_df = pd.read_sql_query("""
        SELECT
            ppl.process_log_id,
            ppl.production_batch_id,
            ppl.process_step,
            ppl.equipment_code,
            ppl.operator_name,
            ppl.input_qty,
            ppl.output_qty,
            ppl.scrap_qty,
            ppl.process_status,
            ppl.start_time,
            ppl.end_time,
            ppl.remark
        FROM production_schedule ps
        JOIN production_process_log ppl ON ps.production_batch_id = ppl.production_batch_id
        WHERE ps.order_item_id = ?
        ORDER BY ppl.process_log_id DESC
    """, conn, params=[order_item_id])

    measurement_df = pd.read_sql_query("""
        SELECT
            pm.measurement_id,
            pm.production_batch_id,
            pm.quality_status,
            pm.release_status,
            pm.inspected_at,
            pm.release_by
        FROM production_schedule ps
        JOIN production_measurement pm ON ps.production_batch_id = pm.production_batch_id
        WHERE ps.order_item_id = ?
        ORDER BY pm.measurement_id DESC
    """, conn, params=[order_item_id])

    lot_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.production_batch_id,
            il.lot_code,
            il.trace_key,
            il.location,
            il.available_qty,
            il.reserved_qty,
            il.lot_status,
            il.release_status,
            il.last_out_qty,
            il.last_out_time
        FROM production_schedule ps
        JOIN inventory_lot il ON ps.production_batch_id = il.production_batch_id
        WHERE ps.order_item_id = ?
        ORDER BY il.inventory_lot_id
    """, conn, params=[order_item_id])

    shipment_df = pd.read_sql_query("""
        SELECT
            s.shipment_id,
            s.shipment_no,
            s.ship_date,
            s.shipment_status,
            si.shipment_item_id,
            si.inventory_lot_id,
            si.shipped_qty,
            si.packaging_label_code,
            si.trace_key
        FROM shipment_item si
        JOIN shipment s ON si.shipment_id = s.shipment_id
        WHERE si.order_item_id = ?
        ORDER BY s.shipment_id DESC, si.shipment_item_id DESC
    """, conn, params=[order_item_id])

    txn_df = pd.read_sql_query("""
        SELECT
            itl.txn_id,
            itl.inventory_lot_id,
            il.lot_code,
            itl.txn_type,
            itl.qty,
            itl.txn_time,
            itl.txn_reason,
            itl.reference_no
        FROM inventory_transaction_log itl
        JOIN inventory_lot il ON itl.inventory_lot_id = il.inventory_lot_id
        WHERE il.trace_key = ?
        ORDER BY itl.txn_id DESC
    """, conn, params=[base["trace_key"]])

    st.markdown("### 订单级全链路追踪")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "排产",
        "工序",
        "质检",
        "入库",
        "出货",
        "流水"
    ])

    with tab1:
        st.markdown("### 排产记录")
        if schedule_df.empty:
            st.info("当前没有排产记录。")
        else:
            show_df(schedule_df, hide_index=True)

        st.markdown("---")
        st.markdown("### 批次主信息")
        if batch_df.empty:
            st.info("当前没有批次主信息。")
        else:
            show_df(batch_df, hide_index=True)

    with tab2:
        st.markdown("### 工序日志")
        if process_df.empty:
            st.info("当前没有工序日志。")
        else:
            show_df(process_df, hide_index=True)

    with tab3:
        st.markdown("### 质检记录")
        if measurement_df.empty:
            st.info("当前没有质检记录。")
        else:
            show_df(measurement_df, hide_index=True)

    with tab4:
        st.markdown("### 入库 Lot")
        if lot_df.empty:
            st.info("当前没有入库 Lot。")
        else:
            show_df(lot_df, hide_index=True)

    with tab5:
        st.markdown("### 出货记录")
        if shipment_df.empty:
            st.info("当前没有出货记录。")
        else:
            show_df(shipment_df, hide_index=True)

    with tab6:
        st.markdown("### 库存流水")
        if txn_df.empty:
            st.info("当前没有库存流水。")
        else:
            show_df(txn_df, hide_index=True)


def beautify_sheet_name(name: str) -> str:
    return table_label(name)[:31]


def show_df(df: pd.DataFrame, **kwargs):
    st.dataframe(beautify_df_for_display(df), use_container_width=True, **kwargs)


def beautify_dynamic_module_df(df: pd.DataFrame, fields_df: pd.DataFrame) -> pd.DataFrame:
    """
    动态模块专用显示：
    1) 优先使用 field_label 作为中文列名
    2) record_id / created_at 等系统列再回退到全局 COLUMN_LABELS
    """
    if df is None or df.empty:
        return df

    rename_map = {}
    if fields_df is not None and not fields_df.empty:
        for _, row in fields_df.iterrows():
            field_name = str(row["field_name"]).strip()
            field_label = str(row["field_label"]).strip()
            rename_map[field_name] = field_label

    for col in df.columns:
        if col not in rename_map:
            rename_map[col] = column_label(col)

    return df.rename(columns=rename_map)


def show_dynamic_module_df(df: pd.DataFrame, fields_df: pd.DataFrame, **kwargs):
    st.dataframe(
        beautify_dynamic_module_df(df, fields_df),
        use_container_width=True,
        **kwargs
    )


# =========================
# 中文表头自动映射
# =========================
HEADER_ALIASES = {
    "订单导入": {
        "customer_name": ["customer_name", "客户名称", "客户", "客户名"],
        "po_no": ["po_no", "订单号", "PO", "PO号", "订单编号"],
        "customer_pn": ["customer_pn", "客户料号", "客户零件号", "客户PN", "客户品号"],
        "drawing_version": ["drawing_version", "图纸版本", "版本号", "图纸编号"],
        "factory_part_no": ["factory_part_no", "本厂料号", "本厂零件号", "厂内料号", "内部料号"],
        "spec_code": ["spec_code", "规格编码", "规格", "产品规格", "规格代码"],
        "ordered_qty": ["ordered_qty", "订单数量", "数量", "订购数量"],
        "overall_deadline": ["overall_deadline", "总交期", "交期", "预计交货日期", "截止日期"],
        "quality_requirement": ["quality_requirement", "质量要求", "品质要求"],
        "special_process": ["special_process", "特殊工艺", "工艺要求", "特殊制程"],
        "material": ["material", "材质", "材料", "玻璃材质", "材料类型", "material_type"],
        "item_note": ["item_note", "备注", "备注说明", "特殊要求"],
        "planned_delivery_date": ["planned_delivery_date", "计划交付日期", "计划出货日期", "计划交期"],
        "planned_delivery_qty": ["planned_delivery_qty", "计划交付数量", "计划出货数量", "计划数量"],
    },
    "检测导入": {
        "batch_code": ["batch_code", "批次号", "生产批次号", "批号"],
        "quality_status": ["quality_status", "质量等级", "品质等级"],
        "release_status": ["release_status", "放行状态", "放行结果", "状态"],
        "inspected_at": ["inspected_at", "检测时间", "检验时间", "检测日期"],
        "release_by": ["release_by", "放行人", "检测人", "检验员", "质检员"],
    },
    "库存调整导入": {
        "lot_code": ["lot_code", "Lot编号", "Lot号", "批号", "库存批号"],
        "location": ["location", "库位", "储位", "位置"],
        "available_qty": ["available_qty", "可用数量", "可发数量"],
        "reserved_qty": ["reserved_qty", "预留数量", "锁定数量"],
        "lot_status": ["lot_status", "Lot状态", "库存状态"],
        "release_status": ["release_status", "放行状态", "放行结果"],
    },
    "生产过程导入": {
        "batch_code": ["batch_code", "批次号", "生产批次号", "批号"],
        "process_step": ["process_step", "工序", "工步", "流程步骤"],
        "equipment_code": ["equipment_code", "设备编号", "设备号", "机台编号"],
        "operator_name": ["operator_name", "操作员", "作业员", "员工"],
        "input_qty": ["input_qty", "投入数量", "投料数量", "输入数量"],
        "output_qty": ["output_qty", "产出数量", "输出数量", "完工数量"],
        "scrap_qty": ["scrap_qty", "报废数量", "损耗数量", "不良数量"],
        "process_status": ["process_status", "工序状态", "状态"],
        "start_time": ["start_time", "开始时间", "开工时间"],
        "end_time": ["end_time", "结束时间", "完工时间"],
        "remark": ["remark", "备注", "说明"],
    }
}


def clean_column_name(col):
    return str(col).strip()


def auto_map_headers(df, import_type):
    df = df.copy()
    df.columns = [clean_column_name(c) for c in df.columns]

    alias_config = HEADER_ALIASES.get(import_type, {})
    rename_map = {}
    matched_source_cols = set()

    for target_col, aliases in alias_config.items():
        for alias in aliases:
            alias_clean = clean_column_name(alias)
            if alias_clean in df.columns:
                rename_map[alias_clean] = target_col
                matched_source_cols.add(alias_clean)
                break

    mapped_df = df.rename(columns=rename_map)
    unmatched_columns = [c for c in df.columns if c not in matched_source_cols]
    return mapped_df, rename_map, unmatched_columns


def show_header_mapping_result(original_df, mapped_df, rename_map):
    st.subheader("表头自动映射结果")

    if rename_map:
        mapping_df = pd.DataFrame(
            [{"原表头": k, "系统字段": v} for k, v in rename_map.items()]
        )
        show_df(mapping_df, hide_index=True)
    else:
        st.warning("没有识别到可映射表头。")

    st.caption("映射后的字段列表")
    st.write(list(mapped_df.columns))


# =========================
# Excel / CSV 读取工具
# =========================
def read_uploaded_table(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return df, "已按 Excel 文件读取"

    if file_name.endswith(".csv"):
        raw = uploaded_file.getvalue()
        encodings_to_try = ["utf-8", "utf-8-sig", "gbk", "gb2312", "big5", "latin1"]
        for enc in encodings_to_try:
            try:
                text = raw.decode(enc)
                df = pd.read_csv(StringIO(text))
                return df, f"已按 CSV 文件读取，识别编码: {enc}"
            except Exception:
                pass
        raise ValueError("CSV 编码识别失败，可尝试将文件另存为 UTF-8 编码后重试。")

    raise ValueError("仅支持 .xlsx 或 .csv 文件")


# =========================
# Excel 工具
# =========================
def dataframe_to_excel_bytes(sheet_map):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheet_map.items():
            safe_name = beautify_sheet_name(sheet_name)
            export_df = beautify_df_for_display(df.copy())
            export_df.to_excel(writer, index=False, sheet_name=safe_name)
    output.seek(0)
    return output.getvalue()


def get_export_data_map(conn):
    return {
        "customer": pd.read_sql_query("SELECT * FROM customer ORDER BY customer_id", conn),
        "product": pd.read_sql_query("SELECT * FROM product ORDER BY product_id", conn),
        "product_spec": pd.read_sql_query("SELECT * FROM product_spec ORDER BY spec_id", conn),
        "orders": pd.read_sql_query("SELECT * FROM orders ORDER BY order_id", conn),
        "order_item": pd.read_sql_query("SELECT * FROM order_item ORDER BY order_item_id", conn),
        "order_requirement": pd.read_sql_query("SELECT * FROM order_requirement ORDER BY requirement_id", conn),
        "delivery_plan": pd.read_sql_query("SELECT * FROM delivery_plan ORDER BY delivery_plan_id", conn),
        "production_batch": pd.read_sql_query("SELECT * FROM production_batch ORDER BY production_batch_id", conn),
        "production_schedule": pd.read_sql_query("SELECT * FROM production_schedule ORDER BY production_schedule_id", conn),
        "production_measurement": pd.read_sql_query("SELECT * FROM production_measurement ORDER BY measurement_id", conn),
        "production_process_log": pd.read_sql_query("SELECT * FROM production_process_log ORDER BY process_log_id", conn),
        "inventory_lot": pd.read_sql_query("SELECT * FROM inventory_lot ORDER BY inventory_lot_id", conn),
        "shipment": pd.read_sql_query("SELECT * FROM shipment ORDER BY shipment_id", conn),
        "shipment_item": pd.read_sql_query("SELECT * FROM shipment_item ORDER BY shipment_item_id", conn),
        "inventory_transaction_log": pd.read_sql_query("SELECT * FROM inventory_transaction_log ORDER BY txn_id", conn),
        "trace_dashboard": pd.read_sql_query("SELECT * FROM v_trace_key_dashboard ORDER BY trace_key", conn),
        "trace_full_flow": pd.read_sql_query("SELECT * FROM v_trace_key_full_flow ORDER BY trace_key", conn),
    }


def get_template_data(template_type):
    if template_type == "订单导入模板":
        return pd.DataFrame([{
            "customer_name": "Alpha Medical Glass",
            "po_no": "PO-NEW-001",
            "customer_pn": "CPN-NEW-001",
            "drawing_version": "DRW-NEW-V1",
            "factory_part_no": "PART-NEW-001",
            "spec_code": "SPEC-A-20x2x1500",
            "ordered_qty": 1000,
            "overall_deadline": "2026-05-10",
            "quality_requirement": "Standard",
            "special_process": "STANDARD",
            "material": "BOROSILICATE",
            "item_note": "Excel 导入测试",
            "planned_delivery_date": "2026-05-01",
            "planned_delivery_qty": 300,
        }])

    if template_type == "检测导入模板":
        return pd.DataFrame([{
            "batch_code": "BATCH-004",
            "quality_status": "A",
            "release_status": "released",
            "inspected_at": "2026-04-23 10:00:00",
            "release_by": "QC User",
        }])

    if template_type == "库存调整模板":
        return pd.DataFrame([{
            "lot_code": "LOT-002",
            "location": "WH-B2",
            "available_qty": 780,
            "reserved_qty": 10,
            "lot_status": "available",
            "release_status": "released",
        }])

    if template_type == "生产过程导入模板":
        return pd.DataFrame([{
            "batch_code": "BATCH-004",
            "process_step": "Cutting",
            "equipment_code": "EQ-CUT-004",
            "operator_name": "Operator X",
            "input_qty": 500,
            "output_qty": 490,
            "scrap_qty": 10,
            "process_status": "done",
            "start_time": "2026-04-23 08:00:00",
            "end_time": "2026-04-23 10:00:00",
            "remark": "Excel 导入工序",
        }])

    return pd.DataFrame()


# =========================
# Excel 导入逻辑
# =========================

def import_orders_from_excel(conn, df):
    required_columns = [
        "customer_name", "po_no", "customer_pn", "drawing_version", "factory_part_no",
        "spec_code", "ordered_qty", "overall_deadline", "quality_requirement",
        "special_process", "item_note", "planned_delivery_date", "planned_delivery_qty"
    ]

    missing = validate_excel_df(df, required_columns)
    if missing:
        return False, f"缺少列: {', '.join(missing)}"

    cursor = conn.cursor()
    success_count = 0
    failed_rows = []

    customer_df = pd.read_sql_query("SELECT customer_id, customer_name FROM customer", conn)

    spec_df = pd.read_sql_query("""
        SELECT
            ps.spec_id,
            ps.spec_code,
            p.product_id,
            p.product_name
        FROM product_spec ps
        JOIN product p ON ps.product_id = p.product_id
    """, conn)

    for idx, row in df.iterrows():
        row_no = idx + 2

        customer_name = normalize_text(row["customer_name"])
        po_no = normalize_text(row["po_no"])
        special_process = normalize_text(row["special_process"]) or "STANDARD"

        # 兼容旧 Excel：如果没有 material 列，就自动给默认材质
        material = normalize_text(row["material"]) if "material" in df.columns else "UNKNOWN_MATERIAL"
        material = material or "UNKNOWN_MATERIAL"

        drawing_version = normalize_text(row["drawing_version"]) or "DRW-NEW-V1"
        spec_code = normalize_text(row["spec_code"])

        if not customer_name:
            failed_rows.append({"行号": row_no, "失败原因": "客户名称为空"})
            continue

        if not po_no:
            failed_rows.append({"行号": row_no, "失败原因": "PO 为空"})
            continue

        if not spec_code:
            failed_rows.append({"行号": row_no, "失败原因": "规格编码为空"})
            continue

        customer_match = customer_df[customer_df["customer_name"] == customer_name]
        if customer_match.empty:
            failed_rows.append({
                "行号": row_no,
                "失败原因": "客户不存在",
                "客户名称": customer_name
            })
            continue

        spec_match = spec_df[spec_df["spec_code"] == spec_code]
        if spec_match.empty:
            failed_rows.append({
                "行号": row_no,
                "失败原因": "规格不存在",
                "规格编码": spec_code
            })
            continue

        customer_id = int(customer_match.iloc[0]["customer_id"])
        spec_id = int(spec_match.iloc[0]["spec_id"])
        product_id = int(spec_match.iloc[0]["product_id"])
        product_name = normalize_text(spec_match.iloc[0]["product_name"])

        trace_key = build_trace_key(
            po_no=po_no,
            spec_code=spec_code,
            special_process=special_process,
            material=material
        )

        cursor.execute("""
            INSERT INTO orders (
                customer_id,
                order_date,
                order_status,
                overall_deadline,
                priority_level
            ) VALUES (?, date('now'), 'confirmed', ?, 'Medium')
        """, (
            customer_id,
            normalize_text(row["overall_deadline"])
        ))

        order_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO order_item (
                order_id,
                product_id,
                spec_id,
                ordered_qty,
                reserved_qty,
                fulfilled_qty,
                shipped_qty,
                allocatable_qty,
                item_status,
                po_no,
                customer_pn,
                drawing_version,
                factory_part_no,
                product_type_text,
                product_spec_text,
                item_note,
                special_process,
                material,
                trace_key
            ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 'open', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            product_id,
            spec_id,
            safe_float(row["ordered_qty"]),
            po_no,
            normalize_text(row["customer_pn"]),
            drawing_version,
            normalize_text(row["factory_part_no"]),
            product_name,
            spec_code,
            normalize_text(row["item_note"]),
            special_process,
            material,
            trace_key
        ))

        order_item_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO order_requirement (
                order_item_id,
                quality_requirement
            ) VALUES (?, ?)
        """, (
            order_item_id,
            normalize_text(row["quality_requirement"])
        ))

        cursor.execute("""
            INSERT INTO delivery_plan (
                order_item_id,
                planned_delivery_date,
                planned_delivery_qty
            ) VALUES (?, ?, ?)
        """, (
            order_item_id,
            normalize_text(row["planned_delivery_date"]),
            safe_float(row["planned_delivery_qty"])
        ))

        success_count += 1

    conn.commit()

    if failed_rows:
        failed_msg = "；失败明细：" + str(failed_rows[:5])
        return True, f"成功导入订单 {success_count} 条，失败 {len(failed_rows)} 条{failed_msg}"

    return True, f"成功导入订单 {success_count} 条"

def import_measurements_from_excel(conn, df):
    """
    检测导入：
    只负责写入 / 更新 production_measurement。

    注意：
    - 不再自动创建 inventory_lot
    - 不再写 WH-AUTO
    - 不再直接入库
    - released 后只把 delivery_plan 状态更新为 待入库确认
    - hold / pending 后把 delivery_plan 状态更新为 质检中
    - 最后统一调用 sync_after_delivery_plan_change()
    """

    required_columns = [
        "batch_code",
        "quality_status",
        "release_status",
        "inspected_at",
        "release_by"
    ]

    missing = validate_excel_df(df, required_columns)
    if missing:
        return False, f"缺少列: {', '.join(missing)}"

    cursor = conn.cursor()
    success_count = 0
    failed_rows = []
    changed_delivery_plan_ids = set()

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.actual_qty,
            ps.delivery_plan_id
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
    """, conn)

    for idx, row in df.iterrows():
        row_no = idx + 2

        batch_code = normalize_text(row["batch_code"])
        quality_status = normalize_text(row["quality_status"]) or "Pending"
        release_status = normalize_text(row["release_status"]) or "pending"
        inspected_at = normalize_text(row["inspected_at"]) or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        release_by = normalize_text(row["release_by"]) or "QC User"

        if not batch_code:
            failed_rows.append({
                "行号": row_no,
                "失败原因": "batch_code 为空"
            })
            continue

        batch_match = batch_df[batch_df["batch_code"] == batch_code]

        if batch_match.empty:
            failed_rows.append({
                "行号": row_no,
                "失败原因": "未找到对应生产批次",
                "batch_code": batch_code
            })
            continue

        batch_id = int(batch_match.iloc[0]["production_batch_id"])
        delivery_plan_id = batch_match.iloc[0]["delivery_plan_id"]

        exists_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM production_measurement
            WHERE production_batch_id = ?
        """, conn, params=[batch_id])

        exists_count = int(exists_df.iloc[0]["cnt"])

        if exists_count == 0:
            cursor.execute("""
                INSERT INTO production_measurement (
                    production_batch_id,
                    quality_status,
                    release_status,
                    inspected_at,
                    release_by
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                batch_id,
                quality_status,
                release_status,
                inspected_at,
                release_by
            ))
        else:
            cursor.execute("""
                UPDATE production_measurement
                SET quality_status = ?,
                    release_status = ?,
                    inspected_at = ?,
                    release_by = ?
                WHERE production_batch_id = ?
            """, (
                quality_status,
                release_status,
                inspected_at,
                release_by,
                batch_id
            ))

        release_status_lower = release_status.lower()

        if pd.notna(delivery_plan_id):
            changed_delivery_plan_ids.add(int(delivery_plan_id))

            if release_status_lower == "released":
                cursor.execute("""
                    UPDATE delivery_plan
                    SET delivery_status = '待入库确认'
                    WHERE delivery_plan_id = ?
                """, (
                    int(delivery_plan_id),
                ))

            elif release_status_lower in ["hold", "pending"]:
                cursor.execute("""
                    UPDATE delivery_plan
                    SET delivery_status = '质检中'
                    WHERE delivery_plan_id = ?
                """, (
                    int(delivery_plan_id),
                ))

        success_count += 1

    conn.commit()

    # =========================
    # 统一同步交付批次 / 订单状态
    # =========================
    if "sync_after_delivery_plan_change" in globals():
        for dp_id in changed_delivery_plan_ids:
            sync_after_delivery_plan_change(conn, int(dp_id))

    if failed_rows:
        return True, (
            f"成功导入检测记录 {success_count} 条，失败 {len(failed_rows)} 条。"
            f"失败示例：{failed_rows[:5]}。"
            "注意：检测导入不会自动入库，released 批次请到仓储总看板执行入库确认。"
        )

    return True, (
        f"成功导入检测记录 {success_count} 条。"
        "已同步交付批次、订单明细和订单状态。"
        "注意：检测导入不会自动入库，released 批次请到仓储总看板执行入库确认。"
    )


def import_inventory_from_excel(conn, df):
    required_columns = ["lot_code", "location", "available_qty", "reserved_qty", "lot_status", "release_status"]
    missing = validate_excel_df(df, required_columns)
    if missing:
        return False, f"缺少列: {', '.join(missing)}"

    cursor = conn.cursor()
    success_count = 0

    for _, row in df.iterrows():
        lot_code = normalize_text(row["lot_code"])
        if not lot_code:
            continue

        exists = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM inventory_lot
            WHERE lot_code = ?
        """, conn, params=[lot_code])["cnt"].iloc[0]

        if exists == 0:
            continue

        cursor.execute("""
            UPDATE inventory_lot
            SET location = ?,
                available_qty = ?,
                reserved_qty = ?,
                lot_status = ?,
                release_status = ?
            WHERE lot_code = ?
        """, (
            normalize_text(row["location"]),
            safe_float(row["available_qty"]),
            safe_float(row["reserved_qty"]),
            normalize_text(row["lot_status"]),
            normalize_text(row["release_status"]),
            lot_code
        ))
        success_count += 1

    conn.commit()
    return True, f"成功更新库存 {success_count} 条"


def import_process_logs_from_excel(conn, df):
    required_columns = [
        "batch_code", "process_step", "equipment_code", "operator_name",
        "input_qty", "output_qty", "scrap_qty", "process_status",
        "start_time", "end_time", "remark"
    ]
    missing = validate_excel_df(df, required_columns)
    if missing:
        return False, f"缺少列: {', '.join(missing)}"

    cursor = conn.cursor()
    success_count = 0

    batch_df = pd.read_sql_query("""
        SELECT production_batch_id, batch_code
        FROM production_batch
    """, conn)

    for _, row in df.iterrows():
        batch_code = normalize_text(row["batch_code"])
        batch_match = batch_df[batch_df["batch_code"] == batch_code]
        if batch_match.empty:
            continue

        batch_id = int(batch_match.iloc[0]["production_batch_id"])

        cursor.execute("""
            INSERT INTO production_process_log (
                production_batch_id, process_step, equipment_code, operator_name,
                input_qty, output_qty, scrap_qty, process_status,
                start_time, end_time, remark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            normalize_text(row["process_step"]),
            normalize_text(row["equipment_code"]),
            normalize_text(row["operator_name"]),
            safe_float(row["input_qty"]),
            safe_float(row["output_qty"]),
            safe_float(row["scrap_qty"]),
            normalize_text(row["process_status"]),
            normalize_text(row["start_time"]),
            normalize_text(row["end_time"]),
            normalize_text(row["remark"])
        ))

        process_status = normalize_text(row["process_status"]).lower()
        output_qty = safe_float(row["output_qty"])

        if process_status in ("running", "done", "hold"):
            cursor.execute("""
                UPDATE production_batch
                SET production_flow_status = ?,
                    actual_qty = CASE
                        WHEN ? > COALESCE(actual_qty, 0) THEN ?
                        ELSE actual_qty
                    END
                WHERE production_batch_id = ?
            """, (process_status, output_qty, output_qty, batch_id))

        success_count += 1

    conn.commit()
    return True, f"成功导入生产过程日志 {success_count} 条"


# =========================
# 动态模块工具
# =========================
def get_enabled_modules(conn):
    return pd.read_sql_query("""
        SELECT *
        FROM app_module_config
        WHERE is_enabled = 1
        ORDER BY sort_order, module_id
    """, conn)


def get_module_fields(conn, module_id):
    return pd.read_sql_query("""
        SELECT *
        FROM app_module_field_config
        WHERE module_id = ?
        ORDER BY field_order, field_id
    """, conn, params=[module_id])


def get_module_options(conn, module_id, field_name):
    return pd.read_sql_query("""
        SELECT option_label, option_value
        FROM app_module_option_config
        WHERE module_id = ? AND field_name = ?
        ORDER BY option_order, option_id
    """, conn, params=[module_id, field_name])


def get_module_primary_key_field(fields_df):
    req = fields_df[fields_df["is_required"] == 1]["field_name"].tolist()
    if req:
        return req[0]
    all_fields = fields_df["field_name"].tolist()
    return all_fields[0] if all_fields else None


def map_field_type_to_sql(field_type):
    mapping = {
        "text": "TEXT",
        "textarea": "TEXT",
        "select": "TEXT",
        "date": "TEXT",
        "datetime": "TEXT",
        "number": "REAL",
        "integer": "INTEGER",
    }
    return mapping.get(field_type, "TEXT")


def create_dynamic_business_table(conn, table_name, fields_df):
    cur = conn.cursor()

    column_defs = ["record_id INTEGER PRIMARY KEY AUTOINCREMENT"]
    for _, row in fields_df.iterrows():
        field_name = row["field_name"]
        field_type = map_field_type_to_sql(row["field_type"])
        column_defs.append(f"{field_name} {field_type}")

    column_defs.append("created_at TEXT DEFAULT CURRENT_TIMESTAMP")

    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {", ".join(column_defs)}
    )
    """
    cur.execute(sql)
    conn.commit()


def ensure_dynamic_demo_module(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipment_master (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_code TEXT,
        equipment_name TEXT,
        location TEXT,
        status TEXT,
        owner_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO app_module_config
        (module_code, module_name, table_name, page_mode, is_enabled, sort_order)
        VALUES ('equipment_master', '设备管理', 'equipment_master', 'form_list', 1, 10)
    """)

    cur.execute("""
        SELECT module_id FROM app_module_config WHERE module_code = 'equipment_master'
    """)
    row = cur.fetchone()
    if not row:
        conn.commit()
        return
    module_id = row[0]

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

    cur.execute("""
        INSERT INTO equipment_master
        (equipment_code, equipment_name, location, status, owner_name)
        SELECT 'EQ-001', '切割机-1', '车间A', 'active', '张三'
        WHERE NOT EXISTS (SELECT 1 FROM equipment_master WHERE equipment_code = 'EQ-001')
    """)

    cur.execute("""
        INSERT INTO equipment_master
        (equipment_code, equipment_name, location, status, owner_name)
        SELECT 'EQ-002', '抛光机-1', '车间B', 'maintenance', '李四'
        WHERE NOT EXISTS (SELECT 1 FROM equipment_master WHERE equipment_code = 'EQ-002')
    """)

    conn.commit()


def get_dynamic_table_columns(conn, table_name):
    df = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
    if df.empty:
        return []
    return df["name"].tolist()


def get_dynamic_module_label_map(fields_df):
    label_map = {}
    for _, row in fields_df.iterrows():
        field_name = str(row["field_name"]).strip()
        field_label = str(row["field_label"]).strip()
        label_map[field_name] = field_name
        label_map[field_label] = field_name
    return label_map


def auto_map_dynamic_headers(df, fields_df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    label_map = get_dynamic_module_label_map(fields_df)
    rename_map = {}

    for col in df.columns:
        if col in label_map:
            rename_map[col] = label_map[col]

    mapped_df = df.rename(columns=rename_map)
    unmatched_columns = [c for c in df.columns if c not in rename_map]
    return mapped_df, rename_map, unmatched_columns


def get_dynamic_required_fields(fields_df):
    return fields_df[fields_df["is_required"] == 1]["field_name"].tolist()


def get_dynamic_list_fields(fields_df):
    return fields_df[fields_df["is_visible_list"] == 1]["field_name"].tolist()


def get_dynamic_form_fields(fields_df):
    return fields_df[fields_df["is_visible_form"] == 1]


def insert_dynamic_record(conn, table_name, form_values):
    cur = conn.cursor()
    col_names = list(form_values.keys())
    placeholders = ", ".join(["?"] * len(col_names))
    sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
    cur.execute(sql, [form_values[c] for c in col_names])
    conn.commit()
    return cur.lastrowid


def update_dynamic_record(conn, table_name, record_id, form_values):
    cur = conn.cursor()
    assignments = ", ".join([f"{col}=?" for col in form_values.keys()])
    sql = f"UPDATE {table_name} SET {assignments} WHERE record_id = ?"
    params = [form_values[c] for c in form_values.keys()] + [record_id]
    cur.execute(sql, params)
    conn.commit()


def delete_dynamic_record(conn, table_name, record_id):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE record_id = ?", (record_id,))
    conn.commit()


def export_dynamic_module_excel(conn, table_name, fields_df):
    df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY record_id DESC", conn)
    export_df = beautify_dynamic_module_df(df, fields_df)
    return dataframe_to_excel_bytes({table_name: export_df})


def get_dynamic_module_template_df(fields_df, label_mode="cn"):
    cols = []
    for _, row in fields_df.iterrows():
        if int(row["is_visible_form"]) == 1:
            cols.append(row["field_label"] if label_mode == "cn" else row["field_name"])
    return pd.DataFrame(columns=cols)


def import_dynamic_module_data(conn, table_name, fields_df, uploaded_file, import_mode="upsert"):
    original_df, read_msg = read_uploaded_table(uploaded_file)
    mapped_df, rename_map, unmatched_columns = auto_map_dynamic_headers(original_df, fields_df)

    allowed_fields = fields_df["field_name"].tolist()
    import_df = mapped_df[[c for c in mapped_df.columns if c in allowed_fields]].copy()

    required_fields = get_dynamic_required_fields(fields_df)
    missing = [c for c in required_fields if c not in import_df.columns]

    if missing:
        return {
            "ok": False,
            "msg": "缺少必需字段: " + ", ".join(missing),
            "read_msg": read_msg,
            "original_df": original_df,
            "mapped_df": mapped_df,
            "rename_map": rename_map,
            "unmatched_columns": unmatched_columns,
            "inserted": 0,
            "updated": 0,
        }

    import_df = import_df.dropna(how="all")
    if import_df.empty:
        return {
            "ok": False,
            "msg": "文件没有可导入的数据行。",
            "read_msg": read_msg,
            "original_df": original_df,
            "mapped_df": mapped_df,
            "rename_map": rename_map,
            "unmatched_columns": unmatched_columns,
            "inserted": 0,
            "updated": 0,
        }

    import_df = import_df.fillna("")

    primary_key_field = get_module_primary_key_field(fields_df)
    cur = conn.cursor()
    inserted = 0
    updated = 0

    for _, row in import_df.iterrows():
        row_dict = {col: row[col] for col in import_df.columns}
        non_empty = any(str(v).strip() != "" for v in row_dict.values())
        if not non_empty:
            continue

        if import_mode == "insert_only" or not primary_key_field or primary_key_field not in row_dict:
            col_names = list(row_dict.keys())
            placeholders = ", ".join(["?"] * len(col_names))
            sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
            cur.execute(sql, [row_dict[c] for c in col_names])
            inserted += 1
            continue

        pk_value = str(row_dict.get(primary_key_field, "")).strip()
        if pk_value == "":
            col_names = list(row_dict.keys())
            placeholders = ", ".join(["?"] * len(col_names))
            sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
            cur.execute(sql, [row_dict[c] for c in col_names])
            inserted += 1
            continue

        exists_df = pd.read_sql_query(
            f"SELECT record_id FROM {table_name} WHERE {primary_key_field} = ? LIMIT 1",
            conn,
            params=[pk_value]
        )

        if exists_df.empty:
            col_names = list(row_dict.keys())
            placeholders = ", ".join(["?"] * len(col_names))
            sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
            cur.execute(sql, [row_dict[c] for c in col_names])
            inserted += 1
        else:
            record_id = int(exists_df.iloc[0]["record_id"])
            assignments = ", ".join([f"{col}=?" for col in row_dict.keys()])
            sql = f"UPDATE {table_name} SET {assignments} WHERE record_id = ?"
            params = [row_dict[c] for c in row_dict.keys()] + [record_id]
            cur.execute(sql, params)
            updated += 1

    conn.commit()

    return {
        "ok": True,
        "msg": f"导入完成：新增 {inserted} 条，更新 {updated} 条",
        "read_msg": read_msg,
        "original_df": original_df,
        "mapped_df": mapped_df,
        "rename_map": rename_map,
        "unmatched_columns": unmatched_columns,
        "inserted": inserted,
        "updated": updated,
    }


def render_dynamic_form_with_values(st_container, conn, module_id, form_fields, initial_values=None, form_prefix="dyn"):
    if initial_values is None:
        initial_values = {}

    form_values = {}

    for _, field_row in form_fields.iterrows():
        field_name = field_row["field_name"]
        field_label = field_row["field_label"]
        field_type = field_row["field_type"]
        default_value = initial_values.get(
            field_name,
            field_row["default_value"] if pd.notna(field_row["default_value"]) else ""
        )

        key = f"{form_prefix}_{module_id}_{field_name}"

        if field_type == "text":
            form_values[field_name] = st_container.text_input(field_label, value=str(default_value), key=key)

        elif field_type == "textarea":
            form_values[field_name] = st_container.text_area(field_label, value=str(default_value), key=key)

        elif field_type == "number":
            try:
                val = float(default_value) if str(default_value).strip() != "" else 0.0
            except Exception:
                val = 0.0
            form_values[field_name] = st_container.number_input(field_label, value=val, key=key)

        elif field_type == "integer":
            try:
                val = int(float(default_value)) if str(default_value).strip() != "" else 0
            except Exception:
                val = 0
            form_values[field_name] = st_container.number_input(field_label, value=val, step=1, key=key)

        elif field_type == "date":
            form_values[field_name] = str(
                st_container.date_input(field_label, value=date.today(), key=key)
            )

        elif field_type == "datetime":
            default_text = str(default_value).strip() if str(default_value).strip() else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form_values[field_name] = st_container.text_input(field_label, value=default_text, key=key)

        elif field_type == "select":
            options_df = get_module_options(conn, module_id, field_name)
            if options_df.empty:
                form_values[field_name] = st_container.text_input(field_label, value=str(default_value), key=key)
            else:
                values = options_df["option_value"].tolist()
                index = 0
                if str(default_value) in values:
                    index = values.index(str(default_value))
                form_values[field_name] = st_container.selectbox(
                    field_label,
                    values,
                    index=index,
                    format_func=lambda x: options_df.loc[options_df["option_value"] == x, "option_label"].iloc[0],
                    key=key
                )
        else:
            form_values[field_name] = st_container.text_input(field_label, value=str(default_value), key=key)

    return form_values


# =========================
# 出货执行函数
# =========================

def refresh_order_item_status(conn, order_item_id):
    """
    出货后自动刷新订单明细状态和订单主表状态。

    逻辑：
    1. 如果已出货数量 >= 订单数量，则订单明细 completed
    2. 如果已出货数量 > 0 但小于订单数量，则订单明细 partial_shipped
    3. 如果还没有出货，则订单明细 open
    4. 如果同一个订单下所有明细都 completed，则订单主表 completed
    5. 否则订单主表保持 confirmed
    """
    cursor = conn.cursor()

    item_df = pd.read_sql_query("""
        SELECT
            order_id,
            ordered_qty,
            shipped_qty
        FROM order_item
        WHERE order_item_id = ?
    """, conn, params=[order_item_id])

    if item_df.empty:
        return

    order_id = int(item_df.iloc[0]["order_id"])
    ordered_qty = float(item_df.iloc[0]["ordered_qty"] or 0)
    shipped_qty = float(item_df.iloc[0]["shipped_qty"] or 0)

    if ordered_qty > 0 and shipped_qty >= ordered_qty:
        item_status = "completed"
    elif shipped_qty > 0:
        item_status = "partial_shipped"
    else:
        item_status = "open"

    cursor.execute("""
        UPDATE order_item
        SET item_status = ?
        WHERE order_item_id = ?
    """, (item_status, order_item_id))

    unfinished_count = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM order_item
        WHERE order_id = ?
          AND COALESCE(item_status, 'open') <> 'completed'
    """, conn, params=[order_id])["cnt"].iloc[0]

    if int(unfinished_count) == 0:
        order_status = "completed"
    else:
        order_status = "confirmed"

    cursor.execute("""
        UPDATE orders
        SET order_status = ?
        WHERE order_id = ?
    """, (order_status, order_id))

    conn.commit()

def run_shipment(conn, customer_id, order_item_id, lot_id, qty,
                 carrier="SF Express",
                 destination="Customer Warehouse",
                 created_by="Streamlit Shipment"):
    cursor = conn.cursor()

    precheck = pd.read_sql_query("""
    SELECT
        o.customer_id AS order_customer_id,
        oi.product_id AS order_product_id,
        il.product_id AS lot_product_id,
        oi.spec_id AS order_spec_id,
        il.spec_id AS lot_spec_id,
        il.available_qty,
        il.release_status,
        il.lot_status,
        COALESCE(oi.trace_key, il.trace_key) AS trace_key,
        CASE
            WHEN o.customer_id <> ? THEN '已阻止：客户不匹配'
            WHEN oi.product_id <> il.product_id THEN '已阻止：产品不匹配'
            WHEN oi.spec_id IS NOT NULL 
                 AND il.spec_id IS NOT NULL 
                 AND oi.spec_id <> il.spec_id 
                 THEN '已阻止：规格不匹配'
            WHEN il.available_qty < ? THEN '已阻止：数量不足'
            WHEN lower(COALESCE(il.release_status, 'pending')) <> 'released' 
                 THEN '已阻止：库存批次未释放'
            WHEN lower(COALESCE(il.lot_status, 'hold')) NOT IN ('available', 'reserved') 
                 THEN '已阻止：库存状态不可销售'
            ELSE 'OK'
        END AS result
    FROM order_item oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN inventory_lot il ON il.inventory_lot_id = ?
    WHERE oi.order_item_id = ?
""", conn, params=[
    customer_id,
    qty,
    lot_id,
    order_item_id
])

    if precheck.empty:
        return False, "Precheck failed: no matching order item / inventory lot."

    result = precheck["result"].iloc[0]
    trace_key = precheck["trace_key"].iloc[0]

    if result != "OK":
        return False, result

    shipment_no = f"SHP-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    packaging_code = f"PKG-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute("""
        INSERT INTO shipment (
            shipment_no, customer_id, ship_date, carrier, destination, created_by, shipment_status, notes
        ) VALUES (?, ?, date('now'), ?, ?, ?, 'shipped', ?)
    """, (
        shipment_no,
        customer_id,
        carrier,
        destination,
        created_by,
        f"Shipment for trace key {trace_key}"
    ))
    shipment_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO shipment_item (
            shipment_id, order_item_id, inventory_lot_id, shipped_qty, packaging_label_code, trace_key
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        shipment_id,
        order_item_id,
        lot_id,
        qty,
        packaging_code,
        trace_key
    ))

    cursor.execute("""
        UPDATE inventory_lot
        SET available_qty = available_qty - ?,
            last_out_qty = ?,
            last_out_time = datetime('now')
        WHERE inventory_lot_id = ?
    """, (qty, qty, lot_id))

    cursor.execute("""
        UPDATE order_item
        SET shipped_qty = COALESCE(shipped_qty, 0) + ?
        WHERE order_item_id = ?
    """, (qty, order_item_id))

    cursor.execute("""
        INSERT INTO inventory_transaction_log (
            inventory_lot_id, txn_type, qty, txn_time, txn_reason, reference_no
        ) VALUES (?, 'outbound', ?, datetime('now'), 'shipment', ?)
    """, (lot_id, qty, shipment_no))

    conn.commit()
    refresh_order_item_status(conn, order_item_id)

    return True, f"Shipment created: {shipment_no}"

def run_mixed_shipment_for_order(conn, customer_id, order_item_id, qty_needed,
                                 carrier="SF Express",
                                 destination="Customer Warehouse",
                                 created_by="Sales Mixed Shipment"):
    cursor = conn.cursor()
    qty = float(qty)
    if qty <= 0:
       return False, "出货数量必须大于 0。"

    order_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.trace_key,
            oi.product_id,
            oi.spec_id,
            oi.po_no,
            oi.ordered_qty,
            oi.shipped_qty,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material
        FROM order_item oi
        WHERE oi.order_item_id = ?
    """, conn, params=[order_item_id])

    if order_df.empty:
        return False, "未找到订单明细。"

    row = order_df.iloc[0]
    order_trace_key = str(row["trace_key"])
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None

    if spec_id is None:
        return False, "订单缺少 spec_id，无法执行混合出货。"

    qty_needed = float(qty_needed)
    if qty_needed <= 0:
        return False, "出货数量必须大于 0。"

    spec_trace_key = "__".join([
    "SPEC_STOCK",
    normalize_trace_part(row["product_spec_text"], "NOSPEC"),
    normalize_trace_part(row["special_process"], "STANDARD"),
    normalize_trace_part(row["material"], "UNKNOWN_MATERIAL"),
])

    # 先找订单库存，再找规格库存
    candidate_lots = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            trace_key,
            location,
            available_qty,
            release_status,
            lot_status,
            CASE
                WHEN trace_key = ? AND location = 'WH-ORDER' THEN 1
                WHEN trace_key LIKE ? AND location = 'WH-SPEC' THEN 2
                ELSE 99
            END AS alloc_priority
        FROM inventory_lot
        WHERE spec_id = ?
          AND lower(COALESCE(release_status, 'pending')) = 'released'
          AND lower(COALESCE(lot_status, 'hold')) IN ('available', 'reserved')
          AND COALESCE(available_qty, 0) > 0
          AND (
                (trace_key = ? AND location = 'WH-ORDER')
             OR (trace_key LIKE ? AND location = 'WH-SPEC')
          )
        ORDER BY alloc_priority ASC, available_qty DESC, inventory_lot_id ASC
    """, conn, params=[
        order_trace_key,
        f"{spec_trace_key_prefix}%",
        spec_id,
        order_trace_key,
        f"{spec_trace_key_prefix}%"
    ])

    if candidate_lots.empty:
        return False, "没有可用于该订单的订单库存或规格库存。"

    total_available = float(candidate_lots["available_qty"].sum())
    if total_available < qty_needed:
        return False, f"可分配总库存仅 {total_available:.0f}，不足覆盖需求 {qty_needed:.0f}。"

    # 创建一个shipment主单
    shipment_no = f"SHP-MIX-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    cursor.execute("""
        INSERT INTO shipment (
            shipment_no, customer_id, ship_date, carrier, destination, created_by, shipment_status, notes
        ) VALUES (?, ?, date('now'), ?, ?, ?, 'shipped', ?)
    """, (
        shipment_no,
        customer_id,
        carrier,
        destination,
        created_by,
        f"Mixed allocation shipment for order_item_id={order_item_id}"
    ))
    shipment_id = cursor.lastrowid

    remaining_qty = qty_needed
    alloc_lines = []

    for _, lot in candidate_lots.iterrows():
        if remaining_qty <= 0:
            break

        lot_id = int(lot["inventory_lot_id"])
        lot_code = str(lot["lot_code"])
        lot_available = float(lot["available_qty"])
        alloc_qty = min(lot_available, remaining_qty)

        if alloc_qty <= 0:
            continue

        packaging_code = f"PKG-{shipment_id}-{lot_id}"

        cursor.execute("""
            INSERT INTO shipment_item (
                shipment_id, order_item_id, inventory_lot_id, shipped_qty, packaging_label_code, trace_key
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            shipment_id,
            order_item_id,
            lot_id,
            alloc_qty,
            packaging_code,
            order_trace_key
        ))

        cursor.execute("""
            UPDATE inventory_lot
            SET available_qty = available_qty - ?,
                last_out_qty = ?,
                last_out_time = datetime('now')
            WHERE inventory_lot_id = ?
        """, (alloc_qty, alloc_qty, lot_id))

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id, txn_type, qty, txn_time, txn_reason, reference_no
            ) VALUES (?, 'outbound', ?, datetime('now'), 'shipment', ?)
        """, (lot_id, alloc_qty, shipment_no))

        alloc_lines.append(f"{lot_code}: {alloc_qty:.0f}")
        remaining_qty -= alloc_qty

    # 更新订单出货量
    cursor.execute("""
        UPDATE order_item
        SET shipped_qty = COALESCE(shipped_qty, 0) + ?
        WHERE order_item_id = ?
    """, (qty_needed, order_item_id))

    conn.commit()

    alloc_text = "；".join(alloc_lines)
    return True, f"混合出货成功：{shipment_no}；分配明细：{alloc_text}"


def run_mixed_shipment_for_delivery_plan(conn, delivery_plan_id,
                                         carrier="SF Express",
                                         destination="Customer Warehouse",
                                         created_by="Delivery Plan Shipment"):
    cursor = conn.cursor()

    dp_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            oi.trace_key AS order_trace_key,
            oi.spec_id,
            oi.po_no,
            o.customer_id
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[delivery_plan_id])

    if dp_df.empty:
        return False, "未找到交付批次。"

    row = dp_df.iloc[0]
    order_item_id = int(row["order_item_id"])
    delivery_batch_no = int(row["delivery_batch_no"])
    planned_qty = float(row["planned_delivery_qty"]) if pd.notna(row["planned_delivery_qty"]) else 0.0
    actual_delivery_qty = float(row["actual_delivery_qty"]) if pd.notna(row["actual_delivery_qty"]) else 0.0
    customer_id = int(row["customer_id"])
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None
    order_trace_key = str(row["order_trace_key"])

    qty_needed = planned_qty - actual_delivery_qty
    if qty_needed <= 0:
        return False, "该交付批次已完成出货，无需重复处理。"

    if spec_id is None:
        return False, "该交付批次缺少 spec_id，无法执行出货。"

    delivery_trace_key = f"{order_trace_key}::DP::{delivery_plan_id}"
    spec_trace_key_prefix = f"SPEC_STOCK::{spec_id}::"

    # 优先该交付批次订单库存，再补规格库存
    candidate_lots = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            trace_key,
            location,
            available_qty,
            release_status,
            lot_status,
            CASE
                WHEN trace_key = ? AND location = 'WH-ORDER' THEN 1
                WHEN trace_key LIKE ? AND location = 'WH-SPEC' THEN 2
                ELSE 99
            END AS alloc_priority
        FROM inventory_lot
        WHERE spec_id = ?
          AND lower(COALESCE(release_status, 'pending')) = 'released'
          AND lower(COALESCE(lot_status, 'hold')) IN ('available', 'reserved')
          AND COALESCE(available_qty, 0) > 0
          AND (
                (trace_key = ? AND location = 'WH-ORDER')
             OR (trace_key LIKE ? AND location = 'WH-SPEC')
          )
        ORDER BY alloc_priority ASC, available_qty DESC, inventory_lot_id ASC
    """, conn, params=[
        delivery_trace_key,
        f"{spec_trace_key_prefix}%",
        spec_id,
        delivery_trace_key,
        f"{spec_trace_key_prefix}%"
    ])

    if candidate_lots.empty:
        return False, "没有可用于该交付批次的订单库存或规格库存。"

    total_available = float(candidate_lots["available_qty"].sum())
    if total_available < qty_needed:
        return False, f"可分配总库存仅 {total_available:.0f}，不足覆盖该批需求 {qty_needed:.0f}。"

    shipment_no = f"SHP-DP-{delivery_plan_id}-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    cursor.execute("""
        INSERT INTO shipment (
            shipment_no, customer_id, ship_date, carrier, destination, created_by, shipment_status, notes
        ) VALUES (?, ?, date('now'), ?, ?, ?, 'shipped', ?)
    """, (
        shipment_no,
        customer_id,
        carrier,
        destination,
        created_by,
        f"Delivery plan shipment for delivery_plan_id={delivery_plan_id}"
    ))
    shipment_id = cursor.lastrowid

    remaining_qty = qty_needed
    alloc_lines = []

    for _, lot in candidate_lots.iterrows():
        if remaining_qty <= 0:
            break

        lot_id = int(lot["inventory_lot_id"])
        lot_code = str(lot["lot_code"])
        lot_available = float(lot["available_qty"])
        alloc_qty = min(lot_available, remaining_qty)

        if alloc_qty <= 0:
            continue

        packaging_code = f"PKG-DP-{shipment_id}-{lot_id}"

        cursor.execute("""
            INSERT INTO shipment_item (
                shipment_id, order_item_id, inventory_lot_id, shipped_qty, packaging_label_code, trace_key
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            shipment_id,
            order_item_id,
            lot_id,
            alloc_qty,
            packaging_code,
            delivery_trace_key
        ))

        cursor.execute("""
            UPDATE inventory_lot
            SET available_qty = available_qty - ?,
                last_out_qty = ?,
                last_out_time = datetime('now')
            WHERE inventory_lot_id = ?
        """, (alloc_qty, alloc_qty, lot_id))

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id, txn_type, qty, txn_time, txn_reason, reference_no
            ) VALUES (?, 'outbound', ?, datetime('now'), 'delivery_plan_shipment', ?)
        """, (lot_id, alloc_qty, shipment_no))

        alloc_lines.append(f"{lot_code}: {alloc_qty:.0f}")
        remaining_qty -= alloc_qty

    # 更新订单累计出货量
    cursor.execute("""
        UPDATE order_item
        SET shipped_qty = COALESCE(shipped_qty, 0) + ?
        WHERE order_item_id = ?
    """, (qty_needed, order_item_id))

    # 更新交付批次实际出货
    cursor.execute("""
        UPDATE delivery_plan
        SET actual_delivery_date = date('now'),
            actual_delivery_qty = COALESCE(actual_delivery_qty, 0) + ?,
            delivery_status = '已出货'
        WHERE delivery_plan_id = ?
    """, (qty_needed, int(delivery_plan_id)))

    conn.commit()

    alloc_text = "；".join(alloc_lines)
    return True, f"交付批次第 {delivery_batch_no} 批出货成功：{shipment_no}；分配明细：{alloc_text}"


def get_available_lots_for_order(conn, order_item_id):
    return pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.trace_key,
            il.inventory_lot_id,
            il.lot_code,
            il.available_qty,
            il.location,
            il.release_status,
            il.lot_status
        FROM order_item oi
        JOIN inventory_lot il ON oi.trace_key = il.trace_key
        WHERE oi.order_item_id = ?
          AND lower(COALESCE(il.release_status, 'pending')) = 'released'
          AND lower(COALESCE(il.lot_status, 'hold')) IN ('available', 'reserved')
          AND COALESCE(il.available_qty, 0) > 0
        ORDER BY il.available_qty DESC, il.inventory_lot_id
    """, conn, params=[order_item_id])


def create_production_for_order(conn, order_item_id, planned_qty=None):
    cursor = conn.cursor()

    order_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.trace_key,
            oi.ordered_qty,
            oi.product_spec_text,
            oi.product_id,
            oi.spec_id,
            oi.po_no,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material
        FROM order_item oi
        WHERE oi.order_item_id = ?
    """, conn, params=[order_item_id])

    if order_df.empty:
        return False, "未找到对应订单明细。"

    row = order_df.iloc[0]

    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_schedule
        WHERE order_item_id = ?
    """, conn, params=[order_item_id])

    if int(exists_df.iloc[0]["cnt"]) > 0:
        return False, "该订单已经存在排产记录，无需重复创建。"

    if planned_qty is None:
        planned_qty = float(row["ordered_qty"])
    else:
        planned_qty = float(planned_qty)

    if planned_qty <= 0:
        return False, "应生产数量必须大于 0。"

    batch_code = f"BATCH-AUTO-{int(order_item_id):04d}"

    cursor.execute("""
        INSERT INTO production_batch (
            batch_code,
            trace_key,
            special_process,
            material,
            common_gauge_size,
            stop_gauge_size,
            production_flow_status,
            required_production_qty,
            actual_qty,
            semi_finished_wh_qty,
            finished_wh_qty
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        batch_code,
        row["trace_key"],
        row["special_process"],
        row["material"],
        "",
        "",
        "planned",
        planned_qty,
        0,
        0,
        0
    ))

    production_batch_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO production_schedule (
            order_item_id,
            production_batch_id,
            scheduled_start_date,
            scheduled_end_date
        ) VALUES (?, ?, date('now'), date('now', '+7 day'))
    """, (
        order_item_id,
        production_batch_id
    ))

    conn.commit()

    return True, (
        f"已为订单明细 {order_item_id} 创建排产，"
        f"批次号 {batch_code}，"
        f"应生产数量 {planned_qty:.0f}，"
        f"工艺 {row['special_process']}，"
        f"材质 {row['material']}"
    )


def push_delivery_plan_to_production(conn, delivery_plan_id):
    """
    销售端将某个交付批次推送给生产端确认。
    只改变 delivery_plan.delivery_status，不直接创建生产批次。
    """
    cursor = conn.cursor()

    check_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.delivery_status,
            ps.production_schedule_id
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[delivery_plan_id])

    if check_df.empty:
        return False, "未找到该交付批次。"

    if pd.notna(check_df.iloc[0]["production_schedule_id"]):
        return False, "该交付批次已经排产，不能重复推送。"

    current_status = str(check_df.iloc[0]["delivery_status"] or "未排产")

    if current_status == "待生产确认":
        return True, "该交付批次已经推送至生产端，等待生产确认。"

    if current_status not in ["未排产", "待生产确认"]:
        return False, f"当前状态为 {current_status}，不适合重新推送。"

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '待生产确认'
        WHERE delivery_plan_id = ?
    """, (int(delivery_plan_id),))

    conn.commit()
    return True, "已推送至生产端，等待生产确认。"

def create_production_for_delivery_plan(conn, delivery_plan_id, planned_qty=None, manual_batch_code=None):
    """
    生产端确认销售推送后，手动输入生产批号并创建生产批次。

    流程：
    1. 销售端先把 delivery_plan 推送为“待生产确认”
    2. 生产端在排产看板确认
    3. 生产端手动录入 batch_code
    4. 系统创建 production_batch + production_schedule
    5. delivery_plan 状态变成“已排产”
    """
    cursor = conn.cursor()

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            oi.trace_key,
            oi.product_spec_text,
            oi.po_no,
            oi.product_type_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[delivery_plan_id])

    if plan_df.empty:
        return False, "未找到对应交付批次。"

    row = plan_df.iloc[0]

    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_schedule
        WHERE delivery_plan_id = ?
    """, conn, params=[delivery_plan_id])

    if int(exists_df.iloc[0]["cnt"]) > 0:
        return False, "该交付批次已经存在排产记录，无需重复创建。"

    if planned_qty is None:
        planned_qty = float(row["planned_delivery_qty"])
    else:
        planned_qty = float(planned_qty)

    if planned_qty <= 0:
        return False, "应生产数量必须大于 0。"

    batch_code = normalize_text(manual_batch_code)

    if not batch_code:
        return False, "生产批号不能为空，请由生产端手动录入。"

    batch_exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_batch
        WHERE batch_code = ?
    """, conn, params=[batch_code])

    if int(batch_exists_df.iloc[0]["cnt"]) > 0:
        return False, f"生产批号 {batch_code} 已存在，请更换批号。"

    order_item_id = int(row["order_item_id"])

    cursor.execute("""
        INSERT INTO production_batch (
            batch_code,
            trace_key,
            special_process,
            material,
            common_gauge_size,
            stop_gauge_size,
            production_flow_status,
            required_production_qty,
            actual_qty,
            semi_finished_wh_qty,
            finished_wh_qty
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        batch_code,
        str(row["trace_key"]),
        str(row["special_process"]),
        str(row["material"]),
        "",
        "",
        "planned",
        planned_qty,
        0,
        0,
        0
    ))

    production_batch_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO production_schedule (
            order_item_id,
            production_batch_id,
            delivery_plan_id,
            scheduled_start_date,
            scheduled_end_date
        ) VALUES (?, ?, ?, date('now'), date('now', '+7 day'))
    """, (
        order_item_id,
        production_batch_id,
        int(delivery_plan_id)
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '已排产'
        WHERE delivery_plan_id = ?
    """, (int(delivery_plan_id),))

    conn.commit()

    return True, (
        f"生产端已确认。交付第 {int(row['delivery_batch_no'])} 批已创建生产批次："
        f"{batch_code}，应生产数量 {planned_qty:.0f}。"
    )


def get_delivery_plan_process_status(conn, delivery_plan_id):
    df = pd.read_sql_query("""
        SELECT
            CASE
                WHEN MAX(CASE WHEN il.inventory_lot_id IS NOT NULL AND lower(COALESCE(il.release_status, 'pending')) = 'released' THEN 1 ELSE 0 END) = 1 THEN '已入库'
                WHEN MAX(CASE WHEN pm.measurement_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '质检'
                WHEN MAX(CASE WHEN ppl.process_step = 'Cleaning' THEN 1 ELSE 0 END) = 1 THEN '清洗'
                WHEN MAX(CASE WHEN ppl.process_step = 'Cutting' THEN 1 ELSE 0 END) = 1 THEN '切割'
                WHEN MAX(CASE WHEN ps.production_schedule_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '已排产'
                ELSE '未排产'
            END AS process_status
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_process_log ppl ON pb.production_batch_id = ppl.production_batch_id
        LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[delivery_plan_id])

    if df.empty:
        return "未排产"
    return str(df.iloc[0]["process_status"])


def advance_delivery_plan_process_status(conn, delivery_plan_id, target_step):
    cursor = conn.cursor()

    schedule_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.trace_key
        FROM production_schedule ps
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        WHERE ps.delivery_plan_id = ?
        ORDER BY ps.production_schedule_id
        LIMIT 1
    """, conn, params=[delivery_plan_id])

    if schedule_df.empty:
        return False, "该交付批次尚未排产，请先创建排产。"

    row = schedule_df.iloc[0]
    production_batch_id = int(row["production_batch_id"])
    required_qty = float(row["required_production_qty"]) if pd.notna(row["required_production_qty"]) else 0.0

    target_step_map = {
        "切割": ("Cutting", "running"),
        "清洗": ("Cleaning", "running"),
        "质检": ("Cleaning", "done"),
    }

    if target_step not in target_step_map:
        return False, "不支持的推进状态。"

    process_step, batch_status = target_step_map[target_step]

    cursor.execute("""
        INSERT INTO production_process_log (
            production_batch_id, process_step, equipment_code, operator_name,
            input_qty, output_qty, scrap_qty, process_status,
            start_time, end_time, remark
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)
    """, (
        production_batch_id,
        process_step,
        f"EQ-{process_step[:3].upper()}-AUTO",
        "Delivery Plan Panel",
        required_qty,
        required_qty,
        0,
        "done" if target_step in ["切割", "清洗"] else "running",
        f"交付批次 {delivery_plan_id} 推进到 {target_step}"
    ))

    cursor.execute("""
        UPDATE production_batch
        SET production_flow_status = ?,
            actual_qty = CASE
                WHEN ? > COALESCE(actual_qty, 0) THEN ?
                ELSE actual_qty
            END
        WHERE production_batch_id = ?
    """, (batch_status, required_qty, required_qty, production_batch_id))

    if target_step == "质检":
        exists_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM production_measurement
            WHERE production_batch_id = ?
        """, conn, params=[production_batch_id])

        if int(exists_df.iloc[0]["cnt"]) == 0:
            cursor.execute("""
                INSERT INTO production_measurement (
                    production_batch_id, quality_status, release_status, inspected_at, release_by
                ) VALUES (?, ?, ?, datetime('now'), ?)
            """, (
                production_batch_id,
                "A",
                "pending",
                "Delivery Plan Panel"
            ))
        else:
            cursor.execute("""
                UPDATE production_measurement
                SET quality_status = 'A',
                    release_status = 'pending',
                    inspected_at = datetime('now'),
                    release_by = 'Delivery Plan Panel'
                WHERE production_batch_id = ?
            """, (production_batch_id,))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = ?
        WHERE delivery_plan_id = ?
    """, (target_step, int(delivery_plan_id)))

    conn.commit()
    return True, f"交付批次 {delivery_plan_id} 已推进到 {target_step}"


def mark_delivery_plan_as_inbound(conn, delivery_plan_id):
    cursor = conn.cursor()

    base_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_qty,
            ps.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.required_production_qty,
            pb.actual_qty,
            oi.product_id,
            oi.spec_id,
            oi.trace_key AS order_trace_key,
            oi.product_spec_text,
            oi.po_no
        FROM delivery_plan dp
        JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        WHERE dp.delivery_plan_id = ?
        ORDER BY ps.production_schedule_id
        LIMIT 1
    """, conn, params=[delivery_plan_id])

    if base_df.empty:
        return False, "该交付批次尚未排产，不能标记已入库。"

    row = base_df.iloc[0]
    production_batch_id = int(row["production_batch_id"])
    batch_no = int(row["delivery_batch_no"])
    planned_delivery_qty = float(row["planned_delivery_qty"]) if pd.notna(row["planned_delivery_qty"]) else 0.0
    actual_qty = float(row["actual_qty"]) if pd.notna(row["actual_qty"]) and float(row["actual_qty"]) > 0 else float(row["required_production_qty"])
    product_id = int(row["product_id"])
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None
    order_trace_key = str(row["order_trace_key"])
    product_spec_text = str(row["product_spec_text"])

    order_linked_inbound_qty = min(actual_qty, planned_delivery_qty)
    extra_spec_inbound_qty = max(actual_qty - planned_delivery_qty, 0.0)

    exists_measure_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[production_batch_id])

    if int(exists_measure_df.iloc[0]["cnt"]) == 0:
        cursor.execute("""
            INSERT INTO production_measurement (
                production_batch_id, quality_status, release_status, inspected_at, release_by
            ) VALUES (?, 'A', 'released', datetime('now'), 'Delivery Plan Panel')
        """, (production_batch_id,))
    else:
        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = 'A',
                release_status = 'released',
                inspected_at = datetime('now'),
                release_by = 'Delivery Plan Panel'
            WHERE production_batch_id = ?
        """, (production_batch_id,))

    # 对应交付批次的订单型库存
    if order_linked_inbound_qty > 0:
        delivery_trace_key = f"{order_trace_key}::DP::{delivery_plan_id}"

        exists_lot_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM inventory_lot
            WHERE production_batch_id = ?
              AND trace_key = ?
        """, conn, params=[production_batch_id, delivery_trace_key])

        if int(exists_lot_df.iloc[0]["cnt"]) == 0:
            lot_code = f"LOT-ORD-{production_batch_id:03d}-{batch_no}"
            cursor.execute("""
                INSERT INTO inventory_lot (
                    production_batch_id, product_id, spec_id, lot_code, trace_key,
                    location, available_qty, reserved_qty, lot_status, release_status,
                    exclusive_customer, forbidden_customer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'available', 'released', '', '')
            """, (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                delivery_trace_key,
                "WH-ORDER",
                order_linked_inbound_qty
            ))
        else:
            cursor.execute("""
                UPDATE inventory_lot
                SET available_qty = ?,
                    lot_status = 'available',
                    release_status = 'released'
                WHERE production_batch_id = ?
                  AND trace_key = ?
            """, (
                order_linked_inbound_qty,
                production_batch_id,
                delivery_trace_key
            ))

    # 多余规格库存
    if extra_spec_inbound_qty > 0:
        spec_trace_key = "__".join([
         "SPEC_STOCK",
         normalize_trace_part(product_spec_text, "NOSPEC"),
         normalize_trace_part(special_process, "STANDARD"),
         normalize_trace_part(material, "UNKNOWN_MATERIAL"),
         ])

        existing_spec_lot_df = pd.read_sql_query("""
            SELECT inventory_lot_id, available_qty
            FROM inventory_lot
            WHERE spec_id = ?
              AND trace_key = ?
              AND location = 'WH-SPEC'
            ORDER BY inventory_lot_id
            LIMIT 1
        """, conn, params=[spec_id, spec_trace_key])

        if existing_spec_lot_df.empty:
            spec_lot_code = f"LOT-SPEC-{spec_id}-{production_batch_id}"
            cursor.execute("""
                INSERT INTO inventory_lot (
                    production_batch_id, product_id, spec_id, lot_code, trace_key,
                    location, available_qty, reserved_qty, lot_status, release_status,
                    exclusive_customer, forbidden_customer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'available', 'released', '', '')
            """, (
                production_batch_id,
                product_id,
                spec_id,
                spec_lot_code,
                spec_trace_key,
                "WH-SPEC",
                extra_spec_inbound_qty
            ))
        else:
            spec_lot_id = int(existing_spec_lot_df.iloc[0]["inventory_lot_id"])
            old_qty = float(existing_spec_lot_df.iloc[0]["available_qty"]) if pd.notna(existing_spec_lot_df.iloc[0]["available_qty"]) else 0.0
            new_qty = old_qty + extra_spec_inbound_qty

            cursor.execute("""
                UPDATE inventory_lot
                SET available_qty = ?,
                    lot_status = 'available',
                    release_status = 'released'
                WHERE inventory_lot_id = ?
            """, (new_qty, spec_lot_id))

    cursor.execute("""
        UPDATE production_batch
        SET production_flow_status = 'done',
            actual_qty = CASE
                WHEN ? > COALESCE(actual_qty, 0) THEN ?
                ELSE actual_qty
            END,
            finished_wh_qty = CASE
                WHEN ? > COALESCE(finished_wh_qty, 0) THEN ?
                ELSE finished_wh_qty
            END
        WHERE production_batch_id = ?
    """, (
        actual_qty, actual_qty,
        actual_qty, actual_qty,
        production_batch_id
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '已入库'
        WHERE delivery_plan_id = ?
    """, (int(delivery_plan_id),))

    conn.commit()

    if extra_spec_inbound_qty > 0:
        return True, f"第 {batch_no} 批已入库；订单库存 {order_linked_inbound_qty:.0f}，多余规格库存 {extra_spec_inbound_qty:.0f}"
    else:
        return True, f"第 {batch_no} 批已入库"






def get_sales_process_status_for_order(conn, order_item_id):
    df = pd.read_sql_query("""
        SELECT
            CASE
                WHEN MAX(CASE WHEN il.inventory_lot_id IS NOT NULL AND lower(COALESCE(il.release_status, 'pending')) = 'released' THEN 1 ELSE 0 END) = 1 THEN '已入库'
                WHEN MAX(CASE WHEN pm.measurement_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '质检'
                WHEN MAX(CASE WHEN ppl.process_step = 'Cleaning' THEN 1 ELSE 0 END) = 1 THEN '清洗'
                WHEN MAX(CASE WHEN ppl.process_step = 'Cutting' THEN 1 ELSE 0 END) = 1 THEN '切割'
                WHEN MAX(CASE WHEN ps.production_schedule_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '已排产'
                ELSE '未排产'
            END AS sales_process_status
        FROM order_item oi
        LEFT JOIN production_schedule ps ON oi.order_item_id = ps.order_item_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_process_log ppl ON pb.production_batch_id = ppl.production_batch_id
        LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
        WHERE oi.order_item_id = ?
    """, conn, params=[order_item_id])

    if df.empty:
        return "未排产"
    return str(df.iloc[0]["sales_process_status"])

def advance_order_process_status(conn, order_item_id, target_step):
    cursor = conn.cursor()

    schedule_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.trace_key
        FROM production_schedule ps
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        WHERE ps.order_item_id = ?
        ORDER BY ps.production_schedule_id
        LIMIT 1
    """, conn, params=[order_item_id])

    if schedule_df.empty:
        return False, "该订单尚未排产，请先创建排产。"

    row = schedule_df.iloc[0]
    production_batch_id = int(row["production_batch_id"])
    required_qty = float(row["required_production_qty"]) if pd.notna(row["required_production_qty"]) else 0.0
    trace_key = str(row["trace_key"])

    target_step_map = {
        "切割": ("Cutting", "running"),
        "清洗": ("Cleaning", "running"),
        "质检": ("Cleaning", "done"),
    }

    if target_step not in target_step_map:
        return False, "不支持的推进状态。"

    process_step, batch_status = target_step_map[target_step]

    # 插入过程日志
    cursor.execute("""
        INSERT INTO production_process_log (
            production_batch_id, process_step, equipment_code, operator_name,
            input_qty, output_qty, scrap_qty, process_status,
            start_time, end_time, remark
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)
    """, (
        production_batch_id,
        process_step,
        f"EQ-{process_step[:3].upper()}-AUTO",
        "Sales Panel",
        required_qty,
        required_qty,
        0,
        "done" if target_step in ["切割", "清洗"] else "running",
        f"销售看板推进到{target_step}"
    ))

    # 更新批次主状态
    cursor.execute("""
        UPDATE production_batch
        SET production_flow_status = ?,
            actual_qty = CASE
                WHEN ? > COALESCE(actual_qty, 0) THEN ?
                ELSE actual_qty
            END
        WHERE production_batch_id = ?
    """, (batch_status, required_qty, required_qty, production_batch_id))

    # 如果推进到质检，就生成/更新质检记录
    if target_step == "质检":
        exists_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM production_measurement
            WHERE production_batch_id = ?
        """, conn, params=[production_batch_id])

        if int(exists_df.iloc[0]["cnt"]) == 0:
            cursor.execute("""
                INSERT INTO production_measurement (
                    production_batch_id, quality_status, release_status, inspected_at, release_by
                ) VALUES (?, ?, ?, datetime('now'), ?)
            """, (
                production_batch_id,
                "A",
                "pending",
                "Sales Panel"
            ))
        else:
            cursor.execute("""
                UPDATE production_measurement
                SET quality_status = 'A',
                    release_status = 'pending',
                    inspected_at = datetime('now'),
                    release_by = 'Sales Panel'
                WHERE production_batch_id = ?
            """, (production_batch_id,))

    conn.commit()
    return True, f"订单 {order_item_id} 已推进到 {target_step}"

def mark_order_as_inbound(conn, order_item_id):
    cursor = conn.cursor()

    base_df = pd.read_sql_query("""
        SELECT
            ps.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.required_production_qty,
            pb.actual_qty,
            oi.product_id,
            oi.spec_id,
            oi.trace_key AS order_trace_key,
            oi.ordered_qty,
            oi.shipped_qty,
            oi.product_spec_text
        FROM production_schedule ps
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        JOIN order_item oi ON ps.order_item_id = oi.order_item_id
        WHERE ps.order_item_id = ?
        ORDER BY ps.production_schedule_id
        LIMIT 1
    """, conn, params=[order_item_id])

    if base_df.empty:
        return False, "该订单尚未排产，不能标记已入库。"

    row = base_df.iloc[0]
    production_batch_id = int(row["production_batch_id"])
    batch_code = str(row["batch_code"])
    batch_trace_key = str(row["trace_key"])
    order_trace_key = str(row["order_trace_key"])
    product_id = int(row["product_id"])
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None

    ordered_qty = float(row["ordered_qty"]) if pd.notna(row["ordered_qty"]) else 0.0
    shipped_qty = float(row["shipped_qty"]) if pd.notna(row["shipped_qty"]) else 0.0
    actual_qty = float(row["actual_qty"]) if pd.notna(row["actual_qty"]) and float(row["actual_qty"]) > 0 else float(row["required_production_qty"])
    product_spec_text = str(row["product_spec_text"])

    # 当前订单尚未满足的需求量
    demand_gap = max(ordered_qty - shipped_qty, 0.0)

    # 拆分为：
    # 1) 订单型入库数量
    # 2) 规格型多余库存数量
    order_linked_inbound_qty = min(actual_qty, demand_gap)
    extra_spec_inbound_qty = max(actual_qty - demand_gap, 0.0)

    # 先补质检为 released
    exists_measure_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[production_batch_id])

    if int(exists_measure_df.iloc[0]["cnt"]) == 0:
        cursor.execute("""
            INSERT INTO production_measurement (
                production_batch_id, quality_status, release_status, inspected_at, release_by
            ) VALUES (?, 'A', 'released', datetime('now'), 'Sales Panel')
        """, (production_batch_id,))
    else:
        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = 'A',
                release_status = 'released',
                inspected_at = datetime('now'),
                release_by = 'Sales Panel'
            WHERE production_batch_id = ?
        """, (production_batch_id,))

    # 1) 订单型库存：优先满足订单缺口
    if order_linked_inbound_qty > 0:
        exists_lot_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM inventory_lot
            WHERE production_batch_id = ?
              AND trace_key = ?
        """, conn, params=[production_batch_id, order_trace_key])

        if int(exists_lot_df.iloc[0]["cnt"]) == 0:
            lot_code = f"LOT-ORD-{production_batch_id:03d}"
            cursor.execute("""
                INSERT INTO inventory_lot (
                    production_batch_id, product_id, spec_id, lot_code, trace_key,
                    location, available_qty, reserved_qty, lot_status, release_status,
                    exclusive_customer, forbidden_customer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'available', 'released', '', '')
            """, (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                order_trace_key,
                "WH-ORDER",
                order_linked_inbound_qty
            ))
        else:
            cursor.execute("""
                UPDATE inventory_lot
                SET available_qty = ?,
                    lot_status = 'available',
                    release_status = 'released'
                WHERE production_batch_id = ?
                  AND trace_key = ?
            """, (
                order_linked_inbound_qty,
                production_batch_id,
                order_trace_key
            ))

    # 2) 多余规格库存：不按订单，只按规格入库
    if extra_spec_inbound_qty > 0:
        spec_trace_key = f"SPEC_STOCK::{spec_id}::{product_spec_text}"

        existing_spec_lot_df = pd.read_sql_query("""
            SELECT inventory_lot_id, available_qty
            FROM inventory_lot
            WHERE spec_id = ?
              AND trace_key = ?
              AND location = 'WH-SPEC'
            ORDER BY inventory_lot_id
            LIMIT 1
        """, conn, params=[spec_id, spec_trace_key])

        if existing_spec_lot_df.empty:
            spec_lot_code = f"LOT-SPEC-{spec_id}-{production_batch_id}"
            cursor.execute("""
                INSERT INTO inventory_lot (
                    production_batch_id, product_id, spec_id, lot_code, trace_key,
                    location, available_qty, reserved_qty, lot_status, release_status,
                    exclusive_customer, forbidden_customer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'available', 'released', '', '')
            """, (
                production_batch_id,
                product_id,
                spec_id,
                spec_lot_code,
                spec_trace_key,
                "WH-SPEC",
                extra_spec_inbound_qty
            ))
        else:
            spec_lot_id = int(existing_spec_lot_df.iloc[0]["inventory_lot_id"])
            old_qty = float(existing_spec_lot_df.iloc[0]["available_qty"]) if pd.notna(existing_spec_lot_df.iloc[0]["available_qty"]) else 0.0
            new_qty = old_qty + extra_spec_inbound_qty

            cursor.execute("""
                UPDATE inventory_lot
                SET available_qty = ?,
                    lot_status = 'available',
                    release_status = 'released'
                WHERE inventory_lot_id = ?
            """, (new_qty, spec_lot_id))

    # 更新批次主表
    cursor.execute("""
        UPDATE production_batch
        SET production_flow_status = 'done',
            actual_qty = CASE
                WHEN ? > COALESCE(actual_qty, 0) THEN ?
                ELSE actual_qty
            END,
            finished_wh_qty = CASE
                WHEN ? > COALESCE(finished_wh_qty, 0) THEN ?
                ELSE finished_wh_qty
            END
        WHERE production_batch_id = ?
    """, (
        actual_qty, actual_qty,
        actual_qty, actual_qty,
        production_batch_id
    ))

    conn.commit()

    if extra_spec_inbound_qty > 0:
        return True, (
            f"订单 {order_item_id} 已标记为已入库；"
            f"其中订单库存 {order_linked_inbound_qty:.0f}，"
            f"多余规格库存 {extra_spec_inbound_qty:.0f}"
        )
    else:
        return True, f"订单 {order_item_id} 已标记为已入库"




# =========================
# 商业分析函数
# =========================
def load_order_risk_base(conn):
    return pd.read_sql_query("""
        WITH delivery_sum AS (
            SELECT
                order_item_id,
                COALESCE(SUM(actual_delivery_qty), 0) AS delivered_qty
            FROM delivery_plan
            GROUP BY order_item_id
        ),
        released_lot AS (
            SELECT
                trace_key,
                COALESCE(SUM(available_qty), 0) AS released_available_qty
            FROM inventory_lot
            WHERE lower(COALESCE(release_status, 'pending')) = 'released'
              AND lower(COALESCE(lot_status, 'hold')) IN ('available', 'reserved')
            GROUP BY trace_key
        ),
        batch_status AS (
            SELECT
                oi.trace_key,
                MAX(COALESCE(pb.production_flow_status, 'planned')) AS production_flow_status,
                COUNT(DISTINCT pb.production_batch_id) AS batch_count
            FROM order_item oi
            LEFT JOIN production_schedule ps ON oi.order_item_id = ps.order_item_id
            LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
            GROUP BY oi.trace_key
        ),
        release_flag AS (
            SELECT
                oi.trace_key,
                MAX(
                    CASE
                        WHEN lower(COALESCE(pm.release_status, 'pending')) = 'released' THEN 1
                        ELSE 0
                    END
                ) AS has_released_batch
            FROM order_item oi
            LEFT JOIN production_schedule ps ON oi.order_item_id = ps.order_item_id
            LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
            GROUP BY oi.trace_key
        )
        SELECT
            oi.order_item_id,
            oi.trace_key,
            oi.po_no,
            oi.product_spec_text,
            oi.product_type_text,
            oi.ordered_qty,
            COALESCE(ds.delivered_qty, 0) AS delivered_qty,
            (oi.ordered_qty - COALESCE(ds.delivered_qty, 0)) AS undelivered_qty,
            o.overall_deadline,
            o.order_status,
            oi.item_status,
            c.customer_name,
            COALESCE(rl.released_available_qty, 0) AS released_available_qty,
            COALESCE(bs.production_flow_status, 'planned') AS production_flow_status,
            COALESCE(bs.batch_count, 0) AS batch_count,
            COALESCE(rf.has_released_batch, 0) AS has_released_batch,
            julianday(o.overall_deadline) - julianday(date('now')) AS days_to_deadline
        FROM order_item oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN delivery_sum ds ON oi.order_item_id = ds.order_item_id
        LEFT JOIN released_lot rl ON oi.trace_key = rl.trace_key
        LEFT JOIN batch_status bs ON oi.trace_key = bs.trace_key
        LEFT JOIN release_flag rf ON oi.trace_key = rf.trace_key
        ORDER BY o.overall_deadline, oi.order_item_id
    """, conn)


def enrich_order_risk(df):
    if df.empty:
        return df

    df = df.copy()
    df["days_to_deadline"] = pd.to_numeric(df["days_to_deadline"], errors="coerce").fillna(999)
    df["undelivered_qty"] = pd.to_numeric(df["undelivered_qty"], errors="coerce").fillna(0)
    df["released_available_qty"] = pd.to_numeric(df["released_available_qty"], errors="coerce").fillna(0)
    df["ordered_qty"] = pd.to_numeric(df["ordered_qty"], errors="coerce").fillna(0)

    df["coverage_gap"] = (df["undelivered_qty"] - df["released_available_qty"]).clip(lower=0)
    df["undelivered_ratio"] = df.apply(
        lambda r: (r["undelivered_qty"] / r["ordered_qty"]) if r["ordered_qty"] > 0 else 0,
        axis=1
    )

    risk_score = []
    urgency_score = []

    for _, r in df.iterrows():
        score = 0
        urgent = 0

        # 交期
        if r["days_to_deadline"] <= 3:
            score += 40
            urgent += 40
        elif r["days_to_deadline"] <= 7:
            score += 25
            urgent += 25
        elif r["days_to_deadline"] <= 14:
            score += 10
            urgent += 10

        # 未交付比例
        if r["undelivered_ratio"] >= 0.8:
            score += 30
            urgent += 30
        elif r["undelivered_ratio"] >= 0.5:
            score += 20
            urgent += 20
        elif r["undelivered_ratio"] > 0:
            score += 10
            urgent += 10

        # released 库存是否覆盖
        if r["coverage_gap"] > 0:
            score += 20
            urgent += 15

        # 批次状态
        status = str(r["production_flow_status"]).lower()
        if status == "hold":
            score += 30
            urgent += 15
        elif status == "planned":
            score += 15
            urgent += 10
        elif status == "running":
            score += 8
            urgent += 5

        # 无已放行批次
        if int(r["has_released_batch"]) == 0:
            score += 10

        risk_score.append(score)
        urgency_score.append(urgent)

    df["risk_score"] = risk_score
    df["urgency_score"] = urgency_score

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 29, 59, 999],
        labels=["低", "中", "高"]
    )

    df["urgency_level"] = pd.cut(
        df["urgency_score"],
        bins=[-1, 24, 49, 999],
        labels=["低", "中", "高"]
    )

    df["risk_reason"] = df.apply(build_risk_reason, axis=1)
    return df


def build_risk_reason(r):
    reasons = []
    if r["days_to_deadline"] <= 3:
        reasons.append("交期≤3天")
    elif r["days_to_deadline"] <= 7:
        reasons.append("交期≤7天")

    if r["undelivered_ratio"] >= 0.5:
        reasons.append("未交付比例高")

    if r["coverage_gap"] > 0:
        reasons.append("released库存不足")

    status = str(r["production_flow_status"]).lower()
    if status == "hold":
        reasons.append("批次Hold")
    elif status == "planned":
        reasons.append("仍处计划阶段")
    elif status == "running":
        reasons.append("仍在生产中")

    if int(r["has_released_batch"]) == 0:
        reasons.append("暂无已放行批次")

    return " / ".join(reasons) if reasons else "风险较低"


def load_production_analysis_base(conn):
    return pd.read_sql_query("""
        WITH process_agg AS (
            SELECT
                production_batch_id,
                COALESCE(SUM(input_qty), 0) AS total_input_qty,
                COALESCE(SUM(output_qty), 0) AS total_output_qty,
                COALESCE(SUM(scrap_qty), 0) AS total_scrap_qty
            FROM production_process_log
            GROUP BY production_batch_id
        ),
        linked_order AS (
            SELECT
                ps.production_batch_id,
                oi.po_no,
                oi.trace_key,
                oi.product_spec_text,
                oi.ordered_qty,
                o.overall_deadline,
                c.customer_name
            FROM production_schedule ps
            JOIN order_item oi ON ps.order_item_id = oi.order_item_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN customer c ON o.customer_id = c.customer_id
        )
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.special_process,
            pb.production_flow_status,
            pb.required_production_qty,
            pb.actual_qty,
            pb.semi_finished_wh_qty,
            pb.finished_wh_qty,
            lo.po_no,
            lo.product_spec_text,
            lo.overall_deadline,
            lo.customer_name,
            COALESCE(pa.total_input_qty, 0) AS total_input_qty,
            COALESCE(pa.total_output_qty, 0) AS total_output_qty,
            COALESCE(pa.total_scrap_qty, 0) AS total_scrap_qty,
            julianday(lo.overall_deadline) - julianday(date('now')) AS days_to_deadline
        FROM production_batch pb
        LEFT JOIN process_agg pa ON pb.production_batch_id = pa.production_batch_id
        LEFT JOIN linked_order lo ON pb.production_batch_id = lo.production_batch_id
        ORDER BY pb.production_batch_id
    """, conn)


def enrich_production_analysis(df):
    if df.empty:
        return df

    df = df.copy()
    for c in ["required_production_qty", "actual_qty", "total_input_qty", "total_output_qty", "total_scrap_qty"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["days_to_deadline"] = pd.to_numeric(df["days_to_deadline"], errors="coerce").fillna(999)
    df["remaining_qty"] = (df["required_production_qty"] - df["actual_qty"]).clip(lower=0)
    df["completion_rate"] = df.apply(
        lambda r: (r["actual_qty"] / r["required_production_qty"]) if r["required_production_qty"] > 0 else 0,
        axis=1
    )
    df["scrap_rate"] = df.apply(
        lambda r: (r["total_scrap_qty"] / r["total_input_qty"]) if r["total_input_qty"] > 0 else 0,
        axis=1
    )

    def batch_risk(row):
        score = 0
        if row["days_to_deadline"] <= 3:
            score += 30
        elif row["days_to_deadline"] <= 7:
            score += 20

        status = str(row["production_flow_status"]).lower()
        if status == "hold":
            score += 35
        elif status == "planned":
            score += 20
        elif status == "running":
            score += 10

        if row["completion_rate"] < 0.5:
            score += 20
        elif row["completion_rate"] < 0.8:
            score += 10

        if row["scrap_rate"] > 0.08:
            score += 15
        elif row["scrap_rate"] > 0.03:
            score += 8

        return score

    df["batch_risk_score"] = df.apply(batch_risk, axis=1)
    df["batch_risk_level"] = pd.cut(
        df["batch_risk_score"],
        bins=[-1, 24, 54, 999],
        labels=["低", "中", "高"]
    )
    return df


def load_inventory_analysis_base(conn):
    return pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            production_batch_id,
            product_id,
            spec_id,
            lot_code,
            trace_key,
            location,
            available_qty,
            reserved_qty,
            lot_status,
            release_status,
            exclusive_customer,
            forbidden_customer,
            last_out_qty,
            last_out_time,
            created_at
        FROM inventory_lot
        ORDER BY inventory_lot_id
    """, conn)


def enrich_inventory_analysis(df):
    if df.empty:
        return df

    df = df.copy()
    for c in ["available_qty", "reserved_qty", "last_out_qty"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["is_shippable"] = df.apply(
        lambda r: 1 if str(r["release_status"]).lower() == "released"
                      and str(r["lot_status"]).lower() in ["available", "reserved"]
                      and r["available_qty"] > 0 else 0,
        axis=1
    )

    def inv_state(row):
        if str(row["release_status"]).lower() != "released":
            return "待放行/受限"
        if str(row["lot_status"]).lower() == "hold":
            return "Hold"
        if row["available_qty"] <= 0:
            return "无可用库存"
        return "可出货"

    df["inventory_state_analysis"] = df.apply(inv_state, axis=1)
    return df


def build_urgent_product_summary(order_df):
    if order_df.empty:
        return pd.DataFrame()

    result = (
        order_df.groupby("product_spec_text", dropna=False)
        .agg(
            订单数=("order_item_id", "count"),
            总未交付量=("undelivered_qty", "sum"),
            平均风险分=("risk_score", "mean"),
            平均紧急分=("urgency_score", "mean"),
            最短剩余天数=("days_to_deadline", "min"),
        )
        .reset_index()
        .rename(columns={"product_spec_text": "产品规格"})
        .sort_values(["平均紧急分", "总未交付量"], ascending=[False, False])
    )
    return result


def build_customer_demand_summary(order_df):
    if order_df.empty:
        return pd.DataFrame()

    result = (
        order_df.groupby("customer_name", dropna=False)
        .agg(
            订单数=("order_item_id", "count"),
            总订单量=("ordered_qty", "sum"),
            已交付量=("delivered_qty", "sum"),
            未交付量=("undelivered_qty", "sum"),
            平均风险分=("risk_score", "mean"),
        )
        .reset_index()
        .rename(columns={"customer_name": "客户名称"})
        .sort_values("未交付量", ascending=False)
    )
    return result


def build_inventory_state_summary(inv_df):
    if inv_df.empty:
        return pd.DataFrame()

    result = (
        inv_df.groupby("inventory_state_analysis", dropna=False)
        .agg(
            Lot数=("inventory_lot_id", "count"),
            可用数量=("available_qty", "sum"),
            预留数量=("reserved_qty", "sum"),
        )
        .reset_index()
        .rename(columns={"inventory_state_analysis": "库存分析状态"})
    )
    return result


def build_shippable_resource_summary(order_df, inv_df):
    total_undelivered = float(order_df["undelivered_qty"].sum()) if not order_df.empty else 0
    total_shippable = float(inv_df.loc[inv_df["is_shippable"] == 1, "available_qty"].sum()) if not inv_df.empty else 0
    coverage_rate = (total_shippable / total_undelivered) if total_undelivered > 0 else 1.0

    return {
        "total_undelivered": total_undelivered,
        "total_shippable": total_shippable,
        "coverage_rate": coverage_rate,
    }


def evaluate_urgent_insert(conn, product_spec_text, urgent_qty, urgent_deadline, special_process=None):
    # 订单基础
    order_df = enrich_order_risk(load_order_risk_base(conn))
    if order_df.empty:
        return {
            "结论": "无法判断",
            "说明": "当前没有足够订单数据用于插单评估。",
            "已放行库存": 0,
            "在制可补量": 0,
            "理论总可用量": 0,
            "加急需求量": urgent_qty,
            "受影响订单": pd.DataFrame(),
            "建议优先批次": pd.DataFrame(),
            "建议优先Lot": pd.DataFrame(),
            "建议动作": [],
        }

    # 同规格订单
    related_orders = order_df[
        order_df["product_spec_text"].fillna("").astype(str) == str(product_spec_text)
    ].copy()

    # 资源池
    resource_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.po_no,
            oi.trace_key,
            oi.product_spec_text,
            oi.product_type_text,
            o.overall_deadline,

            il.inventory_lot_id,
            il.lot_code,
            il.location,
            il.available_qty,
            il.reserved_qty,
            il.release_status,
            il.lot_status,
            il.last_out_time,

            pb.production_batch_id,
            pb.batch_code,
            pb.special_process,
            pb.production_flow_status,
            pb.required_production_qty,
            pb.actual_qty,
            pb.finished_wh_qty,
            pb.semi_finished_wh_qty,

            pm.release_status AS batch_release_status,
            pm.quality_status
        FROM order_item oi
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN inventory_lot il ON oi.trace_key = il.trace_key
        LEFT JOIN production_schedule ps ON oi.order_item_id = ps.order_item_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
    """, conn)

    if resource_df.empty:
        return {
            "结论": "无法判断",
            "说明": "当前没有足够资源数据用于插单评估。",
            "已放行库存": 0,
            "在制可补量": 0,
            "理论总可用量": 0,
            "加急需求量": urgent_qty,
            "受影响订单": pd.DataFrame(),
            "建议优先批次": pd.DataFrame(),
            "建议优先Lot": pd.DataFrame(),
            "建议动作": [],
        }

    df = resource_df.copy()
    for c in [
        "available_qty", "reserved_qty",
        "required_production_qty", "actual_qty",
        "finished_wh_qty", "semi_finished_wh_qty"
    ]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    matched = df[df["product_spec_text"].fillna("").astype(str) == str(product_spec_text)].copy()

    if special_process and "special_process" in matched.columns:
        matched = matched[matched["special_process"].fillna("").astype(str) == str(special_process)]

    # 已放行库存
    released_lot_df = matched[
        (matched["release_status"].fillna("").str.lower() == "released") &
        (matched["lot_status"].fillna("").str.lower().isin(["available", "reserved"])) &
        (matched["available_qty"] > 0)
    ].copy()

    released_available = released_lot_df["available_qty"].sum()

    # 在制可补量
    batch_df = matched[
        matched["production_batch_id"].notna()
    ].copy()

    batch_df["in_production_capacity"] = batch_df.apply(
        lambda r: max(r["required_production_qty"] - r["actual_qty"], 0),
        axis=1
    )

    in_production_capacity = batch_df[
        batch_df["production_flow_status"].fillna("").str.lower().isin(["planned", "running", "done"])
    ]["in_production_capacity"].sum()

    total_possible = float(released_available + in_production_capacity)

    today = pd.Timestamp.today().normalize()
    deadline_days = (pd.to_datetime(urgent_deadline) - today).days if urgent_deadline else 999

    # 结论
    if released_available >= urgent_qty:
        conclusion = "可直接满足"
        note = f"当前已放行可用库存 {released_available:.0f}，可覆盖加急需求 {urgent_qty:.0f}。"
    elif total_possible >= urgent_qty:
        if deadline_days <= 3:
            conclusion = "理论可完成，但存在插单风险"
            note = f"已放行库存不足，但在制+库存合计 {total_possible:.0f}，接近可覆盖；交期很近，可能挤压其他订单。"
        else:
            conclusion = "可插单完成"
            note = f"已放行库存 {released_available:.0f}，在制可补 {in_production_capacity:.0f}，合计 {total_possible:.0f}，可覆盖需求。"
    else:
        conclusion = "大概率无法按期完成"
        note = f"已放行库存 {released_available:.0f}，在制可补 {in_production_capacity:.0f}，合计仅 {total_possible:.0f}，不足覆盖需求 {urgent_qty:.0f}。"

    # 受影响订单
    affected_df = pd.DataFrame()
    if not related_orders.empty:
        impact_orders = related_orders.copy()
        impact_orders = impact_orders[impact_orders["undelivered_qty"] > 0].copy()
        impact_orders = impact_orders.sort_values(
            ["days_to_deadline", "risk_score", "po_no"],
            ascending=[True, False, True]
        ).reset_index(drop=True)

        remaining_pool = total_possible - float(urgent_qty)

        impacted_rows = []
        for _, row in impact_orders.iterrows():
            order_need = float(row["undelivered_qty"])
            before_cov = min(total_possible, order_need)
            after_cov = min(max(remaining_pool, 0), order_need)
            lost_qty = max(before_cov - after_cov, 0)

            if lost_qty > 0:
                impacted_rows.append({
                    "po_no": row["po_no"],
                    "customer_name": row["customer_name"],
                    "product_spec_text": row["product_spec_text"],
                    "overall_deadline": row["overall_deadline"],
                    "undelivered_qty": order_need,
                    "risk_level": row["risk_level"],
                    "risk_reason": row["risk_reason"],
                    "被挤压资源量": lost_qty,
                    "插单后剩余可覆盖量": after_cov,
                    "影响判断": "可能延期" if after_cov < order_need else "轻微影响"
                })

            remaining_pool -= order_need
            if remaining_pool <= 0:
                remaining_pool = 0

        if impacted_rows:
            affected_df = pd.DataFrame(impacted_rows).sort_values(
                ["被挤压资源量", "overall_deadline"],
                ascending=[False, True]
            ).reset_index(drop=True)

    # 建议优先Lot
    suggest_lot_df = pd.DataFrame()
    if not released_lot_df.empty:
        lot_cols = [
            "lot_code", "location", "available_qty", "reserved_qty",
            "release_status", "lot_status", "trace_key", "last_out_time"
        ]
        suggest_lot_df = (
            released_lot_df[lot_cols]
            .drop_duplicates()
            .sort_values(["available_qty", "last_out_time"], ascending=[False, True])
            .head(5)
            .reset_index(drop=True)
        )

    # 建议优先批次
    suggest_batch_df = pd.DataFrame()
    if not batch_df.empty:
        batch_pick = batch_df.copy()
        batch_pick["批次可补量"] = batch_pick["in_production_capacity"]
        batch_pick["批次紧急度"] = batch_pick.apply(
            lambda r: (
                50 if str(r["production_flow_status"]).lower() == "running" else
                35 if str(r["production_flow_status"]).lower() == "done" else
                20 if str(r["production_flow_status"]).lower() == "planned" else
                5
            ) +
            (20 if str(r["batch_release_status"]).lower() == "pending" else 0) +
            (30 if str(r["production_flow_status"]).lower() == "hold" else 0),
            axis=1
        )

        suggest_batch_df = (
            batch_pick[[
                "batch_code", "production_flow_status", "batch_release_status",
                "quality_status", "required_production_qty", "actual_qty",
                "批次可补量", "finished_wh_qty", "semi_finished_wh_qty", "trace_key"
            ]]
            .drop_duplicates()
            .sort_values(["批次可补量", "finished_wh_qty", "semi_finished_wh_qty"], ascending=[False, False, False])
            .head(5)
            .reset_index(drop=True)
        )

    # 建议动作
    action_list = []

    if released_available >= urgent_qty:
        action_list.append("建议优先直接锁定已放行 Lot，先满足加急单。")
    else:
        if not suggest_lot_df.empty:
            action_list.append("建议先检查并优先分配可用数量最大的已放行 Lot。")

        if not suggest_batch_df.empty:
            top_batch = suggest_batch_df.iloc[0]
            if str(top_batch["batch_release_status"]).lower() == "pending":
                action_list.append(f"建议优先完成批次 {top_batch['batch_code']} 的检验/放行。")
            elif str(top_batch["production_flow_status"]).lower() == "running":
                action_list.append(f"建议优先推进在制批次 {top_batch['batch_code']} 完工。")
            elif str(top_batch["production_flow_status"]).lower() == "planned":
                action_list.append(f"建议优先将计划批次 {top_batch['batch_code']} 提前插入生产。")
            elif str(top_batch["production_flow_status"]).lower() == "hold":
                action_list.append(f"建议优先处理 Hold 批次 {top_batch['batch_code']} 异常。")

    if affected_df is not None and not affected_df.empty:
        top_order = affected_df.iloc[0]
        action_list.append(f"若插单执行，最先受影响的订单是 {top_order['po_no']}，建议提前沟通交期。")

    if total_possible < urgent_qty:
        action_list.append("当前资源总量不足，建议追加生产或调整交期承诺。")

    return {
        "结论": conclusion,
        "说明": note,
        "已放行库存": float(released_available),
        "在制可补量": float(in_production_capacity),
        "理论总可用量": float(total_possible),
        "加急需求量": float(urgent_qty),
        "受影响订单": affected_df,
        "建议优先批次": suggest_batch_df,
        "建议优先Lot": suggest_lot_df,
        "建议动作": action_list,
    }

def render_sales_business_analysis(conn):
    st.subheader("销售商业分析")

    base_df = load_order_risk_base(conn)
    analysis_df = enrich_order_risk(base_df)

    if analysis_df.empty:
        st.info("暂无订单分析数据。")
        return

    total_orders = int(analysis_df["order_item_id"].nunique())
    total_undelivered = float(analysis_df["undelivered_qty"].sum())
    high_risk_orders = int((analysis_df["risk_level"] == "高").sum())
    urgent_orders = int((analysis_df["urgency_level"] == "高").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("订单数", total_orders)
    c2.metric("总未交付量", f"{total_undelivered:.0f}")
    c3.metric("高风险订单数", high_risk_orders)
    c4.metric("高紧急订单数", urgent_orders)

    st.markdown("### 哪些订单最可能延期")
    risk_cols = [
        "po_no", "customer_name", "product_spec_text", "overall_deadline",
        "undelivered_qty", "released_available_qty", "production_flow_status",
        "risk_score", "risk_level", "risk_reason"
    ]
    risk_top = analysis_df.sort_values(["risk_score", "undelivered_qty"], ascending=[False, False])[risk_cols].head(10)
    show_df(risk_top, hide_index=True)

    st.markdown("### 哪些产品比较急")
    urgent_product_df = build_urgent_product_summary(analysis_df)
    show_df(urgent_product_df.head(10), hide_index=True)

    st.markdown("### 客户需求分析")
    customer_summary = build_customer_demand_summary(analysis_df)
    show_df(customer_summary.head(10), hide_index=True)

    with st.expander("查看销售分析明细数据"):
        show_df(analysis_df, hide_index=True)


def render_production_business_analysis(conn):
    st.subheader("生产商业分析")

    prod_df = enrich_production_analysis(load_production_analysis_base(conn))
    if prod_df.empty:
        st.info("暂无生产分析数据。")
        return

    total_batches = int(prod_df["production_batch_id"].nunique())
    running_batches = int((prod_df["production_flow_status"].astype(str).str.lower() == "running").sum())
    hold_batches = int((prod_df["production_flow_status"].astype(str).str.lower() == "hold").sum())
    avg_completion = float(prod_df["completion_rate"].mean()) if not prod_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("批次数", total_batches)
    c2.metric("在制批次", running_batches)
    c3.metric("Hold批次", hold_batches)
    c4.metric("平均达成率", f"{avg_completion:.1%}")

    st.markdown("### 批次延期/异常风险")
    risk_cols = [
        "batch_code", "po_no", "customer_name", "special_process",
        "production_flow_status", "required_production_qty", "actual_qty",
        "remaining_qty", "completion_rate", "scrap_rate",
        "days_to_deadline", "batch_risk_score", "batch_risk_level"
    ]
    risk_df = prod_df.sort_values(["batch_risk_score", "remaining_qty"], ascending=[False, False])[risk_cols].head(10)
    show_df(risk_df, hide_index=True)

    st.markdown("### 工艺瓶颈分析")
    process_summary = (
        prod_df.groupby("special_process", dropna=False)
        .agg(
            批次数=("production_batch_id", "count"),
            平均达成率=("completion_rate", "mean"),
            平均报废率=("scrap_rate", "mean"),
            平均风险分=("batch_risk_score", "mean"),
        )
        .reset_index()
        .rename(columns={"special_process": "特殊工艺"})
        .sort_values("平均风险分", ascending=False)
    )
    show_df(process_summary, hide_index=True)

    st.markdown("### 加急单插单评估")
    order_base = load_order_risk_base(conn)
    spec_options = sorted([x for x in order_base["product_spec_text"].dropna().unique().tolist() if str(x).strip() != ""])
    if spec_options:
        col1, col2, col3 = st.columns(3)
        with col1:
            urgent_spec = st.selectbox("加急产品规格", spec_options, key="urgent_spec_eval")
        with col2:
            urgent_qty = st.number_input("加急数量", min_value=1.0, value=200.0, step=10.0, key="urgent_qty_eval")
        with col3:
            urgent_deadline = st.date_input("目标交期", value=date.today(), key="urgent_deadline_eval")

        urgent_result = evaluate_urgent_insert(conn, urgent_spec, urgent_qty, str(urgent_deadline))

        st.info(f"**结论：{urgent_result['结论']}**")
        st.write(urgent_result["说明"])

        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("已放行库存", f"{urgent_result['已放行库存']:.0f}")
        rc2.metric("在制可补量", f"{urgent_result['在制可补量']:.0f}")
        rc3.metric("理论总可用量", f"{urgent_result['理论总可用量']:.0f}")
        rc4.metric("加急需求量", f"{urgent_result['加急需求量']:.0f}")

        st.markdown("#### 会影响哪几个订单")
        affected_df = urgent_result.get("受影响订单", pd.DataFrame())
        if affected_df is None or affected_df.empty:
            st.success("当前评估下，未识别出明显被挤压的同规格订单。")
        else:
            show_df(affected_df, hide_index=True)

        st.markdown("#### 建议优先处理的 Lot")
        lot_df = urgent_result.get("建议优先Lot", pd.DataFrame())
        if lot_df is None or lot_df.empty:
            st.info("当前没有可直接建议的已放行 Lot。")
        else:
            show_df(lot_df, hide_index=True)

        st.markdown("#### 建议优先处理的批次")
        batch_df = urgent_result.get("建议优先批次", pd.DataFrame())
        if batch_df is None or batch_df.empty:
            st.info("当前没有可直接建议的批次。")
        else:
            show_df(batch_df, hide_index=True)

        st.markdown("#### 系统建议动作")
        actions = urgent_result.get("建议动作", [])
        if not actions:
            st.info("当前没有额外建议动作。")
        else:
            for i, action in enumerate(actions, start=1):
                st.write(f"{i}. {action}")

    else:
        st.info("暂无可用于插单评估的产品规格数据。")

    with st.expander("查看生产分析明细数据"):
        show_df(prod_df, hide_index=True)


def render_inventory_business_analysis(conn):
    st.subheader("库存 / 出货商业分析")

    inv_df = enrich_inventory_analysis(load_inventory_analysis_base(conn))
    order_df = enrich_order_risk(load_order_risk_base(conn))

    if inv_df.empty:
        st.info("暂无库存分析数据。")
        return

    resource_summary = build_shippable_resource_summary(order_df, inv_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("可出货库存量", f"{resource_summary['total_shippable']:.0f}")
    c2.metric("未交付需求量", f"{resource_summary['total_undelivered']:.0f}")
    c3.metric("出货覆盖率", f"{resource_summary['coverage_rate']:.1%}")
    c4.metric("Hold/受限 Lot 数", int((inv_df["inventory_state_analysis"] != "可出货").sum()))

    st.markdown("### 可出货资源是否足够")
    if resource_summary["coverage_rate"] >= 1:
        st.success("当前 released 可出货资源理论上足以覆盖全部未交付需求。")
    elif resource_summary["coverage_rate"] >= 0.6:
        st.warning("当前 released 可出货资源可以覆盖部分未交付需求，其余仍依赖在制或待放行资源。")
    else:
        st.error("当前 released 可出货资源不足，未交付需求较大，存在较高交付压力。")

    st.markdown("### 库存状态分析")
    inv_state_df = build_inventory_state_summary(inv_df)
    show_df(inv_state_df, hide_index=True)

    st.markdown("### 可出货库存排行")
    shippable_top = inv_df[inv_df["is_shippable"] == 1].copy()
    shippable_top = shippable_top.sort_values("available_qty", ascending=False)[[
        "lot_code", "trace_key", "location", "available_qty", "reserved_qty", "release_status", "lot_status"
    ]].head(10)
    show_df(shippable_top, hide_index=True)

    st.markdown("### 受限 / Hold 库存分析")
    blocked_df = inv_df[inv_df["inventory_state_analysis"] != "可出货"].copy()[[
        "lot_code", "trace_key", "location", "available_qty", "release_status", "lot_status", "inventory_state_analysis"
    ]].head(10)
    show_df(blocked_df, hide_index=True)

    with st.expander("查看库存分析明细数据"):
        show_df(inv_df, hide_index=True)





# =========================
# 页面模块
# =========================


def show_home(conn):
    st.markdown("""
    <div style="
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #eaf3ff 0%, #f7fbff 100%);
        border: 1px solid #d7e7ff;
        margin-bottom: 1rem;
    ">
        <div style="font-size: 2rem; font-weight: 800; color: #163a63;">
            玻璃套管 MES / ERP 协同平台
        </div>
        <div style="margin-top: 0.35rem; font-size: 1rem; color: #4d6480;">
            销售、生产、仓储、出货、追溯一体化管理首页
        </div>
        <div style="margin-top: 0.7rem; font-size: 0.95rem; color: #5f738d;">
            建议从左侧导航进入：销售管理 / 生产管理 / 库存仓储 / 系统配置
        </div>
    </div>
    """, unsafe_allow_html=True)

    order_item_cnt = metric_count(conn, "order_item")
    batch_cnt = metric_count(conn, "production_batch")
    lot_cnt = metric_count(conn, "inventory_lot")
    shipment_cnt = metric_count(conn, "shipment")

    undelivered_df = pd.read_sql_query("""
        WITH delivery_sum AS (
            SELECT
                order_item_id,
                COALESCE(SUM(actual_delivery_qty), 0) AS delivered_qty
            FROM delivery_plan
            GROUP BY order_item_id
        )
        SELECT
            COUNT(*) AS undelivered_order_count,
            COALESCE(SUM(oi.ordered_qty - COALESCE(ds.delivered_qty, 0)), 0) AS undelivered_qty_total
        FROM order_item oi
        LEFT JOIN delivery_sum ds ON oi.order_item_id = ds.order_item_id
        WHERE (oi.ordered_qty - COALESCE(ds.delivered_qty, 0)) > 0
    """, conn)

    undelivered_order_count = int(undelivered_df.iloc[0]["undelivered_order_count"]) if not undelivered_df.empty else 0
    undelivered_qty_total = float(undelivered_df.iloc[0]["undelivered_qty_total"]) if not undelivered_df.empty else 0.0

    st.markdown("## 经营总览")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.metric("订单明细数", order_item_cnt)
    with k2:
        st.metric("未交付订单数", undelivered_order_count)
    with k3:
        st.metric("未交付总量", f"{undelivered_qty_total:.0f}")
    with k4:
        st.metric("生产批次数", batch_cnt)
    with k5:
        st.metric("库存数", lot_cnt)
    with k6:
        st.metric("出货次数", shipment_cnt)

    st.markdown("---")

    sales_df = pd.read_sql_query("""
        WITH delivery_sum AS (
            SELECT
                order_item_id,
                COALESCE(SUM(actual_delivery_qty), 0) AS delivered_qty
            FROM delivery_plan
            GROUP BY order_item_id
        )
        SELECT
            COUNT(*) AS total_items,
            COALESCE(SUM(ordered_qty), 0) AS total_order_qty,
            COALESCE(SUM(COALESCE(ds.delivered_qty, 0)), 0) AS total_delivered_qty,
            COALESCE(SUM(ordered_qty - COALESCE(ds.delivered_qty, 0)), 0) AS total_undelivered_qty
        FROM order_item oi
        LEFT JOIN delivery_sum ds ON oi.order_item_id = ds.order_item_id
    """, conn)

    prod_df = pd.read_sql_query("""
        SELECT
            COUNT(*) AS total_batches,
            COALESCE(SUM(CASE WHEN lower(COALESCE(production_flow_status, 'planned')) = 'planned' THEN 1 ELSE 0 END), 0) AS planned_batches,
            COALESCE(SUM(CASE WHEN lower(COALESCE(production_flow_status, 'planned')) = 'running' THEN 1 ELSE 0 END), 0) AS running_batches,
            COALESCE(SUM(CASE WHEN lower(COALESCE(production_flow_status, 'planned')) = 'done' THEN 1 ELSE 0 END), 0) AS done_batches
        FROM production_batch
    """, conn)

    inv_df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(COALESCE(available_qty, 0)), 0) AS total_available_qty,
            COALESCE(SUM(CASE WHEN location = 'WH-ORDER' THEN COALESCE(available_qty, 0) + COALESCE(reserved_qty, 0) ELSE 0 END), 0) AS order_stock_qty,
            COALESCE(SUM(CASE WHEN location = 'WH-SPEC' THEN COALESCE(available_qty, 0) + COALESCE(reserved_qty, 0) ELSE 0 END), 0) AS spec_stock_qty,
            COALESCE(SUM(CASE
                WHEN lower(COALESCE(release_status, 'pending')) = 'released'
                 AND lower(COALESCE(lot_status, 'hold')) IN ('available', 'reserved')
                THEN COALESCE(available_qty, 0)
                ELSE 0
            END), 0) AS shippable_qty
        FROM inventory_lot
    """, conn)

    ship_df = pd.read_sql_query("""
        SELECT
            COUNT(*) AS shipment_count,
            COALESCE(SUM(shipped_qty), 0) AS total_shipped_qty
        FROM shipment_item
    """, conn)

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("## 业务概览")

        a, b = st.columns(2)

        with a:
            if not sales_df.empty:
                s = sales_df.iloc[0]
                st.markdown("""
                <div style="
                    background:#f7fbff;
                    border:1px solid #dbeafe;
                    border-radius:16px;
                    padding:16px;
                    min-height:210px;
                ">
                    <div style="font-size:1.15rem;font-weight:700;color:#12436b;margin-bottom:10px;">销售概览</div>
                    <div style="line-height:1.9;">
                        <b>订单明细数：</b>""" + f"{int(s['total_items'])}<br>" + """
                        <b>订单总量：</b>""" + f"{float(s['total_order_qty']):.0f}<br>" + """
                        <b>已交付量：</b>""" + f"{float(s['total_delivered_qty']):.0f}<br>" + """
                        <b>未交付量：</b>""" + f"{float(s['total_undelivered_qty']):.0f}" + """
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with b:
            if not prod_df.empty:
                p = prod_df.iloc[0]
                st.markdown("""
                <div style="
                    background:#f8fcf8;
                    border:1px solid #d9f0df;
                    border-radius:16px;
                    padding:16px;
                    min-height:210px;
                ">
                    <div style="font-size:1.15rem;font-weight:700;color:#1c5a35;margin-bottom:10px;">生产概览</div>
                    <div style="line-height:1.9;">
                        <b>生产批次总数：</b>""" + f"{int(p['total_batches'])}<br>" + """
                        <b>已排产：</b>""" + f"{int(p['planned_batches'])}<br>" + """
                        <b>进行中：</b>""" + f"{int(p['running_batches'])}<br>" + """
                        <b>已完成：</b>""" + f"{int(p['done_batches'])}" + """
                    </div>
                </div>
                """, unsafe_allow_html=True)

        c, d = st.columns(2)

        with c:
            if not inv_df.empty:
                i = inv_df.iloc[0]
                st.markdown("""
                <div style="
                    background:#fffaf4;
                    border:1px solid #f5e2c8;
                    border-radius:16px;
                    padding:16px;
                    min-height:210px;
                ">
                    <div style="font-size:1.15rem;font-weight:700;color:#8a5315;margin-bottom:10px;">仓储概览</div>
                    <div style="line-height:1.9;">
                        <b>可用库存总量：</b>""" + f"{float(i['total_available_qty']):.0f}<br>" + """
                        <b>订单库存：</b>""" + f"{float(i['order_stock_qty']):.0f}<br>" + """
                        <b>规格库存：</b>""" + f"{float(i['spec_stock_qty']):.0f}<br>" + """
                        <b>可出货库存：</b>""" + f"{float(i['shippable_qty']):.0f}" + """
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with d:
            if not ship_df.empty:
                sh = ship_df.iloc[0]
                st.markdown("""
                <div style="
                    background:#fff7f7;
                    border:1px solid #f2d6d6;
                    border-radius:16px;
                    padding:16px;
                    min-height:210px;
                ">
                    <div style="font-size:1.15rem;font-weight:700;color:#8a2c2c;margin-bottom:10px;">出货概览</div>
                    <div style="line-height:1.9;">
                        <b>出货明细数：</b>""" + f"{int(sh['shipment_count'])}<br>" + """
                        <b>累计出货量：</b>""" + f"{float(sh['total_shipped_qty']):.0f}<br>" + """
                        <b>说明：</b>系统已支持订单库存与规格库存混合分配出货
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with right:
        st.markdown("## 快捷指引")

        st.markdown("""
        <div style="
            background:#ffffff;
            border:1px solid #e5e7eb;
            border-radius:16px;
            padding:16px;
            margin-bottom:12px;
        ">
            <div style="font-size:1.05rem;font-weight:700;color:#1f2937;margin-bottom:8px;">销售管理</div>
            <div style="line-height:1.9;">
                • 订单录入<br>
                • 销售看板<br>
                • 交付计划
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background:#ffffff;
            border:1px solid #e5e7eb;
            border-radius:16px;
            padding:16px;
            margin-bottom:12px;
        ">
            <div style="font-size:1.05rem;font-weight:700;color:#1f2937;margin-bottom:8px;">生产管理</div>
            <div style="line-height:1.9;">
                • 排产看板<br>
                • 生产过程录入<br>
                • 批次追踪<br>
                • 检测录入 / 质量放行
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background:#ffffff;
            border:1px solid #e5e7eb;
            border-radius:16px;
            padding:16px;
            margin-bottom:12px;
        ">
            <div style="font-size:1.05rem;font-weight:700;color:#1f2937;margin-bottom:8px;">库存/仓储</div>
            <div style="line-height:1.9;">
                • 仓储总看板<br>
                • 库存<br>
                • 出货管理<br>
                • Trace Key 查询
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background:#eef6ff;
            border:1px solid #cfe3ff;
            border-radius:16px;
            padding:16px;
        ">
            <div style="font-size:1.05rem;font-weight:700;color:#12436b;margin-bottom:8px;">推荐入口</div>
            <div style="line-height:1.9;">
                优先进入 <b>实时联动看板</b>，在同一页面同步查看销售、生产、库存的联动变化。
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("## 推荐操作路径")
    p1, p2 = st.columns(2)

    with p1:
        st.write("1. 先在 **订单录入** 或 **销售看板** 中确认订单与未交付情况。")
        st.write("2. 若库存满足，可在 **销售看板** 或 **实时联动看板** 直接出货。")
        st.write("3. 若库存不足，可创建排产并按流程推进到入库。")

    with p2:
        st.write("4. 入库后，仓库可在 **仓储总看板** 查看订单库存与规格库存。")
        st.write("5. 出货完成后，可在 **Trace Key 查询** 或订单追踪区查看全流程。")
        st.write("6. Excel 数据中心可用于数据批量导入、导出与更新。")

    st.success("首页已升级为门户样式。左侧选择业务区后，可快速进入对应模块。")

def page_order_entry(conn):
    st.header("销售｜订单录入")

    st.info(
        "订单录入会生成订单主表、订单明细、订单要求和交付批次。"
        "特殊工艺和材质会参与 Trace Key 生成，并影响后续库存匹配。"
    )

    # =========================
    # 1. 基础数据检查
    # =========================
    customer_df = pd.read_sql_query("""
        SELECT
            customer_id,
            customer_name,
            COALESCE(customer_code, '') AS customer_code,
            COALESCE(contact_person, '') AS contact_person,
            COALESCE(phone, '') AS phone,
            COALESCE(email, '') AS email
        FROM customer
        WHERE COALESCE(is_enabled, 1) = 1
        ORDER BY customer_name, customer_id
    """, conn)

    spec_df = pd.read_sql_query("""
        SELECT
            ps.spec_id,
            ps.spec_code,
            ps.spec_desc,
            ps.outer_diameter_mm,
            ps.wall_thickness_mm,
            ps.length_mm,
            p.product_id,
            p.product_name,
            p.product_code
        FROM product_spec ps
        JOIN product p
            ON ps.product_id = p.product_id
        WHERE COALESCE(ps.is_enabled, 1) = 1
        AND COALESCE(p.is_enabled, 1) = 1
        ORDER BY p.product_id, ps.spec_id
    """, conn)

    if customer_df.empty:
        st.error("当前没有客户主数据，请先在基础数据中维护客户。")
        return

    if spec_df.empty:
        st.error("当前没有产品规格数据，请先维护产品和规格。")
        return

    # =========================
    # 2. 客户与订单基础信息
    # =========================
    st.subheader("订单基础信息")

    c1, c2 = st.columns(2)

    with c1:
        customer_id = st.selectbox(
            "客户",
            customer_df["customer_id"].tolist(),
            format_func=lambda x: (
                   f"{customer_df.loc[customer_df['customer_id'] == x, 'customer_name'].iloc[0]}"
                   f"｜{customer_df.loc[customer_df['customer_id'] == x, 'customer_code'].iloc[0]}"
                   f"｜联系人：{customer_df.loc[customer_df['customer_id'] == x, 'contact_person'].iloc[0]}"
            ),
            key="order_entry_customer_id"
        )

        po_no = st.text_input(
            "订单号 / PO",
            placeholder="例如：PO-2026-001",
            key="order_entry_po_no"
        )

        customer_pn = st.text_input(
            "客户料号",
            placeholder="例如：CPN-001",
            key="order_entry_customer_pn"
        )

        drawing_version = st.text_input(
            "图纸版本",
            value="DRW-NEW-V1",
            key="order_entry_drawing_version"
        )

    with c2:
        factory_part_no = st.text_input(
            "本厂料号",
            placeholder="例如：PART-001",
            key="order_entry_factory_part_no"
        )

        ordered_qty = st.number_input(
            "订单数量",
            min_value=1.0,
            value=1000.0,
            step=1.0,
            key="order_entry_ordered_qty"
        )

        overall_deadline = st.date_input(
            "总交期",
            value=date.today(),
            key="order_entry_overall_deadline"
        )

        quality_requirement = st.text_input(
            "质量要求",
            value="Standard",
            key="order_entry_quality_requirement"
        )

    item_note = st.text_area(
        "订单备注 / 特殊要求",
        placeholder="例如：客户要求分批交付；包装要求；标签要求等。",
        key="order_entry_item_note"
    )

    st.markdown("---")

    # =========================
    # 3. 产品规格 + 特殊工艺 + 材质
    # =========================
    st.subheader("产品与工艺信息")

    p1, p2, p3 = st.columns(3)

    with p1:
        spec_id = st.selectbox(
            "产品规格",
            spec_df["spec_id"].tolist(),
            format_func=lambda x: (
                f"{spec_df.loc[spec_df['spec_id'] == x, 'product_name'].iloc[0]}"
                f"｜{spec_df.loc[spec_df['spec_id'] == x, 'spec_code'].iloc[0]}"
            ),
            key="order_entry_spec_id"
        )

    special_process_options = get_business_options(
        conn,
        "special_process",
        ["STANDARD", "LASER", "CHAMFER", "DRILLING"]
    )

    material_options = get_business_options(
        conn,
        "material",
        ["BOROSILICATE", "QUARTZ", "SODA-LIME"]
    )

    with p2:
        special_process = st.selectbox(
            "特殊工艺",
            special_process_options,
            index=0,
            key="order_entry_special_process"
        )

    with p3:
        material = st.selectbox(
            "材质",
            material_options,
            index=0,
            key="order_entry_material"
        )

    selected_spec_row = spec_df[spec_df["spec_id"] == spec_id].iloc[0]

    st.caption(
        f"产品：{selected_spec_row['product_name']} ｜ "
        f"规格编码：{selected_spec_row['spec_code']} ｜ "
        f"规格描述：{selected_spec_row['spec_desc']} ｜ "
        f"外径：{selected_spec_row['outer_diameter_mm']} mm ｜ "
        f"壁厚：{selected_spec_row['wall_thickness_mm']} mm ｜ "
        f"长度：{selected_spec_row['length_mm']} mm"
    )

    # =========================
    # 4. Trace Key 预览
    # =========================
    st.markdown("### Trace Key 预览")

    preview_spec_code = normalize_text(selected_spec_row["spec_code"])

    preview_special_process = normalize_business_option(
        conn,
        "special_process",
        special_process,
        "STANDARD"
    )

    preview_material = normalize_business_option(
        conn,
        "material",
        material,
        "BOROSILICATE"
    )

    preview_trace_key = build_trace_key(
        po_no=po_no,
        spec_code=preview_spec_code,
        special_process=preview_special_process,
        material=preview_material
    )

    st.code(preview_trace_key)

    st.caption(
        "Trace Key 规则：PO + 产品规格 + 特殊工艺 + 材质。"
        "该键会用于后续排产、生产批次、库存匹配和全流程追溯。"
    )

    st.markdown("---")

    # =========================
    # 5. 交货计划
    # =========================
    delivery_mode, schedules, remain_qty = render_delivery_schedule_editor(
        prefix="order_entry",
        ordered_qty=float(ordered_qty)
    )

    st.markdown("---")

    # =========================
    # 6. 提交订单
    # =========================
    if st.button("提交订单", key="order_entry_submit"):
        po_no_clean = normalize_text(po_no)
        customer_pn_clean = normalize_text(customer_pn)
        drawing_version_clean = normalize_text(drawing_version) or "DRW-NEW-V1"
        factory_part_no_clean = normalize_text(factory_part_no)
        item_note_clean = normalize_text(item_note)
        quality_requirement_clean = normalize_text(quality_requirement) or "Standard"

        # =========================
        # 保存订单前再次标准化特殊工艺 / 材质
        # 关键修正：这里必须赋值给 special_process_clean / material_clean
        # 后面 INSERT 和 trace_key 都使用这两个变量
        # =========================
        special_process_clean = normalize_business_option(
            conn,
            "special_process",
            special_process,
            "STANDARD"
        )

        material_clean = normalize_business_option(
            conn,
            "material",
            material,
            "BOROSILICATE"
        )

        if not po_no_clean:
            st.error("订单号（PO）不能为空。")
            return

        if float(ordered_qty) <= 0:
            st.error("订单数量必须大于 0。")
            return

        if abs(float(remain_qty)) > 0.000001:
            st.error("交货计划数量未平衡，不能提交。请确保交货计划总量等于订单数量。")
            return

        valid_schedules = [
            s for s in schedules
            if float(s["planned_delivery_qty"]) > 0
        ]

        if not valid_schedules:
            st.error("至少需要一条有效交货计划。")
            return

        spec_row = spec_df[spec_df["spec_id"] == spec_id].iloc[0]

        product_id = int(spec_row["product_id"])
        spec_code = normalize_text(spec_row["spec_code"])
        product_name = normalize_text(spec_row["product_name"])

        trace_key = build_trace_key(
            po_no=po_no_clean,
            spec_code=spec_code,
            special_process=special_process_clean,
            material=material_clean
        )

        cursor = conn.cursor()

        try:
            # =========================
            # 6.1 写入订单主表
            # =========================
            cursor.execute("""
                INSERT INTO orders (
                    customer_id,
                    order_date,
                    order_status,
                    overall_deadline,
                    priority_level
                ) VALUES (?, date('now'), 'confirmed', ?, 'Medium')
            """, (
                int(customer_id),
                str(overall_deadline)
            ))

            order_id = cursor.lastrowid

            # =========================
            # 6.2 写入订单明细
            # =========================
            cursor.execute("""
                INSERT INTO order_item (
                    order_id,
                    product_id,
                    spec_id,
                    ordered_qty,
                    reserved_qty,
                    fulfilled_qty,
                    shipped_qty,
                    allocatable_qty,
                    item_status,
                    po_no,
                    customer_pn,
                    drawing_version,
                    factory_part_no,
                    product_type_text,
                    product_spec_text,
                    item_note,
                    special_process,
                    material,
                    trace_key
                ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 'open', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(order_id),
                int(product_id),
                int(spec_id),
                float(ordered_qty),
                po_no_clean,
                customer_pn_clean,
                drawing_version_clean,
                factory_part_no_clean,
                product_name,
                spec_code,
                item_note_clean,
                special_process_clean,
                material_clean,
                trace_key
            ))

            order_item_id = cursor.lastrowid

            # =========================
            # 6.3 写入质量 / 订单要求
            # =========================
            cursor.execute("""
                INSERT INTO order_requirement (
                    order_item_id,
                    quality_requirement
                ) VALUES (?, ?)
            """, (
                int(order_item_id),
                quality_requirement_clean
            ))

            # =========================
            # 6.4 写入交付批次 delivery_plan
            # 兼容有 / 没有 delivery_batch_no、delivery_status 字段的旧库
            # =========================
            delivery_plan_cols = pd.read_sql_query(
                "PRAGMA table_info(delivery_plan)",
                conn
            )["name"].tolist()

            for idx, schedule in enumerate(valid_schedules, start=1):
                planned_date = normalize_text(schedule["planned_delivery_date"])
                planned_qty = float(schedule["planned_delivery_qty"])

                if (
                    "delivery_batch_no" in delivery_plan_cols
                    and "delivery_status" in delivery_plan_cols
                ):
                    cursor.execute("""
                        INSERT INTO delivery_plan (
                            order_item_id,
                            planned_delivery_date,
                            planned_delivery_qty,
                            actual_delivery_qty,
                            delivery_batch_no,
                            delivery_status
                        ) VALUES (?, ?, ?, 0, ?, '未排产')
                    """, (
                        int(order_item_id),
                        planned_date,
                        planned_qty,
                        int(idx)
                    ))

                elif "delivery_batch_no" in delivery_plan_cols:
                    cursor.execute("""
                        INSERT INTO delivery_plan (
                            order_item_id,
                            planned_delivery_date,
                            planned_delivery_qty,
                            actual_delivery_qty,
                            delivery_batch_no
                        ) VALUES (?, ?, ?, 0, ?)
                    """, (
                        int(order_item_id),
                        planned_date,
                        planned_qty,
                        int(idx)
                    ))

                elif "delivery_status" in delivery_plan_cols:
                    cursor.execute("""
                        INSERT INTO delivery_plan (
                            order_item_id,
                            planned_delivery_date,
                            planned_delivery_qty,
                            actual_delivery_qty,
                            delivery_status
                        ) VALUES (?, ?, ?, 0, '未排产')
                    """, (
                        int(order_item_id),
                        planned_date,
                        planned_qty
                    ))

                else:
                    cursor.execute("""
                        INSERT INTO delivery_plan (
                            order_item_id,
                            planned_delivery_date,
                            planned_delivery_qty,
                            actual_delivery_qty
                        ) VALUES (?, ?, ?, 0)
                    """, (
                        int(order_item_id),
                        planned_date,
                        planned_qty
                    ))

            conn.commit()

            st.success(
                f"订单提交成功。订单编号：{order_id}；"
                f"订单明细编号：{order_item_id}；"
                f"交付批次数：{len(valid_schedules)}。"
            )

            st.markdown("### 已生成 Trace Key")
            st.code(trace_key)

            st.markdown("### 已保存的标准字段")
            c1, c2, c3 = st.columns(3)
            c1.metric("特殊工艺", special_process_clean)
            c2.metric("材质", material_clean)
            c3.metric("交付批次数", len(valid_schedules))

            with st.expander("查看该订单交付批次", expanded=True):
                render_sales_delivery_detail_card(conn, int(order_item_id))

        except Exception as e:
            conn.rollback()
            st.error(f"订单提交失败：{e}")
            return


def render_sales_to_production_push(conn):
    """
    销售看板专用：
    将未排产的交付批次推送给生产端确认。
    """
    st.markdown("---")
    st.subheader("销售推送至生产")

    push_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
            oi.trace_key
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        WHERE ps.production_schedule_id IS NULL
          AND COALESCE(dp.delivery_status, '未排产') IN ('未排产', '待生产确认')
        ORDER BY dp.planned_delivery_date, dp.delivery_plan_id
    """, conn)

    if push_df.empty:
        st.success("当前没有需要推送给生产端的交付批次。")
        return

    show_df(push_df.rename(columns={
        "delivery_plan_id": "交付计划编号",
        "delivery_batch_no": "交付批次",
        "planned_delivery_date": "计划交付日期",
        "planned_delivery_qty": "计划交付数量",
        "delivery_status": "当前状态",
        "customer_name": "客户",
        "po_no": "PO",
        "product_spec_text": "规格",
        "special_process": "特殊工艺",
        "material": "材质"
    }), hide_index=True)

    selected_delivery_plan_id = st.selectbox(
        "选择要推送给生产端的交付批次",
        push_df["delivery_plan_id"].tolist(),
        format_func=lambda x: (
            f"交付计划 {x} | "
            f"PO {push_df.loc[push_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
            f"第 {int(push_df.loc[push_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
            f"{push_df.loc[push_df['delivery_plan_id'] == x, 'planned_delivery_qty'].iloc[0]}"
        ),
        key="sales_push_delivery_plan_select"
    )

    selected = push_df[push_df["delivery_plan_id"] == selected_delivery_plan_id].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户", str(selected["customer_name"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
    c4.metric("计划数量", f"{float(selected['planned_delivery_qty']):.0f}")

    st.caption(
        f"产品：{selected['product_type_text']} ｜ 规格：{selected['product_spec_text']} ｜ "
        f"特殊工艺：{selected['special_process']} ｜ 材质：{selected['material']}"
    )

    st.code(str(selected["trace_key"]))

    if str(selected["delivery_status"]) == "待生产确认":
        st.info("该交付批次已经推送，等待生产端确认。")
    else:
        if st.button("推送至生产端确认", key=f"sales_push_to_production_{selected_delivery_plan_id}"):
            ok, msg = push_delivery_plan_to_production(conn, int(selected_delivery_plan_id))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

def page_realtime_control_tower(conn):
    st.header("联动｜实时联动看板")

    # =========================
    # 1. 按交付批次取未完成数据
    # =========================
    dp_df = pd.read_sql_query("""
        WITH batch_status AS (
            SELECT
                dp.delivery_plan_id,
                CASE
                    WHEN MAX(CASE WHEN il.inventory_lot_id IS NOT NULL
                                   AND lower(COALESCE(il.release_status, 'pending')) = 'released'
                                  THEN 1 ELSE 0 END) = 1 THEN '已入库'
                    WHEN MAX(CASE WHEN pm.measurement_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '质检'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cleaning' THEN 1 ELSE 0 END) = 1 THEN '清洗'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cutting' THEN 1 ELSE 0 END) = 1 THEN '切割'
                    WHEN MAX(CASE WHEN ps.production_schedule_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '已排产'
                    ELSE COALESCE(MAX(dp.delivery_status), '未排产')
                END AS real_process_status
            FROM delivery_plan dp
            LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
            LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN production_process_log ppl ON pb.production_batch_id = ppl.production_batch_id
            LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
            GROUP BY dp.delivery_plan_id
        ),
        inv_sum AS (
            SELECT
                spec_id,
                COALESCE(SUM(CASE
                    WHEN lower(COALESCE(release_status, 'pending')) = 'released'
                     AND lower(COALESCE(lot_status, 'hold')) IN ('available', 'reserved')
                    THEN COALESCE(available_qty, 0)
                    ELSE 0
                END), 0) AS shippable_stock_qty,
                COALESCE(SUM(CASE
                    WHEN location = 'WH-ORDER'
                    THEN COALESCE(available_qty, 0) + COALESCE(reserved_qty, 0)
                    ELSE 0
                END), 0) AS order_stock_qty,
                COALESCE(SUM(CASE
                    WHEN location = 'WH-SPEC'
                    THEN COALESCE(available_qty, 0) + COALESCE(reserved_qty, 0)
                    ELSE 0
                END), 0) AS spec_stock_qty
            FROM inventory_lot
            GROUP BY spec_id
        )
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            (dp.planned_delivery_qty - COALESCE(dp.actual_delivery_qty, 0)) AS undelivered_batch_qty,
            COALESCE(bs.real_process_status, dp.delivery_status, '未排产') AS delivery_status,

            oi.po_no,
            oi.customer_pn,
            oi.product_spec_text,
            oi.trace_key,
            oi.spec_id,
            oi.ordered_qty,
            oi.shipped_qty,

            c.customer_name,
            o.customer_id,

            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status,
            pm.quality_status,
            pm.release_status,

            COALESCE(inv.order_stock_qty, 0) AS order_stock_qty,
            COALESCE(inv.spec_stock_qty, 0) AS spec_stock_qty,
            COALESCE(inv.shippable_stock_qty, 0) AS shippable_stock_qty
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN batch_status bs ON dp.delivery_plan_id = bs.delivery_plan_id
        LEFT JOIN inv_sum inv ON oi.spec_id = inv.spec_id
        WHERE (dp.planned_delivery_qty - COALESCE(dp.actual_delivery_qty, 0)) > 0
        ORDER BY oi.order_item_id, dp.delivery_batch_no, dp.planned_delivery_date
    """, conn)

    if dp_df.empty:
        st.success("当前没有未完成的交付批次。")
        return

    # =========================
    # 2. 顶部总览
    # =========================
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("未完成交付批次数", int(len(dp_df)))
    k2.metric("未完成交付总量", f"{float(dp_df['undelivered_batch_qty'].sum()):.0f}")
    k3.metric("可出货库存总量", f"{float(dp_df['shippable_stock_qty'].max() if len(dp_df) > 0 else 0):.0f}")
    k4.metric("已排产批次数", int((dp_df["delivery_status"] != "未排产").sum()))

    st.markdown("---")

    # =========================
    # 3. 分批总表
    # =========================
    st.subheader("批次级联动总表")

    dp_display_df = dp_df.rename(columns={
        "delivery_batch_no": "交付批次",
        "planned_delivery_date": "计划交付日期",
        "planned_delivery_qty": "计划交付数量",
        "actual_delivery_qty": "实际交付数量",
        "undelivered_batch_qty": "该批未交付量",
        "delivery_status": "交付状态",
        "batch_code": "对应批次号",
        "required_production_qty": "应生产数量",
        "actual_qty": "实际生产数量",
        "production_flow_status": "生产状态",
        "order_stock_qty": "订单库存",
        "spec_stock_qty": "规格库存",
        "shippable_stock_qty": "可出货库存"
    })
    show_df(dp_display_df, hide_index=True)

    st.markdown("---")

    # =========================
    # 4. 选择当前交付批次
    # =========================
    selected_delivery_plan_id = st.selectbox(
        "选择一条交付批次进行联动查看与处理",
        dp_df["delivery_plan_id"].tolist(),
        format_func=lambda x: (
            f"{x} | "
            f"{dp_df.loc[dp_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
            f"第{int(dp_df.loc[dp_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])}批 | "
            f"{dp_df.loc[dp_df['delivery_plan_id'] == x, 'product_spec_text'].iloc[0]}"
        ),
        key="tower_delivery_plan_select"
    )

    selected_row = dp_df[dp_df["delivery_plan_id"] == selected_delivery_plan_id].iloc[0]
    current_status = get_delivery_plan_process_status(conn, int(selected_delivery_plan_id))

    # 当前交付批次相关 Lot
    lots_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.lot_code,
            il.trace_key,
            il.location,
            il.available_qty,
            il.reserved_qty,
            il.release_status,
            il.lot_status
        FROM inventory_lot il
        WHERE il.spec_id = ?
          AND lower(COALESCE(il.release_status, 'pending')) = 'released'
          AND lower(COALESCE(il.lot_status, 'hold')) IN ('available', 'reserved')
          AND COALESCE(il.available_qty, 0) > 0
        ORDER BY
            CASE
                WHEN il.location = 'WH-ORDER' THEN 1
                WHEN il.location = 'WH-SPEC' THEN 2
                ELSE 9
            END,
            il.available_qty DESC,
            il.inventory_lot_id
    """, conn, params=[int(selected_row["spec_id"])])

    # =========================
    # 5. 销售 / 生产 / 库存 三联区
    # =========================
    col_sales, col_prod, col_inv = st.columns(3)

    with col_sales:
        st.markdown("### 销售区")
        st.metric("客户", str(selected_row["customer_name"]))
        st.metric("订单号", str(selected_row["po_no"]))
        st.metric("交付批次", f"第 {int(selected_row['delivery_batch_no'])} 批")
        st.metric("产品规格", str(selected_row["product_spec_text"]))
        st.metric("计划交付数量", f"{float(selected_row['planned_delivery_qty']):.0f}")
        st.metric("实际交付数量", f"{float(selected_row['actual_delivery_qty']):.0f}")
        st.metric("该批未交付量", f"{float(selected_row['undelivered_batch_qty']):.0f}")
        st.metric("交付状态", current_status)

    with col_prod:
        st.markdown("### 生产区")
        if pd.isna(selected_row["production_batch_id"]):
            st.info("当前批次尚未创建排产")
        else:
            st.metric("批次号", str(selected_row["batch_code"]))
            st.metric("生产状态", str(selected_row["production_flow_status"]) if pd.notna(selected_row["production_flow_status"]) else "-")
            st.metric("应生产数量", f"{float(selected_row['required_production_qty'] or 0):.0f}")
            st.metric("实际生产数量", f"{float(selected_row['actual_qty'] or 0):.0f}")
            st.metric("质量状态", str(selected_row["quality_status"]) if pd.notna(selected_row["quality_status"]) else "-")
            st.metric("放行状态", str(selected_row["release_status"]) if pd.notna(selected_row["release_status"]) else "-")

    with col_inv:
        st.markdown("### 库存区")
        st.metric("订单库存", f"{float(selected_row['order_stock_qty'] or 0):.0f}")
        st.metric("规格库存", f"{float(selected_row['spec_stock_qty'] or 0):.0f}")
        st.metric("可出货库存", f"{float(selected_row['shippable_stock_qty'] or 0):.0f}")

        if lots_df.empty:
            st.info("当前无可用 Lot")
        else:
            st.markdown("#### 当前规格可用 Lot")
            show_df(lots_df, hide_index=True)

    st.markdown("---")

    # =========================
    # 6. 实时操作区（按交付批次）
    # =========================
    st.markdown("## 实时操作区")
    render_sales_process_flow(
        current_status if current_status in ["未排产", "已排产", "切割", "清洗", "质检", "已入库"] else "未排产"
    )

    inventory_ready = float(selected_row["shippable_stock_qty"] or 0) >= float(selected_row["undelivered_batch_qty"] or 0)

    if inventory_ready and current_status in ["已入库", "质检", "清洗", "切割", "已排产", "未排产"]:
        st.success("当前库存满足该交付批次需求，可直接按该批次出货。")

        if st.button("标记该交付批次已出货", key=f"tower_dp_ship_{selected_delivery_plan_id}"):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '已出货',
                    actual_delivery_date = COALESCE(actual_delivery_date, date('now')),
                    actual_delivery_qty = COALESCE(actual_delivery_qty, planned_delivery_qty)
                WHERE delivery_plan_id = ?
            """, (int(selected_delivery_plan_id),))
            conn.commit()
            st.success("该交付批次已标记为已出货")
            st.rerun()

    else:
        st.warning("当前库存不足该交付批次需求，需按该批次推进生产。")

        if current_status == "未排产":
            planned_qty_input = st.number_input(
                "该交付批次应生产数量",
                min_value=1.0,
                value=float(selected_row["planned_delivery_qty"]),
                step=1.0,
                key=f"tower_dp_qty_{selected_delivery_plan_id}"
            )
            if st.button("为该交付批次创建排产", key=f"tower_dp_create_{selected_delivery_plan_id}"):
                ok, msg = create_production_for_delivery_plan(
                    conn,
                    int(selected_delivery_plan_id),
                    planned_qty=float(planned_qty_input)
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif current_status == "已排产":
            if st.button("推进到切割", key=f"tower_dp_cutting_{selected_delivery_plan_id}"):
                ok, msg = advance_delivery_plan_process_status(conn, int(selected_delivery_plan_id), "切割")
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif current_status == "切割":
            if st.button("推进到清洗", key=f"tower_dp_cleaning_{selected_delivery_plan_id}"):
                ok, msg = advance_delivery_plan_process_status(conn, int(selected_delivery_plan_id), "清洗")
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif current_status == "清洗":
            if st.button("推进到质检", key=f"tower_dp_qc_{selected_delivery_plan_id}"):
                ok, msg = advance_delivery_plan_process_status(conn, int(selected_delivery_plan_id), "质检")
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif current_status == "质检":
            if st.button("标记已入库", key=f"tower_dp_inbound_{selected_delivery_plan_id}"):
                ok, msg = mark_delivery_plan_as_inbound(conn, int(selected_delivery_plan_id))
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif current_status == "已入库":
            st.info("该交付批次已入库，等待库存满足或直接标记已出货。")

    st.markdown("---")

    # =========================
    # 7. 追踪明细区（订单级沿用）
    # =========================
    render_current_order_trace_detail(conn, int(selected_row["order_item_id"]))


def page_delivery_plan(conn):
    st.header("销售｜交付计划")

    order_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.po_no,
            oi.trace_key,
            oi.ordered_qty,
            oi.product_spec_text,
            c.customer_name
        FROM order_item oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY oi.order_item_id
    """, conn)

    if order_df.empty:
        st.info("当前没有订单明细，无法维护交付计划。")
        return

    # =========================
    # 1. 新增交付计划
    # =========================
    with st.form("delivery_plan_form"):
        order_item_id = st.selectbox(
            "选择订单明细",
            order_df["order_item_id"].tolist(),
            format_func=lambda x: (
                f"{x} | "
                f"{order_df.loc[order_df['order_item_id'] == x, 'po_no'].iloc[0]} | "
                f"{order_df.loc[order_df['order_item_id'] == x, 'customer_name'].iloc[0]} | "
                f"{order_df.loc[order_df['order_item_id'] == x, 'product_spec_text'].iloc[0]}"
            )
        )

        planned_date = st.date_input("计划交付日期", value=date.today())
        planned_qty = st.number_input("计划交付数量", min_value=1.0, value=10.0, step=1.0)

        submitted = st.form_submit_button("新增交付计划")

    if submitted:
        existing_batch_df = pd.read_sql_query("""
            SELECT COALESCE(MAX(delivery_batch_no), 0) AS max_batch_no
            FROM delivery_plan
            WHERE order_item_id = ?
        """, conn, params=[order_item_id])

        next_batch_no = int(existing_batch_df.iloc[0]["max_batch_no"]) + 1

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO delivery_plan (
                order_item_id,
                planned_delivery_date,
                planned_delivery_qty,
                delivery_batch_no,
                delivery_status
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            int(order_item_id),
            str(planned_date),
            float(planned_qty),
            next_batch_no,
            "未排产"
        ))
        conn.commit()
        st.success(f"交付计划新增成功：第 {next_batch_no} 批")
        st.rerun()

    st.markdown("---")

    # =========================
    # 2. 当前交付计划
    # =========================
    st.subheader("当前交付计划")

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            oi.po_no,
            c.customer_name,
            oi.product_spec_text,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            dp.actual_delivery_date,
            dp.actual_delivery_qty,
            dp.delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        ORDER BY dp.order_item_id, dp.delivery_batch_no, dp.planned_delivery_date
    """, conn)

    if plan_df.empty:
        st.info("当前还没有交付计划。")
        return

    display_df = plan_df.rename(columns={
        "delivery_batch_no": "交付批次",
        "planned_delivery_date": "计划交付日期",
        "planned_delivery_qty": "计划交付数量",
        "actual_delivery_date": "实际交付日期",
        "actual_delivery_qty": "实际交付数量",
        "delivery_status": "交付状态",
        "batch_code": "对应批次号",
        "required_production_qty": "应生产数量",
        "actual_qty": "实际生产数量",
        "production_flow_status": "生产状态"
    })
    show_df(display_df, hide_index=True)

    st.markdown("---")

    # =========================
    # 3. 交付批次处理区
    # =========================
    st.subheader("交付批次处理区")

    selected_plan_id = st.selectbox(
        "选择一条交付批次",
        plan_df["delivery_plan_id"].tolist(),
        format_func=lambda x: (
            f"{x} | "
            f"{plan_df.loc[plan_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
            f"第{int(plan_df.loc[plan_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])}批 | "
            f"{plan_df.loc[plan_df['delivery_plan_id'] == x, 'product_spec_text'].iloc[0]}"
        )
    )

    selected_plan_row = plan_df[plan_df["delivery_plan_id"] == selected_plan_id].iloc[0]
    current_status = get_delivery_plan_process_status(conn, int(selected_plan_id))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("订单号", str(selected_plan_row["po_no"]))
    c2.metric("交付批次", f"第 {int(selected_plan_row['delivery_batch_no'])} 批")
    c3.metric("计划数量", f"{float(selected_plan_row['planned_delivery_qty']):.0f}")
    c4.metric("当前状态", current_status)

    if pd.notna(selected_plan_row["batch_code"]):
        st.info(f"当前交付批次对应生产批次：{selected_plan_row['batch_code']}")

    render_sales_process_flow(current_status if current_status in ["未排产", "已排产", "切割", "清洗", "质检", "已入库"] else "未排产")

    # 未排产：创建排产
    if current_status == "未排产":
        planned_qty_input = st.number_input(
            "该交付批次应生产数量",
            min_value=1.0,
            value=float(selected_plan_row["planned_delivery_qty"]),
            step=1.0,
            key=f"delivery_plan_create_qty_{selected_plan_id}"
        )

        if st.button("为该交付批次创建排产", key="create_batch_for_delivery_plan"):
            ok, msg = create_production_for_delivery_plan(
                conn,
                int(selected_plan_id),
                planned_qty=float(planned_qty_input)
            )
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif current_status == "已排产":
        if st.button("推进到切割", key=f"dp_to_cutting_{selected_plan_id}"):
            ok, msg = advance_delivery_plan_process_status(conn, int(selected_plan_id), "切割")
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif current_status == "切割":
        if st.button("推进到清洗", key=f"dp_to_cleaning_{selected_plan_id}"):
            ok, msg = advance_delivery_plan_process_status(conn, int(selected_plan_id), "清洗")
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif current_status == "清洗":
        if st.button("推进到质检", key=f"dp_to_qc_{selected_plan_id}"):
            ok, msg = advance_delivery_plan_process_status(conn, int(selected_plan_id), "质检")
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif current_status == "质检":
        if st.button("标记已入库", key=f"dp_to_inbound_{selected_plan_id}"):
            ok, msg = mark_delivery_plan_as_inbound(conn, int(selected_plan_id))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif current_status == "已入库":
        st.info("该交付批次已入库。可继续在出货后将其标记为已出货。")
        if st.button("标记该批已出货", key=f"dp_to_shipped_{selected_plan_id}"):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '已出货',
                    actual_delivery_date = COALESCE(actual_delivery_date, date('now')),
                    actual_delivery_qty = COALESCE(actual_delivery_qty, planned_delivery_qty)
                WHERE delivery_plan_id = ?
            """, (int(selected_plan_id),))
            conn.commit()
            st.success("该交付批次已标记为已出货")
            st.rerun()

    elif current_status == "已出货":
        st.success("该交付批次已完成出货。")

    st.markdown("---")
    st.markdown("### 手动修正状态")

    manual_status = st.selectbox(
        "手动设置交付状态",
        ["未排产", "已排产", "切割", "清洗", "质检", "已入库", "已出货"],
        index=["未排产", "已排产", "切割", "清洗", "质检", "已入库", "已出货"].index(
            current_status if current_status in ["未排产", "已排产", "切割", "清洗", "质检", "已入库", "已出货"] else "未排产"
        ),
        key=f"manual_status_{selected_plan_id}"
    )

    if st.button("保存手动状态", key=f"save_manual_delivery_status_{selected_plan_id}"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = ?
            WHERE delivery_plan_id = ?
        """, (manual_status, int(selected_plan_id)))
        conn.commit()
        st.success("交付批次状态已更新")
        st.rerun()

def page_production_process_entry(conn):
    st.header("生产过程录入")

    # =========================
    # 1. 只读取已经排产的生产批次
    # =========================
    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status,
            pb.special_process,
            pb.material,

            ps.production_schedule_id,
            ps.delivery_plan_id,
            ps.order_item_id,
            ps.scheduled_start_date,
            ps.scheduled_end_date,

            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '已排产') AS delivery_status,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.drawing_version,
            oi.factory_part_no,
            oi.product_type_text,
            oi.product_spec_text,
            oi.ordered_qty,
            oi.shipped_qty,
            oi.item_status
        FROM production_batch pb
        JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        ORDER BY pb.production_batch_id DESC
    """, conn)

    if batch_df.empty:
        st.warning("当前没有已排产的生产批次。请先在排产看板完成生产确认。")
        return

    # =========================
    # 2. 从排产看板跳转时自动选中对应批次
    # =========================
    default_batch_id = st.session_state.get("selected_process_batch_id", None)

    batch_ids = batch_df["production_batch_id"].tolist()

    default_index = 0
    if default_batch_id in batch_ids:
        default_index = batch_ids.index(default_batch_id)

    batch_id = st.selectbox(
        "选择生产批次",
        batch_ids,
        index=default_index,
        format_func=lambda x: (
            f"{x} | "
            f"{batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
            f"PO {batch_df.loc[batch_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
            f"第 {int(batch_df.loc[batch_df['production_batch_id'] == x, 'delivery_batch_no'].iloc[0])} 批"
        ),
        key="process_entry_batch_select"
    )

    selected = batch_df[batch_df["production_batch_id"] == batch_id].iloc[0]

    st.markdown("---")

    # =========================
    # 3. 交付批次卡片
    # =========================
    st.subheader("交付批次生产卡片")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户", str(selected["customer_name"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
    c4.metric("生产批号", str(selected["batch_code"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("产品", str(selected["product_type_text"]))
    c6.metric("规格", str(selected["product_spec_text"]))
    c7.metric("特殊工艺", str(selected["special_process"]))
    c8.metric("材质", str(selected["material"]))

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
    c10.metric("应生产数量", f"{float(selected['required_production_qty'] or 0):.0f}")
    c11.metric("当前实际产量", f"{float(selected['actual_qty'] or 0):.0f}")
    c12.metric("生产状态", str(selected["production_flow_status"]))

    c13, c14, c15, c16 = st.columns(4)
    c13.metric("计划交付日期", str(selected["planned_delivery_date"]))
    c14.metric("计划开始", str(selected["scheduled_start_date"]))
    c15.metric("计划结束", str(selected["scheduled_end_date"]))
    c16.metric("交付状态", str(selected["delivery_status"]))

    st.caption(
        f"客户料号：{selected['customer_pn']} ｜ "
        f"图纸版本：{selected['drawing_version']} ｜ "
        f"本厂料号：{selected['factory_part_no']} ｜ "
        f"订单数量：{float(selected['ordered_qty'] or 0):.0f} ｜ "
        f"已出货：{float(selected['shipped_qty'] or 0):.0f}"
    )

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    st.markdown("---")

    # =========================
    # 4. 当前批次已有过程记录
    # =========================
    st.subheader("当前批次已有生产过程记录")

    current_log_df = pd.read_sql_query("""
        SELECT
            process_log_id,
            production_batch_id,
            process_step,
            equipment_code,
            operator_name,
            input_qty,
            output_qty,
            scrap_qty,
            process_status,
            start_time,
            end_time,
            remark
        FROM production_process_log
        WHERE production_batch_id = ?
        ORDER BY process_log_id DESC
    """, conn, params=[batch_id])

    if current_log_df.empty:
        st.info("当前批次还没有生产过程记录。")
    else:
        show_df(current_log_df, hide_index=True)

    st.markdown("---")

    # =========================
    # 5. 生产过程录入表单
    # =========================
    st.subheader("录入生产过程")

    with st.form("production_process_entry_form"):
        process_step = st.selectbox(
            "工序",
            ["Cutting", "Heating", "Forming", "Polishing", "Cleaning", "Packing"],
            key=f"process_step_{batch_id}"
        )

        equipment_code = st.text_input(
            "设备编号",
            value="EQ-001",
            key=f"equipment_code_{batch_id}"
        )

        operator_name = st.text_input(
            "操作员",
            value="Operator A",
            key=f"operator_name_{batch_id}"
        )

        input_qty = st.number_input(
            "投入数量",
            min_value=0.0,
            value=float(selected["required_production_qty"] or 100),
            step=1.0,
            key=f"input_qty_{batch_id}"
        )

        output_qty = st.number_input(
            "产出数量",
            min_value=0.0,
            value=float(selected["actual_qty"] or 0),
            step=1.0,
            key=f"output_qty_{batch_id}"
        )

        scrap_qty = st.number_input(
            "报废数量",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"scrap_qty_{batch_id}"
        )

        process_status = st.selectbox(
            "工序状态",
            ["planned", "running", "done", "hold"],
            key=f"process_status_{batch_id}"
        )

        start_time = st.text_input(
            "开始时间",
            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            key=f"start_time_{batch_id}"
        )

        end_time = st.text_input(
            "结束时间",
            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            key=f"end_time_{batch_id}"
        )

        remark = st.text_area(
            "备注",
            value="",
            key=f"remark_{batch_id}"
        )

        submitted = st.form_submit_button("提交生产过程记录")

    if submitted:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO production_process_log (
                production_batch_id,
                process_step,
                equipment_code,
                operator_name,
                input_qty,
                output_qty,
                scrap_qty,
                process_status,
                start_time,
                end_time,
                remark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(batch_id),
            process_step,
            equipment_code,
            operator_name,
            float(input_qty),
            float(output_qty),
            float(scrap_qty),
            process_status,
            start_time,
            end_time,
            remark
        ))

        # 生产状态用工序名更直观，而不是只写 running / done
        if process_status in ("running", "done"):
            new_flow_status = process_step
        elif process_status == "hold":
            new_flow_status = "hold"
        else:
            new_flow_status = str(selected["production_flow_status"])

        cursor.execute("""
            UPDATE production_batch
            SET production_flow_status = ?,
                actual_qty = CASE
                    WHEN ? > COALESCE(actual_qty, 0) THEN ?
                    ELSE actual_qty
                END
            WHERE production_batch_id = ?
        """, (
            new_flow_status,
            float(output_qty),
            float(output_qty),
            int(batch_id)
        ))

        # 同步交付状态为生产中
        if pd.notna(selected["delivery_plan_id"]):
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '生产中'
                WHERE delivery_plan_id = ?
                  AND COALESCE(delivery_status, '') NOT IN ('已入库')
            """, (
                int(selected["delivery_plan_id"]),
            ))

        conn.commit()

        st.success("生产过程记录已写入，批次状态已更新。")
        st.rerun()

    st.markdown("---")

    # =========================
    # 6. 所有生产过程日志
    # =========================
    st.subheader("所有生产过程日志")

    all_log_df = pd.read_sql_query("""
        SELECT
            ppl.process_log_id,
            pb.batch_code,
            ppl.production_batch_id,
            ppl.process_step,
            ppl.equipment_code,
            ppl.operator_name,
            ppl.input_qty,
            ppl.output_qty,
            ppl.scrap_qty,
            ppl.process_status,
            ppl.start_time,
            ppl.end_time,
            ppl.remark
        FROM production_process_log ppl
        JOIN production_batch pb
            ON ppl.production_batch_id = pb.production_batch_id
        ORDER BY ppl.process_log_id DESC
    """, conn)

    if all_log_df.empty:
        st.info("当前还没有任何生产过程日志。")
    else:
        show_df(all_log_df, hide_index=True)




def page_batch_tracking(conn):
    st.header("生产｜批次追踪")

    trace_df = pd.read_sql_query("""
        WITH batch_status AS (
            SELECT
                dp.delivery_plan_id,
                CASE
                    WHEN MAX(CASE WHEN il.inventory_lot_id IS NOT NULL
                                   AND lower(COALESCE(il.release_status, 'pending')) = 'released'
                                  THEN 1 ELSE 0 END) = 1 THEN '已入库'
                    WHEN MAX(CASE WHEN pm.measurement_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '质检'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cleaning' THEN 1 ELSE 0 END) = 1 THEN '清洗'
                    WHEN MAX(CASE WHEN ppl.process_step = 'Cutting' THEN 1 ELSE 0 END) = 1 THEN '切割'
                    WHEN MAX(CASE WHEN ps.production_schedule_id IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN '已排产'
                    ELSE COALESCE(MAX(dp.delivery_status), '未排产')
                END AS real_process_status
            FROM delivery_plan dp
            LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
            LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN production_process_log ppl ON pb.production_batch_id = ppl.production_batch_id
            LEFT JOIN production_measurement pm ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
            GROUP BY dp.delivery_plan_id
        )
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            dp.actual_delivery_date,
            dp.actual_delivery_qty,
            COALESCE(bs.real_process_status, dp.delivery_status, '未排产') AS delivery_status,

            oi.po_no,
            oi.customer_pn,
            oi.product_spec_text,
            oi.trace_key,
            c.customer_name,

            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status
        FROM delivery_plan dp
        JOIN order_item oi ON dp.order_item_id = oi.order_item_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN production_schedule ps ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN batch_status bs ON dp.delivery_plan_id = bs.delivery_plan_id
        ORDER BY oi.order_item_id, dp.delivery_batch_no, dp.planned_delivery_date
    """, conn)

    if trace_df.empty:
        st.info("当前没有可追踪的批次数据。")
        return

    st.subheader("交付批次追踪总表")

    summary_df = trace_df.rename(columns={
        "delivery_plan_id": "交付计划编号",
        "delivery_batch_no": "交付批次",
        "planned_delivery_date": "计划交付日期",
        "planned_delivery_qty": "计划交付数量",
        "actual_delivery_date": "实际交付日期",
        "actual_delivery_qty": "实际交付数量",
        "delivery_status": "交付状态",
        "customer_name": "客户名称",
        "production_schedule_id": "排程编号",
        "production_batch_id": "生产批次编号",
        "batch_code": "批次号",
        "required_production_qty": "应生产数量",
        "actual_qty": "实际生产数量",
        "production_flow_status": "生产状态"
    })
    show_df(summary_df, hide_index=True)

    st.markdown("---")

    selected_delivery_plan_id = st.selectbox(
        "选择一个交付批次追踪",
        trace_df["delivery_plan_id"].tolist(),
        format_func=lambda x: (
            f"{x} | "
            f"{trace_df.loc[trace_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
            f"第{int(trace_df.loc[trace_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])}批 | "
            f"{trace_df.loc[trace_df['delivery_plan_id'] == x, 'product_spec_text'].iloc[0]}"
        ),
        key="batch_tracking_delivery_plan_select"
    )

    selected_row = trace_df[trace_df["delivery_plan_id"] == selected_delivery_plan_id].iloc[0]
    current_status = get_delivery_plan_process_status(conn, int(selected_delivery_plan_id))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户", str(selected_row["customer_name"]))
    c2.metric("订单号", str(selected_row["po_no"]))
    c3.metric("交付批次", f"第 {int(selected_row['delivery_batch_no'])} 批")
    c4.metric("当前状态", current_status)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("计划交付日期", str(selected_row["planned_delivery_date"]))
    c6.metric("计划交付数量", f"{float(selected_row['planned_delivery_qty'] or 0):.0f}")
    c7.metric("实际交付数量", f"{float(selected_row['actual_delivery_qty'] or 0):.0f}")
    c8.metric("批次号", str(selected_row["batch_code"]) if pd.notna(selected_row["batch_code"]) else "-")

    c9, c10, c11 = st.columns(3)
    c9.metric("应生产数量", f"{float(selected_row['required_production_qty'] or 0):.0f}")
    c10.metric("实际生产数量", f"{float(selected_row['actual_qty'] or 0):.0f}")
    c11.metric("生产状态", str(selected_row["production_flow_status"]) if pd.notna(selected_row["production_flow_status"]) else "-")

    render_sales_process_flow(
        current_status if current_status in ["未排产", "已排产", "切割", "清洗", "质检", "已入库"] else "未排产"
    )

    st.markdown("---")

    # 1. 排产信息
    schedule_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.order_item_id,
            ps.delivery_plan_id,
            ps.production_batch_id,
            ps.scheduled_start_date,
            ps.scheduled_end_date
        FROM production_schedule ps
        WHERE ps.delivery_plan_id = ?
        ORDER BY ps.production_schedule_id
    """, conn, params=[int(selected_delivery_plan_id)])

    # 2. 批次主信息
    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.special_process,
            pb.material,
            pb.common_gauge_size,
            pb.stop_gauge_size,
            pb.production_flow_status,
            pb.required_production_qty,
            pb.actual_qty,
            pb.semi_finished_wh_qty,
            pb.finished_wh_qty
        FROM production_schedule ps
        JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
        WHERE ps.delivery_plan_id = ?
        ORDER BY pb.production_batch_id
    """, conn, params=[int(selected_delivery_plan_id)])

    # 3. 工序日志
    process_df = pd.read_sql_query("""
        SELECT
            ppl.process_log_id,
            ppl.production_batch_id,
            ppl.process_step,
            ppl.equipment_code,
            ppl.operator_name,
            ppl.input_qty,
            ppl.output_qty,
            ppl.scrap_qty,
            ppl.process_status,
            ppl.start_time,
            ppl.end_time,
            ppl.remark
        FROM production_schedule ps
        JOIN production_process_log ppl ON ps.production_batch_id = ppl.production_batch_id
        WHERE ps.delivery_plan_id = ?
        ORDER BY ppl.process_log_id DESC
    """, conn, params=[int(selected_delivery_plan_id)])

    # 4. 质检记录
    measurement_df = pd.read_sql_query("""
        SELECT
            pm.measurement_id,
            pm.production_batch_id,
            pm.quality_status,
            pm.release_status,
            pm.inspected_at,
            pm.release_by
        FROM production_schedule ps
        JOIN production_measurement pm ON ps.production_batch_id = pm.production_batch_id
        WHERE ps.delivery_plan_id = ?
        ORDER BY pm.measurement_id DESC
    """, conn, params=[int(selected_delivery_plan_id)])

    # 5. 入库 Lot
    lot_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.production_batch_id,
            il.lot_code,
            il.trace_key,
            il.location,
            il.available_qty,
            il.reserved_qty,
            il.lot_status,
            il.release_status,
            il.last_out_qty,
            il.last_out_time
        FROM production_schedule ps
        JOIN inventory_lot il ON ps.production_batch_id = il.production_batch_id
        WHERE ps.delivery_plan_id = ?
        ORDER BY il.inventory_lot_id
    """, conn, params=[int(selected_delivery_plan_id)])

    # 6. 出货记录（先按订单显示，再结合本批信息参考）
    shipment_df = pd.read_sql_query("""
        SELECT
            s.shipment_id,
            s.shipment_no,
            s.ship_date,
            s.shipment_status,
            si.shipment_item_id,
            si.order_item_id,
            si.inventory_lot_id,
            si.shipped_qty,
            si.packaging_label_code,
            si.trace_key
        FROM shipment_item si
        JOIN shipment s ON si.shipment_id = s.shipment_id
        WHERE si.order_item_id = ?
        ORDER BY s.shipment_id DESC, si.shipment_item_id DESC
    """, conn, params=[int(selected_row["order_item_id"])])

    # 7. 库存流水（按本批次 lot 追踪）
    txn_df = pd.read_sql_query("""
        SELECT
            itl.txn_id,
            itl.inventory_lot_id,
            il.lot_code,
            itl.txn_type,
            itl.qty,
            itl.txn_time,
            itl.txn_reason,
            itl.reference_no
        FROM inventory_transaction_log itl
        JOIN inventory_lot il ON itl.inventory_lot_id = il.inventory_lot_id
        WHERE il.production_batch_id IN (
            SELECT production_batch_id
            FROM production_schedule
            WHERE delivery_plan_id = ?
        )
        ORDER BY itl.txn_id DESC
    """, conn, params=[int(selected_delivery_plan_id)])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "排产",
        "工序",
        "质检",
        "入库",
        "出货",
        "流水"
    ])

    with tab1:
        st.markdown("### 排产记录")
        if schedule_df.empty:
            st.info("当前没有排产记录。")
        else:
            show_df(schedule_df, hide_index=True)

        st.markdown("---")
        st.markdown("### 批次主信息")
        if batch_df.empty:
            st.info("当前没有批次主信息。")
        else:
            show_df(batch_df, hide_index=True)

        st.markdown("---")
        st.subheader("批次数量调整")

        if not batch_df.empty:
            batch_row = batch_df.iloc[0]
            batch_id = int(batch_row["production_batch_id"])

            current_required_qty = float(batch_row["required_production_qty"]) if pd.notna(batch_row["required_production_qty"]) else 0.0
            current_actual_qty = float(batch_row["actual_qty"]) if pd.notna(batch_row["actual_qty"]) else 0.0

            col1, col2 = st.columns(2)
            with col1:
                edit_required_qty = st.number_input(
                    "修改应生产数量",
                    min_value=0.0,
                    value=current_required_qty,
                    step=1.0,
                    key=f"edit_required_qty_dp_{selected_delivery_plan_id}"
                )
            with col2:
                edit_actual_qty = st.number_input(
                    "修改实际生产数量",
                    min_value=0.0,
                    value=current_actual_qty,
                    step=1.0,
                    key=f"edit_actual_qty_dp_{selected_delivery_plan_id}"
                )

            if st.button("保存批次数量调整", key=f"save_batch_qty_dp_{selected_delivery_plan_id}"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE production_batch
                    SET required_production_qty = ?,
                        actual_qty = ?
                    WHERE production_batch_id = ?
                """, (
                    float(edit_required_qty),
                    float(edit_actual_qty),
                    batch_id
                ))
                conn.commit()
                st.success("批次数量已更新")
                st.rerun()

    with tab2:
        st.markdown("### 工序日志")
        if process_df.empty:
            st.info("当前没有工序日志。")
        else:
            show_df(process_df, hide_index=True)

    with tab3:
        st.markdown("### 质检记录")
        if measurement_df.empty:
            st.info("当前没有质检记录。")
        else:
            show_df(measurement_df, hide_index=True)

    with tab4:
        st.markdown("### 入库 Lot")
        if lot_df.empty:
            st.info("当前没有入库 Lot。")
        else:
            show_df(lot_df, hide_index=True)

    with tab5:
        st.markdown("### 出货记录")
        if shipment_df.empty:
            st.info("当前没有出货记录。")
        else:
            show_df(shipment_df, hide_index=True)

    with tab6:
        st.markdown("### 库存流水")
        if txn_df.empty:
            st.info("当前没有库存流水。")
        else:
            show_df(txn_df, hide_index=True)


def page_measurement_entry(conn):
    st.header("检测录入")

    batch_df = pd.read_sql_query("""
        SELECT pb.production_batch_id, pb.batch_code, pb.trace_key, pb.production_flow_status
        FROM production_batch pb
        ORDER BY pb.production_batch_id
    """, conn)

    if batch_df.empty:
        st.warning("当前没有可检测的生产批次。")
        return

    with st.form("measurement_entry_form"):
        batch_id = st.selectbox(
            "选择生产批次",
            batch_df["production_batch_id"].tolist(),
            format_func=lambda x: f"{x} | {batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]}"
        )

        quality_status = st.selectbox("质量等级", ["A", "B", "C"])
        release_status = st.selectbox("放行状态", ["released", "hold", "pending"])
        release_by = st.text_input("检测/放行人", value="QC User")
        inspected_at = st.text_input("检测时间", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        submitted = st.form_submit_button("提交检测结果")

    if submitted:
        cursor = conn.cursor()

        exists = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM production_measurement
            WHERE production_batch_id = ?
        """, conn, params=[batch_id])["cnt"].iloc[0]

        if exists == 0:
            cursor.execute("""
                INSERT INTO production_measurement (
                    production_batch_id, quality_status, release_status, inspected_at, release_by
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                batch_id, quality_status, release_status, inspected_at, release_by
            ))
        else:
            cursor.execute("""
                UPDATE production_measurement
                SET quality_status = ?,
                    release_status = ?,
                    inspected_at = ?,
                    release_by = ?
                WHERE production_batch_id = ?
            """, (
                quality_status, release_status, inspected_at, release_by, batch_id
            ))

        cursor.execute("""
            SELECT pb.trace_key, pb.actual_qty, oi.product_id, oi.spec_id
            FROM production_batch pb
            JOIN production_schedule ps
              ON pb.production_batch_id = ps.production_batch_id
            JOIN order_item oi
              ON ps.order_item_id = oi.order_item_id
            WHERE pb.production_batch_id = ?
            LIMIT 1
        """, (batch_id,))
        row = cursor.fetchone()

        if row:
            trace_key, actual_qty, product_id, spec_id = row

            if release_status == "released":
                exists_lot = pd.read_sql_query("""
                    SELECT COUNT(*) AS cnt
                    FROM inventory_lot
                    WHERE production_batch_id = ?
                """, conn, params=[batch_id])["cnt"].iloc[0]

                if exists_lot == 0:
                    lot_code = f"LOT-AUTO-{batch_id:03d}"
                    cursor.execute("""
                        INSERT INTO inventory_lot (
                            production_batch_id, product_id, spec_id, lot_code, trace_key,
                            location, available_qty, reserved_qty, lot_status, release_status,
                            exclusive_customer, forbidden_customer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'available', 'released', '', '')
                    """, (
                        batch_id, product_id, spec_id, lot_code, trace_key,
                        "WH-AUTO", actual_qty or 0
                    ))
                else:
                    cursor.execute("""
                        UPDATE inventory_lot
                        SET lot_status = 'available',
                            release_status = 'released'
                        WHERE production_batch_id = ?
                    """, (batch_id,))

            elif release_status == "hold":
                cursor.execute("""
                    UPDATE inventory_lot
                    SET lot_status = 'hold',
                        release_status = 'hold'
                    WHERE production_batch_id = ?
                """, (batch_id,))

            elif release_status == "pending":
                cursor.execute("""
                    UPDATE inventory_lot
                    SET lot_status = 'hold',
                        release_status = 'pending'
                    WHERE production_batch_id = ?
                """, (batch_id,))

        conn.commit()
        st.success("检测结果已保存，相关 Lot 状态已同步")

    st.subheader("当前检测记录")
    df = pd.read_sql_query("""
        SELECT *
        FROM production_measurement
        ORDER BY measurement_id DESC
    """, conn)
    show_df(df)

def page_quality_release(conn):
    st.header("质量放行")

    df = pd.read_sql_query("""
        SELECT
            pm.measurement_id,
            pm.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.required_production_qty,
            pb.actual_qty,
            pm.quality_status,
            pm.release_status,
            pm.inspected_at,
            pm.release_by,
            ps.delivery_plan_id,
            dp.delivery_status,
            oi.po_no,
            oi.product_spec_text,
            COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material
        FROM production_measurement pm
        JOIN production_batch pb
            ON pm.production_batch_id = pb.production_batch_id
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        ORDER BY pm.measurement_id DESC
    """, conn)

    if df.empty:
        st.info("当前没有待放行或已放行的质检记录。")
        return

    st.subheader("质检 / 放行记录")
    show_df(df, hide_index=True)

    st.markdown("---")
    st.subheader("执行质量放行")

    selected_measurement_id = st.selectbox(
        "选择质检记录",
        df["measurement_id"].tolist(),
        format_func=lambda x: (
            f"检测 {x} | "
            f"{df.loc[df['measurement_id'] == x, 'batch_code'].iloc[0]} | "
            f"状态 {df.loc[df['measurement_id'] == x, 'release_status'].iloc[0]}"
        ),
        key="quality_release_measurement_select"
    )

    selected = df[df["measurement_id"] == selected_measurement_id].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("生产批号", str(selected["batch_code"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("实际生产数量", f"{float(selected['actual_qty'] or 0):.0f}")
    c4.metric("当前放行状态", str(selected["release_status"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("规格", str(selected["product_spec_text"]))
    c6.metric("特殊工艺", str(selected["special_process"]))
    c7.metric("材质", str(selected["material"]))
    c8.metric("交付状态", str(selected["delivery_status"]))

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    new_quality_status = st.selectbox(
        "质量等级",
        ["A", "B", "C", "Pending", "NG"],
        index=0,
        key="quality_release_quality_status"
    )

    new_release_status = st.selectbox(
        "放行状态",
        ["released", "hold", "pending"],
        index=0,
        key="quality_release_release_status"
    )

    release_by = st.text_input(
        "放行人",
        value="QC User",
        key="quality_release_by"
    )

    if st.button("更新放行状态并同步库存", key="quality_release_submit"):
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = ?,
                release_status = ?,
                inspected_at = datetime('now'),
                release_by = ?
            WHERE measurement_id = ?
        """, (
            new_quality_status,
            new_release_status,
            release_by,
            int(selected_measurement_id)
        ))

        conn.commit()

        if new_release_status == "released":
            ok, msg = auto_inbound_after_quality_release(
                conn,
                int(selected["production_batch_id"])
            )

            if ok:
                st.success(msg)
            else:
                st.warning(msg)

        elif new_release_status == "hold":
            if pd.notna(selected["delivery_plan_id"]):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE delivery_plan
                    SET delivery_status = '质检中'
                    WHERE delivery_plan_id = ?
                """, (
                    int(selected["delivery_plan_id"]),
                ))
                conn.commit()

            st.warning("该批次已设为 hold，暂不入库。")

        else:
            st.info("该批次保持 pending，暂不入库。")

        st.rerun()





def page_realtime_query(conn):
    st.header("实时刷新查询")

    auto_refresh = st.checkbox("开启自动刷新说明", value=True)

    tab1, tab2, tab3, tab4 = st.tabs(["按 Trace Key", "按订单", "按批次", "按 Lot"])

    with tab1:
        keys_df = pd.read_sql_query("""
            SELECT DISTINCT trace_key
            FROM order_item
            WHERE trace_key IS NOT NULL
            ORDER BY trace_key
        """, conn)

        if keys_df.empty:
            st.info("当前没有 Trace Key 数据。")
        else:
            selected_key = st.selectbox(
                "选择 Trace Key",
                keys_df["trace_key"].tolist(),
                key="rt_trace_key"
            )

            if st.button("查询 Trace Key", key="btn_trace_key"):
                df = pd.read_sql_query("""
                    SELECT *
                    FROM v_trace_key_full_flow
                    WHERE trace_key = ?
                """, conn, params=[selected_key])

                if df.empty:
                    st.warning("未查到该 Trace Key")
                else:
                    show_df(df)

    with tab2:
        po_df = pd.read_sql_query("""
            SELECT order_item_id, po_no, trace_key, item_status, ordered_qty, shipped_qty
            FROM order_item
            ORDER BY order_item_id
        """, conn)

        if po_df.empty:
            st.info("当前没有订单数据。")
        else:
            po_id = st.selectbox(
                "选择订单明细",
                po_df["order_item_id"].tolist(),
                format_func=lambda x: f"{x} | {po_df.loc[po_df['order_item_id'] == x, 'po_no'].iloc[0]}",
                key="rt_order_item_id"
            )

            if st.button("查询订单链路", key="btn_order"):
                df = pd.read_sql_query("""
                    SELECT
                        oi.*,
                        o.order_date,
                        o.order_status,
                        c.customer_name,
                        dp.planned_delivery_date,
                        dp.planned_delivery_qty,
                        dp.actual_delivery_date,
                        dp.actual_delivery_qty,
                        pb.production_batch_id,
                        pb.batch_code,
                        pb.production_flow_status,
                        il.inventory_lot_id,
                        il.lot_code,
                        il.available_qty,
                        s.shipment_no,
                        s.ship_date
                    FROM order_item oi
                    JOIN orders o ON oi.order_id = o.order_id
                    JOIN customer c ON o.customer_id = c.customer_id
                    LEFT JOIN delivery_plan dp ON oi.order_item_id = dp.order_item_id
                    LEFT JOIN production_schedule ps ON oi.order_item_id = ps.order_item_id
                    LEFT JOIN production_batch pb ON ps.production_batch_id = pb.production_batch_id
                    LEFT JOIN inventory_lot il ON pb.production_batch_id = il.production_batch_id
                    LEFT JOIN shipment_item si ON oi.order_item_id = si.order_item_id
                    LEFT JOIN shipment s ON si.shipment_id = s.shipment_id
                    WHERE oi.order_item_id = ?
                """, conn, params=[po_id])

                show_df(df)

    with tab3:
        batch_df = pd.read_sql_query("""
            SELECT production_batch_id, batch_code, trace_key, production_flow_status
            FROM production_batch
            ORDER BY production_batch_id
        """, conn)

        if batch_df.empty:
            st.info("当前没有批次数据。")
        else:
            batch_id = st.selectbox(
                "选择批次",
                batch_df["production_batch_id"].tolist(),
                format_func=lambda x: f"{x} | {batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]}",
                key="rt_batch_id"
            )

            if st.button("查询批次状态", key="btn_batch"):
                batch_info = pd.read_sql_query("""
                    SELECT *
                    FROM production_batch
                    WHERE production_batch_id = ?
                """, conn, params=[batch_id])

                process_info = pd.read_sql_query("""
                    SELECT *
                    FROM production_process_log
                    WHERE production_batch_id = ?
                    ORDER BY process_log_id DESC
                """, conn, params=[batch_id])

                qc_info = pd.read_sql_query("""
                    SELECT *
                    FROM production_measurement
                    WHERE production_batch_id = ?
                """, conn, params=[batch_id])

                lot_info = pd.read_sql_query("""
                    SELECT *
                    FROM inventory_lot
                    WHERE production_batch_id = ?
                """, conn, params=[batch_id])

                st.subheader("批次主信息")
                show_df(batch_info)
                st.subheader("工序日志")
                show_df(process_info)
                st.subheader("检测记录")
                show_df(qc_info)
                st.subheader("库存")
                show_df(lot_info)

    with tab4:
        lot_df = pd.read_sql_query("""
            SELECT inventory_lot_id, lot_code, trace_key, available_qty, lot_status
            FROM inventory_lot
            ORDER BY inventory_lot_id
        """, conn)

        if lot_df.empty:
            st.info("当前没有 Lot 数据。")
        else:
            lot_id = st.selectbox(
                "选择 Lot",
                lot_df["inventory_lot_id"].tolist(),
                format_func=lambda x: f"{x} | {lot_df.loc[lot_df['inventory_lot_id'] == x, 'lot_code'].iloc[0]}",
                key="rt_lot_id"
            )

            if st.button("查询 Lot 状态", key="btn_lot"):
                df = pd.read_sql_query("""
                    SELECT
                        il.*,
                        pb.batch_code,
                        pb.production_flow_status,
                        oi.po_no,
                        oi.customer_pn,
                        oi.drawing_version,
                        s.shipment_no,
                        s.ship_date,
                        si.shipped_qty
                    FROM inventory_lot il
                    LEFT JOIN production_batch pb ON il.production_batch_id = pb.production_batch_id
                    LEFT JOIN shipment_item si ON il.inventory_lot_id = si.inventory_lot_id
                    LEFT JOIN shipment s ON si.shipment_id = s.shipment_id
                    LEFT JOIN order_item oi ON il.trace_key = oi.trace_key
                    WHERE il.inventory_lot_id = ?
                """, conn, params=[lot_id])

                show_df(df)

    if auto_refresh:
        st.caption("录入或更新后，再点击查询按钮即可看到最新数据库结果。")


def show_trace_flow(df):
    first = df.iloc[0]

    st.subheader("Trace Key 图表版追踪页面")
    st.caption("一页穿透查看订单 → 批次 → Lot → 出货链路")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("批次数", int(df["production_batch_id"].dropna().nunique()))
    k2.metric("Lot 数", int(df["inventory_lot_id"].dropna().nunique()))
    k3.metric("发货次数", int(df["shipment_id"].dropna().nunique()))
    k4.metric("总发货量", int(df["shipped_qty"].fillna(0).sum()))

    st.markdown("---")

    a, b, c, d = st.columns(4)

    with a:
        st.markdown("### 1. 订单明细")
        st.write(f"**客户**: {first.get('customer_name', '')}")
        st.write(f"**PO**: {first.get('po_no', '')}")
        st.write(f"**规格**: {first.get('spec_code', '')}")
        st.write(f"**图纸版本**: {first.get('drawing_version', '')}")
        st.write(f"**订单状态**: {first.get('order_status', '')}")
        st.write(f"**明细状态**: {first.get('item_status', '')}")

    with b:
        st.markdown("### 2. 生产批次")
        st.write(f"**批次号**: {first.get('batch_code', '')}")
        st.write(f"**特殊工艺**: {first.get('special_process', '')}")
        st.write(f"**通规尺寸**: {first.get('common_gauge_size', '')}")
        st.write(f"**止规尺寸**: {first.get('stop_gauge_size', '')}")
        st.write(f"**质量等级**: {first.get('quality_status', '')}")
        st.write(f"**放行状态**: {first.get('release_status', '')}")

    with c:
        st.markdown("### 3. 库存")
        st.write(f"**Lot 编号**: {first.get('lot_code', '')}")
        st.write(f"**库位**: {first.get('location', '')}")
        st.write(f"**可用数量**: {first.get('available_qty', '')}")
        st.write(f"**预留数量**: {first.get('reserved_qty', '')}")
        st.write(f"**Lot 状态**: {first.get('lot_status', '')}")
        st.write(f"**专供客户**: {first.get('exclusive_customer', '')}")

    with d:
        st.markdown("### 4. 出货记录")
        st.write(f"**Shipment No**: {first.get('shipment_no', 'No Shipment Yet')}")
        st.write(f"**发货日期**: {first.get('ship_date', 'No Shipment Yet')}")
        st.write(f"**发货数量**: {first.get('shipped_qty', 0)}")
        st.write(f"**计划交付**: {first.get('planned_delivery_plan', '')}")
        st.write(f"**实际交付**: {first.get('actual_delivery_plan', '')}")

    st.markdown("---")
    st.subheader("全流程明细表")
    show_df(df, hide_index=True)


def page_trace_query(conn):
    st.header("Trace Key 快速查询")

    keys_df = get_trace_keys(conn)
    default_key = keys_df["trace_key"].iloc[0] if not keys_df.empty else ""

    selected_key = st.selectbox(
        "选择可用 Trace Key",
        keys_df["trace_key"].tolist() if not keys_df.empty else [""]
    )

    trace_key = st.text_input("输入 Trace Key", selected_key if selected_key else default_key)

    if st.button("查询"):
        df_dash = pd.read_sql_query("""
            SELECT *
            FROM v_trace_key_dashboard
            WHERE trace_key = ?
        """, conn, params=[trace_key])

        df_flow = pd.read_sql_query("""
            SELECT *
            FROM v_trace_key_full_flow
            WHERE trace_key = ?
        """, conn, params=[trace_key])

        if df_dash.empty or df_flow.empty:
            st.warning("没有查到这个 Trace Key。")
        else:
            st.success(f"已查询 Trace Key: {trace_key}")
            st.subheader("追踪汇总")
            show_df(df_dash, hide_index=True)
            show_trace_flow(df_flow)

            excel_bytes = dataframe_to_excel_bytes({
                "trace_dashboard": df_dash,
                "trace_full_flow": df_flow
            })
            st.download_button(
                label="下载当前 Trace Key 结果（Excel）",
                data=excel_bytes,
                file_name=f"trace_{trace_key}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


def page_excel_center(conn):
    st.header("Excel 数据中心")

    tab1, tab2, tab3 = st.tabs(["数据导出", "数据导入", "模板下载"])

    with tab1:
        st.subheader("分类导出 / 汇总导出")

        data_map = get_export_data_map(conn)
        export_options = list(data_map.keys())

        col1, col2 = st.columns(2)
        with col1:
            selected_export = st.selectbox(
                "选择导出数据集",
                export_options,
                format_func=lambda x: table_label(x)
            )
        with col2:
            export_mode = st.radio("导出方式", ["单表导出", "全部多 Sheet 导出"], horizontal=True)

        if export_mode == "单表导出":
            df = data_map[selected_export]
            show_df(df)
            excel_bytes = dataframe_to_excel_bytes({selected_export: df})
            st.download_button(
                label=f"下载 {table_label(selected_export)}.xlsx",
                data=excel_bytes,
                file_name=f"{selected_export}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("将当前系统主要数据导出为一个多 Sheet Excel 文件。")
            excel_bytes = dataframe_to_excel_bytes(data_map)
            st.download_button(
                label="下载全量业务数据（multi-sheet Excel）",
                data=excel_bytes,
                file_name="glass_tube_mes_full_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        st.subheader("分类导入 / 更新数据库")

        import_type = st.selectbox(
            "选择导入类型",
            ["订单导入", "检测导入", "库存调整导入", "生产过程导入"]
        )

        uploaded_file = st.file_uploader(
            "上传 Excel / CSV 文件",
            type=["xlsx", "csv"],
            key="excel_import_uploader"
        )

        if import_type == "订单导入":
            required_columns = [
                "customer_name", "po_no", "customer_pn", "drawing_version", "factory_part_no",
                "spec_code", "ordered_qty", "overall_deadline", "quality_requirement",
                "special_process", "item_note", "planned_delivery_date", "planned_delivery_qty"
            ]
        elif import_type == "检测导入":
            required_columns = ["batch_code", "quality_status", "release_status", "inspected_at", "release_by"]
        elif import_type == "库存调整导入":
            required_columns = ["lot_code", "location", "available_qty", "reserved_qty", "lot_status", "release_status"]
        else:
            required_columns = [
                "batch_code", "process_step", "equipment_code", "operator_name",
                "input_qty", "output_qty", "scrap_qty", "process_status",
                "start_time", "end_time", "remark"
            ]

        st.caption("系统要求字段：" + ", ".join(required_columns))
        st.caption("支持中文表头自动映射。")
        st.info("支持 .xlsx 和 .csv，也支持中文业务表头自动映射。建议优先使用模板，成功率更高。")

        if uploaded_file is not None:
            try:
                original_df, read_msg = read_uploaded_table(uploaded_file)
                st.info(read_msg)

                st.subheader("上传原始预览")
                show_df(original_df)

                mapped_df, rename_map, unmatched_columns = auto_map_headers(original_df, import_type)

                show_header_mapping_result(original_df, mapped_df, rename_map)

                missing = validate_excel_df(mapped_df, required_columns)

                if unmatched_columns:
                    with st.expander("未参与映射的原始列"):
                        st.write(unmatched_columns)

                if missing:
                    st.error("缺少系统必需字段：" + ", ".join(missing))
                else:
                    st.success("字段检查通过，可以导入。")
                    st.subheader("映射后数据预览")
                    show_df(mapped_df)

                    if st.button("确认导入到数据库"):
                        if import_type == "订单导入":
                            ok, msg = import_orders_from_excel(conn, mapped_df)
                        elif import_type == "检测导入":
                            ok, msg = import_measurements_from_excel(conn, mapped_df)
                        elif import_type == "库存调整导入":
                            ok, msg = import_inventory_from_excel(conn, mapped_df)
                        else:
                            ok, msg = import_process_logs_from_excel(conn, mapped_df)

                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            except Exception as e:
                st.error(f"读取文件失败: {e}")

    with tab3:
        st.subheader("模板下载")

        template_type = st.selectbox(
            "选择模板",
            ["订单导入模板", "检测导入模板", "库存调整模板", "生产过程导入模板"]
        )

        template_df = get_template_data(template_type)
        show_df(template_df)

        template_bytes = dataframe_to_excel_bytes({template_type: template_df})
        st.download_button(
            label=f"下载 {template_type}.xlsx",
            data=template_bytes,
            file_name=f"{template_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def page_module_config_center(conn):
    st.header("模块配置中心")

    tab1, tab2 = st.tabs(["已有模块", "新建模块"])

    with tab1:
        df = pd.read_sql_query("""
            SELECT module_id, module_code, module_name, table_name, page_mode, is_enabled, sort_order
            FROM app_module_config
            ORDER BY sort_order, module_id
        """, conn)

        if not df.empty:
            df["table_name"] = df["table_name"].apply(table_label)

        show_df(df)

    with tab2:
        st.subheader("新建无代码模块")

        with st.form("create_module_form"):
            module_code = st.text_input("模块编码", value="supplier_master")
            module_name = st.text_input("模块名称", value="供应商管理")
            table_name = st.text_input("数据表名", value="supplier_master")
            page_mode = st.selectbox("页面模式", ["form_list"])
            fields_text = st.text_area(
                "字段定义（每行一个，格式：字段名|中文名|类型|是否必填）",
                value=(
                    "supplier_code|供应商编号|text|1\n"
                    "supplier_name|供应商名称|text|1\n"
                    "contact_person|联系人|text|0\n"
                    "phone|电话|text|0\n"
                    "status|状态|select|1"
                ),
                height=180
            )
            submitted = st.form_submit_button("创建模块")

        if submitted:
            try:
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO app_module_config
                    (module_code, module_name, table_name, page_mode, is_enabled, sort_order)
                    VALUES (?, ?, ?, ?, 1, 100)
                """, (module_code.strip(), module_name.strip(), table_name.strip(), page_mode))
                module_id = cur.lastrowid

                field_rows = []
                for idx, line in enumerate(fields_text.splitlines(), start=1):
                    if not line.strip():
                        continue
                    parts = [x.strip() for x in line.split("|")]
                    if len(parts) < 4:
                        continue

                    field_name, field_label, field_type, is_required = parts[:4]
                    field_rows.append({
                        "module_id": module_id,
                        "field_name": field_name,
                        "field_label": field_label,
                        "field_type": field_type,
                        "is_required": int(is_required),
                        "is_visible_list": 1,
                        "is_visible_form": 1,
                        "is_editable": 1,
                        "default_value": "",
                        "option_source_type": "static" if field_type == "select" else None,
                        "option_source_value": f"{field_name}_options" if field_type == "select" else None,
                        "field_order": idx * 10
                    })

                for row in field_rows:
                    cur.execute("""
                        INSERT INTO app_module_field_config
                        (module_id, field_name, field_label, field_type, is_required,
                         is_visible_list, is_visible_form, is_editable, default_value,
                         option_source_type, option_source_value, field_order)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row["module_id"], row["field_name"], row["field_label"], row["field_type"], row["is_required"],
                        row["is_visible_list"], row["is_visible_form"], row["is_editable"], row["default_value"],
                        row["option_source_type"], row["option_source_value"], row["field_order"]
                    ))

                fields_df = pd.DataFrame(field_rows)
                create_dynamic_business_table(conn, table_name.strip(), fields_df)

                for row in field_rows:
                    if row["field_type"] == "select":
                        cur.execute("""
                            INSERT INTO app_module_option_config
                            (module_id, field_name, option_label, option_value, option_order)
                            VALUES (?, ?, ?, ?, ?)
                        """, (module_id, row["field_name"], "启用", "active", 10))
                        cur.execute("""
                            INSERT INTO app_module_option_config
                            (module_id, field_name, option_label, option_value, option_order)
                            VALUES (?, ?, ?, ?, ?)
                        """, (module_id, row["field_name"], "停用", "inactive", 20))

                conn.commit()
                st.success(f"模块创建成功：{module_name}")
            except Exception as e:
                st.error(f"创建模块失败：{e}")


def page_dynamic_module_center(conn):
    st.header("动态模块中心")

    modules_df = get_enabled_modules(conn)
    if modules_df.empty:
        st.info("当前还没有配置动态模块。")
        return

    selected_module_id = st.selectbox(
        "选择模块",
        modules_df["module_id"].tolist(),
        format_func=lambda x: modules_df.loc[modules_df["module_id"] == x, "module_name"].iloc[0]
    )

    module_row = modules_df[modules_df["module_id"] == selected_module_id].iloc[0]
    module_name = module_row["module_name"]
    table_name = module_row["table_name"]

    fields_df = get_module_fields(conn, selected_module_id)
    form_fields = get_dynamic_form_fields(fields_df)
    required_fields = get_dynamic_required_fields(fields_df)
    list_fields = get_dynamic_list_fields(fields_df)
    primary_key_field = get_module_primary_key_field(fields_df)

    tab1, tab2, tab3, tab4 = st.tabs(
        [f"{module_name}列表", f"新增{module_name}", f"编辑/删除{module_name}", f"{module_name}导入导出"]
    )

    with tab1:
        try:
            if list_fields:
                sql = f"SELECT record_id, {', '.join(list_fields)}, created_at FROM {table_name} ORDER BY record_id DESC"
            else:
                sql = f"SELECT * FROM {table_name} ORDER BY record_id DESC"
            df = pd.read_sql_query(sql, conn)
            show_dynamic_module_df(df, fields_df)
            st.caption(f"当前导入更新主键字段：{column_label(primary_key_field)}" if primary_key_field else "当前未配置主键字段")
        except Exception as e:
            st.error(f"读取模块数据失败：{e}")

    with tab2:
        if form_fields.empty:
            st.warning("当前模块没有可显示表单字段。")
        else:
            with st.form(f"dynamic_add_form_{selected_module_id}"):
                form_values = render_dynamic_form_with_values(
                    st, conn, selected_module_id, form_fields, initial_values={}, form_prefix="add"
                )
                submitted = st.form_submit_button("提交新增")

            if submitted:
                missing_fields = [f for f in required_fields if str(form_values.get(f, "")).strip() == ""]
                if missing_fields:
                    missing_labels = form_fields[form_fields["field_name"].isin(missing_fields)]["field_label"].tolist()
                    st.error("以下必填项为空：" + ", ".join(missing_labels))
                else:
                    try:
                        record_id = insert_dynamic_record(conn, table_name, form_values)
                        st.success(f"{module_name}新增成功，record_id={record_id}")
                    except Exception as e:
                        st.error(f"写入失败：{e}")

    with tab3:
        try:
            all_df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY record_id DESC", conn)
        except Exception as e:
            st.error(f"读取模块数据失败：{e}")
            all_df = pd.DataFrame()

        if all_df.empty:
            st.info("当前没有可编辑记录。")
        else:
            record_id = st.selectbox(
                "选择记录",
                all_df["record_id"].tolist(),
                format_func=lambda x: f"record_id={x}"
            )

            selected_row = all_df[all_df["record_id"] == record_id].iloc[0].to_dict()

            with st.form(f"dynamic_edit_form_{selected_module_id}_{record_id}"):
                edit_values = render_dynamic_form_with_values(
                    st, conn, selected_module_id, form_fields, initial_values=selected_row, form_prefix=f"edit_{record_id}"
                )

                delete_confirm_text = st.text_input("删除确认：输入 DELETE 才可删除", value="")
                c1, c2 = st.columns(2)
                with c1:
                    save_clicked = st.form_submit_button("保存修改")
                with c2:
                    delete_clicked = st.form_submit_button("删除记录")

            if save_clicked:
                missing_fields = [f for f in required_fields if str(edit_values.get(f, "")).strip() == ""]
                if missing_fields:
                    missing_labels = form_fields[form_fields["field_name"].isin(missing_fields)]["field_label"].tolist()
                    st.error("以下必填项为空：" + ", ".join(missing_labels))
                else:
                    try:
                        update_dynamic_record(conn, table_name, record_id, edit_values)
                        st.success(f"{module_name}修改成功")
                    except Exception as e:
                        st.error(f"修改失败：{e}")

            if delete_clicked:
                if delete_confirm_text.strip() != "DELETE":
                    st.error("删除失败：请先在确认框中输入 DELETE")
                else:
                    try:
                        delete_dynamic_record(conn, table_name, record_id)
                        st.success(f"record_id={record_id} 已删除")
                    except Exception as e:
                        st.error(f"删除失败：{e}")

    with tab4:
        st.subheader("模板下载")

        col_a, col_b = st.columns(2)
        with col_a:
            cn_template_df = get_dynamic_module_template_df(fields_df, label_mode="cn")
            show_dynamic_module_df(cn_template_df, fields_df)
            cn_template_bytes = dataframe_to_excel_bytes({f"{table_name}_cn_template": cn_template_df})
            st.download_button(
                label=f"下载 {module_name} 中文模板.xlsx",
                data=cn_template_bytes,
                file_name=f"{table_name}_cn_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_b:
            en_template_df = get_dynamic_module_template_df(fields_df, label_mode="en")
            show_dynamic_module_df(en_template_df, fields_df)
            en_template_bytes = dataframe_to_excel_bytes({f"{table_name}_en_template": en_template_df})
            st.download_button(
                label=f"下载 {module_name} 英文模板.xlsx",
                data=en_template_bytes,
                file_name=f"{table_name}_en_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.markdown("---")
        st.subheader("导出")

        try:
            export_df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY record_id DESC", conn)
            show_dynamic_module_df(export_df, fields_df)
            export_bytes = export_dynamic_module_excel(conn, table_name, fields_df)
            st.download_button(
                label=f"下载 {module_name}.xlsx",
                data=export_bytes,
                file_name=f"{table_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"导出失败：{e}")

        st.markdown("---")
        st.subheader("导入")

        import_mode = st.radio(
            "导入模式",
            ["按主键新增/更新（推荐）", "仅新增"],
            horizontal=True,
            key=f"dynamic_import_mode_{selected_module_id}"
        )
        mode_value = "upsert" if import_mode.startswith("按主键") else "insert_only"

        st.caption("支持 .xlsx / .csv；支持字段英文名或字段中文名。")
        st.caption(f"当前主键字段：{column_label(primary_key_field)}" if primary_key_field else "当前未识别主键字段，将退化为仅新增")
        uploaded_file = st.file_uploader(
            f"上传 {module_name} 数据文件",
            type=["xlsx", "csv"],
            key=f"dynamic_import_{selected_module_id}"
        )

        if uploaded_file is not None:
            try:
                result = import_dynamic_module_data(conn, table_name, fields_df, uploaded_file, import_mode=mode_value)
                st.info(result["read_msg"])

                st.subheader("上传原始预览")
                show_df(result["original_df"])

                if result["rename_map"]:
                    mapping_df = pd.DataFrame(
                        [{"原表头": k, "系统字段": v} for k, v in result["rename_map"].items()]
                    )
                    st.subheader("表头映射结果")
                    show_df(mapping_df, hide_index=True)

                if result["unmatched_columns"]:
                    with st.expander("未参与映射的原始列"):
                        st.write(result["unmatched_columns"])

                st.subheader("映射后预览")
                show_dynamic_module_df(result["mapped_df"], fields_df)

                if result["ok"]:
                    st.success(result["msg"])
                else:
                    st.error(result["msg"])

            except Exception as e:
                st.error(f"导入失败：{e}")

# =========================
# 覆盖版：销售 / 排产 / 生产过程页面
# 说明：
# 放在 main() 前面，用后定义函数覆盖前面的旧函数。
# =========================

def push_delivery_plan_to_production(conn, delivery_plan_id):
    cursor = conn.cursor()

    check_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            ps.production_schedule_id
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if check_df.empty:
        return False, "未找到该交付批次。"

    if pd.notna(check_df.iloc[0]["production_schedule_id"]):
        return False, "该交付批次已经排产，不能重复推送。"

    current_status = str(check_df.iloc[0]["delivery_status"])

    if current_status == "待生产确认":
        return True, "该交付批次已经推送至生产端，等待生产确认。"

    if current_status not in ["未排产", "待生产确认"]:
        return False, f"当前状态为 {current_status}，不适合重新推送。"

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '待生产确认'
        WHERE delivery_plan_id = ?
    """, (int(delivery_plan_id),))

    conn.commit()
    return True, "已推送至生产端，等待生产确认。"


def create_production_for_delivery_plan(
    conn,
    delivery_plan_id,
    planned_qty=None,
    manual_batch_code=None,
    common_gauge_size=None,
    stop_gauge_size=None
):
    """
    根据销售推送的交付批次创建生产批次和排产记录。

    新增：
    - common_gauge_size：通规尺寸，生产确认时手动录入
    - stop_gauge_size：止规尺寸，生产确认时手动录入
    """

    cursor = conn.cursor()

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            oi.trace_key,
            oi.product_spec_text,
            oi.po_no,
            oi.product_type_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if plan_df.empty:
        return False, "未找到对应交付批次。"

    row = plan_df.iloc[0]

    current_status = str(row["delivery_status"] or "未排产")

    if current_status not in ["待生产确认", "未排产"]:
        return False, f"当前交付状态为【{current_status}】，不适合创建生产批次。"

    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_schedule
        WHERE delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if int(exists_df.iloc[0]["cnt"]) > 0:
        return False, "该交付批次已经存在排产记录，无需重复创建。"

    if planned_qty is None:
        planned_qty = float(row["planned_delivery_qty"] or 0)
    else:
        planned_qty = float(planned_qty)

    if planned_qty <= 0:
        return False, "应生产数量必须大于 0。"

    batch_code = normalize_text(manual_batch_code)

    if not batch_code:
        batch_code = (
            f"BATCH-"
            f"{normalize_trace_part(row['po_no'], 'PO')}-"
            f"{int(row['delivery_batch_no'])}"
        )

    common_gauge_size = normalize_text(common_gauge_size)
    stop_gauge_size = normalize_text(stop_gauge_size)

    if not common_gauge_size:
        return False, "请填写通规尺寸。"

    if not stop_gauge_size:
        return False, "请填写止规尺寸。"

    batch_exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_batch
        WHERE batch_code = ?
    """, conn, params=[batch_code])

    if int(batch_exists_df.iloc[0]["cnt"]) > 0:
        return False, f"生产批号 {batch_code} 已存在，请更换批号。"

    cursor.execute("""
        INSERT INTO production_batch (
            batch_code,
            trace_key,
            special_process,
            material,
            common_gauge_size,
            stop_gauge_size,
            production_flow_status,
            required_production_qty,
            actual_qty,
            semi_finished_wh_qty,
            finished_wh_qty
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        batch_code,
        str(row["trace_key"]),
        str(row["special_process"]),
        str(row["material"]),
        common_gauge_size,
        stop_gauge_size,
        "planned",
        planned_qty,
        0,
        0,
        0
    ))

    production_batch_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO production_schedule (
            order_item_id,
            production_batch_id,
            scheduled_start_date,
            scheduled_end_date,
            delivery_plan_id
        ) VALUES (?, ?, date('now'), ?, ?)
    """, (
        int(row["order_item_id"]),
        int(production_batch_id),
        str(row["planned_delivery_date"]),
        int(delivery_plan_id)
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '已排产',
           sales_need_production = 0,
           sales_decision_time = datetime('now')
        WHERE delivery_plan_id = ?
    """, (
        int(delivery_plan_id),
    ))

    conn.commit()

    sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    return True, (
        f"生产批次创建成功：{batch_code}。"
        f"应生产数量：{planned_qty:.0f}；"
        f"通规：{common_gauge_size}；"
        f"止规：{stop_gauge_size}。"
    )


def page_production_process_entry(conn):
    st.header("生产过程录入")

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            pb.required_production_qty,
            pb.actual_qty,
            pb.production_flow_status,
            pb.special_process,
            COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,

            ps.production_schedule_id,
            ps.delivery_plan_id,
            ps.order_item_id,
            ps.scheduled_start_date,
            ps.scheduled_end_date,

            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            dp.planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '已排产') AS delivery_status,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.drawing_version,
            oi.factory_part_no,
            oi.product_type_text,
            oi.product_spec_text,
            oi.ordered_qty,
            oi.shipped_qty,
            oi.item_status
        FROM production_batch pb
        JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        ORDER BY pb.production_batch_id DESC
    """, conn)

    if batch_df.empty:
        st.warning("当前没有已排产的生产批次。请先在排产看板完成生产确认。")
        return

    batch_ids = [int(x) for x in batch_df["production_batch_id"].tolist()]
    target_batch_id = st.session_state.get("selected_process_batch_id", None)

    if target_batch_id is not None:
        try:
            target_batch_id = int(target_batch_id)
        except Exception:
            target_batch_id = None

    if target_batch_id in batch_ids:
        st.session_state["process_entry_batch_select"] = target_batch_id
    elif "process_entry_batch_select" not in st.session_state:
        st.session_state["process_entry_batch_select"] = int(batch_ids[0])

    batch_id = st.selectbox(
        "选择生产批次",
        batch_ids,
        format_func=lambda x: (
            f"{x} | "
            f"{batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
            f"PO {batch_df.loc[batch_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
            f"第 {int(batch_df.loc[batch_df['production_batch_id'] == x, 'delivery_batch_no'].iloc[0])} 批"
        ),
        key="process_entry_batch_select"
    )

    selected = batch_df[batch_df["production_batch_id"] == int(batch_id)].iloc[0]
    st.session_state["selected_process_batch_id"] = int(batch_id)

    st.markdown("---")

    st.subheader("交付批次生产卡片")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户", str(selected["customer_name"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
    c4.metric("生产批号", str(selected["batch_code"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("产品", str(selected["product_type_text"]))
    c6.metric("规格", str(selected["product_spec_text"]))
    c7.metric("特殊工艺", str(selected["special_process"]))
    c8.metric("材质", str(selected["material"]))

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
    c10.metric("应生产数量", f"{float(selected['required_production_qty'] or 0):.0f}")
    c11.metric("当前实际产量", f"{float(selected['actual_qty'] or 0):.0f}")
    c12.metric("生产状态", str(selected["production_flow_status"]))

    c13, c14, c15, c16 = st.columns(4)
    c13.metric("计划交付日期", str(selected["planned_delivery_date"]))
    c14.metric("计划开始", str(selected["scheduled_start_date"]))
    c15.metric("计划结束", str(selected["scheduled_end_date"]))
    c16.metric("交付状态", str(selected["delivery_status"]))

    st.caption(
        f"客户料号：{selected['customer_pn']} ｜ "
        f"图纸版本：{selected['drawing_version']} ｜ "
        f"本厂料号：{selected['factory_part_no']} ｜ "
        f"订单数量：{float(selected['ordered_qty'] or 0):.0f} ｜ "
        f"已出货：{float(selected['shipped_qty'] or 0):.0f}"
    )

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    st.markdown("---")

    st.subheader("当前批次已有生产过程记录")

    current_log_df = pd.read_sql_query("""
        SELECT
            process_log_id,
            production_batch_id,
            process_step,
            equipment_code,
            operator_name,
            input_qty,
            output_qty,
            scrap_qty,
            process_status,
            start_time,
            end_time,
            remark
        FROM production_process_log
        WHERE production_batch_id = ?
        ORDER BY process_log_id DESC
    """, conn, params=[int(batch_id)])

    if current_log_df.empty:
        st.info("当前批次还没有生产过程记录。")
    else:
        show_df(current_log_df, hide_index=True)

    st.markdown("---")

    st.subheader("录入生产过程")

    with st.form(f"production_process_entry_form_{batch_id}"):
        process_step = st.selectbox(
            "工序",
            ["Cutting", "Heating", "Forming", "Polishing", "Cleaning", "Packing"],
            key=f"process_step_{batch_id}"
        )

        equipment_code = st.text_input(
            "设备编号",
            value="EQ-001",
            key=f"equipment_code_{batch_id}"
        )

        operator_name = st.text_input(
            "操作员",
            value="Operator A",
            key=f"operator_name_{batch_id}"
        )

        input_qty = st.number_input(
            "投入数量",
            min_value=0.0,
            value=float(selected["required_production_qty"] or 100),
            step=1.0,
            key=f"input_qty_{batch_id}"
        )

        output_qty = st.number_input(
            "产出数量",
            min_value=0.0,
            value=float(selected["actual_qty"] or 0),
            step=1.0,
            key=f"output_qty_{batch_id}"
        )

        scrap_qty = st.number_input(
            "报废数量",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"scrap_qty_{batch_id}"
        )

        process_status = st.selectbox(
            "工序状态",
            ["planned", "running", "done", "hold"],
            key=f"process_status_{batch_id}"
        )

        start_time = st.text_input(
            "开始时间",
            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            key=f"start_time_{batch_id}"
        )

        end_time = st.text_input(
            "结束时间",
            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            key=f"end_time_{batch_id}"
        )

        remark = st.text_area(
            "备注",
            value="",
            key=f"remark_{batch_id}"
        )

        submitted = st.form_submit_button("提交生产过程记录")

    if submitted:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO production_process_log (
                production_batch_id,
                process_step,
                equipment_code,
                operator_name,
                input_qty,
                output_qty,
                scrap_qty,
                process_status,
                start_time,
                end_time,
                remark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(batch_id),
            process_step,
            equipment_code,
            operator_name,
            float(input_qty),
            float(output_qty),
            float(scrap_qty),
            process_status,
            start_time,
            end_time,
            remark
        ))

        if process_status in ("running", "done"):
            new_flow_status = process_step
        elif process_status == "hold":
            new_flow_status = "hold"
        else:
            new_flow_status = str(selected["production_flow_status"])

        cursor.execute("""
            UPDATE production_batch
            SET production_flow_status = ?,
                actual_qty = CASE
                    WHEN ? > COALESCE(actual_qty, 0) THEN ?
                    ELSE actual_qty
                END
            WHERE production_batch_id = ?
        """, (
            new_flow_status,
            float(output_qty),
            float(output_qty),
            int(batch_id)
        ))

        if pd.notna(selected["delivery_plan_id"]):
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '生产中'
                WHERE delivery_plan_id = ?
                  AND COALESCE(delivery_status, '') NOT IN ('已入库')
            """, (int(selected["delivery_plan_id"]),))

        conn.commit()

        st.success("生产过程记录已写入，批次状态已更新。")
        st.rerun()

    st.markdown("---")

    st.subheader("所有生产过程日志")

    all_log_df = pd.read_sql_query("""
        SELECT
            ppl.process_log_id,
            pb.batch_code,
            ppl.production_batch_id,
            ppl.process_step,
            ppl.equipment_code,
            ppl.operator_name,
            ppl.input_qty,
            ppl.output_qty,
            ppl.scrap_qty,
            ppl.process_status,
            ppl.start_time,
            ppl.end_time,
            ppl.remark
        FROM production_process_log ppl
        JOIN production_batch pb
            ON ppl.production_batch_id = pb.production_batch_id
        ORDER BY ppl.process_log_id DESC
    """, conn)

    if all_log_df.empty:
        st.info("当前还没有任何生产过程日志。")
    else:
        show_df(all_log_df, hide_index=True)


def page_production_process_entry(conn):
    st.header("生产｜生产过程录入")

    st.info(
        "本页面已启用工序数量自动流转："
        "第一道工序投入数量 = 应生产数量；"
        "后续工序投入数量 = 上一道已完成工序的产出数量；"
        "报废数量 = 投入数量 - 产出数量。"
        "同时启用防重复录入：同一批次同一工序已完成后，不能再次提交 done。"
    )

    PROCESS_FLOW = [
        "Cutting",
        "Heating",
        "Forming",
        "Polishing",
        "Cleaning",
        "Packing"
    ]

    PROCESS_CN = {
        "Cutting": "切割",
        "Heating": "加热",
        "Forming": "成型",
        "Polishing": "抛光",
        "Cleaning": "清洗",
        "Packing": "包装"
    }

    # =========================
    # 1. 读取可录入生产批次
    # =========================
    batch_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.delivery_plan_id,
            ps.order_item_id,
            ps.production_batch_id,
            ps.scheduled_start_date,
            ps.scheduled_end_date,

            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,
            COALESCE(pb.special_process, 'STANDARD') AS special_process,
            COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            oi.ordered_qty,
            oi.shipped_qty
        FROM production_schedule ps
        JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        WHERE COALESCE(dp.delivery_status, '未排产') IN (
            '已排产',
            '生产中',
            '质检中',
            '待入库确认'
        )
        ORDER BY ps.production_schedule_id DESC
    """, conn)

    if batch_df.empty:
        st.info("当前没有可录入的生产批次。请先在【排产看板】中完成生产确认。")
        return

    batch_ids = [int(x) for x in batch_df["production_batch_id"].tolist()]

    # =========================
    # 2. 处理从其他页面跳转过来的批次
    # =========================
    if "process_entry_batch_select" in st.session_state:
        try:
            current_selected_batch = int(st.session_state["process_entry_batch_select"])
            if current_selected_batch not in batch_ids:
                del st.session_state["process_entry_batch_select"]
        except Exception:
            del st.session_state["process_entry_batch_select"]

    jump_batch_id = st.session_state.get("selected_process_batch_id", None)

    if jump_batch_id in batch_ids:
        st.session_state["process_entry_batch_select"] = int(jump_batch_id)

    # =========================
    # 3. 选择生产批次
    # =========================
    selected_batch_id = st.selectbox(
        "选择生产批次",
        batch_ids,
        format_func=lambda x: (
            f"【{batch_df.loc[batch_df['production_batch_id'] == x, 'delivery_status'].iloc[0]}】 "
            f"{batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
            f"PO {batch_df.loc[batch_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
            f"第 {int(batch_df.loc[batch_df['production_batch_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
            f"应生产 {float(batch_df.loc[batch_df['production_batch_id'] == x, 'required_production_qty'].iloc[0] or 0):.0f} | "
            f"实际 {float(batch_df.loc[batch_df['production_batch_id'] == x, 'actual_qty'].iloc[0] or 0):.0f}"
        ),
        key="process_entry_batch_select"
    )

    selected = batch_df[
        batch_df["production_batch_id"] == selected_batch_id
    ].iloc[0]

    batch_id = int(selected["production_batch_id"])

    # =========================
    # 4. 当前批次工序记录
    # =========================
    current_log_df = pd.read_sql_query("""
        SELECT
            process_log_id,
            production_batch_id,
            process_step,
            equipment_code,
            operator_name,
            COALESCE(input_qty, 0) AS input_qty,
            COALESCE(output_qty, 0) AS output_qty,
            COALESCE(scrap_qty, 0) AS scrap_qty,
            process_status,
            start_time,
            end_time,
            remark
        FROM production_process_log
        WHERE production_batch_id = ?
        ORDER BY process_log_id ASC
    """, conn, params=[batch_id])

    done_log_df = current_log_df[
        current_log_df["process_status"].astype(str).str.lower() == "done"
    ].copy()

    completed_steps = done_log_df["process_step"].astype(str).tolist()
    completed_standard_steps = [x for x in completed_steps if x in PROCESS_FLOW]

    # 建议下一道工序
    suggested_process_step = PROCESS_FLOW[0]
    for step in PROCESS_FLOW:
        if step not in completed_steps:
            suggested_process_step = step
            break

    all_standard_done = len(set(completed_standard_steps)) >= len(PROCESS_FLOW)

    if all_standard_done:
        suggested_process_step = "Packing"

    completed_count = len(set(completed_standard_steps))
    progress_ratio = completed_count / len(PROCESS_FLOW)

    if not done_log_df.empty:
        latest_done = done_log_df.sort_values("process_log_id").iloc[-1]
        latest_done_step = str(latest_done["process_step"])
        latest_done_output = float(latest_done["output_qty"] or 0)
    else:
        latest_done_step = "-"
        latest_done_output = 0.0

    total_input_qty = pd.to_numeric(
        current_log_df["input_qty"],
        errors="coerce"
    ).fillna(0).sum() if not current_log_df.empty else 0.0

    total_output_qty = pd.to_numeric(
        current_log_df["output_qty"],
        errors="coerce"
    ).fillna(0).sum() if not current_log_df.empty else 0.0

    total_scrap_qty = pd.to_numeric(
        current_log_df["scrap_qty"],
        errors="coerce"
    ).fillna(0).sum() if not current_log_df.empty else 0.0

    # =========================
    # 5. 页面内分区跳转
    # 必须在 radio 创建前修改 process_entry_section
    # =========================
    section_options = [
        "① 生产任务卡",
        "② 录入本次工序",
        "③ 工序记录"
    ]

    if "_process_entry_section_next" in st.session_state:
        st.session_state["_next_process_entry_section"] = st.session_state.pop(
            "_process_entry_section_next"
        )

    if "_next_process_entry_section" in st.session_state:
        next_section = st.session_state.pop("_next_process_entry_section")
        if next_section in section_options:
            st.session_state["process_entry_section"] = next_section

    if st.session_state.get("process_entry_section") not in section_options:
        st.session_state["process_entry_section"] = "① 生产任务卡"

    section = st.radio(
        "选择操作区",
        section_options,
        horizontal=True,
        key="process_entry_section"
    )

    # =========================
    # 6. ① 生产任务卡
    # =========================
    if section == "① 生产任务卡":
        if st.session_state.pop("process_entry_just_updated", False):
            st.success("工序已提交，生产任务卡已实时更新。")

        st.subheader("生产任务卡")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("生产批号", str(selected["batch_code"]))
        c2.metric("客户", str(selected["customer_name"]))
        c3.metric("PO", str(selected["po_no"]))
        c4.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
        c6.metric("应生产数量", f"{float(selected['required_production_qty'] or 0):.0f}")
        c7.metric("当前实际数量", f"{float(selected['actual_qty'] or 0):.0f}")
        c8.metric("交付状态", str(selected["delivery_status"]))

        c9, c10, c11, c12 = st.columns(4)
        c9.metric("生产状态", str(selected["production_flow_status"]))
        c10.metric("最近完成工序", latest_done_step)
        c11.metric("最近产出数量", f"{latest_done_output:.0f}")
        c12.metric("建议下一工序", f"{suggested_process_step} / {PROCESS_CN.get(suggested_process_step, '')}")

        st.caption(
            f"产品：{selected['product_type_text']} ｜ "
            f"规格：{selected['product_spec_text']} ｜ "
            f"特殊工艺：{selected['special_process']} ｜ "
            f"材质：{selected['material']} ｜ "
            f"计划交付日期：{selected['planned_delivery_date']}"
        )

        st.markdown("Trace Key")
        st.code(str(selected["trace_key"]))

        st.markdown("---")
        st.subheader("生产进度")

        st.progress(progress_ratio)

        flow_cols = st.columns(len(PROCESS_FLOW))
        for i, step in enumerate(PROCESS_FLOW):
            step_done = step in completed_steps
            if step_done:
                flow_cols[i].success(f"{PROCESS_CN.get(step, step)}\n已完成")
            elif step == suggested_process_step and not all_standard_done:
                flow_cols[i].info(f"{PROCESS_CN.get(step, step)}\n当前建议")
            else:
                flow_cols[i].caption(f"{PROCESS_CN.get(step, step)}\n待处理")

        if all_standard_done:
            st.success("该生产批次的标准工序已全部完成。请勿重复录入工序。")

        st.markdown("---")

        q1, q2, q3, q4 = st.columns(4)
        q1.metric("累计投入记录", f"{total_input_qty:.0f}")
        q2.metric("累计产出记录", f"{total_output_qty:.0f}")
        q3.metric("累计报废记录", f"{total_scrap_qty:.0f}")
        q4.metric("已完成工序数", f"{completed_count} / {len(PROCESS_FLOW)}")

        st.markdown("---")

        b1, b2 = st.columns(2)

        with b1:
            if all_standard_done:
                st.button(
                    "标准工序已完成，不能继续录入",
                    key=f"go_process_form_disabled_{batch_id}",
                    disabled=True
                )
            else:
                if st.button("进入工序录入", key=f"go_process_form_{batch_id}"):
                    st.session_state["_next_process_entry_section"] = "② 录入本次工序"
                    st.rerun()

        with b2:
            if st.button("查看工序记录", key=f"go_process_log_{batch_id}"):
                st.session_state["_next_process_entry_section"] = "③ 工序记录"
                st.rerun()

        st.markdown("---")

        if current_log_df.empty:
            st.info("当前批次还没有工序记录。")
        else:
            st.subheader("最近工序记录")
            latest_df = current_log_df.sort_values(
                "process_log_id",
                ascending=False
            ).head(5)
            show_df(latest_df, hide_index=True)

    # =========================
    # 7. ② 录入本次工序
    # =========================
    elif section == "② 录入本次工序":
        st.subheader("录入本次工序")

        st.info(
            "系统会自动带入本工序投入数量，并自动计算报废数量。"
            "如需特殊调整，可以手动调整投入数量；但产出数量不能大于投入数量。"
            "已完成的工序不会出现在正常录入选项中。"
        )

        # =========================
        # 只显示未完成的标准工序
        # =========================
        available_process_steps = [
            step for step in PROCESS_FLOW
            if step not in completed_steps
        ]

        if not available_process_steps:
            st.success("当前标准工序已经全部完成，不能继续重复录入。")
            st.info("如需查看或核对，请进入【③ 工序记录】。")
            if st.button("查看工序记录", key=f"go_record_after_all_done_{batch_id}"):
                st.session_state["_next_process_entry_section"] = "③ 工序记录"
                st.rerun()
            return

        if suggested_process_step in available_process_steps:
            default_process_index = available_process_steps.index(suggested_process_step)
        else:
            default_process_index = 0

        process_step = st.selectbox(
            "工序",
            available_process_steps,
            index=default_process_index,
            format_func=lambda x: f"{x} / {PROCESS_CN.get(x, x)}",
            key=f"process_step_select_{batch_id}_{completed_count}"
        )

        selected_process_index = PROCESS_FLOW.index(process_step)

        # =========================
        # 根据选择工序自动计算默认投入数量
        # =========================
        if selected_process_index == 0:
            default_input_qty = float(selected["required_production_qty"] or 0)
            input_source_text = (
                f"当前为第一道工序 {process_step}，"
                f"默认投入数量 = 应生产数量 {default_input_qty:.0f}"
            )
        else:
            previous_step = PROCESS_FLOW[selected_process_index - 1]

            previous_done_df = done_log_df[
                done_log_df["process_step"].astype(str) == previous_step
            ].copy()

            if not previous_done_df.empty:
                previous_done = previous_done_df.sort_values(
                    "process_log_id"
                ).iloc[-1]

                default_input_qty = float(previous_done["output_qty"] or 0)
                input_source_text = (
                    f"当前工序 {process_step} 自动继承上一道工序 "
                    f"{previous_step} 的产出数量：{default_input_qty:.0f}"
                )

            elif not done_log_df.empty:
                latest_done_for_input = done_log_df.sort_values("process_log_id").iloc[-1]
                default_input_qty = float(latest_done_for_input["output_qty"] or 0)
                input_source_text = (
                    f"未找到上一道标准工序 {previous_step} 的完成记录，"
                    f"暂时继承最近完成工序 {latest_done_for_input['process_step']} 的产出数量："
                    f"{default_input_qty:.0f}"
                )

            else:
                default_input_qty = float(selected["required_production_qty"] or 0)
                input_source_text = (
                    f"当前尚无已完成工序，默认投入数量 = 应生产数量 "
                    f"{default_input_qty:.0f}"
                )

        st.success(input_source_text)

        f1, f2 = st.columns(2)

        with f1:
            equipment_code = st.text_input(
                "设备编号",
                value=f"EQ-{process_step.upper()}-001",
                key=f"equipment_code_{batch_id}_{process_step}"
            )

            operator_name = st.text_input(
                "操作员",
                value="Operator A",
                key=f"operator_name_{batch_id}_{process_step}"
            )

            input_qty = st.number_input(
                "投入数量（系统自动带入，可调整）",
                min_value=0.0,
                value=float(default_input_qty),
                step=1.0,
                key=f"input_qty_auto_{batch_id}_{process_step}_{default_input_qty}"
            )

            output_qty = st.number_input(
                "产出数量",
                min_value=0.0,
                value=float(default_input_qty),
                step=1.0,
                key=f"output_qty_auto_{batch_id}_{process_step}_{default_input_qty}"
            )

        with f2:
            process_status = st.selectbox(
                "工序状态",
                ["done", "running", "hold"],
                index=0,
                key=f"process_status_{batch_id}_{process_step}"
            )

            start_time = st.text_input(
                "开始时间",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                key=f"start_time_{batch_id}_{process_step}"
            )

            end_time = st.text_input(
                "结束时间",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                key=f"end_time_{batch_id}_{process_step}"
            )

            remark = st.text_area(
                "备注",
                value="",
                key=f"remark_{batch_id}_{process_step}"
            )

        calculated_scrap_qty = max(float(input_qty) - float(output_qty), 0.0)

        st.markdown("---")
        st.subheader("数量自动计算结果")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("本工序投入数量", f"{float(input_qty):.0f}")
        r2.metric("本工序产出数量", f"{float(output_qty):.0f}")
        r3.metric("自动计算报废数量", f"{float(calculated_scrap_qty):.0f}")
        r4.metric(
            "良率",
            f"{(float(output_qty) / float(input_qty) * 100):.2f}%"
            if float(input_qty) > 0 else "0.00%"
        )

        warning_messages = []

        if float(input_qty) <= 0:
            warning_messages.append("投入数量为 0，请确认是否正确。")

        if float(output_qty) > float(input_qty):
            warning_messages.append("产出数量不能大于投入数量。")

        if process_status == "done" and float(output_qty) <= 0:
            warning_messages.append("工序状态为 done 时，建议产出数量大于 0。")

        if process_step != PROCESS_FLOW[0] and float(input_qty) == 0:
            warning_messages.append("后续工序投入数量为 0，请检查上一道工序是否已完成。")

        # 再次提示是否理论上跳工序
        if selected_process_index > 0:
            previous_step = PROCESS_FLOW[selected_process_index - 1]
            if previous_step not in completed_steps:
                warning_messages.append(
                    f"上一道标准工序 {previous_step} 尚未完成，当前属于跳工序录入，请确认。"
                )

        if warning_messages:
            for msg in warning_messages:
                st.warning(msg)
        else:
            st.success("检查通过，可以提交。")

        final_check = st.checkbox(
            "我确认本次工序的投入、产出和自动计算报废数量无误。",
            key=f"process_submit_check_{batch_id}_{process_step}"
        )

        submitted = st.button(
            "提交本次工序并返回生产任务卡",
            key=f"submit_process_log_{batch_id}_{process_step}"
        )

        if submitted:
            scrap_qty = max(float(input_qty) - float(output_qty), 0.0)

            if not final_check:
                st.error("请先勾选确认。")
                return

            if float(output_qty) > float(input_qty):
                st.error("提交失败：产出数量不能大于投入数量。")
                return

            if process_status == "done" and float(input_qty) <= 0:
                st.error("提交失败：工序完成时投入数量不能为 0。")
                return

            # =========================
            # 防重复提交 done
            # =========================
            duplicate_done_df = pd.read_sql_query("""
                SELECT
                    process_log_id,
                    process_step,
                    process_status,
                    input_qty,
                    output_qty,
                    scrap_qty,
                    start_time,
                    end_time,
                    remark
                FROM production_process_log
                WHERE production_batch_id = ?
                  AND process_step = ?
                  AND lower(COALESCE(process_status, '')) = 'done'
                ORDER BY process_log_id DESC
            """, conn, params=[
                int(batch_id),
                process_step
            ])

            if process_status == "done" and not duplicate_done_df.empty:
                st.error(
                    f"提交失败：当前批次的工序【{process_step}】已经存在完成记录，不能重复提交 done。"
                )
                st.warning("请到【③ 工序记录】查看已有记录。如确实需要返工，建议后续单独增加返工功能，而不是重复覆盖标准工序。")
                show_df(duplicate_done_df, hide_index=True)
                return

            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO production_process_log (
                        production_batch_id,
                        process_step,
                        equipment_code,
                        operator_name,
                        input_qty,
                        output_qty,
                        scrap_qty,
                        process_status,
                        start_time,
                        end_time,
                        remark
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(batch_id),
                    process_step,
                    equipment_code,
                    operator_name,
                    float(input_qty),
                    float(output_qty),
                    float(scrap_qty),
                    process_status,
                    start_time,
                    end_time,
                    remark
                ))

                if process_status in ("running", "done"):
                    new_flow_status = process_step
                elif process_status == "hold":
                    new_flow_status = "hold"
                else:
                    new_flow_status = str(selected["production_flow_status"])

                cursor.execute("""
                    UPDATE production_batch
                    SET production_flow_status = ?,
                        actual_qty = ?
                    WHERE production_batch_id = ?
                """, (
                    new_flow_status,
                    float(output_qty),
                    int(batch_id)
                ))

                if pd.notna(selected["delivery_plan_id"]):
                    cursor.execute("""
                        UPDATE delivery_plan
                        SET delivery_status = '生产中'
                        WHERE delivery_plan_id = ?
                          AND COALESCE(delivery_status, '') NOT IN (
                              '质检中',
                              '待入库确认',
                              '已入库',
                              '已出货',
                              '部分出货'
                          )
                    """, (
                        int(selected["delivery_plan_id"]),
                    ))

                conn.commit()

                # 如果最后一道 Packing 完成，则自动生成质检记录并进入质检中
                if process_step == "Packing" and process_status == "done":
                    if "auto_create_qc_after_production_done" in globals():
                        auto_create_qc_after_production_done(conn, int(batch_id))
                    else:
                        qc_exists_df = pd.read_sql_query("""
                            SELECT COUNT(*) AS cnt
                            FROM production_measurement
                            WHERE production_batch_id = ?
                        """, conn, params=[int(batch_id)])

                        qc_exists = int(qc_exists_df.iloc[0]["cnt"] or 0)
                        cur2 = conn.cursor()

                        if qc_exists == 0:
                            cur2.execute("""
                                INSERT INTO production_measurement (
                                    production_batch_id,
                                    quality_status,
                                    release_status,
                                    inspected_at,
                                    release_by
                                ) VALUES (?, 'Pending', 'pending', datetime('now'), 'Auto QC')
                            """, (
                                int(batch_id),
                            ))

                        if pd.notna(selected["delivery_plan_id"]):
                            cur2.execute("""
                                UPDATE delivery_plan
                                SET delivery_status = '质检中'
                                WHERE delivery_plan_id = ?
                            """, (
                                int(selected["delivery_plan_id"]),
                            ))

                        conn.commit()

                st.session_state["selected_process_batch_id"] = int(batch_id)
                st.session_state["process_entry_just_updated"] = True
                st.session_state["_next_process_entry_section"] = "① 生产任务卡"

                st.success(
                    f"工序 {process_step} 已提交。"
                    f"投入 {float(input_qty):.0f}，"
                    f"产出 {float(output_qty):.0f}，"
                    f"报废 {float(scrap_qty):.0f}。"
                )

                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error("提交失败，数据库已回滚。")
                st.exception(e)

    # =========================
    # 8. ③ 工序记录
    # =========================
    elif section == "③ 工序记录":
        st.subheader("当前批次工序记录")

        if current_log_df.empty:
            st.info("当前批次还没有生产过程记录。")
        else:
            latest_df = current_log_df.sort_values(
                "process_log_id",
                ascending=False
            )
            show_df(latest_df, hide_index=True)

            st.markdown("---")
            st.subheader("工序数量流转汇总")

            flow_rows = []
            for step in PROCESS_FLOW:
                step_df = current_log_df[
                    current_log_df["process_step"].astype(str) == step
                ].copy()

                if step_df.empty:
                    flow_rows.append({
                        "process_step": step,
                        "process_name": PROCESS_CN.get(step, step),
                        "latest_status": "未录入",
                        "input_qty": 0,
                        "output_qty": 0,
                        "scrap_qty": 0,
                        "yield_rate": ""
                    })
                else:
                    latest_step = step_df.sort_values("process_log_id").iloc[-1]
                    input_v = float(latest_step["input_qty"] or 0)
                    output_v = float(latest_step["output_qty"] or 0)
                    scrap_v = float(latest_step["scrap_qty"] or 0)
                    yield_rate = output_v / input_v * 100 if input_v > 0 else 0

                    flow_rows.append({
                        "process_step": step,
                        "process_name": PROCESS_CN.get(step, step),
                        "latest_status": latest_step["process_status"],
                        "input_qty": input_v,
                        "output_qty": output_v,
                        "scrap_qty": scrap_v,
                        "yield_rate": f"{yield_rate:.2f}%"
                    })

            flow_df = pd.DataFrame(flow_rows)
            show_df(flow_df, hide_index=True)

        st.markdown("---")
        st.subheader("所有生产过程日志")

        all_log_df = pd.read_sql_query("""
            SELECT
                ppl.process_log_id,
                ppl.production_batch_id,
                pb.batch_code,
                ppl.process_step,
                ppl.equipment_code,
                ppl.operator_name,
                ppl.input_qty,
                ppl.output_qty,
                ppl.scrap_qty,
                ppl.process_status,
                ppl.start_time,
                ppl.end_time,
                ppl.remark
            FROM production_process_log ppl
            LEFT JOIN production_batch pb
                ON ppl.production_batch_id = pb.production_batch_id
            ORDER BY ppl.process_log_id DESC
        """, conn)

        if all_log_df.empty:
            st.info("当前没有任何生产过程日志。")
        else:
            show_df(all_log_df, hide_index=True)

# =========================
# 覆盖版：库存总览 + 规格化库存调整
# =========================

def adjust_spec_inventory_lot(conn, inventory_lot_id, adjust_type, adjust_qty, adjust_reason, adjust_note):
    """
    规格化库存调整：
    - 只允许调整 WH-SPEC 的规格化库存
    - 减少库存时必须填写原因
    - 所有调整写入 inventory_transaction_log
    - 非出货减少不更新 shipment / shipment_item
    """
    cursor = conn.cursor()

    lot_df = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            location,
            available_qty,
            reserved_qty,
            lot_status,
            release_status,
            trace_key
        FROM inventory_lot
        WHERE inventory_lot_id = ?
    """, conn, params=[int(inventory_lot_id)])

    if lot_df.empty:
        return False, "未找到该库存 Lot。"

    lot = lot_df.iloc[0]

    location = str(lot["location"] or "")
    trace_key = str(lot["trace_key"] or "")
    available_qty = float(lot["available_qty"] or 0)

    is_spec_stock = (
        location == "WH-SPEC"
        or trace_key.startswith("SPEC_STOCK")
    )

    if not is_spec_stock:
        return False, "该 Lot 不是规格化库存。只有 WH-SPEC / SPEC_STOCK 库存允许在这里调整。"

    adjust_qty = float(adjust_qty)

    if adjust_qty <= 0:
        return False, "调整数量必须大于 0。"

    adjust_reason = normalize_text(adjust_reason)
    adjust_note = normalize_text(adjust_note)

    if adjust_type == "减少库存" and not adjust_reason:
        return False, "减少规格化库存时，必须填写减少原因。"

    if adjust_type == "减少库存" and adjust_qty > available_qty:
        return False, f"减少数量不能大于当前可用库存。当前可用库存为 {available_qty:.0f}。"

    reference_no = f"SPEC-ADJ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if adjust_type == "增加库存":
        new_available_qty = available_qty + adjust_qty
        txn_type = "spec_adjust_in"
        txn_reason = f"规格化库存增加：{adjust_reason or 'manual_adjust_in'}"
        signed_qty = adjust_qty

    else:
        new_available_qty = available_qty - adjust_qty
        txn_type = "spec_adjust_out"
        txn_reason = f"规格化库存非出货减少：{adjust_reason}"
        signed_qty = adjust_qty

    if adjust_note:
        txn_reason = f"{txn_reason}；说明：{adjust_note}"

    cursor.execute("""
        UPDATE inventory_lot
        SET available_qty = ?,
            last_out_qty = CASE
                WHEN ? = 'spec_adjust_out' THEN ?
                ELSE last_out_qty
            END,
            last_out_time = CASE
                WHEN ? = 'spec_adjust_out' THEN datetime('now')
                ELSE last_out_time
            END
        WHERE inventory_lot_id = ?
    """, (
        new_available_qty,
        txn_type,
        adjust_qty,
        txn_type,
        int(inventory_lot_id)
    ))

    cursor.execute("""
        INSERT INTO inventory_transaction_log (
            inventory_lot_id,
            txn_type,
            qty,
            txn_time,
            txn_reason,
            reference_no
        ) VALUES (?, ?, ?, datetime('now'), ?, ?)
    """, (
        int(inventory_lot_id),
        txn_type,
        signed_qty,
        txn_reason,
        reference_no
    ))

    conn.commit()

    return True, (
        f"规格化库存调整成功。Lot {lot['lot_code']}："
        f"{available_qty:.0f} → {new_available_qty:.0f}。"
        f"流水号：{reference_no}"
    )



# =========================
# 覆盖版：是否需要生产判断 + 销售看板
# 逻辑：
# 1. 规格库存满足交付批次 → 发货准备
# 2. 规格库存不足交付批次 → 待生产确认 → 排产 → 生产中
# =========================

# =========================
# 销售看板：成品优先匹配 + 半成品 / 生产人工选择
# =========================

def build_spec_stock_trace_key(product_spec_text, special_process, material):
    """
    规格化库存 Trace Key：
    SPEC_STOCK + 规格 + 特殊工艺 + 材质
    """
    return "__".join([
        "SPEC_STOCK",
        normalize_trace_part(product_spec_text, "NOSPEC"),
        normalize_trace_part(special_process, "STANDARD"),
        normalize_trace_part(material, "UNKNOWN_MATERIAL"),
    ])


def get_delivery_plan_sales_decision(conn, delivery_plan_id):
    """
    销售看板库存判断：

    优先级：
    1. 成品订单库存 WH-ORDER / 当前订单 trace_key
    2. 成品规格库存 WH-SPEC / SPEC_STOCK trace_key
    3. 半成品库存 production_batch.semi_finished_wh_qty
    4. 人工选择是否生产 / 是否半成品出库

    返回：
    - qty_needed
    - order_finished_qty
    - spec_finished_qty
    - total_finished_qty
    - semi_finished_qty
    - auto_decision
    """

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            oi.po_no,
            oi.spec_id,
            oi.product_id,
            oi.product_spec_text,
            oi.product_type_text,
            oi.trace_key,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,

            c.customer_name
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN customer c
            ON o.customer_id = c.customer_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if plan_df.empty:
        return {
            "ok": False,
            "message": "未找到该交付批次。"
        }

    plan = plan_df.iloc[0]

    planned_qty = float(plan["planned_delivery_qty"] or 0)
    actual_delivery_qty = float(plan["actual_delivery_qty"] or 0)
    qty_needed = max(planned_qty - actual_delivery_qty, 0)

    order_trace_key = str(plan["trace_key"])
    spec_stock_trace_key = build_spec_stock_trace_key(
        product_spec_text=plan["product_spec_text"],
        special_process=plan["special_process"],
        material=plan["material"]
    )

    if qty_needed <= 0:
        return {
            "ok": True,
            "plan": plan,
            "qty_needed": 0,
            "order_finished_qty": 0,
            "spec_finished_qty": 0,
            "total_finished_qty": 0,
            "semi_finished_qty": 0,
            "auto_decision": "已满足",
            "spec_stock_trace_key": spec_stock_trace_key
        }

    # =========================
    # 1. 成品订单库存 WH-ORDER
    # =========================
    order_finished_df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(COALESCE(available_qty, 0)), 0) AS qty
        FROM inventory_lot
        WHERE trace_key = ?
          AND location = 'WH-ORDER'
          AND lower(COALESCE(release_status, 'pending')) = 'released'
          AND COALESCE(lot_status, 'available') = 'available'
    """, conn, params=[order_trace_key])

    order_finished_qty = float(order_finished_df.iloc[0]["qty"] or 0)

    # =========================
    # 2. 成品规格化库存 WH-SPEC
    # =========================
    spec_finished_df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(COALESCE(available_qty, 0)), 0) AS qty
        FROM inventory_lot
        WHERE (
                trace_key = ?
                OR trace_key = ?
              )
          AND location = 'WH-SPEC'
          AND lower(COALESCE(release_status, 'pending')) = 'released'
          AND COALESCE(lot_status, 'available') = 'available'
    """, conn, params=[
        spec_stock_trace_key,
        order_trace_key
    ])

    spec_finished_qty = float(spec_finished_df.iloc[0]["qty"] or 0)

    total_finished_qty = order_finished_qty + spec_finished_qty

    # =========================
    # 3. 半成品库存
    # 只统计同 trace_key、尚未正式成品入库的半成品
    # =========================
    semi_finished_df = pd.read_sql_query("""
        SELECT
            COALESCE(SUM(COALESCE(pb.semi_finished_wh_qty, 0)), 0) AS qty
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        WHERE pb.trace_key = ?
          AND COALESCE(pb.semi_finished_wh_qty, 0) > 0
          AND COALESCE(dp.delivery_status, '') NOT IN (
                '已入库',
                '已出货',
                '部分出货'
          )
    """, conn, params=[order_trace_key])

    semi_finished_qty = float(semi_finished_df.iloc[0]["qty"] or 0)

    if total_finished_qty >= qty_needed:
        auto_decision = "发货准备"
    else:
        auto_decision = "人工选择"

    return {
        "ok": True,
        "plan": plan,
        "qty_needed": qty_needed,
        "order_finished_qty": order_finished_qty,
        "spec_finished_qty": spec_finished_qty,
        "total_finished_qty": total_finished_qty,
        "semi_finished_qty": semi_finished_qty,
        "auto_decision": auto_decision,
        "spec_stock_trace_key": spec_stock_trace_key
    }

def update_delivery_plan_by_sales_decision(
    conn,
    delivery_plan_id,
    action_choice="自动判断",
    note="",
    need_production=None,
    need_semi_out=None
):
    """
    销售看板推送逻辑。

    成品库存充足：
    - delivery_status = 发货准备
    - sales_need_production = 0
    - sales_need_semi_out = 0

    成品库存不足：
    - 可以只安排生产
    - 可以只半成品出库
    - 可以生产 + 半成品同时进行
    """

    ensure_sales_decision_schema(conn)

    result = get_delivery_plan_sales_decision(conn, delivery_plan_id)

    if not result.get("ok"):
        return False, result.get("message", "判断失败。")

    plan = result["plan"]
    qty_needed = float(result["qty_needed"] or 0)
    total_finished_qty = float(result["total_finished_qty"] or 0)
    semi_finished_qty = float(result["semi_finished_qty"] or 0)

    current_status = str(plan["delivery_status"] or "未排产")
    note = normalize_text(note)

    locked_statuses = [
        "生产中",
        "质检中",
        "待入库确认",
        "已入库",
        "部分出货",
        "已出货"
    ]

    if current_status in locked_statuses:
        return True, f"该交付批次已进入后续流程，当前状态保持为【{current_status}】。"

    cursor = conn.cursor()

    if qty_needed <= 0:
        return True, "该交付批次已无待满足数量，无需处理。"

    # =========================
    # 成品库存充足：直接进入出货
    # =========================
    if total_finished_qty >= qty_needed:
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = '发货准备',
                sales_need_production = 0,
                sales_need_semi_out = 0,
                sales_decision_note = ?,
                sales_decision_time = datetime('now')
            WHERE delivery_plan_id = ?
        """, (
            note or "成品库存充足，销售推送至出货管理",
            int(delivery_plan_id)
        ))

        conn.commit()
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

        return True, (
            f"成品库存充足，已将交付批次 {delivery_plan_id} 更新为【发货准备】。"
            f"需发数量 {qty_needed:.0f}，成品可用 {total_finished_qty:.0f}。"
            "请进入【出货管理】确认发货。"
        )

    # =========================
    # 成品库存不足：人工组合选择
    # =========================
    if need_production is None or need_semi_out is None:
        if action_choice == "安排生产":
            need_production = True
            need_semi_out = False
        elif action_choice == "半成品出库":
            need_production = False
            need_semi_out = True
        elif action_choice == "生产+半成品":
            need_production = True
            need_semi_out = True
        elif action_choice == "暂不处理":
            need_production = False
            need_semi_out = False
        else:
            return False, "请选择处理方式。"

    need_production = bool(need_production)
    need_semi_out = bool(need_semi_out)

    if not need_production and not need_semi_out:
        cursor.execute("""
            UPDATE delivery_plan
            SET sales_need_production = 0,
                sales_need_semi_out = 0,
                sales_decision_note = ?,
                sales_decision_time = datetime('now')
            WHERE delivery_plan_id = ?
        """, (
            note or "销售暂不处理",
            int(delivery_plan_id)
        ))

        conn.commit()
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

        return True, (
            f"已暂不处理该交付批次。"
            f"需发数量 {qty_needed:.0f}，成品可用 {total_finished_qty:.0f}，"
            f"半成品可用 {semi_finished_qty:.0f}。"
        )

    if need_semi_out and semi_finished_qty <= 0:
        return False, "当前没有可用半成品，不能选择半成品出库。"

    if need_production and need_semi_out:
        new_status = "待生产确认"
        decision_text = "销售选择：生产 + 半成品出库"
    elif need_production:
        new_status = "待生产确认"
        decision_text = "销售选择：安排生产"
    else:
        new_status = "半成品出库准备"
        decision_text = "销售选择：半成品出库"

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = ?,
            sales_need_production = ?,
            sales_need_semi_out = ?,
            sales_decision_note = ?,
            sales_decision_time = datetime('now')
        WHERE delivery_plan_id = ?
    """, (
        new_status,
        1 if need_production else 0,
        1 if need_semi_out else 0,
        note or decision_text,
        int(delivery_plan_id)
    ))

    conn.commit()
    sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    sync_msg_parts = []

    if need_production:
        sync_msg_parts.append("已同步至【排产看板 → 销售推送待确认】")

    if need_semi_out:
        sync_msg_parts.append("已同步至【半成品仓库看板】")

    return True, (
        f"{decision_text}。"
        f"需发数量 {qty_needed:.0f}，成品可用 {total_finished_qty:.0f}，"
        f"半成品可用 {semi_finished_qty:.0f}。"
        + "；".join(sync_msg_parts)
    )

def push_delivery_plan_to_production(conn, delivery_plan_id):
    """
    保留旧函数名，避免其他地方调用时报错。
    新逻辑改为销售库存判断。
    """
    return update_delivery_plan_by_sales_decision(
        conn=conn,
        delivery_plan_id=delivery_plan_id,
        action_choice="自动判断"
    )

def page_sales_dashboard(conn):
    st.header("销售｜销售看板")

    st.info(
        "销售看板规则：订单优先匹配成品库存。"
        "若成品库存充足，直接进入【发货准备】；"
        "若成品库存不足，由销售端人工勾选【需要安排生产】和 / 或【需要半成品出库】。"
    )

    # =========================
    # 1. 交付批次总览
    # =========================
    dashboard_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.planned_delivery_qty, 0) - COALESCE(dp.actual_delivery_qty, 0) AS remaining_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            COALESCE(dp.sales_need_production, 0) AS sales_need_production,
            COALESCE(dp.sales_need_semi_out, 0) AS sales_need_semi_out,
            dp.sales_decision_note,
            dp.sales_decision_time,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
            oi.trace_key,

            COALESCE((
                SELECT SUM(COALESCE(il1.available_qty, 0))
                FROM inventory_lot il1
                WHERE il1.trace_key = oi.trace_key
                  AND il1.location = 'WH-ORDER'
                  AND lower(COALESCE(il1.release_status, 'pending')) = 'released'
                  AND COALESCE(il1.lot_status, 'available') = 'available'
            ), 0) AS order_finished_qty,

            COALESCE((
                SELECT SUM(COALESCE(il2.available_qty, 0))
                FROM inventory_lot il2
                WHERE il2.location = 'WH-SPEC'
                  AND lower(COALESCE(il2.release_status, 'pending')) = 'released'
                  AND COALESCE(il2.lot_status, 'available') = 'available'
                  AND (
                        il2.trace_key = oi.trace_key
                        OR il2.trace_key = (
                            'SPEC_STOCK' || '__' ||
                            UPPER(REPLACE(REPLACE(COALESCE(oi.product_spec_text, 'NOSPEC'), '__', '-'), ' ', '-')) || '__' ||
                            UPPER(REPLACE(REPLACE(COALESCE(oi.special_process, 'STANDARD'), '__', '-'), ' ', '-')) || '__' ||
                            UPPER(REPLACE(REPLACE(COALESCE(oi.material, 'UNKNOWN_MATERIAL'), '__', '-'), ' ', '-'))
                        )
                  )
            ), 0) AS spec_finished_qty,

            COALESCE((
                SELECT SUM(COALESCE(pb2.semi_finished_wh_qty, 0))
                FROM production_batch pb2
                LEFT JOIN production_schedule ps2
                    ON pb2.production_batch_id = ps2.production_batch_id
                LEFT JOIN delivery_plan dp2
                    ON ps2.delivery_plan_id = dp2.delivery_plan_id
                WHERE pb2.trace_key = oi.trace_key
                  AND COALESCE(pb2.semi_finished_wh_qty, 0) > 0
                  AND COALESCE(dp2.delivery_status, '') NOT IN (
                        '已入库',
                        '已出货',
                        '部分出货'
                  )
            ), 0) AS semi_finished_qty

        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN customer c
            ON o.customer_id = c.customer_id
        ORDER BY
            CASE COALESCE(dp.delivery_status, '未排产')
                WHEN '未排产' THEN 1
                WHEN '发货准备' THEN 2
                WHEN '待生产确认' THEN 3
                WHEN '半成品出库准备' THEN 4
                WHEN '已排产' THEN 5
                WHEN '生产中' THEN 6
                WHEN '质检中' THEN 7
                WHEN '待入库确认' THEN 8
                WHEN '已入库' THEN 9
                WHEN '部分出货' THEN 10
                WHEN '已出货' THEN 11
                ELSE 99
            END,
            dp.planned_delivery_date,
            dp.delivery_plan_id
    """, conn)

    if dashboard_df.empty:
        st.info("当前没有交付批次数据。")
        return

    dashboard_df["total_finished_qty"] = (
        pd.to_numeric(dashboard_df["order_finished_qty"], errors="coerce").fillna(0)
        + pd.to_numeric(dashboard_df["spec_finished_qty"], errors="coerce").fillna(0)
    )

    dashboard_df["finished_shortage_qty"] = (
        pd.to_numeric(dashboard_df["remaining_qty"], errors="coerce").fillna(0)
        - pd.to_numeric(dashboard_df["total_finished_qty"], errors="coerce").fillna(0)
    ).clip(lower=0)

    # =========================
    # 2. 顶部指标
    # =========================
    total_wait_qty = pd.to_numeric(
        dashboard_df["remaining_qty"],
        errors="coerce"
    ).fillna(0).sum()

    ready_count = len(dashboard_df[dashboard_df["delivery_status"] == "发货准备"])
    production_wait_count = len(
        dashboard_df[
            (dashboard_df["delivery_status"] == "待生产确认")
            | (dashboard_df["sales_need_production"] == 1)
        ]
    )
    semi_wait_count = len(
        dashboard_df[
            (dashboard_df["delivery_status"] == "半成品出库准备")
            | (dashboard_df["sales_need_semi_out"] == 1)
        ]
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("待满足数量", f"{float(total_wait_qty):.0f}")
    m2.metric("发货准备批次", ready_count)
    m3.metric("待生产确认 / 生产需求", production_wait_count)
    m4.metric("半成品出库需求", semi_wait_count)

    st.markdown("---")

    st.subheader("交付批次总览")

    show_df(dashboard_df.rename(columns={
        "delivery_plan_id": "交付计划编号",
        "order_item_id": "订单明细编号",
        "delivery_batch_no": "交付批次",
        "planned_delivery_date": "计划交付日期",
        "planned_delivery_qty": "计划交付数量",
        "actual_delivery_qty": "实际交付数量",
        "remaining_qty": "剩余待满足数量",
        "delivery_status": "交付状态",
        "sales_need_production": "销售要求生产",
        "sales_need_semi_out": "销售要求半成品出库",
        "sales_decision_note": "销售处理说明",
        "sales_decision_time": "销售处理时间",
        "customer_name": "客户",
        "po_no": "PO",
        "customer_pn": "客户料号",
        "product_type_text": "产品",
        "product_spec_text": "规格",
        "special_process": "特殊工艺",
        "material": "材质",
        "order_finished_qty": "订单成品库存",
        "spec_finished_qty": "规格成品库存",
        "total_finished_qty": "成品库存合计",
        "finished_shortage_qty": "成品缺口",
        "semi_finished_qty": "半成品数量",
        "trace_key": "Trace Key"
    }), hide_index=True)

    st.markdown("---")

    # =========================
    # 3. 选择交付批次处理
    # =========================
    selectable_df = dashboard_df[
        dashboard_df["delivery_status"].isin([
            "未排产",
            "发货准备",
            "待生产确认",
            "半成品出库准备"
        ])
    ].copy()

    if selectable_df.empty:
        st.info("当前没有需要销售处理的交付批次。")
        return

    selected_delivery_plan_id = st.selectbox(
        "选择交付批次进行处理",
        selectable_df["delivery_plan_id"].tolist(),
        format_func=lambda x: (
            f"【{selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'delivery_status'].iloc[0]}】 "
            f"交付计划 {x} | "
            f"PO {selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
            f"第 {int(selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
            f"剩余 {float(selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'remaining_qty'].iloc[0] or 0):.0f} | "
            f"成品 {float(selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'total_finished_qty'].iloc[0] or 0):.0f} | "
            f"半成品 {float(selectable_df.loc[selectable_df['delivery_plan_id'] == x, 'semi_finished_qty'].iloc[0] or 0):.0f}"
        ),
        key="sales_dashboard_delivery_plan_select"
    )

    selected = selectable_df[
        selectable_df["delivery_plan_id"] == selected_delivery_plan_id
    ].iloc[0]

    decision = get_delivery_plan_sales_decision(
        conn,
        int(selected_delivery_plan_id)
    )

    if not decision.get("ok"):
        st.error(decision.get("message", "库存判断失败。"))
        return

    qty_needed = float(decision["qty_needed"] or 0)
    order_finished_qty = float(decision["order_finished_qty"] or 0)
    spec_finished_qty = float(decision["spec_finished_qty"] or 0)
    total_finished_qty = float(decision["total_finished_qty"] or 0)
    semi_finished_qty = float(decision["semi_finished_qty"] or 0)
    shortage_qty = max(qty_needed - total_finished_qty, 0)

    st.subheader("销售处理卡片")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户", str(selected["customer_name"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
    c4.metric("当前状态", str(selected["delivery_status"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
    c6.metric("已交付数量", f"{float(selected['actual_delivery_qty'] or 0):.0f}")
    c7.metric("剩余待满足", f"{qty_needed:.0f}")
    c8.metric("成品缺口", f"{shortage_qty:.0f}")

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("订单成品库存 WH-ORDER", f"{order_finished_qty:.0f}")
    c10.metric("规格成品库存 WH-SPEC", f"{spec_finished_qty:.0f}")
    c11.metric("成品库存合计", f"{total_finished_qty:.0f}")
    c12.metric("半成品数量", f"{semi_finished_qty:.0f}")

    c13, c14 = st.columns(2)
    c13.metric("销售要求生产", "是" if int(selected.get("sales_need_production", 0) or 0) == 1 else "否")
    c14.metric("销售要求半成品出库", "是" if int(selected.get("sales_need_semi_out", 0) or 0) == 1 else "否")

    if pd.notna(selected.get("sales_decision_note", None)) and str(selected.get("sales_decision_note", "")).strip():
        st.caption(f"销售处理说明：{selected['sales_decision_note']}")

    st.caption(
        f"产品：{selected['product_type_text']} ｜ "
        f"规格：{selected['product_spec_text']} ｜ "
        f"特殊工艺：{selected['special_process']} ｜ "
        f"材质：{selected['material']} ｜ "
        f"计划交付日期：{selected['planned_delivery_date']}"
    )

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    st.markdown("---")

    # =========================
    # 4. 决策逻辑
    # =========================
    if qty_needed <= 0:
        st.success("该交付批次已满足，无需继续处理。")
        return

    # =========================
    # 成品库存充足：直接进入出货管理
    # =========================
    if total_finished_qty >= qty_needed:
        st.success(
            f"成品库存充足：需发 {qty_needed:.0f}，成品可用 {total_finished_qty:.0f}。"
            "点击下方按钮后将进入【发货准备】，并同步至【出货管理】。"
        )

        if st.button("成品库存充足，推送至出货管理", key=f"sales_ready_ship_{selected_delivery_plan_id}"):
            ok, msg = update_delivery_plan_by_sales_decision(
                conn=conn,
                delivery_plan_id=int(selected_delivery_plan_id),
                action_choice="自动判断",
                note="成品库存充足，销售推送至出货管理"
            )

            if ok:
                st.success(msg)
                st.session_state["_jump_to_page"] = "出货管理"
                st.rerun()
            else:
                st.error(msg)

    # =========================
    # 成品库存不足：人工组合选择
    # =========================
    else:
        st.warning(
            f"成品库存不足：需发 {qty_needed:.0f}，成品可用 {total_finished_qty:.0f}，"
            f"缺口 {shortage_qty:.0f}。请销售端选择后续处理方式。"
        )

        with st.form(f"sales_manual_decision_form_{selected_delivery_plan_id}"):

            st.markdown("### 人工处理选择")

            default_need_semi = semi_finished_qty > 0
            default_need_production = (
                semi_finished_qty <= 0
                or semi_finished_qty < shortage_qty
            )

            need_production = st.checkbox(
                "需要安排生产",
                value=default_need_production,
                key=f"sales_need_production_{selected_delivery_plan_id}"
            )

            need_semi_out = st.checkbox(
                "需要半成品出库",
                value=default_need_semi,
                key=f"sales_need_semi_out_{selected_delivery_plan_id}"
            )

            st.markdown("### 当前可用资源")

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("剩余待满足", f"{qty_needed:.0f}")
            r2.metric("成品库存合计", f"{total_finished_qty:.0f}")
            r3.metric("半成品数量", f"{semi_finished_qty:.0f}")
            r4.metric("成品缺口", f"{shortage_qty:.0f}")

            if semi_finished_qty > 0 and semi_finished_qty < shortage_qty:
                st.warning(
                    f"当前半成品数量 {semi_finished_qty:.0f} 小于成品缺口 {shortage_qty:.0f}。"
                    "建议同时勾选【需要安排生产】和【需要半成品出库】。"
                )

            if semi_finished_qty >= shortage_qty and shortage_qty > 0:
                st.info(
                    f"当前半成品数量 {semi_finished_qty:.0f} 可以覆盖成品缺口 {shortage_qty:.0f}。"
                    "可以只选择半成品出库，也可以同时安排生产作为后续补货。"
                )

            if semi_finished_qty <= 0:
                st.info("当前没有可用半成品，如成品库存不足，建议选择安排生产。")

            decision_note = st.text_area(
                "处理说明",
                placeholder="例如：成品不足，现有半成品先出库，同时安排生产补足剩余缺口。",
                key=f"sales_decision_note_{selected_delivery_plan_id}"
            )

            final_check = st.checkbox(
                "我已确认库存情况和后续处理方式。",
                key=f"sales_decision_final_check_{selected_delivery_plan_id}"
            )

            submitted = st.form_submit_button("确认并同步处理消息")

        if submitted:
            if not final_check:
                st.error("请先勾选确认。")
                return

            if not need_production and not need_semi_out:
                st.error("请至少选择一种处理方式：需要安排生产 或 需要半成品出库。")
                return

            if need_semi_out and semi_finished_qty <= 0:
                st.error("当前没有可用半成品，不能选择半成品出库。")
                return

            if need_semi_out and semi_finished_qty < shortage_qty and not need_production:
                st.warning(
                    "半成品数量不足以覆盖全部缺口。"
                    "如果仍只选择半成品出库，后续可能仍无法满足完整交付。"
                )

            ok, msg = update_delivery_plan_by_sales_decision(
                conn=conn,
                delivery_plan_id=int(selected_delivery_plan_id),
                note=decision_note,
                need_production=need_production,
                need_semi_out=need_semi_out
            )

            if ok:
                st.success(msg)

                if need_production and need_semi_out:
                    st.info("已同时同步到【排产看板】和【半成品仓库看板】。")
                    st.session_state["_jump_to_page"] = "排产看板"

                elif need_production:
                    st.session_state["_jump_to_page"] = "排产看板"

                elif need_semi_out:
                    st.session_state["_jump_to_page"] = "半成品仓库看板"

                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")

    # =========================
    # 5. 当前订单追踪明细
    # =========================
    with st.expander("查看当前订单全流程追踪", expanded=False):
        render_current_order_trace_detail(
            conn,
            int(selected["order_item_id"])
        )



# =========================
# 覆盖版：生产完成 → 自动质检 → 放行后自动入库
# =========================

def auto_create_qc_after_production_done(conn, production_batch_id):
    """
    生产完成后进入半成品仓库并等待质检。

    触发时机：
    - 生产过程录入中 Packing done 后调用

    执行动作：
    1. production_batch.semi_finished_wh_qty = actual_qty
    2. production_batch.production_flow_status = 'done'
    3. 自动创建 / 更新 production_measurement
    4. production_measurement.qc_before_qty = actual_qty
    5. delivery_plan.delivery_status = '质检中'
    6. 写入半成品仓库流水
    7. 调用 sync_after_delivery_plan_change() 统一同步
    """

    ensure_semi_finished_warehouse_schema(conn)

    cursor = conn.cursor()

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,
            ps.delivery_plan_id
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        WHERE pb.production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if batch_df.empty:
        return False, "未找到生产批次。"

    row = batch_df.iloc[0]

    actual_qty = float(row["actual_qty"] or 0)
    old_semi_qty = float(row["semi_finished_wh_qty"] or 0)
    batch_code = str(row["batch_code"])
    delivery_plan_id = row["delivery_plan_id"]

    if actual_qty <= 0:
        return False, "实际生产数量为 0，不能进入半成品仓库。"

    # =========================
    # 1. 生产完成，进入半成品仓库
    # =========================
    cursor.execute("""
        UPDATE production_batch
        SET semi_finished_wh_qty = ?,
            production_flow_status = 'done'
        WHERE production_batch_id = ?
    """, (
        float(actual_qty),
        int(production_batch_id)
    ))

    # =========================
    # 2. 创建 / 更新质检记录
    # =========================
    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    exists_count = int(exists_df.iloc[0]["cnt"] or 0)

    if exists_count == 0:
        cursor.execute("""
            INSERT INTO production_measurement (
                production_batch_id,
                quality_status,
                release_status,
                inspected_at,
                release_by,
                qc_before_qty,
                qc_after_qty,
                qc_loss_qty,
                qc_note
            ) VALUES (?, 'Pending', 'pending', datetime('now'), 'Auto QC', ?, 0, 0, '生产完成后自动进入半成品待检')
        """, (
            int(production_batch_id),
            float(actual_qty)
        ))
    else:
        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = CASE
                    WHEN COALESCE(quality_status, '') = '' THEN 'Pending'
                    ELSE quality_status
                END,
                release_status = CASE
                    WHEN COALESCE(release_status, '') = '' THEN 'pending'
                    ELSE release_status
                END,
                qc_before_qty = CASE
                    WHEN COALESCE(qc_before_qty, 0) = 0 THEN ?
                    ELSE qc_before_qty
                END,
                inspected_at = datetime('now')
            WHERE production_batch_id = ?
        """, (
            float(actual_qty),
            int(production_batch_id)
        ))

    # =========================
    # 3. 交付批次进入质检中
    # =========================
    if pd.notna(delivery_plan_id):
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = '质检中'
            WHERE delivery_plan_id = ?
              AND COALESCE(delivery_status, '') NOT IN (
                    '已入库',
                    '已出货',
                    '部分出货'
              )
        """, (
            int(delivery_plan_id),
        ))

    conn.commit()

    # =========================
    # 4. 写入半成品仓库流水
    # =========================
    if "record_semi_finished_txn" in globals():
        record_semi_finished_txn(
            conn=conn,
            production_batch_id=int(production_batch_id),
            batch_code=batch_code,
            txn_type="production_done_in",
            qty_before=float(old_semi_qty),
            qty_after=float(actual_qty),
            txn_reason="生产完成进入半成品仓库",
            operator_name="System",
            reference_no=batch_code
        )

    # =========================
    # 5. 统一同步交付批次 / 订单状态
    # =========================
    if pd.notna(delivery_plan_id):
        if "sync_after_delivery_plan_change" in globals():
            sync_after_delivery_plan_change(
                conn,
                int(delivery_plan_id)
            )

    return True, "生产完成，已进入半成品仓库并等待质检。"



def auto_inbound_after_quality_release(conn, production_batch_id):
    """
    质量放行后自动入库：
    - release_status = released 时生成 inventory_lot
    - 入库 location 优先为 WH-ORDER
    - 写入 inventory_transaction_log
    - delivery_plan 状态同步为 已入库
    """
    cursor = conn.cursor()

    info_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            pb.required_production_qty,
            COALESCE(pb.special_process, 'STANDARD') AS special_process,
            COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,

            ps.delivery_plan_id,
            ps.order_item_id,

            oi.product_id,
            oi.spec_id,
            oi.product_spec_text,
            oi.po_no,
            oi.trace_key AS order_trace_key,

            pm.quality_status,
            pm.release_status
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        WHERE pb.production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if info_df.empty:
        return False, "未找到生产批次。"

    row = info_df.iloc[0]

    release_status = str(row["release_status"] or "").lower()
    if release_status != "released":
        return False, "当前批次尚未放行，不能自动入库。"

    actual_qty = float(row["actual_qty"] or 0)
    if actual_qty <= 0:
        return False, "实际生产数量为 0，不能自动入库。"

    product_id = int(row["product_id"]) if pd.notna(row["product_id"]) else None
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None

    if product_id is None:
        return False, "缺少 product_id，不能自动入库。"

    exists_lot_df = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            available_qty
        FROM inventory_lot
        WHERE production_batch_id = ?
        ORDER BY inventory_lot_id
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    if exists_lot_df.empty:
        lot_code = f"LOT-AUTO-{int(production_batch_id):04d}"
        trace_key = str(row["order_trace_key"] or row["trace_key"])

        cursor.execute("""
            INSERT INTO inventory_lot (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                trace_key,
                location,
                available_qty,
                reserved_qty,
                lot_status,
                release_status,
                exclusive_customer,
                forbidden_customer
            ) VALUES (?, ?, ?, ?, ?, 'WH-ORDER', ?, 0, 'available', 'released', '', '')
        """, (
            int(production_batch_id),
            product_id,
            spec_id,
            lot_code,
            trace_key,
            actual_qty
        ))

        inventory_lot_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id,
                txn_type,
                qty,
                txn_time,
                txn_reason,
                reference_no
            ) VALUES (?, 'inbound', ?, datetime('now'), 'quality_release_auto_inbound', ?)
        """, (
            int(inventory_lot_id),
            actual_qty,
            str(row["batch_code"])
        ))

    else:
        inventory_lot_id = int(exists_lot_df.iloc[0]["inventory_lot_id"])

        cursor.execute("""
            UPDATE inventory_lot
            SET available_qty = ?,
                lot_status = 'available',
                release_status = 'released',
                location = 'WH-ORDER'
            WHERE inventory_lot_id = ?
        """, (
            actual_qty,
            inventory_lot_id
        ))

    if pd.notna(row["delivery_plan_id"]):
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = '已入库'
            WHERE delivery_plan_id = ?
        """, (
            int(row["delivery_plan_id"]),
        ))

    conn.commit()
    return True, "质量放行后已自动入库，库存数据已更新。"

# =========================
# 新增：出货追踪中心
# =========================

def page_outbound_tracking_center(conn):
    st.header("出货追踪中心")

    st.info(
        "这里用于出货前后的完整信息确认："
        "出货看板、批次追踪、检测录入、质量放行会集中显示，方便出货前准备。"
    )

    tab_ship, tab_batch, tab_qc_entry, tab_release = st.tabs([
        "出货看板",
        "批次追踪",
        "检测录入",
        "质量放行"
    ])

    with tab_ship:
        st.subheader("出货看板")

        ship_ready_df = pd.read_sql_query("""
            SELECT
                dp.delivery_plan_id,
                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                dp.planned_delivery_date,
                dp.planned_delivery_qty,
                COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                c.customer_name,
                oi.order_item_id,
                oi.po_no,
                oi.customer_pn,
                oi.product_type_text,
                oi.product_spec_text,
                COALESCE(oi.special_process, 'STANDARD') AS special_process,
                COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
                oi.trace_key,

                ps.production_batch_id,
                pb.batch_code,
                pb.actual_qty,
                pm.quality_status,
                pm.release_status,

                COALESCE(SUM(il.available_qty), 0) AS available_inventory_qty,
                COUNT(DISTINCT il.inventory_lot_id) AS lot_count
            FROM delivery_plan dp
            JOIN order_item oi
                ON dp.order_item_id = oi.order_item_id
            JOIN orders o
                ON oi.order_id = o.order_id
            JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_schedule ps
                ON dp.delivery_plan_id = ps.delivery_plan_id
            LEFT JOIN production_batch pb
                ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN production_measurement pm
                ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il
                ON (
                    il.trace_key = oi.trace_key
                    OR il.production_batch_id = pb.production_batch_id
                )
               AND lower(COALESCE(il.release_status, 'pending')) = 'released'
               AND lower(COALESCE(il.lot_status, 'hold')) IN ('available', 'reserved')
            WHERE COALESCE(dp.delivery_status, '未排产') IN ('发货准备', '已入库')
            GROUP BY
                dp.delivery_plan_id,
                dp.delivery_batch_no,
                dp.planned_delivery_date,
                dp.planned_delivery_qty,
                dp.actual_delivery_qty,
                dp.delivery_status,
                c.customer_name,
                oi.order_item_id,
                oi.po_no,
                oi.customer_pn,
                oi.product_type_text,
                oi.product_spec_text,
                oi.special_process,
                oi.material,
                oi.trace_key,
                ps.production_batch_id,
                pb.batch_code,
                pb.actual_qty,
                pm.quality_status,
                pm.release_status
            ORDER BY dp.planned_delivery_date, dp.delivery_plan_id
        """, conn)

        if ship_ready_df.empty:
            st.info("当前没有处于发货准备 / 已入库状态的交付批次。")
        else:
            show_df(ship_ready_df.rename(columns={
                "delivery_plan_id": "交付计划编号",
                "delivery_batch_no": "交付批次",
                "planned_delivery_date": "计划交付日期",
                "planned_delivery_qty": "计划交付数量",
                "actual_delivery_qty": "实际交付数量",
                "delivery_status": "交付状态",
                "customer_name": "客户",
                "po_no": "PO",
                "customer_pn": "客户料号",
                "product_type_text": "产品",
                "product_spec_text": "规格",
                "special_process": "特殊工艺",
                "material": "材质",
                "batch_code": "生产批号",
                "quality_status": "质量等级",
                "release_status": "放行状态",
                "available_inventory_qty": "可用库存",
                "lot_count": "Lot数量"
            }), hide_index=True)

            selected_delivery_plan_id = st.selectbox(
                "选择交付批次准备出货",
                ship_ready_df["delivery_plan_id"].tolist(),
                format_func=lambda x: (
                    f"交付计划 {x} | "
                    f"PO {ship_ready_df.loc[ship_ready_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
                    f"第 {int(ship_ready_df.loc[ship_ready_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批"
                ),
                key="outbound_tracking_select_delivery"
            )

            selected = ship_ready_df[
                ship_ready_df["delivery_plan_id"] == selected_delivery_plan_id
            ].iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("客户", str(selected["customer_name"]))
            c2.metric("PO", str(selected["po_no"]))
            c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
            c4.metric("可用库存", f"{float(selected['available_inventory_qty'] or 0):.0f}")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("计划数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
            c6.metric("交付状态", str(selected["delivery_status"]))
            c7.metric("质量等级", str(selected["quality_status"]))
            c8.metric("放行状态", str(selected["release_status"]))

            st.markdown("Trace Key")
            st.code(str(selected["trace_key"]))

            if st.button("进入出货管理", key=f"go_shipment_from_outbound_center_{selected_delivery_plan_id}"):
                st.session_state["_jump_to_page"] = "出货管理"
                st.rerun()

    with tab_batch:
        page_batch_tracking(conn)

    with tab_qc_entry:
        page_measurement_entry(conn)

    with tab_release:
        page_quality_release(conn)

# =========================
# 覆盖版：完整同步函数 + 出货管理
# 目标：
# 1. 出货后同步订单状态
# 2. 出货后同步交付批次状态
# 3. 支持订单库存 WH-ORDER + 规格化库存 WH-SPEC 混合出货
# =========================

def build_spec_stock_trace_key(product_spec_text, special_process, material):
    """
    规格化库存 Trace Key:
    SPEC_STOCK + 规格 + 特殊工艺 + 材质
    """
    return "__".join([
        "SPEC_STOCK",
        normalize_trace_part(product_spec_text, "NOSPEC"),
        normalize_trace_part(special_process, "STANDARD"),
        normalize_trace_part(material, "UNKNOWN_MATERIAL"),
    ])

# =========================
# 全流程实时同步核心函数
# =========================

def ensure_sales_decision_schema(conn):
    """
    确保 delivery_plan 有销售决策同步字段。
    """
    cursor = conn.cursor()

    cols = pd.read_sql_query(
        "PRAGMA table_info(delivery_plan)",
        conn
    )["name"].tolist()

    if "sales_need_production" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_need_production INTEGER DEFAULT 0
        """)

    if "sales_need_semi_out" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_need_semi_out INTEGER DEFAULT 0
        """)

    if "sales_decision_note" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_decision_note TEXT
        """)

    if "sales_decision_time" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_decision_time TEXT
        """)

    conn.commit()


def sync_delivery_plan_status(conn, delivery_plan_id):
    """
    统一同步交付批次状态。

    状态优先级：
    1. 已出货 / 部分出货
    2. 发货准备
    3. 已入库
    4. 待入库确认
    5. 质检中
    6. 生产中
    7. 已排产
    8. 待生产确认
    9. 半成品出库准备
    10. 未排产

    注意：
    - sales_need_production 和 sales_need_semi_out 是并行指令，不完全依赖 delivery_status。
    - 如果销售同时选择“生产 + 半成品”，delivery_status 可以是【待生产确认】，
      但半成品仓库仍通过 sales_need_semi_out = 1 看到任务。
    """

    ensure_sales_decision_schema(conn)

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS current_status,
            COALESCE(dp.sales_need_production, 0) AS sales_need_production,
            COALESCE(dp.sales_need_semi_out, 0) AS sales_need_semi_out,

            oi.ordered_qty,
            oi.shipped_qty
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if plan_df.empty:
        return False, "未找到交付批次。"

    plan = plan_df.iloc[0]

    order_item_id = int(plan["order_item_id"])
    planned_qty = float(plan["planned_delivery_qty"] or 0)
    actual_delivery_qty = float(plan["actual_delivery_qty"] or 0)
    current_status = str(plan["current_status"] or "未排产")
    sales_need_production = int(plan["sales_need_production"] or 0)
    sales_need_semi_out = int(plan["sales_need_semi_out"] or 0)

    related_df = pd.read_sql_query("""
        SELECT
            ps.production_schedule_id,
            ps.production_batch_id,

            pb.batch_code,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,

            pm.measurement_id,
            COALESCE(pm.release_status, 'pending') AS release_status,
            COALESCE(pm.quality_status, 'Pending') AS quality_status,

            il.inventory_lot_id,
            COALESCE(il.available_qty, 0) AS available_qty,
            il.release_status AS lot_release_status,

            ppl.process_log_id,
            ppl.process_step,
            ppl.process_status
        FROM production_schedule ps
        LEFT JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        LEFT JOIN production_process_log ppl
            ON pb.production_batch_id = ppl.production_batch_id
        WHERE ps.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    has_schedule = not related_df.empty
    has_process = False
    has_qc = False
    has_released = False
    has_inventory = False
    semi_qty = 0.0
    finished_qty = 0.0
    prod_status = "planned"

    if has_schedule:
        has_process = related_df["process_log_id"].notna().any()
        has_qc = related_df["measurement_id"].notna().any()

        release_statuses = related_df["release_status"].astype(str).str.lower().tolist()
        has_released = "released" in release_statuses

        inv_df = related_df[
            related_df["inventory_lot_id"].notna()
            & (pd.to_numeric(related_df["available_qty"], errors="coerce").fillna(0) > 0)
        ]
        has_inventory = not inv_df.empty

        semi_qty = pd.to_numeric(
            related_df["semi_finished_wh_qty"],
            errors="coerce"
        ).fillna(0).max()

        finished_qty = pd.to_numeric(
            related_df["finished_wh_qty"],
            errors="coerce"
        ).fillna(0).max()

        prod_status_series = related_df["production_flow_status"].dropna().astype(str)
        if not prod_status_series.empty:
            prod_status = prod_status_series.iloc[0]

    # =========================
    # 1. 出货状态最高优先级
    # =========================
    if planned_qty > 0 and actual_delivery_qty >= planned_qty:
        new_status = "已出货"
        clear_sales_flags = True

    elif actual_delivery_qty > 0:
        new_status = "部分出货"
        clear_sales_flags = False

    # =========================
    # 2. 销售推送到出货管理
    # =========================
    elif current_status == "发货准备":
        new_status = "发货准备"
        clear_sales_flags = False

    # =========================
    # 3. 已正式入库
    # =========================
    elif has_inventory or finished_qty > 0 or current_status == "已入库":
        new_status = "已入库"
        clear_sales_flags = False

    # =========================
    # 4. 质检已放行，等待仓储入库
    # =========================
    elif has_released or current_status == "待入库确认":
        new_status = "待入库确认"
        clear_sales_flags = False

    # =========================
    # 5. 进入质检 / 半成品待检
    # =========================
    elif has_qc or current_status == "质检中":
        new_status = "质检中"
        clear_sales_flags = False

    # =========================
    # 6. 生产过程
    # =========================
    elif has_process or prod_status not in ["planned", "", "None", None]:
        new_status = "生产中"
        clear_sales_flags = False

    # =========================
    # 7. 已排产
    # =========================
    elif has_schedule:
        new_status = "已排产"
        clear_sales_flags = False

    # =========================
    # 8. 销售要求生产
    # =========================
    elif sales_need_production == 1:
        new_status = "待生产确认"
        clear_sales_flags = False

    # =========================
    # 9. 只要求半成品出库
    # =========================
    elif sales_need_semi_out == 1:
        new_status = "半成品出库准备"
        clear_sales_flags = False

    else:
        new_status = "未排产"
        clear_sales_flags = False

    cursor = conn.cursor()

    if clear_sales_flags:
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = ?,
                sales_need_production = 0,
                sales_need_semi_out = 0,
                sales_decision_note = COALESCE(sales_decision_note, '') || '；出货完成，销售指令关闭',
                sales_decision_time = datetime('now')
            WHERE delivery_plan_id = ?
        """, (
            new_status,
            int(delivery_plan_id)
        ))
    else:
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = ?
            WHERE delivery_plan_id = ?
        """, (
            new_status,
            int(delivery_plan_id)
        ))

    conn.commit()

    sync_order_status_after_shipment(conn, order_item_id)

    return True, f"交付批次 {delivery_plan_id} 已同步为【{new_status}】。"


def sync_order_status_after_shipment(conn, order_item_id):
    """
    同步订单明细和订单主表状态。

    item_status:
    - completed：已全部出货
    - partial_shipped：部分出货
    - open：未出货 / 进行中

    order_status:
    - completed：所有明细 completed
    - partial_shipped：任一明细有出货
    - confirmed：未出货
    """

    cursor = conn.cursor()

    item_df = pd.read_sql_query("""
        SELECT
            oi.order_item_id,
            oi.order_id,
            COALESCE(oi.ordered_qty, 0) AS ordered_qty,
            COALESCE(oi.shipped_qty, 0) AS shipped_qty
        FROM order_item oi
        WHERE oi.order_item_id = ?
    """, conn, params=[int(order_item_id)])

    if item_df.empty:
        return False, "未找到订单明细。"

    item = item_df.iloc[0]
    order_id = int(item["order_id"])
    ordered_qty = float(item["ordered_qty"] or 0)
    shipped_qty = float(item["shipped_qty"] or 0)

    if ordered_qty > 0 and shipped_qty >= ordered_qty:
        item_status = "completed"
    elif shipped_qty > 0:
        item_status = "partial_shipped"
    else:
        item_status = "open"

    cursor.execute("""
        UPDATE order_item
        SET item_status = ?,
            fulfilled_qty = CASE
                WHEN ? > COALESCE(fulfilled_qty, 0) THEN ?
                ELSE COALESCE(fulfilled_qty, 0)
            END
        WHERE order_item_id = ?
    """, (
        item_status,
        float(shipped_qty),
        float(shipped_qty),
        int(order_item_id)
    ))

    order_items_df = pd.read_sql_query("""
        SELECT
            COALESCE(ordered_qty, 0) AS ordered_qty,
            COALESCE(shipped_qty, 0) AS shipped_qty
        FROM order_item
        WHERE order_id = ?
    """, conn, params=[order_id])

    if order_items_df.empty:
        conn.commit()
        return True, "订单明细状态已同步。"

    total_ordered = pd.to_numeric(
        order_items_df["ordered_qty"],
        errors="coerce"
    ).fillna(0).sum()

    total_shipped = pd.to_numeric(
        order_items_df["shipped_qty"],
        errors="coerce"
    ).fillna(0).sum()

    if total_ordered > 0 and total_shipped >= total_ordered:
        order_status = "completed"
    elif total_shipped > 0:
        order_status = "partial_shipped"
    else:
        order_status = "confirmed"

    cursor.execute("""
        UPDATE orders
        SET order_status = ?
        WHERE order_id = ?
    """, (
        order_status,
        order_id
    ))

    conn.commit()

    return True, f"订单明细 {order_item_id} / 订单 {order_id} 状态已同步。"


def sync_all_delivery_plans_for_order_item(conn, order_item_id):
    """
    同步某个订单明细下的所有交付批次状态。
    """
    dp_df = pd.read_sql_query("""
        SELECT delivery_plan_id
        FROM delivery_plan
        WHERE order_item_id = ?
        ORDER BY delivery_plan_id
    """, conn, params=[int(order_item_id)])

    for _, row in dp_df.iterrows():
        sync_delivery_plan_status(conn, int(row["delivery_plan_id"]))

    sync_order_status_after_shipment(conn, int(order_item_id))


def sync_after_delivery_plan_change(conn, delivery_plan_id):
    """
    任意页面只要改了 delivery_plan / production / inventory / shipment，
    最后统一调用这个函数。
    """
    dp_df = pd.read_sql_query("""
        SELECT order_item_id
        FROM delivery_plan
        WHERE delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if dp_df.empty:
        return False, "未找到交付批次，无法同步。"

    order_item_id = int(dp_df.iloc[0]["order_item_id"])

    sync_delivery_plan_status(conn, int(delivery_plan_id))
    sync_all_delivery_plans_for_order_item(conn, int(order_item_id))
    sync_order_status_after_shipment(conn, int(order_item_id))

    return True, "交付批次、订单明细、订单主表已同步。"

def get_lots_for_delivery_plan_shipment(conn, delivery_plan_id):
    """
    获取某个交付批次可用于出货的 Lot。

    优先级：
    1. 订单库存 WH-ORDER，trace_key = 订单 trace_key
    2. 规格化库存 WH-SPEC，spec_id + SPEC_STOCK trace_key
    3. 兼容旧规格库存：location = WH-SPEC，spec_id 相同
    """
    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            oi.trace_key AS order_trace_key,
            oi.product_id,
            oi.spec_id,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if plan_df.empty:
        return pd.DataFrame(), None

    plan = plan_df.iloc[0]

    spec_stock_trace_key = build_spec_stock_trace_key(
        product_spec_text=plan["product_spec_text"],
        special_process=plan["special_process"],
        material=plan["material"]
    )

    lot_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.lot_code,
            il.production_batch_id,
            il.product_id,
            il.spec_id,
            il.trace_key,
            il.location,
            COALESCE(il.available_qty, 0) AS available_qty,
            COALESCE(il.reserved_qty, 0) AS reserved_qty,
            il.lot_status,
            il.release_status,
            CASE
                WHEN il.location = 'WH-ORDER'
                 AND il.trace_key = ?
                THEN 1

                WHEN il.location = 'WH-SPEC'
                 AND il.trace_key = ?
                THEN 2

                WHEN il.location = 'WH-SPEC'
                 AND (
                    il.trace_key IS NULL
                    OR il.trace_key = ''
                    OR il.trace_key NOT LIKE 'SPEC_STOCK__%'
                 )
                THEN 3

                ELSE 99
            END AS alloc_priority
        FROM inventory_lot il
        WHERE il.spec_id = ?
          AND COALESCE(il.available_qty, 0) > 0
          AND lower(COALESCE(il.release_status, 'pending')) = 'released'
          AND lower(COALESCE(il.lot_status, 'hold')) IN ('available', 'reserved')
          AND (
                (il.location = 'WH-ORDER' AND il.trace_key = ?)
                OR
                (il.location = 'WH-SPEC' AND il.trace_key = ?)
                OR
                (
                    il.location = 'WH-SPEC'
                    AND (
                        il.trace_key IS NULL
                        OR il.trace_key = ''
                        OR il.trace_key NOT LIKE 'SPEC_STOCK__%'
                    )
                )
          )
        ORDER BY alloc_priority, il.inventory_lot_id
    """, conn, params=[
        str(plan["order_trace_key"]),
        spec_stock_trace_key,
        int(plan["spec_id"]),
        str(plan["order_trace_key"]),
        spec_stock_trace_key
    ])

    return lot_df, plan


def run_delivery_plan_shipment(conn, delivery_plan_id, ship_qty,
                               carrier="SF Express",
                               destination="Customer Warehouse",
                               created_by="Shipment User"):
    """
    按交付批次正式出货。

    支持：
    - 订单库存 WH-ORDER
    - 规格化库存 WH-SPEC
    - 多 Lot 自动拆分扣减
    - 出货后自动同步订单、交付批次、库存流水
    """
    cursor = conn.cursor()

    ship_qty = float(ship_qty)

    if ship_qty <= 0:
        return False, "出货数量必须大于 0。"

    plan_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            oi.order_id,
            oi.trace_key AS order_trace_key,
            oi.product_id,
            oi.spec_id,
            oi.po_no,
            COALESCE(oi.ordered_qty, 0) AS ordered_qty,
            COALESCE(oi.shipped_qty, 0) AS shipped_qty,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,

            o.customer_id,
            c.customer_name
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN customer c
            ON o.customer_id = c.customer_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if plan_df.empty:
        return False, "未找到交付批次。"

    plan = plan_df.iloc[0]

    planned_qty = float(plan["planned_delivery_qty"] or 0)
    actual_delivery_qty = float(plan["actual_delivery_qty"] or 0)
    remaining_delivery_qty = max(planned_qty - actual_delivery_qty, 0)

    if remaining_delivery_qty <= 0:
        return False, "该交付批次已经完成出货，无需重复出货。"

    if ship_qty > remaining_delivery_qty:
        return False, f"出货数量不能超过该交付批次剩余数量。剩余数量：{remaining_delivery_qty:.0f}。"

    lot_df, _ = get_lots_for_delivery_plan_shipment(conn, int(delivery_plan_id))

    if lot_df.empty:
        return False, "没有可用库存。请检查订单库存 WH-ORDER 或规格化库存 WH-SPEC。"

    total_available = pd.to_numeric(
        lot_df["available_qty"],
        errors="coerce"
    ).fillna(0).sum()

    if total_available < ship_qty:
        return False, f"可用库存不足。需要 {ship_qty:.0f}，当前可用 {total_available:.0f}。"

    shipment_no = f"SHIP-DP{int(delivery_plan_id):04d}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute("""
        INSERT INTO shipment (
            shipment_no,
            customer_id,
            ship_date,
            carrier,
            destination,
            created_by,
            shipment_status,
            notes
        ) VALUES (?,?, date('now'), ?, ?, ?, 'created', ?)
    """, (
        shipment_no,
        int(plan["customer_id"]),
        carrier,
        destination,
        created_by,
        f"Auto shipment for delivery_plan_id={int(delivery_plan_id)}"
    ))

    shipment_id = cursor.lastrowid

    qty_to_allocate = ship_qty
    allocated_rows = []

    for _, lot in lot_df.iterrows():
        if qty_to_allocate <= 0:
            break

        lot_id = int(lot["inventory_lot_id"])
        available_qty = float(lot["available_qty"] or 0)

        if available_qty <= 0:
            continue

        take_qty = min(available_qty, qty_to_allocate)

        packaging_code = f"PKG-{shipment_no}-LOT{lot_id}"

        cursor.execute("""
            INSERT INTO shipment_item (
                shipment_id,
                order_item_id,
                inventory_lot_id,
                shipped_qty,
                packaging_label_code,
                trace_key
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(shipment_id),
            int(plan["order_item_id"]),
            int(lot_id),
            float(take_qty),
            packaging_code,
            str(plan["order_trace_key"])
        ))

        cursor.execute("""
            UPDATE inventory_lot
            SET available_qty = COALESCE(available_qty, 0) - ?,
                last_out_qty = ?,
                last_out_time = datetime('now')
            WHERE inventory_lot_id = ?
        """, (
            float(take_qty),
            float(take_qty),
            int(lot_id)
        ))

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id,
                txn_type,
                qty,
                txn_time,
                txn_reason,
                reference_no
            ) VALUES (?, 'outbound', ?, datetime('now'), ?, ?)
        """, (
            int(lot_id),
            float(take_qty),
            f"shipment_delivery_plan_{int(delivery_plan_id)}",
            shipment_no
        ))

        allocated_rows.append({
            "lot_code": lot["lot_code"],
            "location": lot["location"],
            "qty": take_qty
        })

        qty_to_allocate -= take_qty

    cursor.execute("""
        UPDATE order_item
        SET shipped_qty = COALESCE(shipped_qty, 0) + ?
        WHERE order_item_id = ?
    """, (
        float(ship_qty),
        int(plan["order_item_id"])
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET actual_delivery_qty = COALESCE(actual_delivery_qty, 0) + ?,
            actual_delivery_date = date('now')
        WHERE delivery_plan_id = ?
    """, (
        float(ship_qty),
        int(delivery_plan_id)
    ))

    conn.commit()

    # 统一同步交付批次、订单明细、订单主表，并在全部出货后关闭销售指令
    sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    used_text = "；".join([
        f"{x['lot_code']}({x['location']}): {x['qty']:.0f}"
        for x in allocated_rows
    ])

    return True, (
        f"出货完成：{shipment_no}。"
        f"出货数量 {ship_qty:.0f}。"
        f"使用库存：{used_text}"
    )

def page_shipment(conn):
    st.header("出货追踪｜出货管理")

    st.info(
        "出货规则：优先使用订单库存 WH-ORDER；不足时可使用规格化库存 WH-SPEC。"
        "正式出货前必须完成发货确认。出货后会自动同步：库存、库存流水、交付批次状态、订单明细状态、订单主表状态。"
    )

    # =========================
    # 1. 待出货交付批次
    # =========================
    dp_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            dp.planned_delivery_date,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.planned_delivery_qty, 0) - COALESCE(dp.actual_delivery_qty, 0) AS remaining_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            COALESCE(oi.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
            oi.trace_key,

            ps.production_batch_id,
            pb.batch_code,
            pb.production_flow_status,
            pm.quality_status,
            pm.release_status
        FROM delivery_plan dp
        JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN customer c
            ON o.customer_id = c.customer_id
        LEFT JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        WHERE COALESCE(dp.planned_delivery_qty, 0) > COALESCE(dp.actual_delivery_qty, 0)
          AND COALESCE(dp.delivery_status, '未排产') IN (
                '发货准备',
                '已入库',
                '部分出货'
          )
        ORDER BY dp.planned_delivery_date, dp.delivery_plan_id
    """, conn)

    if dp_df.empty:
        st.info("当前没有可出货的交付批次。")
    else:
        st.subheader("可出货交付批次")

        show_df(dp_df.rename(columns={
            "delivery_plan_id": "交付计划编号",
            "order_item_id": "订单明细编号",
            "delivery_batch_no": "交付批次",
            "planned_delivery_date": "计划交付日期",
            "planned_delivery_qty": "计划交付数量",
            "actual_delivery_qty": "已出货数量",
            "remaining_delivery_qty": "剩余待出货",
            "delivery_status": "交付状态",
            "customer_name": "客户",
            "po_no": "PO",
            "customer_pn": "客户料号",
            "product_type_text": "产品",
            "product_spec_text": "规格",
            "special_process": "特殊工艺",
            "material": "材质",
            "batch_code": "生产批号",
            "quality_status": "质量等级",
            "release_status": "放行状态"
        }), hide_index=True)

        st.markdown("---")

        # =========================
        # 2. 选择交付批次
        # =========================
        selected_delivery_plan_id = st.selectbox(
            "选择要出货的交付批次",
            dp_df["delivery_plan_id"].tolist(),
            format_func=lambda x: (
                f"交付计划 {x} | "
                f"PO {dp_df.loc[dp_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
                f"第 {int(dp_df.loc[dp_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
                f"剩余 {float(dp_df.loc[dp_df['delivery_plan_id'] == x, 'remaining_delivery_qty'].iloc[0]):.0f}"
            ),
            key="shipment_delivery_plan_select"
        )

        selected = dp_df[
            dp_df["delivery_plan_id"] == selected_delivery_plan_id
        ].iloc[0]

        lot_df, _ = get_lots_for_delivery_plan_shipment(
            conn,
            int(selected_delivery_plan_id)
        )

        available_qty = 0.0
        if not lot_df.empty:
            available_qty = pd.to_numeric(
                lot_df["available_qty"],
                errors="coerce"
            ).fillna(0).sum()

        remaining_qty = float(selected["remaining_delivery_qty"] or 0)

        # =========================
        # 3. 出货信息确认卡
        # =========================
        st.subheader("出货信息确认")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("客户", str(selected["customer_name"]))
        c2.metric("PO", str(selected["po_no"]))
        c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
        c4.metric("交付状态", str(selected["delivery_status"]))

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("计划数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
        c6.metric("已出货", f"{float(selected['actual_delivery_qty'] or 0):.0f}")
        c7.metric("剩余待出货", f"{remaining_qty:.0f}")
        c8.metric("可用库存", f"{available_qty:.0f}")

        st.caption(
            f"产品：{selected['product_type_text']} ｜ "
            f"规格：{selected['product_spec_text']} ｜ "
            f"特殊工艺：{selected['special_process']} ｜ "
            f"材质：{selected['material']} ｜ "
            f"生产批号：{selected['batch_code'] if pd.notna(selected['batch_code']) else '-'}"
        )

        st.markdown("Trace Key")
        st.code(str(selected["trace_key"]))

        # =========================
        # 4. 出货前检查
        # =========================
        st.markdown("---")
        st.subheader("出货前检查")

        check_pass = True

        if remaining_qty <= 0:
            st.error("该交付批次已无剩余待出货数量。")
            check_pass = False

        if available_qty <= 0:
            st.error("当前没有可用库存，不能出货。")
            check_pass = False

        if available_qty < remaining_qty:
            st.warning(
                f"当前可用库存 {available_qty:.0f} 小于剩余待出货数量 {remaining_qty:.0f}，"
                "只能部分出货或先补充库存。"
            )
        else:
            st.success("库存数量满足当前交付批次的剩余出货需求。")

        if str(selected["delivery_status"]) not in ["发货准备", "已入库", "部分出货"]:
            st.error("当前交付状态不允许出货。")
            check_pass = False

        # =========================
        # 5. 可用 Lot 分配顺序
        # =========================
        st.markdown("---")
        st.subheader("可用 Lot 分配顺序")

        if lot_df.empty:
            st.error("当前没有可用 Lot。")
        else:
            show_df(lot_df.rename(columns={
                "inventory_lot_id": "Lot编号",
                "lot_code": "Lot号",
                "location": "库存类型",
                "available_qty": "可用数量",
                "release_status": "放行状态",
                "lot_status": "Lot状态",
                "alloc_priority": "分配优先级"
            }), hide_index=True)

        # =========================
        # 6. 发货确认表单
        # =========================
        st.markdown("---")
        st.subheader("发货确认")

        with st.form("delivery_plan_shipment_confirm_form"):
            ship_qty = st.number_input(
                "本次出货数量",
                min_value=1.0,
                value=float(min(remaining_qty, available_qty)) if min(remaining_qty, available_qty) > 0 else 1.0,
                step=1.0,
                key="delivery_plan_ship_qty"
            )

            carrier = st.text_input(
                "承运商",
                value="SF Express",
                key="delivery_plan_ship_carrier"
            )

            destination = st.text_input(
                "目的地",
                value="Customer Warehouse",
                key="delivery_plan_ship_destination"
            )

            created_by = st.text_input(
                "创建人",
                value="Warehouse User",
                key="delivery_plan_ship_created_by"
            )

            st.markdown("### 最终确认")

            confirm_check = st.checkbox(
                "我已核对客户、PO、交付批次、规格、数量、库存 Lot，确认可以发货。",
                key="shipment_confirm_check"
            )

            confirm_text = st.text_input(
                "请输入 CONFIRM 进行二次确认",
                value="",
                placeholder="输入 CONFIRM 后才能正式出货",
                key="shipment_confirm_text"
            )

            submitted = st.form_submit_button("确认发货并同步数据")

        if submitted:
            if not check_pass:
                st.error("出货前检查未通过，不能发货。")
                return

            if not confirm_check:
                st.error("请先勾选发货确认。")
                return

            if confirm_text.strip().upper() != "CONFIRM":
                st.error("请输入 CONFIRM 完成二次确认。")
                return

            if float(ship_qty) <= 0:
                st.error("出货数量必须大于 0。")
                return

            if float(ship_qty) > remaining_qty:
                st.error(f"出货数量不能超过剩余待出货数量：{remaining_qty:.0f}。")
                return

            if float(ship_qty) > available_qty:
                st.error(f"出货数量不能超过当前可用库存：{available_qty:.0f}。")
                return

            ok, msg = run_delivery_plan_shipment(
                conn=conn,
                delivery_plan_id=int(selected_delivery_plan_id),
                ship_qty=float(ship_qty),
                carrier=carrier,
                destination=destination,
                created_by=created_by
            )

            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")

    # =========================
    # 7. 出货记录
    # =========================
    st.subheader("出货记录")

    shipment_df = pd.read_sql_query("""
        SELECT
            s.shipment_id,
            s.shipment_no,
            s.ship_date,
            s.carrier,
            s.destination,
            s.created_by,
            s.shipment_status,
            si.shipment_item_id,
            si.order_item_id,
            si.inventory_lot_id,
            il.lot_code,
            il.location,
            si.shipped_qty,
            si.packaging_label_code,
            si.trace_key
        FROM shipment s
        LEFT JOIN shipment_item si
            ON s.shipment_id = si.shipment_id
        LEFT JOIN inventory_lot il
            ON si.inventory_lot_id = il.inventory_lot_id
        ORDER BY s.shipment_id DESC, si.shipment_item_id DESC
    """, conn)

    if shipment_df.empty:
        st.info("当前没有出货记录。")
    else:
        show_df(shipment_df, hide_index=True)

    st.markdown("---")

    # =========================
    # 8. 出货后库存流水
    # =========================
    st.subheader("库存出货流水")

    txn_df = pd.read_sql_query("""
        SELECT
            itl.txn_id,
            itl.inventory_lot_id,
            il.lot_code,
            il.location,
            itl.txn_type,
            itl.qty,
            itl.txn_time,
            itl.txn_reason,
            itl.reference_no
        FROM inventory_transaction_log itl
        LEFT JOIN inventory_lot il
            ON itl.inventory_lot_id = il.inventory_lot_id
        WHERE itl.txn_type = 'outbound'
        ORDER BY itl.txn_id DESC
    """, conn)

    if txn_df.empty:
        st.info("当前没有出货流水。")
    else:
        show_df(txn_df, hide_index=True)

# =========================
# 覆盖版：质检中 → 质量放行 → 自动入库 → 库存/交付状态同步
# =========================

def auto_inbound_after_quality_release(conn, production_batch_id):
    """
    质量放行后自动入库。

    同步内容：
    1. 生成或更新 inventory_lot
    2. location = WH-ORDER
    3. lot_status = available
    4. release_status = released
    5. 写入 inventory_transaction_log
    6. delivery_plan.delivery_status = 已入库
    """

    cursor = conn.cursor()

    info_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.special_process, 'STANDARD') AS special_process,
            COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,

            ps.production_schedule_id,
            ps.delivery_plan_id,
            ps.order_item_id,

            oi.product_id,
            oi.spec_id,
            oi.product_spec_text,
            oi.po_no,
            oi.trace_key AS order_trace_key,

            pm.measurement_id,
            pm.quality_status,
            pm.release_status
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        WHERE pb.production_batch_id = ?
        ORDER BY pm.measurement_id DESC
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    if info_df.empty:
        return False, "未找到生产批次，无法入库。"

    row = info_df.iloc[0]

    release_status = str(row["release_status"] or "").lower()
    if release_status != "released":
        return False, "当前批次尚未放行，不能自动入库。"

    actual_qty = float(row["actual_qty"] or 0)

    if actual_qty <= 0:
        return False, "实际生产数量为 0，不能自动入库。请先在生产过程录入中填写产出数量。"

    if pd.isna(row["product_id"]):
        return False, "缺少 product_id，不能自动入库。"

    product_id = int(row["product_id"])
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None

    delivery_plan_id = int(row["delivery_plan_id"]) if pd.notna(row["delivery_plan_id"]) else None
    order_trace_key = str(row["order_trace_key"] or row["trace_key"])
    batch_code = str(row["batch_code"])

    # 检查是否已经存在该生产批次对应 Lot
    existing_lot_df = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            available_qty,
            location,
            release_status,
            lot_status
        FROM inventory_lot
        WHERE production_batch_id = ?
        ORDER BY inventory_lot_id
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    # 情况 1：还没有 Lot，创建新 Lot
    if existing_lot_df.empty:
        lot_code = f"LOT-AUTO-{int(production_batch_id):04d}"

        cursor.execute("""
            INSERT INTO inventory_lot (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                trace_key,
                location,
                available_qty,
                reserved_qty,
                lot_status,
                release_status,
                exclusive_customer,
                forbidden_customer
            ) VALUES (?, ?, ?, ?, ?, 'WH-ORDER', ?, 0, 'available', 'released', '', '')
        """, (
            int(production_batch_id),
            product_id,
            spec_id,
            lot_code,
            order_trace_key,
            actual_qty
        ))

        inventory_lot_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id,
                txn_type,
                qty,
                txn_time,
                txn_reason,
                reference_no
            ) VALUES (?, 'inbound', ?, datetime('now'), 'quality_release_auto_inbound', ?)
        """, (
            int(inventory_lot_id),
            actual_qty,
            batch_code
        ))

        inbound_msg = f"已创建入库 Lot：{lot_code}，入库数量 {actual_qty:.0f}。"

    # 情况 2：已有 Lot，只同步状态和数量，不重复创建 Lot
    else:
        inventory_lot_id = int(existing_lot_df.iloc[0]["inventory_lot_id"])
        lot_code = str(existing_lot_df.iloc[0]["lot_code"])
        old_available_qty = float(existing_lot_df.iloc[0]["available_qty"] or 0)

        cursor.execute("""
            UPDATE inventory_lot
            SET product_id = ?,
                spec_id = ?,
                trace_key = ?,
                location = 'WH-ORDER',
                available_qty = ?,
                lot_status = 'available',
                release_status = 'released'
            WHERE inventory_lot_id = ?
        """, (
            product_id,
            spec_id,
            order_trace_key,
            actual_qty,
            int(inventory_lot_id)
        ))

        # 如果数量发生变化，补一条修正流水
        if abs(actual_qty - old_available_qty) > 0.000001:
            cursor.execute("""
                INSERT INTO inventory_transaction_log (
                    inventory_lot_id,
                    txn_type,
                    qty,
                    txn_time,
                    txn_reason,
                    reference_no
                ) VALUES (?, 'inbound_adjust', ?, datetime('now'), 'quality_release_inbound_qty_sync', ?)
            """, (
                int(inventory_lot_id),
                actual_qty - old_available_qty,
                batch_code
            ))

        inbound_msg = f"已同步已有 Lot：{lot_code}，库存数量 {old_available_qty:.0f} → {actual_qty:.0f}。"

    # 同步交付批次状态为已入库
    if delivery_plan_id is not None:
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = '已入库'
            WHERE delivery_plan_id = ?
        """, (
            int(delivery_plan_id),
        ))

    conn.commit()

    return True, f"质量放行后自动入库完成。{inbound_msg}"


def page_quality_release(conn):
    st.header("出货追踪｜质量放行")

    st.info(
        "放行逻辑：release_status = released 后，系统会自动入库，"
        "并同步库存 Lot、库存流水、交付批次状态。"
    )

    df = pd.read_sql_query("""
        SELECT
            pm.measurement_id,
            pm.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,

            COALESCE(pm.quality_status, 'Pending') AS quality_status,
            COALESCE(pm.release_status, 'pending') AS release_status,
            pm.inspected_at,
            pm.release_by,

            ps.production_schedule_id,
            ps.delivery_plan_id,
            dp.delivery_status,

            oi.order_item_id,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material,

            il.inventory_lot_id,
            il.lot_code,
            il.location,
            il.available_qty,
            il.lot_status,
            il.release_status AS lot_release_status
        FROM production_measurement pm
        JOIN production_batch pb
            ON pm.production_batch_id = pb.production_batch_id
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        ORDER BY pm.measurement_id DESC
    """, conn)

    if df.empty:
        st.info("当前没有质检记录。生产完成 Packing + done 后会自动生成 pending 质检记录。")
        return

    st.subheader("质检 / 放行记录")
    show_df(df, hide_index=True)

    st.markdown("---")
    st.subheader("执行质量放行")

    selected_measurement_id = st.selectbox(
        "选择质检记录",
        df["measurement_id"].tolist(),
        format_func=lambda x: (
            f"检测 {x} | "
            f"{df.loc[df['measurement_id'] == x, 'batch_code'].iloc[0]} | "
            f"放行状态 {df.loc[df['measurement_id'] == x, 'release_status'].iloc[0]} | "
            f"交付状态 {df.loc[df['measurement_id'] == x, 'delivery_status'].iloc[0]}"
        ),
        key="quality_release_measurement_select"
    )

    selected = df[df["measurement_id"] == selected_measurement_id].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("生产批号", str(selected["batch_code"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("实际生产数量", f"{float(selected['actual_qty'] or 0):.0f}")
    c4.metric("当前放行状态", str(selected["release_status"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("规格", str(selected["product_spec_text"]))
    c6.metric("特殊工艺", str(selected["special_process"]))
    c7.metric("材质", str(selected["material"]))
    c8.metric("交付状态", str(selected["delivery_status"]))

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("Lot", str(selected["lot_code"]) if pd.notna(selected["lot_code"]) else "-")
    c10.metric("库位", str(selected["location"]) if pd.notna(selected["location"]) else "-")
    c11.metric("库存数量", f"{float(selected['available_qty'] or 0):.0f}" if pd.notna(selected["available_qty"]) else "-")
    c12.metric("Lot状态", str(selected["lot_status"]) if pd.notna(selected["lot_status"]) else "-")

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    new_quality_status = st.selectbox(
        "质量等级",
        ["A", "B", "C", "Pending", "NG"],
        index=0,
        key="quality_release_quality_status"
    )

    new_release_status = st.selectbox(
        "放行状态",
        ["released", "hold", "pending"],
        index=0,
        key="quality_release_release_status"
    )

    release_by = st.text_input(
        "放行人",
        value="QC User",
        key="quality_release_by"
    )

    if st.button("更新放行状态并同步入库", key="quality_release_submit"):
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = ?,
                release_status = ?,
                inspected_at = datetime('now'),
                release_by = ?
            WHERE measurement_id = ?
        """, (
            new_quality_status,
            new_release_status,
            release_by,
            int(selected_measurement_id)
        ))

        conn.commit()

        production_batch_id = int(selected["production_batch_id"])

        if new_release_status == "released":
            ok, msg = auto_inbound_after_quality_release(
                conn,
                production_batch_id
            )

            if ok:
                st.success(msg)
            else:
                st.warning(msg)

        elif new_release_status == "hold":
            if pd.notna(selected["delivery_plan_id"]):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE delivery_plan
                    SET delivery_status = '质检中'
                    WHERE delivery_plan_id = ?
                """, (
                    int(selected["delivery_plan_id"]),
                ))

                cursor.execute("""
                    UPDATE inventory_lot
                    SET lot_status = 'hold',
                        release_status = 'hold'
                    WHERE production_batch_id = ?
                """, (
                    production_batch_id,
                ))

                conn.commit()

            st.warning("该批次已设为 hold，保持质检中，暂不入库。")

        else:
            if pd.notna(selected["delivery_plan_id"]):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE delivery_plan
                    SET delivery_status = '质检中'
                    WHERE delivery_plan_id = ?
                """, (
                    int(selected["delivery_plan_id"]),
                ))

                cursor.execute("""
                    UPDATE inventory_lot
                    SET lot_status = 'hold',
                        release_status = 'pending'
                    WHERE production_batch_id = ?
                """, (
                    production_batch_id,
                ))

                conn.commit()

            st.info("该批次保持 pending，暂不入库。")

        st.rerun()


# =========================
# 覆盖版：排产流程加入质检 / 入库入口，库存看板加入入库确认
# =========================

def ensure_qc_record_for_batch(conn, production_batch_id):
    """
    确保生产批次有一条质检记录。
    如果没有，则创建 pending 质检记录。
    """
    cursor = conn.cursor()

    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if int(exists_df.iloc[0]["cnt"]) == 0:
        cursor.execute("""
            INSERT INTO production_measurement (
                production_batch_id,
                quality_status,
                release_status,
                inspected_at,
                release_by
            ) VALUES (?, 'Pending', 'pending', datetime('now'), 'Auto QC')
        """, (
            int(production_batch_id),
        ))

        conn.commit()

    return True

def update_batch_quality_release(
    conn,
    production_batch_id,
    quality_status,
    release_status,
    release_by,
    qc_before_qty=None,
    qc_after_qty=None,
    qc_note=""
):
    """
    半成品仓库内执行质检放行。

    新增：
    - qc_before_qty：检测前数量
    - qc_after_qty：检测后合格数量
    - qc_loss_qty：检测损耗 / 不合格数量 = 检测前 - 检测后

    released:
    - delivery_plan = 待入库确认
    - production_batch.actual_qty = qc_after_qty
    - production_batch.semi_finished_wh_qty = qc_after_qty

    hold / pending:
    - delivery_plan = 质检中
    - 半成品仍留在半成品仓库
    """

    ensure_semi_finished_warehouse_schema(conn)

    cursor = conn.cursor()

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            ps.delivery_plan_id
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        WHERE pb.production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if batch_df.empty:
        return False, "未找到生产批次。"

    batch = batch_df.iloc[0]
    batch_code = str(batch["batch_code"])

    old_semi_qty = float(batch["semi_finished_wh_qty"] or 0)
    actual_qty = float(batch["actual_qty"] or 0)

    if qc_before_qty is None:
        qc_before_qty = old_semi_qty if old_semi_qty > 0 else actual_qty

    if qc_after_qty is None:
        qc_after_qty = qc_before_qty

    qc_before_qty = float(qc_before_qty or 0)
    qc_after_qty = float(qc_after_qty or 0)

    if qc_before_qty <= 0:
        return False, "检测前数量必须大于 0。"

    if qc_after_qty < 0:
        return False, "检测后数量不能小于 0。"

    if qc_after_qty > qc_before_qty:
        return False, "检测后数量不能大于检测前数量。"

    qc_loss_qty = qc_before_qty - qc_after_qty

    # 确保有质检记录
    exists_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if int(exists_df.iloc[0]["cnt"]) == 0:
        cursor.execute("""
            INSERT INTO production_measurement (
                production_batch_id,
                quality_status,
                release_status,
                inspected_at,
                release_by,
                qc_before_qty,
                qc_after_qty,
                qc_loss_qty,
                qc_note
            ) VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?, ?)
        """, (
            int(production_batch_id),
            quality_status,
            release_status,
            release_by,
            float(qc_before_qty),
            float(qc_after_qty),
            float(qc_loss_qty),
            normalize_text(qc_note)
        ))
    else:
        cursor.execute("""
            UPDATE production_measurement
            SET quality_status = ?,
                release_status = ?,
                inspected_at = datetime('now'),
                release_by = ?,
                qc_before_qty = ?,
                qc_after_qty = ?,
                qc_loss_qty = ?,
                qc_note = ?
            WHERE production_batch_id = ?
        """, (
            quality_status,
            release_status,
            release_by,
            float(qc_before_qty),
            float(qc_after_qty),
            float(qc_loss_qty),
            normalize_text(qc_note),
            int(production_batch_id)
        ))

    schedule_df = pd.read_sql_query("""
        SELECT delivery_plan_id
        FROM production_schedule
        WHERE production_batch_id = ?
        ORDER BY production_schedule_id DESC
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    delivery_plan_id = None
    if not schedule_df.empty and pd.notna(schedule_df.iloc[0]["delivery_plan_id"]):
        delivery_plan_id = int(schedule_df.iloc[0]["delivery_plan_id"])

    release_status_lower = str(release_status).lower()

    if release_status_lower == "released":
        cursor.execute("""
            UPDATE production_batch
            SET actual_qty = ?,
                semi_finished_wh_qty = ?,
                production_flow_status = 'qc_released'
            WHERE production_batch_id = ?
        """, (
            float(qc_after_qty),
            float(qc_after_qty),
            int(production_batch_id)
        ))

        if delivery_plan_id is not None:
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '待入库确认'
                WHERE delivery_plan_id = ?
            """, (
                int(delivery_plan_id),
            ))

        conn.commit()
        if delivery_plan_id is not None:
            sync_after_delivery_plan_change(conn, int(delivery_plan_id))

        record_semi_finished_txn(
            conn=conn,
            production_batch_id=int(production_batch_id),
            batch_code=batch_code,
            txn_type="qc_released",
            qty_before=old_semi_qty,
            qty_after=qc_after_qty,
            txn_reason=f"质检放行；检测前 {qc_before_qty:.0f}，检测后 {qc_after_qty:.0f}，损耗 {qc_loss_qty:.0f}",
            operator_name=release_by,
            reference_no=batch_code
        )

        return True, (
            f"质检已放行。检测前 {qc_before_qty:.0f}，"
            f"检测后 {qc_after_qty:.0f}，损耗 {qc_loss_qty:.0f}。"
            "交付批次已进入【待入库确认】。"
        )

    else:
        cursor.execute("""
            UPDATE production_batch
            SET semi_finished_wh_qty = ?,
                production_flow_status = 'qc_hold'
            WHERE production_batch_id = ?
        """, (
            float(qc_before_qty),
            int(production_batch_id)
        ))

        if delivery_plan_id is not None:
            cursor.execute("""
                UPDATE delivery_plan
                SET delivery_status = '质检中'
                WHERE delivery_plan_id = ?
            """, (
                int(delivery_plan_id),
            ))

        conn.commit()
        if delivery_plan_id is not None:
           sync_after_delivery_plan_change(conn, int(delivery_plan_id))

        return True, (
            f"该批次仍保留在【质检中】。检测前 {qc_before_qty:.0f}，"
            f"检测后 {qc_after_qty:.0f}，损耗 {qc_loss_qty:.0f}。"
        )



def confirm_batch_inbound_to_inventory(conn, production_batch_id, location=None, confirmed_by="Warehouse User"):
    """
    仓储总看板：入库确认。

    自动分类入库规则：
    1. 计划交付数量以内 -> 订单库存 WH-ORDER
    2. 超过计划交付数量 -> 规格化库存 WH-SPEC
    3. 自动写入 inventory_transaction_log
    4. production_batch.finished_wh_qty = 入库数量
    5. production_batch.semi_finished_wh_qty = 0
    6. production_batch.production_flow_status = 'inbound_done'
    7. delivery_plan.delivery_status = '已入库'
    8. 调用 sync_after_delivery_plan_change() 统一同步
    """

    cursor = conn.cursor()

    info_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
            COALESCE(pb.special_process, 'STANDARD') AS special_process,
            COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,

            ps.production_schedule_id,
            ps.delivery_plan_id,
            ps.order_item_id,

            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            oi.product_id,
            oi.spec_id,
            oi.trace_key AS order_trace_key,
            oi.po_no,
            oi.product_spec_text,
            COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS order_special_process,
            COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS order_material,

            pm.measurement_id,
            COALESCE(pm.quality_status, 'Pending') AS quality_status,
            COALESCE(pm.release_status, 'pending') AS release_status,
            COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
            COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
            COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        WHERE pb.production_batch_id = ?
        ORDER BY pm.measurement_id DESC
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    if info_df.empty:
        return False, "未找到生产批次，无法入库。"

    row = info_df.iloc[0]

    batch_code = str(row["batch_code"])
    delivery_plan_id = row["delivery_plan_id"]
    order_item_id = row["order_item_id"]

    release_status = str(row["release_status"] or "pending").lower()

    if release_status != "released":
        return False, "当前批次尚未质检放行，不能入库。请先到【半成品仓库看板 → 质检放行】完成放行。"

    # =========================
    # 防止重复入库
    # =========================
    exists_lot_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM inventory_lot
        WHERE production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if int(exists_lot_df.iloc[0]["cnt"] or 0) > 0:
        return False, "该生产批次已经生成库存 Lot，不能重复入库。"

    actual_qty = float(row["actual_qty"] or 0)
    semi_finished_qty = float(row["semi_finished_wh_qty"] or 0)
    qc_after_qty = float(row["qc_after_qty"] or 0)

    # 优先使用检测后合格数量，其次使用实际生产数量
    inbound_qty = qc_after_qty if qc_after_qty > 0 else actual_qty

    if inbound_qty <= 0:
        return False, "可入库数量为 0，不能入库。"

    planned_delivery_qty = float(row["planned_delivery_qty"] or 0)

    # 订单库存数量：计划交付数量以内
    order_linked_inbound_qty = min(inbound_qty, planned_delivery_qty)

    # 规格化库存数量：超出计划交付部分
    extra_spec_inbound_qty = max(inbound_qty - order_linked_inbound_qty, 0)

    product_id = int(row["product_id"]) if pd.notna(row["product_id"]) else None
    spec_id = int(row["spec_id"]) if pd.notna(row["spec_id"]) else None

    order_trace_key = str(row["order_trace_key"] or row["trace_key"])
    product_spec_text = str(row["product_spec_text"] or "")
    order_special_process = str(row["order_special_process"] or row["special_process"] or "STANDARD")
    order_material = str(row["order_material"] or row["material"] or "UNKNOWN_MATERIAL")

    spec_stock_trace_key = build_spec_stock_trace_key(
        product_spec_text=product_spec_text,
        special_process=order_special_process,
        material=order_material
    )

    # =========================
    # 1. 订单库存 WH-ORDER
    # =========================
    if order_linked_inbound_qty > 0:
        order_lot_code = f"LOT-ORDER-{batch_code}"

        cursor.execute("""
            INSERT INTO inventory_lot (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                trace_key,
                location,
                available_qty,
                reserved_qty,
                lot_status,
                release_status,
                exclusive_customer,
                forbidden_customer
            ) VALUES (?, ?, ?, ?, ?, 'WH-ORDER', ?, 0, 'available', 'released', NULL, NULL)
        """, (
            int(production_batch_id),
            product_id,
            spec_id,
            order_lot_code,
            order_trace_key,
            float(order_linked_inbound_qty)
        ))

        order_lot_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id,
                txn_type,
                qty,
                txn_reason,
                reference_no
            ) VALUES (?, 'inbound', ?, ?, ?)
        """, (
            int(order_lot_id),
            float(order_linked_inbound_qty),
            f"入库确认：订单库存；操作人：{confirmed_by}",
            batch_code
        ))

    # =========================
    # 2. 规格化库存 WH-SPEC
    # =========================
    if extra_spec_inbound_qty > 0:
        spec_lot_code = f"LOT-SPEC-{batch_code}"

        cursor.execute("""
            INSERT INTO inventory_lot (
                production_batch_id,
                product_id,
                spec_id,
                lot_code,
                trace_key,
                location,
                available_qty,
                reserved_qty,
                lot_status,
                release_status,
                exclusive_customer,
                forbidden_customer
            ) VALUES (?, ?, ?, ?, ?, 'WH-SPEC', ?, 0, 'available', 'released', NULL, NULL)
        """, (
            int(production_batch_id),
            product_id,
            spec_id,
            spec_lot_code,
            spec_stock_trace_key,
            float(extra_spec_inbound_qty)
        ))

        spec_lot_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO inventory_transaction_log (
                inventory_lot_id,
                txn_type,
                qty,
                txn_reason,
                reference_no
            ) VALUES (?, 'inbound', ?, ?, ?)
        """, (
            int(spec_lot_id),
            float(extra_spec_inbound_qty),
            f"入库确认：规格化库存；操作人：{confirmed_by}",
            batch_code
        ))

    # =========================
    # 3. 更新生产批次：半成品清零，成品库存更新
    # =========================
    cursor.execute("""
        UPDATE production_batch
        SET finished_wh_qty = ?,
            semi_finished_wh_qty = 0,
            actual_qty = ?,
            production_flow_status = 'inbound_done'
        WHERE production_batch_id = ?
    """, (
        float(inbound_qty),
        float(inbound_qty),
        int(production_batch_id)
    ))

    # =========================
    # 4. 更新交付批次状态
    # 注意：这里不更新 actual_delivery_qty，因为 actual_delivery_qty 应该由出货完成后更新
    # =========================
    if pd.notna(delivery_plan_id):
        cursor.execute("""
            UPDATE delivery_plan
            SET delivery_status = '已入库'
            WHERE delivery_plan_id = ?
        """, (
            int(delivery_plan_id),
        ))

    conn.commit()

    # =========================
    # 5. 半成品流水：入库转出
    # =========================
    if "record_semi_finished_txn" in globals():
        record_semi_finished_txn(
            conn=conn,
            production_batch_id=int(production_batch_id),
            batch_code=batch_code,
            txn_type="finished_inbound",
            qty_before=float(semi_finished_qty),
            qty_after=0,
            txn_reason=(
                f"成品入库确认；入库数量 {inbound_qty:.0f}；"
                f"订单库存 {order_linked_inbound_qty:.0f}；"
                f"规格化库存 {extra_spec_inbound_qty:.0f}"
            ),
            operator_name=confirmed_by,
            reference_no=batch_code
        )

    # =========================
    # 6. 统一同步交付批次 / 订单状态
    # =========================
    if pd.notna(delivery_plan_id):
        if "sync_after_delivery_plan_change" in globals():
            sync_after_delivery_plan_change(
                conn,
                int(delivery_plan_id)
            )

    if extra_spec_inbound_qty > 0:
        return True, (
            f"入库确认完成。"
            f"订单库存 {order_linked_inbound_qty:.0f}，"
            f"规格化库存 {extra_spec_inbound_qty:.0f}，"
            f"半成品库存已清零，生产状态已更新为 inbound_done。"
        )

    return True, (
        f"入库确认完成。"
        f"订单库存 {order_linked_inbound_qty:.0f}，"
        f"半成品库存已清零，生产状态已更新为 inbound_done。"
    )



def page_production_dashboard(conn):
    st.header("生产｜排产看板")

    st.info(
        "排产看板现在只负责：销售推送待确认、排产确认、生产过程查看。"
        "质检放行和待入库确认已移动到【半成品仓库 → 半成品仓库看板】。"
    )

    tab_pending, tab_schedule, tab_detail = st.tabs([
        "销售推送待确认",
        "排产过程",
        "当前排产明细"
    ])

    # =========================
    # 1. 销售推送待确认
    # =========================
    with tab_pending:
        st.subheader("销售推送待确认")

        pending_df = pd.read_sql_query("""
            SELECT
                dp.delivery_plan_id,
                dp.order_item_id,
                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                dp.planned_delivery_date,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                c.customer_name,
                oi.po_no,
                oi.customer_pn,
                oi.drawing_version,
                oi.factory_part_no,
                oi.product_type_text,
                oi.product_spec_text,
                COALESCE(oi.special_process, 'STANDARD') AS special_process,
                COALESCE(oi.material, 'UNKNOWN_MATERIAL') AS material,
                oi.trace_key
            FROM delivery_plan dp
            JOIN order_item oi
                ON dp.order_item_id = oi.order_item_id
            JOIN orders o
                ON oi.order_id = o.order_id
            JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_schedule ps
                ON dp.delivery_plan_id = ps.delivery_plan_id
            WHERE ( COALESCE(dp.delivery_status, '未排产') = '待生产确认'
                 OR COALESCE(dp.sales_need_production, 0) = 1
                 )
             AND ps.production_schedule_id IS NULL
            ORDER BY dp.planned_delivery_date, dp.delivery_plan_id
        """, conn)

        if pending_df.empty:
            st.info("当前没有销售推送待确认的交付批次。")
        else:
            show_df(pending_df.rename(columns={
                "delivery_plan_id": "交付计划编号",
                "order_item_id": "订单明细编号",
                "delivery_batch_no": "交付批次",
                "planned_delivery_date": "计划交付日期",
                "planned_delivery_qty": "计划交付数量",
                "actual_delivery_qty": "实际交付数量",
                "delivery_status": "状态",
                "customer_name": "客户",
                "po_no": "PO",
                "customer_pn": "客户料号",
                "drawing_version": "图纸版本",
                "factory_part_no": "本厂料号",
                "product_type_text": "产品",
                "product_spec_text": "规格",
                "special_process": "特殊工艺",
                "material": "材质",
                "trace_key": "Trace Key"
            }), hide_index=True)

            st.markdown("---")

            selected_pending_id = st.selectbox(
                "选择销售推送单进行生产确认",
                pending_df["delivery_plan_id"].tolist(),
                format_func=lambda x: (
                    f"【{pending_df.loc[pending_df['delivery_plan_id'] == x, 'delivery_status'].iloc[0]}】 "
                    f"交付计划 {x} | "
                    f"PO {pending_df.loc[pending_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
                    f"第 {int(pending_df.loc[pending_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
                    f"计划交付 {pending_df.loc[pending_df['delivery_plan_id'] == x, 'planned_delivery_date'].iloc[0]} | "
                    f"数量 {float(pending_df.loc[pending_df['delivery_plan_id'] == x, 'planned_delivery_qty'].iloc[0] or 0):.0f}"
                ),
                key="production_pending_select"
            )

            selected = pending_df[
                pending_df["delivery_plan_id"] == selected_pending_id
            ].iloc[0]

            st.markdown("### 排产确认卡片")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("客户", str(selected["customer_name"]))
            c2.metric("PO", str(selected["po_no"]))
            c3.metric("交付批次", f"第 {int(selected['delivery_batch_no'])} 批")
            c4.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("产品", str(selected["product_type_text"]))
            c6.metric("规格", str(selected["product_spec_text"]))
            c7.metric("特殊工艺", str(selected["special_process"]))
            c8.metric("材质", str(selected["material"]))

            st.caption(
                f"客户料号：{selected['customer_pn']} ｜ "
                f"图纸版本：{selected['drawing_version']} ｜ "
                f"本厂料号：{selected['factory_part_no']} ｜ "
                f"计划交付日期：{selected['planned_delivery_date']}"
            )

            st.markdown("Trace Key")
            st.code(str(selected["trace_key"]))

            default_batch_code = (
                f"BATCH-"
                f"{normalize_trace_part(selected['po_no'], 'PO')}-"
                f"{int(selected['delivery_batch_no'])}"
            )

            st.markdown("---")
            st.markdown("### 生产确认信息")

            p_confirm_1, p_confirm_2 = st.columns(2)

            with p_confirm_1:
                manual_batch_code = st.text_input(
                    "生产端手动录入生产批号",
                    value=default_batch_code,
                    key=f"manual_batch_code_{selected_pending_id}"
                )

            with p_confirm_2:
                planned_qty_input = st.number_input(
                    "确认应生产数量",
                    min_value=1.0,
                    value=float(selected["planned_delivery_qty"] or 1),
                    step=1.0,
                    key=f"confirm_planned_qty_{selected_pending_id}"
                )

            gauge_col_1, gauge_col_2 = st.columns(2)

            with gauge_col_1:
                common_gauge_size = st.text_input(
                    "通规尺寸",
                    placeholder="例如：20.00 mm / Go Gauge 20.00",
                    key=f"common_gauge_size_{selected_pending_id}"
                )

            with gauge_col_2:
                stop_gauge_size = st.text_input(
                    "止规尺寸",
                    placeholder="例如：20.10 mm / No-Go Gauge 20.10",
                    key=f"stop_gauge_size_{selected_pending_id}"
                )

            st.caption(
                "说明：生产批号、通规尺寸、止规尺寸会随生产批次一起保存，用于后续生产、质检和批次追踪。"
            )

            if st.button("生产确认并创建批次", key=f"confirm_production_{selected_pending_id}"):

                if not normalize_text(manual_batch_code):
                    st.error("请填写生产批号。")
                    return

                if not normalize_text(common_gauge_size):
                    st.error("请填写通规尺寸。")
                    return

                if not normalize_text(stop_gauge_size):
                    st.error("请填写止规尺寸。")
                    return

                ok, msg = create_production_for_delivery_plan(
                    conn=conn,
                    delivery_plan_id=int(selected_pending_id),
                    planned_qty=float(planned_qty_input),
                    manual_batch_code=manual_batch_code,
                    common_gauge_size=common_gauge_size,
                    stop_gauge_size=stop_gauge_size
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # =========================
    # 2. 排产过程
    # 只显示：已排产 / 生产中
    # =========================
    with tab_schedule:
        st.subheader("排产过程")

        schedule_df = pd.read_sql_query("""
            SELECT
                ps.production_schedule_id,
                ps.delivery_plan_id,
                ps.order_item_id,
                ps.production_batch_id,
                ps.scheduled_start_date,
                ps.scheduled_end_date,

                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                dp.planned_delivery_date,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                pb.batch_code,
                COALESCE(pb.required_production_qty, 0) AS required_production_qty,
                COALESCE(pb.actual_qty, 0) AS actual_qty,
                COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
                COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
                COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,
                COALESCE(pb.material, 'UNKNOWN_MATERIAL') AS material,
                COALESCE(pb.special_process, 'STANDARD') AS special_process,
                pb.common_gauge_size,
                pb.stop_gauge_size,

                c.customer_name,
                oi.po_no,
                oi.customer_pn,
                oi.product_type_text,
                oi.product_spec_text,
                oi.trace_key
            FROM production_schedule ps
            JOIN production_batch pb
                ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN delivery_plan dp
                ON ps.delivery_plan_id = dp.delivery_plan_id
            LEFT JOIN order_item oi
                ON ps.order_item_id = oi.order_item_id
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            LEFT JOIN customer c
                ON o.customer_id = c.customer_id
            WHERE COALESCE(dp.delivery_status, '未排产') IN (
                '已排产',
                '生产中'
            )
            ORDER BY ps.production_schedule_id DESC
        """, conn)

        if schedule_df.empty:
            st.info(
                "当前没有处于【已排产】或【生产中】的排产记录。"
                "已进入质检、待入库或已入库的批次，请到【半成品仓库】或【仓储总看板】查看。"
            )
        else:
            selected_schedule_id = st.selectbox(
                "选择排产记录查看过程",
                schedule_df["production_schedule_id"].tolist(),
                format_func=lambda x: (
                    f"【{schedule_df.loc[schedule_df['production_schedule_id'] == x, 'delivery_status'].iloc[0]}】 "
                    f"排程 {x} | "
                    f"PO {schedule_df.loc[schedule_df['production_schedule_id'] == x, 'po_no'].iloc[0]} | "
                    f"{schedule_df.loc[schedule_df['production_schedule_id'] == x, 'batch_code'].iloc[0]} | "
                    f"第 {int(schedule_df.loc[schedule_df['production_schedule_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
                    f"计划交付 {schedule_df.loc[schedule_df['production_schedule_id'] == x, 'planned_delivery_date'].iloc[0]} | "
                    f"计划数量 {float(schedule_df.loc[schedule_df['production_schedule_id'] == x, 'planned_delivery_qty'].iloc[0] or 0):.0f} | "
                    f"实际生产 {float(schedule_df.loc[schedule_df['production_schedule_id'] == x, 'actual_qty'].iloc[0] or 0):.0f}"
                ),
                key="production_schedule_process_select"
            )

            selected_sch = schedule_df[
                schedule_df["production_schedule_id"] == selected_schedule_id
            ].iloc[0]

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("排程编号", int(selected_sch["production_schedule_id"]))
            p2.metric("生产批号", str(selected_sch["batch_code"]))
            p3.metric("交付批次", f"第 {int(selected_sch['delivery_batch_no'])} 批")
            p4.metric("交付状态", str(selected_sch["delivery_status"]))

            p5, p6, p7, p8 = st.columns(4)
            p5.metric("客户", str(selected_sch["customer_name"]))
            p6.metric("PO", str(selected_sch["po_no"]))
            p7.metric("应生产数量", f"{float(selected_sch['required_production_qty'] or 0):.0f}")
            p8.metric("实际生产数量", f"{float(selected_sch['actual_qty'] or 0):.0f}")

            p9, p10, p11, p12 = st.columns(4)
            p9.metric("生产状态", str(selected_sch["production_flow_status"]))
            p10.metric("通规尺寸", str(selected_sch["common_gauge_size"]) if pd.notna(selected_sch["common_gauge_size"]) else "-")
            p11.metric("止规尺寸", str(selected_sch["stop_gauge_size"]) if pd.notna(selected_sch["stop_gauge_size"]) else "-")
            p12.metric("半成品数量", f"{float(selected_sch['semi_finished_wh_qty'] or 0):.0f}")

            st.caption(
                f"产品：{selected_sch['product_type_text']} ｜ "
                f"规格：{selected_sch['product_spec_text']} ｜ "
                f"特殊工艺：{selected_sch['special_process']} ｜ "
                f"材质：{selected_sch['material']}"
            )

            st.markdown("Trace Key")
            st.code(str(selected_sch["trace_key"]))

            st.markdown("### 排产流程")

            flow_steps = [
                "销售推送",
                "生产确认",
                "已排产",
                "生产过程录入",
                "进入半成品仓库",
                "质检放行",
                "待入库确认",
                "成品入库"
            ]

            current_delivery_status = str(selected_sch["delivery_status"])
            current_prod_status = str(selected_sch["production_flow_status"])
            semi_qty = float(selected_sch["semi_finished_wh_qty"] or 0)
            finished_qty = float(selected_sch["finished_wh_qty"] or 0)

            if current_delivery_status == "已入库" or finished_qty > 0:
                active_index = 7
            elif current_delivery_status == "待入库确认":
                active_index = 6
            elif current_delivery_status == "质检中":
                active_index = 5
            elif semi_qty > 0:
                active_index = 4
            elif current_delivery_status == "生产中" or current_prod_status not in ["planned", "", None]:
                active_index = 3
            else:
                active_index = 2

            cols = st.columns(len(flow_steps))
            for i, step in enumerate(flow_steps):
                if i < active_index:
                    cols[i].success(step)
                elif i == active_index:
                    cols[i].info(f"当前：{step}")
                else:
                    cols[i].caption(step)

            st.markdown("---")

            b1, b2 = st.columns(2)

            with b1:
                if st.button("进入生产过程录入", key=f"go_process_entry_from_schedule_{selected_schedule_id}"):
                    st.session_state["_jump_to_page"] = "生产过程录入"
                    st.session_state["selected_process_batch_id"] = int(selected_sch["production_batch_id"])
                    st.rerun()

            with b2:
                if st.button("查看半成品仓库", key=f"go_semi_finished_from_schedule_{selected_schedule_id}"):
                    st.session_state["_jump_to_page"] = "半成品仓库看板"
                    st.rerun()

            st.markdown("---")
            st.subheader("当前排程相关明细")
            show_df(pd.DataFrame([selected_sch]), hide_index=True)

    # =========================
    # 3. 当前排产明细
    # 显示全部排产历史
    # =========================
    with tab_detail:
        st.subheader("当前排产明细")

        detail_df = pd.read_sql_query("""
            SELECT
                ps.production_schedule_id,
                ps.delivery_plan_id,
                ps.production_batch_id,
                pb.batch_code,
                c.customer_name,
                oi.po_no,
                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                dp.planned_delivery_date,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                COALESCE(pb.required_production_qty, 0) AS required_production_qty,
                COALESCE(pb.actual_qty, 0) AS actual_qty,
                COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
                COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
                COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,
                pb.common_gauge_size,
                pb.stop_gauge_size,

                pm.quality_status,
                pm.release_status,
                COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
                COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
                COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,
                pm.inspected_at,
                pm.release_by,

                il.lot_code,
                il.location,
                il.available_qty
            FROM production_schedule ps
            JOIN production_batch pb
                ON ps.production_batch_id = pb.production_batch_id
            LEFT JOIN delivery_plan dp
                ON ps.delivery_plan_id = dp.delivery_plan_id
            LEFT JOIN order_item oi
                ON ps.order_item_id = oi.order_item_id
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            LEFT JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_measurement pm
                ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il
                ON pb.production_batch_id = il.production_batch_id
            ORDER BY
                CASE COALESCE(dp.delivery_status, '未排产')
                    WHEN '待生产确认' THEN 1
                    WHEN '已排产' THEN 2
                    WHEN '生产中' THEN 3
                    WHEN '质检中' THEN 4
                    WHEN '待入库确认' THEN 5
                    WHEN '已入库' THEN 6
                    WHEN '已出货' THEN 7
                    ELSE 99
                END,
                ps.production_schedule_id DESC
        """, conn)

        if detail_df.empty:
            st.info("当前没有排产明细。")
        else:
            show_df(detail_df.rename(columns={
                "production_schedule_id": "排程编号",
                "delivery_plan_id": "交付计划编号",
                "production_batch_id": "生产批次编号",
                "batch_code": "生产批号",
                "customer_name": "客户",
                "po_no": "PO",
                "delivery_batch_no": "交付批次",
                "planned_delivery_date": "计划交付日期",
                "planned_delivery_qty": "计划交付数量",
                "actual_delivery_qty": "实际交付数量",
                "delivery_status": "交付状态",
                "required_production_qty": "应生产数量",
                "actual_qty": "实际生产数量",
                "semi_finished_wh_qty": "半成品数量",
                "finished_wh_qty": "成品数量",
                "production_flow_status": "生产状态",
                "common_gauge_size": "通规尺寸",
                "stop_gauge_size": "止规尺寸",
                "quality_status": "质量等级",
                "release_status": "放行状态",
                "qc_before_qty": "检测前数量",
                "qc_after_qty": "检测后数量",
                "qc_loss_qty": "检测损耗数量",
                "inspected_at": "检测时间",
                "release_by": "放行人",
                "lot_code": "Lot号",
                "location": "库位",
                "available_qty": "可用库存"
            }), hide_index=True)




# =========================
# 覆盖版：仓储总看板负责入库确认，库存页面只负责库存查看
# =========================

def render_inbound_confirm_section(conn, section_key_prefix="warehouse_overview"):
    """
    入库确认公共区块。
    现在放在仓储总看板中使用。
    逻辑：
    - 只显示 release_status = released 且尚未入库 / 待入库确认的生产批次
    - 确认后调用 confirm_batch_inbound_to_inventory()
    - 自动分类入库：WH-ORDER / WH-SPEC
    """

    st.subheader("入库确认")

    inbound_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,

            ps.production_schedule_id,
            ps.delivery_plan_id,

            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS special_process,
            COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material,

            pm.quality_status,
            pm.release_status,

            il.inventory_lot_id,
            il.lot_code,
            il.location,
            il.available_qty,
            il.lot_status,
            il.release_status AS lot_release_status
        FROM production_batch pb
        JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        WHERE lower(COALESCE(pm.release_status, 'pending')) = 'released'
          AND (
                il.inventory_lot_id IS NULL
                OR COALESCE(dp.delivery_status, '') = '待入库确认'
              )
        ORDER BY ps.production_schedule_id DESC
    """, conn)

    if inbound_df.empty:
        st.success("当前没有待入库确认的批次。")
        return

    st.info(
        "这里负责正式入库确认。系统会自动分类："
        "计划交付数量以内进入 WH-ORDER；超过计划交付数量的部分进入 WH-SPEC。"
    )

    show_df(inbound_df.rename(columns={
        "production_batch_id": "生产批次编号",
        "batch_code": "生产批号",
        "actual_qty": "实际生产数量",
        "required_production_qty": "应生产数量",
        "delivery_batch_no": "交付批次",
        "planned_delivery_qty": "计划交付数量",
        "actual_delivery_qty": "已交付数量",
        "delivery_status": "交付状态",
        "customer_name": "客户",
        "po_no": "PO",
        "customer_pn": "客户料号",
        "product_type_text": "产品",
        "product_spec_text": "规格",
        "special_process": "特殊工艺",
        "material": "材质",
        "quality_status": "质量等级",
        "release_status": "放行状态",
        "lot_code": "Lot号",
        "location": "当前库位",
        "available_qty": "当前库存数量"
    }), hide_index=True)

    st.markdown("---")

    default_batch_id = st.session_state.get("selected_inbound_batch_id", None)
    inbound_batch_ids = [int(x) for x in inbound_df["production_batch_id"].tolist()]

    default_index = 0
    if default_batch_id in inbound_batch_ids:
        default_index = inbound_batch_ids.index(default_batch_id)

    selected_batch_id = st.selectbox(
        "选择待入库批次",
        inbound_batch_ids,
        index=default_index,
        format_func=lambda x: (
            f"{x} | "
            f"{inbound_df.loc[inbound_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
            f"PO {inbound_df.loc[inbound_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
            f"实际生产 {float(inbound_df.loc[inbound_df['production_batch_id'] == x, 'actual_qty'].iloc[0]):.0f} | "
            f"计划交付 {float(inbound_df.loc[inbound_df['production_batch_id'] == x, 'planned_delivery_qty'].iloc[0]):.0f}"
        ),
        key=f"{section_key_prefix}_inbound_batch_select"
    )

    selected = inbound_df[inbound_df["production_batch_id"] == selected_batch_id].iloc[0]

    actual_qty = float(selected["actual_qty"] or 0)
    planned_delivery_qty = float(selected["planned_delivery_qty"] or 0)
    order_inbound_qty = min(actual_qty, planned_delivery_qty)
    spec_inbound_qty = max(actual_qty - planned_delivery_qty, 0)

    st.markdown("### 入库确认卡片")

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("生产批号", str(selected["batch_code"]))
    i2.metric("PO", str(selected["po_no"]))
    i3.metric("实际生产数量", f"{actual_qty:.0f}")
    i4.metric("交付状态", str(selected["delivery_status"]))

    i5, i6, i7, i8 = st.columns(4)
    i5.metric("产品", str(selected["product_type_text"]))
    i6.metric("规格", str(selected["product_spec_text"]))
    i7.metric("质量等级", str(selected["quality_status"]))
    i8.metric("放行状态", str(selected["release_status"]))

    st.markdown("### 自动分类结果预览")

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("计划交付数量", f"{planned_delivery_qty:.0f}")
    p2.metric("应生产数量", f"{float(selected['required_production_qty'] or 0):.0f}")
    p3.metric("订单库存 WH-ORDER", f"{order_inbound_qty:.0f}")
    p4.metric("规格化库存 WH-SPEC", f"{spec_inbound_qty:.0f}")

    if actual_qty < planned_delivery_qty:
        st.warning(
            f"实际生产数量 {actual_qty:.0f} 小于计划交付数量 {planned_delivery_qty:.0f}，"
            "本次只能入订单库存，后续出货可能库存不足。"
        )
    elif spec_inbound_qty > 0:
        st.success(
            f"实际生产数量超过计划交付数量，超出 {spec_inbound_qty:.0f} 将自动进入规格化库存 WH-SPEC。"
        )
    else:
        st.info("实际生产数量等于计划交付数量，全部进入订单库存 WH-ORDER。")

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    with st.form(f"{section_key_prefix}_inbound_confirm_form"):
        confirmed_by = st.text_input(
            "入库确认人",
            value="Warehouse User",
            key=f"{section_key_prefix}_inbound_confirmed_by"
        )

        final_check = st.checkbox(
            "我已核对生产批号、PO、交付批次、质量放行状态和入库数量，确认可以入库。",
            key=f"{section_key_prefix}_inbound_final_check"
        )

        submitted = st.form_submit_button("确认入库并同步仓储数据")

    if submitted:
        if not final_check:
            st.error("请先勾选入库确认。")
            return

        ok, msg = confirm_batch_inbound_to_inventory(
            conn=conn,
            production_batch_id=int(selected_batch_id),
            confirmed_by=confirmed_by
        )

        if ok:
            st.success(msg)
            if "selected_inbound_batch_id" in st.session_state:
                del st.session_state["selected_inbound_batch_id"]
            st.rerun()
        else:
            st.error(msg)


def page_inventory_overview(conn):
    st.header("仓储｜仓储总看板")

    st.info(
        "仓储总看板现在负责：库存总览、入库确认、订单库存、规格化库存、库存流水。"
        "入库确认后，库存看板和出货管理会同步看到最新库存。"
    )

    stock_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.lot_code,
            il.production_batch_id,
            il.product_id,
            il.spec_id,
            il.trace_key,
            il.location,
            COALESCE(il.available_qty, 0) AS available_qty,
            COALESCE(il.reserved_qty, 0) AS reserved_qty,
            COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0) AS lot_total_qty,
            il.lot_status,
            il.release_status,
            il.exclusive_customer,
            il.forbidden_customer,
            il.last_out_qty,
            il.last_out_time,
            ps.spec_code,
            ps.outer_diameter_mm,
            ps.wall_thickness_mm,
            ps.length_mm,
            p.product_name,
            CASE
                WHEN il.location = 'WH-ORDER' THEN '订单库存'
                WHEN il.location = 'WH-SPEC' THEN '规格化库存'
                WHEN il.trace_key LIKE 'SPEC_STOCK%' THEN '规格化库存'
                ELSE '其他库存'
            END AS stock_type
        FROM inventory_lot il
        LEFT JOIN product_spec ps
            ON il.spec_id = ps.spec_id
        LEFT JOIN product p
            ON il.product_id = p.product_id
        ORDER BY
            stock_type,
            ps.outer_diameter_mm ASC,
            ps.wall_thickness_mm ASC,
            ps.length_mm ASC,
            il.inventory_lot_id ASC
    """, conn)

    if stock_df.empty:
        order_stock_qty = 0
        spec_stock_qty = 0
        other_stock_qty = 0
        total_stock_qty = 0
    else:
        order_stock_qty = stock_df.loc[
            stock_df["stock_type"] == "订单库存",
            "lot_total_qty"
        ].sum()

        spec_stock_qty = stock_df.loc[
            stock_df["stock_type"] == "规格化库存",
            "lot_total_qty"
        ].sum()

        other_stock_qty = stock_df.loc[
            stock_df["stock_type"] == "其他库存",
            "lot_total_qty"
        ].sum()

        total_stock_qty = order_stock_qty + spec_stock_qty

    # 待入库数量
    wait_inbound_df = pd.read_sql_query("""
        SELECT
            COUNT(DISTINCT pb.production_batch_id) AS wait_inbound_batch_count,
            COALESCE(SUM(COALESCE(pb.actual_qty, 0)), 0) AS wait_inbound_qty
        FROM production_batch pb
        JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        WHERE lower(COALESCE(pm.release_status, 'pending')) = 'released'
          AND (
                il.inventory_lot_id IS NULL
                OR COALESCE(dp.delivery_status, '') = '待入库确认'
              )
    """, conn)

    wait_inbound_batch_count = int(wait_inbound_df.iloc[0]["wait_inbound_batch_count"] or 0)
    wait_inbound_qty = float(wait_inbound_df.iloc[0]["wait_inbound_qty"] or 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("总库存", f"{total_stock_qty:.0f}")
    c2.metric("订单库存", f"{order_stock_qty:.0f}")
    c3.metric("规格化库存", f"{spec_stock_qty:.0f}")
    c4.metric("待入库批次", f"{wait_inbound_batch_count}")
    c5.metric("待入库数量", f"{wait_inbound_qty:.0f}")

    st.caption("总库存口径：订单库存 WH-ORDER + 规格化库存 WH-SPEC；其他库存单独列示，不计入主口径。")

    st.markdown("---")

    tab_summary, tab_inbound, tab_order, tab_spec, tab_spec_adjust, tab_detail, tab_txn = st.tabs([
        "库存总览",
        "入库确认",
        "订单库存",
        "规格化库存",
        "规格化库存调整",
        "库存明细",
        "库存流水"
    ])

    with tab_summary:
        st.subheader("按规格汇总库存")

        spec_summary_df = pd.read_sql_query("""
            SELECT
                ps.spec_id,
                ps.spec_code,
                p.product_name,
                ps.outer_diameter_mm,
                ps.wall_thickness_mm,
                ps.length_mm,

                COALESCE(SUM(
                    CASE
                        WHEN il.location = 'WH-ORDER'
                        THEN COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0)
                        ELSE 0
                    END
                ), 0) AS order_stock_qty,

                COALESCE(SUM(
                    CASE
                        WHEN il.location = 'WH-SPEC'
                          OR il.trace_key LIKE 'SPEC_STOCK%'
                        THEN COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0)
                        ELSE 0
                    END
                ), 0) AS spec_stock_qty,

                COALESCE(SUM(
                    CASE
                        WHEN il.location IN ('WH-ORDER', 'WH-SPEC')
                          OR il.trace_key LIKE 'SPEC_STOCK%'
                        THEN COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0)
                        ELSE 0
                    END
                ), 0) AS total_stock_qty,

                COALESCE(SUM(il.available_qty), 0) AS available_stock_qty,
                COALESCE(SUM(il.reserved_qty), 0) AS reserved_stock_qty,

                COUNT(DISTINCT il.inventory_lot_id) AS lot_count

            FROM inventory_lot il
            LEFT JOIN product_spec ps
                ON il.spec_id = ps.spec_id
            LEFT JOIN product p
                ON il.product_id = p.product_id
            GROUP BY
                ps.spec_id,
                ps.spec_code,
                p.product_name,
                ps.outer_diameter_mm,
                ps.wall_thickness_mm,
                ps.length_mm
            ORDER BY
                ps.outer_diameter_mm ASC,
                ps.wall_thickness_mm ASC,
                ps.length_mm ASC,
                ps.spec_code ASC
        """, conn)

        if spec_summary_df.empty:
            st.info("当前没有库存汇总数据。")
        else:
            show_df(spec_summary_df, hide_index=True)

    with tab_inbound:
        render_inbound_confirm_section(
            conn,
            section_key_prefix="warehouse_overview"
        )

    with tab_order:
        st.subheader("订单库存 WH-ORDER")

        if stock_df.empty:
            st.info("当前没有订单库存。")
        else:
            order_df = stock_df[stock_df["stock_type"] == "订单库存"].copy()
            if order_df.empty:
                st.info("当前没有订单库存。")
            else:
                show_df(order_df, hide_index=True)

    with tab_spec:
        st.subheader("规格化库存 WH-SPEC")

        if stock_df.empty:
            st.info("当前没有规格化库存。")
        else:
            spec_df = stock_df[stock_df["stock_type"] == "规格化库存"].copy()
            if spec_df.empty:
                st.info("当前没有规格化库存。")
            else:
                show_df(spec_df, hide_index=True)
    with tab_spec_adjust:
         render_spec_inventory_adjust_section(
            conn,
            section_key_prefix="warehouse_overview"
         )

    with tab_detail:
        st.subheader("库存明细")

        if stock_df.empty:
            st.info("当前没有库存。")
        else:
            show_df(stock_df, hide_index=True)

    with tab_txn:
        st.subheader("库存流水")

        txn_df = pd.read_sql_query("""
            SELECT
                itl.txn_id,
                itl.inventory_lot_id,
                il.lot_code,
                il.location,
                il.trace_key,
                itl.txn_type,
                itl.qty,
                itl.txn_time,
                itl.txn_reason,
                itl.reference_no
            FROM inventory_transaction_log itl
            LEFT JOIN inventory_lot il
                ON itl.inventory_lot_id = il.inventory_lot_id
            ORDER BY itl.txn_id DESC
        """, conn)

        if txn_df.empty:
            st.info("当前没有库存流水。")
        else:
            show_df(txn_df, hide_index=True)


def page_inventory_lot(conn):
    st.header("库存")

    st.info(
        "库存页面现在只用于查看库存明细。"
        "正式入库请进入【仓储总看板 → 入库确认】。"
    )

    stock_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.lot_code,
            il.production_batch_id,
            il.product_id,
            il.spec_id,
            il.trace_key,
            il.location,
            COALESCE(il.available_qty, 0) AS available_qty,
            COALESCE(il.reserved_qty, 0) AS reserved_qty,
            COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0) AS lot_total_qty,
            il.lot_status,
            il.release_status,
            il.exclusive_customer,
            il.forbidden_customer,
            il.last_out_qty,
            il.last_out_time,
            ps.spec_code,
            p.product_name,
            CASE
                WHEN il.location = 'WH-ORDER' THEN '订单库存'
                WHEN il.location = 'WH-SPEC' THEN '规格化库存'
                WHEN il.trace_key LIKE 'SPEC_STOCK%' THEN '规格化库存'
                ELSE '其他库存'
            END AS stock_type
        FROM inventory_lot il
        LEFT JOIN product_spec ps
            ON il.spec_id = ps.spec_id
        LEFT JOIN product p
            ON il.product_id = p.product_id
        ORDER BY
            stock_type,
            il.inventory_lot_id
    """, conn)

    if stock_df.empty:
        order_stock_qty = 0
        spec_stock_qty = 0
        total_stock_qty = 0
    else:
        order_stock_qty = stock_df.loc[
            stock_df["stock_type"] == "订单库存",
            "lot_total_qty"
        ].sum()

        spec_stock_qty = stock_df.loc[
            stock_df["stock_type"] == "规格化库存",
            "lot_total_qty"
        ].sum()

        total_stock_qty = order_stock_qty + spec_stock_qty

    c1, c2, c3 = st.columns(3)
    c1.metric("总库存", f"{total_stock_qty:.0f}")
    c2.metric("订单库存", f"{order_stock_qty:.0f}")
    c3.metric("规格化库存", f"{spec_stock_qty:.0f}")

    st.markdown("---")

    tab_all, tab_order, tab_spec, tab_txn = st.tabs([
        "库存总览",
        "订单库存",
        "规格化库存",
        "库存流水"
    ])

    with tab_all:
        st.subheader("库存总览")
        if stock_df.empty:
            st.info("当前没有库存。")
        else:
            show_df(stock_df, hide_index=True)

    with tab_order:
        st.subheader("订单库存")
        if stock_df.empty:
            st.info("当前没有订单库存。")
        else:
            order_df = stock_df[stock_df["stock_type"] == "订单库存"].copy()
            if order_df.empty:
                st.info("当前没有订单库存。")
            else:
                show_df(order_df, hide_index=True)

    with tab_spec:
        st.subheader("规格化库存")
        if stock_df.empty:
            st.info("当前没有规格化库存。")
        else:
            spec_df = stock_df[stock_df["stock_type"] == "规格化库存"].copy()
            if spec_df.empty:
                st.info("当前没有规格化库存。")
            else:
                show_df(spec_df, hide_index=True)

    with tab_txn:
        st.subheader("库存流水")

        txn_df = pd.read_sql_query("""
            SELECT
                itl.txn_id,
                itl.inventory_lot_id,
                il.lot_code,
                il.location,
                il.trace_key,
                itl.txn_type,
                itl.qty,
                itl.txn_time,
                itl.txn_reason,
                itl.reference_no
            FROM inventory_transaction_log itl
            LEFT JOIN inventory_lot il
                ON itl.inventory_lot_id = il.inventory_lot_id
            ORDER BY itl.txn_id DESC
        """, conn)

        if txn_df.empty:
            st.info("当前没有库存流水。")
        else:
            show_df(txn_df, hide_index=True)

# =========================
# 规格化库存调整：非买卖原因增减库存
# =========================

def adjust_spec_inventory_lot(conn, inventory_lot_id, adjust_type, adjust_qty, adjust_reason, adjust_note, operator_name):
    """
    规格化库存调整窗口。

    适用范围：
    - 只允许调整 WH-SPEC / SPEC_STOCK 规格化库存
    - 不生成 shipment
    - 不生成 shipment_item
    - 只更新 inventory_lot
    - 写入 inventory_transaction_log

    调整类型：
    - 非买卖减少：盘点差异、破损报废、样品领用、内部测试、返工消耗等
    - 非买卖增加：盘点增加、退回入库、数量修正等
    """

    cursor = conn.cursor()

    lot_df = pd.read_sql_query("""
        SELECT
            inventory_lot_id,
            lot_code,
            production_batch_id,
            product_id,
            spec_id,
            trace_key,
            location,
            COALESCE(available_qty, 0) AS available_qty,
            COALESCE(reserved_qty, 0) AS reserved_qty,
            lot_status,
            release_status
        FROM inventory_lot
        WHERE inventory_lot_id = ?
    """, conn, params=[int(inventory_lot_id)])

    if lot_df.empty:
        return False, "未找到该规格化库存 Lot。"

    lot = lot_df.iloc[0]

    location = str(lot["location"] or "")
    trace_key = str(lot["trace_key"] or "")
    available_qty = float(lot["available_qty"] or 0)
    adjust_qty = float(adjust_qty)

    is_spec_stock = (
        location == "WH-SPEC"
        or trace_key.startswith("SPEC_STOCK")
    )

    if not is_spec_stock:
        return False, "该 Lot 不是规格化库存。这里只允许调整 WH-SPEC / SPEC_STOCK 库存。"

    if adjust_qty <= 0:
        return False, "调整数量必须大于 0。"

    adjust_reason = normalize_text(adjust_reason)
    adjust_note = normalize_text(adjust_note)
    operator_name = normalize_text(operator_name) or "Warehouse User"

    if adjust_type == "减少库存":
        if not adjust_reason:
            return False, "减少规格化库存时，必须填写减少原因。"

        if adjust_qty > available_qty:
            return False, f"减少数量不能大于当前可用库存。当前可用库存为 {available_qty:.0f}。"

        new_available_qty = available_qty - adjust_qty
        txn_type = "spec_adjust_out"
        txn_qty = adjust_qty
        txn_reason = f"规格化库存非买卖减少：{adjust_reason}"

    else:
        new_available_qty = available_qty + adjust_qty
        txn_type = "spec_adjust_in"
        txn_qty = adjust_qty
        txn_reason = f"规格化库存非买卖增加：{adjust_reason or '库存修正'}"

    if adjust_note:
        txn_reason = f"{txn_reason}；说明：{adjust_note}"

    txn_reason = f"{txn_reason}；操作人：{operator_name}"

    reference_no = f"SPEC-ADJ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute("""
        UPDATE inventory_lot
        SET available_qty = ?,
            lot_status = CASE
                WHEN ? <= 0 THEN 'empty'
                ELSE 'available'
            END,
            last_out_qty = CASE
                WHEN ? = 'spec_adjust_out' THEN ?
                ELSE last_out_qty
            END,
            last_out_time = CASE
                WHEN ? = 'spec_adjust_out' THEN datetime('now')
                ELSE last_out_time
            END
        WHERE inventory_lot_id = ?
    """, (
        float(new_available_qty),
        float(new_available_qty),
        txn_type,
        float(adjust_qty),
        txn_type,
        int(inventory_lot_id)
    ))

    cursor.execute("""
        INSERT INTO inventory_transaction_log (
            inventory_lot_id,
            txn_type,
            qty,
            txn_time,
            txn_reason,
            reference_no
        ) VALUES (?, ?, ?, datetime('now'), ?, ?)
    """, (
        int(inventory_lot_id),
        txn_type,
        float(txn_qty),
        txn_reason,
        reference_no
    ))

    conn.commit()

    return True, (
        f"规格化库存调整完成。"
        f"Lot {lot['lot_code']}：{available_qty:.0f} → {new_available_qty:.0f}。"
        f"流水号：{reference_no}"
    )


def render_spec_inventory_adjust_section(conn, section_key_prefix="warehouse_overview"):
    """
    仓储总看板中的规格化库存调整窗口。
    """

    st.subheader("规格化库存调整")

    st.warning(
        "这里只用于非买卖原因调整规格化库存，例如盘点差异、破损报废、样品领用、内部测试、返工消耗等。"
        "正式出货请走【出货管理】，不要在这里扣订单库存或出货库存。"
    )

    spec_lot_df = pd.read_sql_query("""
        SELECT
            il.inventory_lot_id,
            il.lot_code,
            il.production_batch_id,
            il.product_id,
            il.spec_id,
            il.trace_key,
            il.location,
            COALESCE(il.available_qty, 0) AS available_qty,
            COALESCE(il.reserved_qty, 0) AS reserved_qty,
            COALESCE(il.available_qty, 0) + COALESCE(il.reserved_qty, 0) AS lot_total_qty,
            il.lot_status,
            il.release_status,
            ps.spec_code,
            p.product_name,
            CASE
                WHEN il.location = 'WH-SPEC' THEN '规格化库存'
                WHEN il.trace_key LIKE 'SPEC_STOCK%' THEN '规格化库存'
                ELSE '其他'
            END AS stock_type
        FROM inventory_lot il
        LEFT JOIN product_spec ps
            ON il.spec_id = ps.spec_id
        LEFT JOIN product p
            ON il.product_id = p.product_id
        WHERE il.location = 'WH-SPEC'
           OR il.trace_key LIKE 'SPEC_STOCK%'
        ORDER BY
            ps.spec_code,
            il.inventory_lot_id
    """, conn)

    if spec_lot_df.empty:
        st.info("当前没有可调整的规格化库存。")
        return

    show_df(spec_lot_df.rename(columns={
        "inventory_lot_id": "Lot编号",
        "lot_code": "Lot号",
        "spec_code": "规格编码",
        "product_name": "产品",
        "location": "库位",
        "available_qty": "可用数量",
        "reserved_qty": "预留数量",
        "lot_total_qty": "库存合计",
        "lot_status": "Lot状态",
        "release_status": "放行状态",
        "trace_key": "规格化库存Trace Key"
    }), hide_index=True)

    st.markdown("---")

    selected_lot_id = st.selectbox(
        "选择要调整的规格化库存 Lot",
        spec_lot_df["inventory_lot_id"].tolist(),
        format_func=lambda x: (
            f"{x} | "
            f"{spec_lot_df.loc[spec_lot_df['inventory_lot_id'] == x, 'lot_code'].iloc[0]} | "
            f"{spec_lot_df.loc[spec_lot_df['inventory_lot_id'] == x, 'spec_code'].iloc[0]} | "
            f"可用 {float(spec_lot_df.loc[spec_lot_df['inventory_lot_id'] == x, 'available_qty'].iloc[0]):.0f}"
        ),
        key=f"{section_key_prefix}_spec_adjust_lot_select"
    )

    selected = spec_lot_df[
        spec_lot_df["inventory_lot_id"] == selected_lot_id
    ].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lot号", str(selected["lot_code"]))
    c2.metric("规格", str(selected["spec_code"]))
    c3.metric("当前可用数量", f"{float(selected['available_qty'] or 0):.0f}")
    c4.metric("当前预留数量", f"{float(selected['reserved_qty'] or 0):.0f}")

    st.markdown("规格化库存 Trace Key")
    st.code(str(selected["trace_key"]))

    st.markdown("---")

    with st.form(f"{section_key_prefix}_spec_inventory_adjust_form"):
        adjust_type = st.radio(
            "调整类型",
            ["减少库存", "增加库存"],
            horizontal=True,
            key=f"{section_key_prefix}_spec_adjust_type"
        )

        adjust_qty = st.number_input(
            "调整数量",
            min_value=1.0,
            value=1.0,
            step=1.0,
            key=f"{section_key_prefix}_spec_adjust_qty"
        )

        if adjust_type == "减少库存":
            adjust_reason = st.selectbox(
                "减少原因",
                [
                    "盘点差异",
                    "破损/报废",
                    "样品领用",
                    "内部测试消耗",
                    "返工消耗",
                    "生产损耗补记",
                    "客户退样消耗",
                    "其他"
                ],
                key=f"{section_key_prefix}_spec_reduce_reason"
            )
        else:
            adjust_reason = st.selectbox(
                "增加原因",
                [
                    "盘点增加",
                    "退回入库",
                    "数量修正",
                    "历史库存补录",
                    "其他"
                ],
                key=f"{section_key_prefix}_spec_add_reason"
            )

        adjust_note = st.text_area(
            "说明",
            placeholder="请填写具体说明，例如：盘点少 20 支；实验室样品领用 5 支；破损报废 3 支等。",
            key=f"{section_key_prefix}_spec_adjust_note"
        )

        operator_name = st.text_input(
            "操作人",
            value="Warehouse User",
            key=f"{section_key_prefix}_spec_adjust_operator"
        )

        final_check = st.checkbox(
            "我确认这是非买卖原因的规格化库存调整，不属于正式出货。",
            key=f"{section_key_prefix}_spec_adjust_final_check"
        )

        submitted = st.form_submit_button("提交规格化库存调整")

    if submitted:
        if not final_check:
            st.error("请先勾选确认说明。")
            return

        ok, msg = adjust_spec_inventory_lot(
            conn=conn,
            inventory_lot_id=int(selected_lot_id),
            adjust_type=adjust_type,
            adjust_qty=float(adjust_qty),
            adjust_reason=adjust_reason,
            adjust_note=adjust_note,
            operator_name=operator_name
        )

        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


# =========================
# 半成品仓库：字段与流水表初始化
# =========================

def ensure_semi_finished_warehouse_schema(conn):
    """
    半成品仓库扩展：
    1. production_measurement 增加检测前数量、检测后数量、检测损耗数量、检测说明
    2. 新增 semi_finished_transaction_log 半成品仓库流水表
    """

    cursor = conn.cursor()

    pm_cols = pd.read_sql_query(
        "PRAGMA table_info(production_measurement)",
        conn
    )["name"].tolist()

    if "qc_before_qty" not in pm_cols:
        cursor.execute("""
            ALTER TABLE production_measurement
            ADD COLUMN qc_before_qty REAL DEFAULT 0
        """)

    if "qc_after_qty" not in pm_cols:
        cursor.execute("""
            ALTER TABLE production_measurement
            ADD COLUMN qc_after_qty REAL DEFAULT 0
        """)

    if "qc_loss_qty" not in pm_cols:
        cursor.execute("""
            ALTER TABLE production_measurement
            ADD COLUMN qc_loss_qty REAL DEFAULT 0
        """)

    if "qc_note" not in pm_cols:
        cursor.execute("""
            ALTER TABLE production_measurement
            ADD COLUMN qc_note TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semi_finished_transaction_log (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            production_batch_id INTEGER,
            batch_code TEXT,
            txn_type TEXT,
            qty_before REAL DEFAULT 0,
            qty_after REAL DEFAULT 0,
            qty_delta REAL DEFAULT 0,
            txn_reason TEXT,
            operator_name TEXT,
            txn_time TEXT DEFAULT CURRENT_TIMESTAMP,
            reference_no TEXT
        )
    """)

    conn.commit()


def record_semi_finished_txn(
    conn,
    production_batch_id,
    batch_code,
    txn_type,
    qty_before,
    qty_after,
    txn_reason,
    operator_name="System",
    reference_no=""
):
    """
    写入半成品仓库流水。
    """
    cursor = conn.cursor()

    qty_before = float(qty_before or 0)
    qty_after = float(qty_after or 0)
    qty_delta = qty_after - qty_before

    cursor.execute("""
        INSERT INTO semi_finished_transaction_log (
            production_batch_id,
            batch_code,
            txn_type,
            qty_before,
            qty_after,
            qty_delta,
            txn_reason,
            operator_name,
            reference_no
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(production_batch_id),
        str(batch_code),
        str(txn_type),
        float(qty_before),
        float(qty_after),
        float(qty_delta),
        str(txn_reason),
        str(operator_name),
        str(reference_no)
    ))

    conn.commit()

# =========================
# 半成品仓库看板
# =========================

def page_semi_finished_dashboard(conn):
    st.header("半成品仓库｜半成品仓库看板")

    st.info(
        "半成品仓库负责：生产完成后的半成品接收、质检放行、待入库确认。"
        "正式成品入库仍在【仓储总看板 → 入库确认】执行。"
    )

    tab_overview, tab_qc, tab_wait_inbound, tab_flow = st.tabs([
        "半成品看板",
        "质检放行",
        "待入库确认",
        "半成品流水"
    ])

    # =========================
    # 1. 半成品看板
    # =========================
    with tab_overview:
        st.subheader("半成品库存总览")

        overview_df = pd.read_sql_query("""
            SELECT
                pb.production_batch_id,
                pb.batch_code,
                pb.trace_key,
                COALESCE(pb.actual_qty, 0) AS actual_qty,
                COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
                COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
                COALESCE(dp.sales_need_production, 0) AS sales_need_production,
                COALESCE(dp.sales_need_semi_out, 0) AS sales_need_semi_out,
                dp.sales_decision_note,
                dp.sales_decision_time,
                pb.production_flow_status,
                pb.common_gauge_size,
                pb.stop_gauge_size,

                ps.delivery_plan_id,
                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                c.customer_name,
                oi.po_no,
                oi.product_type_text,
                oi.product_spec_text,
                COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS special_process,
                COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material,

                pm.quality_status,
                pm.release_status,
                COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
                COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
                COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,
                pm.inspected_at,
                pm.release_by
            FROM production_batch pb
            LEFT JOIN production_schedule ps
                ON pb.production_batch_id = ps.production_batch_id
            LEFT JOIN delivery_plan dp
                ON ps.delivery_plan_id = dp.delivery_plan_id
            LEFT JOIN order_item oi
                ON ps.order_item_id = oi.order_item_id
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            LEFT JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_measurement pm
                ON pb.production_batch_id = pm.production_batch_id
            WHERE COALESCE(pb.semi_finished_wh_qty, 0) > 0
               OR COALESCE(dp.delivery_status, '') IN ('质检中',
                                                       '待入库确认',
                                                       '半成品出库准备')
                OR COALESCE(dp.sales_need_semi_out, 0) = 1
            ORDER BY
                CASE COALESCE(dp.delivery_status, '未排产')
                    WHEN '质检中' THEN 1
                    WHEN '待入库确认' THEN 2
                    WHEN '半成品出库准备' THEN 3
                    ELSE 99
                END,
                pb.production_batch_id DESC
        """, conn)

        if overview_df.empty:
            st.info("当前没有半成品仓库数据。")
        else:
            total_semi_qty = pd.to_numeric(
                overview_df["semi_finished_wh_qty"],
                errors="coerce"
            ).fillna(0).sum()

            wait_qc_count = len(
                overview_df[overview_df["delivery_status"] == "质检中"]
            )

            wait_inbound_count = len(
                overview_df[overview_df["delivery_status"] == "待入库确认"]
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("半成品库存数量", f"{float(total_semi_qty):.0f}")
            c2.metric("待质检批次", wait_qc_count)
            c3.metric("待入库确认批次", wait_inbound_count)

            show_df(overview_df.rename(columns={
                "production_batch_id": "生产批次编号",
                "batch_code": "生产批号",
                "actual_qty": "生产实际数量",
                "semi_finished_wh_qty": "半成品库存",
                "finished_wh_qty": "成品库存",
                "production_flow_status": "生产状态",
                "common_gauge_size": "通规尺寸",
                "stop_gauge_size": "止规尺寸",
                "delivery_plan_id": "交付计划编号",
                "delivery_batch_no": "交付批次",
                "planned_delivery_qty": "计划交付数量",
                "delivery_status": "交付状态",
                "customer_name": "客户",
                "po_no": "PO",
                "product_type_text": "产品",
                "product_spec_text": "规格",
                "special_process": "特殊工艺",
                "material": "材质",
                "quality_status": "质量等级",
                "release_status": "放行状态",
                "qc_before_qty": "检测前数量",
                "qc_after_qty": "检测后数量",
                "qc_loss_qty": "检测损耗数量",
                "inspected_at": "检测时间",
                "release_by": "放行人"
            }), hide_index=True)

    # =========================
    # 2. 质检放行
    # =========================
    with tab_qc:
        st.subheader("质检放行")

        qc_df = pd.read_sql_query("""
            SELECT
                pb.production_batch_id,
                pb.batch_code,
                pb.trace_key,
                COALESCE(pb.actual_qty, 0) AS actual_qty,
                COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
                COALESCE(pb.required_production_qty, 0) AS required_production_qty,
                pb.common_gauge_size,
                pb.stop_gauge_size,
                pb.production_flow_status,

                ps.production_schedule_id,
                ps.delivery_plan_id,
                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                c.customer_name,
                oi.po_no,
                oi.product_type_text,
                oi.product_spec_text,
                COALESCE(oi.special_process, pb.special_process, 'STANDARD') AS special_process,
                COALESCE(oi.material, pb.material, 'UNKNOWN_MATERIAL') AS material,

                pm.measurement_id,
                COALESCE(pm.quality_status, 'Pending') AS quality_status,
                COALESCE(pm.release_status, 'pending') AS release_status,
                COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
                COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
                COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,
                pm.qc_note,
                pm.inspected_at,
                pm.release_by
            FROM production_batch pb
            JOIN production_schedule ps
                ON pb.production_batch_id = ps.production_batch_id
            LEFT JOIN delivery_plan dp
                ON ps.delivery_plan_id = dp.delivery_plan_id
            LEFT JOIN order_item oi
                ON ps.order_item_id = oi.order_item_id
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            LEFT JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_measurement pm
                ON pb.production_batch_id = pm.production_batch_id
            WHERE COALESCE(dp.delivery_status, '未排产') = '质检中'
            ORDER BY ps.production_schedule_id DESC
        """, conn)

        if qc_df.empty:
            st.info("当前没有处于【质检中】的半成品批次。")
        else:
            show_df(qc_df.rename(columns={
                "production_batch_id": "生产批次编号",
                "batch_code": "生产批号",
                "actual_qty": "生产实际数量",
                "semi_finished_wh_qty": "半成品数量",
                "required_production_qty": "应生产数量",
                "common_gauge_size": "通规尺寸",
                "stop_gauge_size": "止规尺寸",
                "delivery_batch_no": "交付批次",
                "planned_delivery_qty": "计划交付数量",
                "delivery_status": "交付状态",
                "customer_name": "客户",
                "po_no": "PO",
                "product_type_text": "产品",
                "product_spec_text": "规格",
                "quality_status": "质量等级",
                "release_status": "放行状态",
                "qc_before_qty": "检测前数量",
                "qc_after_qty": "检测后数量",
                "qc_loss_qty": "检测损耗数量"
            }), hide_index=True)

            qc_batch_ids = [int(x) for x in qc_df["production_batch_id"].tolist()]

            selected_batch_id = st.selectbox(
                "选择半成品批次进行质检放行",
                qc_batch_ids,
                format_func=lambda x: (
                    f"【{qc_df.loc[qc_df['production_batch_id'] == x, 'delivery_status'].iloc[0]}】 "
                    f"{qc_df.loc[qc_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
                    f"PO {qc_df.loc[qc_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
                    f"半成品 {float(qc_df.loc[qc_df['production_batch_id'] == x, 'semi_finished_wh_qty'].iloc[0] or 0):.0f} | "
                    f"计划交付 {float(qc_df.loc[qc_df['production_batch_id'] == x, 'planned_delivery_qty'].iloc[0] or 0):.0f}"
                ),
                key="semi_finished_qc_batch_select"
            )

            selected_qc = qc_df[
                qc_df["production_batch_id"] == selected_batch_id
            ].iloc[0]

            default_before_qty = float(
                selected_qc["semi_finished_wh_qty"]
                if float(selected_qc["semi_finished_wh_qty"] or 0) > 0
                else selected_qc["actual_qty"]
            )

            q1, q2, q3, q4 = st.columns(4)
            q1.metric("生产批号", str(selected_qc["batch_code"]))
            q2.metric("PO", str(selected_qc["po_no"]))
            q3.metric("半成品数量", f"{default_before_qty:.0f}")
            q4.metric("交付状态", str(selected_qc["delivery_status"]))

            q5, q6, q7, q8 = st.columns(4)
            q5.metric("通规尺寸", str(selected_qc["common_gauge_size"]) if pd.notna(selected_qc["common_gauge_size"]) else "-")
            q6.metric("止规尺寸", str(selected_qc["stop_gauge_size"]) if pd.notna(selected_qc["stop_gauge_size"]) else "-")
            q7.metric("当前质量等级", str(selected_qc["quality_status"]))
            q8.metric("当前放行状态", str(selected_qc["release_status"]))

            st.markdown("Trace Key")
            st.code(str(selected_qc["trace_key"]))

            with st.form("semi_finished_qc_release_form"):
                quality_options = ["A", "B", "C", "Pending", "NG"]
                release_options = ["released", "hold", "pending"]

                quality_status = st.selectbox(
                    "质量等级",
                    quality_options,
                    index=0,
                    key="semi_finished_quality_status"
                )

                release_status = st.selectbox(
                    "放行状态",
                    release_options,
                    index=0,
                    key="semi_finished_release_status"
                )

                qc_before_qty = st.number_input(
                    "检测前数量",
                    min_value=0.0,
                    value=float(default_before_qty),
                    step=1.0,
                    key="semi_finished_qc_before_qty"
                )

                qc_after_qty = st.number_input(
                    "检测后合格数量",
                    min_value=0.0,
                    value=float(default_before_qty),
                    step=1.0,
                    key="semi_finished_qc_after_qty"
                )

                qc_loss_qty = max(float(qc_before_qty) - float(qc_after_qty), 0.0)

                c_loss_1, c_loss_2, c_loss_3 = st.columns(3)
                c_loss_1.metric("检测前数量", f"{float(qc_before_qty):.0f}")
                c_loss_2.metric("检测后数量", f"{float(qc_after_qty):.0f}")
                c_loss_3.metric("检测损耗", f"{float(qc_loss_qty):.0f}")

                release_by = st.text_input(
                    "检验 / 放行人",
                    value="QC User",
                    key="semi_finished_release_by"
                )

                qc_note = st.text_area(
                    "检测说明",
                    placeholder="例如：外观不良 5 支，尺寸 NG 3 支，其余合格。",
                    key="semi_finished_qc_note"
                )

                final_check = st.checkbox(
                    "我已确认检测前数量、检测后数量、质量等级和放行状态。",
                    key="semi_finished_qc_final_check"
                )

                submitted = st.form_submit_button("提交质检放行")

            if submitted:
                if not final_check:
                    st.error("请先勾选确认。")
                    return

                ok, msg = update_batch_quality_release(
                    conn=conn,
                    production_batch_id=int(selected_batch_id),
                    quality_status=quality_status,
                    release_status=release_status,
                    release_by=release_by,
                    qc_before_qty=float(qc_before_qty),
                    qc_after_qty=float(qc_after_qty),
                    qc_note=qc_note
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # =========================
    # 3. 待入库确认
    # =========================
    with tab_wait_inbound:
        st.subheader("待入库确认")

        inbound_wait_df = pd.read_sql_query("""
            SELECT
                pb.production_batch_id,
                pb.batch_code,
                pb.trace_key,
                COALESCE(pb.actual_qty, 0) AS actual_qty,
                COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
                COALESCE(pb.required_production_qty, 0) AS required_production_qty,
                pb.common_gauge_size,
                pb.stop_gauge_size,

                ps.production_schedule_id,
                ps.delivery_plan_id,

                COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
                COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
                COALESCE(dp.delivery_status, '未排产') AS delivery_status,

                c.customer_name,
                oi.po_no,
                oi.product_type_text,
                oi.product_spec_text,

                pm.quality_status,
                pm.release_status,
                COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
                COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
                COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,

                il.inventory_lot_id,
                il.lot_code,
                il.location,
                il.available_qty
            FROM production_batch pb
            JOIN production_schedule ps
                ON pb.production_batch_id = ps.production_batch_id
            LEFT JOIN delivery_plan dp
                ON ps.delivery_plan_id = dp.delivery_plan_id
            LEFT JOIN order_item oi
                ON ps.order_item_id = oi.order_item_id
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            LEFT JOIN customer c
                ON o.customer_id = c.customer_id
            LEFT JOIN production_measurement pm
                ON pb.production_batch_id = pm.production_batch_id
            LEFT JOIN inventory_lot il
                ON pb.production_batch_id = il.production_batch_id
            WHERE lower(COALESCE(pm.release_status, 'pending')) = 'released'
              AND (
                    COALESCE(dp.delivery_status, '') = '待入库确认'
                    OR il.inventory_lot_id IS NULL
                  )
            ORDER BY ps.production_schedule_id DESC
        """, conn)

        if inbound_wait_df.empty:
            st.success("当前没有待入库确认的半成品批次。")
        else:
            show_df(inbound_wait_df.rename(columns={
                "production_batch_id": "生产批次编号",
                "batch_code": "生产批号",
                "actual_qty": "检测后合格数量",
                "semi_finished_wh_qty": "半成品数量",
                "required_production_qty": "应生产数量",
                "common_gauge_size": "通规尺寸",
                "stop_gauge_size": "止规尺寸",
                "delivery_plan_id": "交付计划编号",
                "delivery_batch_no": "交付批次",
                "planned_delivery_qty": "计划交付数量",
                "delivery_status": "交付状态",
                "customer_name": "客户",
                "po_no": "PO",
                "product_type_text": "产品",
                "product_spec_text": "规格",
                "quality_status": "质量等级",
                "release_status": "放行状态",
                "qc_before_qty": "检测前数量",
                "qc_after_qty": "检测后数量",
                "qc_loss_qty": "检测损耗数量",
                "lot_code": "Lot号",
                "location": "库位",
                "available_qty": "可用库存"
            }), hide_index=True)

            selected_inbound_batch_id = st.selectbox(
                "选择半成品批次查看待入库信息",
                inbound_wait_df["production_batch_id"].tolist(),
                format_func=lambda x: (
                    f"【{inbound_wait_df.loc[inbound_wait_df['production_batch_id'] == x, 'delivery_status'].iloc[0]}】 "
                    f"{inbound_wait_df.loc[inbound_wait_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
                    f"PO {inbound_wait_df.loc[inbound_wait_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
                    f"检测后 {float(inbound_wait_df.loc[inbound_wait_df['production_batch_id'] == x, 'qc_after_qty'].iloc[0] or 0):.0f} | "
                    f"计划交付 {float(inbound_wait_df.loc[inbound_wait_df['production_batch_id'] == x, 'planned_delivery_qty'].iloc[0] or 0):.0f}"
                ),
                key="semi_finished_wait_inbound_select"
            )

            selected_ib = inbound_wait_df[
                inbound_wait_df["production_batch_id"] == selected_inbound_batch_id
            ].iloc[0]

            i1, i2, i3, i4 = st.columns(4)
            i1.metric("生产批号", str(selected_ib["batch_code"]))
            i2.metric("PO", str(selected_ib["po_no"]))
            i3.metric("检测后合格数量", f"{float(selected_ib['qc_after_qty'] or selected_ib['actual_qty'] or 0):.0f}")
            i4.metric("交付状态", str(selected_ib["delivery_status"]))

            i5, i6, i7, i8 = st.columns(4)
            i5.metric("检测前数量", f"{float(selected_ib['qc_before_qty'] or 0):.0f}")
            i6.metric("检测损耗", f"{float(selected_ib['qc_loss_qty'] or 0):.0f}")
            i7.metric("通规尺寸", str(selected_ib["common_gauge_size"]) if pd.notna(selected_ib["common_gauge_size"]) else "-")
            i8.metric("止规尺寸", str(selected_ib["stop_gauge_size"]) if pd.notna(selected_ib["stop_gauge_size"]) else "-")

            st.info("正式成品入库请进入【仓储总看板 → 入库确认】。")

            if st.button("跳转到仓储总看板入库确认", key=f"go_inventory_overview_inbound_from_sf_{selected_inbound_batch_id}"):
                st.session_state["_jump_to_page"] = "仓储总看板"
                st.session_state["selected_inbound_batch_id"] = int(selected_inbound_batch_id)
                st.rerun()

    # =========================
    # 4. 半成品流水
    # =========================
    with tab_flow:
        st.subheader("半成品仓库流水")

        txn_df = pd.read_sql_query("""
            SELECT
                txn_id,
                production_batch_id,
                batch_code,
                txn_type,
                qty_before,
                qty_after,
                qty_delta,
                txn_reason,
                operator_name,
                txn_time,
                reference_no
            FROM semi_finished_transaction_log
            ORDER BY txn_id DESC
        """, conn)

        if txn_df.empty:
            st.info("当前没有半成品仓库流水。")
        else:
            show_df(txn_df.rename(columns={
                "txn_id": "流水编号",
                "production_batch_id": "生产批次编号",
                "batch_code": "生产批号",
                "txn_type": "流水类型",
                "qty_before": "变动前数量",
                "qty_after": "变动后数量",
                "qty_delta": "变动数量",
                "txn_reason": "原因",
                "operator_name": "操作人",
                "txn_time": "时间",
                "reference_no": "参考号"
            }), hide_index=True)


# =========================
# 半成品仓库录入
# =========================

def page_semi_finished_entry(conn):
    st.header("半成品仓库｜半成品仓库录入")

    st.info(
        "这里用于半成品库存手动修正，例如盘点差异、待检数量修正、异常冻结等。"
        "正常生产完成进入半成品仓库会由 Packing done 自动触发。"
    )

    batch_df = pd.read_sql_query("""
        SELECT
            pb.production_batch_id,
            pb.batch_code,
            pb.trace_key,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            pb.production_flow_status,

            ps.delivery_plan_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,

            c.customer_name,
            oi.po_no,
            oi.product_type_text,
            oi.product_spec_text
        FROM production_batch pb
        LEFT JOIN production_schedule ps
            ON pb.production_batch_id = ps.production_batch_id
        LEFT JOIN delivery_plan dp
            ON ps.delivery_plan_id = dp.delivery_plan_id
        LEFT JOIN order_item oi
            ON ps.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        ORDER BY pb.production_batch_id DESC
    """, conn)

    if batch_df.empty:
        st.info("当前没有生产批次。")
        return

    show_df(batch_df.rename(columns={
        "production_batch_id": "生产批次编号",
        "batch_code": "生产批号",
        "actual_qty": "实际生产数量",
        "semi_finished_wh_qty": "半成品数量",
        "production_flow_status": "生产状态",
        "delivery_status": "交付状态",
        "customer_name": "客户",
        "po_no": "PO",
        "product_type_text": "产品",
        "product_spec_text": "规格"
    }), hide_index=True)

    st.markdown("---")

    batch_ids = [int(x) for x in batch_df["production_batch_id"].tolist()]

    selected_batch_id = st.selectbox(
        "选择要调整的半成品批次",
        batch_ids,
        format_func=lambda x: (
            f"{batch_df.loc[batch_df['production_batch_id'] == x, 'batch_code'].iloc[0]} | "
            f"PO {batch_df.loc[batch_df['production_batch_id'] == x, 'po_no'].iloc[0]} | "
            f"半成品 {float(batch_df.loc[batch_df['production_batch_id'] == x, 'semi_finished_wh_qty'].iloc[0] or 0):.0f} | "
            f"状态 {batch_df.loc[batch_df['production_batch_id'] == x, 'delivery_status'].iloc[0]}"
        ),
        key="semi_finished_entry_batch_select"
    )

    selected = batch_df[
        batch_df["production_batch_id"] == selected_batch_id
    ].iloc[0]

    old_qty = float(selected["semi_finished_wh_qty"] or 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("生产批号", str(selected["batch_code"]))
    c2.metric("PO", str(selected["po_no"]))
    c3.metric("当前半成品数量", f"{old_qty:.0f}")
    c4.metric("交付状态", str(selected["delivery_status"]))

    st.markdown("Trace Key")
    st.code(str(selected["trace_key"]))

    with st.form("semi_finished_manual_entry_form"):
        new_qty = st.number_input(
            "调整后的半成品数量",
            min_value=0.0,
            value=float(old_qty),
            step=1.0,
            key="semi_finished_new_qty"
        )

        adjust_reason = st.selectbox(
            "调整原因",
            [
                "盘点修正",
                "检测前数量修正",
                "异常冻结",
                "返工转出",
                "返工转入",
                "其他"
            ],
            key="semi_finished_adjust_reason"
        )

        adjust_note = st.text_area(
            "说明",
            placeholder="例如：盘点少 10 支；返工转出 20 支；检测前数量修正等。",
            key="semi_finished_adjust_note"
        )

        operator_name = st.text_input(
            "操作人",
            value="Warehouse User",
            key="semi_finished_adjust_operator"
        )

        final_check = st.checkbox(
            "我确认这是半成品仓库数量调整，不是正式成品入库。",
            key="semi_finished_adjust_final_check"
        )

        submitted = st.form_submit_button("提交半成品数量调整")

    if submitted:
        if not final_check:
            st.error("请先勾选确认。")
            return

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE production_batch
            SET semi_finished_wh_qty = ?
            WHERE production_batch_id = ?
        """, (
            float(new_qty),
            int(selected_batch_id)
        ))

        conn.commit()

        record_semi_finished_txn(
            conn=conn,
            production_batch_id=int(selected_batch_id),
            batch_code=str(selected["batch_code"]),
            txn_type="manual_adjust",
            qty_before=float(old_qty),
            qty_after=float(new_qty),
            txn_reason=f"{adjust_reason}；{adjust_note}",
            operator_name=operator_name,
            reference_no=str(selected["batch_code"])
        )
        # =========================
        # 半成品数量调整后，统一同步对应交付批次 / 订单状态
        # =========================
        dp_df = pd.read_sql_query("""
           SELECT delivery_plan_id
           FROM production_schedule
           WHERE production_batch_id = ?
           ORDER BY production_schedule_id DESC
           LIMIT 1
        """, conn, params=[int(selected_batch_id)])

        if not dp_df.empty and pd.notna(dp_df.iloc[0]["delivery_plan_id"]):
             if "sync_after_delivery_plan_change" in globals():
                 sync_after_delivery_plan_change(
                     conn,
                     int(dp_df.iloc[0]["delivery_plan_id"])
                )

        st.success(f"半成品数量已调整：{old_qty:.0f} → {float(new_qty):.0f}，相关交付批次已同步。")
        st.rerun()



# =========================
# 销售决策同步字段
# =========================

def ensure_sales_decision_schema(conn):
    """
    销售看板扩展字段：
    - sales_need_production：是否需要生产端处理
    - sales_need_semi_out：是否需要半成品仓库处理
    - sales_decision_note：销售处理说明
    - sales_decision_time：销售处理时间
    """

    cursor = conn.cursor()

    cols = pd.read_sql_query(
        "PRAGMA table_info(delivery_plan)",
        conn
    )["name"].tolist()

    if "sales_need_production" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_need_production INTEGER DEFAULT 0
        """)

    if "sales_need_semi_out" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_need_semi_out INTEGER DEFAULT 0
        """)

    if "sales_decision_note" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_decision_note TEXT
        """)

    if "sales_decision_time" not in cols:
        cursor.execute("""
            ALTER TABLE delivery_plan
            ADD COLUMN sales_decision_time TEXT
        """)

    conn.commit()

def clear_sales_decision_after_shipment(conn, delivery_plan_id):
    """
    出货完成后清理销售侧处理指令。
    """
    ensure_sales_decision_schema(conn)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE delivery_plan
        SET sales_need_production = 0,
            sales_need_semi_out = 0,
            sales_decision_note = COALESCE(sales_decision_note, '') || '；出货完成，销售指令已关闭',
            sales_decision_time = datetime('now')
        WHERE delivery_plan_id = ?
          AND COALESCE(delivery_status, '') IN (
              '已出货',
              '部分出货'
          )
    """, (
        int(delivery_plan_id),
    ))

    conn.commit()

# =========================
# 异常处理 / 流程回退模块
# =========================

def ensure_correction_schema(conn):
    """
    初始化异常处理 / 流程回退日志表。
    所有回退都必须写日志，不建议静默删除。
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correction_log (
            correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            correction_type TEXT,
            target_type TEXT,
            delivery_plan_id INTEGER,
            production_batch_id INTEGER,
            production_schedule_id INTEGER,
            order_item_id INTEGER,
            old_status TEXT,
            new_status TEXT,
            old_qty REAL DEFAULT 0,
            new_qty REAL DEFAULT 0,
            correction_reason TEXT,
            operator_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def record_correction_log(
    conn,
    correction_type,
    target_type,
    delivery_plan_id=None,
    production_batch_id=None,
    production_schedule_id=None,
    order_item_id=None,
    old_status="",
    new_status="",
    old_qty=0,
    new_qty=0,
    correction_reason="",
    operator_name="System"
):
    """
    写入流程回退日志。
    """
    ensure_correction_schema(conn)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO correction_log (
            correction_type,
            target_type,
            delivery_plan_id,
            production_batch_id,
            production_schedule_id,
            order_item_id,
            old_status,
            new_status,
            old_qty,
            new_qty,
            correction_reason,
            operator_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(correction_type),
        str(target_type),
        int(delivery_plan_id) if delivery_plan_id is not None and pd.notna(delivery_plan_id) else None,
        int(production_batch_id) if production_batch_id is not None and pd.notna(production_batch_id) else None,
        int(production_schedule_id) if production_schedule_id is not None and pd.notna(production_schedule_id) else None,
        int(order_item_id) if order_item_id is not None and pd.notna(order_item_id) else None,
        str(old_status),
        str(new_status),
        float(old_qty or 0),
        float(new_qty or 0),
        str(correction_reason),
        str(operator_name)
    ))

    conn.commit()


def get_exception_flow_records(conn):
    """
    获取可回退对象。
    以 delivery_plan 为主线，关联排产、生产批次、质检、库存。
    """
    df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_batch_no, 1) AS delivery_batch_no,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            COALESCE(dp.planned_delivery_qty, 0) AS planned_delivery_qty,
            COALESCE(dp.actual_delivery_qty, 0) AS actual_delivery_qty,
            COALESCE(dp.sales_need_production, 0) AS sales_need_production,
            COALESCE(dp.sales_need_semi_out, 0) AS sales_need_semi_out,
            dp.sales_decision_note,
            dp.sales_decision_time,

            ps.production_schedule_id,
            ps.production_batch_id,

            pb.batch_code,
            COALESCE(pb.required_production_qty, 0) AS required_production_qty,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            COALESCE(pb.finished_wh_qty, 0) AS finished_wh_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,

            pm.measurement_id,
            COALESCE(pm.quality_status, 'Pending') AS quality_status,
            COALESCE(pm.release_status, 'pending') AS release_status,
            COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
            COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
            COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,

            il.inventory_lot_id,
            il.lot_code,
            COALESCE(il.available_qty, 0) AS available_qty,

            c.customer_name,
            oi.po_no,
            oi.customer_pn,
            oi.product_type_text,
            oi.product_spec_text,
            oi.trace_key
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        LEFT JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        LEFT JOIN order_item oi
            ON dp.order_item_id = oi.order_item_id
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        LEFT JOIN customer c
            ON o.customer_id = c.customer_id
        ORDER BY dp.delivery_plan_id DESC
    """, conn)

    return df


def rollback_delivery_to_sales(conn, delivery_plan_id, reason, operator_name):
    """
    回退 1：
    待生产确认 / 半成品出库准备 → 未排产

    适用：
    - 销售判断错了
    - 需要重新回到销售看板判断
    - 尚未创建 production_schedule
    """
    ensure_correction_schema(conn)

    dp_df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            COALESCE(dp.sales_need_production, 0) AS sales_need_production,
            COALESCE(dp.sales_need_semi_out, 0) AS sales_need_semi_out,
            ps.production_schedule_id
        FROM delivery_plan dp
        LEFT JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if dp_df.empty:
        return False, "未找到交付批次。"

    row = dp_df.iloc[0]
    old_status = str(row["delivery_status"])

    if pd.notna(row["production_schedule_id"]):
        return False, "该交付批次已经存在排产记录，不能直接退回销售判断。请使用【已排产 → 待生产确认】。"

    if old_status not in ["待生产确认", "半成品出库准备", "未排产", "发货准备"]:
        return False, f"当前状态为【{old_status}】，不适合退回销售判断。"

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '未排产',
            sales_need_production = 0,
            sales_need_semi_out = 0,
            sales_decision_note = COALESCE(sales_decision_note, '') || '；异常回退：退回销售判断',
            sales_decision_time = datetime('now')
        WHERE delivery_plan_id = ?
    """, (
        int(delivery_plan_id),
    ))

    conn.commit()

    record_correction_log(
        conn=conn,
        correction_type="退回销售判断",
        target_type="delivery_plan",
        delivery_plan_id=int(delivery_plan_id),
        order_item_id=int(row["order_item_id"]),
        old_status=old_status,
        new_status="未排产",
        correction_reason=reason,
        operator_name=operator_name
    )

    if "sync_after_delivery_plan_change" in globals():
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    return True, f"交付批次 {delivery_plan_id} 已退回【未排产】，可回到销售看板重新判断。"


def rollback_schedule_to_pending(conn, delivery_plan_id, reason, operator_name):
    """
    回退 2：
    已排产 → 待生产确认

    适用：
    - 生产批号、通规、止规、应生产数量录错
    - 还没有生产工序记录
    - 还没有质检 / 入库记录

    处理：
    - 删除 production_schedule
    - 删除 production_batch
    - delivery_plan 回到 待生产确认
    - sales_need_production = 1
    """
    ensure_correction_schema(conn)

    df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status,

            COUNT(DISTINCT ppl.process_log_id) AS process_count,
            COUNT(DISTINCT pm.measurement_id) AS measurement_count,
            COUNT(DISTINCT il.inventory_lot_id) AS lot_count
        FROM delivery_plan dp
        JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        LEFT JOIN production_process_log ppl
            ON pb.production_batch_id = ppl.production_batch_id
        LEFT JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        WHERE dp.delivery_plan_id = ?
        GROUP BY
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.actual_qty,
            pb.production_flow_status
    """, conn, params=[int(delivery_plan_id)])

    if df.empty:
        return False, "未找到已排产记录。"

    row = df.iloc[0]

    old_status = str(row["delivery_status"])
    production_batch_id = int(row["production_batch_id"])
    production_schedule_id = int(row["production_schedule_id"])

    if int(row["process_count"] or 0) > 0:
        return False, "该批次已经存在生产工序记录，不能直接取消排产。请使用【生产中 → 已排产】先回退工序。"

    if int(row["measurement_count"] or 0) > 0:
        return False, "该批次已经存在质检记录，不能直接取消排产。"

    if int(row["lot_count"] or 0) > 0:
        return False, "该批次已经存在库存 Lot，不能直接取消排产。"

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM production_schedule
        WHERE production_schedule_id = ?
    """, (
        int(production_schedule_id),
    ))

    cursor.execute("""
        DELETE FROM production_batch
        WHERE production_batch_id = ?
    """, (
        int(production_batch_id),
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '待生产确认',
            sales_need_production = 1,
            sales_decision_time = datetime('now')
        WHERE delivery_plan_id = ?
    """, (
        int(delivery_plan_id),
    ))

    conn.commit()

    record_correction_log(
        conn=conn,
        correction_type="取消排产",
        target_type="production_schedule",
        delivery_plan_id=int(delivery_plan_id),
        production_batch_id=int(production_batch_id),
        production_schedule_id=int(production_schedule_id),
        order_item_id=int(row["order_item_id"]),
        old_status=old_status,
        new_status="待生产确认",
        old_qty=float(row["actual_qty"] or 0),
        new_qty=0,
        correction_reason=reason,
        operator_name=operator_name
    )

    if "sync_after_delivery_plan_change" in globals():
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    return True, f"排产记录已取消，交付批次 {delivery_plan_id} 已回到【待生产确认】。"


def rollback_last_process_step(conn, delivery_plan_id, reason, operator_name):
    """
    回退 3：
    生产中 → 已排产

    第一版策略：
    - 只删除最后一条 production_process_log
    - 重新计算 production_batch.actual_qty
    - 如果没有任何工序记录了，则 delivery_plan = 已排产
    - 如果仍有工序记录，则 delivery_plan 保持 生产中
    """
    ensure_correction_schema(conn)

    df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.production_flow_status, 'planned') AS production_flow_status
        FROM delivery_plan dp
        JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        WHERE dp.delivery_plan_id = ?
    """, conn, params=[int(delivery_plan_id)])

    if df.empty:
        return False, "未找到该交付批次对应的生产批次。"

    base = df.iloc[0]
    production_batch_id = int(base["production_batch_id"])

    has_qc_df = pd.read_sql_query("""
        SELECT COUNT(*) AS cnt
        FROM production_measurement
        WHERE production_batch_id = ?
    """, conn, params=[int(production_batch_id)])

    if int(has_qc_df.iloc[0]["cnt"] or 0) > 0:
        return False, "该批次已经进入质检，不能用此功能回退生产工序。请先执行【待入库确认 → 质检中】或后续质检回退。"

    log_df = pd.read_sql_query("""
        SELECT
            process_log_id,
            process_step,
            process_status,
            input_qty,
            output_qty,
            scrap_qty
        FROM production_process_log
        WHERE production_batch_id = ?
        ORDER BY process_log_id DESC
        LIMIT 1
    """, conn, params=[int(production_batch_id)])

    if log_df.empty:
        return False, "当前批次没有生产工序记录，无需回退。"

    last_log = log_df.iloc[0]
    old_qty = float(base["actual_qty"] or 0)

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM production_process_log
        WHERE process_log_id = ?
    """, (
        int(last_log["process_log_id"]),
    ))

    remaining_df = pd.read_sql_query("""
        SELECT
            process_log_id,
            process_step,
            output_qty,
            process_status
        FROM production_process_log
        WHERE production_batch_id = ?
        ORDER BY process_log_id DESC
    """, conn, params=[int(production_batch_id)])

    if remaining_df.empty:
        new_actual_qty = 0.0
        new_flow_status = "planned"
        new_delivery_status = "已排产"
    else:
        latest = remaining_df.iloc[0]
        new_actual_qty = float(latest["output_qty"] or 0)
        new_flow_status = str(latest["process_step"])
        new_delivery_status = "生产中"

    cursor.execute("""
        UPDATE production_batch
        SET actual_qty = ?,
            production_flow_status = ?
        WHERE production_batch_id = ?
    """, (
        float(new_actual_qty),
        new_flow_status,
        int(production_batch_id)
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = ?
        WHERE delivery_plan_id = ?
    """, (
        new_delivery_status,
        int(delivery_plan_id)
    ))

    conn.commit()

    record_correction_log(
        conn=conn,
        correction_type="回退最后一道工序",
        target_type="production_process_log",
        delivery_plan_id=int(delivery_plan_id),
        production_batch_id=int(production_batch_id),
        production_schedule_id=int(base["production_schedule_id"]),
        order_item_id=int(base["order_item_id"]),
        old_status=str(base["delivery_status"]),
        new_status=new_delivery_status,
        old_qty=old_qty,
        new_qty=new_actual_qty,
        correction_reason=(
            f"{reason}；删除工序记录 {int(last_log['process_log_id'])} / "
            f"{last_log['process_step']} / {last_log['process_status']}"
        ),
        operator_name=operator_name
    )

    if "sync_after_delivery_plan_change" in globals():
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    return True, (
        f"已删除最后一条工序记录：{last_log['process_step']}。"
        f"当前交付状态已同步为【{new_delivery_status}】，实际数量更新为 {new_actual_qty:.0f}。"
    )


def rollback_qc_release_to_qc(conn, delivery_plan_id, reason, operator_name):
    """
    回退 4：
    待入库确认 → 质检中

    适用：
    - 质检放行录错
    - 检测后数量录错
    - 尚未正式入库

    处理：
    - production_measurement.release_status = pending
    - production_measurement.qc_after_qty = 0
    - production_measurement.qc_loss_qty = 0
    - delivery_plan.delivery_status = 质检中
    - production_batch.production_flow_status = qc_pending
    """
    ensure_correction_schema(conn)

    df = pd.read_sql_query("""
        SELECT
            dp.delivery_plan_id,
            dp.order_item_id,
            COALESCE(dp.delivery_status, '未排产') AS delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            COALESCE(pb.actual_qty, 0) AS actual_qty,
            COALESCE(pb.semi_finished_wh_qty, 0) AS semi_finished_wh_qty,
            pm.measurement_id,
            COALESCE(pm.release_status, 'pending') AS release_status,
            COALESCE(pm.qc_before_qty, 0) AS qc_before_qty,
            COALESCE(pm.qc_after_qty, 0) AS qc_after_qty,
            COALESCE(pm.qc_loss_qty, 0) AS qc_loss_qty,

            COUNT(DISTINCT il.inventory_lot_id) AS lot_count
        FROM delivery_plan dp
        JOIN production_schedule ps
            ON dp.delivery_plan_id = ps.delivery_plan_id
        JOIN production_batch pb
            ON ps.production_batch_id = pb.production_batch_id
        JOIN production_measurement pm
            ON pb.production_batch_id = pm.production_batch_id
        LEFT JOIN inventory_lot il
            ON pb.production_batch_id = il.production_batch_id
        WHERE dp.delivery_plan_id = ?
        GROUP BY
            dp.delivery_plan_id,
            dp.order_item_id,
            dp.delivery_status,
            ps.production_schedule_id,
            ps.production_batch_id,
            pb.batch_code,
            pb.actual_qty,
            pb.semi_finished_wh_qty,
            pm.measurement_id,
            pm.release_status,
            pm.qc_before_qty,
            pm.qc_after_qty,
            pm.qc_loss_qty
    """, conn, params=[int(delivery_plan_id)])

    if df.empty:
        return False, "未找到该交付批次对应的质检记录。"

    row = df.iloc[0]

    if int(row["lot_count"] or 0) > 0:
        return False, "该批次已经正式入库，不能直接退回质检。请后续使用【反入库】功能。"

    old_status = str(row["delivery_status"])
    old_qty = float(row["qc_after_qty"] or row["actual_qty"] or 0)
    qc_before_qty = float(row["qc_before_qty"] or row["semi_finished_wh_qty"] or row["actual_qty"] or 0)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE production_measurement
        SET release_status = 'pending',
            quality_status = 'Pending',
            qc_after_qty = 0,
            qc_loss_qty = 0,
            qc_note = COALESCE(qc_note, '') || '；异常回退：撤回质检放行',
            inspected_at = datetime('now')
        WHERE measurement_id = ?
    """, (
        int(row["measurement_id"]),
    ))

    cursor.execute("""
        UPDATE production_batch
        SET actual_qty = ?,
            semi_finished_wh_qty = ?,
            production_flow_status = 'qc_pending'
        WHERE production_batch_id = ?
    """, (
        float(qc_before_qty),
        float(qc_before_qty),
        int(row["production_batch_id"])
    ))

    cursor.execute("""
        UPDATE delivery_plan
        SET delivery_status = '质检中'
        WHERE delivery_plan_id = ?
    """, (
        int(delivery_plan_id),
    ))

    conn.commit()

    record_correction_log(
        conn=conn,
        correction_type="撤回质检放行",
        target_type="production_measurement",
        delivery_plan_id=int(delivery_plan_id),
        production_batch_id=int(row["production_batch_id"]),
        production_schedule_id=int(row["production_schedule_id"]),
        order_item_id=int(row["order_item_id"]),
        old_status=old_status,
        new_status="质检中",
        old_qty=old_qty,
        new_qty=qc_before_qty,
        correction_reason=reason,
        operator_name=operator_name
    )

    if "sync_after_delivery_plan_change" in globals():
        sync_after_delivery_plan_change(conn, int(delivery_plan_id))

    return True, f"已撤回质检放行，交付批次 {delivery_plan_id} 已回到【质检中】。"


def page_exception_correction(conn):
    st.header("系统管理｜异常处理 / 流程回退")

    ensure_correction_schema(conn)

    st.warning(
        "本页面用于纠错和流程回退。已入库、已出货阶段暂不允许直接回退，"
        "后续建议单独做【反入库】和【反出货】。"
    )

    tab_rollback, tab_log = st.tabs([
        "流程回退",
        "纠错日志"
    ])

    with tab_rollback:
        st.subheader("选择需要回退的交付批次")

        flow_df = get_exception_flow_records(conn)

        if flow_df.empty:
            st.info("当前没有可查看的流程记录。")
            return

        show_cols = [
            "delivery_plan_id",
            "delivery_batch_no",
            "delivery_status",
            "sales_need_production",
            "sales_need_semi_out",
            "production_schedule_id",
            "production_batch_id",
            "batch_code",
            "customer_name",
            "po_no",
            "planned_delivery_qty",
            "actual_delivery_qty",
            "actual_qty",
            "semi_finished_wh_qty",
            "finished_wh_qty",
            "production_flow_status",
            "quality_status",
            "release_status",
            "lot_code",
            "available_qty"
        ]

        existing_show_cols = [c for c in show_cols if c in flow_df.columns]

        st.markdown("### 当前流程记录")
        show_df(flow_df[existing_show_cols], hide_index=True)

        st.markdown("---")

        delivery_plan_ids = [int(x) for x in flow_df["delivery_plan_id"].dropna().unique().tolist()]

        selected_delivery_plan_id = st.selectbox(
            "选择交付批次",
            delivery_plan_ids,
            format_func=lambda x: (
                f"【{flow_df.loc[flow_df['delivery_plan_id'] == x, 'delivery_status'].iloc[0]}】 "
                f"交付批次 {x} | "
                f"PO {flow_df.loc[flow_df['delivery_plan_id'] == x, 'po_no'].iloc[0]} | "
                f"第 {int(flow_df.loc[flow_df['delivery_plan_id'] == x, 'delivery_batch_no'].iloc[0])} 批 | "
                f"批号 {flow_df.loc[flow_df['delivery_plan_id'] == x, 'batch_code'].iloc[0] if pd.notna(flow_df.loc[flow_df['delivery_plan_id'] == x, 'batch_code'].iloc[0]) else '-'}"
            ),
            key="exception_delivery_plan_select"
        )

        selected_rows = flow_df[flow_df["delivery_plan_id"] == selected_delivery_plan_id].copy()
        selected = selected_rows.iloc[0]

        st.markdown("### 当前批次状态卡片")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("交付批次编号", int(selected["delivery_plan_id"]))
        c2.metric("当前状态", str(selected["delivery_status"]))
        c3.metric("PO", str(selected["po_no"]))
        c4.metric("客户", str(selected["customer_name"]))

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("计划交付数量", f"{float(selected['planned_delivery_qty'] or 0):.0f}")
        c6.metric("实际交付数量", f"{float(selected['actual_delivery_qty'] or 0):.0f}")
        c7.metric("生产批号", str(selected["batch_code"]) if pd.notna(selected["batch_code"]) else "-")
        c8.metric("生产状态", str(selected["production_flow_status"]) if pd.notna(selected["production_flow_status"]) else "-")

        c9, c10, c11, c12 = st.columns(4)
        c9.metric("实际生产数量", f"{float(selected['actual_qty'] or 0):.0f}")
        c10.metric("半成品数量", f"{float(selected['semi_finished_wh_qty'] or 0):.0f}")
        c11.metric("成品数量", f"{float(selected['finished_wh_qty'] or 0):.0f}")
        c12.metric("放行状态", str(selected["release_status"]) if pd.notna(selected["release_status"]) else "-")

        st.markdown("Trace Key")
        st.code(str(selected["trace_key"]))

        st.markdown("---")

        current_status = str(selected["delivery_status"])

        rollback_options = []

        if current_status in ["未排产", "待生产确认", "半成品出库准备", "发货准备"]:
            rollback_options.append("退回销售判断：待生产确认 / 半成品出库准备 / 发货准备 → 未排产")

        if current_status in ["已排产"]:
            rollback_options.append("取消排产：已排产 → 待生产确认")

        if current_status in ["生产中"]:
            rollback_options.append("回退最后一道工序：生产中 → 已排产 / 生产中")

        if current_status in ["待入库确认"]:
            rollback_options.append("撤回质检放行：待入库确认 → 质检中")

        if current_status in ["质检中"]:
            st.info("当前已经处于【质检中】，如需修改质检数据，请在半成品仓库看板重新质检放行。")

        if current_status in ["已入库", "部分出货", "已出货"]:
            st.error("当前状态属于高风险阶段，暂不允许直接回退。后续应使用反入库 / 反出货功能。")

        if not rollback_options:
            st.info("当前状态没有可执行的低风险回退动作。")
            return

        selected_action = st.selectbox(
            "选择回退动作",
            rollback_options,
            key="exception_rollback_action_select"
        )

        operator_name = st.text_input(
            "操作人",
            value="Admin User",
            key="exception_operator_name"
        )

        reason = st.text_area(
            "回退原因",
            placeholder="请填写具体原因，例如：生产批号录错、通规止规录错、误录入工序、质检数量录错等。",
            key="exception_reason"
        )

        confirm_text = st.text_input(
            "请输入 CONFIRM 确认执行",
            value="",
            key="exception_confirm_text"
        )

        final_check = st.checkbox(
            "我确认该操作是异常纠错，会写入纠错日志，并可能影响后续页面数据。",
            key="exception_final_check"
        )

        if st.button("执行流程回退", key="execute_exception_rollback"):
            if not final_check:
                st.error("请先勾选确认。")
                return

            if normalize_text(confirm_text).upper() != "CONFIRM":
                st.error("请输入 CONFIRM 进行二次确认。")
                return

            if not normalize_text(reason):
                st.error("请填写回退原因。")
                return

            if selected_action.startswith("退回销售判断"):
                ok, msg = rollback_delivery_to_sales(
                    conn=conn,
                    delivery_plan_id=int(selected_delivery_plan_id),
                    reason=reason,
                    operator_name=operator_name
                )

            elif selected_action.startswith("取消排产"):
                ok, msg = rollback_schedule_to_pending(
                    conn=conn,
                    delivery_plan_id=int(selected_delivery_plan_id),
                    reason=reason,
                    operator_name=operator_name
                )

            elif selected_action.startswith("回退最后一道工序"):
                ok, msg = rollback_last_process_step(
                    conn=conn,
                    delivery_plan_id=int(selected_delivery_plan_id),
                    reason=reason,
                    operator_name=operator_name
                )

            elif selected_action.startswith("撤回质检放行"):
                ok, msg = rollback_qc_release_to_qc(
                    conn=conn,
                    delivery_plan_id=int(selected_delivery_plan_id),
                    reason=reason,
                    operator_name=operator_name
                )

            else:
                ok, msg = False, "未知回退动作。"

            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab_log:
        st.subheader("纠错日志")

        log_df = pd.read_sql_query("""
            SELECT
                correction_id,
                correction_type,
                target_type,
                delivery_plan_id,
                production_batch_id,
                production_schedule_id,
                order_item_id,
                old_status,
                new_status,
                old_qty,
                new_qty,
                correction_reason,
                operator_name,
                created_at
            FROM correction_log
            ORDER BY correction_id DESC
        """, conn)

        if log_df.empty:
            st.info("当前还没有纠错日志。")
        else:
            show_df(log_df.rename(columns={
                "correction_id": "纠错编号",
                "correction_type": "纠错类型",
                "target_type": "对象类型",
                "delivery_plan_id": "交付批次编号",
                "production_batch_id": "生产批次编号",
                "production_schedule_id": "排程编号",
                "order_item_id": "订单明细编号",
                "old_status": "原状态",
                "new_status": "新状态",
                "old_qty": "原数量",
                "new_qty": "新数量",
                "correction_reason": "纠错原因",
                "operator_name": "操作人",
                "created_at": "操作时间"
            }), hide_index=True)

# =========================
# 基础选项管理：特殊工艺 / 材质
# =========================

def ensure_business_option_schema(conn):
    """
    基础业务选项表：
    用于维护特殊工艺、材质等下拉选项。
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_option (
            option_id INTEGER PRIMARY KEY AUTOINCREMENT,
            option_group TEXT,
            option_value TEXT,
            option_label TEXT,
            is_enabled INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 100,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    default_rows = [
        ("special_process", "STANDARD", "STANDARD", 1, 10),
        ("special_process", "LASER", "LASER", 1, 20),
        ("special_process", "CHAMFER", "CHAMFER", 1, 30),
        ("special_process", "DRILLING", "DRILLING", 1, 40),

        ("material", "BOROSILICATE", "BOROSILICATE", 1, 10),
        ("material", "QUARTZ", "QUARTZ", 1, 20),
        ("material", "SODA-LIME", "SODA-LIME", 1, 30),
    ]

    for option_group, option_value, option_label, is_enabled, sort_order in default_rows:
        exists_df = pd.read_sql_query("""
            SELECT COUNT(*) AS cnt
            FROM business_option
            WHERE option_group = ?
              AND option_value = ?
        """, conn, params=[option_group, option_value])

        if int(exists_df.iloc[0]["cnt"] or 0) == 0:
            cursor.execute("""
                INSERT INTO business_option (
                    option_group,
                    option_value,
                    option_label,
                    is_enabled,
                    sort_order
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                option_group,
                option_value,
                option_label,
                is_enabled,
                sort_order
            ))

    conn.commit()


def get_business_options(conn, option_group, fallback_options=None):
    """
    获取启用的业务选项。
    """
    ensure_business_option_schema(conn)

    df = pd.read_sql_query("""
        SELECT
            option_value,
            option_label
        FROM business_option
        WHERE option_group = ?
          AND is_enabled = 1
        ORDER BY sort_order, option_id
    """, conn, params=[option_group])

    if df.empty:
        return fallback_options or []

    return df["option_value"].astype(str).tolist()


def normalize_business_option(conn, option_group, value, default_value):
    """
    标准化业务选项：
    - 如果输入值在系统选项里，返回标准值
    - 如果不在，返回默认值
    """
    options = get_business_options(conn, option_group, [default_value])
    text = normalize_text(value).upper()

    if text in options:
        return text

    return default_value

def page_business_option_manager(conn):
    st.header("系统配置｜基础选项管理")

    ensure_business_option_schema(conn)
    ensure_product_spec_manage_schema(conn)

    st.info(
        "这里用于维护订单录入中的基础选项。"
        "特殊工艺和材质会进入下拉选项；产品规格会写入产品规格主数据，并自动出现在订单录入页面。"
    )

    tab_list, tab_add, tab_manage, tab_spec = st.tabs([
        "当前选项",
        "新增选项",
        "启用 / 停用",
        "产品规格管理"
    ])

    # =========================
    # 1. 当前选项
    # =========================
    with tab_list:
        st.subheader("当前基础选项")

        option_df = pd.read_sql_query("""
            SELECT
                option_id,
                option_group,
                option_value,
                option_label,
                is_enabled,
                sort_order,
                created_at
            FROM business_option
            ORDER BY option_group, sort_order, option_id
        """, conn)

        if option_df.empty:
            st.info("当前没有特殊工艺 / 材质基础选项。")
        else:
            option_df["option_group_cn"] = option_df["option_group"].map({
                "special_process": "特殊工艺",
                "material": "材质"
            }).fillna(option_df["option_group"])

            show_df(option_df.rename(columns={
                "option_id": "选项编号",
                "option_group_cn": "选项类别",
                "option_value": "选项值",
                "option_label": "显示名称",
                "is_enabled": "是否启用",
                "sort_order": "排序",
                "created_at": "创建时间"
            }), hide_index=True)

        st.markdown("---")
        st.subheader("当前产品规格")

        spec_df = pd.read_sql_query("""
            SELECT
                ps.spec_id,
                p.product_id,
                p.product_name,
                p.product_code,
                COALESCE(p.category, '') AS category,
                ps.spec_code,
                ps.spec_desc,
                ps.outer_diameter_mm,
                ps.wall_thickness_mm,
                ps.length_mm,
                COALESCE(p.is_enabled, 1) AS product_enabled,
                COALESCE(ps.is_enabled, 1) AS spec_enabled
            FROM product_spec ps
            JOIN product p
                ON ps.product_id = p.product_id
            ORDER BY
                COALESCE(ps.is_enabled, 1) DESC,
                p.product_name,
                ps.spec_code
        """, conn)

        if spec_df.empty:
            st.info("当前没有产品规格。")
        else:
            show_df(spec_df.rename(columns={
                "spec_id": "规格编号",
                "product_id": "产品编号",
                "product_name": "产品名称",
                "product_code": "产品编码",
                "category": "产品分类",
                "spec_code": "规格编码",
                "spec_desc": "规格描述",
                "outer_diameter_mm": "外径(mm)",
                "wall_thickness_mm": "壁厚(mm)",
                "length_mm": "长度(mm)",
                "product_enabled": "产品启用",
                "spec_enabled": "规格启用"
            }), hide_index=True)

    # =========================
    # 2. 新增选项
    # =========================
    with tab_add:
        st.subheader("新增基础选项")

        option_group_cn = st.selectbox(
            "选项类别",
            ["特殊工艺", "材质", "产品规格"],
            key="business_option_group_cn"
        )

        # =========================
        # 2.1 新增特殊工艺 / 材质
        # =========================
        if option_group_cn in ["特殊工艺", "材质"]:
            option_group = "special_process" if option_group_cn == "特殊工艺" else "material"

            option_value = st.text_input(
                "选项值",
                placeholder="例如：POLISHING / ALUMINO-SILICATE",
                key="business_option_value"
            )

            option_label = st.text_input(
                "显示名称",
                placeholder="通常和选项值一致",
                key="business_option_label"
            )

            sort_order = st.number_input(
                "排序",
                min_value=1,
                value=100,
                step=10,
                key="business_option_sort_order"
            )

            if st.button("新增选项", key="add_business_option"):
                value_clean = normalize_text(option_value).upper()
                label_clean = normalize_text(option_label).upper() or value_clean

                if not value_clean:
                    st.error("请填写选项值。")
                    return

                exists_df = pd.read_sql_query("""
                    SELECT COUNT(*) AS cnt
                    FROM business_option
                    WHERE option_group = ?
                      AND option_value = ?
                """, conn, params=[option_group, value_clean])

                if int(exists_df.iloc[0]["cnt"] or 0) > 0:
                    st.error("该选项已经存在。")
                    return

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO business_option (
                        option_group,
                        option_value,
                        option_label,
                        is_enabled,
                        sort_order
                    ) VALUES (?, ?, ?, 1, ?)
                """, (
                    option_group,
                    value_clean,
                    label_clean,
                    int(sort_order)
                ))

                conn.commit()
                st.success(f"已新增选项：{value_clean}")
                st.rerun()

        # =========================
        # 2.2 新增产品规格
        # =========================
        else:
            st.markdown("### 新增产品规格")

            existing_product_df = pd.read_sql_query("""
                SELECT
                    product_id,
                    product_name,
                    COALESCE(product_code, '') AS product_code,
                    COALESCE(category, '') AS category,
                    COALESCE(is_enabled, 1) AS is_enabled
                FROM product
                ORDER BY product_name, product_id
            """, conn)

            product_source = st.radio(
                "产品来源",
                ["选择已有产品", "新增产品"],
                horizontal=True,
                key="spec_product_source"
            )

            product_id = None

            if product_source == "选择已有产品":
                if existing_product_df.empty:
                    st.warning("当前没有已有产品，请选择【新增产品】。")
                    product_source = "新增产品"
                else:
                    product_id = st.selectbox(
                        "选择产品",
                        existing_product_df["product_id"].tolist(),
                        format_func=lambda x: (
                            f"{existing_product_df.loc[existing_product_df['product_id'] == x, 'product_name'].iloc[0]}"
                            f"｜{existing_product_df.loc[existing_product_df['product_id'] == x, 'product_code'].iloc[0]}"
                        ),
                        key="spec_existing_product_id"
                    )

            if product_source == "新增产品":
                c1, c2, c3 = st.columns(3)

                with c1:
                    new_product_name = st.text_input(
                        "产品名称",
                        placeholder="例如：Glass Tube",
                        key="spec_new_product_name"
                    )

                with c2:
                    new_product_code = st.text_input(
                        "产品编码",
                        placeholder="例如：PROD-GLASS-TUBE",
                        key="spec_new_product_code"
                    )

                with c3:
                    new_category = st.text_input(
                        "产品分类",
                        value="Glass Tube",
                        key="spec_new_product_category"
                    )

            st.markdown("---")

            s1, s2, s3 = st.columns(3)

            with s1:
                spec_code = st.text_input(
                    "规格编码",
                    placeholder="例如：SPEC-A-20x2x1500",
                    key="new_spec_code"
                )

                outer_diameter_mm = st.number_input(
                    "外径(mm)",
                    min_value=0.0,
                    value=20.0,
                    step=0.1,
                    key="new_spec_outer_diameter"
                )

            with s2:
                spec_desc = st.text_input(
                    "规格描述",
                    placeholder="例如：20mm OD x 2mm WT x 1500mm L",
                    key="new_spec_desc"
                )

                wall_thickness_mm = st.number_input(
                    "壁厚(mm)",
                    min_value=0.0,
                    value=2.0,
                    step=0.1,
                    key="new_spec_wall_thickness"
                )

            with s3:
                length_mm = st.number_input(
                    "长度(mm)",
                    min_value=0.0,
                    value=1500.0,
                    step=1.0,
                    key="new_spec_length"
                )

                spec_enabled = st.radio(
                    "是否启用",
                    [1, 0],
                    format_func=lambda x: "启用" if x == 1 else "停用",
                    horizontal=True,
                    index=0,
                    key="new_spec_enabled"
                )

            if st.button("新增产品规格", key="add_product_spec_from_option"):
                spec_code_clean = normalize_text(spec_code).upper()
                spec_desc_clean = normalize_text(spec_desc)

                if not spec_code_clean:
                    st.error("请填写规格编码。")
                    return

                cursor = conn.cursor()

                try:
                    # 如果是新增产品，先写 product
                    if product_source == "新增产品":
                        product_name_clean = normalize_text(new_product_name)

                        if not product_name_clean:
                            st.error("请填写产品名称。")
                            return

                        product_code_clean = normalize_text(new_product_code).upper()
                        if not product_code_clean:
                            product_code_clean = f"PROD-{product_name_clean.upper().replace(' ', '-')}"

                        category_clean = normalize_text(new_category) or "Glass Tube"

                        product_exists_df = pd.read_sql_query("""
                            SELECT product_id
                            FROM product
                            WHERE product_name = ?
                               OR product_code = ?
                            LIMIT 1
                        """, conn, params=[
                            product_name_clean,
                            product_code_clean
                        ])

                        if product_exists_df.empty:
                            cursor.execute("""
                                INSERT INTO product (
                                    product_name,
                                    product_code,
                                    category,
                                    is_enabled
                                ) VALUES (?, ?, ?, 1)
                            """, (
                                product_name_clean,
                                product_code_clean,
                                category_clean
                            ))
                            product_id_use = cursor.lastrowid
                        else:
                            product_id_use = int(product_exists_df.iloc[0]["product_id"])

                    else:
                        product_id_use = int(product_id)

                    # 检查规格是否重复
                    spec_exists_df = pd.read_sql_query("""
                        SELECT COUNT(*) AS cnt
                        FROM product_spec
                        WHERE spec_code = ?
                    """, conn, params=[spec_code_clean])

                    if int(spec_exists_df.iloc[0]["cnt"] or 0) > 0:
                        st.error("该规格编码已存在。")
                        return

                    cursor.execute("""
                        INSERT INTO product_spec (
                            product_id,
                            spec_code,
                            spec_desc,
                            outer_diameter_mm,
                            wall_thickness_mm,
                            length_mm,
                            is_enabled
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        int(product_id_use),
                        spec_code_clean,
                        spec_desc_clean,
                        float(outer_diameter_mm),
                        float(wall_thickness_mm),
                        float(length_mm),
                        int(spec_enabled)
                    ))

                    conn.commit()

                    st.success(f"产品规格已新增：{spec_code_clean}")
                    st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"新增产品规格失败：{e}")
                    return

    # =========================
    # 3. 启用 / 停用特殊工艺、材质
    # =========================
    with tab_manage:
        st.subheader("启用 / 停用特殊工艺、材质")

        option_df = pd.read_sql_query("""
            SELECT
                option_id,
                option_group,
                option_value,
                option_label,
                is_enabled,
                sort_order
            FROM business_option
            ORDER BY option_group, sort_order, option_id
        """, conn)

        if option_df.empty:
            st.info("当前没有可管理的选项。")
        else:
            selected_option_id = st.selectbox(
                "选择选项",
                option_df["option_id"].tolist(),
                format_func=lambda x: (
                    f"{option_df.loc[option_df['option_id'] == x, 'option_group'].iloc[0]} | "
                    f"{option_df.loc[option_df['option_id'] == x, 'option_value'].iloc[0]} | "
                    f"{'启用' if int(option_df.loc[option_df['option_id'] == x, 'is_enabled'].iloc[0] or 0) == 1 else '停用'}"
                ),
                key="manage_business_option_select"
            )

            selected = option_df[option_df["option_id"] == selected_option_id].iloc[0]

            new_enabled = st.radio(
                "状态",
                [1, 0],
                format_func=lambda x: "启用" if x == 1 else "停用",
                horizontal=True,
                index=0 if int(selected["is_enabled"] or 0) == 1 else 1,
                key="manage_business_option_enabled"
            )

            new_sort_order = st.number_input(
                "排序",
                min_value=1,
                value=int(selected["sort_order"] or 100),
                step=10,
                key="manage_business_option_sort"
            )

            if st.button("保存修改", key="save_business_option_manage"):
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE business_option
                    SET is_enabled = ?,
                        sort_order = ?
                    WHERE option_id = ?
                """, (
                    int(new_enabled),
                    int(new_sort_order),
                    int(selected_option_id)
                ))

                conn.commit()
                st.success("选项已更新。")
                st.rerun()

    # =========================
    # 4. 产品规格管理
    # =========================
    with tab_spec:
        st.subheader("产品规格管理")

        spec_df = pd.read_sql_query("""
            SELECT
                ps.spec_id,
                p.product_id,
                p.product_name,
                p.product_code,
                COALESCE(p.category, '') AS category,
                ps.spec_code,
                ps.spec_desc,
                ps.outer_diameter_mm,
                ps.wall_thickness_mm,
                ps.length_mm,
                COALESCE(p.is_enabled, 1) AS product_enabled,
                COALESCE(ps.is_enabled, 1) AS spec_enabled
            FROM product_spec ps
            JOIN product p
                ON ps.product_id = p.product_id
            ORDER BY
                COALESCE(ps.is_enabled, 1) DESC,
                p.product_name,
                ps.spec_code
        """, conn)

        if spec_df.empty:
            st.info("当前没有产品规格。")
            return

        selected_spec_id = st.selectbox(
            "选择产品规格",
            spec_df["spec_id"].tolist(),
            format_func=lambda x: (
                f"{spec_df.loc[spec_df['spec_id'] == x, 'product_name'].iloc[0]} | "
                f"{spec_df.loc[spec_df['spec_id'] == x, 'spec_code'].iloc[0]} | "
                f"{'启用' if int(spec_df.loc[spec_df['spec_id'] == x, 'spec_enabled'].iloc[0] or 0) == 1 else '停用'}"
            ),
            key="manage_product_spec_select"
        )

        selected_spec = spec_df[spec_df["spec_id"] == selected_spec_id].iloc[0]

        c1, c2, c3 = st.columns(3)

        with c1:
            edit_spec_code = st.text_input(
                "规格编码",
                value=str(selected_spec["spec_code"]),
                key="edit_spec_code"
            )

            edit_outer_diameter = st.number_input(
                "外径(mm)",
                min_value=0.0,
                value=float(selected_spec["outer_diameter_mm"] or 0),
                step=0.1,
                key="edit_outer_diameter"
            )

        with c2:
            edit_spec_desc = st.text_input(
                "规格描述",
                value=str(selected_spec["spec_desc"]) if pd.notna(selected_spec["spec_desc"]) else "",
                key="edit_spec_desc"
            )

            edit_wall_thickness = st.number_input(
                "壁厚(mm)",
                min_value=0.0,
                value=float(selected_spec["wall_thickness_mm"] or 0),
                step=0.1,
                key="edit_wall_thickness"
            )

        with c3:
            edit_length = st.number_input(
                "长度(mm)",
                min_value=0.0,
                value=float(selected_spec["length_mm"] or 0),
                step=1.0,
                key="edit_length"
            )

            edit_spec_enabled = st.radio(
                "规格状态",
                [1, 0],
                format_func=lambda x: "启用" if x == 1 else "停用",
                horizontal=True,
                index=0 if int(selected_spec["spec_enabled"] or 0) == 1 else 1,
                key="edit_spec_enabled"
            )

        if st.button("保存产品规格修改", key="save_product_spec_manage"):
            spec_code_clean = normalize_text(edit_spec_code).upper()

            if not spec_code_clean:
                st.error("规格编码不能为空。")
                return

            duplicate_df = pd.read_sql_query("""
                SELECT COUNT(*) AS cnt
                FROM product_spec
                WHERE spec_id <> ?
                  AND spec_code = ?
            """, conn, params=[
                int(selected_spec_id),
                spec_code_clean
            ])

            if int(duplicate_df.iloc[0]["cnt"] or 0) > 0:
                st.error("其他产品规格已使用相同规格编码。")
                return

            cursor = conn.cursor()
            cursor.execute("""
                UPDATE product_spec
                SET spec_code = ?,
                    spec_desc = ?,
                    outer_diameter_mm = ?,
                    wall_thickness_mm = ?,
                    length_mm = ?,
                    is_enabled = ?
                WHERE spec_id = ?
            """, (
                spec_code_clean,
                normalize_text(edit_spec_desc),
                float(edit_outer_diameter),
                float(edit_wall_thickness),
                float(edit_length),
                int(edit_spec_enabled),
                int(selected_spec_id)
            ))

            conn.commit()
            st.success("产品规格已更新。")
            st.rerun()

# =========================
# 客户主数据管理
# =========================

def ensure_customer_schema(conn):
    """
    确保 customer 表具备客户管理所需字段。
    已存在字段不会重复添加。
    """
    cursor = conn.cursor()

    cols = pd.read_sql_query(
        "PRAGMA table_info(customer)",
        conn
    )["name"].tolist()

    if "customer_code" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN customer_code TEXT
        """)

    if "contact_person" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN contact_person TEXT
        """)

    if "phone" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN phone TEXT
        """)

    if "email" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN email TEXT
        """)

    if "address" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN address TEXT
        """)

    if "is_enabled" not in cols:
        cursor.execute("""
            ALTER TABLE customer
            ADD COLUMN is_enabled INTEGER DEFAULT 1
        """)

    conn.commit()


def page_customer_manager(conn):
    st.header("销售管理｜客户管理")

    ensure_customer_schema(conn)

    st.info(
        "这里用于维护客户主数据。新增或启用客户后，订单录入页面会自动出现在客户下拉框中。"
    )

    tab_list, tab_add, tab_manage = st.tabs([
        "客户列表",
        "新增客户",
        "启用 / 停用"
    ])

    # =========================
    # 1. 客户列表
    # =========================
    with tab_list:
        st.subheader("客户列表")

        customer_df = pd.read_sql_query("""
            SELECT
                customer_id,
                customer_code,
                customer_name,
                contact_person,
                phone,
                email,
                address,
                COALESCE(is_enabled, 1) AS is_enabled
            FROM customer
            ORDER BY
                COALESCE(is_enabled, 1) DESC,
                customer_id DESC
        """, conn)

        if customer_df.empty:
            st.info("当前没有客户数据。")
        else:
            show_df(customer_df.rename(columns={
                "customer_id": "客户编号",
                "customer_code": "客户编码",
                "customer_name": "客户名称",
                "contact_person": "联系人",
                "phone": "电话",
                "email": "邮箱",
                "address": "地址",
                "is_enabled": "是否启用"
            }), hide_index=True)

    # =========================
    # 2. 新增客户
    # =========================
    with tab_add:
        st.subheader("新增客户")

        c1, c2 = st.columns(2)

        with c1:
            customer_name = st.text_input(
                "客户名称",
                placeholder="例如：Alpha Medical Glass",
                key="customer_manager_add_name"
            )

            customer_code = st.text_input(
                "客户编码",
                placeholder="例如：CUST-ALPHA",
                key="customer_manager_add_code"
            )

            contact_person = st.text_input(
                "联系人",
                placeholder="例如：Mr. Wang",
                key="customer_manager_add_contact"
            )

        with c2:
            phone = st.text_input(
                "电话",
                placeholder="例如：13800000000",
                key="customer_manager_add_phone"
            )

            email = st.text_input(
                "邮箱",
                placeholder="例如：contact@example.com",
                key="customer_manager_add_email"
            )

            address = st.text_input(
                "地址",
                placeholder="例如：Chengdu, China",
                key="customer_manager_add_address"
            )

        if st.button("新增客户", key="customer_manager_add_btn"):
            customer_name_clean = normalize_text(customer_name)
            customer_code_clean = normalize_text(customer_code).upper()

            if not customer_name_clean:
                st.error("客户名称不能为空。")
                return

            if not customer_code_clean:
                customer_code_clean = f"CUST-{customer_name_clean.upper().replace(' ', '-')}"

            exists_df = pd.read_sql_query("""
                SELECT COUNT(*) AS cnt
                FROM customer
                WHERE customer_name = ?
                   OR customer_code = ?
            """, conn, params=[
                customer_name_clean,
                customer_code_clean
            ])

            if int(exists_df.iloc[0]["cnt"] or 0) > 0:
                st.error("客户名称或客户编码已存在，请检查后再新增。")
                return

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO customer (
                    customer_name,
                    customer_code,
                    contact_person,
                    phone,
                    email,
                    address,
                    is_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                customer_name_clean,
                customer_code_clean,
                normalize_text(contact_person),
                normalize_text(phone),
                normalize_text(email),
                normalize_text(address),
            ))

            conn.commit()

            st.success(f"客户已新增：{customer_name_clean}")
            st.rerun()

    # =========================
    # 3. 启用 / 停用
    # =========================
    with tab_manage:
        st.subheader("启用 / 停用客户")

        customer_df = pd.read_sql_query("""
            SELECT
                customer_id,
                customer_code,
                customer_name,
                contact_person,
                phone,
                email,
                address,
                COALESCE(is_enabled, 1) AS is_enabled
            FROM customer
            ORDER BY customer_id DESC
        """, conn)

        if customer_df.empty:
            st.info("当前没有客户可管理。")
            return

        selected_customer_id = st.selectbox(
            "选择客户",
            customer_df["customer_id"].tolist(),
            format_func=lambda x: (
                f"{customer_df.loc[customer_df['customer_id'] == x, 'customer_name'].iloc[0]} | "
                f"{customer_df.loc[customer_df['customer_id'] == x, 'customer_code'].iloc[0]} | "
                f"{'启用' if int(customer_df.loc[customer_df['customer_id'] == x, 'is_enabled'].iloc[0] or 0) == 1 else '停用'}"
            ),
            key="customer_manager_select"
        )

        selected = customer_df[
            customer_df["customer_id"] == selected_customer_id
        ].iloc[0]

        c1, c2 = st.columns(2)

        with c1:
            edit_customer_name = st.text_input(
                "客户名称",
                value=str(selected["customer_name"]),
                key="customer_manager_edit_name"
            )

            edit_customer_code = st.text_input(
                "客户编码",
                value=str(selected["customer_code"]) if pd.notna(selected["customer_code"]) else "",
                key="customer_manager_edit_code"
            )

            edit_contact_person = st.text_input(
                "联系人",
                value=str(selected["contact_person"]) if pd.notna(selected["contact_person"]) else "",
                key="customer_manager_edit_contact"
            )

        with c2:
            edit_phone = st.text_input(
                "电话",
                value=str(selected["phone"]) if pd.notna(selected["phone"]) else "",
                key="customer_manager_edit_phone"
            )

            edit_email = st.text_input(
                "邮箱",
                value=str(selected["email"]) if pd.notna(selected["email"]) else "",
                key="customer_manager_edit_email"
            )

            edit_address = st.text_input(
                "地址",
                value=str(selected["address"]) if pd.notna(selected["address"]) else "",
                key="customer_manager_edit_address"
            )

        new_enabled = st.radio(
            "客户状态",
            [1, 0],
            format_func=lambda x: "启用" if x == 1 else "停用",
            horizontal=True,
            index=0 if int(selected["is_enabled"] or 0) == 1 else 1,
            key="customer_manager_enabled"
        )

        if st.button("保存客户修改", key="customer_manager_save"):
            name_clean = normalize_text(edit_customer_name)
            code_clean = normalize_text(edit_customer_code).upper()

            if not name_clean:
                st.error("客户名称不能为空。")
                return

            if not code_clean:
                code_clean = f"CUST-{name_clean.upper().replace(' ', '-')}"

            duplicate_df = pd.read_sql_query("""
                SELECT COUNT(*) AS cnt
                FROM customer
                WHERE customer_id <> ?
                  AND (
                        customer_name = ?
                        OR customer_code = ?
                      )
            """, conn, params=[
                int(selected_customer_id),
                name_clean,
                code_clean
            ])

            if int(duplicate_df.iloc[0]["cnt"] or 0) > 0:
                st.error("其他客户已使用相同客户名称或客户编码。")
                return

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE customer
                SET customer_name = ?,
                    customer_code = ?,
                    contact_person = ?,
                    phone = ?,
                    email = ?,
                    address = ?,
                    is_enabled = ?
                WHERE customer_id = ?
            """, (
                name_clean,
                code_clean,
                normalize_text(edit_contact_person),
                normalize_text(edit_phone),
                normalize_text(edit_email),
                normalize_text(edit_address),
                int(new_enabled),
                int(selected_customer_id)
            ))

            conn.commit()

            st.success("客户信息已更新。")
            st.rerun()

# =========================
# 产品规格管理字段补充
# =========================

def ensure_product_spec_manage_schema(conn):
    """
    确保 product / product_spec 支持系统内维护产品规格。
    已存在字段不会重复添加。
    """

    cursor = conn.cursor()

    product_cols = pd.read_sql_query(
        "PRAGMA table_info(product)",
        conn
    )["name"].tolist()

    if "product_code" not in product_cols:
        cursor.execute("""
            ALTER TABLE product
            ADD COLUMN product_code TEXT
        """)

    if "category" not in product_cols:
        cursor.execute("""
            ALTER TABLE product
            ADD COLUMN category TEXT
        """)

    if "is_enabled" not in product_cols:
        cursor.execute("""
            ALTER TABLE product
            ADD COLUMN is_enabled INTEGER DEFAULT 1
        """)

    spec_cols = pd.read_sql_query(
        "PRAGMA table_info(product_spec)",
        conn
    )["name"].tolist()

    if "is_enabled" not in spec_cols:
        cursor.execute("""
            ALTER TABLE product_spec
            ADD COLUMN is_enabled INTEGER DEFAULT 1
        """)

    conn.commit()


# =========================
# 主程序
# =========================

def main():
    conn = get_conn()

    # =========================
    # 1. 初始化数据库结构与视图
    # =========================
    ensure_trace_key_columns(conn)
    ensure_delivery_plan_batch_fields(conn)
    ensure_production_schedule_delivery_plan_field(conn)
    ensure_business_option_schema(conn)
    ensure_product_spec_manage_schema(conn)
    ensure_customer_schema(conn)
    ensure_semi_finished_warehouse_schema(conn)
    ensure_sales_decision_schema(conn)
    ensure_correction_schema(conn)
    init_trace_views(conn)
    ensure_dynamic_demo_module(conn)

    apply_global_ui_style()

    # =========================
    # 2. 检查必要表
    # =========================
    missing = find_missing_tables(conn, REQUIRED_TABLES)
    if missing:
        st.error("数据库缺少必要表，当前 Streamlit 页面无法运行。")
        st.write("缺少表：", ", ".join(missing))
        with st.expander("查看当前数据库对象"):
            st.dataframe(
                list_db_objects(conn),
                use_container_width=True,
                hide_index=True
            )
        conn.close()
        return

    # =========================
    # 3. 页面分组
    # =========================
    NAV_GROUPS = {
        "首页": [
            "首页",
        ],
        "销售管理": [
            "客户管理",
            "订单录入",
            "销售看板",
        ],
        "生产管理": [
            "排产看板",
            "生产过程录入",
        ],
        "半成品仓库": [
             "半成品仓库看板",
             "半成品仓库录入",
        ],
        "库存/仓储": [
            "仓储总看板",
            "库存",
        ],
        "出货追踪": [
             "出货追踪中心",
             "出货管理",
             "批次追踪",
        ],

        "联动总控": [
            "实时联动看板",
            "实时刷新查询",
            "Trace Key 查询",
        ],

        "系统管理": [
            "异常处理",
        ],

        "系统配置": [
            "基础选项管理",
            "Excel 数据中心",
            "模块配置中心",
            "动态模块中心",
        ],
    }

    all_pages = [
        p
        for group_pages in NAV_GROUPS.values()
        for p in group_pages
    ]

    group_names = list(NAV_GROUPS.keys())

    # =========================
    # 4. 支持程序内跳转
    # 例如：
    # st.session_state["_jump_to_page"] = "生产过程录入"
    # st.session_state["selected_process_batch_id"] = production_batch_id
    # st.rerun()
    # =========================
    jump_page = st.session_state.pop("_jump_to_page", None)

    if jump_page in all_pages:
        target_page = jump_page
    else:
        target_page = st.session_state.get("nav_page_radio", "首页")

    if target_page not in all_pages:
        target_page = "首页"

    target_group = "首页"
    for group_name, group_pages in NAV_GROUPS.items():
        if target_page in group_pages:
            target_group = group_name
            break

    # 如果是按钮触发跳转，需要同步 sidebar 控件状态
    if jump_page in all_pages:
        st.session_state["nav_group_select"] = target_group
        st.session_state["nav_page_radio"] = target_page

    # =========================
    # 5. 侧边栏导航
    # =========================
    st.sidebar.title("功能导航")

    nav_group = st.sidebar.selectbox(
        "选择业务区",
        group_names,
        index=group_names.index(target_group),
        key="nav_group_select"
    )

    group_pages = NAV_GROUPS[nav_group]

    if target_page in group_pages:
        default_page_in_group = target_page
    else:
        default_page_in_group = group_pages[0]

    page = st.sidebar.radio(
        "选择功能",
        group_pages,
        index=group_pages.index(default_page_in_group),
        key="nav_page_radio"
    )

    # 记录当前页面，方便下次刷新保持当前位置
    st.session_state["current_page"] = page

    # =========================
    # 6. 页面路由
    # =========================
    if page == "首页":
        show_home(conn)

    elif page == "客户管理":
         page_customer_manager(conn)

    elif page == "订单录入":
        page_order_entry(conn)

    elif page == "销售看板":
        page_sales_dashboard(conn)

    elif page == "交付计划":
        page_delivery_plan(conn)

    elif page == "排产看板":
        page_production_dashboard(conn)

    elif page == "生产过程录入":
        page_production_process_entry(conn)

    elif page == "半成品仓库看板":
        page_semi_finished_dashboard(conn)

    elif page == "半成品仓库录入":
        page_semi_finished_entry(conn)

    elif page == "批次追踪":
        page_batch_tracking(conn)

    elif page == "检测录入":
        page_measurement_entry(conn)

    elif page == "质量放行":
        page_quality_release(conn)

    elif page == "仓储总看板":
        page_inventory_overview(conn)

    elif page == "库存":
        page_inventory_lot(conn)

    elif page == "出货追踪中心":
        page_outbound_tracking_center(conn)

    elif page == "出货管理":
        page_shipment(conn)

    elif page == "实时刷新查询":
        page_realtime_query(conn)

    elif page == "Trace Key 查询":
        page_trace_query(conn)

    elif page == "实时联动看板":
        page_realtime_control_tower(conn)

    elif page == "异常处理":
        page_exception_correction(conn)

    elif page == "基础选项管理":
        page_business_option_manager(conn)

    elif page == "Excel 数据中心":
        page_excel_center(conn)

    elif page == "模块配置中心":
        page_module_config_center(conn)

    elif page == "动态模块中心":
        page_dynamic_module_center(conn)

    # =========================
    # 7. 调试区
    # =========================
    with st.expander("调试：查看当前数据库对象"):
        st.dataframe(
            list_db_objects(conn),
            use_container_width=True,
            hide_index=True
        )

    conn.close()


if __name__ == "__main__":
    main()