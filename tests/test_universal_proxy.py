import unittest
from fetch_proxy import parse_proxy_line, parse_proxy_lines, ProxyEndpoint

class TestUniversalProxy(unittest.TestCase):
    def test_socks5h_and_socks4a_requests_url(self):
        # 1. socks5 with auth -> socks5h
        ep1 = parse_proxy_line('socks5://user:pass@gw1.remproxy.com:9696')
        self.assertIsNotNone(ep1)
        self.assertTrue(ep1.requests_url().startswith('socks5h://'), ep1.requests_url())
        self.assertEqual(ep1.requests_url(), 'socks5h://user:pass@gw1.remproxy.com:9696')

        # 2. socks4 -> socks4a
        ep2 = parse_proxy_line('socks4://user:pass@1.2.3.4:1080')
        self.assertIsNotNone(ep2)
        self.assertTrue(ep2.requests_url().startswith('socks4a://'), ep2.requests_url())

        # 3. http -> http
        ep3 = parse_proxy_line('http://user:pass@1.2.3.4:8080')
        self.assertIsNotNone(ep3)
        self.assertTrue(ep3.requests_url().startswith('http://'), ep3.requests_url())

    def test_effective_scheme_autodetect(self):
        # Known SOCKS ports or auth backconnect proxies should auto-detect socks5
        ep_gw = parse_proxy_line('gw1.remproxy.com:9696:lgthsa819c-session-bc0e:1ecbv6zcps')
        self.assertIsNotNone(ep_gw)
        self.assertEqual(ep_gw.effective_scheme, 'socks5')
        self.assertTrue(ep_gw.is_socks)
        self.assertTrue(ep_gw.requests_url().startswith('socks5h://'))

        # Standard port 1080 should auto-detect socks5
        ep_1080 = parse_proxy_line('1.2.3.4:1080')
        self.assertIsNotNone(ep_1080)
        self.assertEqual(ep_1080.effective_scheme, 'socks5')

        # Standard web proxy 8080 should be http
        ep_8080 = parse_proxy_line('1.2.3.4:8080')
        self.assertIsNotNone(ep_8080)
        self.assertEqual(ep_8080.effective_scheme, 'http')

        # Explicit scheme overrides default
        ep_override = parse_proxy_line('http://1.2.3.4:1080')
        self.assertEqual(ep_override.effective_scheme, 'http')
        self.assertFalse(ep_override.is_socks)

    def test_auth_extraction(self):
        line = 'gw1.remproxy.com:9696:lgthsa819c-session-bc0e:1ecbv6zcps'
        ep = parse_proxy_line(line)
        self.assertIsNotNone(ep)
        host, port = ep.host_port()
        self.assertEqual(host, 'gw1.remproxy.com')
        self.assertEqual(port, 9696)
        self.assertEqual(ep.username, 'lgthsa819c-session-bc0e')
        self.assertEqual(ep.password, '1ecbv6zcps')

    def test_category_lookup_host_extraction(self):
        # Ensure that given a canonical line with user:pass@host:port,
        # extracting host does not extract username!
        canonical = 'socks5://lgthsa819c-session-bc0e:1ecbv6zcps@gw1.remproxy.com:9696'
        ep = parse_proxy_line(canonical)
        self.assertIsNotNone(ep)
        h, _ = ep.host_port()
        self.assertEqual(h, 'gw1.remproxy.com')
        self.assertNotEqual(h, 'lgthsa819c-session-bc0e')

if __name__ == '__main__':
    unittest.main()
