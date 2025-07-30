# file: projects/ocpp/csms.py
# web.app path: ocpp/csms/

import json
import os
import shutil
import time
import uuid
import traceback
import asyncio
import html
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from bottle import request, redirect, HTTPError

from gway import gw

    
def setup_app(*,
    app=None,
    location=None,
    authorize=None,
    email=None,
    auth="disabled",
):
    global _active_cons, _msg_log
    # no globals needed here; dictionaries are modified in-place
    email = email if isinstance(email, str) else (gw.resolve('[ADMIN_EMAIL]') if email else email)

    auth_required = str(auth).strip().lower() not in {
        "none", "false", "disabled", "optional"
    }

    oapp = app
    from fastapi import FastAPI as _FastAPI
    match app:
        case _FastAPI() as f:
            app = f
            _is_new_app = False
        case list() | tuple() as seq:
            app = next((x for x in seq if isinstance(x, _FastAPI)), None)
            _is_new_app = app is None
        case None:
            _is_new_app = True
        case _ if isinstance(app, _FastAPI):
            _is_new_app = False
        case _ if hasattr(app, "__iter__") and not isinstance(app, (str, bytes, bytearray)):
            app = next((x for x in app if isinstance(x, _FastAPI)), None)
            _is_new_app = app is None
        case _:
            _is_new_app = app is None or not isinstance(app, _FastAPI)
    if _is_new_app:
        app = _FastAPI()
        # Reset lingering connection states
        try:
            gw.ocpp.data.reset_connections()
        except Exception as exc:
            gw.warn(f"[OCPP] Failed to reset connections: {exc}")

    validator = None
    if isinstance(authorize, str):
        validator = gw[authorize]
    elif callable(authorize):
        validator = authorize

    @app.websocket("/{path:path}")
    async def websocket_ocpp(websocket: WebSocket, path: str):
        global _csms_loop, _active_cons, _msg_log
        if auth_required:
            if not gw.web.auth.check_websocket_auth(websocket):
                await websocket.close(code=4401, reason="Unauthorized")
                gw.warn(f"[OCPP] Unauthorized WebSocket connection attempt for charger_id={path}")
                return

        g = globals()
        g.setdefault("_active_cons", {})
        g.setdefault("_msg_log", {})

        _csms_loop = asyncio.get_running_loop()
        charger_id = path.strip("/").split("/")[-1]
        gw.info(f"[OCPP] WebSocket connected: charger_id={charger_id}")

        def call_authorize(payload, action):
            if not validator:
                return True
            try:
                return bool(
                    validator(
                        payload=payload,
                        charger_id=charger_id,
                        action=action,
                    )
                )
            except Exception as e:
                gw.error(f"[OCPP] authorization failed: {e}")
                gw.debug(traceback.format_exc())
                return False

        protos = websocket.headers.get("sec-websocket-protocol", "").split(",")
        protos = [p.strip() for p in protos if p.strip()]
        if "ocpp1.6" in protos:
            await websocket.accept(subprotocol="ocpp1.6")
        else:
            await websocket.accept()

        _active_cons[charger_id] = websocket
        gw.ocpp.data.set_connection_status(charger_id, True)
        tx_data = None

        try:
            while True:
                raw = await websocket.receive_text()
                gw.info(f"[OCPP:{charger_id}] → {raw}")
                gw.ocpp.data.record_last_msg(charger_id)
                globals().setdefault("_msg_log", {}).setdefault(charger_id, []).append(f"> {raw}")
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    gw.warn(f"[OCPP:{charger_id}] Received non-JSON message: {raw!r}")
                    continue

                if isinstance(msg, list) and msg[0] == 2:
                    message_id, action = msg[1], msg[2]
                    payload = msg[3] if len(msg) > 3 else {}
                    gw.debug(f"[OCPP:{charger_id}] Action={action} Payload={payload}")

                    response_payload = {}

                    if action == "Authorize":
                        status = "Accepted" if call_authorize(payload, action) else "Rejected"
                        response_payload = {"idTagInfo": {"status": status}}

                    elif action == "BootNotification":
                        response_payload = {
                            "currentTime": datetime.utcnow().isoformat() + "Z",
                            "interval": 300,
                            "status": "Accepted"
                        }

                    elif action == "Heartbeat":
                        response_payload = {"currentTime": datetime.utcnow().isoformat() + "Z"}
                        gw.ocpp.data.record_heartbeat(charger_id, response_payload["currentTime"])

                    elif action == "StartTransaction":
                        if not call_authorize(payload, action):
                            response_payload = {"transactionId": 0, "idTagInfo": {"status": "Rejected"}}
                        else:
                            now = int(time.time())
                            transaction_id = now
                            tx_data = {
                                "connectorId": payload.get("connectorId"),
                                "idTagStart": payload.get("idTag"),
                                "meterStart": payload.get("meterStart"),
                                "reservationId": payload.get("reservationId", -1),
                                "startTime": now,
                                "startTimeStr": datetime.utcfromtimestamp(now).isoformat() + "Z",
                                "startMs": int(time.time() * 1000) % 1000,
                                "transactionId": transaction_id,
                                "MeterValues": []
                            }
                            cp_ts = None
                            if payload.get("timestamp"):
                                try:
                                    cp_ts = int(datetime.fromisoformat(payload["timestamp"].rstrip("Z")).timestamp())
                                except Exception:
                                    cp_ts = None
                            gw.ocpp.data.record_transaction_start(
                                charger_id,
                                transaction_id,
                                now,
                                id_tag=payload.get("idTag"),
                                vin=payload.get("vin"),
                                validator=getattr(validator, "__name__", None) if validator else None,
                                meter_start=payload.get("meterStart"),
                                charger_timestamp=cp_ts,
                            )
                            response_payload = {
                                "transactionId": transaction_id,
                                "idTagInfo": {"status": "Accepted"}
                            }

                        if email:
                            subject = f"OCPP: Charger {charger_id} STARTED transaction {transaction_id}"
                            body = (
                                f"Charging session started.\n"
                                f"Charger: {charger_id}\n"
                                f"idTag: {payload.get('idTag')}\n"
                                f"Connector: {payload.get('connectorId')}\n"
                                f"Start Time: {datetime.utcfromtimestamp(now).isoformat()}Z\n"
                                f"Transaction ID: {transaction_id}\n"
                                f"Meter Start: {payload.get('meterStart')}\n"
                                f"Reservation ID: {payload.get('reservationId', -1)}"
                            )
                            gw.mail.send(subject, body, to=email)

                    elif action == "MeterValues":

                        if tx_data:
                            for entry in payload.get("meterValue", []):
                                ts = entry.get("timestamp")
                                ts_epoch = (
                                    int(datetime.fromisoformat(ts.rstrip("Z")).timestamp())
                                    if ts else int(time.time())
                                )
                                sampled = []
                                for sv in entry.get("sampledValue", []):
                                    val = sv.get("value")
                                    unit = sv.get("unit", "")
                                    measurand = sv.get("measurand", "")
                                    try:
                                        fval = float(val)
                                        if unit == "Wh":
                                            fval = fval / 1000.0
                                        sampled.append({
                                            "value": fval,
                                            "unit": "kWh" if unit == "Wh" else unit,
                                            "measurand": measurand,
                                            "context": sv.get("context", ""),
                                        })
                                        gw.ocpp.data.record_meter_value(
                                            charger_id,
                                            tx_data.get("transactionId"),
                                            ts_epoch,
                                            measurand,
                                            fval,
                                            "kWh" if unit == "Wh" else unit,
                                            sv.get("context", ""),
                                        )
                                    except Exception:
                                        continue
                                tx_data["MeterValues"].append({
                                    "timestamp": ts_epoch,
                                    "timestampStr": datetime.utcfromtimestamp(ts_epoch).isoformat() + "Z",
                                    "timeMs": int(time.time() * 1000) % 1000,
                                    "sampledValue": sampled,
                                })
                        response_payload = {}

                    elif action == "StopTransaction":
                        now = int(time.time())
                        if tx_data:
                            if tx_data.get("MeterValues"):
                                try:
                                    archive_energy(charger_id, tx_data["transactionId"], tx_data["MeterValues"])
                                except Exception as e:
                                    gw.error("Error recording energy chart.")
                                    gw.exception(e)
                            tx_data.update({
                                "idTagStop": payload.get("idTag"),
                                "meterStop": payload.get("meterStop"),
                                "stopTime": now,
                                "stopTimeStr": datetime.utcfromtimestamp(now).isoformat() + "Z",
                                "stopMs": int(time.time() * 1000) % 1000,
                                "reason": 4,
                                "reasonStr": "Local",
                            })
                            cp_stop = None
                            if payload.get("timestamp"):
                                try:
                                    cp_stop = int(datetime.fromisoformat(payload["timestamp"].rstrip("Z")).timestamp())
                                except Exception:
                                    cp_stop = None
                            gw.ocpp.data.record_transaction_stop(
                                charger_id,
                                tx_data.get("transactionId"),
                                now,
                                meter_stop=payload.get("meterStop"),
                                reason="Local",
                                charger_timestamp=cp_stop,
                            )
                            archive_transaction(charger_id, tx_data)
                            if location:
                                file_path = gw.resource(
                                    "work", "etron", "records", location,
                                    f"{charger_id}_{tx_data['transactionId']}.dat"
                                )
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                with open(file_path, "w") as f:
                                    json.dump(tx_data, f, indent=2)
                            tx_data = None
                        response_payload = {"idTagInfo": {"status": "Accepted"}}

                    elif action == "StatusNotification":
                        status = payload.get("status")
                        error_code = payload.get("errorCode")
                        info = payload.get("info", "")
                        if is_abnormal_status(status, error_code):
                            gw.ocpp.data.update_status(charger_id, status, error_code, info)
                            gw.warn(f"[OCPP] Abnormal status for {charger_id}: {status}/{error_code} - {info}")
                            gw.ocpp.data.record_error(charger_id, status, error_code, info)
                        else:
                            gw.ocpp.data.clear_status(charger_id)
                            gw.info(f"[OCPP] Status normalized for {charger_id}: {status}/{error_code}")
                        response_payload = {}

                    else:
                        response_payload = {"status": "Accepted"}

                    response = [3, message_id, response_payload]
                    gw.info(f"[OCPP:{charger_id}] ← {action} => {response_payload}")
                    await websocket.send_text(json.dumps(response))

                elif isinstance(msg, list) and msg[0] == 3:
                    # Handle CALLRESULT
                    continue

                elif isinstance(msg, list) and msg[0] == 4:
                    gw.info(f"[OCPP:{charger_id}] Received CALLERROR: {msg}")
                    continue

                else:
                    gw.warn(f"[OCPP:{charger_id}] Invalid or unsupported message format: {msg}")

        except WebSocketDisconnect:
            gw.info(f"[OCPP:{charger_id}] WebSocket disconnected")
        except Exception as e:
            gw.error(f"[OCPP:{charger_id}] WebSocket failure: {e}")
            gw.debug(traceback.format_exc())
        finally:
            # Mark the connection as offline but retain the record
            acons = globals().get("_active_cons", {})
            if charger_id in acons:
                gw.warning(f"[OCPP] {charger_id}")
                acons[charger_id] = None
            gw.ocpp.data.set_connection_status(charger_id, False)

    return (app if not oapp else (oapp, app)) if _is_new_app else oapp

