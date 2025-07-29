import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import structlog
import websockets
from dotenv import find_dotenv, load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .. import __version__
from ..logs import setup_logging
from .utils import is_port_in_use

logger = structlog.get_logger("timbal.server.watch")


class FileWatcher(FileSystemEventHandler):

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    
    def _broadcast_event(self, event_type: str, file_path: str):
        """Broadcast file system event to all connected clients"""
        file_path = Path(file_path).expanduser().resolve()
        ts = datetime.now().isoformat()

        try: 
            relative_path = file_path.relative_to(self.path)
            message = {
                "type": event_type,
                "payload": {
                    "path": relative_path.as_posix(),
                    "ts": ts,
                }
            }
            # TODO broadcast
            logger.info("broadcasting", message=message)

        except Exception as e:
            logger.error("broadcasting", error=e)


    def on_created(self, event):
        if not event.is_directory:
            self._broadcast_event('file_added', event.src_path)
        else:
            self._broadcast_event('directory_added', event.src_path)
    

    def on_modified(self, event):
        if not event.is_directory:
            self._broadcast_event('file_changed', event.src_path)
    

    def on_deleted(self, event):
        if not event.is_directory:
            self._broadcast_event('file_removed', event.src_path)
        else:
            self._broadcast_event('directory_removed', event.src_path)



async def main(path: Path) -> None:

    try:
        event_handler = FileWatcher(path)
        observer = Observer()
        observer.schedule(event_handler, path.as_posix(), recursive=True)
        observer.start()

        await asyncio.Future()

    except KeyboardInterrupt:
        logger.info("Server shutting down...")

    finally:
        observer.stop()
        observer.join()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Timbal watch server.")
    parser.add_argument(
        "-v", 
        "--version", 
        action="store_true", 
        help="Show version and exit."
    )
    parser.add_argument(
        "--path",
        dest="path",
        type=str,
        required=True,
        help="Path to watch.",
    )
    parser.add_argument(
        "--host",
        dest="host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to.",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=4488, # TODO Change this
        help="Port to bind to.",
    )
    args = parser.parse_args()

    if args.version:
        print(f"timbal.servers.watch {__version__}") # noqa: T201
        sys.exit(0)

    if is_port_in_use(args.port):
        print(f"Port {args.port} is already in use. Please use a different port.") # noqa: T201
        sys.exit(1)

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"Path {path} does not exist.") # noqa: T201
        sys.exit(1)
    if not path.is_dir():
        print(f"Path {path} is not a directory.") # noqa: T201
        sys.exit(1)

    logger.info("loading_dotenv", path=find_dotenv())
    load_dotenv(override=True)
    setup_logging()

    logger.info("watching", path=path, host=args.host, port=args.port)

    asyncio.run(main(path))
