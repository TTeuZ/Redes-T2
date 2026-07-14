# Fodinha over a Ring Network (Token Ring)

Distributed implementation of the Brazilian card game **Fodinha** (also known as "Foda-se"), running over a **ring** network topology with **token** passing, using raw UDP sockets (no networking/RPC frameworks). Assignment for the Computer Networks 2 course.

## The game

Fodinha is a Truco variant played by several people simultaneously, each one "against all the others". General rules of the game:

- Each player starts with a fixed amount of lives.
- Each round the cards are shuffled and dealt by a "dealer".
- One card is flipped (the **vira**); the card ranked immediately above it on the strength scale becomes **manilha** (the strongest card of the round). Manilha ties are broken by suit (Ouros < Espadas < Copas < Paus).
- Before playing, each player **bets** how many of the tricks they think they'll win. The sum of all players' bets **must** differ from the number of tricks to be played, since at least 1 player must lose life(s) every hand.
- Cards are played; whoever plays the strongest card wins the trick.
- At the end, each player loses lives equal to `|bet - tricks won|`.
- Whoever reaches 0 lives is eliminated; the game ends when a single player remains alive (the winner).

This implementation fixes the game at **4 players** (`NUM_PLAYERS`), **3 cards per hand** (`CARDS_BY_HAND`) and **3 tricks per hand** (`ROUNDS`), with **12** starting lives — a simplified version, scoped to fit a networking assignment rather than reproducing every table variant.

## Technical decisions

### Ring network + token

Each node (`Node`) only knows its **direct neighbor** (`neighbor`/ `neighbor_port`) — there is no central server and no broadcast. All communication is **point-to-point, node → neighbor**, forming a physical/logical ring: `N1 → N2 → N3 → N4 → N1`.

Two game abstractions circulate around the ring, acting as the **token**:

1. **Game protocol turn**: in each phase (dealing cards, betting, playing a card, showing results, etc.) a packet is born at the dealer, hops node by node collecting/forwarding data, makes a full lap around the ring and returns to whoever originated it — only then does the phase advance. This serializes access to the "shared state" (the hand's round) without a distributed lock or central coordinator: only whoever holds the token can write.
2. **Dealer role**: at the end of each hand, the `DEALER` packet is explicitly passed to the next neighbor (`pass_dealer`), transferring the role of "who shuffles/starts the phase" — just like token passing in classic Token Ring (IEEE 802.5), where only the token holder may transmit.

Eliminated players (`dead_mode`) keep **forwarding** any packet not addressed to them, so the ring never breaks — the "dead" node becomes a passive repeater until `END_GAME` circulates.

### UDP sockets + custom application protocol

- Transport: **UDP** (`socket.SOCK_DGRAM`), with no OS-level handshake or delivery/order guarantees — logical reliability (waiting for a response before advancing) is implemented at the application layer, with blocking `select()` and a timeout (`Constants.TIMEOUT`) instead of explicit retry/ACK.
- Message framing: `Package.get_message()` serializes into delimited plain text: `~|src|dst|type|data|~`. `type` is an integer enum (`CONNECTION`, `LIST`, `CARDS`, `BET`, `SHOW`, `MOVE`, `RESULTS`, `ROUND`, `ALIVE`, `END_GAME`, `DEALER`) that defines how the `data` payload should be parsed in each phase — a simple, hand-rolled application protocol over an unreliable transport.
- **Ring discovery/handshake**: `establish_connection()` implements a manual join — the dealer starts a `CONNECTION` packet that travels the ring, self-appending (each node's hostname) until `NUM_PLAYERS` nodes are counted; the final list is redistributed (`LIST`) so every node knows all participants before the game starts.

## Project structure

```
main.py            # main game loop (dealer/player), CLI arg parsing
src/
  Constants.py      # fixed config: player count, deck, strength scales, packet types
  Node.py           # network layer: UDP socket, neighbor, ring join, send/recv
  Package.py        # (de)serialization of the application protocol (message framing)
  Game.py           # Fodinha rules and the state machine for each round phase
```

## How to run

### Required hardware/network

- **4 machines** (`NUM_PLAYERS = 4`, fixed value in `Constants.py`) on the same local network, each with Python 3 installed.
- IP connectivity between the machines — in practice, all connected to an **Ethernet switch/hub** (a star physical topology is enough; the ring here is **logical**, defined by whichever node each one calls its "neighbor", not by the wiring). One Ethernet cable per machine to the switch is enough; no special hardware is needed beyond NICs + switch + cables.
- No special port needs to be opened besides the UDP port chosen via `-p` (same LAN, no NAT/firewall in between).
- To **test without 4 physical machines**: use `Constants.LOCAL_NAMES` (`N1`..`N4`) as `--machine`/`--neighbor` — in that case the node uses `127.0.0.1` and the whole "ring" runs on localhost, one process per terminal, each on a different port.

### Commands

Each process runs:

```bash
python3 main.py -m <machine> -p <port> -n <neighbor> -np <neighbor_port> -d <dealer>
```

- `-m/--machine`: hostname/IP of this machine (or `N1`..`N4` in local mode).
- `-p/--port`: local UDP port.
- `-n/--neighbor`: hostname/IP of the next node in the ring (where this node sends to).
- `-np/--neighbor_port`: neighbor's UDP port.
- `-d/--dealer`: `1` if this node starts as dealer, `0` otherwise (**exactly one** of the 4 must start with `1`).

Example on 4 physical machines forming the ring `A → B → C → D → A`, all on port `5000`:

```bash
# Machine A (starting dealer)
python3 main.py -m A -p 5000 -n B -np 5000 -d 1
# Machine B
python3 main.py -m B -p 5000 -n C -np 5000 -d 0
# Machine C
python3 main.py -m C -p 5000 -n D -np 5000 -d 0
# Machine D
python3 main.py -m D -p 5000 -n A -np 5000 -d 0
```

Local example (4 terminals on the same machine, distinct ports):

```bash
python3 main.py -m N1 -p 5001 -n N2 -np 5002 -d 1
python3 main.py -m N2 -p 5002 -n N3 -np 5003 -d 0
python3 main.py -m N3 -p 5003 -n N4 -np 5004 -d 0
python3 main.py -m N4 -p 5004 -n N1 -np 5001 -d 0
```

All 4 processes must be started before the handshake completes (`establish_connection`), since the join waits to count `NUM_PLAYERS` nodes.

## Theoretical background (computer networks)

- **Ring topology**: each node has exactly 2 logical neighbors (predecessor/successor), forming a closed cycle; messages travel the ring node by node until completing the lap.
- **Token passing (Token Ring, IEEE 802.5)**: a "right to transmit/act" (here, the game's phase token and the dealer role) circulates around the ring; only the holder may initiate an action, avoiding collisions/the need for central arbitration — fully distributed medium access control.
- **UDP vs TCP**: UDP is connectionless and gives no delivery/order guarantees; here "reliability" (waiting for confirmation before proceeding) is manually recreated at the application layer via blocking waits (`select`) and a full round-trip around the ring, illustrating why application protocols sometimes reimplement guarantees TCP would give for free.
- **Application protocol/message framing**: the need to define delimiters and a custom message format (`~|src|dst|type|data|~`) so the receiver can separate fields within a text payload — the same problem real protocols (HTTP, SMTP) solve with delimiters/headers.
- **Tolerating a "dead" node without breaking the ring**: eliminated nodes keep routing packets (repeater mode), demonstrating the classic problem of keeping a ring topology functional despite a participant failing/leaving.
