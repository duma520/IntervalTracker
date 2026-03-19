@echo off
chcp 65001 >nul

echo 开始编译...
nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --include-module=pypinyin ^
    --include-data-dir="D:\Program Files\Python310\lib\site-packages\pypinyin"=pypinyin ^
    --follow-imports ^
    --jobs=4 ^
    --clang ^
    --remove-output ^
    --output-dir=build_output ^
    IntervalTracker.py

if %errorlevel% equ 0 (
    echo 编译成功！
    echo 输出目录: build_output\IntervalTracker.dist
) else (
    echo 编译失败，错误代码: %errorlevel%
)

pause