...

def is_abnormal_status(status: str, error_code: str) -> bool:
    """Determine if a status/errorCode is 'abnormal' per OCPP 1.6."""
    status = (status or "").capitalize()
    error_code = (error_code or "").capitalize()
    # Available/NoError or Preparing are 'normal'
    if status in ("Available", "Preparing") and error_code in ("Noerror", "", None):
        return False
    # All Faulted, Unavailable, Suspended, etc. are abnormal
    if status in ("Faulted", "Unavailable", "Suspendedev", "Suspended", "Removed"):
        return True
    if error_code not in ("Noerror", "", None):
        return True
    return False

def get_charger_state(cid, tx, raw_hb):
    """
    Determine charger state for status stripe and text.

    - ``error``: abnormal status reported by charger
    - ``online``: connection active with an open transaction
    - ``available``: connection active but idle/no transaction
    - ``offline``: charger known but currently disconnected
    - ``unknown``: no record of this charger yet
    """
    conn_info = gw.ocpp.data.get_connection(cid) or {}
    if conn_info.get("status"):
        return "error"

    connected = bool(conn_info.get("connected"))
    last_msg = conn_info.get("last_msg")
    if tx and last_msg and time.time() - int(last_msg) > 60:
        return "unknown"

    if connected:
        if tx and not tx.get("syncStop"):
            return "online"
        return "available"

    if conn_info:
        return "offline"
    return "unknown"

