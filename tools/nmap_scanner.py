import subprocess
import json
import re
from rich.console import Console
from config.config_manager import ConfigManager

console = Console()

class NmapScanner:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.nmap_path = self.config_manager.get_tool_path("nmap_path")

    def scan_target(self, target, scan_type="basic", options=None):
        """
        Perform NMAP scan on target
        scan_type: basic, full, vuln, udp, stealth
        """
        try:
            cmd = [self.nmap_path]

            # Basic scan options
            if scan_type == "basic":
                cmd.extend(["-sV", "-O", "--version-light", target])
            elif scan_type == "full":
                cmd.extend(["-sS", "-sV", "-O", "-A", "--version-all", target])
            elif scan_type == "vuln":
                cmd.extend(["-sV", "--script=vuln", target])
            elif scan_type == "udp":
                cmd.extend(["-sU", "-sV", target])
            elif scan_type == "stealth":
                cmd.extend(["-sS", "-T2", "-f", "--data-length", "16", target])
            else:
                cmd.extend(["-sV", target])

            # Add custom options
            if options:
                if isinstance(options, str):
                    cmd.extend(options.split())
                elif isinstance(options, list):
                    cmd.extend(options)

            console.print(f"[cyan]Running NMAP scan: {' '.join(cmd)}[/cyan]")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": result.stderr,
                    "command": ' '.join(cmd),
                    "scan_type": scan_type,
                    "target": target
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "command": ' '.join(cmd),
                    "scan_type": scan_type,
                    "target": target
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Scan timed out after 5 minutes",
                "command": ' '.join(cmd) if 'cmd' in locals() else "timeout",
                "scan_type": scan_type,
                "target": target
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"NMAP not found at {self.nmap_path}. Please install NMAP or update the path in config.",
                "command": self.nmap_path,
                "scan_type": scan_type,
                "target": target
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(cmd) if 'cmd' in locals() else "unknown",
                "scan_type": scan_type,
                "target": target
            }

    def parse_scan_results(self, scan_output):
        """Parse NMAP scan results into structured data"""
        results = {
            "hosts": [],
            "services": [],
            "os_matches": [],
            "vulnerabilities": []
        }

        # Extract host information
        host_pattern = r"Nmap scan report for ([^\n]+)"
        hosts = re.findall(host_pattern, scan_output)
        results["hosts"] = hosts

        # Extract port/service information
        port_pattern = r"(\d+)/(\w+)\s+(\w+)\s+([^/]+)(?:/([^/\n]+))?(?:/([^/\n]+))?(?:/([^/\n]+))?"
        ports = re.findall(port_pattern, scan_output)

        for port_info in ports:
            port, state, service, version = port_info[0], port_info[2], port_info[3], port_info[4] if len(port_info) > 4 else ""
            results["services"].append({
                "port": port,
                "state": state,
                "service": service,
                "version": version
            })

        # Extract OS information
        os_pattern = r"OS details: ([^\n]+)"
        os_matches = re.findall(os_pattern, scan_output)
        results["os_matches"] = os_matches

        # Extract vulnerability information (if vuln scan)
        vuln_pattern = r"\| ([^\n]+)\n\|_*\n((?:\|[^\n]+\n)+)"
        vuln_matches = re.findall(vuln_pattern, scan_output, re.MULTILINE)
        for vuln in vuln_matches:
            results["vulnerabilities"].append({
                "title": vuln[0].strip(),
                "details": vuln[1].strip()
            })

        return results

    def quick_port_scan(self, target, ports="1-1000"):
        """Quick port scan on specified port range"""
        return self.scan_target(target, options=[f"-p{ports}"])

    def service_version_scan(self, target):
        """Detailed service version scan"""
        return self.scan_target(target, options=["-sV", "--version-all"])

    def vulnerability_scan(self, target):
        """Scan for known vulnerabilities"""
        return self.scan_target(target, options=["--script=vuln"])

    def udp_scan(self, target):
        """UDP port scan"""
        return self.scan_target(target, options=["-sU"])

    def aggressive_scan(self, target):
        """Aggressive scan with OS detection and traceroute"""
        return self.scan_target(target, options=["-A"])
