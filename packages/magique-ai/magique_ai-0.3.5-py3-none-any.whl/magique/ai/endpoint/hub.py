import yaml
from pathlib import Path
import asyncio

from executor.engine import Engine, ProcessJob

from . import Endpoint, EndpointConfig
from ..toolset import ToolSet, tool
from ..utils.log import logger


class EndpointHub(ToolSet):
    def __init__(self, config_dir: str | Path, workspace_base_path: str | Path, worker_params: dict | None = None):
        self.config_dir = Path(config_dir)
        self.endpoint_configs: dict[str, EndpointConfig] = {}
        self.load_endpoint_configs()
        self.workspace_base_path = Path(workspace_base_path)
        self.endpoints: dict[str, Endpoint] = {}
        self.engine = Engine()
        self.jobs: dict[str, ProcessJob] = {}
        super().__init__("endpoint-hub", worker_params=worker_params)

    def load_endpoint_configs(self):
        for config_file in self.config_dir.glob("*.yaml"):
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
                self.endpoint_configs[config_file.stem] = config

    @tool
    async def list_configs(self) -> list[str]:
        return list(self.endpoint_configs.keys())

    @tool
    async def get_config(self, config_name: str) -> dict:
        return self.endpoint_configs[config_name]

    @tool
    async def new_endpoint(self, config_name: str, id_hash: str) -> dict:
        logger.info(f"New endpoint {config_name} with id_hash {id_hash}")
        config = self.endpoint_configs[config_name]
        if id_hash in self.endpoints:
            return {
                "success": False,
                "error": f"Endpoint {id_hash} already exists",
            }
        config["id_hash"] = id_hash
        config["workspace_path"] = str(self.workspace_base_path / id_hash)
        endpoint = Endpoint(config)
        self.endpoints[id_hash] = endpoint
        job = ProcessJob(endpoint.run, retries=10)
        await self.engine.submit_async(job)
        await job.wait_until_status("running")
        return {
            "success": True,
            "service_id": endpoint.worker.service_id,
        }

    @tool
    async def get_endpoint(self, id_hash: str) -> dict:
        endpoint = self.endpoints.get(id_hash)
        if endpoint:
            return {
                "success": True,
                "service_id": endpoint.worker.service_id,
            }
        return {
            "success": False,
            "error": f"Endpoint {id_hash} not found",
        }

    @tool
    async def delete_endpoint(self, id_hash: str) -> dict:
        logger.info(f"Deleting endpoint {id_hash}")
        job = self.jobs.get(id_hash)
        if job:
            await job.cancel()
            del self.jobs[id_hash]
            del self.endpoints[id_hash]
            return {
                "success": True,
            }
        else:
            return {
                "success": False,
                "error": f"Endpoint {id_hash} not found",
            }

    async def run(self, log_level: str = "INFO"):
        while True:
            try:
                await super().run(log_level)
            except Exception as e:
                logger.error(f"Error running endpoint hub: {e}")
                await asyncio.sleep(1)
                logger.info(f"Restarting endpoint hub")
