from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
import datetime
import logging
import os
import urllib.request
import urllib.error
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for Python 3.12+ datetime deprecation warning
# Register a custom converter for datetime objects
import sqlite3
sqlite3.register_converter("TIMESTAMP", lambda x: datetime.datetime.fromisoformat(x.decode()))
sqlite3.register_adapter(datetime.datetime, lambda x: x.isoformat())

app = FastAPI(title="ZKTeco ADMS Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number TEXT UNIQUE NOT NULL,
            ip_address TEXT NOT NULL,
            model TEXT,
            last_seen TIMESTAMP,
            firmware_version TEXT,
            status TEXT DEFAULT 'offline'
        )
    ''')
    
    # Create device_commands table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_sn TEXT NOT NULL,
            command TEXT NOT NULL,
            status TEXT DEFAULT 'queued',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_at TIMESTAMP NULL,
            response TEXT NULL,
            FOREIGN KEY (device_sn) REFERENCES devices (serial_number)
        )
    ''')
    
    # Create attendance_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_sn TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            verify_mode INTEGER,
            status INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_sn) REFERENCES devices (serial_number)
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class Device(BaseModel):
    serial_number: str
    ip_address: str
    model: Optional[str] = None
    firmware_version: Optional[str] = None

class CommandRequest(BaseModel):
    command: str

class CommandResponse(BaseModel):
    id: int
    command: str
    status: str

# Helper functions
def register_or_update_device(sn: str, ip: str, model: Optional[str] = None, firmware: Optional[str] = None):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Check if device exists
    cursor.execute('SELECT id FROM devices WHERE serial_number = ?', (sn,))
    device = cursor.fetchone()
    
    # Convert datetime to string to avoid deprecation warning
    now_str = datetime.datetime.now().isoformat()
    
    if device:
        # Update existing device
        cursor.execute('''
            UPDATE devices 
            SET ip_address = ?, model = ?, firmware_version = ?, last_seen = ?, status = ?
            WHERE serial_number = ?
        ''', (ip, model, firmware, now_str, 'online', sn))
    else:
        # Register new device
        cursor.execute('''
            INSERT INTO devices (serial_number, ip_address, model, firmware_version, last_seen, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sn, ip, model, firmware, now_str, 'online'))
        logger.info(f"New device connected: {sn} from {ip}")
    
    conn.commit()
    conn.close()

def get_pending_commands(sn: str):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, command FROM device_commands 
        WHERE device_sn = ? AND status = 'queued'
        ORDER BY created_at ASC
    ''', (sn,))
    
    commands = cursor.fetchall()
    conn.close()
    
    return commands

