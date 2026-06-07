---
title: "HPE GreenLake Consumption Analytics Usage Fields"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/usage-fields.md"
scraped_at: "2026-06-07T05:46:08.063667+00:00Z"
---

# HPE GreenLake Consumption Analytics Usage Fields

Usage fields are the attributes available for filtering, grouping, and displaying data in reports. There are two categories of fields: system fields and provider fields.

## System fields

System fields are present for **all tenants**, regardless of the data sources configured. They represent the normalized, cross-provider schema that Consumption Analytics maps all usage data into.

| Field Name | Display Name |
|  --- | --- |
| `sys_AccountId_s` | Account ID |
| `sys_AccountingDate_d` | Accounting Date |
| `sys_AccountingMonth_d` | Accounting Month |
| `sys_AccountingQuarter_d` | Accounting Quarter |
| `sys_AccountingYear_d` | Accounting Year |
| `sys_AccountName_s` | Account Name |
| `sys_AccountOwner_s` | Account Owner |
| `sys_AccountOwnerId_s` | Account Owner ID |
| `sys_Billable_s` | Billable |
| `sys_CapacityFree_f` | Capacity Free |
| `sys_CapacityFreePct_f` | Capacity Free Percent |
| `sys_CapacityUnit_s` | Capacity Units |
| `sys_CapacityUsable_f` | Capacity Installed |
| `sys_CapacityUsed_f` | Capacity Used |
| `sys_CapacityUsedPct_f` | Capacity Used Percent |
| `sys_Cost_f` | Cost |
| `sys_CostCenter_s` | Cost Center |
| `sys_CpuUtilPct_f` | CPU Utilization |
| `sys_CustomerPrice_f` | Customer Price |
| `sys_CustomerRate_f` | Customer Rate |
| `sys_CustomerWorkspaceId_s` | Customer Workspace ID |
| `sys_CustomerWorkspaceName_s` | Customer Workspace Name |
| `sys_DatasourceId_s` | Data Source ID |
| `sys_DatasourceName_s` | Data Source Name |
| `sys_EndTime_t` | Usage End |
| `sys_Instance_s` | Resource ID |
| `sys_InstanceDesc_s` | Resource Description |
| `sys_InstanceName_s` | Resource Name |
| `sys_InstanceType_s` | Resource Type |
| `sys_MeterId_s` | Meter ID |
| `sys_MeterName_s` | Meter Name |
| `sys_NetworkInMB_f` | Network In MB |
| `sys_NetworkOutMB_f` | Network Out MB |
| `sys_Product_s` | Product |
| `sys_Provider_s` | Provider |
| `sys_ProviderRegion_s` | Provider Region |
| `sys_ProviderType_s` | Provider Type |
| `sys_ProviderZone_s` | Provider Zone |
| `sys_Quantity_f` | Quantity |
| `sys_Rate_f` | Rate |
| `sys_ReadThroughput_i` | Read Throughput |
| `sys_RecordType_s` | Charge Type |
| `sys_ServiceCategory_s` | Service Category |
| `sys_Source_s` | Source |
| `sys_StartTime_t` | Usage Start |
| `sys_StorageReadBytes_i` | Storage Read Bytes |
| `sys_StorageWriteBytes_i` | Storage Write Bytes |
| `sys_Unit_s` | Units |
| `sys_VMCpuCount_i` | VM CPU Count |
| `sys_VMDiskSizeGB_f` | VM Disk GB |
| `sys_VMDiskType_s` | VM Disk Type |
| `sys_VMFamily_s` | VM Family |
| `sys_VMGPUCount_i` | VM GPU Count |
| `sys_VMMaxNumDisk_i` | VM Max Num Disk |
| `sys_VMMemoryGB_f` | VM Memory GB |
| `sys_VMOperatingSys_s` | Operating System |
| `sys_VMProviderSeries_s` | VM Provider Series |
| `sys_VMProviderType_s` | VM Provider Type |
| `sys_VMSize_s` | VM Size |
| `sys_WriteThroughput_i` | Write Throughput |


