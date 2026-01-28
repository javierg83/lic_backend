import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from features.licitaciones.sub_features.items.actions.show.service import ItemsLicitacionShowService

async def verify():
    licitacion_id = "2b54095a-5a9c-4510-ade8-4f426487c887"
    print(f"Verifying items for licitacion_id: {licitacion_id}")
    
    response = await ItemsLicitacionShowService.process(licitacion_id)
    
    if response.success:
        print(f"Success: {response.message}")
        print(f"Number of items: {len(response.data.items)}")
        for i, item in enumerate(response.data.items):
            print(f"  {i+1}. {item.nombre_item} - {item.cantidad} {item.unidad}")
            if i >= 2 and i < 14:
                 if i == 3: print("  ...")
                 continue
    else:
        print(f"Error: {response.message}")
        if response.error:
            print(f"Details: {response.error}")

if __name__ == "__main__":
    asyncio.run(verify())
