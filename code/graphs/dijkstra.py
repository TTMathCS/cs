import heapq

PLACES = ["Erebus Montes", "Olympus Mons", "Ascraeus Mons", "Valles Marineris", "Elysium Mons",
          "Utopia Planitia", "Gale crater", "Jezero crater", "Hellas Planitia"]
# roads between real places on Mars, with their great-circle lengths in km
ROADS = [(0, 1, 2369), (0, 4, 2016), (0, 5, 2305), (1, 2, 1740), (2, 3, 3043), (4, 6, 1879), (5, 4, 1486),
         (5, 7, 3214), (7, 6, 3782), (7, 8, 3616), (6, 8, 4122), (1, 6, 5337)]


def dijkstra(adj, src):
    """Shortest distances from src when every edge weight is >= 0, and each vertex's parent."""
    INF = float("inf")
    dist = [INF] * len(adj)
    parent = [-1] * len(adj)
    dist[src] = 0
    pq = [(0, src)]                          # (distance found so far, vertex)
    while pq:
        d, u = heapq.heappop(pq)             # the closest vertex not yet settled
        if d > dist[u]:
            continue                         # an old, longer entry: skip it
        for v, w in adj[u]:
            if d + w < dist[v]:              # relax: going through u is shorter
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))
    return dist, parent


def route(parent, t):
    out = []
    while t != -1:
        out.append(t)
        t = parent[t]
    return out[::-1]


if __name__ == "__main__":
    adj = [[] for _ in PLACES]
    for u, v, w in ROADS:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist, parent = dijkstra(adj, 0)
    for v, name in enumerate(PLACES):
        print(f"{name}: {dist[v]} km via {' > '.join(PLACES[x] for x in route(parent, v))}")
