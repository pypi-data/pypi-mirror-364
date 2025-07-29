# IPE Python Client

A modern, asynchronous, and easy-to-use Python SDK for the IPE API.

## Installation

Install the package directly from PyPI:

```bash
pip install ipe-client
```

## Usage

Here is a basic example of how to instantiate the client and check a job status. The client should be used in an `async` context.

```python
import asyncio
import os
from ipe_client import IPEClient

async def main():
    # Load configuration securely from environment variables
    client = IIPSClient(
        base_url=os.environ.get("IPE_BASE_URL"),
        username=os.environ.get("IPE_USERNAME"),
        password=os.environ.get("IPE_PASSWORD")
    )

    try:
        job_ids = ["some-job-id-from-a-previous-submission"]
        status = await client.check_iips_job_status(job_ids)
        print(status)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # It's important to close the client to release connections.
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```