#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <cmath>

// Define data structures
struct Email {
    std::string MetadataFrom;
    std::string MetadataTo;
    std::string RawText;
};

struct Alias {
    std::string Alias;
    int PersonId;
};

struct Person {
    int Id;
    std::string Name;
};

struct Edge {
    std::string sender;
    std::string receiver;
    int weight;
};

// Function to unify names and aliases
std::string unifyName(const std::string& name, const std::unordered_map<std::string, int>& aliasMapping, const std::unordered_map<int, std::string>& personMapping) {
    std::string unifiedName = name;
    std::transform(unifiedName.begin(), unifiedName.end(), unifiedName.begin(), ::tolower);
    size_t atPos = unifiedName.find('@');
    if (atPos != std::string::npos) {
        unifiedName = unifiedName.substr(0, atPos);
    }
    auto aliasIt = aliasMapping.find(unifiedName);
    if (aliasIt != aliasMapping.end()) {
        unifiedName = personMapping.at(aliasIt->second);
    }
    return unifiedName;
}

// Function to calculate PageRank
std::map<std::string, double> calculatePageRank(const std::vector<Edge>& edges) {
    std::map<std::string, double> pageRank;
    std::map<std::string, double> newPageRank;
    const double dampingFactor = 0.85;
    const double initialRank = 1.0 / edges.size();

    // Initialize PageRank values
    for (const Edge& edge : edges) {
        pageRank[edge.sender] = initialRank;
        pageRank[edge.receiver] = initialRank;
    }

    // Perform PageRank iterations
    for (int iteration = 0; iteration < 10; ++iteration) {
        for (const Edge& edge : edges) {
            newPageRank[edge.receiver] += dampingFactor * pageRank[edge.sender] / edges.size();
        }
        pageRank = newPageRank;
        newPageRank.clear();
    }
    return pageRank;
}

int main() {
    // Load the emails dataset
    std::ifstream emailsFile("Emails.csv");
    std::vector<Email> emails;
    // Read emails data into 'emails' vector

    // Load the aliases dataset
    std::ifstream aliasesFile("Aliases.csv");
    std::vector<Alias> aliases;
    // Read aliases data into 'aliases' vector

    // Load the persons dataset
    std::ifstream personsFile("Persons.csv");
    std::vector<Person> persons;
    // Read persons data into 'persons' vector

    // Create alias and person mappings
    std::unordered_map<std::string, int> aliasMapping;
    for (const Alias& alias : aliases) {
        aliasMapping[alias.Alias] = alias.PersonId;
    }

    std::unordered_map<int, std::string> personMapping;
    for (const Person& person : persons) {
        personMapping[person.Id] = person.Name;
    }

    // Create a vector of edges
    std::vector<Edge> edges;
    for (const Email& email : emails) {
        std::string sender = unifyName(email.MetadataFrom, aliasMapping, personMapping);
        std::string receiver = unifyName(email.MetadataTo, aliasMapping, personMapping);
        bool edgeFound = false;
        for (Edge& edge : edges) {
            if (edge.sender == sender && edge.receiver == receiver) {
                edge.weight++;
                edgeFound = true;
                break;
            }
        }
        if (!edgeFound) {
            edges.push_back({sender, receiver, 1});
        }
    }

    // Calculate PageRank
    std::map<std::string, double> pageRank = calculatePageRank(edges);

    // Output PageRank results
    for (const auto& pair : pageRank) {
        std::cout << "Node: " << pair.first << ", PageRank: " << pair.second << std::endl;
    }

    return 0;
}

