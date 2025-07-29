#include <iostream>
#include <vector>
#include <unordered_set>
#include <string>
#include <fstream>

#include "MCMC.h"
#include "helpers.h"

void print_graph(const std::vector<std::unordered_set<int>>& graph) {
    for (size_t i = 0; i < graph.size(); ++i) {
        std::cout << "Node " << i << ": ";
        for (int neighbor : graph[i]) {
            std::cout << neighbor << " ";
        }
        std::cout << std::endl;
    }
}

int main() {
    // Initialize MCMC sampler with graph from file
    std::string filename = "graph.txt";
    MCMCSampler sampler(filename);

    // Number of samples and steps
    int num_samples = 1000;
    int num_steps = 100;
    double total_path_length = 0.0;
    int valid_samples = 0;
    std::vector<double> path_length_history;

    for (int i = 0; i < num_samples; ++i) {
        // Run the sampler for a number of steps
        sampler.run(num_steps);

        // Get the resulting graph
        const auto& graph = sampler.get_graph();

        // Compute the shortest path length between nodes 0 and 1
        int path_length = shortest_path_length(graph, 0, 1);
        if (path_length != -1) {
            total_path_length += path_length;
            valid_samples++;
        }

        // Compute and store the average path length
        if (valid_samples > 0) {
            double average_path_length = total_path_length / valid_samples;
            path_length_history.push_back(average_path_length);
        } else {
            path_length_history.push_back(-1); // Indicate no valid paths found
        }
    }

    // Write the history of average path lengths to a CSV file
    std::ofstream csv_file("path_length_history.csv");
    csv_file << "Sample,AveragePathLength\n";
    for (size_t i = 0; i < path_length_history.size(); ++i) {
        csv_file << i + 1 << "," << path_length_history[i] << "\n";
    }
    csv_file.close();

    std::cout << "Path length history written to path_length_history.csv" << std::endl;

    return 0;
}