...

def _render_card_controls(cid):
    return f'''
            <form method="post" action="" class="charger-action-form">
              <input type="hidden" name="charger_id" value="{cid}">
              <select name="action" id="action-{cid}" aria-label="Action">
                <option value="remote_stop">Stop</option>
                <option value="reset_soft">Soft Reset</option>
                <option value="reset_hard">Hard Reset</option>
                <option value="disconnect">Disconnect</option>
              </select>
              <div class="charger-actions-btns">
                <button type="submit" name="do" value="send">Send</button>
                <a href="/ocpp/csms/energy-graph?charger_id={cid}" class="graph-btn" target="_blank">Graph</a>
              </div>
            </form>
    '''

def _render_card_link(cid):
    return (
        '<div class="charger-actions-btns">'
        f'<a href="/ocpp/csms/charger-detail?charger_id={cid}" class="graph-btn">Details</a>'
        '</div>'
    )

def _render_charger_card(cid, tx, state, raw_hb, *, show_controls=True):
    """Render a charger card with the appropriate status stripe."""
    from datetime import datetime

    status_class = f"status-{state}"
    tx_id       = tx.get("transactionId") if tx else '-'
    meter_start = tx.get("meterStart") if tx else '-'
    id_tag      = tx.get("idTag") if tx else '-'
    latest      = (
        tx.get("meterStop")
        if tx and tx.get("meterStop") is not None
        else (tx["MeterValues"][-1].get("meter") if tx and tx.get("MeterValues") else 'None')
    )
    power  = power_consumed(tx)
    if state == "online":
        status = "Charging"
    elif state == "available":
        status = "Available"
    elif state == "error":
        status = "Error"
    else:
        status = "Offline"
    latest_hb = "-"
    if raw_hb:
        try:
            dt = datetime.fromisoformat(str(raw_hb).replace("Z", "+00:00"))
            latest_hb = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                dt = datetime.utcfromtimestamp(int(float(raw_hb)))
                latest_hb = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                latest_hb = str(raw_hb)

    conn = gw.ocpp.data.get_connection(cid) or {}
    last_msg_ts = conn.get("last_msg")
    if last_msg_ts:
        try:

            last_updated = (
                datetime.utcfromtimestamp(int(float(last_msg_ts))).isoformat() + "Z"
            )
        except Exception:
            last_updated = str(last_msg_ts)
    else:
        last_updated = "-"

    controls_html = _render_card_controls(cid) if show_controls else _render_card_link(cid)
    details_html = ''

    return f'''
    <div class="charger-card {status_class}" id="charger-{cid}">
      <input type="hidden" name="last_updated" value="{last_updated}">
      <table class="charger-layout">
        <tr>
          <td class="charger-info-td">
            <table class="charger-info-table">
              <colgroup>
                <col class="label-col">
                <col class="value-col">
                <col class="label-col">
                <col class="value-col">
              </colgroup>
              <tr>
                <td class="label">ID</td>
                <td class="value">{cid}</td>
                <td class="label">TXN</td>
                <td class="value">{tx_id}</td>
              </tr>
              <tr>
                <td class="label">RFID</td>
                <td class="value" colspan="3">{id_tag}</td>
              </tr>
              <tr>
                <td class="label">Start</td>
                <td class="value">{meter_start}</td>
                <td class="label">Latest</td>
                <td class="value">{latest}</td>
              </tr>
              <tr>
                <td class="label">kWh.</td>
                <td class="value">{power}</td>
                <td class="label">Last HB</td>
                <td class="value">{latest_hb}</td>
              </tr>
              <tr>
                <td class="label">Updated</td>
                <td class="value">{last_updated}</td>
                <td class="label">Status</td>
                <td class="value">{status}</td>
              </tr>
            </table>
          </td>
          <td class="charger-actions-td">
            {controls_html}
          </td>
        </tr>
      </table>
      {details_html}
    </div>
    '''

