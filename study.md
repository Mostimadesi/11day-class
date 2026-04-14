 # 11天编程班学习记录
 ## day1 配置开发环境/编写第一行代码
 1、在python官网安装python：https://www.python.org/downloads/ 

 2、在系统变量处检查有无python路径：<img width="1423" height="885" alt="image" src="https://github.com/user-attachments/assets/097127a4-08ef-40b9-bc4d-3bc4729f7a23" />

 3、在终端检查python能否正常运行：<img width="1730" height="924" alt="image" src="https://github.com/user-attachments/assets/46c4a940-a488-4784-b7b8-e1620875f74b" />

 4、在VScode中安装python扩展并配置python解释器：<img width="2099" height="1370" alt="image" src="https://github.com/user-attachments/assets/872930a1-72f8-4bc8-ad22-a169bf5ca073" />

 5、在vscode中打开由git拉取的仓库文件夹，创建新的py文件编写第一行代码并运行：<img width="2096" height="1370" alt="image" src="https://github.com/user-attachments/assets/b51e0d5b-10f7-433d-b249-54e1dfa2906d" />

 6、使用git将修改后的项目commit到github仓库中：<img width="882" height="521" alt="image" src="https://github.com/user-attachments/assets/281b9a0d-3c88-4d72-ab23-8234e998c7a1" />

 ## day1 表达式
 ### 常量、变量、保留字
 常量：值固定、**不允许改变**的数据，常用来表示不变的数据，如圆周率，约定上一般用大写表示

 变量：值可以改变，在程序运行过程中可以变化，变量名实际上是用户向python请求分配一块内存并存放某些数据的“地方”

 保留字：编程语言中预先定义的，有特殊含义的字符，不能用作变量名或函数名
 ### 运算符、类型
 顺序：幂运算-->乘除运算-->加减运算，括号优先，同级运算从左到右

 类型：即type，表示数据属于何种类型，以及能够进行的操作，一般来说同类型的数据才能进行运算

 比较运算符：用于条件表达式中(ifelse/while...)，is/isnot比双等号的判定要求更严格

 逻辑运算符：用于将多个（条件）语句相连，常用的有 且and 或or 非not

 ## day1 条件控制语句
 ### if/else语句
 缩进：python用缩进来表示代码块的范围（而不是大括号），不正确的缩进会让条件控制语句的范围出现混乱

 if/else：如果条件成立，则执行if下的代码块；否则，执行另一代码块（跳过/执行else下的块）

 elif：如果elif的上一个if条件不成立，则判断此elif的条件（一旦前面的某个条件成立，后面的条件不再参与判断）

 条件表达式：结果为布尔值（真True/假False），表达式中通常使用比较运算符
 ### try...except语句
 try...except：捕获并处理抛出异常（程序无法按当前预定方式执行）的语句，异常点后的try代码块不会再执行

 异常类：except后匹配的是异常类，即匹配抛出的异常属于python中的哪个异常层级，通常捕获Exception类
 ### while...语句
 while...：如果条件为真，则不断执行while下的代码框，直到条件为假退出循环

 break：强制跳出**当前**循环      continue：强制结束此轮执行并**回到**循环起点
 ### for...语句
 for...：从一个**确定**的迭代对象里依次取值并执行代码块，直到迭代对象已完全遍历

 ## day1 封装函数
 ### 函数的要素
 函数名：函数的标识符，用户通过函数名（及传入的参数）调用函数

 参数：运行此函数所需要输入的内容，即“接口”，定义函数时暂时用一个“别名”代替真正输入的内容

 返回：函数运行结束后所输出的内容，即“出口”，同上

 块：通过缩进来规定的函数代码框范围

 ## day2 AI编程环境测试
 1、进入trae官网安装软件：https://www.trae.cn/，初始化中选择导入vscode设置，在主界面选择进入SOLO模式

 2、在本地项目根目录下新建一个文件夹用于AIvibe项目（vibetest）

 3、通过提一个简单的问题让AI”随机“地生成一个贪吃蛇小游戏：<img width="2163" height="1360" alt="image" src="https://github.com/user-attachments/assets/224027d5-b446-4868-881a-66918c9980ea" />

 4、在测试后细化你的要求（可借助其他LLM），让AI进行修改：<img width="2163" height="1360" alt="image" src="https://github.com/user-attachments/assets/797f7a22-8875-4231-9205-ced1cdcbd70b" />

 5、向AI询问项目具体是如何实现的（反向学习）：<img width="2163" height="1360" alt="image" src="https://github.com/user-attachments/assets/0ad46f49-2058-411b-bb79-1939a557d3c7" />

 6、让AI将开发项目内容写成文档供后续参考：<img width="2163" height="1360" alt="image" src="https://github.com/user-attachments/assets/37bb5c98-7240-4553-b593-0e009f06253c" />

 ## day2 API配置相关
 ### 基本要素
 Prompt：提示词，在LLM广泛普及后基本可视为“用户访问大模型时的所有输入文本”，大部分提示词通常以任务或问题的形式传入LLM

 Temperature：温度，控制LLM生成结果的随机性，越高的温度会带来越不可预测的输出（以及更有创意、更多样化的输出）

 System prompt：系统提示词，可以认为是“全局提示词”，常用于对模型进行初始化设定（如模拟人格）

 Context：上下文，可以认为是模型的“短期记忆”，系统一次浏览的上下文由Context window（上下文窗口）决定

 Max_tokens：最大生成token数，控制模型输出长度（考虑到输出成本/性能）
 ### 配置参数
 base_api_url：API服务入口地址，决定调用哪个服务（例如，即使api是openai协议格式，只要其他提供商也使用该格式，则可以只更改base_api_url和model_name）

 API_KEY：API凭证，是调用者的**唯一**身份标识，一般在环境变量中设置以避免暴露

 Access_token：许可token，相当于调用的“第二层保险”

 ## day3 ollame部署测试
 1、从官网下载可执行程序并安装：https://ollama.com/download

 2、配置环境变量OLLAMA_MODELS和OLLAMA_HOST：<img width="930" height="375" alt="image" src="https://github.com/user-attachments/assets/68506bd8-53bf-4dfb-a81a-84300c7bbabb" />

 3、重启电脑，在终端中使用run modelname指令自动下载模型并对话（同时验证环境变量更改是否生效）：<img width="1730" height="924" alt="image" src="https://github.com/user-attachments/assets/37bf6235-86b3-4e46-9a4c-2126b4ec2936" />

 4、克隆ollama-webui的仓库并运行：<img width="1730" height="924" alt="image" src="https://github.com/user-attachments/assets/b9eb29ba-4b2e-4f3a-b6f3-5f8b3c0a33cd" />

 5、在webui可视化界面进行对话：<img width="2560" height="1347" alt="image" src="https://github.com/user-attachments/assets/a7eaadb1-8957-48f9-bd0c-3667418ef1a1" />

 6、在vscode中使用CODEX编写一个支持多轮对话和参数设置的ollama对话系统：<img width="2493" height="1407" alt="image" src="https://github.com/user-attachments/assets/3a49730d-65fd-433e-972f-ee215fe95956" />

