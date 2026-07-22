import asyncio
import httpx
from collectors.hardware import collect as collect_hardware
from collectors.operating_system import collect as collect_os

async def enroll():
    # Token from earlier seed
    token = "68f3d11d-1d5d-40ff-ab2c-dea342d21567"
    
    # Collect real hardware data
    hw = collect_hardware()
    os_info = collect_os()
    
    print(hw.model_dump())
    
    import uuid
    payload = {
        "hostname": os_info.computer_name,
        "os_platform": os_info.name,
        "os_version": os_info.version,
        "hardware_uuid": str(uuid.uuid4()),
        "ip_address": "127.0.0.1", # placeholder for IP
        "enrollment_token": token
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/agent/register",
            json=payload,
            headers=headers
        )
        
        if response.status_code in (200, 201):
            data = response.json()
            agent_id = data["agent_id"]
            agent_secret = data["agent_secret"]
            
            with open(".env.agent", "w") as f:
                f.write(f"AGENT_ID={agent_id}\n")
                f.write(f"AGENT_SECRET={agent_secret}\n")
                f.write("API_BASE_URL=http://localhost:8000\n")
            
            print(f"Agent successfully enrolled! ID: {agent_id}")
        else:
            print(f"Failed to enroll: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(enroll())
