# MyAIFriends-我的AI朋友们

1. 支持用户创建并分享任意多个虚拟朋友，可以自定义角色音色、性格、简介；
2. 支持语音识别、语音合成，实现跟虚拟人物语音通话交流；
3. 支持function call、知识库；
4. 后端采用Django，前端采用Vue，大模型框架采用LangChain；
5. 内含前后端全栈代码，且已对接大模型。


## 效果展示
1. 初始界面：
<img width="1919" height="1019" alt="image" src="https://github.com/user-attachments/assets/1ae165b3-55d1-4d45-950b-2794164cbeaa" />

2. 搜索功能：
<img width="1918" height="781" alt="image" src="https://github.com/user-attachments/assets/370585a8-2af4-4443-b954-12e12effd477" />

3. 个人主页
<img width="1920" height="912" alt="image" src="https://github.com/user-attachments/assets/7006a4ad-4bd1-467f-b654-14cc126c0b2e" />

4. 创建角色
<img width="1923" height="974" alt="image" src="https://github.com/user-attachments/assets/97cd375b-33a4-4473-8e71-b5f3656a903b" />

5. 文本对话与记忆
<img width="1920" height="912" alt="image" src="https://github.com/user-attachments/assets/ee375cdc-1474-472d-9fac-4afec3b70920" />






## 目录说明

*   **`backend/`**: 基于 Django 框架的后端服务。采用解耦的结构，将模型 (`models`)、视图 (`views`) 拆分为独立模块。使用 LanceDB 管理本地向量知识库 (`documents`)，并提供 RESTful/HTTP 接口供前端调用。
*   **`frontend/`**: 基于 Vue 3 + Vite 构建的前端单页应用 (SPA)。集成 Pinia 进行状态管理，Vue Router 管理页面路由。包含语音交互 VAD 处理支持。
*   **`media/` & `static/`**: 分别用于处理项目运行时的动态媒体上传（如相册、头像）和打包后的静态资源。
*   **`MyAIFrinds流程记录/`**: 存放了系统开发流程的 Markdown 文档记录，记录环境配置、布局、语音识别和上线流程。
```text
MyAIFriends
├── backend/                  # Django 后端目录
│   ├── backend/              # Django 项目全局配置目录 (settings, urls, wsgi/asgi)
│   ├── media/                # 用户和角色上传的媒体文件 (头像、背景等)
│   ├── static/               # 收集的静态文件，包含前端构建产物和 VAD 模型
│   ├── web/                  # Django 主应用目录
│   │   ├── documents/        # 知识库文档和向量存储 (Lancedb) 配置
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── models/           # 数据库模型定义 (User, Character, Friend)
│   │   ├── templates/        # Django 模板 (承载前端入口 index.html)
│   │   └── views/            # 业务逻辑视图 (账号、角色创建、主页等 API)
│   ├── .env                  # 后端环境变量配置
│   ├── db.sqlite3            # SQLite 数据库文件
│   └── manage.py             # Django 命令行入口工具
├── frontend/                 # Vue 前端目录
│   ├── public/               # 公共静态资源 (VAD 语音活动检测相关文件)
│   ├── src/                  # 前端源代码
│   │   ├── assets/           # 样式和静态资源
│   │   ├── components/       # Vue 公共组件 (导航栏、角色卡片等)
│   │   ├── js/               # 全局配置、HTTP 请求封装和工具函数
│   │   ├── router/           # Vue Router 路由配置
│   │   ├── stores/           # Pinia 状态管理 (用户状态等)
│   │   ├── views/            # 页面级 Vue 组件 (创建、主页、聊天、用户页等)
│   │   ├── App.vue           # 前端根组件
│   │   └── main.js           # 前端入口文件
│   ├── index.html            # Vite HTML 模板
│   ├── vite.config.js        # Vite 构建配置
│   └── package.json          # 前端依赖配置
├── MyAIFrinds流程记录/       # 项目开发与流程记录文档
├── requirements.txt          # Python 后端依赖列表
├── package.json              # 根目录 Node.js 配置
└── README.md                 # 项目说明文档
```


### 详细文件说明

