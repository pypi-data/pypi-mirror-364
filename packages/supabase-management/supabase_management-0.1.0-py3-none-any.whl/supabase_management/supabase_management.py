
import httpx
import json

SUPABASE_API_URL = "https://api.supabase.com"

class SupabaseManagementAPIError(Exception):
    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message)
        self.response = response

def is_supabase_error(error: Exception) -> bool:
    return isinstance(error, SupabaseManagementAPIError)

async def _safe_parse_error_response_body(
    response: httpx.Response,
) -> dict | None:
    try:
        body = response.json()
        if isinstance(body, dict) and "message" in body and isinstance(body["message"], str):
            return {"message": body["message"]}
    except json.JSONDecodeError:
        pass
    return None

class SupabaseManagementAPI:
    def __init__(self, access_token: str, base_url: str = SUPABASE_API_URL):
        self.access_token = access_token
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

    async def _create_response_error(self, response: httpx.Response, action: str) -> SupabaseManagementAPIError:
        error_body = await _safe_parse_error_response_body(response)
        message = (
            f"Failed to {action}: {response.status_code} {response.reason_phrase}"
        )
        if error_body:
            message += f": {error_body['message']}"
        return SupabaseManagementAPIError(message, response)

    async def get_organizations(self) -> list:
        response = await self.client.get("/v1/organizations")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get organizations")
        return response.json()

    async def create_organization(self, body: dict) -> dict:
        response = await self.client.post("/v1/organizations", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create organization")
        return response.json()

    async def get_branch_details(self, branch_id: str) -> dict:
        response = await self.client.get(f"/v1/branches/{branch_id}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get branch details")
        return response.json()

    async def delete_branch(self, branch_id: str):
        response = await self.client.delete(f"/v1/branches/{branch_id}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete branch")

    async def update_branch(self, branch_id: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/branches/{branch_id}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update branch")
        return response.json()

    async def get_projects(self) -> list:
        response = await self.client.get("/v1/projects")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get projects")
        return response.json()

    async def create_project(self, body: dict) -> dict:
        response = await self.client.post("/v1/projects", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create project")
        return response.json()

    async def delete_project(self, ref: str) -> dict:
        response = await self.client.delete(f"/v1/projects/{ref}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete project")
        return response.json()

    async def check_service_health(self, ref: str, query: dict) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/health", params=query)
        if response.status_code != 200:
            raise await self._create_response_error(response, "check service health")
        return response.json()

    async def list_functions(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/functions")
        if response.status_code != 200:
            raise await self._create_response_error(response, "list functions")
        return response.json()

    async def create_function(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/functions", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create function")
        return response.json()

    async def get_function(self, ref: str, slug: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/functions/{slug}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get function")
        return response.json()

    async def update_function(self, ref: str, slug: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/functions/{slug}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update function")
        return response.json()

    async def delete_function(self, ref: str, slug: str):
        response = await self.client.delete(f"/v1/projects/{ref}/functions/{slug}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete function")

    async def get_function_body(self, ref: str, slug: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/functions/{slug}/body")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get function body")
        return response.json()

    async def get_project_api_keys(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/api-keys")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project api keys")
        return response.json()

    async def get_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get custom hostname")
        return response.json()

    async def remove_custom_hostname_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove custom hostname config")

    async def create_custom_hostname_config(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/initialize", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create custom hostname config")
        return response.json()

    async def reverify_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/reverify")
        if response.status_code != 200:
            raise await self._create_response_error(response, "reverify custom hostname config")
        return response.json()

    async def activate_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/activate")
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate custom hostname config")
        return response.json()

    async def get_network_bans(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-bans/retrieve")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network bans")
        return response.json()

    async def remove_network_ban(self, ref: str, body: dict):
        response = await self.client.delete(f"/v1/projects/{ref}/network-bans", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove network ban")

    async def get_network_restrictions(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/network-restrictions")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network restrictions")
        return response.json()

    async def apply_network_restrictions(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-restrictions/apply", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "apply network restrictions")
        return response.json()

    async def get_pgsodium_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/pgsodium")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get pg sodium config")
        return response.json()

    async def update_pgsodium_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/pgsodium", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update pg sodium config")
        return response.json()

    async def get_postgrest_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/postgrest")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get postgrest config")
        return response.json()

    async def update_postgrest_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/postgrest", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update postgrest config")
        return response.json()

    async def run_query(self, ref: str, query: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/database/query", json={"query": query})
        if response.status_code != 201:
            raise await self._create_response_error(response, "run query")
        return response.json()

    async def enable_webhooks(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/database/webhooks/enable")
        if response.status_code != 201:
            raise await self._create_response_error(response, "enable webhooks")

    async def get_secrets(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/secrets")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get secrets")
        return response.json()

    async def create_secrets(self, ref: str, body: dict):
        response = await self.client.post(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create secrets")

    async def delete_secrets(self, ref: str, body: dict) -> dict:
        response = await self.client.delete(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete secrets")
        return response.json()

    async def get_ssl_enforcement_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/ssl-enforcement")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get ssl enforcement config")
        return response.json()

    async def update_ssl_enforcement_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/ssl-enforcement", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update ssl enforcement config")
        return response.json()

    async def get_typescript_types(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/types/typescript")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get typescript types")
        return response.json()

    async def get_vanity_subdomain_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get vanity subdomain config")
        return response.json()

    async def remove_vanity_subdomain_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove vanity subdomain config")

    async def check_vanity_subdomain_availability(self, ref: str, subdomain: str) -> bool:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/check-availability", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "check vanity subdomain availability")
        data = response.json()
        return data.get("available", False)

    async def activate_vanity_subdomain_please(self, ref: str, subdomain: str) -> str | None:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/activate", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate vanity subdomain")
        data = response.json()
        return data.get("custom_domain")

    async def upgrade_project(self, ref: str, target_version: int):
        response = await self.client.post(f"/v1/projects/{ref}/upgrade", json={"target_version": target_version})
        if response.status_code != 200:
            raise await self._create_response_error(response, "upgrade project")

    async def get_upgrade_eligibility(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/eligibility")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade eligibility")
        return response.json()

    async def get_upgrade_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/status")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade status")
        return response.json()

    async def get_read_only_mode_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/readonly")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get readonly mode status")
        return response.json()

    async def temporarily_disable_readonly_mode(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/readonly/temporary-disable")
        if response.status_code != 200:
            raise await self._create_response_error(response, "temporarily disable readonly mode")

    async def get_pg_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/postgres")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get PG config")
        return response.json()

    async def update_pg_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/database/postgres", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update PG config")
        return response.json()

    async def get_pgbouncer_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/pgbouncer")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get Pgbouncer config")
        return response.json()

    async def get_project_auth_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project auth config")
        return response.json()

    async def update_project_auth_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/config/auth", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update project auth config")
        return response.json()

    async def get_sso_providers(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO providers")
        return response.json()

    async def create_sso_provider(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/config/auth/sso/providers", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create SSO provider")
        return response.json()

    async def get_sso_provider(self, ref: str, uuid: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO provider")
        return response.json()

    async def update_sso_provider(self, ref: str, uuid: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update SSO provider")
        return response.json()

    async def delete_sso_provider(self, ref: str, uuid: str):
        response = await self.client.delete(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 204:
            raise await self._create_response_error(response, "delete SSO provider")

    async def list_snippets(self, project_ref: str | None = None) -> list:
        params = {}
        if project_ref:
            params["project_ref"] = project_ref
        response = await self.client.get("/v1/snippets", params=params)
        if response.status_code != 200:
            raise await self._create_response_error(response, "list snippets")
        return response.json()

    async def get_snippet(self, id: str) -> dict:
        response = await self.client.get(f"/v1/snippets/{id}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get snippet")
        return response.json()

    async def get_project_api_keys(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/api-keys")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project api keys")
        return response.json()

    async def get_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get custom hostname")
        return response.json()

    async def remove_custom_hostname_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove custom hostname config")

    async def create_custom_hostname_config(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/initialize", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create custom hostname config")
        return response.json()

    async def reverify_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/reverify")
        if response.status_code != 200:
            raise await self._create_response_error(response, "reverify custom hostname config")
        return response.json()

    async def activate_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/activate")
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate custom hostname config")
        return response.json()

    async def get_network_bans(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-bans/retrieve")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network bans")
        return response.json()

    async def remove_network_ban(self, ref: str, body: dict):
        response = await self.client.delete(f"/v1/projects/{ref}/network-bans", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove network ban")

    async def get_network_restrictions(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/network-restrictions")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network restrictions")
        return response.json()

    async def apply_network_restrictions(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-restrictions/apply", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "apply network restrictions")
        return response.json()

    async def get_pgsodium_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/pgsodium")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get pg sodium config")
        return response.json()

    async def update_pgsodium_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/pgsodium", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update pg sodium config")
        return response.json()

    async def get_postgrest_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/postgrest")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get postgrest config")
        return response.json()

    async def update_postgrest_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/postgrest", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update postgrest config")
        return response.json()

    async def run_query(self, ref: str, query: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/database/query", json={"query": query})
        if response.status_code != 201:
            raise await self._create_response_error(response, "run query")
        return response.json()

    async def enable_webhooks(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/database/webhooks/enable")
        if response.status_code != 201:
            raise await self._create_response_error(response, "enable webhooks")

    async def get_secrets(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/secrets")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get secrets")
        return response.json()

    async def create_secrets(self, ref: str, body: dict):
        response = await self.client.post(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create secrets")

    async def delete_secrets(self, ref: str, body: dict) -> dict:
        response = await self.client.delete(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete secrets")
        return response.json()

    async def get_ssl_enforcement_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/ssl-enforcement")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get ssl enforcement config")
        return response.json()

    async def update_ssl_enforcement_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/ssl-enforcement", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update ssl enforcement config")
        return response.json()

    async def get_typescript_types(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/types/typescript")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get typescript types")
        return response.json()

    async def get_vanity_subdomain_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get vanity subdomain config")
        return response.json()

    async def remove_vanity_subdomain_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove vanity subdomain config")

    async def check_vanity_subdomain_availability(self, ref: str, subdomain: str) -> bool:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/check-availability", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "check vanity subdomain availability")
        data = response.json()
        return data.get("available", False)

    async def activate_vanity_subdomain_please(self, ref: str, subdomain: str) -> str | None:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/activate", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate vanity subdomain")
        data = response.json()
        return data.get("custom_domain")

    async def upgrade_project(self, ref: str, target_version: int):
        response = await self.client.post(f"/v1/projects/{ref}/upgrade", json={"target_version": target_version})
        if response.status_code != 200:
            raise await self._create_response_error(response, "upgrade project")

    async def get_upgrade_eligibility(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/eligibility")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade eligibility")
        return response.json()

    async def get_upgrade_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/status")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade status")
        return response.json()

    async def get_read_only_mode_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/readonly")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get readonly mode status")
        return response.json()

    async def temporarily_disable_readonly_mode(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/readonly/temporary-disable")
        if response.status_code != 200:
            raise await self._create_response_error(response, "temporarily disable readonly mode")

    async def get_pg_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/postgres")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get PG config")
        return response.json()

    async def update_pg_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/database/postgres", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update PG config")
        return response.json()

    async def get_pgbouncer_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/pgbouncer")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get Pgbouncer config")
        return response.json()

    async def get_project_auth_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project auth config")
        return response.json()

    async def update_project_auth_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/config/auth", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update project auth config")
        return response.json()

    async def get_sso_providers(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO providers")
        return response.json()

    async def create_sso_provider(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/config/auth/sso/providers", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create SSO provider")
        return response.json()

    async def get_sso_provider(self, ref: str, uuid: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO provider")
        return response.json()

    async def update_sso_provider(self, ref: str, uuid: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update SSO provider")
        return response.json()

    async def delete_sso_provider(self, ref: str, uuid: str):
        response = await self.client.delete(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 204:
            raise await self._create_response_error(response, "delete SSO provider")

    async def get_project_api_keys(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/api-keys")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project api keys")
        return response.json()

    async def get_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get custom hostname")
        return response.json()

    async def remove_custom_hostname_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove custom hostname config")

    async def create_custom_hostname_config(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/initialize", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create custom hostname config")
        return response.json()

    async def reverify_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/reverify")
        if response.status_code != 200:
            raise await self._create_response_error(response, "reverify custom hostname config")
        return response.json()

    async def activate_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/activate")
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate custom hostname config")
        return response.json()

    async def get_network_bans(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-bans/retrieve")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network bans")
        return response.json()

    async def remove_network_ban(self, ref: str, body: dict):
        response = await self.client.delete(f"/v1/projects/{ref}/network-bans", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove network ban")

    async def get_network_restrictions(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/network-restrictions")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network restrictions")
        return response.json()

    async def apply_network_restrictions(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-restrictions/apply", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "apply network restrictions")
        return response.json()

    async def get_pgsodium_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/pgsodium")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get pg sodium config")
        return response.json()

    async def update_pgsodium_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/pgsodium", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update pg sodium config")
        return response.json()

    async def get_postgrest_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/postgrest")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get postgrest config")
        return response.json()

    async def update_postgrest_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/postgrest", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update postgrest config")
        return response.json()

    async def run_query(self, ref: str, query: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/database/query", json={"query": query})
        if response.status_code != 201:
            raise await self._create_response_error(response, "run query")
        return response.json()

    async def enable_webhooks(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/database/webhooks/enable")
        if response.status_code != 201:
            raise await self._create_response_error(response, "enable webhooks")

    async def get_secrets(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/secrets")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get secrets")
        return response.json()

    async def create_secrets(self, ref: str, body: dict):
        response = await self.client.post(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create secrets")

    async def delete_secrets(self, ref: str, body: dict) -> dict:
        response = await self.client.delete(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete secrets")
        return response.json()

    async def get_ssl_enforcement_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/ssl-enforcement")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get ssl enforcement config")
        return response.json()

    async def update_ssl_enforcement_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/ssl-enforcement", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update ssl enforcement config")
        return response.json()

    async def get_typescript_types(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/types/typescript")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get typescript types")
        return response.json()

    async def get_vanity_subdomain_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get vanity subdomain config")
        return response.json()

    async def remove_vanity_subdomain_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove vanity subdomain config")

    async def check_vanity_subdomain_availability(self, ref: str, subdomain: str) -> bool:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/check-availability", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "check vanity subdomain availability")
        data = response.json()
        return data.get("available", False)

    async def activate_vanity_subdomain_please(self, ref: str, subdomain: str) -> str | None:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/activate", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate vanity subdomain")
        data = response.json()
        return data.get("custom_domain")

    async def upgrade_project(self, ref: str, target_version: int):
        response = await self.client.post(f"/v1/projects/{ref}/upgrade", json={"target_version": target_version})
        if response.status_code != 200:
            raise await self._create_response_error(response, "upgrade project")

    async def get_upgrade_eligibility(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/eligibility")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade eligibility")
        return response.json()

    async def get_upgrade_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/status")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade status")
        return response.json()

    async def get_read_only_mode_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/readonly")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get readonly mode status")
        return response.json()

    async def temporarily_disable_readonly_mode(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/readonly/temporary-disable")
        if response.status_code != 200:
            raise await self._create_response_error(response, "temporarily disable readonly mode")

    async def get_pg_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/postgres")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get PG config")
        return response.json()

    async def update_pg_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/database/postgres", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update PG config")
        return response.json()

    async def get_pgbouncer_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/pgbouncer")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get Pgbouncer config")
        return response.json()

    async def get_project_auth_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project auth config")
        return response.json()

    async def update_project_auth_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/config/auth", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update project auth config")
        return response.json()

    async def get_sso_providers(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO providers")
        return response.json()

    async def create_sso_provider(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/config/auth/sso/providers", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create SSO provider")
        return response.json()

    async def get_sso_provider(self, ref: str, uuid: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO provider")
        return response.json()

    async def update_sso_provider(self, ref: str, uuid: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update SSO provider")
        return response.json()

    async def delete_sso_provider(self, ref: str, uuid: str):
        response = await self.client.delete(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 204:
            raise await self._create_response_error(response, "delete SSO provider")

    async def list_snippets(self, project_ref: str | None = None) -> list:
        params = {}
        if project_ref:
            params["project_ref"] = project_ref
        response = await self.client.get("/v1/snippets", params=params)
        if response.status_code != 200:
            raise await self._create_response_error(response, "list snippets")
        return response.json()

    async def get_project_api_keys(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/api-keys")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project api keys")
        return response.json()

    async def get_project_api_keys(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/api-keys")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project api keys")
        return response.json()

    async def get_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get custom hostname")
        return response.json()

    async def remove_custom_hostname_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/custom-hostname")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove custom hostname config")

    async def create_custom_hostname_config(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/initialize", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create custom hostname config")
        return response.json()

    async def reverify_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/reverify")
        if response.status_code != 200:
            raise await self._create_response_error(response, "reverify custom hostname config")
        return response.json()

    async def activate_custom_hostname_config(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/custom-hostname/activate")
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate custom hostname config")
        return response.json()

    async def get_network_bans(self, ref: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-bans/retrieve")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network bans")
        return response.json()

    async def remove_network_ban(self, ref: str, body: dict):
        response = await self.client.delete(f"/v1/projects/{ref}/network-bans", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove network ban")

    async def get_network_restrictions(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/network-restrictions")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get network restrictions")
        return response.json()

    async def apply_network_restrictions(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/network-restrictions/apply", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "apply network restrictions")
        return response.json()

    async def get_pgsodium_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/pgsodium")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get pg sodium config")
        return response.json()

    async def update_pgsodium_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/pgsodium", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update pg sodium config")
        return response.json()

    async def get_postgrest_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/postgrest")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get postgrest config")
        return response.json()

    async def update_postgrest_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/postgrest", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update postgrest config")
        return response.json()

    async def run_query(self, ref: str, query: str) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/database/query", json={"query": query})
        if response.status_code != 201:
            raise await self._create_response_error(response, "run query")
        return response.json()

    async def enable_webhooks(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/database/webhooks/enable")
        if response.status_code != 201:
            raise await self._create_response_error(response, "enable webhooks")

    async def get_secrets(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/secrets")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get secrets")
        return response.json()

    async def create_secrets(self, ref: str, body: dict):
        response = await self.client.post(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create secrets")

    async def delete_secrets(self, ref: str, body: dict) -> dict:
        response = await self.client.delete(f"/v1/projects/{ref}/secrets", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "delete secrets")
        return response.json()

    async def get_ssl_enforcement_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/ssl-enforcement")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get ssl enforcement config")
        return response.json()

    async def update_ssl_enforcement_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/ssl-enforcement", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update ssl enforcement config")
        return response.json()

    async def get_typescript_types(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/types/typescript")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get typescript types")
        return response.json()

    async def get_vanity_subdomain_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get vanity subdomain config")
        return response.json()

    async def remove_vanity_subdomain_config(self, ref: str):
        response = await self.client.delete(f"/v1/projects/{ref}/vanity-subdomain")
        if response.status_code != 200:
            raise await self._create_response_error(response, "remove vanity subdomain config")

    async def check_vanity_subdomain_availability(self, ref: str, subdomain: str) -> bool:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/check-availability", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "check vanity subdomain availability")
        data = response.json()
        return data.get("available", False)

    async def activate_vanity_subdomain_please(self, ref: str, subdomain: str) -> str | None:
        response = await self.client.post(f"/v1/projects/{ref}/vanity-subdomain/activate", json={"vanity_subdomain": subdomain})
        if response.status_code != 200:
            raise await self._create_response_error(response, "activate vanity subdomain")
        data = response.json()
        return data.get("custom_domain")

    async def upgrade_project(self, ref: str, target_version: int):
        response = await self.client.post(f"/v1/projects/{ref}/upgrade", json={"target_version": target_version})
        if response.status_code != 200:
            raise await self._create_response_error(response, "upgrade project")

    async def get_upgrade_eligibility(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/eligibility")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade eligibility")
        return response.json()

    async def get_upgrade_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/upgrade/status")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get upgrade status")
        return response.json()

    async def get_read_only_mode_status(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/readonly")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get readonly mode status")
        return response.json()

    async def temporarily_disable_readonly_mode(self, ref: str):
        response = await self.client.post(f"/v1/projects/{ref}/readonly/temporary-disable")
        if response.status_code != 200:
            raise await self._create_response_error(response, "temporarily disable readonly mode")

    async def get_pg_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/postgres")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get PG config")
        return response.json()

    async def update_pg_config(self, ref: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/database/postgres", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update PG config")
        return response.json()

    async def get_pgbouncer_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/database/pgbouncer")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get Pgbouncer config")
        return response.json()

    async def get_project_auth_config(self, ref: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get project auth config")
        return response.json()

    async def update_project_auth_config(self, ref: str, body: dict) -> dict:
        response = await self.client.patch(f"/v1/projects/{ref}/config/auth", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update project auth config")
        return response.json()

    async def get_sso_providers(self, ref: str) -> list:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO providers")
        return response.json()

    async def create_sso_provider(self, ref: str, body: dict) -> dict:
        response = await self.client.post(f"/v1/projects/{ref}/config/auth/sso/providers", json=body)
        if response.status_code != 201:
            raise await self._create_response_error(response, "create SSO provider")
        return response.json()

    async def get_sso_provider(self, ref: str, uuid: str) -> dict:
        response = await self.client.get(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 200:
            raise await self._create_response_error(response, "get SSO provider")
        return response.json()

    async def update_sso_provider(self, ref: str, uuid: str, body: dict) -> dict:
        response = await self.client.put(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}", json=body)
        if response.status_code != 200:
            raise await self._create_response_error(response, "update SSO provider")
        return response.json()

    async def delete_sso_provider(self, ref: str, uuid: str):
        response = await self.client.delete(f"/v1/projects/{ref}/config/auth/sso/providers/{uuid}")
        if response.status_code != 204:
            raise await self._create_response_error(response, "delete SSO provider")