def view_active_chargers(*, action=None, charger_id=None, **_):
    """
    Card-based OCPP dashboard: summary of currently active chargers.
    Renders <div id="charger-list" gw-render="charger_list" gw-refresh="5">
    so the client can periodically refresh the list via render.js.
    """
    global _active_cons, _msg_log
    msg = ""
    gw.debug(
        f"[view_active_chargers] start: action={action} charger_id={charger_id}"
    )
    if request.method == "POST":
        action = request.forms.get("action")
        charger_id = request.forms.get("charger_id")
        if action and charger_id:
            try:
                dispatch_action(charger_id, action)
                msg = f"Action {action} sent"
            except Exception as e:
                gw.error(f"Failed to dispatch action {action} to {charger_id}: {e}")
                msg = f"Error: {e}"

    txs = gw.ocpp.data.get_active_transactions()
    db_active = gw.ocpp.data.get_active_chargers()
    gw.debug(f"[view_active_chargers] active_db={db_active}")
    gw.debug(f"[view_active_chargers] transactions={list(txs.keys())}")

    all_chargers = set(db_active) | set(txs)
    gw.debug(
        f"[view_active_chargers] all_chargers={sorted(all_chargers)}"
    )
    html = [
        '<link rel="stylesheet" href="/static/ocpp/csms/charger_status.css">',
        '<script src="/static/render.js"></script>',
        '<script src="/static/ocpp/csms/charger_status.js"></script>',
        "<h1>OCPP Status Dashboard</h1>"
    ]
    if msg:
        html.append(f'<p class="error">{msg}</p>')


    # Abnormal status warning
    ab_status = {
        cid: info
        for cid in all_chargers
        if (info := gw.ocpp.data.get_connection(cid)) and info.get("status")
    }
    if ab_status:
        html.append(
            '<div class="ocpp-alert">'
            "⚠️ Abnormal Charger Status Detected:<ul>"
        )
        for cid, err in sorted(ab_status.items()):
            status = err.get("status", "")
            error_code = err.get("errorCode", "")
            info = err.get("info", "")
            ts = err.get("timestamp", "")
            msg = f"<b>{cid}</b>: {status}/{error_code}"
            if info: msg += f" ({info})"
            if ts: msg += f" <span class='timestamp'>@{ts}</span>"
            html.append(f"<li>{msg}</li>")
        html.append("</ul></div>")

    # --- The key block for autorefresh ---
    html.append(
        '<div id="charger-list" gw-render="charger_list" gw-refresh="5" gw-click="refresh">'
    )
    if not all_chargers:
        html.append('<p><em>No chargers connected or transactions seen yet.</em></p>')
    else:
        for cid in sorted(all_chargers):
            tx = txs.get(cid)
            conn_info = gw.ocpp.data.get_connection(cid) or {}
            raw_hb = conn_info.get("last_heartbeat")
            state = get_charger_state(cid, tx, raw_hb)
            html.append(_render_charger_card(cid, tx, state, raw_hb, show_controls=False))
    html.append('</div>')

    ws_url = gw.web.build_ws_url()
    html.append(f"""
    <div class="ocpp-wsbar">
      <input type="text" id="ocpp-ws-url" value="{ws_url}" readonly
        style="flex:1;font-family:monospace;font-size:1em;
               padding:10px 6px;background:#222;color:#fff;
               border:1px solid #333;border-radius:5px;min-width:160px;max-width:530px;"/>
      <button id="copy-ws-url-btn"
        style="padding:6px 16px;font-size:1em;border-radius:5px;
               border:1px solid #444;background:#444;color:#fff;cursor:pointer">
        Copy
      </button>
      <a href="/ocpp/evcs/cp-simulator" style="margin-left:1.3em">Simulator</a>
    </div>
    """)
    return "".join(html)

