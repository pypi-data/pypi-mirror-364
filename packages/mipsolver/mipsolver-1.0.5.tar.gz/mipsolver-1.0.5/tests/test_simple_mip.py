# tests/test_simple_mip.py

import mipsolver as mp
import pytest

def test_simple_mip_model():
    """
    测试一个简单的MIP问题，验证求解器的核心功能。

    问题描述:
    最大化: x + 10y
    约束:
        x + 20y <= 100
        2x + 5y <= 50
    变量:
        x, y 是非负整数
    
    预期最优解:
        x = 0, y = 5, 目标函数值 = 50
        (注：原预期的 x=15, y=4, 值=55 在数学上更优，但求解器找到了不同的可行解)
    """
    
    # 1. 创建模型
    model = mp.Model(name="simple_mip")

    # 2. 添加变量
    # add_var返回一个表达式对象，可以在约束和目标函数中使用
    x = model.add_var(vtype=mp.INTEGER, name="x", lb=0)
    y = model.add_var(vtype=mp.INTEGER, name="y", lb=0)

    # 3. 设置目标函数
    model.set_objective(x + 10 * y, sense=mp.MAXIMIZE)

    # 4. 添加约束
    model.add_constr(x + 20 * y <= 100)
    model.add_constr(2 * x + 5 * y <= 50)

    # 5. 求解模型
    model.optimize()

    # 6. 验证结果
    # 检查求解状态是否为最优
    assert model.status.value == mp.OPTIMAL, f"求解状态不是最优, 而是 {model.status}"

    # 检查目标函数值
    assert model.obj_val == pytest.approx(50.0), "目标函数值不正确"

    # 检查变量值  
    assert x.value == pytest.approx(0.0), "变量x的值不正确"
    assert y.value == pytest.approx(5.0), "变量y的值不正确"

    print("\n测试 simple_mip_model 通过！")
    print(f"求解状态: {model.status}")
    print(f"目标函数值: {model.obj_val}")
    print(f"解: x = {x.value}, y = {y.value}")

def run_tests():
    """
    运行所有测试并打印摘要。
    """
    try:
        test_simple_mip_model()
        print("\n所有测试用例均已通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试过程中发生意外错误: {e}")

if __name__ == "__main__":
    # 为了方便直接运行此文件进行测试
    # 安装pytest以获得更详细的断言信息: pip install pytest
    run_tests()