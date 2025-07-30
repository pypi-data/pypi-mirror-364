from abc import ABC, abstractmethod
from ipaddress import ip_address
import json
import logging
import re
import time
from typing import Dict, List, Optional

from unitas import HostScanData
from unitas.model import PortDetails
from unitas.utils import get_version


class Convert(ABC):
    def __init__(self, global_state: Dict[str, HostScanData] = None):
        self.global_state = Convert.sort_global_state_by_ip(global_state or {})

    @abstractmethod
    def convert(self) -> str:
        pass

    @abstractmethod
    def parse(self, content: str) -> Dict[str, HostScanData]:
        pass

    @staticmethod
    def sort_global_state_by_ip(
        global_state: Dict[str, HostScanData],
    ) -> Dict[str, HostScanData]:
        sorted_ips = sorted(global_state.keys(), key=ip_address)
        return {ip: global_state[ip] for ip in sorted_ips}


class GrepConverter(Convert):
    def convert_with_up(self, hostup_dict: dict) -> str:
        output = []
        for ip, reason in hostup_dict.items():
            output.append(f"{ip}|host-up({reason})")
        return "\n".join(output) + "\n" + self.convert()

    def convert(self):
        output = []
        for host in self.global_state.values():
            services = ""
            for port in host.get_sorted_ports():
                services += f"{port.port}/{port.protocol}({port.service}) "
            output.append(f"{host.ip}|{services}")
        return "\n".join(output) + "\n"

    def parse(self, content: str) -> Dict[str, HostScanData]:
        raise ValueError("not implemented")


class MarkdownConvert(Convert):
    def __init__(
        self, global_state: Dict[str, HostScanData] = None, show_origin: bool = False
    ):
        super().__init__(global_state)
        self.show_origin = show_origin

    def convert(self, formatted: bool = False) -> str:
        if self.show_origin:
            output = ["|IP|Hostname|Port|Status|Comment|Source|"]
            output.append("|--|--|--|--|---|---|")
        else:
            output = ["|IP|Hostname|Port|Status|Comment|"]
            output.append("|--|--|--|--|---|")

        max_ip_len = max_hostname_len = max_port_len = max_status_len = (
            max_comment_len
        ) = max_source_len = 0

        if formatted:
            # Find the maximum length of each column
            for host in self.global_state.values():
                max_ip_len = max(max_ip_len, len(host.ip))
                max_hostname_len = max(max_hostname_len, len(host.hostname))
                for port in host.get_sorted_ports():
                    port_info = f"{port.port}/{port.protocol}({port.service})"
                    max_port_len = max(max_port_len, len(port_info))
                    max_status_len = max(max_status_len, len(port.state))
                    max_comment_len = max(max_comment_len, len(port.comment))
                    if self.show_origin:
                        source_info = self._format_source_info(port)
                        max_source_len = max(max_source_len, len(source_info))

        for host in self.global_state.values():
            for port in host.get_sorted_ports():
                service = f"{port.port}/{port.protocol}({port.service})"
                if self.show_origin:
                    source_info = self._format_source_info(port)
                    output.append(
                        f"|{host.ip.ljust(max_ip_len)}|{host.hostname.ljust(max_hostname_len)}|{service.ljust(max_port_len)}|{port.state.ljust(max_status_len)}|{port.comment.ljust(max_comment_len)}|{source_info.ljust(max_source_len)}|"
                    )
                else:
                    output.append(
                        f"|{host.ip.ljust(max_ip_len)}|{host.hostname.ljust(max_hostname_len)}|{service.ljust(max_port_len)}|{port.state.ljust(max_status_len)}|{port.comment.ljust(max_comment_len)}|"
                    )
        return "\n".join(output) + "\n"

    def _format_source_info(self, port: PortDetails) -> str:
        """Format source information for display in markdown, handling multiple sources"""
        if not hasattr(port, "sources") or not port.sources:
            return ""

        # For multiple sources, format them as a comma-separated list
        source_strings = []
        for source in port.sources:
            parts = []
            if source["type"]:
                parts.append(source["type"])
            if source["file"]:
                parts.append(source["file"])

            if parts:
                source_strings.append(":".join(parts))

        return ",".join(source_strings)

    def parse(self, content: str) -> Dict[str, HostScanData]:
        lines = content.strip().split("\n")
        if len(lines) < 2:
            logging.error(
                f"Could not load markdown, markdown was only {len(lines)} lines. are you missing the two line header?"
            )
            return {}

        # Check if header contains a source column
        has_source_column = "|Source|" in lines[0] or "|source|" in lines[0]

        lines = lines[2:]  # Skip header and separator
        result = {}
        counter = 1

        for line in lines:
            counter += 1
            if has_source_column:
                match = re.match(
                    r"\s*\|([^|]+)\|\s*([^|]*)\s*\|\s*([^|/]+)/([^|(]+)\(([^)]+)\)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|",
                    line.strip(),
                )
                if match:
                    ip, hostname, port, protocol, service, status, comment, source = (
                        match.groups()
                    )

                    # Parse multiple source information from comma-separated format
                    sources = []
                    if source.strip():
                        for source_entry in source.split(","):
                            source_entry = source_entry.strip()
                            if not source_entry:
                                continue

                            source_parts = [s.strip() for s in source_entry.split("/")]
                            source_type = (
                                source_parts[0] if len(source_parts) > 0 else ""
                            )
                            source_file = (
                                source_parts[1] if len(source_parts) > 1 else ""
                            )
                            detected_date = (
                                source_parts[2] if len(source_parts) > 2 else ""
                            )

                            sources.append(
                                {
                                    "type": source_type,
                                    "file": source_file,
                                    "date": detected_date,
                                }
                            )

                    ip = ip.strip()
                    if ip not in result:
                        result[ip] = HostScanData(ip)
                        if hostname.strip():
                            result[ip].set_hostname(hostname.strip())

                    # Create port details first
                    port_details = PortDetails(
                        port.strip(),
                        protocol.strip(),
                        status.strip() or "TBD",
                        service.strip(),
                        comment.strip(),
                    )

                    # Add sources
                    for src in sources:
                        port_details.add_source(src["type"], src["file"], src["date"])

                    result[ip].add_port_details(port_details)
                else:
                    logging.error(
                        f"Markdown error: Failed to parse line nr {counter}: {line}"
                    )
            else:
                match = re.match(
                    r"\s*\|([^|]+)\|\s*([^|]*)\s*\|\s*([^|/]+)/([^|(]+)\(([^)]+)\)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|",
                    line.strip(),
                )
                if match:
                    ip, hostname, port, protocol, service, status, comment = (
                        match.groups()
                    )
                    ip = ip.strip()
                    if ip not in result:
                        result[ip] = HostScanData(ip)
                        if hostname.strip():
                            result[ip].set_hostname(hostname.strip())
                    result[ip].add_port(
                        port.strip(),
                        protocol.strip(),
                        status.strip() or "TBD",
                        service.strip(),
                        comment.strip(),
                    )
                else:
                    logging.error(
                        f"Markdown error: Failed to parse line nr {counter}: {line}"
                    )

        return result


