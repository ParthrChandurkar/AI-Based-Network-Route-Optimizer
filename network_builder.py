"""
network_builder.py — NetworkX graph construction and mutation.
All public functions return (G, message) so the UI can show status.
"""
import networkx as nx
import pandas as pd
import numpy as np
from typing import Tuple

LINK_DEFAULTS = dict(
    distance=20, bandwidth=300.0, latency=20.0,
    packet_loss=1.0, traffic_load=50.0,
    failure_prob=0.0, risk_label="Low",
    ai_weight=20.0, failed=False,
)


def build_default_topology() -> nx.Graph:
    """8-router ISP-style topology with realistic link attributes."""
    G = nx.Graph()
    for r in ["R1","R2","R3","R4","R5","R6","R7","R8"]:
        G.add_node(r)
    links = [
        ("R1","R2", dict(distance=10, bandwidth=900, latency=5,  packet_loss=0.5, traffic_load=30)),
        ("R1","R3", dict(distance=20, bandwidth=600, latency=12, packet_loss=1.0, traffic_load=50)),
        ("R2","R4", dict(distance=15, bandwidth=750, latency=8,  packet_loss=0.8, traffic_load=60)),
        ("R2","R5", dict(distance=25, bandwidth=400, latency=18, packet_loss=2.5, traffic_load=75)),
        ("R3","R4", dict(distance=12, bandwidth=500, latency=15, packet_loss=1.5, traffic_load=45)),
        ("R3","R6", dict(distance=30, bandwidth=200, latency=35, packet_loss=5.0, traffic_load=80)),
        ("R4","R7", dict(distance=18, bandwidth=650, latency=10, packet_loss=1.0, traffic_load=55)),
        ("R5","R8", dict(distance=22, bandwidth=350, latency=22, packet_loss=3.0, traffic_load=70)),
        ("R6","R7", dict(distance=14, bandwidth=550, latency=14, packet_loss=1.2, traffic_load=40)),
        ("R7","R8", dict(distance=10, bandwidth=800, latency=6,  packet_loss=0.6, traffic_load=35)),
        ("R5","R6", dict(distance=35, bandwidth=150, latency=45, packet_loss=8.0, traffic_load=90)),
        ("R1","R4", dict(distance=28, bandwidth=300, latency=25, packet_loss=3.5, traffic_load=65)),
    ]
    for u, v, attrs in links:
        G.add_edge(u, v, **{**LINK_DEFAULTS, **attrs, "ai_weight": float(attrs["distance"])})
    _assign_positions(G)
    return G


def _assign_positions(G: nx.Graph):
    pos = nx.spring_layout(G, seed=42, k=2.5)
    for node, (x, y) in pos.items():
        G.nodes[node]["pos"] = (round(float(x), 4), round(float(y), 4))


def add_router(G: nx.Graph, name: str) -> Tuple[bool, str]:
    name = name.strip()
    if not name:           return False, "Router name cannot be empty."
    if name in G.nodes:    return False, f"Router '{name}' already exists."
    G.add_node(name, pos=(0.0, 0.0))
    _assign_positions(G)
    return True, f"Router '{name}' added."


def remove_router(G: nx.Graph, name: str) -> Tuple[bool, str]:
    if name not in G.nodes: return False, f"Router '{name}' not found."
    G.remove_node(name)
    return True, f"Router '{name}' and its links removed."


def add_link(G: nx.Graph, src: str, dst: str, attrs: dict) -> Tuple[bool, str]:
    if src not in G.nodes: return False, f"Router '{src}' not found."
    if dst not in G.nodes: return False, f"Router '{dst}' not found."
    if src == dst:         return False, "Source and destination must differ."
    if G.has_edge(src, dst): return False, f"Link '{src}↔{dst}' already exists."
    full = {**LINK_DEFAULTS, **attrs, "ai_weight": float(attrs.get("distance", 20))}
    G.add_edge(src, dst, **full)
    return True, f"Link '{src}↔{dst}' added."


def remove_link(G: nx.Graph, src: str, dst: str) -> Tuple[bool, str]:
    if not G.has_edge(src, dst): return False, f"Link '{src}↔{dst}' not found."
    G.remove_edge(src, dst)
    return True, f"Link '{src}↔{dst}' removed."


def update_link(G: nx.Graph, src: str, dst: str, attrs: dict) -> Tuple[bool, str]:
    if not G.has_edge(src, dst): return False, f"Link '{src}↔{dst}' not found."
    for k, v in attrs.items():
        G[src][dst][k] = v
    return True, f"Link '{src}↔{dst}' updated."


def set_link_failed(G: nx.Graph, src: str, dst: str, failed: bool) -> Tuple[bool, str]:
    if not G.has_edge(src, dst): return False, f"Link '{src}↔{dst}' not found."
    G[src][dst]["failed"] = failed
    state = "FAILED" if failed else "RESTORED"
    return True, f"Link '{src}↔{dst}' marked {state}."


def get_edge_df(G: nx.Graph) -> pd.DataFrame:
    rows = []
    for u, v, data in G.edges(data=True):
        rows.append({"source": u, "target": v, **data})
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def graph_summary(G: nx.Graph) -> dict:
    return {
        "routers":   G.number_of_nodes(),
        "links":     G.number_of_edges(),
        "connected": nx.is_connected(G) if G.number_of_nodes() > 1 else False,
        "density":   round(nx.density(G), 4),
    }
