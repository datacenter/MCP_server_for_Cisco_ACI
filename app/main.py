from   mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import os
import json
import logging
from   auth_manager import apic_auth_manager 

# set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("APICmcp")

mcp = FastMCP("APICmcp", settings={"initialization_timeout": 10.0}) 

@mcp.tool()
async def fetch_apic_class(class_name: str) -> str:
    """
    Fetches a class of Managed Object from Cisco APIC.
    Requires APIC authentication.

    Args:
        class_name (str): The class name of the Managed Object (e.g., 'fvTenant', 'topSystem').

    Returns:
        str: The JSON response from APIC.
    """
    logger.info(f"Logging in to APIC")
    await apic_auth_manager.initialize()
    client = await apic_auth_manager.get_authenticated_client()
    if not client:
        logger.error("Error: Unable to authenticate with APIC. Please check your credentials.")
    logger.info(f"Authenticated successfully with APIC: {apic_auth_manager.apic_base_url}")

    base_url = apic_auth_manager.apic_base_url
    url = f"{base_url}/api/class/{class_name}.json"

    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2) 
    except httpx.HTTPStatusError as e:
        return f"Error: APIC returned status {e.response.status_code} for {e.request.url}. Response: {e.response.text}"
    except httpx.RequestError as e:
        return f"Error: An error occurred while requesting {e.request.url}: {e}"
    except RuntimeError as e:
        return f"APIC Authentication Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

async def apic_rest_post(url: str, payload: dict) -> str:
    """
    Performs a POST request to APIC's REST API to create or update a Managed Object.
    Requires APIC authentication.

    Args:
        url (str): The URL to POST to
        payload (dict): The JSON payload to POST to the REST API.

    Returns:
        str: The JSON response from APIC.   
    """
    logger.info(f"Logging in to APIC")
    await apic_auth_manager.initialize()
    client = await apic_auth_manager.get_authenticated_client()
    if not client:
        logger.error("Error: Unable to authenticate with APIC. Please check your credentials.")
    logger.info(f"Authenticated successfully with APIC: {apic_auth_manager.apic_base_url}")

    base_url = apic_auth_manager.apic_base_url
    url = f"{base_url}/{url}"
    try:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info(f"Successfully posted to {url}")
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error making request to {url}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"Request to {url} failed with status {e.response.status_code}: {e.response.text}")
        return None
    

@mcp.tool()
async def make_aci_backup(scp_server_ip: str, scp_username: str, scp_password: str, remote_name: str, remote_path: str, export_policy_name: str) -> str:
    """
    Creates a backup of the APIC configuration.
    Requires APIC authentication.

    args:
        scp_server_ip (str): The IP address of the SCP server.
        scp_username (str): The username for the SCP server.
        scp_passwpord (str): The password for the SCP server.
        remote_path_name (str): The name of the remote path in APIC.
        export_policy_name (str): The name of the export policy.    
    
    Returns:
        str: The status of the backup operation.
    """
    # --- Create remote destination ---
    logger.info("Creating remote destination")
    remote_location_content = {
        "fileRemotePath": {
            "attributes": {
                "dn": f"uni/fabric/path-{remote_name}",
                "remotePort": "22",
                "name": remote_name,
                "descr": "MCP backup SCP Server",
                "protocol": "scp",
                "remotePath": remote_path,
                "userName": scp_username,
                "userPasswd": scp_password,
                "host": scp_server_ip,
                "status": "created,modified"
            },
            "children": [
                {
                    "fileRsARemoteHostToEpg": {
                        "attributes": {
                            "tDn": "uni/tn-mgmt/mgmtp-default/oob-default",
                            "status": "created,modified"
                        },
                        "children": []
                    }
                }
            ]
        }
    }
    await apic_rest_post(url="/api/node/mo/uni.json", payload=remote_location_content)

    # --- Enable Global AES Encryption Settings ---
    logger.info("Enabling Global AES Encryption Settings")
    aes_encryption_content = {
        "pkiExportEncryptionKey": {
            "attributes": {
                "dn": "uni/exportcryptkey",
                "strongEncryptionEnabled": "true",
                "passphrase": "mcpServermcpServermcpServer"
            },
            "children": []
        }
    }
    await apic_rest_post(url="/api/node/mo/uni.json", payload=aes_encryption_content)

    # --- Create an Export Policy ---
    logger.info("Creating an Export Policy")
    export_policy_content = {
        "configExportP": {
            "attributes": {
                "dn": f"uni/fabric/configexp-{export_policy_name}",
                "name": export_policy_name,
                "descr": "Export Policy for SCP",
                "adminSt": "triggered",
                "format": "json",
                "status": "created,modified"
            },
            "children": [{
                "configRsExportScheduler": {
                    "attributes": {
                        "tnTrigSchedPName": "EveryEightHours",
                        "status": "created,modified"
                    },
                    "children": []
                }
            },
            {
                "configRsRemotePath": {
                    "attributes": {
                        "tnFileRemotePathName": remote_name,
                        "status": "created,modified"
                    },
                    "children": []
                }
            }]
        }
    }
    await apic_rest_post(url="/api/node/mo/uni.json", payload=export_policy_content)


if __name__ == "__main__":
    logger.info("Starting MCP server APICmcp on STDIO...")
    mcp.run()
