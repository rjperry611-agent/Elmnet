"""
network.py
~~~~~~~~~~~

This module implements a very lightweight peer‑to‑peer (P2P) networking
layer inspired by some of the ideas found in the Bitcoin protocol.  Each
node in the network generates a random private key and derives a short
address from it using SHA‑256 and RIPEMD‑160 followed by Base58Check
encoding.  Nodes discover one another by connecting to a list of
bootstrap peers and perform a simple handshake consisting of a
``version`` message and a ``verack`` acknowledgement, similar to the
version/verack handshake described in Bitcoin【741702894021493†L867-L878】.

After the handshake has completed a bidirectional JSON based message
protocol is used on top of a plain TCP socket.  Messages are encoded
as newline separated JSON objects with a ``type`` field.  The two
primary application level messages are:

* ``query`` – broadcast by a node that wishes to ask all of its peers
  to process a query.  It carries a unique UUID in the ``id`` field,
  an ``origin`` address identifying the original requester and the
  query text itself.  Nodes forward unknown queries to all peers
  except the one they received the message from and send back a
  ``response``.
* ``response`` – carries the original query ``id`` along with the
  replying node's ``from`` address and the result of locally
  processing the query.

The ``P2PNetwork`` class encapsulates all networking concerns.  It
spawns its own ``asyncio`` event loop in a background thread to avoid
blocking the FastAPI server.  Each peer connection is handled by an
asynchronous task that reads and writes JSON messages.  When a query
is broadcast the initiator registers an aggregator entry in
``self.pending_queries`` containing a list of responses and an
``asyncio.Event``.  As response messages arrive the aggregator is
updated and the event is set once all peers have replied or a
timeout occurs.

To integrate the network with the rest of the application simply
instantiate ``P2PNetwork`` with a port, an optional list of bootstrap
peers and a callback.  The callback should accept a query string and
return the local node's response.  When running in production the
callback will likely wrap the orchestrator's call into the LLAMA
pipeline; during development and testing it can be a simple function
that returns a fixed string.  Once started the network runs until the
Python process exits.

Note: this implementation focuses on demonstrating the underlying
network mechanics.  It is **not** a full implementation of the
Bitcoin protocol.  Keys are generated from random bytes instead of a
secp256k1 ECDSA key pair, address derivation is simplified and
messages are exchanged using JSON instead of Bitcoin's binary wire
format.  Nonetheless the major concepts of handshake, peer discovery,
unique node identifiers and query propagation are preserved【761311005096124†L350-L399】.
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
import hashlib
import secrets
from typing import Callable, Dict, List, Optional, Tuple


class P2PNetwork:
    """A simple peer‑to‑peer network built using asyncio sockets.

    Instances of this class manage a TCP server, connect to known
    peers, perform a version/verack handshake and then exchange
    newline‑delimited JSON messages.  Queries may be broadcast to all
    connected peers and responses are collected and returned to the
    caller.

    :param port: The TCP port to listen on for inbound P2P traffic.
    :param bootstrap_peers: Optional list of ``host:port`` strings to
        connect to upon startup.  If provided the node will attempt
        to establish outgoing connections to these peers.
    :param on_query: A callback invoked whenever the node receives a
        new query.  It is passed the query string and should return a
        result.  If the callback returns a coroutine it will be
        awaited automatically.
    """

    def __init__(self, port: int, bootstrap_peers: Optional[List[str]], on_query: Callable[[str], object]):
        self.port = port
        self.bootstrap_peers = bootstrap_peers or []
        self.on_query = on_query

        # Generate a random "private key" and derive a base58 encoded address.
        self._private_key = secrets.token_bytes(32)
        self.address = self._derive_address(self._private_key)

        # Maps peer address strings to stream writers.
        self.peers: Dict[str, asyncio.StreamWriter] = {}

        # Set of processed query IDs to prevent replay loops.
        self.processed_queries: set[str] = set()

        # Pending queries waiting for responses.  Each entry maps a
        # query ID to a dict containing a list of responses, the
        # expected number of replies and an asyncio.Event used to
        # signal completion.
        self.pending_queries: Dict[str, Dict[str, object]] = {}

        # Dedicated event loop for all networking tasks.  Running a
        # separate loop allows the network to operate concurrently
        # alongside FastAPI/uvicorn which will create its own loop.
        self.loop = asyncio.new_event_loop()

    # ------------------------------------------------------------------
    # Public API

    def start(self) -> None:
        """Start the P2P network in a background daemon thread.

        This method returns immediately.  All networking happens on
        the network's own asyncio event loop running in a separate
        thread.  If the loop already runs this method does nothing.
        """
        thread = threading.Thread(target=self._start_loop, daemon=True)
        thread.start()

    async def query_peers(self, query: str, timeout: float = 10.0) -> List[object]:
        """Broadcast a query to all connected peers and collect their responses.

        A unique UUID is generated for the query.  The query is sent
        to every currently connected peer.  The method returns a list
        of responses.  If no peers are connected an empty list is
        returned.  If not all peers reply before the given timeout
        expires only the received responses are returned.  The query
        remains in the processed set to prevent reprocessing on
        future broadcasts.

        :param query: The question or task to broadcast to peers.
        :param timeout: Maximum number of seconds to wait for replies.
        :returns: A list of response objects from peers.
        """
        if not self.peers:
            return []
        qid = str(uuid.uuid4())
        # Mark as processed locally to prevent loopback processing when
        # our own message propagates back to us.
        self.processed_queries.add(qid)
        # Prepare aggregator entry.
        agg = {
            'responses': [],
            'remaining': len(self.peers),
            'event': asyncio.Event()
        }
        self.pending_queries[qid] = agg
        # Build query message once.
        msg = {'type': 'query', 'id': qid, 'origin': self.address, 'payload': query}
        # Send to all peers.
        for peer_id, writer in list(self.peers.items()):
            try:
                await self._send_message(writer, msg)
            except Exception as exc:
                # Treat errors as missing responses.
                print(f"Error sending query to peer {peer_id}: {exc}")
                agg['remaining'] -= 1
        # Wait for responses or until timeout.
        try:
            await asyncio.wait_for(agg['event'].wait(), timeout=timeout)
        except asyncio.TimeoutError:
            print("Timed out waiting for peer responses")
        # Clean up pending state and return a snapshot of responses.
        self.pending_queries.pop(qid, None)
        return list(agg['responses'])

    # ------------------------------------------------------------------
    # Private helpers

    def _start_loop(self) -> None:
        """Internal helper to run the event loop forever."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())

    async def _run(self) -> None:
        """Coroutine that starts the server and connects to bootstrap peers."""
        server = await asyncio.start_server(self._handle_incoming, host='0.0.0.0', port=self.port)
        print(f"P2P network listening on port {self.port}, address {self.address}")
        # Attempt to establish outbound connections to bootstrap peers.
        for peer in self.bootstrap_peers:
            # Expect host:port strings.
            try:
                host, port_str = peer.split(':', 1)
                port = int(port_str)
            except ValueError:
                print(f"Invalid bootstrap peer entry: {peer}, expected host:port")
                continue
            try:
                reader, writer = await asyncio.open_connection(host, port)
                await self._outgoing_handshake(reader, writer)
            except Exception as exc:
                print(f"Failed to connect to bootstrap peer {peer}: {exc}")
        async with server:
            await server.serve_forever()

    # Base58 encoding used for simplified address derivation.
    @staticmethod
    def _base58_encode(data: bytes) -> str:
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(data, 'big')
        encode = ''
        while num > 0:
            num, rem = divmod(num, 58)
            encode = alphabet[rem] + encode
        # Preserve leading zero bytes.
        pad = 0
        for b in data:
            if b == 0:
                pad += 1
            else:
                break
        return alphabet[0] * pad + encode

    def _derive_address(self, private_key: bytes) -> str:
        """Derive a simple Base58Check encoded address from random bytes.

        The derivation follows the high level steps used in Bitcoin
        address construction: a SHA‑256 hash of the private key is
        passed through RIPEMD‑160 to shorten it; a 0x00 prefix is
        prepended to denote the network; a 4‑byte double SHA‑256
        checksum is appended and finally the result is encoded using
        Base58【761311005096124†L350-L399】.
        """
        sha = hashlib.sha256(private_key).digest()
        ripe = hashlib.new('ripemd160', sha).digest()
        payload = b'\x00' + ripe
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        return self._base58_encode(payload + checksum)

    async def _outgoing_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Perform a version/verack handshake on an outbound connection."""
        # Send our version.
        version_msg = {'type': 'version', 'address': self.address}
        await self._send_message(writer, version_msg)
        # Wait for the peer's version.
        msg = await self._read_message(reader)
        if msg.get('type') != 'version':
            print("Unexpected message during handshake (outgoing):", msg)
            writer.close()
            await writer.wait_closed()
            return
        remote_addr = msg.get('address')
        # Send and receive verack.
        await self._send_message(writer, {'type': 'verack'})
        msg2 = await self._read_message(reader)
        if msg2.get('type') != 'verack':
            print("Expected verack during handshake (outgoing)")
            writer.close()
            await writer.wait_closed()
            return
        # Store the peer writer and spawn a reader task.
        self.peers[remote_addr] = writer
        print(f"Connected to peer {remote_addr}")
        # Launch a task to handle incoming messages from this peer.
        self.loop.create_task(self._peer_reader(remote_addr, reader, writer))

    async def _incoming_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Optional[str]:
        """Perform a version/verack handshake on an inbound connection."""
        # Expect the peer's version first.
        msg = await self._read_message(reader)
        if msg.get('type') != 'version':
            print("Unexpected message during handshake (incoming):", msg)
            return None
        remote_addr = msg.get('address')
        # Respond with our version.
        await self._send_message(writer, {'type': 'version', 'address': self.address})
        # Expect verack and send back verack.
        msg2 = await self._read_message(reader)
        if msg2.get('type') != 'verack':
            print("Expected verack during handshake (incoming)")
            return None
        await self._send_message(writer, {'type': 'verack'})
        # Save the writer and spawn a reader task.
        self.peers[remote_addr] = writer
        print(f"Accepted connection from peer {remote_addr}")
        return remote_addr

    async def _handle_incoming(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a new inbound connection by performing a handshake."""
        peer_id = await self._incoming_handshake(reader, writer)
        if peer_id is None:
            writer.close()
            await writer.wait_closed()
            return
        # Launch a reader for this connection.
        await self._peer_reader(peer_id, reader, writer)

    async def _peer_reader(self, peer_id: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Continuously read and dispatch messages from a connected peer."""
        try:
            while True:
                msg = await self._read_message(reader)
                if not msg:
                    break
                await self._dispatch_message(msg, peer_id)
        except Exception as exc:
            print(f"Error while reading from peer {peer_id}: {exc}")
        finally:
            # Remove peer on disconnect.
            if peer_id in self.peers:
                del self.peers[peer_id]
            writer.close()
            await writer.wait_closed()
            print(f"Disconnected from peer {peer_id}")

    async def _dispatch_message(self, msg: Dict[str, object], sender_peer: str) -> None:
        """Handle an incoming message based on its type."""
        mtype = msg.get('type')
        if mtype == 'query':
            await self._handle_query(msg, sender_peer)
        elif mtype == 'response':
            await self._handle_response(msg, sender_peer)
        # Unknown message types are ignored.

    async def _handle_query(self, msg: Dict[str, object], sender_peer: str) -> None:
        """Process an inbound query message.

        If this node has already processed the query the message is
        ignored.  Otherwise the query is forwarded to all other peers,
        the callback is invoked to obtain a local result and a
        response message is sent back to the sender.
        """
        qid = msg.get('id')  # type: ignore
        origin = msg.get('origin')  # type: ignore
        query = msg.get('payload')  # type: ignore
        if not isinstance(qid, str) or not isinstance(query, str):
            return
        # Skip if we've already seen this query.
        if qid in self.processed_queries:
            return
        self.processed_queries.add(qid)
        # Forward to all peers except the sender.
        for peer_id, writer in list(self.peers.items()):
            if peer_id == sender_peer:
                continue
            try:
                await self._send_message(writer, msg)
            except Exception as exc:
                print(f"Error forwarding query to peer {peer_id}: {exc}")
        # Process locally via callback.
        try:
            result = self.on_query(query)
            # Await if the callback is async.
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as exc:
            result = {'error': str(exc)}
        # Build response and send it back to the sender.  The sender
        # will propagate it towards the originator.
        resp_msg = {
            'type': 'response',
            'id': qid,
            'from': self.address,
            'response': result,
        }
        writer = self.peers.get(sender_peer)
        if writer is not None:
            try:
                await self._send_message(writer, resp_msg)
            except Exception as exc:
                print(f"Error sending response to peer {sender_peer}: {exc}")

    async def _handle_response(self, msg: Dict[str, object], peer_id: str) -> None:
        """Handle an inbound response message for a pending query."""
        qid = msg.get('id')  # type: ignore
        if not isinstance(qid, str):
            return
        agg = self.pending_queries.get(qid)
        if agg is None:
            return
        # Append the response along with the address of the peer that sent it.
        response_payload = msg.get('response')
        agg['responses'].append(response_payload)
        agg['remaining'] -= 1
        if agg['remaining'] <= 0:
            agg['event'].set()

    async def _send_message(self, writer: asyncio.StreamWriter, message: Dict[str, object]) -> None:
        """Serialize and send a single JSON message to a peer."""
        data = json.dumps(message).encode('utf-8') + b'\n'
        writer.write(data)
        await writer.drain()

    async def _read_message(self, reader: asyncio.StreamReader) -> Dict[str, object]:
        """Read a single newline‑terminated JSON message from a peer."""
        try:
            line = await reader.readline()
        except Exception:
            return {}
        if not line:
            return {}
        try:
            return json.loads(line.decode('utf-8'))
        except Exception:
            return {}