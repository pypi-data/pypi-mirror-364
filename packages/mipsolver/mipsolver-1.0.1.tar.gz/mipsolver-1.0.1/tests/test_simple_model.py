import mipsolver as mp

def test_simple_mip_model():
    """
    测试一个简单的混合整数规划问题。
    
    最大化 x + 2y
    约束条件:
      x + y <= 10
      x, y 是非负整数
      
    预期解: x=0, y=10, 目标函数值=20
    """
    # 1. 创建模型
    model = mp.Model(name="simple_mip")

    # 2. 添加变量
    x = model.add_var(name="x", var_type="I", lb=0)
    y = model.add_var(name="y", var_type="I", lb=0)

    # 3. 添加约束
    model.add_constr(x + y <= 10)

    # 4. 设置目标函数
    model.set_objective(x + 2 * y, sense="max")

    # 5. 求解模型
    status = model.solve()

    # 6. 验证结果
    assert status == mp.SolutionStatus.OPTIMAL, "模型未能找到最优解"
    
    assert abs(model.get_objective_value() - 20.0) < 1e-6, "目标函数值不正确"
    
    assert abs(x.get_value() - 0.0) < 1e-6, "变量x的值不正确"
    assert abs(y.get_value() - 10.0) < 1e-6, "变量y的值不正确"

    print("\n测试 test_simple_mip_model 通过！")
    print(f"  - 目标值: {model.get_objective_value()}")
    print(f"  - 解: x={x.get_value()}, y={y.get_value()}")

# 如果直接运行此文件，则执行测试
if __name__ == "__main__":
    test_simple_mip_model()
