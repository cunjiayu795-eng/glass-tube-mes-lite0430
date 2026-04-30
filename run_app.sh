#!/bin/bash

APP_FILE=$(find /workspaces/codespaces-blank -name streamlit_app.py | head -n 1)
APP_DIR=$(dirname "$APP_FILE")

echo "进入项目目录: $APP_DIR"
cd "$APP_DIR" || exit 1

echo "安装依赖..."
python3 -m pip install --user -r requirements.txt

echo "启动 Streamlit..."
python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
