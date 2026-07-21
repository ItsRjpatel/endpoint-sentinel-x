# ruff: noqa: E501
"""
Storage Inventory Collector for Endpoint Sentinel X.

Collects comprehensive storage information including physical disks, SMART data,
partitions, volumes, storage pools, and virtual disks.
"""

import json
from datetime import datetime, timezone

import structlog

from config.settings import agent_settings
from models.inventory import (
    DiskPayload,
    StorageInventoryRequest,
    StoragePoolPayload,
    VolumePayload,
)
from utils.hashing import compute_inventory_hash
from utils.powershell import run_powershell
from utils.serialization import serialize_storage

logger = structlog.get_logger(__name__)


def collect_storage() -> StorageInventoryRequest:
    """Collects all storage configuration from the Windows endpoint."""
    script = r"""
    $ErrorActionPreference = 'SilentlyContinue'

    # 1. Disks & SMART
    $disksRaw = Get-Disk | Select-Object Number, FriendlyName, Manufacturer, Model, SerialNumber, FirmwareVersion, BusType, HealthStatus, OperationalStatus, Size, LogicalSectorSize, PhysicalSectorSize, IsBoot, IsSystem, UniqueId, Location, PartitionStyle, IsOffline, IsReadOnly
    $disks = @()

    foreach ($d in $disksRaw) {
        $smartRaw = Get-StorageReliabilityCounter -DiskNumber $d.Number -ErrorAction SilentlyContinue
        $smart = $null
        if ($smartRaw) {
            $smart = @{
                predict_failure = if ($smartRaw.PredictFailure -ne $null) { $smartRaw.PredictFailure } else { $null }
                temperature = if ($smartRaw.Temperature -ne $null) { [int]$smartRaw.Temperature } else { $null }
                wear_level = if ($smartRaw.Wear -ne $null) { [int]$smartRaw.Wear } else { $null }
                remaining_life = if ($smartRaw.LifeRemaining -ne $null) { [int]$smartRaw.LifeRemaining } else { $null }
                reallocated_sector_count = if ($smartRaw.ReallocatedSectors -ne $null) { [int]$smartRaw.ReallocatedSectors } else { $null }
            }
        }

        $pd = Get-PhysicalDisk -DeviceId $d.Number -ErrorAction SilentlyContinue
        $mediaType = if ($pd -and $pd.MediaType) { [string]$pd.MediaType } else { $null }
        $busType = if ($pd -and $pd.BusType) { [string]$pd.BusType } elseif ($d.BusType) { [string]$d.BusType } else { $null }
        $canPool = if ($pd -and $pd.CanPool -ne $null) { $pd.CanPool } else { $false }
        $rotationRate = if ($pd -and $pd.SpindleSpeed -ne $null -and $pd.SpindleSpeed -ne [uint32]::MaxValue) { [int]$pd.SpindleSpeed } else { $null }

        $disks += @{
            device_name = "PhysicalDrive$($d.Number)"
            friendly_name = $d.FriendlyName
            manufacturer = $d.Manufacturer
            model = $d.Model
            serial_number = $d.SerialNumber
            firmware_version = $d.FirmwareVersion
            interface_type = $busType
            bus_type = $busType
            media_type = $mediaType
            health_status = if ($d.HealthStatus) { [string]$d.HealthStatus } else { $null }
            operational_status = if ($d.OperationalStatus) { [string]$d.OperationalStatus } else { $null }
            size_bytes = $d.Size
            logical_sector_size = $d.LogicalSectorSize
            physical_sector_size = $d.PhysicalSectorSize
            rotation_rate = $rotationRate
            is_removable = if ($busType -eq 'USB') { $true } else { $false }
            is_boot_disk = if ($d.IsBoot -ne $null) { $d.IsBoot } else { $false }
            is_system_disk = if ($d.IsSystem -ne $null) { $d.IsSystem } else { $false }
            unique_id = $d.UniqueId
            location = $d.Location
            partition_style = if ($d.PartitionStyle) { [string]$d.PartitionStyle } else { $null }
            is_offline = if ($d.IsOffline -ne $null) { $d.IsOffline } else { $false }
            is_read_only = if ($d.IsReadOnly -ne $null) { $d.IsReadOnly } else { $false }
            can_pool = $canPool
            smart = $smart
            partitions = @()
            Number = $d.Number
        }
    }

    # 2. Partitions
    $partitionsRaw = Get-Partition | Select-Object DiskNumber, PartitionNumber, Type, Size, Offset, DriveLetter, IsBoot, IsActive, IsHidden, IsReadOnly, AccessPaths, MbrType, GptType
    foreach ($p in $partitionsRaw) {
        $matchedDisk = $null
        for ($i=0; $i -lt $disks.Count; $i++) {
            if ($disks[$i].Number -eq $p.DiskNumber) {
                $matchedDisk = $disks[$i]
                break
            }
        }
        if (-not $matchedDisk) { continue }

        $volRef = $null
        if ($p.AccessPaths) {
            foreach ($ap in $p.AccessPaths) {
                if ($ap -match "^\\\\\\?\\\\Volume") {
                    $volRef = $ap
                    break
                }
            }
        }

        $partType = $p.Type
        if (-not $partType) {
            if ($p.MbrType) { $partType = [string]$p.MbrType }
            elseif ($p.GptType) { $partType = [string]$p.GptType }
        }

        $part = @{
            partition_number = $p.PartitionNumber
            partition_style = $matchedDisk.partition_style
            partition_type = $partType
            size_bytes = $p.Size
            offset_bytes = $p.Offset
            drive_letter = if ($p.DriveLetter -and $p.DriveLetter -ne "`0") { [string]$p.DriveLetter } else { $null }
            is_boot = if ($p.IsBoot -ne $null) { $p.IsBoot } else { $false }
            is_active = if ($p.IsActive -ne $null) { $p.IsActive } else { $false }
            is_hidden = if ($p.IsHidden -ne $null) { $p.IsHidden } else { $false }
            is_read_only = if ($p.IsReadOnly -ne $null) { $p.IsReadOnly } else { $false }
            volume_id_ref = $volRef
        }
        $matchedDisk.partitions += $part
    }

    # Remove internal sorting property
    foreach ($d in $disks) {
        $d.psobject.properties.remove('Number')
    }

    # 3. Volumes
    $volumesRaw = Get-Volume | Select-Object DriveLetter, FileSystemLabel, FileSystem, HealthStatus, Size, SizeRemaining, UniqueId, AllocationUnitSize
    $volumes = @()
    foreach ($v in $volumesRaw) {
        $driveLetter = if ($v.DriveLetter -and $v.DriveLetter -ne "`0") { [string]$v.DriveLetter } else { $null }
        $vol = @{
            volume_id_ref = $v.UniqueId
            drive_letter = $driveLetter
            volume_name = $v.FileSystemLabel
            file_system = if ($v.FileSystem) { [string]$v.FileSystem } else { $null }
            file_system_label = $v.FileSystemLabel
            file_system_version = $null
            allocation_unit_size = $v.AllocationUnitSize
            total_size = $v.Size
            free_space = $v.SizeRemaining
            used_space = if ($v.Size -ne $null -and $v.SizeRemaining -ne $null) { $v.Size - $v.SizeRemaining } else { $null }
            percentage_used = if ($v.Size -gt 0) { [Math]::Round(($v.Size - $v.SizeRemaining) / $v.Size * 100, 2) } else { $null }
            percentage_free = if ($v.Size -gt 0) { [Math]::Round($v.SizeRemaining / $v.Size * 100, 2) } else { $null }
            health_status = if ($v.HealthStatus) { [string]$v.HealthStatus } else { $null }
            compression_enabled = $null
            deduplication_enabled = $null
            shadow_copies_enabled = $null
            mounts = @()
        }

        # Add basic mount point
        if ($driveLetter) {
            $vol.mounts += @{ mount_path = "$($driveLetter):\" }
        }

        $volumes += $vol
    }

    # 4. Storage Pools
    $poolsRaw = Get-StoragePool -IsPrimordial $false -ErrorAction SilentlyContinue | Select-Object FriendlyName, HealthStatus, OperationalStatus, Size, AllocatedSize
    $pools = @()
    if ($poolsRaw) {
        foreach ($sp in $poolsRaw) {
            $pName = $sp.FriendlyName
            $vdsRaw = Get-VirtualDisk -StoragePoolFriendlyName $pName -ErrorAction SilentlyContinue | Select-Object FriendlyName, ResiliencySettingName, ProvisioningType, HealthStatus, OperationalStatus, Size
            $vds = @()
            if ($vdsRaw) {
                foreach ($vd in $vdsRaw) {
                    $vds += @{
                        virtual_disk_name = $vd.FriendlyName
                        resiliency_type = if ($vd.ResiliencySettingName) { [string]$vd.ResiliencySettingName } else { $null }
                        provisioning_type = if ($vd.ProvisioningType) { [string]$vd.ProvisioningType } else { $null }
                        health_status = if ($vd.HealthStatus) { [string]$vd.HealthStatus } else { $null }
                        operational_status = if ($vd.OperationalStatus) { [string]$vd.OperationalStatus } else { $null }
                        size_bytes = $vd.Size
                    }
                }
            }

            $pools += @{
                pool_name = $pName
                health_status = if ($sp.HealthStatus) { [string]$sp.HealthStatus } else { $null }
                operational_status = if ($sp.OperationalStatus) { [string]$sp.OperationalStatus } else { $null }
                total_capacity = $sp.Size
                free_capacity = if ($sp.Size -ne $null -and $sp.AllocatedSize -ne $null) { $sp.Size - $sp.AllocatedSize } else { $null }
                virtual_disks = $vds
            }
        }
    }

    $payload = @{
        disks = $disks
        volumes = $volumes
        storage_pools = $pools
    }

    $payload | ConvertTo-Json -Depth 5
    """

    try:
        output = run_powershell(script)
        if not output.strip():
            logger.warning("Storage script returned empty output")
            data = {"disks": [], "volumes": [], "storage_pools": []}
        else:
            data = json.loads(output)
    except Exception as e:
        logger.error("Storage PowerShell execution failed", error=str(e))
        data = {"disks": [], "volumes": [], "storage_pools": []}

    try:
        # Construct strongly-typed sub-objects
        disks_payload = [DiskPayload(**d) for d in data.get("disks", [])]
        volumes_payload = [VolumePayload(**v) for v in data.get("volumes", [])]
        pools_payload = [StoragePoolPayload(**p) for p in data.get("storage_pools", [])]

        collected_at = datetime.now(timezone.utc)
        agent_version = agent_settings.agent_version

        # Dummy hash to allow serialization
        request_obj = StorageInventoryRequest(
            collected_at=collected_at,
            agent_version=agent_version,
            inventory_hash="pending",
            disks=disks_payload,
            volumes=volumes_payload,
            storage_pools=pools_payload,
        )

        canonical_json = serialize_storage(request_obj)
        request_obj.inventory_hash = compute_inventory_hash(canonical_json)
        return request_obj

    except Exception as e:
        logger.error("Storage payload construction failed", error=str(e))
        raise
