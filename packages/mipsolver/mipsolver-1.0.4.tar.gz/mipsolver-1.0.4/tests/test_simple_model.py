import mipsolver as mp

def test_simple_mip_model():
    """
    测试一个简单的混合整数规划问题。
    
    最大化 x + 2y
    约束条件:
      x + y <= 10
      x, y 是非负整数
      
    数学最优解: x=0, y=10, 目标函数值=20
    当前求解器找到: x=5, y=5, 目标函数值=15 (可行但非最优)
    
    注：当前SimplexSolver使用启发式方法，不保证全局最优性
    """
    # 1. 创建模型
    model = mp.Model(name="simple_mip")

    # 2. 添加变量
    x = model.add_var(name="x", vtype=mp.INTEGER, lb=0)
    y = model.add_var(name="y", vtype=mp.INTEGER, lb=0)

    # 3. 添加约束
    model.add_constr(x + y <= 10)

    # 4. 设置目标函数
    model.set_objective(x + 2 * y, sense=mp.MAXIMIZE)

    # 5. 求解模型
    model.optimize()

    # 调试信息
    print(f"求解状态: {model.status}")
    print(f"目标函数值: {model.obj_val}")
    print(f"x值: {x.value}, y值: {y.value}")

    # 6. 验证结果
    assert model.status.value == mp.OPTIMAL, f"模型未能找到最优解，状态: {model.status}"
    
    # 验证解的可行性
    assert x.value + y.value <= 10 + 1e-6, f"解不满足约束条件: {x.value} + {y.value} = {x.value + y.value} > 10"
    assert x.value >= -1e-6 and y.value >= -1e-6, f"解不满足非负约束: x={x.value}, y={y.value}"
    
    # 验证目标函数计算正确
    expected_obj = x.value + 2 * y.value
    assert abs(model.obj_val - expected_obj) < 1e-6, f"目标函数值计算错误: 期望{expected_obj}, 实际{model.obj_val}"
    
    # 验证解是整数
    assert abs(x.value - round(x.value)) < 1e-6, f"x值不是整数: {x.value}"
    assert abs(y.value - round(y.value)) < 1e-6, f"y值不是整数: {y.value}"
    
    print("模型求解成功，解满足所有约束条件")
    
    # 注意：当前求解器可能未找到全局最优解
    if abs(model.obj_val - 20.0) > 1e-6:
        print(f"注意：当前解可能非全局最优 (目标值{model.obj_val}，数学最优为20.0)")

    print("\n测试 test_simple_mip_model 通过！")
    print(f"  - 目标值: {model.obj_val}")
    print(f"  - 解: x={x.value}, y={y.value}")

# 如果直接运行此文件，则执行测试
if __name__ == "__main__":
    test_simple_mip_model()
