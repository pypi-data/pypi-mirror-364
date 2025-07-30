#include "../api/mipsolver_c_api.h"
#include <iostream>
#include <vector>

int main() {
    std::cout << "=== MIPSolver C++ API Example ===" << std::endl;
    
    // 1. Create a problem
    MIPSolver_ProblemHandle problem = MIPSolver_CreateProblem("cpp_example", MIPSOLVER_OBJ_MAXIMIZE);
    if (!problem) {
        std::cerr << "Failed to create problem!" << std::endl;
        return -1;
    }
    
    // 2. Add variables
    // Maximize: x + 2*y
    // Subject to: x + y <= 10, x >= 0, y >= 0, x and y are integers
    
    int x_idx = MIPSolver_AddVariable(problem, "x", MIPSOLVER_VAR_INTEGER);
    int y_idx = MIPSolver_AddVariable(problem, "y", MIPSOLVER_VAR_INTEGER);
    
    std::cout << "Added variables: x (index " << x_idx << "), y (index " << y_idx << ")" << std::endl;
    
    // 3. Set variable bounds
    MIPSolver_SetVariableBounds(problem, x_idx, 0.0, 1000.0);  // x >= 0
    MIPSolver_SetVariableBounds(problem, y_idx, 0.0, 1000.0);  // y >= 0
    
    // 4. Set objective coefficients
    MIPSolver_SetObjectiveCoefficient(problem, x_idx, 1.0);   // coefficient for x
    MIPSolver_SetObjectiveCoefficient(problem, y_idx, 2.0);   // coefficient for y
    
    // 5. Add constraint: x + y <= 10
    int constraint_idx = MIPSolver_AddConstraint(problem, "capacity", 1, 10.0);  // 1 = LESS_EQUAL
    MIPSolver_AddConstraintCoefficient(problem, constraint_idx, x_idx, 1.0);  // coefficient for x
    MIPSolver_AddConstraintCoefficient(problem, constraint_idx, y_idx, 1.0);  // coefficient for y
    
    std::cout << "Problem setup complete!" << std::endl;
    
    // 6. Solve the problem
    std::cout << "Solving..." << std::endl;
    MIPSolver_SolutionHandle solution = MIPSolver_Solve(problem);
    
    if (!solution) {
        std::cerr << "Failed to solve problem!" << std::endl;
        MIPSolver_DestroyProblem(problem);
        return -1;
    }
    
    // 7. Get and display results
    MIPSolver_SolutionStatus status = MIPSolver_GetStatus(solution);
    double objective_value = MIPSolver_GetObjectiveValue(solution);
    int num_vars = MIPSolver_GetSolutionNumVars(solution);
    
    std::cout << "\n=== Results ===" << std::endl;
    std::cout << "Status: ";
    switch (status) {
        case MIPSOLVER_STATUS_OPTIMAL:
            std::cout << "Optimal" << std::endl;
            break;
        case MIPSOLVER_STATUS_INFEASIBLE:
            std::cout << "Infeasible" << std::endl;
            break;
        default:
            std::cout << "Unknown (" << status << ")" << std::endl;
    }
    
    std::cout << "Objective Value: " << objective_value << std::endl;
    std::cout << "Number of Variables: " << num_vars << std::endl;
    
    // Get variable values
    if (status == MIPSOLVER_STATUS_OPTIMAL && num_vars > 0) {
        std::vector<double> values(num_vars);
        MIPSolver_GetVariableValues(solution, values.data());
        
        std::cout << "Variable Values:" << std::endl;
        for (int i = 0; i < num_vars; ++i) {
            char var_name = (i == 0) ? 'x' : 'y';
            std::cout << "  " << var_name << " = " << values[i] << std::endl;
        }
    }
    
    // 8. Clean up
    MIPSolver_DestroySolution(solution);
    MIPSolver_DestroyProblem(problem);
    
    std::cout << "\nC++ API example completed successfully!" << std::endl;
    return 0;
}
