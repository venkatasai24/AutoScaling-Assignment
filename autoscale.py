import libvirt
import time
import uuid
import os
import shutil

# Threshold CPU usage percentage for autoscaling
CPU_THRESHOLD = 80.0
# Time to wait before next check (in seconds)
CHECK_INTERVAL = 1
# Directory where disk images are stored
DISK_IMAGE_DIR = "/var/lib/libvirt/images/"


def get_cpu_utilization(domain, interval=1):
    """Calculate the CPU utilization percentage for a libvirt domain."""
    try:
        # Get initial stats and time
        prev_stats = domain.getCPUStats(True)
        prev_time = time.time()

        # Wait for the interval
        time.sleep(interval)

        # Get updated stats and time
        current_stats = domain.getCPUStats(True)
        current_time = time.time()

        # Calculate CPU time difference across all vCPUs
        cpu_time_diff = sum(
            curr["cpu_time"] - prev["cpu_time"]
            for curr, prev in zip(current_stats, prev_stats)
        )

        elapsed_time = current_time - prev_time
        num_cpu = domain.maxVcpus()

        # Return 0 if elapsed time is invalid
        if elapsed_time <= 0:
            return 0.0

        # Normalize CPU time and calculate utilization
        utilization = (cpu_time_diff / (elapsed_time * num_cpu * 1e9)) * 100
        return utilization

    except libvirt.libvirtError as e:
        print(f"Error getting CPU utilization for domain {domain.name()}: {e}")
        return None


def generate_unique_server_name(existing_domains):
    """Generate a unique server name."""
    i = 1
    while True:
        name = f"server{i}"
        if name not in existing_domains:
            return name
        i += 1


def create_new_server(conn):
    """Create a new VM based on the configuration of Server1."""
    try:
        base_domain = conn.lookupByName("server1")
        xml_desc = base_domain.XMLDesc(0)
        existing_domains = [dom.name() for dom in conn.listAllDomains(0)]
        new_server_name = generate_unique_server_name(existing_domains)

        # Update the configuration XML with a new name and UUID
        new_uuid = str(uuid.uuid4())
        new_xml = xml_desc.replace(
            "<name>server1</name>", f"<name>{new_server_name}</name>"
        )
        new_xml = new_xml.replace(
            f"<uuid>{base_domain.UUIDString()}</uuid>", f"<uuid>{new_uuid}</uuid>"
        )

        # Prepare a new disk image
        new_disk_image = os.path.join(DISK_IMAGE_DIR, f"{new_server_name}.qcow2")
        base_disk_image = os.path.join(DISK_IMAGE_DIR, "server1.qcow2")

        if not os.path.exists(base_disk_image):
            print(f"[AUTOSCALER] Base disk image '{base_disk_image}' not found.")
            return

        shutil.copy(base_disk_image, new_disk_image)  # Copy the disk image
        new_xml = new_xml.replace(base_disk_image, new_disk_image)

        # Define and start the new VM
        new_domain = conn.defineXML(new_xml)
        print(f"[AUTOSCALER] Domain '{new_server_name}' defined.")

        new_domain.create()
        print(f"[AUTOSCALER] New server created and started: {new_server_name}")

    except libvirt.libvirtError as e:
        print(f"[AUTOSCALER] Error while creating new server: {e}")


def monitor_and_autoscale():
    """Monitor CPU usage and scale up if necessary."""
    conn = libvirt.open("qemu:///system")
    if conn is None:
        print("[MONITOR] Failed to connect to hypervisor.")
        return

    try:
        while True:
            high_usage = False
            for domain_name in ["server1", "server2"]:
                try:
                    domain = conn.lookupByName(domain_name)
                    cpu_usage = get_cpu_utilization(domain, interval=CHECK_INTERVAL)
                    print(f"[MONITOR] {domain_name} CPU usage: {cpu_usage:.2f}%")

                    if cpu_usage is not None and cpu_usage > CPU_THRESHOLD:
                        high_usage = True

                except libvirt.libvirtError:
                    print(f"[MONITOR] Unable to access {domain_name}")

            if high_usage:
                print("[AUTOSCALER] High CPU usage detected, creating a new server...")
                create_new_server(conn)
                break  # Exit after scaling for demonstration purposes

            time.sleep(CHECK_INTERVAL)
    finally:
        conn.close()


if __name__ == "__main__":
    monitor_and_autoscale()