def render_charger_list(**kwargs):
    """
    Regenerate the full charger list HTML (all cards).
    No parsing of incoming HTML; just returns a new block of HTML for charger-list.
    Called via POST (or GET) from render.js, possibly with params in kwargs.
    """
    global _active_cons, _msg_log
    gw.debug("[OCPP] Render CL")
    txs = gw.ocpp.data.get_active_transactions()
    db_active = gw.ocpp.data.get_active_chargers()
    all_chargers = set(db_active) | set(txs)
    html = []
    if not all_chargers:
        html.append('<p><em>No chargers connected or transactions seen yet.</em></p>')
    else:
        for cid in sorted(all_chargers):
            tx = txs.get(cid)
            conn_info = gw.ocpp.data.get_connection(cid) or {}
            raw_hb = conn_info.get("last_heartbeat")
            state = get_charger_state(cid, tx, raw_hb)
            html.append(_render_charger_card(cid, tx, state, raw_hb, show_controls=False))
    return "\n".join(html)

def view_charger_detail(*, charger_id=None, **_):
    """Detail view for a single charger with live log."""
    if not charger_id:
        return redirect("/ocpp/csms/active-chargers")
    # Allow viewing details even if the charger hasn't connected yet.
    # If the ID truly doesn't exist we simply render an empty placeholder
    # instead of redirecting back to the dashboard.

    msg = ""
    if request.method == "POST":
        action = request.forms.get("action")
        if action:
            try:
                dispatch_action(charger_id, action)
                msg = f"Action {action} sent"
            except Exception as e:
                gw.error(f"Failed to dispatch action {action} to {charger_id}: {e}")
                msg = f"Error: {e}"

    tx = gw.ocpp.data.get_active_transaction(charger_id)
    conn_info = gw.ocpp.data.get_connection(charger_id) or {}
    raw_hb = conn_info.get("last_heartbeat")
    state = get_charger_state(charger_id, tx, raw_hb)
    now = datetime.utcnow()
    since_default = (now - timedelta(days=1)).date().isoformat()
    until_default = now.date().isoformat()
    since = request.query.get('since') or since_default
    until = request.query.get('until') or until_default

    html = [
        '<link rel="stylesheet" href="/static/ocpp/csms/charger_status.css">',
        '<script src="/static/render.js"></script>',
        f'<h1><a href="/ocpp/csms/active-chargers">All Chargers</a> / {charger_id} Details</h1>'
    ]
    if msg:
        html.append(f'<p class="error">{msg}</p>')

    html.append(
        f'<div id="charger-info" gw-render="charger_info" gw-refresh="5" gw-click="refresh" data-charger-id="{charger_id}">' +
        _render_charger_card(charger_id, tx, state, raw_hb) +
        '</div>'
    )

    html.append(
        f'''<form id="tx-range" method="get">
            <input type="hidden" name="charger_id" value="{charger_id}">
            <label>From:
                <input type="date" name="since" value="{since}">
            </label>
            <label>To:
                <input type="date" name="until" value="{until}">
            </label>
            <button type="submit">Apply</button>
        </form>'''
    )

    html.append(
        f'<div id="charger-transactions" gw-render="charger_transactions" '
        f'data-charger-id="{charger_id}" data-since="{since}" data-until="{until}">' +
        render_charger_transactions(charger_id=charger_id, since=since, until=until) +
        '</div>'
    )

    html.append(
        f'<div id="charger-log" gw-render="charger_log" gw-refresh="2" gw-click="refresh" data-charger-id="{charger_id}">' +
        render_charger_log(charger_id=charger_id) +
        '</div>'
    )

    return "".join(html)

