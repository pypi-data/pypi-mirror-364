#include "helpers.h"
#include <queue>
#include <vector>
#include <unordered_set>

// ...existing code...

int shortest_path_length(const std::vector<std::unordered_set<int>>& graph, int start, int end) {
    if (start == end) {
        return 0;
    }

    std::vector<int> distances(graph.size(), -1);
    std::queue<int> q;

    distances[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int node = q.front();
        q.pop();

        for (int neighbor : graph[node]) {
            if (distances[neighbor] == -1) {
                distances[neighbor] = distances[node] + 1;
                if (neighbor == end) {
                    return distances[neighbor];
                }
                q.push(neighbor);
            }
        }
    }

    return -1; // Return -1 if there is no path between start and end
}
