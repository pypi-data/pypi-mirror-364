#ifndef MIPSOLVER_HPP
#define MIPSOLVER_HPP

/**
 * @file mipsolver.hpp
 * @brief MIPSolver C++ API 主头文件
 * 
 * This header provides convenient access to all MIPSolver C++ interfaces.
 * Include this file to use MIPSolver in your C++ projects.
 * 
 * @author lytreallynb  
 * @version 1.0.3
 */

// Core MIPSolver classes
#include "src/core.h"
#include "src/solution.h"
#include "src/branch_bound_solver.h"

// C API (optional)
#ifdef MIPSOLVER_INCLUDE_C_API
#include "api/mipsolver_c_api.h"
#endif

/**
 * @namespace MIPSolver
 * @brief Main namespace for all MIPSolver C++ classes and functions
 */
namespace MIPSolver {

/**
 * @brief Convenience function to create and solve a simple problem
 * @param name Problem name
 * @param obj_type Objective type (MAXIMIZE or MINIMIZE)
 * @return Problem instance ready for variable and constraint addition
 */
inline Problem createProblem(const std::string& name, ObjectiveType obj_type = ObjectiveType::MINIMIZE) {
    return Problem(name, obj_type);
}

/**
 * @brief Convenience function to create a solver with common settings
 * @param verbose Enable verbose output
 * @param time_limit Time limit in seconds
 * @return Configured solver instance
 */
inline BranchBoundSolver createSolver(bool verbose = false, double time_limit = 3600.0) {
    BranchBoundSolver solver;
    solver.setVerbose(verbose);
    solver.setTimeLimit(time_limit);
    return solver;
}

/**
 * @brief Quick solve function for simple problems
 * @param problem Problem to solve
 * @param verbose Enable verbose output
 * @return Solution object
 */
inline Solution quickSolve(const Problem& problem, bool verbose = false) {
    auto solver = createSolver(verbose);
    return solver.solve(problem);
}

} // namespace MIPSolver

#endif // MIPSOLVER_HPP
