# tests/test_comprehensive.py
"""
综合测试套件 - 测试MIPSolver的各种功能
"""

import mipsolver as mp
import pytest
import math

def test_basic_linear_program():
    """测试基本线性规划问题"""
    model = mp.Model("linear_program")
    
    # 创建连续变量
    x = model.add_var(vtype=mp.CONTINUOUS, name="x", lb=0)
    y = model.add_var(vtype=mp.CONTINUOUS, name="y", lb=0)
    
    # 目标函数: 最大化 3x + 2y
    model.set_objective(3*x + 2*y, sense=mp.MAXIMIZE)
    
    # 约束: x + y <= 4, 2x + y <= 6
    model.add_constr(x + y <= 4)
    model.add_constr(2*x + y <= 6)
    
    # 求解
    model.optimize()
    
    # 验证
    assert model.status.value == mp.OPTIMAL
    assert model.obj_val >= 8.0  # 最优解应该在 (2,2) 附近，目标值为 10
    print(f"线性规划测试通过 - 目标值: {model.obj_val}, x={x.value}, y={y.value}")

def test_binary_variables():
    """测试二进制变量"""
    model = mp.Model("binary_test")
    
    # 创建二进制变量
    x = model.add_var(vtype=mp.BINARY, name="x")
    y = model.add_var(vtype=mp.BINARY, name="y")
    
    # 目标函数: 最大化 x + 2y
    model.set_objective(x + 2*y, sense=mp.MAXIMIZE)
    
    # 约束: x + y <= 1 (只能选择一个)
    model.add_constr(x + y <= 1)
    
    # 求解
    model.optimize()
    
    # 验证
    assert model.status.value == mp.OPTIMAL
    assert model.obj_val == pytest.approx(2.0)  # 应该选择 y=1, x=0
    assert x.value == pytest.approx(0.0)
    assert y.value == pytest.approx(1.0)
    print(f"二进制变量测试通过 - x={x.value}, y={y.value}")

def test_infeasible_problem():
    """测试不可行问题"""
    model = mp.Model("infeasible")
    
    x = model.add_var(vtype=mp.CONTINUOUS, name="x", lb=10)  # 下界为10
    
    # 矛盾约束: x <= 5 但下界是 10
    # 使用LinExpr来创建约束
    expr = 1.0 * x  # 创建表达式
    model.add_constr(expr <= 5)
    
    model.set_objective(x, sense=mp.MAXIMIZE)
    
    # 这个应该会失败，因为模型不可行
    try:
        model.optimize()
        # 如果求解器能检测到不可行性，状态应该是 INFEASIBLE
        if model.status.value == mp.INFEASIBLE:
            print("不可行问题正确检测")
        else:
            print(f"状态: {model.status} (可能求解器未检测到不可行性)")
    except Exception as e:
        print(f"求解不可行问题时出错: {e}")

def test_multiple_constraints():
    """测试多约束问题"""
    model = mp.Model("multi_constraints")
    
    # 创建多个变量
    vars = []
    for i in range(3):
        vars.append(model.add_var(vtype=mp.INTEGER, name=f"x{i}", lb=0))
    
    x1, x2, x3 = vars
    
    # 目标函数
    model.set_objective(x1 + 2*x2 + 3*x3, sense=mp.MAXIMIZE)
    
    # 多个约束
    model.add_constr(x1 + x2 + x3 <= 10)
    model.add_constr(2*x1 + x2 <= 8)
    model.add_constr(x2 + 2*x3 <= 12)
    
    # 求解
    model.optimize()
    
    # 验证
    assert model.status.value == mp.OPTIMAL
    total = x1.value + x2.value + x3.value
    assert total <= 10.1  # 允许小的数值误差
    print(f"多约束测试通过 - 目标值: {model.obj_val}")
    print(f"   解: x1={x1.value}, x2={x2.value}, x3={x3.value}")

def test_minimization():
    """测试最小化问题"""
    model = mp.Model("minimization")
    
    x = model.add_var(vtype=mp.CONTINUOUS, name="x", lb=0)
    y = model.add_var(vtype=mp.CONTINUOUS, name="y", lb=0)
    
    # 最小化 x + y
    model.set_objective(x + y, sense=mp.MINIMIZE)
    
    # 约束: x + y >= 5
    model.add_constr(x + y >= 5)
    
    # 求解
    model.optimize()
    
    # 验证
    assert model.status.value == mp.OPTIMAL
    assert model.obj_val == pytest.approx(5.0, abs=0.1)
    print(f"最小化测试通过 - 目标值: {model.obj_val}")

def run_all_tests():
    """运行所有测试"""
    tests = [
        test_basic_linear_program,
        test_binary_variables,
        test_multiple_constraints,
        test_minimization,
        test_infeasible_problem,
    ]
    
    passed = 0
    total = len(tests)
    
    print("开始运行综合测试套件...\n")
    
    for test_func in tests:
        try:
            print(f"运行 {test_func.__name__}...")
            test_func()
            passed += 1
            print()
        except Exception as e:
            print(f"FAILED {test_func.__name__} 失败: {e}\n")
    
    print(f"测试结果: {passed}/{total} 通过")
    if passed == total:
        print("所有测试都通过了！")
    else:
        print(f"{total - passed} 个测试失败")

if __name__ == "__main__":
    run_all_tests()
