from typing import Optional

from ...types._api_version import ApiVersion
from ...types.api.pipelines_config import (
    PipelineConfigResponse,
    ExportPipelineDefinitionResponse,
)
from .._request_handler import AsyncRequestHandler
from .base_pipelines_config import BasePipelinesConfig


class AsyncPipelinesConfig(BasePipelinesConfig):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_pipeline_config(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> PipelineConfigResponse:
        """
        Retrieve configuration details for a specific pipeline.

        This method fetches comprehensive information about a pipeline including its
        deployment details, execution statistics, version information, and metadata.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to retrieve
                configuration for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            PipelineConfigResponse: A response object containing the pipeline
                configuration.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get pipeline configuration
            config = await client.pipelines_config.get_pipeline_config(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {config.agent.name}")
            print(f"Description: {config.agent.agent_description}")
            ```

        Note:
            This method only retrieves configuration information and does not
            execute the pipeline. Use execute_pipeline() to run the pipeline.
        """
        request_data = self._pre_get_pipeline_config(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return PipelineConfigResponse(**resp)

    async def export_pipeline_definition(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> ExportPipelineDefinitionResponse:
        """
        Export the complete definition of a pipeline including all its components.

        This method retrieves a comprehensive export of a pipeline definition including
        metadata, agent configuration, data sources, prompts, tools, models, memories,
        Python code blocks, routers, and deployment information.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to export
                definition for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            ExportPipelineDefinitionResponse: A response object containing the complete
                pipeline definition export.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Export pipeline definition
            export = await client.pipelines_config.export_pipeline_definition(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {export.agent.name}")
            print(f"Export version: {export.metadata.export_version}")
            print(f"Data sources: {len(export.data_sources or [])}")
            print(f"Tools: {len(export.tools or [])}")
            ```

        Note:
            This method exports the complete pipeline definition which can be used
            for backup, version control, or importing into other environments.
        """
        request_data = self._pre_export_pipeline_definition(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return ExportPipelineDefinitionResponse(**resp)
