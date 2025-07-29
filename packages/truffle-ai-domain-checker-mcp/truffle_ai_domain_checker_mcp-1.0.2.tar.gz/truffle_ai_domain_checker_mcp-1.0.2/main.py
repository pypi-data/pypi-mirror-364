#!/usr/bin/env python3
"""
MCP Server for checking domain name availability using FastMCP 2.0
Adapted for Truffle AI MCP servers collection
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List
import dns.resolver
import aiohttp
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("truffle-domain-checker")

# Create the FastMCP server
mcp = FastMCP(
    name="Truffle Domain Checker",
    instructions="When you are asked about domain availability or to check if a domain is available for registration, call the appropriate function. This tool is perfect for product name research and brand name validation."
)

class DomainChecker:
    """Domain availability checker using RDAP and DNS resolution"""
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 10
        self.session = None
    
    async def check_domain_availability(self, domain: str) -> Dict[str, Any]:
        """Check if a domain is available using RDAP and DNS resolution"""
        results = {
            "domain": domain,
            "available": None,
            "rdap_registered": None,
            "dns_resolvable": None,
            "error": None,
            "details": {},
            "cloudflare_link": f"https://domains.cloudflare.com/?domain={domain}"
        }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            
            # Method 1: RDAP lookup (modern replacement for WHOIS)
            rdap_result = await self._check_rdap(domain)
            results["rdap_registered"] = rdap_result["registered"]
            results["details"]["rdap"] = rdap_result
            
            # Method 2: DNS resolution check
            dns_result = await self._check_dns_resolution(domain)
            results["dns_resolvable"] = dns_result["resolvable"]
            results["details"]["dns"] = dns_result
            
            # Improved availability logic - no more "None/Unclear"
            if results["rdap_registered"] is True:
                # Definitely registered
                results["available"] = False
            elif results["rdap_registered"] is False:
                # RDAP says not registered
                results["available"] = True
            elif results["dns_resolvable"] is False:
                # RDAP unclear but domain doesn't resolve - likely available
                results["available"] = True
            elif results["dns_resolvable"] is True:
                # RDAP unclear but domain resolves - likely taken
                results["available"] = False
            else:
                # Both RDAP and DNS failed - assume available (conservative)
                results["available"] = True
                
        except Exception as e:
            results["error"] = str(e)
            results["available"] = True  # Default to available on error
            logger.error(f"Error checking domain {domain}: {e}")
        
        return results
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _check_rdap(self, domain: str) -> Dict[str, Any]:
        """Check domain registration using RDAP (Registration Data Access Protocol)"""
        try:
            # Extract TLD to find appropriate RDAP server
            tld = domain.split('.')[-1].lower()
            
            # Use bootstrap service to find RDAP server for this TLD
            rdap_url = f"https://rdap.org/domain/{domain}"
            
            async with self.session.get(rdap_url, headers={
                'Accept': 'application/rdap+json',
                'User-Agent': 'Truffle-Domain-Checker/1.0'
            }) as response:
                if response.status == 404:
                    return {"registered": False, "reason": "Domain not found in RDAP"}
                elif response.status == 200:
                    data = await response.json()
                    
                    # Extract registration information
                    status = data.get('status', [])
                    events = data.get('events', [])
                    entities = data.get('entities', [])
                    
                    # Look for active registration indicators
                    is_registered = bool(
                        status or  # Has status entries
                        entities or  # Has registrant/registrar entities
                        any(event.get('eventAction') == 'registration' for event in events)
                    )
                    
                    result = {
                        "registered": is_registered, 
                        "reason": "Domain found in RDAP registry" if is_registered else "Domain available in RDAP",
                        "status": status,
                        "events": events[:2],  # Limit to first 2 events
                        "rdap_server": rdap_url
                    }
                    
                    # Add registration date if available
                    for event in events:
                        if event.get('eventAction') == 'registration':
                            result["registration_date"] = event.get('eventDate')
                            break
                    
                    return result
                else:
                    return {"registered": None, "reason": f"RDAP server error: {response.status}"}
                    
        except asyncio.TimeoutError:
            return {"registered": None, "reason": "RDAP lookup timeout"}
        except Exception as e:
            return {"registered": None, "reason": f"RDAP lookup failed: {str(e)}"}
    
    async def _check_dns_resolution(self, domain: str) -> Dict[str, Any]:
        """Check if domain resolves via DNS"""
        try:
            loop = asyncio.get_event_loop()
            
            def resolve_dns():
                try:
                    answers = self.dns_resolver.resolve(domain, 'A')
                    return [str(answer) for answer in answers]
                except dns.resolver.NXDOMAIN:
                    return None
                except Exception as e:
                    raise e
            
            a_records = await loop.run_in_executor(None, resolve_dns)
            
            if a_records:
                return {
                    "resolvable": True,
                    "a_records": a_records,
                    "reason": "Domain resolves to IP addresses"
                }
            else:
                return {
                    "resolvable": False,
                    "reason": "Domain does not resolve (NXDOMAIN)"
                }
                
        except Exception as e:
            return {
                "resolvable": None,
                "reason": f"DNS lookup failed: {str(e)}"
            }

# Initialize domain checker
domain_checker = DomainChecker()

@mcp.tool()
async def check_domain(domain: str) -> str:
    """Check if a single domain name is available for registration. Perfect for product name research and brand validation."""
    result = await domain_checker.check_domain_availability(domain)
    
    # Format the response with definitive status
    if result["available"] is True:
        status = "✅ AVAILABLE"
        action = f"🛒 Purchase: {result['cloudflare_link']}"
    else:
        status = "❌ NOT AVAILABLE"
        action = f"🔍 Search alternatives: {result['cloudflare_link']}"
    
    # Extract key registration info
    rdap_info = result['details'].get('rdap', {})
    dns_info = result['details'].get('dns', {})
    
    response = f"""Domain: {domain}
