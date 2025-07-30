import math
import cmath
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Math Genie Calculator")


@mcp.tool(name="add", title="加法运算", description="两个数相加")
def add(a: float, b: float) -> float:
    """加法运算

    参数:
    a: 第一个数字
    b: 第二个数字

    返回:
    两数之和
    """
    return a + b


@mcp.tool(name="subtract", title="减法运算", description="两个数相减")
def subtract(a: float, b: float) -> float:
    """减法运算

    参数:
    a: 第一个数字
    b: 第二个数字

    返回:
    两数之差 (a - b)
    """
    return a - b


@mcp.tool(name="multiply", title="乘法运算", description="两个数相乘")
def multiply(a: float, b: float) -> float:
    """乘法运算

    参数:
    a: 第一个数字
    b: 第二个数字

    返回:
    两数之积
    """
    return a * b


@mcp.tool(name="divide", title="除法运算", description="两个数相除")
def divide(a: float, b: float) -> float:
    """除法运算

    参数:
    a: 被除数
    b: 除数

    返回:
    两数之商 (a / b)

    异常:
    ValueError: 当除数为零时
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


@mcp.tool(name="sine", title="正弦函数", description="计算正弦函数")
def sin(degree: float) -> float:
    """sin函数运算

        参数:
        degree: 角度

        返回:
        正弦值

        异常:
        ValueError: 当除数为零时
        """
    angle_rad = math.radians(degree)
    return math.sin(angle_rad)


@mcp.tool(name="cos", title="余弦函数", description="计算余弦函数")
def cos(degree: float) -> float:
    """cos函数运算

        参数:
        degree: 角度

        返回:
        余弦值

        异常:
        ValueError: 当除数为零时
        """
    angle_rad = math.radians(degree)
    return math.cos(angle_rad)


@mcp.tool(name="tangent", title="正切函数", description="计算正切函数")
def tan(degree: float) -> float:
    """cos函数运算

        参数:
        degree: 角度

        返回:
        正切值

        异常:
        ValueError: 当除数为零时
        """
    angle_rad = math.radians(degree)
    return math.tan(angle_rad)


@mcp.tool(name="cotangent", title="余切函数", description="计算余切函数")
def cot(degree: float) -> float:
    """cos函数运算

        参数:
        degree: 角度

        返回:
        余切值

        异常:
        ValueError: 当除数为零时
        """
    angle_rad = math.radians(degree)
    return 1 / math.tan(angle_rad)


@mcp.tool(name="secant", title="正割函数", description="计算正割函数")
def secant(degree: float) -> float:
    """正割函数运算

    参数:
    degree: 角度

    返回:
    正割值

    异常:
    ValueError: 当除数为零时
    """
    angle_rad = math.radians(degree)
    return 1 / math.cos(angle_rad)


@mcp.tool(name="cosecant", title="余割函数", description="计算余割函数")
def cosecant(degree: float) -> float:
    """余割函数运算

    参数:
    degree: 角度

    返回:
    余割值

    异常:
    ValueError: 当除数为零时
    """
    angle_rad = math.radians(degree)
    return 1 / math.sin(angle_rad)


@mcp.tool(name="natural_log", title="自然对数", description="计算自然对数(底数为e)")
def natural_log(x: float):
    """计算自然对数(底数为e)"""
    return math.log(x)


@mcp.tool(name="common_log", title="常用对数", description="计算常用对数(底数为10)")
def common_log(x: float):
    """计算常用对数(底数为10)"""
    return math.log10(x)


@mcp.tool(name="custom_log", title="自定义对数", description="根据给定的底数计算对数")
def custom_log(x: float, base: float):
    """计算任意底数的对数"""
    return math.log(x, base)


@mcp.tool(name="math_sqrt", title="数学库平方根", description="使用Python内置的数学模块进行平方根计算")
def math_sqrt(x):
    """标准库平方根计算"""
    return math.sqrt(int(x))


@mcp.tool(name="operator_sqrt", title="指数运算符", description="使用指数运算符来计算平方根")
def operator_sqrt(x: float):
    """使用指数运算符"""
    return x ** 0.5


@mcp.tool(name="complex_sqrt", title="复数平方根", description="计算复数平方根")
def complex_sqrt(x: complex):
    """复数平方根计算"""
    return cmath.sqrt(x)


@mcp.tool(name="exponentiation", title="幂运算", description="计算幂运算，支持负整数和小数")
def exponentiation(base: float, exponent: float):
    """
    计算幂运算，支持负整数和小数
    :param base:
    :param exponent:
    :return:
    """

    if not isinstance(exponent, (int, float)):
        return "指数为整数或小数."

    if not isinstance(base, (int, float)):
        return "底数为整数或小数."

    power = 1 / exponent if exponent < 0 else exponent
    return math.pow(base, power)


@mcp.tool(name="arcsin", title="反正弦函数", description="计算反正弦函数")
def arcsin(value: float):
    """
    反正弦函数
    :param value:
    :return:
    """
    if abs(value) > 1:
        return "输入值范围是[-1, 1]."

    return math.asin(value)


@mcp.tool(name="arccos", title="反余弦函数", description="计算反余弦函数")
def arccos(value: float):
    """
    反余弦函数
    :param value:
    :return:
    """
    if abs(value) > 1:
        return "输入值范围是[-1, 1]."
    return math.acos(value)


@mcp.tool(name="arctan", title="反正切函数", description="计算反正切函数")
def arctan(value: float):
    """
    反正切函数
    :param value:
    :return:
    """

    return math.atan(value)


@mcp.tool(name="factorial_math", title="阶乘", description="求阶乘")
def factorial_math(n: int):
    """
    求阶乘
    :param n:
    :return:
    """
    if n < 0:
        return "输入值必须为正整数."
    return math.factorial(n)


if __name__ == "__main__":
    # mcp.run(transport='streamable-http', host="192.168.146.128", port=8001)
    mcp.run()
