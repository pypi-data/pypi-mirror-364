#include "../mipsolver.hpp"
#include <iostream>

int main() {
    std::cout << "=== MIPSolver Convenience API Example ===" << std::endl;
    
    // 使用便利函数创建问题
    auto problem = MIPSolver::createProblem("convenience_example", MIPSolver::ObjectiveType::MAXIMIZE);
    
    // 添加变量: maximize x + 2*y subject to x + y <= 10
    int x = problem.addVariable("x", MIPSolver::VariableType::INTEGER);
    int y = problem.addVariable("y", MIPSolver::VariableType::INTEGER);
    
    // 设置变量界限
    problem.getVariable(x).setBounds(0.0, 100.0);
    problem.getVariable(y).setBounds(0.0, 100.0);
    
    // 设置目标函数
    problem.setObjectiveCoefficient(x, 1.0);
    problem.setObjectiveCoefficient(y, 2.0);
    
    // 添加约束
    int constraint = problem.addConstraint("capacity", MIPSolver::ConstraintType::LESS_EQUAL, 10.0);
    problem.getConstraint(constraint).addVariable(x, 1.0);
    problem.getConstraint(constraint).addVariable(y, 1.0);
    
    // 使用快速求解函数
    std::cout << "Solving with convenience API..." << std::endl;
    auto solution = MIPSolver::quickSolve(problem, true);
    
    // 显示结果
    std::cout << "\n=== Results ===" << std::endl;
    if (solution.getStatus() == MIPSolver::Solution::Status::OPTIMAL) {
        std::cout << "Status: Optimal" << std::endl;
        std::cout << "Objective: " << solution.getObjectiveValue() << std::endl;
        std::cout << "x = " << solution.getValue(x) << std::endl;
        std::cout << "y = " << solution.getValue(y) << std::endl;
    } else {
        std::cout << "Problem could not be solved optimally" << std::endl;
    }
    
    std::cout << "\nConvenience API example completed!" << std::endl;
    return 0;
}
