# proxyrequest/utils.py
import requests
from datetime import datetime, timezone
from typing import Optional, Dict
import time
import random
from urllib.parse import urlparse
import tldextract

def proxy_verifier(proxy: Optional[Dict[str, str]] = None, url: str = "http://httpbin.org/ip", timeout: int = 5, headers: Optional[Dict[str, str]] = None, verify: bool = True) -> bool:
    """
    Checks whether the given proxy is working by making a simple HTTP request to a test URL.
    If no proxy is provided, it fetches the public IP directly.

    Args:
        proxy (dict, optional): The proxy configuration (e.g., {"http": "http://proxy_ip:port", "https": "https://proxy_ip:port"}). Default is None.
        url (str): The URL to test the proxy against. Default is http://httpbin.org/ip.
        timeout (int): The timeout value for the request in seconds. Default is 5 seconds.
        headers (dict, optional): Custom headers to be sent with the request. Default is None, which sends a standard User-Agent.
        verify (bool, optional): Whether to verify SSL certificates. Default is True. Set to False if you want to skip SSL verification.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    # If no proxy is provided, default to an empty dictionary
    if proxy is None:
        proxy = {}

    # If no custom headers are provided, use a default User-Agent header
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    try:
        # If no proxy is given, get the public IP directly
        if not proxy:
            print(url)
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        else:
            # Sending a GET request to the test URL using the proxy, custom headers, timeout, and SSL verification
            response = requests.get(url, proxies=proxy, headers=headers, timeout=timeout, verify=verify)
        
        # If the status code is 200, the proxy is working or we got the IP
        if response.status_code == 200:
            if not proxy:
                # If no proxy, just print and return the public IP
                public_ip = response.json().get("origin", "Unknown")
                print(f"Public IP is used: {public_ip}")
                return True
            else:
                # If proxy was used, print success
                print(f"Proxy {proxy} is working!")
                return True
        else:
            print(f"Failed with status code {response.status_code}")
            return False    

    except requests.exceptions.ConnectTimeout:
        print(f"Error: timeout")
        return False

    except requests.exceptions.ConnectionError:
        print(f"Error: check net connections")
        return False

    except requests.exceptions.SSLError:
        print(f"Error: certificate verify failed (SSL)")
        return False

    except requests.exceptions.JSONDecodeError:
        print(f"Error: decoding JSON")
        return False

    except requests.exceptions.ReadTimeout:
        print(f"Error: ReadTimeout")
        return False        

    except Exception as error:
        print(error)
        return False 


def get_base_domain(url: str) -> Optional[str]:
    """
    Extracts the registered base domain from a given URL using tldextract.

    Args:
        url (str): The full URL or hostname.

    Returns:
        Optional[str]: The base domain (e.g., 'example.com', 'example.co.uk'),
                       or None if it cannot be extracted.

    Examples:
        >>> get_base_domain("https://sub.example.co.uk/path")
        'example.co.uk'

        >>> get_base_domain("example.com")
        'example.com'

        >>> get_base_domain("invalid_url")
        None
    """
    if not isinstance(url, str) or not url.strip():
        print("Invalid input: URL must be a non-empty string.")
        return None

    try:
        # Normalize the URL
        parsed_url = urlparse(url.strip())
        netloc = parsed_url.netloc or parsed_url.path  # handle URLs without scheme

        extracted = tldextract.extract(netloc)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        else:
            print(f"Could not extract base domain from: {url}")
            return None
    except Exception as e:
        print(f"Error extracting base domain from URL '{url}': {e}")
        return None

def get_header(referer:str = "", authority:str=""):
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    ]
    user_agent = random.choice(user_agent_list)

    headers = {
        'Authority': authority,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, br',
        'Pragma': 'no-cache',
        'Referer': referer,
        'Sec-CH-UA': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }

    return headers

def fetch_proxy_ips(country:str="all",protocol:str="http",port:int=None,limit:int=None):
    """
    Displays the details of the proxies fetched from the API.

    Args:
        proxies (Optional[list]): List of proxies to display. Each proxy is a dictionary.
    """
    API_URL = f"https://api.proxyscrape.com/v4/free-proxy-list/get?request=displayproxies&protocol={protocol}&timeout=10000&country={country}&ssl=all&anonymity=all&skip=0&limit=2000&proxy_format=ipport&format=json"
    try:
        response = get_request(url=API_URL, proxy=False)
        proxies = response.json()
        
        if proxies is None:
            print("No proxies available.")
            return

        data_list = list()
        for idx, proxy in enumerate(proxies.get("proxies",""), start=1):
            data_dict = dict()

            ip = proxy.get("ip")
            json_port = proxy.get("port")
            ssl = proxy.get("ssl")
            protocol = proxy.get("protocol")
            uptime = proxy.get("uptime")
            uptime = f"{uptime:.2f}%"
            last_update = proxy.get("ip_data_last_update")
            last_update = datetime.fromtimestamp(last_update, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            as_name = proxy.get("ip_data", {}).get("as", "")
            asname = proxy.get("ip_data", {}).get("asname", "")
            isp = proxy.get("ip_data", {}).get("isp", "")
            lat = proxy.get("ip_data", {}).get("lat", "")
            lon = proxy.get("ip_data", {}).get("lon", "")
            country = proxy.get("ip_data", {}).get("country", "Unknown")

            if port is None:
                data_dict["ip"] = ip
                data_dict["port"] = json_port
                data_dict["proxy"] = f"{ip}:{json_port}"
                data_dict["protocol"] = protocol
                data_dict["uptime"] = uptime
                data_dict["last_update"] = last_update
                data_dict["as"] = as_name
                data_dict["asname"] = asname
                data_dict["isp"] = isp
                data_dict["lat"] = lat
                data_dict["lon"] = lon
                data_dict["country"] = country
                data_list.append(data_dict)
            
            else:
                if port == json_port:
                    data_dict["ip"] = ip
                    data_dict["port"] = json_port
                    data_dict["proxy"] = f"{ip}:{json_port}"
                    data_dict["protocol"] = protocol
                    data_dict["uptime"] = uptime
                    data_dict["last_update"] = last_update
                    data_dict["as"] = as_name
                    data_dict["asname"] = asname
                    data_dict["isp"] = isp
                    data_dict["lat"] = lat
                    data_dict["lon"] = lon
                    data_dict["country"] = country
                    data_list.append(data_dict)

        if limit is None:
            return data_list
        return data_list[:limit]
    
    except Exception as e:
        print(e)

def get_request(url, max_retries=5, header=None, country:str="all", protocol:str="http", port:int=None, proxy:bool=True):
    if "api.proxyscrape.com" not in url:
        print(f"Request:{url}")
    request_obj = None
    attempts = 0

    while attempts < max_retries:
        attempts += 1
        
        if proxy:
            if "api.proxyscrape.com" not in url:
                proxies = fetch_proxy_ips(country=country,protocol=protocol, port=port)
                proxy_list = [item.get("proxy") for item in proxies]
                proxy_ele = random.choice(proxy_list)
                proxy_dict = {"http": f"http://{proxy_ele}", "https": f"http://{proxy_ele}"}

            if header is None:
                domain_url = get_base_domain(url = url)
                header = get_header(referer = domain_url, authority = domain_url)

        try:
            time.sleep(random.randint(3, 7))
            if proxy:
                print(f"[Attempt {attempts}] Using proxy: {proxy_ele}")
                request_obj = requests.get(url, headers=header, proxies=proxy_dict, timeout=10)
            elif not proxy:
                request_obj = requests.get(url, timeout=10)

        except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout) as e:
            try:
                time.sleep(random.randint(3, 7))
                if proxy:
                    request_obj = requests.get(url, headers=header, proxies=proxy_dict, verify=False, timeout=15)
                elif not proxy:
                    request_obj = requests.get(url, verify=False, timeout=15)
            except Exception as e:
                continue
        
        except requests.exceptions.ConnectionError as error:
            print("Check Net Connection")
            continue

        except Exception as e:
            print(f"Unexpected error: {e}")
            continue

        if request_obj and request_obj.status_code == 200:
            if "api.proxyscrape.com" not in url:
                print(f"Response:{request_obj.status_code}")
            return request_obj
        else:
            print(f"Request failed with status: {request_obj.status_code if request_obj else 'No response'}")
            print("Re-trying...")

    print(f"Failed to get a successful response after {max_retries} attempts.")