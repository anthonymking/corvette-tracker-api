import asyncio
import json
from matson_tracker import get_tracking_info

async def main():
    status = await get_tracking_info()
    with open("status_cache.json", "w") as f:
        json.dump(status, f)

if __name__ == "__main__":
    asyncio.run(main()) 