1. Django 后端核心目录结构 (backend/ & web/)
```text
backend/                            # Django 后端服务主目录
├── .env                            # 后端环境变量 (存放 LLM API Key、数据库配置、Secret Key等)
├── db.sqlite3                      # 默认开发的 SQLite 本地数据库文件
├── manage.py                       # Django 核心命令行控制工具 (用于迁移、运行服务、创建超级用户等)
│
├── backend/                        # Django 项目全局配置核心包
│   ├── __init__.py
│   ├── asgi.py                     # ASGI 服务器入口 (用于支持异步请求，如未来的 WebSocket 支持)
│   ├── settings.py                 # 全局配置文件 (极其关键：包含 CORS跨域配置、中间件、应用注册、媒体及静态路径等)
│   ├── urls.py                     # 根路由分发中心 (将带有 api 路径的请求转发到各个子应用)
│   ├── wsgi.py                     # WSGI 服务器入口 (传统的同步 Web 服务器部署入口，如搭配 Gunicorn)
│   └── __pycache__/
│
└── web/                            # 项目唯一的核心 Django 自定义应用层 (处理所有前后端分离的 API)
    ├── __init__.py
    ├── admin.py                    # Django 后台管理系统注册配置 (在此注册 Model 以便通过 /admin 管理)
    ├── apps.py                     # 当前 web App 的应用程序配置元数据
    ├── tests.py                    # 后端单元测试框架入口文件
    ├── urls.py                     # 当前 App 的子路由分发器 (所有的 view 接口在此按规则映射到具体类或函数)
    ├── __pycache__/
    ├── templates/                  # 渲染模板目录
    │   └── index.html              # 空白的白板模板，用于挂载且一次性加载 Vue 构建出的前端静态文件
    │    
    ├── documents/                  # [核心] LanceDB 向量数据库与 RAG 检索增强生成的承载目录
    │   ├── data.txt                # 被作为外部知识库来源注入的源头文字素材
    │   ├── lancedb_storage/        # LanceDB 本地持久化的物理存储目录区
    │   │   └── my_knowledge_base.lance/ # 具体知识库的 Lance 索引库表
    │   └── utils/                  # 知识库配套的 Python 脚本工具
    │       ├── custom_embeddings.py# 自定义大语言模型的 Embedding (词嵌入向量化) 转换逻辑
    │       └── insert_documents.py # 将长文本 (如 data.txt) 词块化 (Chunking) 并异步写入到 LanceDB 向量库的执行脚本
    │
    ├── models/                     # [核心] 数据库映射层，完全去除了原单文件，按业务解耦的 ORM 模型文件夹
    │   ├── character.py            # AI 虚拟角色数据模型 (设定角色的名字、Prompt、语音参数等字段)
    │   ├── friend.py               # 用户与 AI 角色缔结聊天羁绊的好友关系网络模型
    │   └── user.py                 # 继承重写后的定制化应用系统用户模型 (携带头像、自定义属性)
    │
    ├── migrations/                 # 数据库结构化改变的迁移历史跟踪文件夹，由 manage.py makemigrations 自动生成
    │   ├── 0001_initial.py         # 建表初始化记录
    │   ├── 0003_character.py       # (历史) 创建角色表的记录
    │   ├── 0008_systemprompt.py    # (历史) 及后续结构迭代表更记录...
    │   └── __pycache__/
    │
    └── views/                      # API 视图逻辑层，也是按业务极限解耦的大型控制器文件夹 (采用 REST / JSON 响应)
        ├── index.py                # 用于响应根目录，返回加载并拼装了前端资源的 index.html
        ├── utils/                  # 视图层的公用重复调用函数抽离
        │   └── photo.py            # 处理上传的各种媒体图片/头像格式校验和持久化的工具包
        │
        ├── account/                # 处理使用者账户状态的 API 控制器群
        │   ├── login.py            # 基于 Token 或 Session 的传统登入鉴权 API
        │   ├── logout.py           # 注销当前凭证 API
        │   ├── register.py         # 新用用户数据入库写入并初始化授权 API
        │   ├── get_user_info.py    # 用于前端载入时重新从 Server 中取得用户配置信息的 API
        │   └── refresh_token.py    # 用于处理前端 Token 续期更新的 API
        │
        ├── homepage/               # 用户通过鉴权后落地的入口模块 API
        │   └── index.py            # 返回推荐池、信息流或随机拉取活跃虚拟角色的 API 数据源
        │
        ├── user/                   # 仅针对使用者本身的局部功能 API 模块
        │   └── profile/
        │       └── update.py       # 使用者自主修改呢称、修改头像的更新业务控制器
        │
        ├── create/                 # 针对各类业务实体从无到有的业务组
        │   └── character/          
        │       ├── create.py       # 关键接口: 解析创造表单并生成虚拟角色实例存入模型
        │       ├── get_list.py     # 获取当前玩家所创建的所有自制角色接口
        │       ├── get_single.py   # 根据特定 ID 切面获取一个角色的具体档案数据
        │       ├── update.py       # 修改某个被拥有的虚拟角色的设定参数 API
        │       └── remove.py       # 删除/下架某角色 API
        │
        └── friend/                 # [核心链路] 包含拉关系直到聊天互动的全流程 API 模块
            ├── get_or_create.py    # 判断当前用户和特定角色之前是否有历史聊天，若无则初始化建立好友网络联系并存入 Friend 模型
            ├── get_list.py         # 拉取已建立聊天联系的所有虚拟朋友列表，作为好友边栏回显数据
            ├── remove.py           # 从通讯录中解除某个虚拟 AI 好友联系
            │
            └── message/            # 深层对话流机制层
                ├── get_history.py  # 提取此前对话数据库中的聊天 Message 模型序列以回推到前端复现现场
                ├── asr/
                │   └── asr.py      # [语音] 处理前端录音转译为文本 (Automatic Speech Recognition) 的音频解析 API 控制器
                ├── chat/
                │   ├── chat.py     # 最核心的聊天 API，承接来自于前端的上行文本、拼接系统 Prompt 并请求大模型返回响应，再将结果推流回前端
                │   └── graph.py    # 存放聊天过程中与知识图谱或工作流节点调度相关的辅助图逻辑
                └── memory/
                    ├── graph.py    # 伴随聊天中用于长效记忆记忆图谱提取的相关计算图模块
                    └── update.py   # 当单次聊天完成时，触发此 API 以将最新设定异步更新入数据库或反哺大模型上下文长效记忆库
```

