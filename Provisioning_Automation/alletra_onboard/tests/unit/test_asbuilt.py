import docx
from docx.oxml.ns import qn

from alletra_onboard.application.asbuilt import AsBuiltData, default_template, generate_asbuilt

_CHECKHEALTH = (
    "Checking alert\n"
    "Component ----Summary Description---- Qty\n"
    "Alert     New alerts                    9\n"
    "Cage      Cages degraded                1\n"
    "----------------------------------------\n"
    "        2 total                        10\n"
    "\n"
    "Component --Identifier-- ---Detailed Description--- Resolution\n"
    "Alert     hw_cage:1      Cage over temperature      Manual\n"
    "-------------------------------------------------------------\n"
    "       1 total                                      10\n"
)

_INVENTORY = (  # showinventory -csvtable output
    "-----------------------Cage Inventory--------------------,,,\n"
    "Cage,-Name-,-Manufacturer-,-Type-\n"
    "1,cage1,HPE,DCN7\n"
    ",,,\n"
    "-----------------------Disk Inventory--------------------,,,\n"
    "Id,CagePos,State,--MFR--\n"
    "0,1:1,normal,SAMSUNG\n"
)

_SAMPLE = AsBuiltData(
    customer="ACME Corp", name="MPB10K-E24U21-LZ", model="HPE Alletra Storage MP",
    serial_no="SGHD45FF0Y", controller_nodes="2", os_version="10.5.51", drive_cages="1 (cage1)",
    cache_gb="503 GiB", nvme_ssd_disks="10 x 3.84 TB NVMe SSD", raw_capacity="34.9 TiB",
    raid="RAID 6 (SSD_r6)", host_ports="8 x 32Gbps FC target",
    mgmt_ip="10.64.154.225", netmask="255.255.248.0", gateway="10.64.159.254",
    ntp="ntp.example.net", dns="10.203.96.10, 10.203.96.9",
    inventory=_INVENTORY, checkhealth=_CHECKHEALTH,
)


def _read(path):
    doc = docx.Document(str(path))
    text = "".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))
    return doc, text


def test_default_template_is_the_bundled_block_storage_docx():
    t = default_template()
    assert t is not None and t.name == "asbuilt_template.docx" and t.is_file()


def test_generate_fills_cover_table01_and_renders_checkhealth_tables(tmp_path):
    out = generate_asbuilt(_SAMPLE, tmp_path / "asbuilt.docx")
    doc, text = _read(out)

    # cover-page customer name replaced
    assert "ACME Corp" in text and "<Customer Name>" not in text

    # Table 01 (the template's own table) filled by label
    t01 = {r.cells[0].text.strip(): r.cells[1].text.strip() for r in doc.tables[0].rows}
    assert t01["Serial No"] == "SGHD45FF0Y"
    assert t01["InServ IP Address"] == "10.64.154.225"
    assert t01["Cache(GB)"].startswith("503 GiB")

    # checkhealth + inventory rendered as HPE Word tables (found by their headers, any order)
    all_headers = [tuple(c.text.strip() for c in t.rows[0].cells) for t in doc.tables]
    assert ("Component", "Summary Description", "Qty") in all_headers
    assert any(h[:2] == ("Component", "Identifier") for h in all_headers)
    assert any("Manufacturer" in h for h in all_headers)  # an inventory sub-table

    # inventory values landed in a table, and the template's boilerplate is preserved
    assert "cage1" in text and "SAMSUNG" in text
    assert "Proprietary Notice" in text


def test_generate_leaves_placeholder_when_no_customer(tmp_path):
    out = generate_asbuilt(AsBuiltData(serial_no="SGH123"), tmp_path / "no_cust.docx")
    _doc, text = _read(out)
    assert "<Customer Name>" in text  # untouched when the operator gives no customer
