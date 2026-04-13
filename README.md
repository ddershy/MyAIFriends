# MyAIFriends-我的AI朋友们

1. 支持用户创建并分享任意多个虚拟朋友，可以自定义角色音色、性格、简介；
2. 支持语音识别、语音合成、语音复刻，实现跟虚拟人物语音通话交流；
3. 支持function call、知识库；
4. 后端采用Django，前端采用Vue，大模型框架采用LangChain；
5. 内含前后端全栈代码，且已对接大模型；详细过程参考 `\MyAIFriends流程记录\MyAIFrinds.md` 系列。


### 目录说明

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