2. Vue 前端应用核心目录结构 (frontend/)

```text
frontend/                           # Vue 3 前端根目录
├── index.html                      # Vite 挂载的独立 HTML 模板层 (通常含 <div id="app">)
├── jsconfig.json                   # 设定 JavaScript 开发环境提示和别名映射 (@/ 路径等)
├── package.json                    # 前端生态依赖与启动剧本包 (包含 Vue, Pinia, Vue-Router 等版本)
├── vite.config.js                  # Vite 本地构建服务器配置 (配置了跨域 Proxy 与资源打包策略)
│
├── public/                         # 不参与打包，直接 copy 到发布目标根目录的静态源文件
│   └── vad/                        # [高频] Silero VAD (语音端点检测) 前端纯离线原生依赖层 
│       ├── ort-wasm-simd-threaded.mjs # ONNX Runtime WebAssembly SIMD 加速加载器 (浏览器运行 AI 模型的基础)
│       ├── silero_vad_legacy.onnx     # 核心语音 VAD 判定计算图模型 (识别用户的说话与停顿)
│       └── vad.worklet.bundle.min.js  # 本地起 Audio Worklet 线程单独截取处理麦克风音频以防主渲染线程卡顿
│
└── src/                            # Vue 前端核心源码目录 
    ├── App.vue                     # 最顶层根组件 (通常包含 RouterView 占位)
    ├── main.js                     # 客户端打包与启动入口 (挂载 Pinia, Router 和持久化插件)
    ├── assets/                     
    │   └── main.css                # 全局公用 CSS 样式定义
    │
    ├── router/                     # 前端单页路由表
    │   └── index.js                # 定义各页面 (views) 的跳转路径、重定向规则以及路由守卫验证拦截
    │
    ├── stores/                     # 
    │   └── user.js                 # 注册并存储长期生效的用户信息 (如 Token、登录状态、头像)
    │
    ├── js/                         # 原生 JS 业务挂载中心
    │   ├── config/
    │   │   └── config.js           # 存放服务相关的全局默认常量 (如 API 根路由变量 URL 等)
    │   ├── http/                   # [高频] 底层网络请求拦截与封包管理 
    │   │   ├── api.js              # 基于 Axios 等封装的常规 HTTP 同步请求 (自动携带 Token, 全局报错拦截)
    │   │   └── streamApi.js        # [极其重要] 专门用于处理大模型 SSE / 流式响应的流式拉取请求，实现打字机吐字效果
    │   └── utils/
    │       └── base64_to_file.js   # 工具：将上传后转码的图片 Base64 数据反解为 File 流给后端 
    │
    ├── components/                 # 解耦提取出的可复用 Vue 组件库
    │   ├── navbar/                 # 全局顶部/侧边导航栏相关
    │   │   ├── NavBar.vue          # 导航容器主体
    │   │   ├── UserMenu.vue        # 展开的用户菜单弹层组件
    │   │   └── icons/              # 导航区涉及的所有 SVG 图标精细化组件 (Homepage, Search, Logout等)
    │   │
    │   └── character/              # [核心组件集] 处理与虚拟角色 AI 的对话全链路界面
    │       ├── Character.vue       # AI 对应的基础卡片容器或根视图组件
    │       ├── icons/              # AI 交流过程中涉及的具体图标集 (如发送、键盘、麦克风等)
    │       └── chat_field/         # [核心] 对话面板全集
    │           ├── ChatField.vue   # 聊天主控面板 (组装历史流与输入框)
    │           ├── character_photo_field/
    │           │   └── CharacterPhotoField.vue # 对话中浮现或置顶的 AI 角色立绘呈现
    │           ├── chat_history/
    │           │   ├── ChatHistory.vue # 聊天记录承载容器 (包含平滑滚动到底部、虚拟列表等可能的优化)
    │           │   └── message/
    │           │       └── Message.vue # 每一条消息的气泡单元组件 (需兼容本人和机器人的不同样式)
    │           └── input_field/    # 用户输入交互操作区
    │               ├── InputField.vue  # 文字键盘输入与发送调控台
    │               └── Microphone.vue  # [重要] 麦克风录音按钮组件 (内嵌 VAD 控制，按住/点击驱动说话，通过 WebAudioAPI 收集音频，联动后端 ASR)
    │
    └── views/                      # 充当实际网页载体的 Page 级别巨型视图路由组件
        ├── error/
        │   └── NotFoundIndex.vue   # 匹配不上路由的通用 404 捕获页面
        ├── user/                   # 人类用户自我相关模块
        │   ├── account/
        │   │   ├── LoginIndex.vue  # 登录表单页
        │   │   └── RegisterIndex.vue # 注册表单页 (需要走获取与上传头像表单)
        │   ├── profile/            # 修改用户主档信息的页面模块及子组件 (改头像、改昵称)
        │   └── space/              # 用户自己的展示私域主页模块
        ├── homepage/               
        │   └── HomepageIndex.vue   # 登入后展示全平台公共角色大厅的主页组件
        ├── friend/
        │   └── FriendsIndex.vue    # 已匹配羁绊的虚拟角色的独立侧边会话页 (从这里拉取对话历史并进入 chat_field)
        └── create/                 # 创建虚拟角色的入口及其向导页
            ├── CreateIndex.vue     # 主面板调度切换核心
            └── character/          # 虚拟分身的属性拆解子填报项
                ├── CreateCharacter.vue # 创建流程父节点
                ├── UpdateCharacter.vue # 修改历史设置页面
                └── components/         frontend/                           # Vue 3 前端根目录
├── index.html                      # Vite 挂载的独立 HTML 模板层 (通常含 <div id="app">)
├── jsconfig.json                   # 设定 JavaScript 开发环境提示和别名映射 (@/ 路径等)
├── package.json                    # 前端生态依赖与启动剧本包 (包含 Vue, Pinia, Vue-Router 等版本)
├── vite.config.js                  # Vite 本地构建服务器配置 (配置了跨域 Proxy 与资源打包策略)
│
├── public/                         # 不参与打包，直接 copy 到发布目标根目录的静态源文件
│   └── vad/                        # [高频] Silero VAD (语音端点检测) 前端纯离线原生依赖层 
│       ├── ort-wasm-simd-threaded.mjs # ONNX Runtime WebAssembly SIMD 加速加载器 (浏览器运行 AI 模型的基础)
│       ├── silero_vad_legacy.onnx     # 核心语音 VAD 判定计算图模型 (识别用户的说话与停顿)
│       └── vad.worklet.bundle.min.js  # 本地起 Audio Worklet 线程单独截取处理麦克风音频以防主渲染线程卡顿
│
└── src/                            # Vue 前端核心源码目录 
    ├── App.vue                     # 最顶层根组件 (通常包含 RouterView 占位)
    ├── main.js                     # 客户端打包与启动入口 (挂载 Pinia, Router 和持久化插件)
    ├── assets/                     
    │   └── main.css                # 全局公用 CSS 样式定义
    │
    ├── router/                     # 前端单页路由表
    │   └── index.js                # 定义各页面 (views) 的跳转路径、重定向规则以及路由守卫验证拦截
    │
    ├── stores/                     # 
    │   └── user.js                 # 注册并存储长期生效的用户信息 (如 Token、登录状态、头像)
    │
    ├── js/                         # 原生 JS 业务挂载中心
    │   ├── config/
    │   │   └── config.js           # 存放服务相关的全局默认常量 (如 API 根路由变量 URL 等)
    │   ├── http/                   # [高频] 底层网络请求拦截与封包管理 
    │   │   ├── api.js              # 基于 Axios 等封装的常规 HTTP 同步请求 (自动携带 Token, 全局报错拦截)
    │   │   └── streamApi.js        # 专门用于处理大模型 SSE / 流式响应的流式拉取请求，实现打字机吐字效果
    │   └── utils/
    │       └── base64_to_file.js   # 工具：将上传后转码的图片 Base64 数据反解为 File 流给后端 
    │
    ├── components/                 # 解耦提取出的可复用 Vue 组件库
    │   ├── navbar/                 # 全局顶部/侧边导航栏相关
    │   │   ├── NavBar.vue          # 导航容器主体
    │   │   ├── UserMenu.vue        # 展开的用户菜单弹层组件
    │   │   └── icons/              # 导航区涉及的所有 SVG 图标精细化组件 (Homepage, Search, Logout等)
    │   │
    │   └── character/              # [核心组件集] 处理与虚拟角色 AI 的对话全链路界面
    │       ├── Character.vue       # AI 对应的基础卡片容器或根视图组件
    │       ├── icons/              # AI 交流过程中涉及的具体图标集 (如发送、键盘、麦克风等)
    │       └── chat_field/         # [核心] 对话面板全集
    │           ├── ChatField.vue   # 聊天主控面板 (组装历史流与输入框)
    │           ├── character_photo_field/
    │           │   └── CharacterPhotoField.vue # 对话中浮现或置顶的 AI 角色立绘呈现
    │           ├── chat_history/
    │           │   ├── ChatHistory.vue # 聊天记录承载容器 (包含平滑滚动到底部、虚拟列表等可能的优化)
    │           │   └── message/
    │           │       └── Message.vue # 每一条消息的气泡单元组件 (需兼容本人和机器人的不同样式)
    │           └── input_field/    # 用户输入交互操作区
    │               ├── InputField.vue  # 文字键盘输入与发送调控台
    │               └── Microphone.vue  # [重要] 麦克风录音按钮组件 (内嵌 VAD 控制，按住/点击驱动说话，通过 WebAudioAPI 收集音频，联动后端 ASR)
    │
    └── views/                      # 充当实际网页载体的 Page 级别巨型视图路由组件
        ├── error/
        │   └── NotFoundIndex.vue   # 匹配不上路由的通用 404 捕获页面
        ├── user/                   # 人类用户自我相关模块
        │   ├── account/
        │   │   ├── LoginIndex.vue  # 登录表单页
        │   │   └── RegisterIndex.vue # 注册表单页 (需要走获取与上传头像表单)
        │   ├── profile/            # 修改用户主档信息的页面模块及子组件 (改头像、改昵称)
        │   └── space/              # 用户自己的展示私域主页模块
        ├── homepage/               
        │   └── HomepageIndex.vue   # 登入后展示全平台公共角色大厅的主页组件
        ├── friend/
        │   └── FriendsIndex.vue    # 已匹配羁绊的虚拟角色的独立侧边会话页 (从这里拉取对话历史并进入 chat_field)
        └── create/                 # 创建虚拟角色的入口及其向导页
            ├── CreateIndex.vue     # 主面板调度切换核心
            └── character/          # 虚拟分身的属性拆解子填报项
                ├── CreateCharacter.vue # 创建流程父节点
                ├── UpdateCharacter.vue # 修改历史设置页面
                └── components/         #拼装设定用到底层的组件 (如背景抽取、基础设定Profile、命名及头像定制)
```

