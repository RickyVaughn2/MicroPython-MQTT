import usocket
from ubinascii import hexlify
from uhashlib import sha1
import ussl
import ustruct

def connect(client_id, username, password, host, port, keepalive):
    s = usocket.socket()
    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][-1]
    s.connect(addr)

    if username is not None:
        s = ussl.wrap_socket(s)

    packet = bytearray(b"\x10\0\0\0\0")
    packet[0] |= 0x02 << 4
    if username is not None:
        packet[0] |= 0xC0
    if password is not None:
        packet[0] |= 0x80
    if username is None:
        username = b""
    if password is None:
        password = b""

    client_id = client_id.encode("utf-8")
    username = username.encode("utf-8")
    password = password.encode("utf-8")

    rem_len = 2 + len(client_id) + 2 + len(username) + 2 + len(password)

    packet[1] = rem_len
    packet.extend(ustruct.pack("!H", len(client_id)))
    packet.extend(client_id)
    packet.extend(ustruct.pack("!H", len(username)))
    packet.extend(username)
    packet.extend(ustruct.pack("!H", len(password)))
    packet.extend(password)

    s.write(packet)

    resp = s.read(4)
    cmd = resp[0] & 0xF0
    if cmd != 0x20:
        raise Exception("Not CONNACK")

    return s

def publish(s, topic, payload, qos=0, retain=False):
    topic = topic.encode("utf-8")
    packet = bytearray(b"\x30\0\0\0")
    packet[0] |= qos << 1
    if retain:
        packet[0] |= 1
    packet[1] = len(topic) + 2 + len(payload)
    packet.extend(ustruct.pack("!H", len(topic)))
    packet.extend(topic)
    packet.extend(payload)

    s.write(packet)

# Connect to the broker
s = connect("client_id", None, None, "broker.example.com", 1883, 60)

# Publish a message to the topic "test"
publish(s, "test", "Hello, MQTT!", qos=0, retain=False)