def get_device_info(sn: str):
    """Get device information including IP address and status"""
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ip_address, status FROM devices 
        WHERE serial_number = ?
    ''', (sn,))
    
    device = cursor.fetchone()
    conn.close()
    
    if device:
        return {"ip_address": device[0], "status": device[1]}
    return None

def update_command_status(command_id: int, status: str, response: Optional[str] = None):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Convert datetime to string to avoid deprecation warning
    now_str = datetime.datetime.now().isoformat()
    
    if response:
        cursor.execute('''
            UPDATE device_commands 
            SET status = ?, executed_at = ?, response = ?
            WHERE id = ?
        ''', (status, now_str, response, command_id))
    else:
        cursor.execute('''
            UPDATE device_commands 
            SET status = ?, executed_at = ?
            WHERE id = ?
        ''', (status, now_str, command_id))
    
    conn.commit()
    conn.close()

def clear_commands_from_queue(sn: str, command_ids: List[int]):
    """Clear specific commands from the queue for a device"""
    if not command_ids:
        return
    
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Update status of commands to 'sent'
    placeholders = ','.join('?' * len(command_ids))
    cursor.execute(f'''
        UPDATE device_commands 
        SET status = 'sent'
        WHERE id IN ({placeholders})
    ''', command_ids)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Cleared {len(command_ids)} commands from queue for device {sn}")

# ADMS Endpoints
@app.get("/iclock/getrequest", response_class=PlainTextResponse)
async def get_request(request: Request):
    sn = request.query_params.get("SN")
    ip = request.client.host
    
    if not sn:
        raise HTTPException(status_code=400, detail="SN parameter required")
    
    # Register or update device
    register_or_update_device(sn, ip)
    
    # Get pending commands
    commands = get_pending_commands(sn)
    
    if commands:
        # Format commands as plain text (C: command) with proper ZKTeco format
        response_text = ""
        command_ids = []
        for command_id, command in commands:
            # Convert to uppercase and format according to ZKTeco standards with proper line endings
            # Remove any existing C: prefix and whitespace
            clean_command = command.upper().strip()
            if clean_command.startswith("C:"):
                clean_command = clean_command[2:].strip()
            
            response_text += f"C: {clean_command}\r\n"  # Use \r\n as recommended
            command_ids.append(command_id)
        
        # Clear commands from queue
        clear_commands_from_queue(sn, command_ids)
        
        # Enhanced logging for debugging
        logger.info(f"[GetRequest] Sending {len(commands)} commands to device {sn} from {ip}")
        logger.info(f"[GetRequest] Command content: {response_text.strip()}")
        logger.info(f"[GetRequest] Command IDs: {command_ids}")
        
        # Return plain text with proper content-type header and charset
        return PlainTextResponse(
            response_text, 
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-store"
            }
        )
    else:
        logger.info(f"[GetRequest] No pending commands for device {sn} from {ip}")
        return PlainTextResponse(
            "OK", 
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-store"
            }
        )

@app.get("/iclock/devicecmd", response_class=PlainTextResponse)
@app.post("/iclock/devicecmd", response_class=PlainTextResponse)
async def device_cmd(request: Request):
    sn = request.query_params.get("SN")
    ip = request.client.host
    response_param = request.query_params.get("Response")
    cmd = request.query_params.get("CMD")
    cmd_id = request.query_params.get("CMDID")
    
    # Log all query parameters for debugging
    logger.info(f"[DeviceCMD] Received request from {ip} with params: SN={sn}, CMD={cmd}, Response={response_param}, CMDID={cmd_id}, Method={request.method}")
    
    if not sn:
        logger.warning("[DeviceCMD] SN parameter missing")
        raise HTTPException(status_code=400, detail="SN parameter required")
    
    # Register or update device
    register_or_update_device(sn, ip)
    
    # Log the request
    logger.info(f"[DeviceCMD] Device {sn} responded to command {cmd} with response={response_param}")
    
    # Update command status if CMD is provided
    if cmd:
        try:
            # Find the command in the database by command text and device SN
            conn = sqlite3.connect('adms.db')
            cursor = conn.cursor()
            
            # Look for the most recent command with this text that was sent
            # Use exact match instead of LIKE for better accuracy
            cursor.execute('''
                SELECT id, command FROM device_commands 
                WHERE device_sn = ? AND status = 'sent'
                ORDER BY created_at DESC
                LIMIT 10
            ''', (sn,))
            
            command_records = cursor.fetchall()
            conn.close()
            
            matched_command = None
            matched_command_id = None
            
            # Try to find an exact match first
            for record in command_records:
                record_id, record_command = record
                # Normalize both commands for comparison
                normalized_record = record_command.strip().upper()
                normalized_cmd = cmd.strip().upper()
                
                # Handle different command formats
                if normalized_record == normalized_cmd:
                    matched_command = normalized_cmd
                    matched_command_id = record_id
                    break
                # Also check if the command is contained in the record
                elif normalized_cmd in normalized_record or normalized_record in normalized_cmd:
                    matched_command = normalized_cmd
                    matched_command_id = record_id
                    break
            
            if matched_command and matched_command_id:
                # Update command status based on response
                if response_param and response_param.upper() == "OK":
                    update_command_status(matched_command_id, "completed", response_param)
                    logger.info(f"[DeviceCMD] Command {matched_command} completed successfully on device {sn}")
                else:
                    update_command_status(matched_command_id, "failed", response_param)
                    logger.info(f"[DeviceCMD] Command {matched_command} failed on device {sn} with response: {response_param}")
            else:
                logger.warning(f"[DeviceCMD] No matching command found for device {sn} with command {cmd}")
                # Log all recent commands for debugging
                if command_records:
                    recent_commands = [f"{record[0]}: {record[1]}" for record in command_records]
                    logger.info(f"[DeviceCMD] Recent commands for device {sn}: {', '.join(recent_commands)}")
                else:
                    logger.info(f"[DeviceCMD] No recent commands found for device {sn}")
        except Exception as e:
            logger.error(f"[DeviceCMD] Error updating command status: {e}", exc_info=True)
    else:
        logger.warning(f"[DeviceCMD] No command specified in device response from {sn}")
    
    return PlainTextResponse("OK", headers={"Content-Type": "text/plain; charset=utf-8"})

@app.post("/iclock/fdata", response_class=PlainTextResponse)
async def receive_fdata(request: Request):
    sn = request.query_params.get("SN")
    ip = request.client.host
    
    if not sn:
        raise HTTPException(status_code=400, detail="SN parameter required")
    
    # Register or update device
    register_or_update_device(sn, ip)
    
    # Log the request
    logger.info(f"Device {sn} sent fingerprint data from {ip}")
    
    return PlainTextResponse("OK", headers={"Content-Type": "text/plain"})

@app.post("/iclock/cdata", response_class=PlainTextResponse)
@app.get("/iclock/cdata", response_class=PlainTextResponse)
async def receive_data(request: Request):
    sn = request.query_params.get("SN")
    ip = request.client.host
    
    if not sn:
        raise HTTPException(status_code=400, detail="SN parameter required")
    
    # Extract additional parameters
    model = request.query_params.get("model")
    firmware = request.query_params.get("pushver")
    
    # Register or update device with model and firmware info
    register_or_update_device(sn, ip, model, firmware)
    
    # Log the request
    logger.info(f"[CData] Device {sn} sent data from {ip} (Model: {model}, Firmware: {firmware})")
    
    # For GET requests, check for pending commands
    if request.method == "GET":
        # Get pending commands
        commands = get_pending_commands(sn)
        
        if commands:
            # Format commands as plain text (C: command) with proper ZKTeco format
            response_text = ""
            command_ids = []
            for command_id, command in commands:
                # Convert to uppercase and format according to ZKTeco standards with proper line endings
                # Remove any existing C: prefix and whitespace
                clean_command = command.upper().strip()
                if clean_command.startswith("C:"):
                    clean_command = clean_command[2:].strip()
                
                response_text += f"C: {clean_command}\r\n"  # Use \r\n as recommended
                command_ids.append(command_id)
            
            # Clear commands from queue
            clear_commands_from_queue(sn, command_ids)
            
            # Enhanced logging for debugging
            logger.info(f"[CData-GET] Sending {len(commands)} commands to device {sn} from {ip}")
            logger.info(f"[CData-GET] Command content: {response_text.strip()}")
            logger.info(f"[CData-GET] Command IDs: {command_ids}")
            
            # Return plain text with proper content-type header and charset
            return PlainTextResponse(
                response_text, 
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "Cache-Control": "no-store"
                }
            )
        else:
            logger.info(f"[CData-GET] No pending commands for device {sn} from {ip}")
            return PlainTextResponse(
                "OK", 
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "Cache-Control": "no-store"
                }
            )
    
    # Parse attendance data if present (for POST requests)
    body = await request.body()
    body_str = body.decode('utf-8')
    
    logger.info(f"[CData-POST] Received data from device {sn}: {body_str[:200]}...")  # Log first 200 chars
    
    if body_str.startswith("GET OPTION FROM:"):
        # This is an option request, not attendance data
        # Check for commands even in option requests
        commands = get_pending_commands(sn)
        
        if commands:
            # Format commands as plain text (C: command) with proper ZKTeco format
            response_text = ""
            command_ids = []
            for command_id, command in commands:
                # Convert to uppercase and format according to ZKTeco standards with proper line endings
                # Remove any existing C: prefix and whitespace
                clean_command = command.upper().strip()
                if clean_command.startswith("C:"):
                    clean_command = clean_command[2:].strip()
                
                response_text += f"C: {clean_command}\r\n"  # Use \r\n as recommended
                command_ids.append(command_id)
            
            # Clear commands from queue
            clear_commands_from_queue(sn, command_ids)
            
            # Enhanced logging for debugging
            logger.info(f"[CData-OPTION] Sending {len(commands)} commands to device {sn} from {ip}")
            logger.info(f"[CData-OPTION] Command content: {response_text.strip()}")
            logger.info(f"[CData-OPTION] Command IDs: {command_ids}")
            
            # Return plain text with proper content-type header and charset
            return PlainTextResponse(
                response_text, 
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "Cache-Control": "no-store"
                }
            )
        else:
            logger.info(f"[CData-OPTION] No pending commands for device {sn} from {ip}")
            return PlainTextResponse(
                "OK", 
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "Cache-Control": "no-store"
                }
            )
    
    # Process attendance logs
    if "TRANS RECORDS" in body_str:
        lines = body_str.split("\n")
        conn = sqlite3.connect('adms.db')
        cursor = conn.cursor()
        
        logger.info(f"[CData-ATTENDANCE] Processing {len(lines)} lines of attendance data from device {sn}")
        
        for line in lines:
            if line.startswith("TRANS") and len(line.split("\t")) >= 5:
                parts = line.split("\t")
                try:
                    user_id = parts[1]
                    timestamp = parts[2]
                    verify_mode = int(parts[3])
                    status = int(parts[4])
                    
                    # Insert attendance log
                    cursor.execute('''
                        INSERT INTO attendance_logs (device_sn, user_id, timestamp, verify_mode, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sn, user_id, timestamp, verify_mode, status))
                except Exception as e:
                    logger.error(f"[CData-ATTENDANCE] Error parsing attendance record: {e}")
        
        conn.commit()
        conn.close()
    
    # After processing attendance, check for more commands to send
    commands = get_pending_commands(sn)
    
    if commands:
        # Format commands as plain text (C: command) with proper ZKTeco format
        response_text = ""
        command_ids = []
        for command_id, command in commands:
            # Convert to uppercase and format according to ZKTeco standards with proper line endings
            # Remove any existing C: prefix and whitespace
            clean_command = command.upper().strip()
            if clean_command.startswith("C:"):
                clean_command = clean_command[2:].strip()
            
            response_text += f"C: {clean_command}\r\n"  # Use \r\n as recommended
            command_ids.append(command_id)
        
        # Clear commands from queue
        clear_commands_from_queue(sn, command_ids)
        
        # Enhanced logging for debugging
        logger.info(f"[CData-POST] Sending {len(commands)} commands to device {sn} from {ip} after attendance processing")
        logger.info(f"[CData-POST] Command content: {response_text.strip()}")
        logger.info(f"[CData-POST] Command IDs: {command_ids}")
        
        # Return plain text with proper content-type header and charset
        return PlainTextResponse(
            response_text, 
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-store"
            }
        )
    else:
        logger.info(f"[CData-POST] No pending commands for device {sn} from {ip} after attendance processing")
        return PlainTextResponse(
            "OK", 
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-store"
            }
        )