3. frontend/src
```text
src/                                # Vue 前端核心源码目录
├── App.vue                         # 前端全局根组件，作为所有的页面路由 (RouterView) 的顶层视图容器
├── main.js                         # 客户端启动的主入口文件，负责挂载 Vue 实例、Pinia、路由及全局插件
│
├── assets/                         # 存放静态样式资源
│   └── main.css                    # 全局通用的基础 CSS 样式定义
│
├── js/                             # 原生 JavaScript 业务逻辑及辅助机制
│   ├── config/
│   │   └── config.js               # 前端全局配置项 (包含不同环境的 API Base URL、常量映射等)
│   ├── http/                       # [核心] 网络请求封装层
│   │   ├── api.js                  # 基于 Axios 封装的常规 HTTP 请求 (处理 Token 携带、请求拦截与全局异常报错)
│   │   └── streamApi.js            # 处理大模型流式拉取 (SSE/Fetch Stream) 的专用 API，实现大模型回答的“打字机”吐字效果
│   └── utils/                      
│       └── base64_to_file.js       # 通用工具函数：将前端裁剪或转换的 Base64 编码图片转为 File 文件对象以便上传后端
│
├── router/                         # Vue Router 前端单页面路由规则引擎
│   └── index.js                    # 定义了前端所有的页面路由路径、懒加载映射以及全局路由守卫 (如未登录拦截)
│
├── stores/                        
│   └── user.js                     # 管理全局唯一的用户状态 (如缓存的 JWT Token、用户个人信息、登录登出状态流转)
│
├── components/                     # [核心] 跨页面复用的高内聚低耦合 Vue 组件库
│   ├── navbar/                     # 页面导航及侧边栏相关组件
│   │   ├── NavBar.vue              # 全局顶部或侧边导航栏主体容器
│   │   ├── UserMenu.vue            # 点击头像展开的用户下拉菜单动作面板
│   │   └── icons/                  # 导航模块专属的精萃 SVG 图标组件集 
│   │       ├── CreateIcon.vue      # 创建图标 (加号等)
│   │       ├── FriendIcon.vue      # 聊天好友图标
│   │       ├── HomepageIcon.vue    # 主页图标
│   │       ├── MenuIcon.vue        # 移动端折叠菜单响应图标 (汉堡菜单)
│   │       ├── SearchIcon.vue      # 发现/搜索图标
│   │       ├── UserLogoutIcon.vue  # 登出退出图标
│   │       ├── UserProfileIcon.vue # 资料修改图标
│   │       └── UserSpaceIcon.vue   # 个人空间图标
│   │
│   └── character/                  # [高频] 构成 AI 角色互动与聊天的核心复杂组件群
│       ├── Character.vue           # 角色信息展示的外层主控组件或单一卡片容器
│       ├── icons/                  # 聊天交互专属操作按钮图标集
│       │   ├── KeyboardIcon.vue    # 切换至键盘文字输入图标
│       │   ├── MicIcon.vue         # 切换至麦克风语音输入图标
│       │   ├── RemoveIcon.vue      # 移除历史或删除角色操作图标
│       │   ├── SendIcon.vue        # 发送文本消息图标
│       │   └── UpdateIcon.vue      # 更新配置操作图标
│       └── chat_field/             # 高度集成的会话操作面板
│           ├── ChatField.vue       # 整个对话视窗的编排总线组件 (整合历史消息、用户输入和对方反馈)
│           ├── character_photo_field/
│           │   └── CharacterPhotoField.vue # 聊天界面内动态展示的 AI 角色实时头像或状态立绘
│           ├── chat_history/       # 历史消息滚动画布区
│           │   ├── ChatHistory.vue # 负责长列表滚动、定位最新消息容器 (可能涉及虚拟滚动优化)
│           │   └── message/
│           │       └── Message.vue # 最小信息单元气泡组件 (根据发送人是用户还是 AI 呈现不同样式和 Markdown 渲染)
│           └── input_field/        # 底部人类输入控制区
│               ├── InputField.vue  # 文字输入框和常规功能按钮的封装组件
│               └── Microphone.vue  # 内嵌录音逻辑的麦克风组件，联动外层 Silero VAD 模型进行音控端点检测与录音录制
│
└── views/                          # 映射到 Vue-Router 的顶级页面 (Page) 视图组件
    ├── error/                      # 系统级错误拦截页
    │   └── NotFoundIndex.vue       # 404 找不到页面的通用回退降级页面
    │
    ├── homepage/                   # 落地页大厅
    │   └── HomepageIndex.vue       # 系统登录后的首页广场，推荐热门的或其他用户创建的 AI Aigents
    │
    ├── friend/                     # 个人聊天聚合页
    │   └── FriendsIndex.vue        # 通讯录及聊天视图的主页，获取所有建立羁绊的好友历史并进入会话状态
    │
    ├── create/                     # 创作者经济与捏人核心页面模块
    │   ├── CreateIndex.vue         # 调控创建 AI 角色的总引导枢纽聚合页
    │   └── character/              # 针对具体 AI 详情的配置页面
    │       ├── CreateCharacter.vue # 新建空白角色提交的主表单页面
    │       ├── UpdateCharacter.vue # 回显过往数据并允许再编辑微调参数的更新页面
    │       └── components/         # 拆分后的高内聚设定填报控件表单组件
    │           ├── BackgroundImage.vue # 用于配置并上传该 AI 角色专有聊天背景图的组件
    │           ├── Name.vue        # 角色名称登记区
    │           ├── Photo.vue       # 角色头像切割与上传组件
    │           └── Profile.vue     # [最重要] 核心系统提示词(System Prompt)设定与角色前史/性格人设输入文本域
    │
    └── user/                       # 真实账号相关视图全集
        ├── account/                # 账号核验入口
        │   ├── LoginIndex.vue      # 登入页面表单
        │   └── RegisterIndex.vue   # 注册并初始化人类账号数据页面
        ├── profile/                # 用户自己档案修改页面
        │   ├── ProfileIndex.vue    # 对外资料大屏设置面板
        │   └── components/         # 修改资料专用的复用输入单元
        │       ├── Photo.vue       # 真人玩家修改自己头像的组件
        │       ├── Profile.vue     # 真人玩家修改个性签名的组件
        │       ├── Username.vue    # 真人玩家修改社交昵称的面单
        │       └── icon/           # 修改资料处专用配套提示图标
        │           └── CameraIcon.vue 
        └── space/                  # 用户私有空间展示页
            ├── SpaceIndex.vue      # 用户自己的看板src/                                # Vue 前端核心源码目录
├── App.vue                         # 前端全局根组件，作为所有的页面路由 (RouterView) 的顶层视图容器
├── main.js                         # 客户端启动的主入口文件，负责挂载 Vue 实例、Pinia、路由及全局插件
│
├── assets/                         # 存放静态样式资源
│   └── main.css                    # 全局通用的基础 CSS 样式定义
│
├── js/                             # 原生 JavaScript 业务逻辑及辅助机制
│   ├── config/
│   │   └── config.js               # 前端全局配置项 (包含不同环境的 API Base URL、常量映射等)
│   ├── http/                       # [核心] 网络请求封装层
│   │   ├── api.js                  # 基于 Axios 封装的常规 HTTP 请求 (处理 Token 携带、请求拦截与全局异常报错)
│   │   └── streamApi.js            # 处理大模型流式拉取 (SSE/Fetch Stream) 的专用 API，实现大模型回答的“打字机”吐字效果
│   └── utils/                      
│       └── base64_to_file.js       # 通用工具函数：将前端裁剪或转换的 Base64 编码图片转为 File 文件对象以便上传后端
│
├── router/                         # Vue Router 前端单页面路由规则引擎
│   └── index.js                    # 定义了前端所有的页面路由路径、懒加载映射以及全局路由守卫 (如未登录拦截)
│
├── stores/                         # Pinia 组合式状态管理器
│   └── user.js                     # 管理全局唯一的用户状态 (如缓存的 JWT Token、用户个人信息、登录登出状态流转)
│
├── components/                     # [核心] 跨页面复用的高内聚低耦合 Vue 组件库
│   ├── navbar/                     # 页面导航及侧边栏相关组件
│   │   ├── NavBar.vue              # 全局顶部或侧边导航栏主体容器
│   │   ├── UserMenu.vue            # 点击头像展开的用户下拉菜单动作面板
│   │   └── icons/                  # 导航模块专属的精萃 SVG 图标组件集 
│   │       ├── CreateIcon.vue      # 创建图标 (加号等)
│   │       ├── FriendIcon.vue      # 聊天好友图标
│   │       ├── HomepageIcon.vue    # 主页图标
│   │       ├── MenuIcon.vue        # 移动端折叠菜单响应图标 (汉堡菜单)
│   │       ├── SearchIcon.vue      # 发现/搜索图标
│   │       ├── UserLogoutIcon.vue  # 登出退出图标
│   │       ├── UserProfileIcon.vue # 资料修改图标
│   │       └── UserSpaceIcon.vue   # 个人空间图标
│   │
│   └── character/                  # [极高频] 构成 AI 角色互动与聊天的核心复杂组件群
│       ├── Character.vue           # 角色信息展示的外层主控组件或单一卡片容器
│       ├── icons/                  # 聊天交互专属操作按钮图标集
│       │   ├── KeyboardIcon.vue    # 切换至键盘文字输入图标
│       │   ├── MicIcon.vue         # 切换至麦克风语音输入图标
│       │   ├── RemoveIcon.vue      # 移除历史或删除角色操作图标
│       │   ├── SendIcon.vue        # 发送文本消息图标
│       │   └── UpdateIcon.vue      # 更新配置操作图标
│       └── chat_field/             # 高度集成的会话操作面板
│           ├── ChatField.vue       # 整个对话视窗的编排总线组件 (整合历史消息、用户输入和对方反馈)
│           ├── character_photo_field/
│           │   └── CharacterPhotoField.vue # 聊天界面内动态展示的 AI 角色实时头像或状态立绘
│           ├── chat_history/       # 历史消息滚动画布区
│           │   ├── ChatHistory.vue # 负责长列表滚动、定位最新消息容器 (可能涉及虚拟滚动优化)
│           │   └── message/
│           │       └── Message.vue # 最小信息单元气泡组件 (根据发送人是用户还是 AI 呈现不同样式和 Markdown 渲染)
│           └── input_field/        # 底部人类输入控制区
│               ├── InputField.vue  # 文字输入框和常规功能按钮的封装组件
│               └── Microphone.vue  #  内嵌录音逻辑的麦克风组件，联动外层 Silero VAD 模型进行音控端点检测与录音录制
│
└── views/                          # 映射到 Vue-Router 的顶级页面 (Page) 视图组件
    ├── error/                      # 系统级错误拦截页
    │   └── NotFoundIndex.vue       # 404 找不到页面的通用回退降级页面
    │
    ├── homepage/                   # 落地页大厅
    │   └── HomepageIndex.vue       # 系统登录后的首页广场，推荐热门的或其他用户创建的 AI Aigents
    │
    ├── friend/                     # 个人聊天聚合页
    │   └── FriendsIndex.vue        # 通讯录及聊天视图的主页，获取所有建立羁绊的好友历史并进入会话状态
    │
    ├── create/                     # 创作者经济与捏人核心页面模块
    │   ├── CreateIndex.vue         # 调控创建 AI 角色的总引导枢纽聚合页
    │   └── character/              # 针对具体 AI 详情的配置页面
    │       ├── CreateCharacter.vue # 新建空白角色提交的主表单页面
    │       ├── UpdateCharacter.vue # 回显过往数据并允许再编辑微调参数的更新页面
    │       └── components/         # 拆分后的高内聚设定填报控件表单组件
    │           ├── BackgroundImage.vue # 用于配置并上传该 AI 角色专有聊天背景图的组件
    │           ├── Name.vue        # 角色名称登记区
    │           ├── Photo.vue       # 角色头像切割与上传组件
    │           └── Profile.vue     # [最重要] 核心系统提示词(System Prompt)设定与角色前史/性格人设输入文本域
    │
    └── user/                       # 真实账号相关视图全集
        ├── account/                # 账号核验入口
        │   ├── LoginIndex.vue      # 登入页面表单
        │   └── RegisterIndex.vue   # 注册并初始化人类账号数据页面
        ├── profile/                # 用户自己档案修改页面
        │   ├── ProfileIndex.vue    # 对外资料大屏设置面板
        │   └── components/         # 修改资料专用的复用输入单元
        │       ├── Photo.vue       # 真人玩家修改自己头像的组件
        │       ├── Profile.vue     # 真人玩家修改个性签名的组件
        │       ├── Username.vue    # 真人玩家修改社交昵称的面单
        │       └── icon/           # 修改资料处专用配套提示图标
        │           └── CameraIcon.vue 
        └── space/                  # 用户私有空间展示页
            ├── SpaceIndex.vue      # 用户自己的看板
```