def render_charger_info(*, charger_id=None, chargerId=None, **_):
    cid = charger_id or chargerId
    if not cid:
        return ""
    tx = gw.ocpp.data.get_active_transaction(cid)
    conn_info = gw.ocpp.data.get_connection(cid) or {}
    raw_hb = conn_info.get("last_heartbeat")
    state = get_charger_state(cid, tx, raw_hb)
    return _render_charger_card(cid, tx, state, raw_hb)

def render_charger_log(*, charger_id=None, chargerId=None, **_):
    cid = charger_id or chargerId
    if not cid:
        return ""
    lines = globals().get("_msg_log", {}).get(cid, [])[-50:]
    esc = lambda s: html.escape(s)
    return '<pre>' + '\n'.join(esc(line) for line in lines) + '</pre>'

def render_charger_transactions(*, charger_id=None, chargerId=None, since=None, until=None, **_):
    cid = charger_id or chargerId
    if not cid:
        return ""
    since = since or request.forms.get('since') or request.query.get('since')
    until = until or request.forms.get('until') or request.query.get('until')

    def to_epoch(date_str):
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str)
            if len(date_str) == 10:
                return int(dt.timestamp())
            return int(dt.timestamp())
        except Exception:
            return None

    start_ts = to_epoch(since)
    end_ts = to_epoch(until)
    rows = list(
        gw.ocpp.data.iter_transactions(
            cid,
            start=start_ts,
            end=end_ts,
            sort="start_time",
            order="desc",
            limit=50,
        )
    )

    def fmt(ts):
        if not ts:
            return "-"
        try:
            return datetime.utcfromtimestamp(int(ts)).isoformat() + "Z"
        except Exception:
            return str(ts)

    html = [
        '<table class="ocpp-details">',
        '<tr><th>ID</th><th>Start</th><th>Stop</th><th>Meter Δ(kWh)</th><th>Reason</th></tr>'
    ]
    for r in rows:
        delta = (r[5] or 0) - (r[4] or 0)
        html.append(
            f"<tr><td>{r[1]}</td><td>{fmt(r[2])}</td><td>{fmt(r[3])}</td><td>{round(delta/1000.0,3)}</td><td>{r[6] or ''}</td></tr>"
        )
    html.append('</table>')
    return '\n'.join(html)

...

