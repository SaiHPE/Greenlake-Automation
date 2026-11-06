from alletra_onboard.application.documents.asbuilt_parse import (
    parse_asbuilt,
    parse_checkhealth,
    parse_inventory,
    split_sections,
)

# A genericized dump that mirrors the real `asbuilt_array.py` output format (no lab data).
_DUMP = """# ASBUILT + PROVISIONING READ-ONLY ARRAY DUMP
# array=10.0.0.10  user=3paradm

===== $ shownode =====
Node ----Name---- Encl:Bay Master InCluster Mem(MiB) -------Up_Since--------
   0 TESTSN0001-0      1:1 Yes    Yes         257498 2026-05-21 10:52:08 IST
   1 TESTSN0001-1      1:2 No     Yes         257498 2026-05-21 10:52:25 IST

===== $ showcage =====
Id Name  Drives Temp  Model FormFactor State
 1 cage1     10 28-29 DCN7  SFF        normal

===== $ showsys -d =====
System Name                  :         TEST-ARRAY-01
System Model                 :   HPE Alletra Storage MP
Serial Number                :               TESTSN0001
Number of Nodes              :                        2

---Raw System Capacity (MiB)---
Total Capacity     :   36608000
Allocated Capacity :     522771

-Usable System Capacity (MiB)--
Total Capacity     :   25675204

===== $ shownet =====
IP Address    Netmask/PrefixLen Nodes Active Speed Duplex AutoNeg Status Mode
10.0.0.10         255.255.248.0    01      0  1000 Full   Yes     Active Static

Default IPv4 route :                                      10.0.0.254
NTP server         :                 ntp.example.net
DNS server         :                           10.1.1.1 10.1.1.2

===== $ showversion =====
Release version 10.5.51
Release Type: Standard Support Release

===== $ showpd =====
Id CagePos Type RPM State     Total     Free Capacity(GB)
 0 1:1     SSD  N/A normal  3660800  3386368         3840
 1 1:2     SSD  N/A normal  3660800  3386368         3840
 2 1:3     SSD  N/A normal  3660800  3386368         3840
---------------------------------------------------------
 3 total                   ...

===== $ showcpg =====
Id Name   Warn% VVs TPVVs TDVVs   Used   Free  Total
 0 SSD_r6     -   8     8     0 491400 145950 637350
----------------------------------------------------
 1 total                        491400 145950 637350

===== $ showport =====
N:S:P   Mode     State --Node_WWN/IP--- -Port_WWN/HW_Addr-    Type Protocol Label
0:3:1 target     ready 2FF70002AC000000   20310002AC000000    host       FC     -
0:3:3 target loss_sync 2FF70002AC000000   20330002AC000000    free       FC     -
0:4:1 target   offline          0.0.0.0       40A6B7000000    free    iSCSI     -
0:5:1   peer     ready                -        202AC000103 cluster       IP     -

===== $ showport -par =====
N:S:P Connmode ConnType CfgRate MaxRate Class2   UniqNodeWwn VCN      IntCoal TMWO
0:3:1 host     point    auto    32Gbps  disabled disabled    disabled enabled disabled

===== $ showinventory =====
-----------------------Cage Inventory--------------------
Cage -Name- -Manufacturer- -Assem_Part-
   1 cage1  HPE            R7C75-63004

===== $ checkhealth -svc -detail =====
Checking alert
Checking cage
Component ----Summary---- Qty
Cage      Cages degraded   1
-----------------------------
        2 total            3
"""


def test_split_sections_keys_by_command():
    sec = split_sections(_DUMP)
    assert "showsys -d" in sec and "checkhealth -svc -detail" in sec
    assert "System Name" in sec["showsys -d"]


def test_parse_asbuilt_extracts_every_table01_field():
    d = parse_asbuilt(_DUMP)
    assert d.name == "TEST-ARRAY-01"
    assert d.model == "HPE Alletra Storage MP"
    assert d.serial_no == "TESTSN0001"
    assert d.controller_nodes == "2"
    assert d.os_version == "10.5.51"
    assert d.drive_cages == "1 (cage1)"
    assert "GiB" in d.cache_gb                       # 2 x 257498 MiB -> ~503 GiB
    assert d.nvme_ssd_disks == "3 x 3.84 TB NVMe SSD"
    assert d.raid == "RAID 6 (SSD_r6)"
    assert d.host_ports.startswith("2 x 32Gbps FC target") and "0:3:1" in d.host_ports
    assert d.mgmt_ip == "10.0.0.10" and d.netmask == "255.255.248.0"
    assert d.gateway == "10.0.0.254"
    assert d.ntp == "ntp.example.net"
    assert d.dns == "10.1.1.1, 10.1.1.2"
    assert "Cage Inventory" in d.inventory
    assert "Checking alert" in d.checkhealth and "2 total" in d.checkhealth


