import asyncpg
import asyncio
import psutil
from datetime import datetime
import plotly.express as px
from asyncpg import Pool
from fasthtml.common import *
from monsterui.all import *
import pandas as pd

DB_POOL: Optional[Pool] = None


async def ensure_pool():
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await asyncpg.create_pool(
            host=os.environ["PGHOST"],
            port=os.environ["PGPORT"],
            database=os.environ["OPERATOR_DB_NAME"],
            user=os.environ["PG_JUPYTER_READONLY_ROLE"],
            password=os.environ["PG_JUPYTER_READONLY_PW"],
            min_size=2,
            max_size=10,
        )


async def get_direct_db_connection():
    return await asyncpg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        database=os.environ["OPERATOR_DB_NAME"],
        user=os.environ["PG_JUPYTER_READONLY_ROLE"],
        password=os.environ["PG_JUPYTER_READONLY_PW"],
    )


# 1. Individual Request KPIs (top-requests.bash equivalent)
async def get_top_requests(node_name="node0", limit=40):
    await ensure_pool()
    async with DB_POOL.acquire() as conn:
        query = """
        WITH q AS (
          SELECT *,
            CASE
                WHEN topic = 0 THEN 'ORDER'
                WHEN topic = 1 THEN 'CANCEL_ORDER'
                WHEN topic = 3 THEN 'CANCEL_ALL'
                WHEN topic = 4 THEN 'WITHDRAW'
                WHEN topic = 5 THEN 'WITHDRAW_DDX'
                WHEN topic = 6 THEN 'INSURANCE_FUND_WITHDRAW'
                WHEN topic = 2 THEN 'UPDATE_PROFILE'
                WHEN topic = 50 THEN 'BLOCK'
                WHEN topic = 51 THEN 'ADVANCE_SETTLEMENT_EPOCH'
                WHEN topic = 53 THEN 'MINT_PRICE_CHECKPOINT'
                WHEN topic = 54 THEN 'ADVANCE_TIME'
                WHEN topic = 60 THEN 'ADVANCE_EPOCH'
                WHEN topic = 71 THEN 'PRICE'
                WHEN topic = 80 THEN 'DISASTER_RECOVERY'
                WHEN topic = 99 THEN 'GENESIS'
                ELSE 'UNKNOWN'
            END kind
         FROM request.queue
        ), p AS (
          SELECT request_index, sequence_busy + sequence_idle AS s,
            exec_total_busy + exec_total_idle AS e,
            exec_trusted_busy + exec_trusted_idle AS t,
            exec_commit_busy + exec_commit_idle AS c,
            exec_finalize_busy + exec_finalize_idle AS f
          FROM stats.perf_request
          WHERE origin = $1
        )
        SELECT q.created_at, q.request_index, q.topic, q.kind, q.entry_index, 
               round(p.e / 1000::numeric, 2) AS exec_ms
        FROM q
        LEFT JOIN p ON (p.request_index = q.request_index)
        ORDER BY q.request_index DESC
        LIMIT $2
        """
        result = await conn.fetch(query, f"operator-{node_name}", limit)
        return result


# 2. TX Log (top-txlog.bash equivalent)
async def get_top_txlog(node_name="node0", limit=40):
    await ensure_pool()
    async with DB_POOL.acquire() as conn:
        query = """
        WITH l AS (
          SELECT *,
              CASE
                WHEN event_kind IS NULL THEN 'NO_TX'
                WHEN event_kind = 0 THEN 'PARTIAL_FILL'
                WHEN event_kind = 1 THEN 'COMPLETE_FILL'
                WHEN event_kind = 2 THEN 'POST'
                WHEN event_kind = 3 THEN 'CANCEL'
                WHEN event_kind = 30 THEN 'CANCEL_ALL'
                WHEN event_kind = 4 THEN 'LIQUIDATION'
                WHEN event_kind = 5 THEN 'STRATEGY_UPDATE'
                WHEN event_kind = 6 THEN 'TRADER_UPDATE'
                WHEN event_kind = 7 THEN 'WITHDRAW'
                WHEN event_kind = 8 THEN 'WITHDRAW_DDX'
                WHEN event_kind = 9 THEN 'PRICE_CHECKPOINT'
                WHEN event_kind = 10 THEN 'PNL_REALIZATION'
                WHEN event_kind = 11 THEN 'FUNDING'
                WHEN event_kind = 12 THEN 'TRADE_MINING'
                WHEN event_kind = 13 THEN 'SPECS_UPDATE'
                WHEN event_kind = 14 THEN 'INSURANCE_FUND_UPDATE'
                WHEN event_kind = 15 THEN 'INSURANCE_FUND_WITHDRAW'
                WHEN event_kind = 16 THEN 'DISASTER_RECOVERY'
                WHEN event_kind = 60 THEN 'SIGNER_REGISTERED'
                WHEN event_kind = 100 THEN 'EPOCH_MARKER'
                WHEN event_kind = 70 THEN 'FEE_DISTRIBUTION'
                ELSE 'UNKNOWN'
            END kind
         FROM tx_log
        ), p AS (
          SELECT request_index, sequence_busy + sequence_idle AS s,
            exec_total_busy + exec_total_idle AS e,
            exec_trusted_busy + exec_trusted_idle AS t,
            exec_commit_busy + exec_commit_idle AS c,
            exec_finalize_busy + exec_finalize_idle AS f
          FROM stats.perf_request
          WHERE origin = $1
        )
        SELECT l.epoch_id, l.tx_ordinal, l.request_index, l.event_kind, l.kind, 
               round(p.e / 1000::numeric, 2) AS exec_ms
        FROM l
        LEFT JOIN p ON (p.request_index = l.request_index)
        ORDER BY l.epoch_id DESC, l.tx_ordinal DESC
        LIMIT $2
        """
        result = await conn.fetch(query, f"operator-{node_name}", limit)
        return result


