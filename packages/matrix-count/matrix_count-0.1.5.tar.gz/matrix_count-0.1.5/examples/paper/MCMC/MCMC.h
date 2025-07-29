#ifndef MCMC_H
#define MCMC_H

#include <vector>
#include <unordered_set>
#include <utility>
#include <string>

class MCMCSampler {
public:
    MCMCSampler(const std::string& filename);
    void run(int num_steps);
    const std::vector<std::unordered_set<int>>& get_graph() const;

private:
    std::vector<std::unordered_set<int>> graph;
    std::vector<int> degree_sequence;
    std::vector<std::pair<int, int>> edges;
    void initialize_graph_from_file(const std::string& filename);
    bool double_edge_swap();
};

#endif // MCMC_H
