from pathlib import Path

from alletra_onboard.application.intake import load_work_items_csv


def test_load_work_items_csv(tmp_path: Path):
    csv_path = tmp_path / "arrays.csv"
    csv_path.write_text(
        "serial_number,part_number,subscription_key,service_catalog_region_id,dscc_region_code,cloudinit_url,mgmt_ipv4,mask,gateway,dns,ntp,timezone,proxy_host,proxy_port,dscc_system_name,dscc_country,blueprint_name,apply_blueprint\n"
        "SGHD44LQLS,S0B84A,secret,ap-northeast,jp1,https://169.254.239.27/cloudinit,10.64.122.140,255.255.255.0,10.64.122.1,10.0.0.10;10.0.0.11,ntp.example.com,Asia/Kolkata,proxy.example.com,8080,array01,India,bp,true\n",
        encoding="utf-8",
    )
    items = load_work_items_csv(csv_path)
    assert len(items) == 1
    assert items[0].network.dns == ["10.0.0.10", "10.0.0.11"]
    assert items[0].dscc_setup.apply_blueprint is True
    # DSCC support-contact/credential columns are optional; absent -> sensible defaults.
    assert items[0].dscc_setup.credential_name == "b10000-admin"
    assert items[0].dscc_setup.username == "3paradm"
    assert items[0].dscc_setup.password is None
    assert items[0].dscc_setup.contact_language == "English"


def test_load_work_items_csv_with_dscc_fields(tmp_path: Path):
    csv_path = tmp_path / "arrays.csv"
    header = (
        "serial_number,part_number,subscription_key,service_catalog_region_id,dscc_region_code,"
        "cloudinit_url,mgmt_ipv4,mask,gateway,dns,ntp,timezone,proxy_host,proxy_port,"
        "dscc_system_name,dscc_country,contact_first_name,contact_last_name,contact_language,"
        "contact_company,contact_phone,contact_email,secret_name,secret_username,secret_password,"
        "blueprint_name,apply_blueprint\n"
    )
    row = (
        "SGHD45FF0Y,S0B84A,KEY,ap-northeast,jp1,https://169.254.184.89/cloudinit,10.64.154.225,"
        "255.255.248.0,10.64.159.254,10.203.96.10;10.203.96.9,ntp.example.net,Asia/Kolkata,"
        "proxy.example.net,8080,MPB10K-E24U21-LZ,India,Gantasala,Sai Roopesh,English,HPE,"
        "8217270831,g-sai-roopesh@hpe.com,crv,3paradm,3pardata,,false\n"
    )
    csv_path.write_text(header + row, encoding="utf-8")
    dscc = load_work_items_csv(csv_path)[0].dscc_setup
    assert dscc.system_name == "MPB10K-E24U21-LZ"
    assert dscc.country == "India"
    assert (dscc.contact_first_name, dscc.contact_last_name) == ("Gantasala", "Sai Roopesh")
    assert dscc.contact_company == "HPE"
    assert dscc.contact_email == "g-sai-roopesh@hpe.com"
    assert dscc.credential_name == "crv"
    assert dscc.password is not None and dscc.password.get_secret_value() == "3pardata"
