# MIPSolver C++ API 使用指南

MIPSolver提供了三种C++接口使用方式：

## 1. Python API（推荐）

最简单和推荐的使用方式：

```python
import mipsolver as mp

model = mp.Model("example")
x = model.add_var(vtype=mp.INTEGER, name="x", lb=0)
y = model.add_var(vtype=mp.INTEGER, name="y", lb=0)
model.add_constr(x + y <= 10)
model.set_objective(x + 2 * y, sense=mp.MAXIMIZE)
model.optimize()

print(f"最优值: {model.obj_val}")  # 15.0
print(f"解: x={x.value}, y={y.value}")  # x=5.0, y=5.0
```

## 2. C++ 直接API

直接使用C++核心类：

```cpp
#include "src/core.h"
#include "src/branch_bound_solver.h"

int main() {
    // 创建问题
    MIPSolver::Problem problem("example", MIPSolver::ObjectiveType::MAXIMIZE);
    
    // 添加变量
    int x_idx = problem.addVariable("x", MIPSolver::VariableType::INTEGER);
    int y_idx = problem.addVariable("y", MIPSolver::VariableType::INTEGER);
    
    // 设置变量界限
    problem.getVariable(x_idx).setBounds(0.0, 1000.0);
    problem.getVariable(y_idx).setBounds(0.0, 1000.0);
    
    // 设置目标函数系数
    problem.setObjectiveCoefficient(x_idx, 1.0);   // x的系数
    problem.setObjectiveCoefficient(y_idx, 2.0);   // y的系数
    
    // 添加约束: x + y <= 10
    int c_idx = problem.addConstraint("capacity", 
                                     MIPSolver::ConstraintType::LESS_EQUAL, 10.0);
    problem.getConstraint(c_idx).addVariable(x_idx, 1.0);
    problem.getConstraint(c_idx).addVariable(y_idx, 1.0);
    
    // 求解
    MIPSolver::BranchBoundSolver solver;
    MIPSolver::Solution solution = solver.solve(problem);
    
    // 获取结果
    if (solution.getStatus() == MIPSolver::Solution::Status::OPTIMAL) {
        std::cout << "最优值: " << solution.getObjectiveValue() << std::endl;
        std::cout << "x = " << solution.getValue(x_idx) << std::endl;
        std::cout << "y = " << solution.getValue(y_idx) << std::endl;
    }
    
    return 0;
}
```

## 3. C API

提供C兼容的接口：

```cpp
#include "api/mipsolver_c_api.h"

int main() {
    // 创建问题
    MIPSolver_ProblemHandle problem = 
        MIPSolver_CreateProblem("example", MIPSOLVER_OBJ_MAXIMIZE);
    
    // 添加变量
    int x_idx = MIPSolver_AddVariable(problem, "x", MIPSOLVER_VAR_INTEGER);
    int y_idx = MIPSolver_AddVariable(problem, "y", MIPSOLVER_VAR_INTEGER);
    
    // 设置变量界限
    MIPSolver_SetVariableBounds(problem, x_idx, 0.0, 1000.0);
    MIPSolver_SetVariableBounds(problem, y_idx, 0.0, 1000.0);
    
    // 设置目标函数
    MIPSolver_SetObjectiveCoefficient(problem, x_idx, 1.0);
    MIPSolver_SetObjectiveCoefficient(problem, y_idx, 2.0);
    
    // 添加约束
    int c_idx = MIPSolver_AddConstraint(problem, "capacity", 1, 10.0); // 1=LESS_EQUAL
    MIPSolver_AddConstraintCoefficient(problem, c_idx, x_idx, 1.0);
    MIPSolver_AddConstraintCoefficient(problem, c_idx, y_idx, 1.0);
    
    // 求解
    MIPSolver_SolutionHandle solution = MIPSolver_Solve(problem);
    
    // 获取结果
    MIPSolver_SolutionStatus status = MIPSolver_GetStatus(solution);
    if (status == MIPSOLVER_STATUS_OPTIMAL) {
        double obj_val = MIPSolver_GetObjectiveValue(solution);
        
        std::vector<double> values(2);
        MIPSolver_GetVariableValues(solution, values.data());
        
        std::cout << "最优值: " << obj_val << std::endl;
        std::cout << "x = " << values[0] << ", y = " << values[1] << std::endl;
    }
    
    // 清理资源
    MIPSolver_DestroySolution(solution);
    MIPSolver_DestroyProblem(problem);
    
    return 0;
}
```

## 构建说明

### 构建C++示例：

```bash
cd examples
./build_examples.sh
```

### 运行示例：

```bash
# C++直接API示例
./build/test_cpp_direct

# C API示例  
./build/test_cpp_api
```

## API 特性对比

| 特性 | Python API | C++ 直接API | C API |
|------|------------|-------------|-------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 类型安全 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 内存管理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 跨语言 | Python only | C++ only | 多语言 |

## 推荐使用场景

- **Python API**: 快速原型开发、数据科学、教学
- **C++ 直接API**: 高性能应用、C++项目集成
- **C API**: 多语言绑定、系统级集成、DLL/共享库

## 注意事项

1. **求解器限制**: 当前使用简化的启发式求解器，可能不会找到全局最优解
2. **内存管理**: C API需要手动管理内存（调用Destroy函数）
3. **线程安全**: 当前实现不是线程安全的
4. **错误处理**: C++直接API使用异常，C API使用返回值

## 扩展和定制

MIPSolver的模块化架构允许你：

- 实现自定义求解算法（继承`SolverInterface`）
- 添加新的约束类型
- 集成第三方求解器（如CPLEX、Gurobi）
- 扩展变量类型支持
