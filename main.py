from __future__ import annotations
from pathlib import Path
import pandas as pd
from utils import (_safe_str, _safe_int, _limit)

from owlready2 import (
    get_ontology,
    Thing,
    DataProperty,
    ObjectProperty,
    FunctionalProperty,
    TransitiveProperty,
    sync_reasoner,
)

# constants
MAX_STOPS = 800
MAX_ROUTES = 250
MAX_TRIPS = 1200
MAX_TRANSFERS = 2000
MAX_PATHWAYS = 500
MAX_STOP_TIMES = 2000

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


CSV = {
    "stops": DATA_DIR / "stops.csv",
    "routes": DATA_DIR / "routes.csv",
    "trips": DATA_DIR / "trips.csv",
    "transfers": DATA_DIR / "transfers.csv",
    "pathways": DATA_DIR / "pathways.csv",
    "stop_times": DATA_DIR / "stop_times.csv",
}

OUT_FILE = DATA_DIR / "transport.owl"
ONTO_IRI = "http://example.org/transport.owl"


def main() -> None:
    stops_df = _limit(pd.read_csv(CSV["stops"]), MAX_STOPS)
    routes_df = _limit(pd.read_csv(CSV["routes"]), MAX_ROUTES)
    trips_df = _limit(pd.read_csv(CSV["trips"]), MAX_TRIPS)
    transfers_df = _limit(pd.read_csv(CSV["transfers"]), MAX_TRANSFERS)
    pathways_df = _limit(pd.read_csv(CSV["pathways"]), MAX_PATHWAYS)
    stop_times_df = _limit(pd.read_csv(CSV["stop_times"]), MAX_STOP_TIMES)

    onto = get_ontology(ONTO_IRI)

    with onto:
        class Stop(Thing):
            pass

        class Route(Thing):
            pass

        class Trip(Thing):
            pass

        class Transfer(Thing):
            pass

        class Pathway(Thing):
            pass

        # Subclasses
        class BusRoute(Route):
            pass

        class TramRoute(Route):
            pass

        class TrolleyRoute(Route):
            pass


        class WheelchairFriendlyTrip(Trip):
            pass

        class FastTransfer(Transfer):
            pass

        class SlowTransfer(Transfer):
            pass

        class ElevatorPathway(Pathway):
            pass

        class StairsPathway(Pathway):
            pass

        class EscalatorPathway(Pathway):
            pass

        class Walkway(Pathway):
            pass

        # Composite (DL) concepts
        class AccessibleStop(Stop):
            pass

        # Object properties
        class hasStop(ObjectProperty):
            domain = [Trip]
            range = [Stop]

        class isStopOf(ObjectProperty):
            domain = [Stop]
            range = [Trip]
            inverse_property = hasStop

        class hasTrip(ObjectProperty):
            domain = [Route]
            range = [Trip]

        class belongsToRoute(ObjectProperty):
            domain = [Trip]
            range = [Route]
            inverse_property = hasTrip  # inverse

        class fromStop(ObjectProperty):
            domain = [Transfer]
            range = [Stop]

        class toStop(ObjectProperty):
            domain = [Transfer]
            range = [Stop]


        # Property hierarchy (subproperty)
        class connectsTransportElement(ObjectProperty):
            pass

        class connectsStop(ObjectProperty):
            domain = [Pathway]
            range = [Stop]

        connectsStop.is_a.append(connectsTransportElement)

        # Transitive relation between stops
        class connectedTo(ObjectProperty, TransitiveProperty):
            domain = [Stop]
            range = [Stop]

        # Data properties
        class stopName(DataProperty, FunctionalProperty):
            domain = [Stop]
            range = [str]

        class locationType(DataProperty, FunctionalProperty):
            domain = [Stop]
            range = [int]

        class routeType(DataProperty, FunctionalProperty):
            domain = [Route]
            range = [int]

        class routeShortName(DataProperty, FunctionalProperty):
            domain = [Route]
            range = [str]

        class tripHeadsign(DataProperty, FunctionalProperty):
            domain = [Trip]
            range = [str]

        class wheelchairAccessible(DataProperty, FunctionalProperty):
            domain = [Trip]
            range = [int]

        class pathwayMode(DataProperty, FunctionalProperty):
            domain = [Pathway]
            range = [int]

        class isBidirectional(DataProperty, FunctionalProperty):
            domain = [Pathway]
            range = [int]

        class minTransferTime(DataProperty, FunctionalProperty):
            domain = [Transfer]
            range = [int]

        #DL (Description Logic) composite concepts
        # TramRoute ≡ Route ⊓ (routeType = 0)
        TramRoute.equivalent_to = [
            Route & routeType.value(0)
        ]

        # TrolleyRoute ≡ Route ⊓ (routeType = 3)
        TrolleyRoute.equivalent_to = [
            Route & routeType.value(3)
        ]

        # BusRoute ≡ Route ⊓ (routeType = 11)
        BusRoute.equivalent_to = [
            Route & routeType.value(11)
        ]

        # AccessibleStop ≡ Stop ⊓ (∃ connectsStop.ElevatorPathway)   (EXISTS + AND)
        AccessibleStop.equivalent_to = [Stop & connectsStop.some(ElevatorPathway)]

        # WheelchairFriendlyTrip ≡ Trip ⊓ (wheelchairAccessible = 1)
        WheelchairFriendlyTrip.equivalent_to = [Trip & wheelchairAccessible.value(1)]

        # StairsPathway ≡ Pathway ⊓ (pathwayMode = 1)
        StairsPathway.equivalent_to = [
            Pathway & pathwayMode.value(1)
        ]

        # EscalatorPathway ≡ Pathway ⊓ (pathwayMode = 5)
        EscalatorPathway.equivalent_to = [
            Pathway & pathwayMode.value(5)
        ]

        # Walkway ≡ Pathway ⊓ (pathwayMode = 2)
        Walkway.equivalent_to = [
            Pathway & pathwayMode.value(2)
        ]

        # FastTransfer ≡ Transfer ⊓ (minTransferTime ≤ 392) (the average transfer time)
        FastTransfer.equivalent_to = [
            Transfer & minTransferTime.max(300)
        ]

        # SlowTransfer ≡ Transfer ⊓ (minTransferTime > 391)
        SlowTransfer.equivalent_to = [
            Transfer & minTransferTime.min(301)
        ]
 
    # Create Individuals from CSV
    # Stops
    stop_by_id: dict[str, Thing] = {}
    for _, row in stops_df.iterrows():
        sid = _safe_str(row.get("stop_id"))
        if not sid:
            continue

        s = onto.Stop(f"stop_{sid}")
        stop_by_id[sid] = s

        nm = _safe_str(row.get("stop_name"))
        if nm:
            s.stopName = nm

        lt = _safe_int(row.get("location_type"))
        if lt is not None:
            s.locationType = lt

    # Routes
    route_by_id: dict[str, Thing] = {}
    for _, row in routes_df.iterrows():
        rid = _safe_str(row.get("route_id"))
        if not rid:
            continue

        r = onto.Route(f"route_{rid}")
        route_by_id[rid] = r

        rsn = _safe_str(row.get("route_short_name"))
        if rsn:
            r.routeShortName = rsn

        rtype = _safe_int(row.get("route_type"))
        if rtype is not None:
            r.routeType = rtype

    # Trips
    trip_by_id: dict[str, Thing] = {}
    trips_df2 = trips_df[trips_df["route_id"].astype(str).isin(route_by_id.keys())].copy()
    for _, row in trips_df2.iterrows():
        tid = _safe_str(row.get("trip_id"))
        rid = _safe_str(row.get("route_id"))
        if not tid or rid not in route_by_id:
            continue

        t = onto.Trip(f"trip_{tid}")
        trip_by_id[tid] = t

        # link Trip -> Route (inverse of hasTrip)
        t.belongsToRoute.append(route_by_id[rid])

        hs = _safe_str(row.get("trip_headsign"))
        if hs:
            t.tripHeadsign = hs

        wa = _safe_int(row.get("wheelchair_accessible"))
        if wa is not None:
            t.wheelchairAccessible = wa

    # StopTimes: connect Trips and Stops
    stop_times_df2 = stop_times_df[
        stop_times_df["trip_id"].astype(str).isin(trip_by_id.keys())
        & stop_times_df["stop_id"].astype(str).isin(stop_by_id.keys())
        ].copy()

    for _, row in stop_times_df2.iterrows():
        tid = _safe_str(row.get("trip_id"))
        sid = _safe_str(row.get("stop_id"))

        if not tid or not sid:
            continue

        trip = trip_by_id[tid]
        stop = stop_by_id[sid]

        trip.hasStop.append(stop)

    # Transfers
    # Create transfers only if we have both stops in our stop sample (keeps ontology consistent)
    transfers_df2 = transfers_df[
        transfers_df["from_stop_id"].astype(str).isin(stop_by_id.keys())
        & transfers_df["to_stop_id"].astype(str).isin(stop_by_id.keys())
    ].copy()

    for i, row in transfers_df2.iterrows():
        fs = _safe_str(row.get("from_stop_id"))
        ts = _safe_str(row.get("to_stop_id"))
        if not fs or not ts:
            continue

        tr = onto.Transfer(f"transfer_{fs}_{ts}_{i}")
        tr.fromStop.append(stop_by_id[fs])
        tr.toStop.append(stop_by_id[ts])

        mtt = _safe_int(row.get("min_transfer_time"))
        if mtt is not None:
            tr.minTransferTime = mtt

        # Connect stops for reachability (transitive connectedTo)
        stop_by_id[fs].connectedTo.append(stop_by_id[ts])

    # Pathways
    # Create pathways only if both stops exist
    pathways_df2 = pathways_df[
        pathways_df["from_stop_id"].astype(str).isin(stop_by_id.keys())
        & pathways_df["to_stop_id"].astype(str).isin(stop_by_id.keys())
    ].copy()

    for _, row in pathways_df2.iterrows():
        pid = _safe_str(row.get("pathway_id"))
        fs = _safe_str(row.get("from_stop_id"))
        ts = _safe_str(row.get("to_stop_id"))
        if not pid or not fs or not ts:
            continue

        p = onto.Pathway(f"pathway_{pid}")

        # link pathway -> stops
        p.connectsStop.append(stop_by_id[fs])
        p.connectsStop.append(stop_by_id[ts])

        pm = _safe_int(row.get("pathway_mode"))
        if pm is not None:
            p.pathwayMode = pm

        bi = _safe_int(row.get("is_bidirectional"))
        if bi is not None:
            p.isBidirectional = bi

        # also connect stops directly for reachability
        stop_by_id[fs].connectedTo.append(stop_by_id[ts])
        if bi == 1:
            stop_by_id[ts].connectedTo.append(stop_by_id[fs])

    sync_reasoner()

    onto.save(file=str(OUT_FILE), format="rdfxml")
    print(f"Saved ontology to: {OUT_FILE}")
    print(f"Counts: Stops={len(stop_by_id)}, Routes={len(route_by_id)}, Trips={len(trip_by_id)}")


if __name__ == "__main__":
    main()