# 3. Aggregate Performance KPIs (stats-requests.bash equivalent)
async def get_stats_requests(node_name="node0"):
    await ensure_pool()
    async with DB_POOL.acquire() as conn:
        query = """
        WITH r AS (
          SELECT q.request_index,
            CASE
                WHEN topic = 0 THEN 'ORDER'
                WHEN topic = 1 THEN 'CANCEL_ORDER'
                WHEN topic = 3 THEN 'CANCEL_ALL'
                WHEN topic = 4 THEN 'WITHDRAW'
                WHEN topic = 5 THEN 'WITHDRAW_DDX'
                WHEN topic = 6 THEN 'INSURANCE_FUND_WITHDRAW'
                WHEN topic = 2 THEN 'UPDATE_PROFILE'
                WHEN topic = 50 THEN 'BLOCK'
                WHEN topic = 51 THEN 'ADVANCE_SETTLEMENT_EPOCH'
                WHEN topic = 53 THEN 'MINT_PRICE_CHECKPOINT'
                WHEN topic = 54 THEN 'ADVANCE_TIME'
                WHEN topic = 60 THEN 'ADVANCE_EPOCH'
                WHEN topic = 71 THEN 'PRICE'
                WHEN topic = 80 THEN 'DISASTER_RECOVERY'
                WHEN topic = 99 THEN 'GENESIS'
                ELSE 'UNKNOWN'
            END kind,
              CASE
                WHEN event_kind IS NULL THEN 'NO_TX'
                WHEN event_kind = 0 THEN 'PARTIAL_FILL'
                WHEN event_kind = 1 THEN 'COMPLETE_FILL'
                WHEN event_kind = 2 THEN 'POST'
                WHEN event_kind = 3 THEN 'CANCEL'
                WHEN event_kind = 30 THEN 'CANCEL_ALL'
                WHEN event_kind = 4 THEN 'LIQUIDATION'
                WHEN event_kind = 5 THEN 'STRATEGY_UPDATE'
                WHEN event_kind = 6 THEN 'TRADER_UPDATE'
                WHEN event_kind = 7 THEN 'WITHDRAW'
                WHEN event_kind = 8 THEN 'WITHDRAW_DDX'
                WHEN event_kind = 9 THEN 'PRICE_CHECKPOINT'
                WHEN event_kind = 10 THEN 'PNL_REALIZATION'
                WHEN event_kind = 11 THEN 'FUNDING'
                WHEN event_kind = 12 THEN 'TRADE_MINING'
                WHEN event_kind = 13 THEN 'SPECS_UPDATE'
                WHEN event_kind = 14 THEN 'INSURANCE_FUND_UPDATE'
                WHEN event_kind = 15 THEN 'INSURANCE_FUND_WITHDRAW'
                WHEN event_kind = 16 THEN 'DISASTER_RECOVERY'
                WHEN event_kind = 60 THEN 'SIGNER_REGISTERED'
                WHEN event_kind = 100 THEN 'EPOCH_MARKER'
                WHEN event_kind = 70 THEN 'FEE_DISTRIBUTION'
                ELSE 'UNKNOWN'
            END evt
          FROM request.queue q
          LEFT JOIN tx_log l ON (q.request_index = l.request_index)
          WHERE created_at >= NOW() - INTERVAL '24 hours'
        ), p AS (
          SELECT request_index, sequence_busy + sequence_idle AS s,
            exec_total_busy + exec_total_idle AS e,
            exec_trusted_busy + exec_trusted_idle AS t,
            exec_commit_busy + exec_commit_idle AS c,
            exec_finalize_busy + exec_finalize_idle AS f
          FROM stats.perf_request
          WHERE origin = $1
        )
        SELECT coalesce(r.kind, 'ALL') AS kind,
            r.evt,
            count(1) AS cpt,
            round(avg(s) / 1000::numeric, 2) AS seq_ms,
            sum(CASE WHEN e IS NOT NULL THEN 1 ELSE 0 END) AS cpt_ex,
            round(avg(e) / 1000::numeric, 2) AS exec_ms,
            round(avg(t / e::numeric) * 100, 2) AS t_pct,
            round(avg(c / e::numeric) * 100, 2) AS c_pct,
            round(avg(f / e::numeric) * 100, 2) AS f_pct
          FROM p
        INNER JOIN r ON (p.request_index = r.request_index)
        GROUP BY ROLLUP (r.kind, r.evt)
        ORDER BY r.kind, r.evt
        """
        result = await conn.fetch(query, f"operator-{node_name}")
        return result


