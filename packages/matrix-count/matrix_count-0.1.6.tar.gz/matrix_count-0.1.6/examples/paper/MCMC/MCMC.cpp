#include "MCMC.h"
#include <algorithm>
#include <fstream>
#include <random>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iostream>

MCMCSampler::MCMCSampler(const std::string& filename) {
    initialize_graph_from_file(filename);
}

void MCMCSampler::initialize_graph_from_file(const std::string& filename) {
    std::ifstream infile(filename);
    if (!infile) {
        throw std::runtime_error("Could not open file");
    }

    int u, v;
    int max_node = -1;
    std::unordered_map<int, int> degree_count;
    std::vector<std::pair<int, int>> temp_edges;

    while (infile >> u >> v) {
        if (u != v) {
            temp_edges.emplace_back(u, v);
            degree_count[u]++;
            degree_count[v]++;
            max_node = std::max({max_node, u, v});
        }
    }

    graph.resize(max_node + 1);
    for (const auto& edge : temp_edges) {
        int u = edge.first;
        int v = edge.second;
        graph[u].insert(v);
        graph[v].insert(u);
        edges.emplace_back(u, v);
    }

    degree_sequence.resize(graph.size());
    for (const auto& [node, degree] : degree_count) {
        degree_sequence[node] = degree;
    }
}

bool MCMCSampler::double_edge_swap() {
    std::random_device rd;
    std::mt19937 rng(rd());
    std::uniform_int_distribution<int> dist(0, edges.size() - 1);

    int idx1 = dist(rng);
    int idx2 = dist(rng);

    auto [u1, v1] = edges[idx1];
    auto [u2, v2] = edges[idx2];

    // Ensure no self-loops and no multiple edges
    if (u1 == u2 || u1 == v2 || v1 == u2 || v1 == v2 || graph[u1].count(v2) || graph[u2].count(v1)) {
        return false;
    }

    // Perform the swap
    graph[u1].erase(v1);
    graph[v1].erase(u1);
    graph[u2].erase(v2);
    graph[v2].erase(u2);

    graph[u1].insert(v2);
    graph[v2].insert(u1);
    graph[u2].insert(v1);
    graph[v1].insert(u2);

    edges[idx1] = {u1, v2};
    edges[idx2] = {u2, v1};

    return true;
}

void MCMCSampler::run(int num_steps) {
    for (int i = 0; i < num_steps; ++i) {
        double_edge_swap();
    }
}

const std::vector<std::unordered_set<int>>& MCMCSampler::get_graph() const {
    return graph;
}