# API Endpoints for Web UI
@app.get("/api/devices")
async def get_devices():
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Update device status based on last seen time (offline if not seen in last 5 minutes)
    five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
    five_minutes_ago_str = five_minutes_ago.isoformat()
    
    cursor.execute('''
        UPDATE devices 
        SET status = CASE 
            WHEN last_seen > ? THEN 'online' 
            ELSE 'offline' 
        END
    ''', (five_minutes_ago_str,))
    
    cursor.execute('''
        SELECT serial_number, ip_address, model, last_seen, status, firmware_version 
        FROM devices 
        ORDER BY last_seen DESC
    ''')
    
    devices = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for device in devices:
        result.append({
            "serial_number": device[0],
            "ip_address": device[1],
            "model": device[2],
            "last_seen": device[3],
            "status": device[4],
            "firmware_version": device[5]
        })
    
    return result

@app.post("/api/devices/{sn}/command")
async def queue_command(sn: str, command_req: CommandRequest):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Check if device exists
    cursor.execute('SELECT id FROM devices WHERE serial_number = ?', (sn,))
    device = cursor.fetchone()
    
    if not device:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Convert command to uppercase for proper ZKTeco format
    formatted_command = command_req.command.upper()
    
    # Insert command
    cursor.execute('''
        INSERT INTO device_commands (device_sn, command, status)
        VALUES (?, ?, 'queued')
    ''', (sn, formatted_command))
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    if command_id is None:
        raise HTTPException(status_code=500, detail="Failed to create command")
    
    # Just return the queued command without trying to notify the device
    return CommandResponse(id=int(command_id), command=formatted_command, status="queued")

