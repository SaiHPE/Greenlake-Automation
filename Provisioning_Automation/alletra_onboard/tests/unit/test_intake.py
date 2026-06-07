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