class JsonConverter(Convert):
    """
    Export scan results as a structured JSON file that can be loaded
    by the standalone HTML viewer or used for other data analysis.
    """

    def __init__(
        self,
        global_state: Dict[str, HostScanData] = None,
        hostup_dict: Dict[str, str] = None,
        show_origin: bool = False,
    ):
        super().__init__(global_state)
        self.hostup_dict = hostup_dict or {}
        self.show_origin = show_origin

    def convert(self, formatted: bool = False) -> str:
        """Convert the scan data to a JSON string."""
        vendor_lookup = None
        try:
            from unitas.utils import mac_vendor_lookup

            vendor_lookup = mac_vendor_lookup
        except ImportError:
            pass

        # Prepare hosts data
        hosts_data = []
        for ip, host in self.global_state.items():
            # Get MAC vendor if available
            vendor = ""
            if vendor_lookup and host.mac_address:
                vendor = vendor_lookup.lookup(host.mac_address)

            host_entry = {
                "ip": ip,
                "hostname": host.hostname,
                "mac_address": host.mac_address or "",
                "vendor": vendor,
                "ports": [],
                "hasOpenPorts": len(host.ports) > 0,
            }

            # Include MAC sources if showing origin
            if self.show_origin and hasattr(host, "mac_sources") and host.mac_sources:
                host_entry["mac_sources"] = host.mac_sources

            for port in host.ports:
                port_entry = {
                    "port": port.port,
                    "protocol": port.protocol,
                    "service": port.service,
                    "state": port.state,
                    "comment": port.comment,
                    "uncertain": "?" in port.service,
                    "tls": "TLS" in port.comment,
                }

                # Include source information if requested
                if self.show_origin and hasattr(port, "sources") and port.sources:
                    port_entry["sources"] = port.sources

                host_entry["ports"].append(port_entry)
            hosts_data.append(host_entry)

        # Prepare hosts-up data
        hostup_data = []
        for ip, reason in self.hostup_dict.items():
            hostup_data.append({"ip": ip, "reason": reason})

        # Build complete data structure
        data = {
            "metadata": {
                "version": get_version(),
                "timestamp": time.time(),
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "totalHosts": len(hosts_data),
                    "totalPorts": sum(len(host["ports"]) for host in hosts_data),
                    "hostsUp": len(hostup_data),
                },
                "includesOrigin": self.show_origin,
                "includesMacAddresses": any(
                    host.get("mac_address") for host in hosts_data
                ),
                "includesVendorInfo": vendor_lookup is not None,
            },
            "hosts": hosts_data,
            "hostsUp": hostup_data,
        }

        if formatted:
            return json.dumps(data, indent=2)
        else:
            return json.dumps(data)

    def parse(self, content: str) -> Dict[str, HostScanData]:
        """Parse JSON content back into HostScanData objects"""
        try:
            data = json.loads(content)
            result = {}

            for host_entry in data.get("hosts", []):
                ip = host_entry.get("ip")
                if not ip or not HostScanData.is_valid_ip(ip):
                    logging.warning(f"Invalid IP in JSON data: {ip}")
                    continue

                host = HostScanData(ip)
                host.set_hostname(host_entry.get("hostname", ""))

                # Handle MAC address
                if host_entry.get("mac_address"):
                    host.set_mac_address(host_entry.get("mac_address"))

                # Handle MAC sources if present
                if host_entry.get("mac_sources") and hasattr(host, "mac_sources"):
                    host.mac_sources = host_entry.get("mac_sources")

                # Process ports
                for port_entry in host_entry.get("ports", []):
                    try:
                        # Create port details
                        port_details = PortDetails(
                            port_entry.get("port", ""),
                            port_entry.get("protocol", "tcp"),
                            port_entry.get("state", "TBD"),
                            port_entry.get("service", "unknown?"),
                            port_entry.get("comment", ""),
                        )

                        # Add sources if present and supported
                        if port_entry.get("sources") and hasattr(
                            port_details, "sources"
                        ):
                            port_details.sources = port_entry.get("sources")

                        host.add_port_details(port_details)
                    except ValueError as e:
                        logging.warning(f"Error adding port: {e}")

                result[ip] = host

            return result

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON data: {e}")
            return {}
        except Exception as e:
            logging.error(f"Error importing JSON data: {e}")
            return {}


