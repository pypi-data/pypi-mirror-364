from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class DatabricksAuthConfig(BaseSettings):
    personal_access_token: str | None = Field(
        default=None,
        alias="CLOE_DBX_PAT",
        description=(
            "Databricks Personal Access Token (PAT) for direct authentication. "
            "If set, service principal credentials are ignored."
        ),
    )


class AzureDatabricksAuthConfig(DatabricksAuthConfig):
    """
    Authentication configuration for Azure Databricks.

    Supports two mutually exclusive authentication methods:
    1. Personal Access Token (PAT)
    2. Microsoft Entra ID Service Principal authentication
    """

    tenant_id: str | None = Field(
        None,
        alias="CLOE_AZURE_TENANT_ID",
        description="Tenant ID from Microsoft Entra ID.",
    )
    client_id: str | None = Field(
        None,
        alias="CLOE_AZURE_CLIENT_ID",
        description="Application (Client) ID from Microsoft Entra ID.",
    )
    client_secret: str | None = Field(
        None,
        alias="CLOE_AZURE_CLIENT_SECRET",
        description="Client secret from Microsoft Entra ID.",
    )

    @property
    def is_token_auth(self) -> bool:
        return self.personal_access_token is not None

    @property
    def is_service_principal_auth(self) -> bool:
        return all([self.tenant_id, self.client_id, self.client_secret])

    @model_validator(mode="after")
    def validate_auth_method(self) -> "AzureDatabricksAuthConfig":
        if not self.is_token_auth and not self.is_service_principal_auth:
            raise ValueError(
                "Authentication credentials missing: Provide either a personal access token "
                "or all three of Azure tenant ID, client ID, and client secret for service principal authentication."
            )
        return self


class AzureDatabricksConfig(BaseSettings):
    """
    Main configuration for Azure Databricks connection.

    Loads workspace host and authentication configuration.
    """

    model_config = {
        "env_prefix": "",  # No prefix so aliases work directly
        "extra": "ignore",
    }

    host: Annotated[
        str,
        Field(
            ...,
            alias="CLOE_DBX_HOST",
            description="Azure Databricks workspace URL. Must start with 'https://'.",
        ),
    ]

    auth: AzureDatabricksAuthConfig = Field(default_factory=AzureDatabricksAuthConfig)  # type: ignore[arg-type]

    @field_validator("host")
    @classmethod
    def validate_host_url(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("Invalid host URL: Must start with 'https://'.")
        return value
