from alletra_onboard.adapters.greenlake.service_catalog import parse_service_manager_provision


def test_parse_service_manager_provision_uses_service_manager_id():
    provision = parse_service_manager_provision(
        {
            "serviceManager": {"id": "svc-123", "resourceUri": "/service-catalog/v1/service-managers/svc-123"},
            "region": "ap-northeast",
            "provisionStatus": "PROVISIONED",
            "resourceUri": "/service-catalog/v1/service-manager-provisions/prov-123",
        }
    )
    assert provision.service_manager_id == "svc-123"
    assert provision.region == "ap-northeast"
    assert provision.provision_status == "PROVISIONED"
