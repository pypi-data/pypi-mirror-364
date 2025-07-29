# Python script that uses our package to generate a configuration model graph

import matrix_count

# Distribute with a power law
# test_margin = []
# for i in range(100):
#     test_margin.append(int(30*((i+40)/50)**-2))

test_margin = [3,3,2,2,2,2]

if sum(test_margin) % 2 == 1:
    test_margin[-1] += 1

filename = "graph.txt"
sample, entropy = matrix_count.sample_symmetric_matrix(test_margin, binary_matrix=True, seed = 0)
print(entropy)

with open(filename, "w") as f:
    for i in range(len(sample)):
        for j in range(i):
            if sample[i][j] == 1:
                f.write(f"{i} {j}\n")