import sys, json
sys.path.insert(0, '.')
from fetch_proxy import ProxyUtils

# Тест 1: ProxyScrape v3/v4 формат (proxy = URI, ip_data.proxy = boolean)
test1 = json.dumps({
    "proxies": [{
        "ip": "1.2.3.4",
        "port": 8080,
        "proxy": "http://1.2.3.4:8080",
        "ip_data": {
            "hosting": True,
            "mobile": False,
            "isp": "test",
            "proxy": False,
            "countryCode": "US"
        }
    }]
})
r1 = ProxyUtils.parse_proxies(test1)
print(f"Test 1 (ProxyScrape): {r1}")
assert r1 == ["1.2.3.4:8080"], f"FAIL: expected ['1.2.3.4:8080'], got {r1}"

# Тест 2: monosans формат (host вместо ip, вложенная geolocation)
test2 = json.dumps([{
    "host": "5.6.7.8",
    "port": 3128,
    "exit_ip": "5.6.7.8",
    "geolocation": {
        "city": {"geoname_id": 524901, "names": {"en": "Moscow"}},
        "country": {"iso_code": "RU"}
    }
}])
r2 = ProxyUtils.parse_proxies(test2)
print(f"Test 2 (monosans): {r2}")
assert r2 == ["5.6.7.8:3128"], f"FAIL: expected ['5.6.7.8:3128'], got {r2}"

# Тест 3: geonode формат (data wrapper, port = string)
test3 = json.dumps({
    "data": [{
        "ip": "9.10.11.12",
        "port": "1080",
        "protocols": ["socks5"]
    }],
    "total": 1
})
r3 = ProxyUtils.parse_proxies(test3)
print(f"Test 3 (geonode): {r3}")
assert r3 == ["9.10.11.12:1080"], f"FAIL: expected ['9.10.11.12:1080'], got {r3}"

# Тест 4: текстовый формат (ip:port per line)
test4 = "1.1.1.1:8080\n2.2.2.2:3128\n"
r4 = ProxyUtils.parse_proxies(test4)
print(f"Test 4 (plain text): {sorted(r4)}")
assert set(r4) == {"1.1.1.1:8080", "2.2.2.2:3128"}, f"FAIL: {r4}"

print("\n✅ ALL TESTS PASSED")