# 4. System KPIs (top equivalent)
def get_system_stats():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        load_avg = psutil.getloadavg()

        return {
            "cpu_percent": cpu_percent,
            "memory_total": memory.total // (1024**3),  # GB
            "memory_used": memory.used // (1024**3),  # GB
            "memory_percent": memory.percent,
            "disk_total": disk.total // (1024**3),  # GB
            "disk_used": disk.used // (1024**3),  # GB
            "disk_percent": (disk.used / disk.total) * 100,
            "load_1min": load_avg[0],
            "load_5min": load_avg[1],
            "load_15min": load_avg[2],
        }
    except Exception as e:
        return {"error": str(e)}


async def get_epoch_bin_data(node_name="node0", bin_size=20):
    await ensure_pool()
    async with DB_POOL.acquire() as conn:
        # conn = await get_direct_db_connection()
        query = """
        WITH binned_data AS (
          SELECT 
            CASE
              WHEN event_kind = 0 THEN 'partial_fill'
              WHEN event_kind = 1 THEN 'complete_fill'
              WHEN event_kind = 2 THEN 'post'
              WHEN event_kind = 3 THEN 'cancel'
              WHEN event_kind = 30 THEN 'cancel_all'
              WHEN event_kind = 4 THEN 'liquidation'
              WHEN event_kind = 5 THEN 'strategy_update'
              WHEN event_kind = 6 THEN 'trader_update'
              WHEN event_kind = 7 THEN 'withdraw'
              WHEN event_kind = 8 THEN 'withdraw_ddx'
              WHEN event_kind = 9 THEN 'price_checkpoint'
              WHEN event_kind = 10 THEN 'pnl_realization'
              WHEN event_kind = 11 THEN 'funding'
              WHEN event_kind = 17 THEN 'futures_expiry'
              WHEN event_kind = 12 THEN 'trade_mining'
              WHEN event_kind = 13 THEN 'specs_update'
              WHEN event_kind = 18 THEN 'tradable_product_update'
              WHEN event_kind = 14 THEN 'insurance_fund_update'
              WHEN event_kind = 15 THEN 'insurance_fund_withdraw'
              WHEN event_kind = 16 THEN 'disaster_recovery'
              WHEN event_kind = 60 THEN 'signer_registered'
              WHEN event_kind = 100 THEN 'epoch_marker'
              WHEN event_kind = 70 THEN 'fee_distribution'
              WHEN event_kind = 999 THEN 'no_transition'
              ELSE 'unknown'
            END as event_name,
            (epoch_id / $1) * $1 as bin_start
          FROM tx_log
          WHERE event_kind NOT IN (100, 60)
        )
        SELECT 
          event_name,
          bin_start,
          COUNT(*) as frequency
        FROM binned_data
        GROUP BY event_name, bin_start
        ORDER BY bin_start, event_name;
        """

        result = await conn.fetch(query, bin_size)
        return result


# UI Components using MonsterUI
def format_timestamp(dt):
    if dt:
        return dt.strftime("%m-%d %H:%M:%S")
    return ""


