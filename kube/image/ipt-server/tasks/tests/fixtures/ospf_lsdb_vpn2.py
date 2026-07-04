"""Realistic OSPF LSDB / RIB JSON fixtures for nexthop_monitor tests.

These mirror vpn2 topology after outer_de is added: two transit-providers
(outer_pt and outer_de) both originating default, wg_uk.rutestvpn and
wg_de.rutestvpn as local peers, ipt_server as the viewer.
"""
from __future__ import annotations


# router LSDB fragment — only the sections probe code actually reads
ROUTER_LSDB_TWO_OUTERS = {
    "routerId": "10.130.30.99",
    "routerLinkStates": {
        "areas": {
            "0.0.0.0": [
                # outer_pt's Router LSA — declares 10.9.19.2 as p2p link
                {
                    "linkStateId": "10.130.30.23",
                    "advertisingRouter": "10.130.30.23",
                    "asbr": True,
                    "routerLinks": {
                        "link0": {"linkType": "Stub Network",
                                   "networkAddress": "172.30.0.0",
                                   "networkMask": "255.255.255.0"},
                        "link1": {"linkType": "another Router (point-to-point)",
                                   "neighborRouterId": "10.130.30.20",
                                   "routerInterfaceAddress": "10.9.19.2"},
                        "link2": {"linkType": "Stub Network",
                                   "networkAddress": "10.9.19.0",
                                   "networkMask": "255.255.255.0"},
                    },
                },
                # outer_de's Router LSA — declares 10.9.21.2 as p2p link
                {
                    "linkStateId": "10.130.30.33",
                    "advertisingRouter": "10.130.30.33",
                    "asbr": True,
                    "routerLinks": {
                        "link0": {"linkType": "Stub Network",
                                   "networkAddress": "172.30.0.0",
                                   "networkMask": "255.255.255.0"},
                        "link1": {"linkType": "another Router (point-to-point)",
                                   "neighborRouterId": "10.130.30.30",
                                   "routerInterfaceAddress": "10.9.21.2"},
                        "link2": {"linkType": "Stub Network",
                                   "networkAddress": "10.9.21.0",
                                   "networkMask": "255.255.255.0"},
                    },
                },
                # Some other router (wg_uk.rutestvpn) — has 10.9.19.1 as its side
                {
                    "linkStateId": "10.130.30.20",
                    "advertisingRouter": "10.130.30.20",
                    "asbr": False,
                    "routerLinks": {
                        "link0": {"linkType": "another Router (point-to-point)",
                                   "neighborRouterId": "10.130.30.23",
                                   "routerInterfaceAddress": "10.9.19.1"},
                        "link1": {"linkType": "Stub Network",
                                   "networkAddress": "10.9.19.0",
                                   "networkMask": "255.255.255.0"},
                    },
                },
            ],
        },
    },
}


# external LSDB — both outers originate default
EXTERNAL_LSDB_BOTH_DEFAULTS = {
    "routerId": "10.130.30.99",
    "asExternalLinkStates": [
        {"linkStateId": "0.0.0.0", "networkMask": 0,
         "advertisingRouter": "10.130.30.23"},
        {"linkStateId": "0.0.0.0", "networkMask": 0,
         "advertisingRouter": "10.130.30.33"},
        # Unrelated external — firezone advertising its subnet
        {"linkStateId": "10.9.20.0", "networkMask": 24,
         "advertisingRouter": "10.9.20.2"},
    ],
}


# external LSDB — only outer_pt originates default (outer_de down or
# default_originate disabled)
EXTERNAL_LSDB_ONLY_PT = {
    "routerId": "10.130.30.99",
    "asExternalLinkStates": [
        {"linkStateId": "0.0.0.0", "networkMask": 0,
         "advertisingRouter": "10.130.30.23"},
    ],
}


EXTERNAL_LSDB_NONE = {
    "routerId": "10.130.30.99",
    "asExternalLinkStates": [],
}


