import os
import sys
import uuid
import base64
import asyncio
from pathlib import Path
from typing import TypedDict

from executor.engine import Engine, LocalJob, ProcessJob
from executor.engine.job.extend import SubprocessJob

from ..toolset import tool
from ..constant import SERVER_URLS
from ..utils.remote import connect_remote
from ..tools.file_transfer import FileTransferToolSet
from ..utils.log import logger


class EndpointConfig(TypedDict):
    service_name: str
    workspace_path: str
    log_level: str
    allow_file_transfer: bool
    builtin_services: list[str | dict]
    outer_services: list[str]
    docker_services: list[str]


class Endpoint(FileTransferToolSet):
    def __init__(
        self,
        config: EndpointConfig,
    ):
        self.config = config
        name = self.config.get("service_name", "pantheon-chatroom-endpoint")
        workspace_path = self.config.get("workspace_path", "./.pantheon-chatroom-workspace")
        Path(workspace_path).mkdir(parents=True, exist_ok=True)
        self.id_hash = self.config.get("id_hash", None)
        worker_params = self.config.get("worker_params", {})
        if self.id_hash is None:
            self.id_hash = str(uuid.uuid4())
        worker_params["id_hash"] = self.id_hash
        self.services: list[dict] = []
        self.allow_file_transfer = self.config.get("allow_file_transfer", True)
        self._services_to_start: list[str] = []
        super().__init__(name, workspace_path, worker_params)

    def setup_tools(self):
        if not self.allow_file_transfer:
            self.fetch_image_base64._is_tool = False
            self.open_file_for_write._is_tool = False
            self.write_chunk._is_tool = False
            self.close_file._is_tool = False
            self.read_file._is_tool = False
        super().setup_tools()

    @tool
    async def list_services(self) -> list[dict]:
        res = []
        for s in self.services:
            res.append({
                "name": s["name"],
                "id": s["id"],
            })
        return res

    @tool
    async def fetch_image_base64(self, image_path: str) -> dict:
        """Fetch an image and return the base64 encoded image."""
        if '..' in image_path:
            return {"success": False, "error": "Image path cannot contain '..'"}
        i_path = self.path / image_path
        if not i_path.exists():
            return {"success": False, "error": "Image does not exist"}
        format = i_path.suffix.lower()
        if format not in [".jpg", ".jpeg", ".png", ".gif"]:
            return {"success": False, "error": "Image format must be jpg, jpeg, png or gif"}
        with open(i_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            data_uri = f"data:image/{format};base64,{b64}"
        return {
            "success": True,
            "image_path": image_path,
            "data_uri": data_uri,
        }

    @tool
    async def add_service(self, service_id: str):
        """Add a service to the endpoint."""
        try:
            s = await connect_remote(service_id, SERVER_URLS)
            info = await s.fetch_service_info()
            self.services.append({
                "id": service_id,
                "name": info.service_name,
            })
            if service_id in self._services_to_start:
                self._services_to_start.remove(service_id)
            elif info.service_name in self._services_to_start:
                self._services_to_start.remove(info.service_name)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @tool
    async def get_service(self, service_id_or_name: str) -> dict | None:
        """Get a service by id or name."""
        for s in self.services:
            if (
                s["id"] == service_id_or_name
                or s["name"] == service_id_or_name
            ):
                return s
        return None

    @tool
    async def services_ready(self) -> bool:
        """Check if all services are ready."""
        return len(self._services_to_start) == 0

    async def run_builtin_services(self, engine: Engine):
        services = []
        default_services = [
            "python_interpreter",
            "file_manager",
            "web_browse",
        ]
        builtin_services = self.config.get("builtin_services", default_services)
        for service in builtin_services:
            if isinstance(service, str):
                service_type = service
                params = {}
            else:
                service_type = service.get("type", service)
                params = service.copy()
                del params["type"]

            if service_type == "python_interpreter":
                from ..tools.python import PythonInterpreterToolSet
                toolset = PythonInterpreterToolSet(
                    name=params.get("name", "python_interpreter"),
                    workdir=str(self.path),
                    endpoint_service_id=self.service_id,
                    worker_params={"id_hash": self.id_hash + "_python_interpreter"},
                )
            elif service_type == "file_manager":
                from ..tools.file_manager import FileManagerToolSet
                toolset = FileManagerToolSet(
                    name=params.get("name", "file_manager"),
                    path=str(self.path),
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_file_manager"},
                )
            elif service_type == "web_browse":
                from ..tools.web_browse import WebBrowseToolSet
                toolset = WebBrowseToolSet(
                    name=params.get("name", "web_browse"),
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_web_browse"},
                )
            elif service_type == "r_interpreter":
                from ..tools.r import RInterpreterToolSet
                toolset = RInterpreterToolSet(
                    name=params.get("name", "r_interpreter"),
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_r_interpreter"},
                )
            elif service_type == "shell":
                from ..tools.shell import ShellToolSet
                toolset = ShellToolSet(
                    name=params.get("name", "shell"),
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_shell"},
                )
            elif service_type == "vector_rag":
                from ..tools.vector_rag import VectorRAGToolSet
                db_path = params.get("db_path")
                if not db_path:
                    raise ValueError("db_path is required for vector_rag service")
                if params.get("download_from_huggingface"):
                    from ..rag.build import download_from_huggingface
                    download_path = params.get("download_path", "tmp/db")
                    if not os.path.exists(download_path):
                        logger.info(f"Downloading vector database from Hugging Face to {download_path}")
                        download_from_huggingface(
                            download_path,
                            params.get("repo_id", "NaNg/pantheon_rag_db"),
                            params.get("filename", "latest.zip")
                        )
                    else:
                        logger.info(f"Vector database already exists in {download_path}")
                toolset = VectorRAGToolSet(
                    name=params.get("name", "vector_rag"),
                    db_path=db_path,
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_vector_rag"},
                )
            elif service_type == "scraper":
                from ..tools.scraper import ScraperToolSet
                toolset = ScraperToolSet(
                    name=params.get("name", "scraper"),
                    endpoint_service_id=self.worker.service_id,
                    worker_params={"id_hash": self.id_hash + "_scraper"},
                )
            services.append(toolset)

        for service in services:
            self._services_to_start.append(service.service_id)
            job = ProcessJob(
                service.run,
                args=(self.config.get("log_level", "INFO"),),
                retries=10,
            )
            await engine.submit_async(job)
            await job.wait_until_status("running")

    async def add_outer_services(self):
        for service_id in self.config.get("outer_services", []):
            logger.info(f"Adding outer service {service_id}")
            resp = await self.add_service(service_id)
            if not resp["success"]:
                logger.error(f"Failed to add outer service {service_id}: {resp['error']}")

    async def run_docker_services(self, engine: Engine):
        data_dir = str(self.path.absolute())
        for item in self.config.get("docker_services", []):
            if isinstance(item, str):
                docker_image_name = item
                service_name = docker_image_name
            else:
                docker_image_name = item.get("image")
                service_name = item.get("name", docker_image_name)

            self._services_to_start.append(service_name)
            server_urls = "|".join(SERVER_URLS)
            cmd = (
                f"docker run -e ID_HASH={self.id_hash}_{docker_image_name} "
                f"-e SERVICE_NAME={service_name} "
                f"-e MAGIQUE_SERVER_URL=\"{server_urls}\" "
                f"-e ENDPOINT_SERVICE_ID={self.service_id} "
                f"-v {data_dir}:/data "
                f"{docker_image_name}"
            )
            job = SubprocessJob(cmd, retries=10)
            await engine.submit_async(job)
            await job.wait_until_status("running")

    async def run(self):
        from loguru import logger
        logger.add(sys.stderr, level=self.config.get("log_level", "INFO"))
        engine = Engine()
        job = LocalJob(self.worker.run)
        await engine.submit_async(job)
        await job.wait_until_status("running")
        await asyncio.sleep(2)
        await self.run_builtin_services(engine)
        await self.add_outer_services()
        await self.run_docker_services(engine)
        logger.info(f"Endpoint started: {self.service_id}")
        await engine.wait_async()
