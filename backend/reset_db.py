#!/usr/bin/env python3
"""重置数据库并重新初始化"""
import os
from app import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()
    print('旧表已删除')
    db.create_all()
    print('新表已创建')

# 重新运行seed
print('n运行seed脚本...')
os.system('python seed.py')
print('n数据库重置完成！')