## day3 提示词工程相关

### 提示词设计原则

1、提示词应当参照训练时的标准形式，对于LLM来说即清晰、详细、具体的自然语言描述

2、对于复杂任务/大型项目，提示词所指派的待解决问题不要过长/过多，而是分步解决

3、提示词应当尽量具有逻辑清晰的结构（结构化输入输出）

 ### 具体的提示词优化技巧

1、Few-shot：少样本提示，即给模型少量示范样例，让模型自行模仿用户期望的输出格式

​      ------上传一个网页截图并告诉AI仿照截图做网页样式

​      ------上传一个json文件并告诉AI按此格式输出回答

2、指定步骤：将复杂任务拆解成各个独立的步骤，并让AI按步骤依次完成

​      ------如写一个RAG：fetch文档-->切分chunk-->索引index-->answer回答

3、结构化提示词：使用适当的分隔符来使提示词更结构化

​      ------请使用此格式回答：<问题> <回答> <论据> <推理过程>

4、引导模型思考：使用适当的提示语让模型“多次思考“

​      ------在提示词结尾加上：请认真思考，并给出尽可能多的解决方案

​      ------在提问时加上：请首先自己解决这个问题，再评估我的方案是否正确/哪里需要改进

5、让另一个LLM优化：提示词本身就可以由大模型来优化，甚至可以写一个skill专门优化

## day4 RAG相关
### 基本流程
1、fetch文档：让系统读取本地文档或从url下载文档

2、切分chunk：将文档切分成多个chunk，每个chunk包含一定数量的文本

3、索引index：将切分得到的chunk向量化，建立索引，以便后续查询

4、answer回答：根据用户的问题，通过索引查询最相关的chunk，并优化用户的提示词

### 传统RAG的问题
1、固定切分：传统RAG通常使用固定的切分长度，破坏文档原有的逻辑结构

2、单模态索引：传统RAG使用的嵌入模型一般是非多模态的，会忽略图标等非文本信息

3、单次查询：RAG一般只查询一次，容易因为用户的用语不准而无法检索到相关内容

4、单次推理：RAG一般只优化一次提示词并交付LLM进行推理，容易因为模型随机性而使答案扰动

### KohakuRAG的解决方案
1、层级索引：通过四级树形结构（文档--章节--段落--句子）建立索引，更好地保留文档结构

2、支持多模态：通过使用jinav4多模态模型来创建非文本内容（图像/图表）嵌入

3、多查询索引：通过planner LLM进行多次查询，进行上下文扩展，尽可能检索相关内容

4、集成推理：通过让LLM进行多次独立推理并对结果投票，稳定答案输出，并在证据不足时倾向于让AI弃权

## day5 dify平台部署
1、访问dify官网并使用github账号登录：https://cloud.dify.ai/

2、选择创建空白应用：

3、








