from flask import Flask, jsonify
from flask import Flask, jsonify, send_from_directory
import os

try:
    # 作为包安装时使用相对导入
    from .game import Game
except ImportError:
    # 直接运行时使用绝对导入
    from game import Game

package_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(package_dir, 'web', 'static')
app = Flask(__name__, static_folder=static_path)
game = Game()

def main():
    """启动游戏服务器"""
    print("启动厕所侦探游戏...")
    print("访问 http://localhost:5000 开始游戏")
    print("注意：在寻找拉屎的人时不要孕吐！")
    app.run(debug=True)

@app.route('/')
def index():
    """游戏主界面"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/game')
def game_data():
    """获取游戏数据API"""
    suspects = []
    for suspect in game.suspects:
        suspects.append({
            'name': suspect.name,
            'description': suspect.description,
            'footprints': suspect.footprints,
            'fingerprints': suspect.fingerprints,
            'dna': suspect.dna,
            'suspicious_level': suspect.suspicious_level
        })
    return jsonify({
        'suspects': suspects,
        'hint': '找出所有线索都匹配的嫌疑人'
    })

# 静态文件路由
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    main()