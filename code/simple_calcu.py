#定义运算
def calculate(a, operator, b):
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        if b == 0:
            return ZeroDivisionError
        return a / b
    elif operator == '%':
        if b == 0:
            return ZeroDivisionError
        return a % b
    else:
        return "不支持的运算符"

def main():
    print("请输入表达式，例如: 2 + 3")
    print("支持运算符: + - * / %")
    print("输入 q 退出")
    
    while True:
        user_input = input(">>>").strip()
        
        if user_input.lower() == 'q':
            print("已退出计算器，再见！")
            break
        
        parts = user_input.split()
        #检查输入格式
        if len(parts) != 3:
            print("输入格式错误，标准格式：[数字 运算符 数字]，例如 2 + 3")
            continue
        try:
            #从parts中拆分数字（转为浮点数）和运算符
            a = float(parts[0])
            operator = parts[1]
            b = float(parts[2])
            
            result = calculate(a, operator, b)
            print("结果:", result)
        #捕获错误
        except ValueError as e:
            print("输入错误：", e)
        except ZeroDivisionError as e:
            print("除数不能为0：", e)

if __name__ == "__main__":
    main()