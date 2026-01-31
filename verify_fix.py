import asyncio
import uuid
from src.features.licitaciones.sub_features.items.actions.show.service import ItemsLicitacionShowService

async def verify():
    # Use a random UUID to ensure it doesn't exist in DB
    random_id = str(uuid.uuid4())
    print(f"Testing with random ID: {random_id}")
    
    response = await ItemsLicitacionShowService.process(random_id)
    
    print(f"Response success: {response.success}")
    print(f"Items count: {len(response.data.items)}")
    
    if response.success and len(response.data.items) == 0:
        print("SUCCESS: Items list is empty as expected.")
    else:
        print("FAILURE: Items list is not empty or request failed.")

if __name__ == "__main__":
    asyncio.run(verify())
