import argparse
import importlib
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

from app.config import cfg
from app.logger import logger
from app.terminus import printc, TerminalColors


class ModuleReloader(FileSystemEventHandler):
    def __init__(self, module_folder, command):
        self.module_folder = module_folder
        self.command = command
        self.proc = None
        self.run_app()
        self.pt = {}

    def reload_module(self, file_name):
        try:
            module_name, _ = os.path.splitext(os.path.basename(file_name))
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
            # print(f"Module '{module_name}' reloaded successfully")
        except Exception as e:
            # printc(f"Error reloading module '{module_name}': {e}", TerminalColors.RED)
            pass

    def on_modified(self, event):
        if event.is_directory:
            return
        self.reload_module(event.src_path)
        if self.proc:
            path = os.path.relpath(event.src_path, __file__)
            printc(f"Reloading module {path}.....", TerminalColors.YELLOW)
            self.proc.terminate()
            self.proc = None
            self.run_app()

    def run_app(self):
        try:
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)
            self.proc = subprocess.Popen(self.command, shell=True, cwd=dname)
            printc("Reloaded.", TerminalColors.YELLOW)
            printc("App is running.", TerminalColors.YELLOW)
        except Exception as e:
            printc(f"Error: {e}", TerminalColors.RED)


def watch_folder(module_folder, command):
    event_handler = ModuleReloader(module_folder, command)
    observer = Observer()
    observer.schedule(event_handler, path=module_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # TODO add option to preserve database
    module_folder = "."

    params = sys.argv[1:]
    params = [x if len(x.split()) == 1 else f'"{x}"' for x in params]
    params = " ".join(params)
    command = f"python main.py {params}"
    logger.info(command)

    watch_folder(module_folder, command)
