#include "../src/core.h"
#include "../src/branch_bound_solver.h"
#include "../src/solution.h"
#include <iostream>

int main() {
    std::cout << "=== MIPSolver C++ Direct API Example ===" << std::endl;
    
    try {
        // 1. Create a problem using the direct C++ API
        // Maximize: x + 2*y
        // Subject to: x + y <= 10, x >= 0, y >= 0, x and y are integers
        
        MIPSolver::Problem problem("cpp_direct_example", MIPSolver::ObjectiveType::MAXIMIZE);
        
        // 2. Add variables
        int x_idx = problem.addVariable("x", MIPSolver::VariableType::INTEGER);
        int y_idx = problem.addVariable("y", MIPSolver::VariableType::INTEGER);
        
        std::cout << "Added variables: x (index " << x_idx << "), y (index " << y_idx << ")" << std::endl;
        
        // 3. Set variable bounds
        problem.getVariable(x_idx).setBounds(0.0, 1000.0);  // x >= 0
        problem.getVariable(y_idx).setBounds(0.0, 1000.0);  // y >= 0
        
        // 4. Set objective coefficients
        problem.setObjectiveCoefficient(x_idx, 1.0);   // coefficient for x
        problem.setObjectiveCoefficient(y_idx, 2.0);   // coefficient for y
        
        // 5. Add constraint: x + y <= 10
        int constraint_idx = problem.addConstraint("capacity", MIPSolver::ConstraintType::LESS_EQUAL, 10.0);
        problem.getConstraint(constraint_idx).addVariable(x_idx, 1.0);  // coefficient for x
        problem.getConstraint(constraint_idx).addVariable(y_idx, 1.0);  // coefficient for y
        
        std::cout << "Problem setup complete!" << std::endl;
        
        // Print problem statistics
        problem.printStatistics();
        
        // 6. Create and configure solver
        MIPSolver::BranchBoundSolver solver;
        solver.setVerbose(true);  // Enable detailed output
        
        // 7. Solve the problem
        std::cout << "\nSolving..." << std::endl;
        MIPSolver::Solution solution = solver.solve(problem);
        
        // 8. Display results
        std::cout << "\n=== Results ===" << std::endl;
        solution.print();
        
        // Get specific values
        if (solution.getStatus() == MIPSolver::Solution::Status::OPTIMAL) {
            std::cout << "\nDetailed Solution:" << std::endl;
            std::cout << "x = " << solution.getValue(x_idx) << std::endl;
            std::cout << "y = " << solution.getValue(y_idx) << std::endl;
            std::cout << "Objective = " << solution.getObjectiveValue() << std::endl;
            
            // Verify the solution
            double constraint_lhs = solution.getValue(x_idx) + solution.getValue(y_idx);
            std::cout << "Constraint verification: " << constraint_lhs << " <= 10 ? " 
                      << (constraint_lhs <= 10.001 ? "✓" : "✗") << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return -1;
    }
    
    std::cout << "\nC++ Direct API example completed successfully!" << std::endl;
    return 0;
}
