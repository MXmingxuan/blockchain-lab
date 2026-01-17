# 🔗 Blockchain Lab

MIT 区块链课程学习笔记 & 交互式工具集

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-持续更新中-orange.svg)

## 🎯 项目背景

这是我在学习 [MIT 15.S12: Blockchain and Money](https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018/) 课程过程中创建的学习与记录项目。

通过为每一章开发可交互的小工具，将抽象的区块链概念转化为可视化的代码逻辑，帮助自己更深入地理解和应用所学知识。

> � **项目持续更新中** - 随着课程学习进度不断添加新工具

### 第三章：密码学原语

| 工具 | 描述 |
|------|------|
| 🌀 雪崩效应演示器 | SHA-256 哈希位翻转可视化 |
| ⛓️ 迷你区块链构建器 | 哈希指针链接 + 篡改检测 |
| 🌲 默克尔树计算器 | 交易压缩为根哈希 |
| ✍️ 数字签名模拟器 | ECDSA 签名与验证 |
| 📍 比特币地址生成器 | 完整的 7 步派生流程 |

### 第四章：共识与挖矿

| 工具 | 描述 |
|------|------|
| ⛏️ PoW 挖矿模拟器 | Nonce 寻找 + 难度指数增长演示 |
| 💰 挖矿盈亏计算器 | 关机币价计算 |
| 📊 难度调整预测器 | 2016 区块周期分析 |
| 🔀 分叉监控器 | 6 确认安全性解释 |
| 📉 通胀率仪表盘 | 减半倒计时 + 供应进度 |

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/blockchain.git
cd blockchain

# 安装依赖
pip install flask ecdsa requests

# 启动服务器
python app.py
```

访问 **http://localhost:5000** 开始学习！

## 📁 项目结构

```
blockchain/
├── crypto_tools/           # 第三章工具模块
│   ├── avalanche.py        # 雪崩效应
│   ├── mini_blockchain.py  # 区块链构建
│   ├── merkle_tree.py      # 默克尔树
│   ├── digital_signature.py # 数字签名
│   └── bitcoin_address.py  # 比特币地址
├── mining_tools/           # 第四章工具模块
│   ├── pow_simulator.py    # PoW 模拟
│   ├── mining_calc.py      # 盈亏计算
│   ├── difficulty.py       # 难度预测
│   ├── fork_monitor.py     # 分叉监控
│   └── inflation.py        # 通胀率
├── templates/              # HTML 模板
├── static/                 # CSS 样式
└── app.py                  # Flask 应用
```

## 🎓 课程资源

- [MIT 15.S12: Blockchain and Money](https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018/)
- 讲师: Gary Gensler (现任 SEC 主席)

## 📝 License

MIT License
