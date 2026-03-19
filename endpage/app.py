from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import json
import os  # 新增：引入系统路径工具
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.llms import Tongyi

os.environ["DASHSCOPE_API_KEY"] = "sk-a3549a83674d4076bd473eb42dd0c8eb"

base_dir = os.path.abspath(os.path.dirname(__file__))
frontpage_dir = os.path.join(os.path.dirname(base_dir), 'frontpage')

app = Flask(__name__, 
            template_folder=frontpage_dir,
            static_folder=frontpage_dir)
CORS(app)

# 用户数据文件路径
USER_DATA_FILE = 'users.json'

# ========== 1：添加系统角色设定 ==========
SYSTEM_PROMPT = """你是一个生态小助手，专门帮助用户了解白头叶猴保护知识和声音降噪技术。

你的职责：
1. 回答关于白头叶猴的生态习性、保护现状等问题
2. 解释声音降噪技术的原理和应用
3. 提供项目相关的信息咨询
4. 语气友好、专业、简洁

请注意：
- 只回答与生态保护、白头叶猴、声音降噪相关的问题
- 如果用户问无关问题，礼貌地引导回主题
- 回答要简洁明了，避免过长"""
# ========== 系统角色设置结束 ==========

# 创建全局内存记忆对象（用于保持对话上下文）
memory = ConversationBufferMemory(return_messages=True)

def load_users():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

# 根路径重定向到登录页
@app.route('/')
def root():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('index1.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/work')
def work_page():
    return render_template('work.html')

@app.route('/work1')
def work1_page():
    return render_template('work1.html')

@app.route('/work2')
def work2_page():
    return render_template('work2.html')

@app.route('/work3')
def work3_page():
    return render_template('work3.html')

@app.route('/monitor')
def monitor():
    return render_with_template('monitor.html')

# ========== 2：聊天接口添加角色设定 ==========
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': '请输入问题内容'})
        
        # 初始化通义千问模型
        model = Tongyi(
            model="qwen-max"
        )
        
        # 创建对话链
        chain = ConversationChain(llm=model, memory=memory)
        
        # ========== 3：将系统提示与用户消息组合 ==========
        # 如果是第一条消息，添加系统角色设定
        if len(memory.chat_memory.messages) == 0:
            # 在用户消息前添加系统提示
            full_prompt = f"{SYSTEM_PROMPT}\n\n用户问题：{user_message}"
        else:
            full_prompt = user_message
        # ========== 组合结束 ==========
        
        # 获取 AI 回复
        response = chain.invoke({"input": full_prompt})
        
        return jsonify({'response': response["response"]})
        
    except Exception as e:
        return jsonify({'response': f'服务异常：{str(e)}'}), 500
# ========== 聊天接口结束 ==========

# 兼容旧链接
@app.route('/home.html')
def home_html():
    return redirect(url_for('home_page'))

@app.route('/work.html')
def work_html():
    return redirect(url_for('work_page'))

@app.route('/work1.html')
def work1_html():
    return redirect(url_for('work1_page'))

@app.route('/work2.html')
def work2_html():
    return redirect(url_for('work2_page'))

@app.route('/work3.html')
def work3_html():
    return redirect(url_for('work3_page'))

# 注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    users = load_users()
    if username in users:
        return jsonify({'success': False, 'message': '用户名已存在'})
    
    users[username] = password
    save_users(users)
    return jsonify({'success': True, 'message': '注册成功'})

# 登录
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    users = load_users()
    if username in users and users[username] == password:
        return jsonify({'success': True, 'message': '密码正确', 'redirect_url': '/home'})
    
    return jsonify({'success': False, 'message': '用户名或密码错误'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
