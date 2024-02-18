import json
import subprocess
import sys
import time
import logging
from os.path import relpath
from pathlib import Path
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

CRAWLY_ROOT = "/usr/src/"

class ServiceChangeEventHandler(FileSystemEventHandler):

    extensions = ["py"]

    def on_modified(self, event: FileSystemEvent) -> None:
        relp = Path(relpath(event.src_path, CRAWLY_ROOT))
        extension = relp.parts[-1].split(".")[-1]
        if extension in self.extensions and len(relp.parts) > 1:
            svc_name = f"{relp.parts[0]}_{relp.parts[1]}"
            try:
                asyncio.run(send_restart(svc_name))
            except BaseException as e:
                pass



async def send_restart(svc_name: str):
    listener_endpoint = "http://localhost/config/listeners"
    app_info_endpoint = "http://localhost/config/applications"
    app_control_endpoint = "http://localhost/control/applications"
    
    # Get all applications in json
    app_response = await unix_req(app_info_endpoint)
    apps = app_response.keys()
    logging.info(apps)
    if svc_name not in list(apps):
        print(f"Service {svc_name} is not in running services list.")
        return
    
    # Get all listeners in json
    listener_response = await unix_req(listener_endpoint)
    listener = None
    for k, l in listener_response.items():
        if l.get('pass') == 'applications/' + svc_name:
            listener = k

    # Restart application
    print(f"Process {svc_name} is restarting. Stand by...")
    await unix_req(f"{app_control_endpoint}/{svc_name}/restart", "GET")
    print(f"Process {svc_name} is ready.")

async def unix_req(endpoint: str, req_type: str = "GET", data: dict = None):
    cmd = f"curl -X {req_type}"
    if data:
        cmd = f"{cmd} -d'{json.dumps(data)}'"
    cmd = f"{cmd} --unix-socket /var/run/control.unit.sock {endpoint}"

    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        json_response = json.loads(res.stdout)
    except:
        json_response = {}
    return json_response

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )
    logging.info(f'start watching directory {CRAWLY_ROOT!r}')
    observer = Observer()
    event_handler = ServiceChangeEventHandler()
    observer.schedule(event_handler, CRAWLY_ROOT, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
    