@echo off
chcp 65001 > nul
title L�����ķ����������

echo ================================================
echo L�����ķ������������
echo ����ԭ����ҵ - ��Ŀ6.2
echo ================================================
echo.
echo ����: ������
echo ѧ��: 2021060187
echo �༶: �ƿ�2203
echo.
echo ������������...
echo.

REM ���Python�Ƿ�װ
python --version > nul 2>&1
if errorlevel 1 (
    echo ����: δ��⵽Python����
    echo ��ȷ���Ѱ�װPython 3.7����߰汾
    echo.
    pause
    exit /b 1
)

REM ����������ļ��Ƿ����
if not exist "�����ļ�\l_attribute_main.py" (
    echo ����: �Ҳ����������ļ�
    echo ��ȷ�������ļ�����
    echo.
    pause
    exit /b 1
)

REM ���г���
cd �����ļ�
python l_attribute_main.py

REM ���������н��
if errorlevel 1 (
    echo.
    echo �������г������������Ϣ
    echo.
    pause
) else (
    echo.
    echo ���������˳�
)

echo.
echo ��������˳�...
pause > nul