def create_requests_table(data, title="Top Requests"):
    if not data:
        return Card(H4(title), P("No data available", cls=TextPresets.muted_sm))

    rows = []
    for record in data:
        formatted_time = format_timestamp(record.get("created_at"))
        exec_time = record.get("exec_ms")
        exec_display = f"{exec_time} ms" if exec_time else "-"

        rows.append(
            Tr(
                Td(formatted_time, cls=TextT.sm),
                Td(str(record.get("request_index", "")), cls=TextT.sm),
                Td(record.get("kind", ""), cls=TextT.sm),
                Td(exec_display, cls=TextT.sm),
            )
        )

    return Card(
        H4(title),
        Table(
            Thead(
                Tr(
                    Th("created_at", cls=TextT.sm),
                    Th("request_index", cls=TextT.sm),
                    Th("kind", cls=TextT.sm),
                    Th("exec_ms", cls=TextT.sm),
                )
            ),
            Tbody(*rows),
            cls=(TableT.striped, TableT.sm),
        ),
        cls="h-96 overflow-y-auto",
    )


def create_txlog_table(data):
    if not data:
        return Card(H4("TX Log"), P("No data available", cls=TextPresets.muted_sm))

    rows = []
    for record in data:
        exec_time = record.get("exec_ms")
        exec_display = f"{exec_time} ms" if exec_time else "-"

        rows.append(
            Tr(
                Td(str(record.get("epoch_id", "")), cls=TextT.sm),
                Td(str(record.get("tx_ordinal", "")), cls=TextT.sm),
                Td(str(record.get("request_index", "")), cls=TextT.sm),
                Td(record.get("kind", ""), cls=TextT.sm),
                Td(exec_display, cls=TextT.sm),
            )
        )

    return Card(
        H4("TX Log"),
        Table(
            Thead(
                Tr(
                    Th("epoch_id", cls=TextT.sm),
                    Th("tx_ordinal", cls=TextT.sm),
                    Th("request_index", cls=TextT.sm),
                    Th("kind", cls=TextT.sm),
                    Th("exec_ms", cls=TextT.sm),
                )
            ),
            Tbody(*rows),
            cls=(TableT.striped, TableT.sm),
        ),
        cls="h-96 overflow-y-auto",
    )


def create_stats_table(data):
    if not data:
        return Card(
            H4("Performance Stats"), P("No data available", cls=TextPresets.muted_sm)
        )

    rows = []
    for record in data:
        if not record.get("kind"):  # Skip rollup rows without kind
            continue

        rows.append(
            Tr(
                Td(record.get("kind", ""), cls=TextT.sm),
                Td(record.get("evt", ""), cls=TextT.sm),
                Td(str(record.get("cpt", "")), cls=TextT.sm),
                Td(
                    f"{record.get('seq_ms', 0)} ms" if record.get("seq_ms") else "-",
                    cls=TextT.sm,
                ),
                Td(str(record.get("cpt_ex", "")), cls=TextT.sm),
                Td(
                    f"{record.get('exec_ms', 0)} ms" if record.get("exec_ms") else "-",
                    cls=TextT.sm,
                ),
                Td(
                    f"{record.get('t_pct', 0)}%" if record.get("t_pct") else "-",
                    cls=TextT.sm,
                ),
                Td(
                    f"{record.get('c_pct', 0)}%" if record.get("c_pct") else "-",
                    cls=TextT.sm,
                ),
                Td(
                    f"{record.get('f_pct', 0)}%" if record.get("f_pct") else "-",
                    cls=TextT.sm,
                ),
            )
        )

    return Card(
        H4("Performance Stats (24h)"),
        Table(
            Thead(
                Tr(
                    Th("kind", cls=TextT.sm),
                    Th("evt", cls=TextT.sm),
                    Th("cpt", cls=TextT.sm),
                    Th("seq_ms", cls=TextT.sm),
                    Th("cpt_ex", cls=TextT.sm),
                    Th("exec_ms", cls=TextT.sm),
                    Th("t%", cls=TextT.sm),
                    Th("c%", cls=TextT.sm),
                    Th("f%", cls=TextT.sm),
                )
            ),
            Tbody(*rows),
            cls=(TableT.striped, TableT.sm),
        ),
    )


