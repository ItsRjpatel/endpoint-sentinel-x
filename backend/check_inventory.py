import asyncio
import httpx
from sqlalchemy import select
from app.db.models.inventory_hardware import InventoryHardware
from app.db.models.inventory_os import InventoryOS
from app.db.models.inventory_security_status import InventorySecurityStatus
from app.db.session import AsyncSessionLocal

async def main():
    headers = {
        'X-Agent-ID': 'bde173ad-adee-4b86-8867-ce9faf02fc03',
        'X-Agent-Secret': 'esx_as_f26fdcf2c6c6a99cd6ec24198cd97ab0c5f1b653546db046cae3a649a1b12d79',
        'Content-Type': 'application/json',
    }

    hardware_payload = {
        'collected_at': '2026-07-23T00:00:00+00:00',
        'agent_version': '0.1.0',
        'inventory_hash': 'test-hash-hardware',
        'hardware': {
            'cpu_model': 'Test CPU',
            'cpu_cores': 4,
            'cpu_threads': 8,
            'total_ram_bytes': 16000000000,
            'system_manufacturer': 'Test',
            'system_model': 'Model',
            'bios_version': '1.0',
        },
    }
    os_payload = {
        'collected_at': '2026-07-23T00:00:00+00:00',
        'agent_version': '0.1.0',
        'inventory_hash': 'test-hash-os',
        'os': {
            'name': 'Microsoft Windows 11 Pro',
            'edition': 'Pro',
            'version': '10.0.26200',
            'build_number': '26200',
            'display_version': '24H2',
            'architecture': '64-bit',
            'computer_name': 'DESKTOP',
            'domain': 'WORKGROUP',
        },
    }
    security_payload = {
        'collected_at': '2026-07-23T00:00:00+00:00',
        'agent_version': '0.1.0',
        'inventory_hash': 'test-hash-security',
        'security': {
            'defender': {'installed': True, 'enabled': True, 'real_time_protection': True},
            'tpm': {'present': True, 'enabled': True},
            'secure_boot': {'supported': True, 'enabled': True},
            'uac': {'enabled': True},
            'security_center': {'status': 'Healthy'},
        },
    }

    with httpx.Client() as client:
        hardware_resp = client.post('http://127.0.0.1:8000/api/v1/inventory/hardware', json=hardware_payload, headers=headers)
        os_resp = client.post('http://127.0.0.1:8000/api/v1/inventory/os', json=os_payload, headers=headers)
        security_resp = client.post('http://127.0.0.1:8000/api/v1/inventory/security', json=security_payload, headers=headers)
        print('hardware', hardware_resp.status_code, hardware_resp.text)
        print('os', os_resp.status_code, os_resp.text)
        print('security', security_resp.status_code, security_resp.text)

    async with AsyncSessionLocal() as db:
        hw = (await db.execute(select(InventoryHardware).where(InventoryHardware.endpoint_id == 790))).scalars().first()
        os_row = (await db.execute(select(InventoryOS).where(InventoryOS.endpoint_id == 790))).scalars().first()
        sec_row = (await db.execute(select(InventorySecurityStatus).where(InventorySecurityStatus.endpoint_id == 790))).scalars().first()
        print('hw_row', bool(hw), hw.cpu_model if hw else None)
        print('os_row', bool(os_row), os_row.name if os_row else None)
        print('sec_row', bool(sec_row), sec_row.defender_enabled if sec_row else None)

asyncio.run(main())