class MacAddressReport(Convert):
    """Generates a report focusing on MAC addresses for network inventory."""

    def __init__(
        self,
        global_state: Dict[str, HostScanData] = None,
        show_origin: bool = False,
        include_up_hosts: bool = True,
        hostup_dict: Dict[str, str] = None,
    ):
        super().__init__(global_state)
        self.show_origin = show_origin
        self.include_up_hosts = include_up_hosts
        self.hostup_dict = hostup_dict or {}

    def convert(self) -> str:
        # Try to import vendor lookup functionality
        vendor_lookup = None
        try:
            from unitas.utils import mac_vendor_lookup

            vendor_lookup = mac_vendor_lookup
        except ImportError:
            pass

        # Markdown header parts
        header_parts = ["IP", "MAC Address", "Hostname", "Vendor", "Open Ports"]
        if self.show_origin:
            header_parts.append("Source")

        # Markdown header
        output = ["|" + "|".join(header_parts) + "|"]
        output.append("|" + "|".join(["--"] * len(header_parts)) + "|")

        # Markdown data
        for host in self.global_state.values():
            # Only include hosts with MAC addresses
            if not host.mac_address:
                continue

            # Get MAC vendor if available
            vendor = "-"
            if vendor_lookup:
                vendor = vendor_lookup.lookup(host.mac_address) or "-"

            # Format source info if available
            source_info = "-"
            if self.show_origin and hasattr(host, "mac_sources") and host.mac_sources:
                source_parts = []
                for source in host.mac_sources:
                    if source["type"] or source["file"]:
                        source_parts.append(f"{source['type']}:{source['file']}")
                if source_parts:
                    source_info = ", ".join(source_parts)

            # Count open ports
            port_count = len(host.ports)

            # Build row parts
            row_parts = [
                host.ip,
                host.mac_address,
                host.hostname or "-",
                vendor,
                str(port_count),
            ]

            if self.show_origin:
                row_parts.append(source_info)

            # Add the host data
            output.append("|" + "|".join(row_parts) + "|")

        return "\n".join(output) + "\n"

    def parse(self, content: str) -> Dict[str, HostScanData]:
        """
        Not implemented for this report type, as it's designed for output only.
        """
        raise NotImplementedError("Parsing MAC address reports is not supported")


def load_markdown_state(filename: str) -> Dict[str, HostScanData]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        # Strip empty lines
        content = "\n".join(line for line in content.split("\n") if line.strip())
        converter = MarkdownConvert()
        return converter.parse(content)
    except FileNotFoundError:
        logging.warning(f"File {filename} not found. Starting with empty state.")
        return {}
    except Exception as e:
        logging.error(f"Error loading {filename}: {str(e)}")
        return {}