@app.get("/api/attendance")
async def get_attendance_logs(limit: int = 100):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT device_sn, user_id, timestamp, verify_mode, status, created_at
        FROM attendance_logs
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for log in logs:
        result.append({
            "device_sn": log[0],
            "user_id": log[1],
            "timestamp": log[2],
            "verify_mode": log[3],
            "status": log[4],
            "created_at": log[5]
        })
    
    return result

@app.get("/api/commands")
async def get_commands(device_sn: Optional[str] = None):
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    if device_sn:
        cursor.execute('''
            SELECT id, device_sn, command, status, created_at, executed_at, response
            FROM device_commands
            WHERE device_sn = ?
            ORDER BY created_at DESC
        ''', (device_sn,))
    else:
        cursor.execute('''
            SELECT id, device_sn, command, status, created_at, executed_at, response
            FROM device_commands
            ORDER BY created_at DESC
        ''')
    
    commands = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for cmd in commands:
        result.append({
            "id": cmd[0],
            "device_sn": cmd[1],
            "command": cmd[2],
            "status": cmd[3],
            "created_at": cmd[4],
            "executed_at": cmd[5],
            "response": cmd[6]
        })
    
    return result

@app.delete("/api/commands/queued")
async def clear_queued_commands():
    """Clear all queued commands from the database"""
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM device_commands WHERE status = 'queued'")
    count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {"message": f"Successfully cleared {count} queued commands"}

