import asyncio

async def async_http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
    try:
        fut = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
        
        if proto == 'http':
            req = b"GET http://gstatic.com/generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
            writer.write(req)
            await writer.drain()
            
            resp = await asyncio.wait_for(reader.read(1024), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return b"204 No Content" in resp
            
        elif proto == 'socks4':
            # SOCKS4 connect request to gstatic.com (142.250.186.99): 80
            # 142 = 0x8e, 250 = 0xfa, 186 = 0xba, 99 = 0x63
            req = b"\x04\x01\x00\x50\x8E\xFA\xBA\x63\x00"
            writer.write(req)
            await writer.drain()
            
            resp = await asyncio.wait_for(reader.read(8), timeout=timeout)
            if len(resp) < 8 or resp[1] != 0x5a:
                writer.close()
                await writer.wait_closed()
                return False
                
            req2 = b"GET /generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
            writer.write(req2)
            await writer.drain()
            resp2 = await asyncio.wait_for(reader.read(1024), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return b"204 No Content" in resp2
            
        elif proto == 'socks5':
            # SOCKS5 hello
            writer.write(b"\x05\x01\x00")
            await writer.drain()
            resp = await asyncio.wait_for(reader.read(2), timeout=timeout)
            if len(resp) < 2 or resp[1] != 0x00:
                writer.close()
                await writer.wait_closed()
                return False
            
            # SOCKS5 connect to gstatic.com:80
            host = b"gstatic.com"
            req = b"\x05\x01\x00\x03" + bytes([len(host)]) + host + b"\x00\x50"
            writer.write(req)
            await writer.drain()
            
            # Read response, SOCKS5 bind response is 10 bytes for IPv4, variable for domain.
            # But the server replies with its bind address. Usually we just need to ensure the second byte is 0x00.
            # We'll read 4 bytes to get the address type, then read the rest.
            resp_hdr = await asyncio.wait_for(reader.readexactly(4), timeout=timeout)
            if resp_hdr[1] != 0x00:
                writer.close()
                await writer.wait_closed()
                return False
            
            atype = resp_hdr[3]
            if atype == 0x01: # IPv4
                await asyncio.wait_for(reader.readexactly(4 + 2), timeout=timeout)
            elif atype == 0x03: # Domain
                domain_len = (await asyncio.wait_for(reader.readexactly(1), timeout=timeout))[0]
                await asyncio.wait_for(reader.readexactly(domain_len + 2), timeout=timeout)
            elif atype == 0x04: # IPv6
                await asyncio.wait_for(reader.readexactly(16 + 2), timeout=timeout)
                
            req2 = b"GET /generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
            writer.write(req2)
            await writer.drain()
            resp2 = await asyncio.wait_for(reader.read(1024), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return b"204 No Content" in resp2
            
    except Exception as e:
        print("Error:", e)
        return False

async def main():
    print("Testing SOCKS5...")
    # Use a public socks5 or http to test
    # Need to find a working proxy first or just mock it.
    pass

if __name__ == '__main__':
    asyncio.run(main())
