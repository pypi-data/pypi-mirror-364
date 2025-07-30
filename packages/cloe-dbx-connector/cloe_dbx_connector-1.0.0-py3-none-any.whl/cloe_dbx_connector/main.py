from pydantic import ValidationError

from cloe_dbx_connector.config import AzureDatabricksConfig
from cloe_dbx_connector.connector import DatabricksConnector


def main():
    try:
        config = AzureDatabricksConfig()  # loads env vars automatically
    except ValidationError as e:
        print("Configuration error:", e)
        return

    print("Connecting to:", config.host)

    if config.auth.is_token_auth:
        print("Using PAT authentication.")
    else:
        print("Using Entra ID service principal authentication.")

    connector = DatabricksConnector(config)
    client = connector.client
    # Use client as needed...
    print(f"Catalogs -> {[c.name for c in client.catalogs.list()]}")


if __name__ == "__main__":
    main()
