availabilityDomains = ["PnAA:AP-HYDERABAD-1-AD-1"]
displayName = 'MayasFreePC'
compartmentId = 'ocid1.tenancy.oc1..aaaaaaaazvk526dpm6fr277l7beuihasm2dfanqfl5fuy6rgo7lrq7sznzca'
imageId = "ocid1.image.oc1.ap-hyderabad-1.aaaaaaaa7mcpvsclmefvj4ccejxnv3wlf4ktdlxwoale7qkwakacjxtpwv7q"
subnetId = 'ocid1.subnet.oc1.ap-hyderabad-1.aaaaaaaadpaotnwu23jxfkcvgkjb5no6enroibpdqmrx5gwct2ziwywlrloa'
ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDYhaWYnyX4IEbmMyN5JGxgcwbqnl6E95FlkfND9SoTPaguKS2NwqtNCiu/EshWW6L4NhUQ1gyoZG76Bhqi6FF4zh2vXdoXJQ67uuFYK7cA14plEUQF0LLaeAh9iFZmj7x4SQYoC6gZXAOwnyWt2Q5ztblEyJ8ukyxufVm4rxkypmrYQUpl0WMvG4cu3yEEGv1thrYlxElBKLWn7m5Rvi3wvpncWpSmemgx6lu79R9IOo6rSSrtuX9BHDEjsN3BcUWzNUrHh+AfubS/ESlzjGBGTAA7nw/joRlcg00stkTRYmX42JCS4gog0rXPstqOd/aKYLmKT/QGybexPCm1QZ7IwzRYEQ/dU4HpckBENYkezHdf0UbDTPIbc039WJfeXVmSf9h/EQX+a2ROB4fNKq3xPilfxXivsGRsqJ5uDuoDo1BB8VPGg+PvpJsHqH1+89Rx17lKK3GMrtKcy5mgNg65ZPScNSaLoj1d66+JoIgVCZKizPif9TZe5OSP0CgJf+s= mayank@mayaspc"

ocpus = 4
memory_in_gbs = 24
wait_s_for_retry = 20

import oci
import logging
import time
import sys
import requests

LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("oci.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.A1.Flex instance")


message = f'Start spawning instance VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)


message = f"Instance to create: VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)

logging.info("Check current instances in account")
logging.info(
    "Note: Free upto 4xVM.Standard.A1.Flex instance, total of 4 ocpus and 24 GB of memory")
current_instance = to_launch_instance.list_instances(
    compartment_id=compartmentId)
response = current_instance.data

total_ocpus = total_memory = _A1_Flex = 0
instance_names = []
if response:
    logging.info(f"{len(response)} instance(s) found!")
    for instance in response:
        logging.info(f"{instance.display_name} - {instance.shape} - {int(instance.shape_config.ocpus)} ocpu(s) - {instance.shape_config.memory_in_gbs} GB(s) | State: {instance.lifecycle_state}")
        instance_names.append(instance.display_name)
        if instance.shape == "VM.Standard.A1.Flex" and instance.lifecycle_state not in ("TERMINATING", "TERMINATED"):
            _A1_Flex += 1
            total_ocpus += int(instance.shape_config.ocpus)
            total_memory += int(instance.shape_config.memory_in_gbs)

    message = f"Current: {_A1_Flex} active VM.Standard.A1.Flex instance(s) (including RUNNING OR STOPPED)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")


message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {4-total_ocpus} ocpus - Free memory: {24-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 4 or total_memory + memory_in_gbs > 24:
    message = "Total maximum resource exceed free tier limit (Over 4 ocpus/24GB total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if displayName in instance_names:
    message = f"Duplicate display name: >>>{displayName}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

message = f"Precheck pass! Create new instance VM.Standard.A1.Flex: {ocpus} opus - {memory_in_gbs} GB"
logging.info(message)

while True:
    for availabilityDomain in availabilityDomains:
        instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_authorized_keys
    },
    availability_domain=availabilityDomain,
    shape='VM.Standard.A1.Flex',
    compartment_id=compartmentId,
    display_name=displayName,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image", image_id=imageId,boot_volume_size_in_gbs=150),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False, subnet_id=subnetId, assign_private_dns_record=True),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[oci.core.models.InstanceAgentPluginConfigDetails(
            name='Vulnerability Scanning', desired_state='DISABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=False),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs)
)
        try:
        	to_launch_instance.launch_instance(instance_detail)
        	message = 'VPS is created successfully! Watch video to get public ip address for your VPS'
        	logging.info(message)
        	sys.exit()
        except oci.exceptions.ServiceError as e:
            if e.status == 500:
            	message = f"{e.message} Retry in {wait_s_for_retry}s"
            else:
            	message = f"{e} Retry in {wait_s_for_retry}s"
            logging.info(message)
            time.sleep(wait_s_for_retry)
        except Exception as e:
        	message = f"{e} Retry in {wait_s_for_retry}s"
        	logging.info(message)
        	time.sleep(wait_s_for_retry)
        except KeyboardInterrupt:
        	sys.exit()
