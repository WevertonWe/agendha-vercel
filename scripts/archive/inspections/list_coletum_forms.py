import asyncio
from app.services.coletum_service import listar_formularios_coletum

async def main():
    forms = await listar_formularios_coletum()
    print(f"Total de formulários Coletum: {len(forms)}")
    for f in forms:
        print(f"ID: {f.get('id')} | Nome: {f.get('name')}")

asyncio.run(main())