# OSPF neighbor state (show ip ospf neighbor json). Keyed by neighbor
# router-id; each value is a list of adjacency entries. Both egress routers
# (outer_pt 10.130.30.23, outer_de 10.130.30.33) are Full — the healthy
# steady state. The stub-owner router (10.130.30.30) is also Full so the
# directly-attached backbone-transit probe stays alive.
NEIGHBORS_BOTH_FULL = {
    "neighbors": {
        "10.130.30.23": [
            {"state": "Full/DR", "address": "172.30.0.110", "ifaceName": "backbone"},
        ],
        "10.130.30.33": [
            {"state": "Full/Backup", "address": "172.30.0.112", "ifaceName": "backbone"},
        ],
        "10.130.30.30": [
            {"state": "Full/-", "address": "172.30.0.6", "ifaceName": "backbone"},
        ],
        "10.130.30.20": [
            {"state": "Full/DROther", "address": "172.30.0.110", "ifaceName": "backbone"},
        ],
    },
}


# OSPF neighbor state with outer_de (10.130.30.33) NOT Full: the de edge is
# dead, so its OSPF adjacency to the hub has dropped. This is the issue #37
# case — the hub-side WireGuard interface stays UP so 10.9.21.0/24 remains
# on-link and RIB-resolvable, but the neighbor is no longer Full.
NEIGHBORS_DE_DOWN = {
    "neighbors": {
        "10.130.30.23": [
            {"state": "Full/DR", "address": "172.30.0.110", "ifaceName": "backbone"},
        ],
        # outer_de present but stuck in ExStart (adjacency never re-formed) —
        # not Full, so it must NOT count as a live egress.
        "10.130.30.33": [
            {"state": "ExStart/-", "address": "172.30.0.112", "ifaceName": "backbone"},
        ],
    },
}


# OSPF neighbor state with the de edge fully gone from the neighbor table
# (Dead Interval expired and the neighbor entry was removed entirely).
NEIGHBORS_DE_ABSENT = {
    "neighbors": {
        "10.130.30.23": [
            {"state": "Full/DR", "address": "172.30.0.110", "ifaceName": "backbone"},
        ],
    },
}


# OSPF RIB (show ip ospf route)
RIB_TWO_OUTERS = {
    "10.9.19.0/24": {"routeType": "N", "cost": 20, "area": "0.0.0.0",
                     "nexthops": [{"ip": "172.30.0.3", "via": "backbone",
                                    "advertisedRouter": "10.130.30.20"}]},
    "10.9.21.0/24": {"routeType": "N", "cost": 20, "area": "0.0.0.0",
                     "nexthops": [{"ip": "172.30.0.4", "via": "backbone",
                                    "advertisedRouter": "10.130.30.30"}]},
    "10.130.30.23": {"routeType": "R ", "cost": 20, "area": "0.0.0.0",
                     "routerType": "asbr",
                     "nexthops": [{"ip": "172.30.0.3", "via": "backbone"}]},
    "10.130.30.33": {"routeType": "R ", "cost": 20, "area": "0.0.0.0",
                     "routerType": "asbr",
                     "nexthops": [{"ip": "172.30.0.4", "via": "backbone"}]},
    "0.0.0.0/0": {"routeType": "N E2", "cost": 20,
                  "nexthops": [
                      {"ip": "172.30.0.3", "via": "backbone",
                       "advertisedRouter": "10.130.30.23"},
                      {"ip": "172.30.0.4", "via": "backbone",
                       "advertisedRouter": "10.130.30.33"},
                  ]},
}


# RIB with outer_pt gone (Dead Interval expired)
RIB_PT_GONE = {
    "10.9.21.0/24": {"routeType": "N", "cost": 20, "area": "0.0.0.0",
                     "nexthops": [{"ip": "172.30.0.4", "via": "backbone",
                                    "advertisedRouter": "10.130.30.30"}]},
    "10.130.30.33": {"routeType": "R ", "cost": 20, "area": "0.0.0.0",
                     "routerType": "asbr",
                     "nexthops": [{"ip": "172.30.0.4", "via": "backbone"}]},
    "0.0.0.0/0": {"routeType": "N E2", "cost": 20,
                  "nexthops": [
                      {"ip": "172.30.0.4", "via": "backbone",
                       "advertisedRouter": "10.130.30.33"},
                  ]},
}