def create_system_stats_card(data):
    if "error" in data:
        return Card(
            H4("System Stats"), P("System stats unavailable", cls=TextPresets.muted_sm)
        )

    return Card(
        H4("System Stats"),
        Grid(
            Div(
                Strong("CPU"),
                Br(),
                P(f"{data.get('cpu_percent', 0):.1f}%", cls=TextT.lg),
            ),
            Div(
                Strong("Memory"),
                Br(),
                P(
                    f"{data.get('memory_used', 0)}/{data.get('memory_total', 0)} GB",
                    cls=TextT.sm,
                ),
                P(f"({data.get('memory_percent', 0):.1f}%)", cls=TextPresets.muted_sm),
            ),
            Div(
                Strong("Disk"),
                Br(),
                P(
                    f"{data.get('disk_used', 0)}/{data.get('disk_total', 0)} GB",
                    cls=TextT.sm,
                ),
                P(f"({data.get('disk_percent', 0):.1f}%)", cls=TextPresets.muted_sm),
            ),
            Div(
                Strong("Load Avg"),
                Br(),
                P(f"1m: {data.get('load_1min', 0):.2f}", cls=TextT.sm),
                P(f"5m: {data.get('load_5min', 0):.2f}", cls=TextT.sm),
                P(f"15m: {data.get('load_15min', 0):.2f}", cls=TextT.sm),
            ),
            cols=2,
        ),
    )


def create_epoch_bin_chart(data):
    if not data:
        return Card(H4("Transaction Events Analysis"), P("No data available"))

    df = pd.DataFrame([dict(record) for record in data])
    pivot_df = df.pivot_table(
        index="bin_start", columns="event_name", values="frequency", fill_value=0
    )

    fig = px.bar(pivot_df, title="Transaction Events by Epoch Bin")

    return Card(
        H4("Transaction Events Analysis"),
        Div(NotStr(fig.to_html(include_plotlyjs="cdn")), cls="w-full"),
        cls="w-full",
    )


# FastHTML App
app, rt = fast_app(hdrs=Theme.blue.headers())


@rt("/current-time")
async def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@rt("/requests-data")
async def requests_data():
    node_name = "node0"
    top_requests_data = await get_top_requests(node_name, 20)
    return create_requests_table(top_requests_data)


@rt("/txlog-data")
async def txlog_data():
    node_name = "node0"
    txlog_data = await get_top_txlog(node_name, 20)
    return create_txlog_table(txlog_data)


@rt("/stats-data")
async def stats_data():
    node_name = "node0"
    stats_data = await get_stats_requests(node_name)
    return create_stats_table(stats_data)


@rt("/system-data")
async def system_data():
    system_data = get_system_stats()
    return create_system_stats_card(system_data)


@rt("/transaction-events-by-epoch-bin")
async def transaction_events_by_epoch_bin_data():
    transaction_events_by_epoch_bin_data = await get_epoch_bin_data()
    return create_epoch_bin_chart(transaction_events_by_epoch_bin_data)


@rt
async def index():
    node_name = "node0"

    # Gather all data
    try:
        (
            top_requests_data,
            txlog_data,
            stats_data,
            epoch_bin_data,
        ) = await asyncio.gather(
            get_top_requests(node_name, 20),
            get_top_txlog(node_name, 20),
            get_stats_requests(node_name),
            get_epoch_bin_data(node_name),
        )
        system_data = get_system_stats()

        # Create components
        requests_table = create_requests_table(top_requests_data)
        txlog_table = create_txlog_table(txlog_data)
        stats_table = create_stats_table(stats_data)
        system_card = create_system_stats_card(system_data)
        epoch_bin_data_card = create_epoch_bin_chart(epoch_bin_data)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return Container(
            DivFullySpaced(
                H1("Operator Monitoring Dashboard"),
                P(
                    f"Last updated: {current_time}",
                    cls=TextPresets.muted_sm,
                    hx_get="/current-time",
                    hx_trigger="every 5s",
                ),
            ),
            # Top row: requests and txlog (2 columns)
            Grid(
                Div(requests_table, hx_get="/requests-data", hx_trigger="every 5s"),
                Div(txlog_table, hx_get="/txlog-data", hx_trigger="every 5s"),
                cols=2,
                gap=4,
            ),
            # Middle row: stats table (full width)
            Div(stats_table, hx_get="/stats-data", hx_trigger="every 5s"),
            # Middle row: stats table (full width)
            Div(system_card, hx_get="/system-data", hx_trigger="every 5s"),
            # Bottom row: epoch bin chart (full width)
            Div(
                epoch_bin_data_card,
                hx_get="/transaction-events-by-epoch-bin",
                hx_trigger="every 5s",
            ),
            cls=(ContainerT.xl, "space-y-4"),
        )

    except Exception as e:
        return Container(
            H1("Operator Monitoring Dashboard"),
            Alert(f"Error loading data: {str(e)}", cls=AlertT.error),
        )


if __name__ == "__main__":
    serve()
