import urllib.request
import json

class CVEService:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def search_cve(self, cve_id):
        try:
            # Format CVE ID (e.g., CVE-2021-44228)
            if not cve_id.upper().startswith('CVE-'):
                cve_id = f"CVE-{cve_id}"
            
            url = f"{self.base_url}?cveId={cve_id}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'LAID-CVE-Search/1.0')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            if data.get('vulnerabilities'):
                vuln = data['vulnerabilities'][0]['cve']
                desc = vuln.get('descriptions', [{}])[0].get('value', 'No description')
                
                # Get CVSS score if available
                cvss = "N/A"
                metrics = vuln.get('metrics', {})
                if 'cvssMetricV31' in metrics:
                    cvss = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                elif 'cvssMetricV30' in metrics:
                    cvss = metrics['cvssMetricV30'][0]['cvssData']['baseScore']
                
                # Get references
                refs = [ref['url'] for ref in vuln.get('references', [])[:3]]
                
                return {
                    "cve_id": vuln.get('id', ''),
                    "summary": desc,
                    "cvss": cvss,
                    "references": refs,
                    "published": vuln.get('published', ''),
                    "modified": vuln.get('lastModified', '')
                }
            else:
                return {"error": "CVE not found"}
        except Exception as e:
            return {"error": f"CVE search failed: {str(e)}"}
    
    def search_cve_by_keyword(self, keyword):
        try:
            url = f"{self.base_url}?keywordSearch={keyword}&resultsPerPage=5"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'LAID-CVE-Search/1.0')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            results = []
            for vuln_data in data.get('vulnerabilities', []):
                vuln = vuln_data['cve']
                desc = vuln.get('descriptions', [{}])[0].get('value', 'No description')[:200] + '...'
                
                cvss = "N/A"
                metrics = vuln.get('metrics', {})
                if 'cvssMetricV31' in metrics:
                    cvss = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                elif 'cvssMetricV30' in metrics:
                    cvss = metrics['cvssMetricV30'][0]['cvssData']['baseScore']
                
                results.append({
                    "cve_id": vuln.get('id', ''),
                    "summary": desc,
                    "cvss": cvss,
                    "published": vuln.get('published', '')
                })
            
            return {"results": results, "keyword": keyword}
        except Exception as e:
            return {"error": f"CVE keyword search failed: {str(e)}"}