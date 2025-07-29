import asyncio
from magique.client import connect_to_server, ServiceProxy, MagiqueError, ServerProxy

from ..constant import SERVER_URLS
from ..utils.log import logger


current_server_url = None


async def connect_remote(
        service_name_or_id: str,
        server_url: str | list[str] | None = None,
        server_timeout: float = 5.0,
        service_timeout: float = 5.0,
        time_delta: float = 0.5,
        ) -> ServiceProxy:
    if server_url is None:
        server_urls = SERVER_URLS
    elif isinstance(server_url, str):
        server_urls = [server_url]
    else:
        server_urls = server_url

    async def _get_server(url: str) -> ServerProxy:
        while True:
            try:
                server = await connect_to_server(url)
                return server
            except Exception:
                await asyncio.sleep(time_delta)


    async def _get_service(server: ServerProxy) -> ServiceProxy:
        while True:
            try:
                service = await server.get_service(service_name_or_id)
                return service
            except MagiqueError:
                await asyncio.sleep(time_delta)
    
    async def _try_get_service(url: str):
        try:
            logger.debug(f"Trying to connect to server {url}")
            server = await asyncio.wait_for(_get_server(url), server_timeout)
            logger.debug(f"Connected to server {url}")
        except asyncio.TimeoutError:
            logger.error(f"Failed to connect to server {url}")
            return
        try:
            service = await asyncio.wait_for(_get_service(server), service_timeout)
            logger.debug(f"Service {service_name_or_id} is available on server {url}")
            return service, url
        except asyncio.TimeoutError:
            logger.error(f"Failed to get service {service_name_or_id} on server {url}")
            return

    async def _search_available_server_then_get_service():
        global current_server_url
        tasks = []
        for url in server_urls:
            task = asyncio.create_task(_try_get_service(url))
            tasks.append(task)

        for future in asyncio.as_completed(tasks):
            result = await future
            if result is not None:
                service, url = result
                current_server_url = url
                logger.info(f"Found service {service_name_or_id} on server {url}")
                return service

        raise asyncio.TimeoutError(
            f"No server is available for {service_name_or_id} service in {server_urls}")

    if current_server_url is not None:
        try:
            server = await asyncio.wait_for(_get_server(current_server_url), server_timeout)
            service = await asyncio.wait_for(_get_service(server), service_timeout)
        except asyncio.TimeoutError:
            logger.debug(f"Current server {current_server_url} is not available")
            service = await _search_available_server_then_get_service()
    else:
        service = await _search_available_server_then_get_service()

    return service


def toolset_cli(toolset_type, default_service_name: str):
    import fire

    async def main(service_name: str = default_service_name, **kwargs):
        toolset = toolset_type(service_name, **kwargs)
        await toolset.run()

    fire.Fire(main)