def dispatch_action(charger_id: str, action: str):
    """
    Dispatch a remote admin action to the charger over OCPP via websocket.
    """
    ws = globals().get("_active_cons", {}).get(charger_id)
    if not ws:
        raise HTTPError(404, "No active connection")
    msg_id = str(uuid.uuid4())

    # Compose and send the appropriate OCPP message for the requested action
    msg_text = None
    if action == "remote_stop":
        tx = gw.ocpp.data.get_active_transaction(charger_id)
        if not tx:
            raise HTTPError(404, "No transaction to stop")
        msg_text = json.dumps([2, msg_id, "RemoteStopTransaction",
                               {"transactionId": tx["transactionId"]}])
        coro = ws.send_text(msg_text)
    elif action.startswith("reset_"):
        _, mode = action.split("_", 1)
        msg_text = json.dumps([2, msg_id, "Reset", {"type": mode.capitalize()}])
        coro = ws.send_text(msg_text)
    elif action == "disconnect":
        coro = ws.close(code=1000, reason="Admin disconnect")
    else:
        raise HTTPError(400, f"Unknown action: {action}")

    loop = globals().get("_csms_loop")
    if loop:
        loop.call_soon_threadsafe(lambda: loop.create_task(coro))
    else:
        gw.warn("No CSMS event loop; action not sent")

    if msg_text:
        globals().setdefault("_msg_log", {}).setdefault(charger_id, []).append(f"< {msg_text}")

    return {"status": "requested", "messageId": msg_id}

...

# Calculation tools

def extract_meter(tx):
    """
    Return the latest Energy.Active.Import.Register (kWh) from MeterValues or meterStop.
    """
    if not tx:
        return "-"
    # Try meterStop first
    if tx.get("meterStop") is not None:
        try:
            return float(tx["meterStop"]) / 1000.0  # assume Wh, convert to kWh
        except Exception:
            return tx["meterStop"]
    # Try MeterValues: last entry, find Energy.Active.Import.Register
    mv = tx.get("MeterValues", [])
    if mv:
        last_mv = mv[-1]
        for sv in last_mv.get("sampledValue", []):
            if sv.get("measurand") == "Energy.Active.Import.Register":
                val = sv.get("value")
                try:
                    val_f = float(val)
                    if sv.get("unit") == "Wh":
                        val_f = val_f / 1000.0
                    return val_f
                except Exception:
                    return val
    elif tx.get("transactionId") is not None and tx.get("charger_id"):
        val = gw.ocpp.data.get_latest_meter_value(
            tx["charger_id"], tx["transactionId"]
        )
        if val is not None:
            return val
    return "-"


def power_consumed(tx):
    """Calculate power consumed in kWh from transaction's meter values (Energy.Active.Import.Register)."""
    if not tx:
        return 0.0

    # Try to use MeterValues if present and well-formed
    meter_values = tx.get("MeterValues", [])
    energy_vals = []
    for entry in meter_values:
        for sv in entry.get("sampledValue", []):
            if sv.get("measurand") == "Energy.Active.Import.Register":
                val = sv.get("value")
                try:
                    val_f = float(val)
                    if sv.get("unit") == "Wh":
                        val_f = val_f / 1000.0
                    energy_vals.append(val_f)
                except Exception:
                    pass

    meter_start = tx.get("meterStart")
    start_val = None
    if energy_vals:
        start_val = energy_vals[0]
    elif meter_start is not None:
        try:
            start_val = float(meter_start) / 1000.0
        except Exception:
            start_val = None

    end_val = None
    if energy_vals:
        end_val = energy_vals[-1]
    elif tx.get("meterStop") is not None:
        try:
            end_val = float(tx["meterStop"]) / 1000.0
        except Exception:
            end_val = None
    elif tx.get("transactionId") is not None and tx.get("charger_id"):
        latest = gw.ocpp.data.get_latest_meter_value(
            tx["charger_id"], tx["transactionId"]
        )
        if latest is not None:
            end_val = latest

    if start_val is not None and end_val is not None:
        return round(end_val - start_val, 3)

    # Fallback to meterStart/meterStop if no sampled values
    meter_stop = tx.get("meterStop")
    # handle int or float or None
    try:
        if meter_start is not None and meter_stop is not None:
            return round(float(meter_stop) / 1000.0 - float(meter_start) / 1000.0, 3)
        if meter_start is not None:
            return 0.0
    except Exception:
        pass

    return 0.0

