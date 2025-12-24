import csv
from owlready2 import *
import pandas as pd

def read_csv(path, fn):

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:

            fn(row)
            count += 1

        print("count: ", count)

read_csv('./Data/agency.csv', print)


onto = get_ontology("http://example.org/transport.owl")

with onto:
    class Stop(Thing): pass
    class Route(Thing): pass
    class Trip(Thing): pass
    class Transfer(Thing): pass
    class Pathway(Thing): pass
    class Level(Thing): pass

    class MetroStop(Stop): pass
    class TramStop(Stop): pass
    class BusStop(Stop): pass

    class BusRoute(Route): pass
    class TramRoute(Route): pass
    class MetroRoute(Route): pass

    class LongTrip(Trip): pass
    class ShortTrip(Trip): pass

    class FastTransfer(Transfer): pass
    class SlowTransfer(Transfer): pass