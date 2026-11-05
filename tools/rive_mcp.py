"""Call a tool on the Rive editor's local MCP server (http://127.0.0.1:9791/mcp) without a session connector.
Usage: python3 tools/rive_mcp.py <tool> '<json args>' [image-out-dir]
Images in the result are written as PNG files into image-out-dir (default build/captures)."""
import base64, json, os, sys, urllib.request
URL = 'http://127.0.0.1:9791/mcp'
H = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}

def post(body, sid=None):
    h = dict(H, **({'mcp-session-id': sid} if sid else {}))
    req = urllib.request.Request(URL, json.dumps(body).encode(), h)
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
        sid = r.headers.get('mcp-session-id') or sid
    lines = [l[5:].strip() for l in raw.splitlines() if l.startswith('data:')]
    return (json.loads(lines[-1]) if lines else (json.loads(raw) if raw.strip() else {})), sid

_, sid = post({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
    'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'uikit-tools', 'version': '1'}}})
post({'jsonrpc': '2.0', 'method': 'notifications/initialized'}, sid)
tool, args = sys.argv[1], json.loads(sys.argv[2] if len(sys.argv) > 2 else '{}')
out_dir = sys.argv[3] if len(sys.argv) > 3 else 'build/captures'
res, _ = post({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': {'name': tool, 'arguments': args}}, sid)
if 'error' in res:
    print(json.dumps(res['error'])); sys.exit(1)
for i, c in enumerate(res['result'].get('content', [])):
    if c.get('type') == 'image':
        os.makedirs(out_dir, exist_ok=True)
        name = (args.get('artboardId') or tool).replace(' ', '_')
        p = os.path.join(out_dir, f'{name}.png')
        open(p, 'wb').write(base64.b64decode(c['data']))
        print('image ->', p)
    elif c.get('type') == 'text':
        print(c['text'][:3000])