def test_raw_capacity_takes_raw_not_usable_total():
    # There are TWO "Total Capacity" lines (Raw + Usable); the as-built shows the Raw one.
    d = parse_asbuilt(_DUMP)
    assert "36,608,000" in d.raw_capacity and "25,675,204" not in d.raw_capacity


def test_host_ports_excludes_iscsi_and_peer_ports():
    d = parse_asbuilt(_DUMP)
    assert "0:4:1" not in d.host_ports and "0:5:1" not in d.host_ports


_CHECKHEALTH = """Checking alert
Checking cage
Component ----------------Summary Description---------------- Qty
Alert     New alerts                                            9
vlun      Hosts not connected to a port                         1
-----------------------------------------------------------------
       2 total                                                 10

Component ---Identifier--- ------Detailed Description------ Resolution
Alert     hw_cage:1        Cage cage1 over temperature      Manual
Task      Task:7092        Failed Task                      Manual
--------------------------------------------------------------------
       2 total                                                     2
"""


# `showinventory -csvtable` output — deterministic CSV (quoted commas, values with spaces).
_INVENTORY = """ID,------Name------,--------Model---------,--Serial--,System_PN,Nodes
0x2F629,TEST-ARRAY-01,HPE Alletra Storage MP,TESTSN0001,S0B84A,2

-------------------------------Interface Card-------------------------------,,,,,,
Cage,-I/F_card-,-Name-,-Manufacturer-,-Assem_Part-,-Assem_Serial-,-Firmware-
1,1,Node 0,HPE,R7D02-63003,EXTVUB912M200K,1005
,,,,,,
------------------------------Memory Devices-------------------------------,,,,,,,,(GiB/s),(GiB),------
Cage,IOM,Mem,-------Name--------,Type,Manufacturer,--PartNumber---,-Serial-,Speed,Size,RCD
1,1,1,Iom[1]PROC 1 DIMM 1,DDR4,Hynix,HMAG84EXNRA086N,3727967E,3200,32,0xb380
,,,,,,,,,,
---------------------------------------------CPU---------------------------------------------,,,,,,
Cage,IOM,Slot,Cores,Threads,--------Manufacturer--------,---------------Model----------------
1,1,1,16,32,"Advanced Micro Devices, Inc.",0 (AMD EPYC 7313P 16-Core Processor)
------------------------------------
2,total,,
"""


def test_parse_inventory_splits_csv_subsections():
    tables = parse_inventory(_INVENTORY)
    by_title = {title: (headers, rows) for title, headers, rows in tables}
    assert set(by_title) == {"", "Interface Card", "Memory Devices", "CPU"}  # footer/blank rows dropped

    # the array-id block (no section title)
    assert by_title[""][1][0][3] == "TESTSN0001"

    # a value with an internal space stays one cell
    assert by_title["Interface Card"][1][0][2] == "Node 0"

    # REGRESSION (was mis-split by fixed-width): Speed/Size/RCD land in the right columns
    assert by_title["Memory Devices"][1][0][-3:] == ["3200", "32", "0xb380"]

    # a quoted comma inside a value is one cell (csv, not naive split)
    assert by_title["CPU"][1][0][5] == "Advanced Micro Devices, Inc."


def test_parse_checkhealth_splits_summary_and_detail_tables():
    summary, detail = parse_checkhealth(_CHECKHEALTH)
    assert ("Alert", "New alerts", "9") in summary
    assert ("vlun", "Hosts not connected to a port", "1") in summary
    assert ("Alert", "hw_cage:1", "Cage cage1 over temperature", "Manual") in detail
    assert ("Task", "Task:7092", "Failed Task", "Manual") in detail
    # the "N total M" footers must not leak into the rows
    assert all(not r[0].isdigit() for r in summary + [(d[0],) for d in detail])
