# Supabase Management Python Client

A Python client for the Supabase Management API.

## Installation

```bash
pip install supabase-management
```

## Usage

```python
import asyncio
from supabase_management import SupabaseManagementAPI

async def main():
    access_token = "YOUR_SUPABASE_ACCESS_TOKEN"
    supabase = SupabaseManagementAPI(access_token)

    # Example: Get organizations
    organizations = await supabase.get_organizations()
    print("Organizations:", organizations)

    # Example: Create a project (replace with your actual organization ID and project details)
    # try:
    #     new_project = await supabase.create_project({
    #         "name": "my-new-project",
    #         "organization_id": "your-org-id",
    #         "plan": "free"
    #     })
    #     print("New Project:", new_project)
    # except Exception as e:
    #     print(f"Error creating project: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```
