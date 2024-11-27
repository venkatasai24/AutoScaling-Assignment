import libvirt
import time
import xml.etree.ElementTree as ET

conn = libvirt.open('qemu:///system')

# List all domains
for domain_id in conn.listDomainsID():
    dom = conn.lookupByID(domain_id)
    print(f"Domain name: {dom.name()}")