@app.delete("/api/devices/{sn}")
async def remove_device(sn: str):
    """Remove a device and all its related commands and attendance logs"""
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    # Check if device exists
    cursor.execute('SELECT id FROM devices WHERE serial_number = ?', (sn,))
    device = cursor.fetchone()
    
    if not device:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Delete related attendance logs
    cursor.execute("DELETE FROM attendance_logs WHERE device_sn = ?", (sn,))
    logs_count = cursor.rowcount
    
    # Delete related commands
    cursor.execute("DELETE FROM device_commands WHERE device_sn = ?", (sn,))
    commands_count = cursor.rowcount
    
    # Delete the device
    cursor.execute("DELETE FROM devices WHERE serial_number = ?", (sn,))
    devices_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {
        "message": f"Successfully removed device {sn}",
        "devices_deleted": devices_count,
        "commands_deleted": commands_count,
        "logs_deleted": logs_count
    }

@app.delete("/api/attendance")
async def clear_attendance_logs():
    """Clear all attendance logs from the database"""
    conn = sqlite3.connect('adms.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM attendance_logs")
    count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {"message": f"Successfully cleared {count} attendance logs"}

@app.get("/")
async def root():
    # Serve the dashboard HTML file
    return FileResponse('dashboard.html')

# Initialize database on startup
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="128.199.24.193", port=8080)