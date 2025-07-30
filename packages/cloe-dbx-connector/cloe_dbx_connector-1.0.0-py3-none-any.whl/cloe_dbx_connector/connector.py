from cloe_logging import LoggerFactory
from databricks.sdk import WorkspaceClient

from cloe_dbx_connector.config import AzureDatabricksConfig

# Configure logging
logger = LoggerFactory.get_logger(handler_types=["console", "file"], filename="databricks_connector.log")


class DatabricksConnector:
    """
    Connector to authenticate to a Databricks host with Personal Access Token or Service Principle credentials retrieved
    from environment variables.
    """

    def __init__(self, config: AzureDatabricksConfig):
        self.config = config
        self.client = self._init_client()

    def _init_client(self) -> WorkspaceClient:
        if self.config.auth.is_service_principal_auth:
            return WorkspaceClient(
                host=self.config.host,
                azure_client_id=self.config.auth.client_id,
                azure_client_secret=self.config.auth.client_secret,
                azure_tenant_id=self.config.auth.tenant_id,
            )
        return WorkspaceClient(host=self.config.host, token=self.config.auth.personal_access_token)