Status: {status}
{action}

📋 RDAP Check: {'Registered' if result['rdap_registered'] else 'Not registered' if result['rdap_registered'] is False else 'Unavailable'}
🌐 DNS Resolution: {'Resolving' if result['dns_resolvable'] else 'Not resolving' if result['dns_resolvable'] is False else 'Error'}
"""

    # Add registration details if available
    if rdap_info.get('registration_date'):
        response += f"📅 Registered: {rdap_info['registration_date'][:10]}\n"
    
    if result["error"]:
        response += f"\n⚠️  Note: {result['error']}"
    
    response += f"\n\nDetailed results:\n{json.dumps(result['details'], indent=2)}"
    
    return response

@mcp.tool()
async def check_multiple_domains(domains: List[str]) -> str:
    """Check availability for multiple domain names at once. Excellent for comparing different product name options."""
    if not domains:
        return "Error: Domain list is required"
    
    # Check domains concurrently
    tasks = [domain_checker.check_domain_availability(domain) for domain in domains]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions in the results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "domain": domains[i],
                "available": None,
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    # Format results as a table
    response = "Domain Availability Check Results:\n\n"
    for result in processed_results:
        if result["available"] is True:
            status = "✅ AVAILABLE"
        else:
            status = "❌ NOT AVAILABLE"
        
        response += f"{result['domain']:<30} {status}\n"
    
    response += f"\nDetailed results:\n{json.dumps(processed_results, indent=2)}"
    
    return response

@mcp.tool()
async def check_domain_variations(base_name: str, extensions: List[str] = None) -> str:
    """Check availability for a base name with multiple TLD extensions. Great for comprehensive product name research."""
    if extensions is None:
        extensions = ['.com', '.net', '.org', '.io', '.app', '.dev', '.tech']
    
    domains = [f"{base_name}{ext}" for ext in extensions]
    
    # Check domains concurrently using the same logic as check_multiple_domains
    if not domains:
        return "Error: Domain list is required"
    
    tasks = [domain_checker.check_domain_availability(domain) for domain in domains]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions in the results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "domain": domains[i],
                "available": None,
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    # Format results as a table
    response = "Domain Availability Check Results:\n\n"
    for result in processed_results:
        if result["available"] is True:
            status = "✅ AVAILABLE"
        else:
            status = "❌ NOT AVAILABLE"
        
        response += f"{result['domain']:<30} {status}\n"
    
    response += f"\nDetailed results:\n{json.dumps(processed_results, indent=2)}"
    
    return response

@mcp.resource("domain://check/{domain}")
async def domain_info_resource(domain: str) -> str:
    """Get domain availability information as a resource"""
    result = await domain_checker.check_domain_availability(domain)
    return json.dumps(result, indent=2)

def main():
    """Main entry point for uvx execution"""
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Support both stdio and http transports
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()