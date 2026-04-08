#自定义函数
def beginner():
    print("Hello, World!")

#输入（水果、动作）处理（组句）输出（句子）
def workflow():
    input_material = input("fruit：")
    next_step = input("action：")
    print("You have " + input_material + " and you will " + next_step)

def enter_fra():
    try:
        input_material = 1 / int(input("Please enter a number："))
        print("You have entered " + str(input_material))
    except Exception as e:
        print("\nAn error occurred: " + str(e))  #如果输入0，则出现除0错误；如果输入非数字，则出现ValueError错误

def greet(language):
    #if语句：根据满足的条件执行不同的代码块
    if language == "En" or language == "en":
        print("Bonvoyage!")
    elif language == "Cn" or language == "cn":
        print("一路顺风！")
    else:
        print("Sorry, I don't understand this language.")

def find_max(num_list):
    max_num = num_list[0]
    #for循环依次迭代
    for num in num_list:
        if num > max_num:
            max_num = num
    return max_num

if __name__ == "__main__":
    beginner()
    workflow()
    enter_fra()
    greet("En")