def archive_energy(charger_id, transaction_id, meter_values):
    """
    Store MeterValues for a charger/transaction as a dated file for graphing.
    """
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    base = gw.resource("work", "etron", "graphs", charger_id)
    os.makedirs(base, exist_ok=True)
    # File name: <date>_<txn_id>.json (add .json for safety)
    file_path = os.path.join(base, f"{date_str}_{transaction_id}.json")
    with open(file_path, "w") as f:
        json.dump(meter_values, f, indent=2)
    return file_path

def archive_transaction(charger_id, tx):
    """Write a transaction record as JSON in work/ocpp/records."""
    try:
        connector = tx.get("connectorId", 0)
        txn_id = tx.get("transactionId")
        if txn_id is None:
            return None
        base = gw.resource("work", "ocpp", "records", charger_id)
        os.makedirs(base, exist_ok=True)
        file_path = os.path.join(base, f"{connector}_{txn_id}.dat")
        with open(file_path, "w") as f:
            json.dump(tx, f, indent=2)
        return file_path
    except Exception:
        gw.exception("Failed to archive transaction")
        return None

def view_energy_graph(*, charger_id=None, date=None, **_):
    """
    Render a page with a graph for a charger's session by date.
    """
    import glob
    html = ['<link rel="stylesheet" href="/static/ocpp/csms/charger_status.css">']
    html.append('<h1>Charger Transaction Graph</h1>')

    # Form for charger/date selector
    graph_dir = gw.resource("work", "etron", "graphs")
    charger_dirs = sorted(os.listdir(graph_dir)) if os.path.isdir(graph_dir) else []
    txn_files = []
    if charger_id:
        cdir = os.path.join(graph_dir, charger_id)
        if os.path.isdir(cdir):
            txn_files = sorted(glob.glob(os.path.join(cdir, "*.json")))
    html.append('<form method="get" action="/ocpp/csms/energy-graph" style="margin-bottom:2em;">')
    html.append('<label>Charger: <select name="charger_id">')
    html.append('<option value="">(choose)</option>')
    for cid in charger_dirs:
        sel = ' selected' if cid == charger_id else ''
        html.append(f'<option value="{cid}"{sel}>{cid}</option>')
    html.append('</select></label> ')
    if txn_files:
        html.append('<label>Transaction Date: <select name="date">')
        html.append('<option value="">(choose)</option>')
        for fn in txn_files:
            # Filename: YYYY-MM-DD_<txn_id>.json
            dt = os.path.basename(fn).split("_")[0]
            sel = ' selected' if dt == date else ''
            html.append(f'<option value="{dt}"{sel}>{dt}</option>')
        html.append('</select></label> ')
    html.append('<button type="submit">Show</button></form>')

    # Load and render the graph if possible
    graph_data = []
    if charger_id and date:
        base = os.path.join(graph_dir, charger_id)
        match = glob.glob(os.path.join(base, f"{date}_*.json"))
        if match:
            with open(match[0]) as f:
                graph_data = json.load(f)
        # Graph placeholder: (replace with your JS plotting lib)
        html.append('<div style="background:#222;border-radius:1em;padding:1.5em;min-height:320px;">')
        if graph_data:
            html.append('<h3>Session kWh Over Time</h3>')
            html.append('<pre style="color:#fff;font-size:1.02em;">')
            # Show simple table (replace with a chart)
            html.append("Time                | kWh\n---------------------|------\n")
            for mv in graph_data:
                ts = mv.get("timestampStr", "-")
                kwh = "-"
                for sv in mv.get("sampledValue", []):
                    if sv.get("measurand") == "Energy.Active.Import.Register":
                        kwh = sv.get("value")
                html.append(f"{ts:21} | {kwh}\n")
            html.append('</pre>')
        else:
            html.append("<em>No data available for this session.</em>")
        html.append('</div>')

    return "".join(html)


def purge(*, database: bool = False, logs: bool = False):
    """Clear in-memory CSMS data and optionally purge persistent storage."""

    globals().get("_active_cons", {}).clear()
    globals().get("_msg_log", {}).clear()
    gw.info("[OCPP] In-memory state purged.")

    if database:
        conn = gw.sql.open_db(project="ocpp")
        gw.sql.execute("DELETE FROM transactions", connection=conn)
        gw.sql.execute("DELETE FROM meter_values", connection=conn)
        gw.sql.execute("DELETE FROM errors", connection=conn)
        gw.info("[OCPP] Database records purged.")

    if logs:
        for path in [gw.resource("work", "ocpp", "records"),
                     gw.resource("work", "etron", "graphs")]:
            if os.path.isdir(path):
                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
        gw.info("[OCPP] Log files purged.")