## Provider fields

Provider fields are **only available to tenants that have the corresponding data source configured**. They expose raw or supplemental attributes that are specific to a given cloud or infrastructure provider.

### HPE GreenLake

The following fields are available when an HPE GreenLake data source is configured.

| Field Name | Display Name |
|  --- | --- |
| `ext_b979bd413895266ecb7c30d8c8bb2837_s` | Account Purpose |
| `ext_3916fd38e0e20499c6444c724c3063c6_s` | Alt Component Id |
| `ext_6f557d79be4e21acf602a1b89c81f0f3_s` | Alt Device Id |
| `ext_36dc3be646a97dd5c43e7e0e187e1d9d_s` | Alt Resource Id |
| `ext_c21b76f2f09e229d93d528b11272d21b_f` | Average CPU Utilization |
| `ext_181f0fe6d76283c79fe8866d38ad192c_f` | Average Node Utilization |
| `ext_ee069a13e944b30c6375a97871126e25_s` | Billing Method |
| `ext_5154525fdcdae19c415ac4c6d093144e_i` | Blade Number |
| `ext_249694a485fc5d3289c38986b4f8e887_s` | Cluster |
| `ext_d41634927066d67a2a3f88245907e6c3_s` | Cluster Id |
| `ext_3451b9b269585ddecbaad824bc8ef34f_i` | Cluster Host Count |
| `ext_0d2ea5e0f9ac0b509c26680c75da4037_f` | Cluster Installed Memory Size |
| `ext_861205b6b5f06415f4a5ac34e9bc55c1_i` | Cluster HDD Drive Count |
| `ext_3c0530178ef4a56b0a0b339f3a0e0c7b_i` | Cluster Physical Core Count |
| `ext_277228e100485c21c044ba621ad2ca5a_f` | Cluster SSD Capacity Installed |
| `ext_379e1bb4d288d8b132e8fbf539d63cf8_f` | Cluster SSD Capacity Used |
| `ext_2086aa883dc2924b47cdf9434ea2c2cb_i` | Cluster SSD Drive Count |
| `ext_5474287ea054474b4e5db306d82ce724_i` | Cluster Threaded Core Count |
| `ext_976901348d61fd802d0fdd1ef032acac_f` | Cluster Total Capacity Installed |
| `ext_e3c841f21bdbfdb556c8bbc7913d87e0_f` | Cluster Total Capacity Used |
| `ext_49c19e7a80ea236f0e663e91648387d1_i` | Cluster VM Count |
| `ext_c9891816e6d2678f04164808097d062f_f` | Committed Capacity |
| `ext_41dfb893fc037f7dc670771fac8a4233_f` | Committed Percent |
| `ext_a1f32de763bec68377fc8edfff0a8ae6_f` | Compressed Capacity Used |
| `ext_59716c97497eb9694541f7c3d37b1a4d_s` | Country |
| `ext_34cd9f818fc61eb071908881fd69c504_f` | CPU Count |
| `ext_ddcea6f58b858fed36a06b67b1b8239f_f` | CPU Core Count |
| `ext_ce26601dac0dea138b7295f02b7620a7_s` | Customer |
| `ext_47df2b78ac4b3edfbf1c6d0b2a64c579_s` | Data Center |
| `ext_b5a7adde1af5c87d7fd797b6245c2a39_s` | Description |
| `ext_e0ac20adce6ffee48c7151b070aa5737_s` | Device |
| `ext_0f5a10b3c642b95943d2c1373954b9bc_s` | Device Description |
| `ext_2e8f11ede1199f48c85453ec3cd462ec_s` | Device ID |
| `ext_0b4451950df7636e1b7d7effd5cd2826_s` | Device Serial Number |
| `ext_7d378b56cf6185a4635cc003e0d8af9f_f` | Disk Used |
| `ext_7274a3d3c6c96eee7386b108d02f555f_s` | Distributor |
| `ext_a80425472d94ae02c836da5b6f205b7b_s` | Feed |
| `ext_e28e06539239a6f156cd0799a6f2b206_s` | FolderName |
| `ext_1c07f24dbaeb847f4662960d2691d528_s` | Host Name |
| `ext_c60f17085dd008238072cb1a936f5937_s` | Host ID |
| `ext_ebc75e6fab6465cd2fd94b07bde4c6c9_f` | Host CPU Load Percent |
| `ext_8cd2317ccd13af09192b0ab830641a68_s` | Host Serial Number |
| `ext_1b21b0d71706897b69f108572c444d40_s` | Hypervisor |
| `ext_d0e72cad9dc2ac02a7901fd942954af1_s` | Component ID |
| `ext_71a55699c54704bfb82a98824267d180_s` | Component Name |
| `ext_d5281604a8e8310bf0680003e6da5e6b_s` | Component Description |
| `ext_168919211ebc109c81da0e27f1e53f59_s` | Location ID |
| `ext_ce5bf551379459c1c61d2a204061c455_s` | Location |
| `ext_6f384d4d6c4bfcc1af4e3f82caad347e_s` | Location Tier ID |
| `ext_4b8f79d60273b30ccea58eeb63c22eae_i` | Managed Node Count |
| `ext_c0bd7654d5b278e65f21cf4e9153fdb4_s` | Manufacturer |
| `ext_a341651258858327421549c8fefcbb39_s` | Marketing Capacity |
| `ext_bd4895cad12b3c652f1f22b118aefe32_f` | Maximum CPU Utilization |
| `ext_b5ab5bfcf2a45bc299a7d50387a9184c_f` | Memory Available |
| `ext_fa4665ac784c14b8a22483b7f6707e27_f` | Memory Size |
| `ext_2397947828b3f7532b5eb42f6daf5aaa_f` | Memory Utilization |
| `ext_ea75344ee44e0de52cbc1f3966df54bb_s` | Meter Type |
| `ext_f3d9aa32afb1a7e979d4f5bdedc6e337_f` | Min. Contractual Capacity |
| `ext_d663e067985e25ddfd55ffaaf7d74d28_f` | Minimum CPU Utilization |
| `ext_ed6758e5ad024d9edb70ef0d2dbb767a_s` | Native ID |
| `ext_bd4bd898f822d201ec120ce4b46c99bd_s` | Native VM ID |
| `ext_47fc9e1cfa6a2d29102a83ab4a8fa0d7_i` | Number vCPUs |
| `ext_419f3742e6de8e0ec4b22cce005e7630_s` | Platform |
| `ext_1b1d31e5faa40d143f18d99d87fa90ea_s` | Pool Type |
| `ext_7e240928383acb93e5066a6149430337_s` | Pool Name |
| `ext_5546628f1e282c80b58b8d36d7e88390_f` | PoolCapacityGiB |
| `ext_1d250b58bea5fa2e20a271061175f658_s` | Port Description |
| `ext_bc3c828cce582fafd1e35e77b8c84327_s` | Port Name |
| `ext_b81dbdcd51802845e275c5bd54d84e17_s` | Port Number |
| `ext_90d80b71e6e4515405d0541b58077671_s` | Port Speed |
| `ext_decf73c0061e0987dab6565eeaa64c4d_s` | RAID Parity |
| `ext_1f19599b2aff8b35d5365bf20380aa27_f` | Raid config |
| `ext_dabf0c1b73fe35f7bff46756087df0cb_s` | RAID Type |
| `ext_f447ac856e7e72435904956e3b15f433_s` | Region |
| `ext_00f25dcdeb460788d45b488585efcd8e_s` | Reseller |
| `ext_5a1f1f813792b0833e6cd0774c3610d9_f` | Requested Capacity |
| `ext_65e432361b11226b0cbc52adfaa187ad_s` | Resource Description |
| `ext_dd23acac46f17cbfd4d5541f8ee3c7a1_s` | Resource Group |
| `ext_fe2284eb32d4b09d29fd34217324b19a_s` | RPM |
| `ext_c2ba7e785c49050f48da9aacc45c2b85_s` | Service |
| `ext_691acfa686b1dd04edfbca19bb7f8a53_s` | Service Instance ID |
| `ext_ee28d1f42a1f4fa7cc7737ed3a1ab2f3_i` | Server Core Count |
| `ext_f5c5069c483b3152d0bd4bbe3378b008_i` | Server Socket Count |
| `ext_ec53a8c4f07baed5d8825072c89799be_s` | Status |
| `ext_3f66ff9522ede52d62ea481c9e4990ed_f` | Storage Capacity |
| `ext_3121ef8feef888da78503d48030f3255_s` | Sub Region |
| `ext_9bf79c7f10eadd0b612b8c354ad19bdc_s` | Subscription ID |
| `ext_e0588ef1b83dbe7de7b24ea582790444_s` | System ID |
| `ext_9483f17a69bd0b52dbc44f9106718634_s` | Tier |
| `ext_4d72768ef78424678be8087518e4d41d_s` | Tier ID |
| `ext_ed472ddbb730b7246dbd337f1e0f6918_s` | Tier License Type |
| `ext_3d77b4ef35401af4df832bfbe4765075_s` | Tier Number |
| `ext_93cc0d0255368f933fa4a38336539d87_f` | Total Disk |
| `ext_5b0a06194fb387485b6954b5ac8a8a2b_f` | Uncompressed Capacity Used |
| `ext_a7d6e22f4e42b9f526689d7c05ed15ce_f` | Utilization |
| `ext_ec9ceefe0c19f4c029008c23e3c947b7_s` | Vendor |
| `ext_4607897d6aab5e0e7cff62ecf293c008_s` | Virtual Switch ID |
| `ext_b0c34632375baf4263a8ba6d52c0b9f0_s` | VM Manager ID |
| `ext_608c29642d6cca11c83c53f0ab2dffc0_s` | VM Manager Name |
| `ext_2a7ba2b34478aaba7c37b0e044e13541_f` | VM Storage Capacity Installed |
| `ext_7935000005af9bbe0165af32705efaaa_f` | VM Storage Capacity Used |
| `ext_191fac23c2b2ea4e948178972521292f_f` | Volume Size |
| `ext_7bf6134278ec791feda0ca0853f117cc_f` | Volume Used |
| `ext_c25b6c6162efb8a9d5166946cae0db0b_f` | Volume Free |
| `ext_a984e0c125346b682594641182382377_f` | Volume Failed |
| `ext_de4b8596c6fb778ca3a3ad7fb4900c8c_f` | Volume Spare |
| `ext_38d13845d1ae18ca7ca807c084ea1a41_f` | VolumeLogicalUsageGiB |
| `ext_5a104c82a1831b194d1d11959c8882f4_f` | VolumeCompressDedupeGiB |
| `ext_45a2cf87b0cb54370c27bde165b1c365_f` | VolumeProvisionedSizeGiB |
| `ext_22bb75b17c257e3403e89aa51a170ac3_s` | WWN |
| `ext_c97c03b735279732a9c3ac4e46bf0086_f` | XP Compressed Volume Used |


### AWS

The following fields are available when an AWS data source is configured.

| Field Name | Display Name |
|  --- | --- |
| `ext_8e70b34654110e2de9be88520c7a80a4_f` | Blended Rate |
| `ext_f8793d4e87c679a72727b68524f92771_f` | Blended Cost |
| `ext_67617c3dd7048bff7de2a5db0e9bb12c_s` | Report type |
| `ext_36ef84e1435a34646184355bc79065c2_s` | Reserved Instance |