from __future__ import absolute_import

import os
import zipfile

import jinja2
from flask import Flask, request, send_file

from .lib import global_vars   # 默认变量

app = Flask(__name__)

DIR_PATH = os.path.join(os.path.dirname(__file__), 'templates')


def renders(file: str, **kwargs):
    with open(os.path.join(DIR_PATH, file), 'r', encoding='utf-8') as f:
        s = f.read()
    template = jinja2.Template(s)
    return template.render(**kwargs)


@app.route('/', methods=['GET', 'POST'])
def index():   # 主网页
    if request.method == 'GET':
        return renders('index.html', error=None)

    cwd = os.getcwd()  # 记录当前工作路径
    data_path = os.path.join(cwd, 'data')
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    os.chdir(data_path)  # 进入数据工作路径
    # 先编译 std.exe
    std = request.form.get('std')
    gpp_path = request.form.get('gpp-path')
    options = request.form.get('options')
    with open('std.cpp', 'w', encoding='utf-8') as f:
        f.write(std)  # 写入std.cpp
    os.system(f'"{gpp_path}" {options} -o std.exe std.cpp')  # 编译 std
    print('[INFO] std.cpp 编译完成', flush=True)

    use_spj, use_cfg = request.form.get('useSpj'), request.form.get('useCfg')
    if use_spj:
        checker = request.form.get('checker')
        with open('checker.cpp', 'w', encoding='utf-8') as f:
            f.write(checker)
    if use_cfg:
        config = request.form.get('config')
        with open('config.yml', 'w', encoding='utf-8') as f:
            f.write(config)

    number = int(request.form.get('num'))   # 数据组数
    maker_type = 'python'
    maker_complied = None
    if request.form.get('maker').strip():
        try:
            maker_complied = compile(request.form.get('maker'), 'maker.py', 'exec')   # 编译生成器
        except (Exception, SystemExit) as err:
            os.chdir(cwd)
            return renders('index.html', error=str(err))
        print('[INFO] maker.py 编译完成', flush=True)
    else:
        maker_type = 'cpp'
        maker_cpp = request.form.get('maker-cpp')
        with open('maker.cpp', 'w', encoding='utf-8') as f:
            f.write(maker_cpp)  # 写入maker.cpp
        os.system(f'"{gpp_path}" {options} -o maker.exe maker.cpp')  # 编译 std
        print('[INFO] maker.cpp 编译完成', flush=True)

    prefix = request.form.get('prefix').strip()   # 数据前缀名
    for i in range(1, number + 1):  # 循环并生成数据
        in_name = f'{prefix}{i}.in'
        out_name = f'{prefix}{i}.out'
        print(f"[INFO] 数据生成中……当前数据点：{in_name} / {out_name}", flush=True)
        if maker_type == 'python':
            local_vars = global_vars.copy()
            in_file = open(in_name, 'w', encoding='utf-8')
            local_vars['num'] = i
            local_vars['print'] = lambda *args, **kwargs: print(*args, **kwargs, file=in_file)  # 设置变量
            try:
                exec(maker_complied, local_vars)
            except (Exception, SystemExit) as err:
                os.chdir(cwd)  # 切换回原工作路径
                return renders('index.html', error=str(err))
            finally:
                in_file.close()
        else:
            with open('number.tmp', 'w', encoding='utf-8') as f:
                f.write(str(i))
            os.system(f'maker.exe < number.tmp > {in_name}')
        os.system(f'std.exe < {in_name} > {out_name}')  # 使用 std 生成答案

    zip_name = f'{prefix}.zip' if prefix else 'data.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:  # 打包 zip 文件
        for i in range(1, number + 1):
            print(f"[INFO] 数据打包中……当前数据点：{prefix}{i}.in / {prefix}{i}.out", flush=True)
            zf.write(f'{prefix}{i}.in')
            zf.write(f'{prefix}{i}.out')
        if use_spj:
            zf.write('checker.cpp')
        if use_cfg:
            zf.write('config.yml')

    os.chdir(cwd)  # 切换回原工作路径
    return send_file(os.path.join(data_path, zip_name), as_attachment=True)  # 返回答案 zip 文件


@app.route('/help/')
def show_help():
    return renders('help.html')


@app.route('/help/cyaron/')
def show_help_cyaron():
    return renders('cyaron.html')
