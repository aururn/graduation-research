#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import binascii
import nfc

#sys.path.insert(1, os.path.split(sys.path[0])[0])
sys.path.append('/home/pi/nfcpy')
input_file = ''         # データ取得するファイルパス
output_file = ''        # データ出力するファイルパス

file = open(output_file, 'w')   # テキストファイルを書き込みモードで開く

service_code_9 = 0x0009     # Felicaへ読み書きするサービスコード

# 使用ICカードの属性を表示
def on_connect(tag):
    print("connected")
    print(str(tag))
    print('\n')

# ファイルからデータを取得
def get_data():
    target_line = int(input("書き込む行数を指定 : "))
    # ファイルを読み込みモードで開く
    with open(input_file, 'r') as file:
    # 指定した行数までスキップ
        for i in range(target_line - 1):
            file.readline()

    # 指定した行を読み込む
        line = file.readline().strip()
        data = [int(num) for num in line.split()]

    # Felicaへの書き込みの都合上、要素数を16とする(0埋め)
    if len(data) < 16:
        for i in data:
            if len(data) < 16:
                data.append(0)
            else:
                break
    else:
        print("error: Number of elements must be less than 16")
        return False
    print(f"書き込む数値: {data}")

    return data

# Felicaへデータの書き込み
def write_Card(tag,block):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc_9 = nfc.tag.tt3.ServiceCode(service_code_9 >> 6, service_code_9 & 0x3f)      # サービス指定
            bc = nfc.tag.tt3.BlockCode(block, service=0)        # ブロック指定
            byte_array = bytearray(get_data())      # データ配列をbytearrayに変換
            tag.write_without_encryption([sc_9], [bc], byte_array)      # Felicaに書き込み
            
            return True
        
        except Exception as e:
            print ("error: %s\n" % e)
            return False
    else:
        print ("error: tag isn't Type3Tag\n")
        return False

# Felicaから読み込み
def read_Card(tag,block):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc_9 = nfc.tag.tt3.ServiceCode(service_code_9 >> 6, service_code_9 & 0x3f)        # サービス指定
            bc = nfc.tag.tt3.BlockCode(block, service=0)         # ブロック指定
            Data = tag.read_without_encryption([sc_9], [bc])        # Felicaから読み込み
            print(f"取得データ{list(Data)}\n")       # bytearrayをデータ配列に変換
            get_txt(Data)       # データをテキストファイルに書き込み
        except Exception as e:
            print ("error: %s\n" % e)            
    else:
        print ("error: tag isn't Type3Tag\n")

# データをテキストファイルに書き込み
def get_txt(Data):
    # 数値をスペースで区切って1行に書き込む
    file.write(' '.join(map(str, Data)) + '\n')


def main():
    # PaSoRiとの接続
    clf = nfc.ContactlessFrontend('usb')
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    on_connect(tag)

    while True:
        mode = int(input("モード選択 | カードに書きこむ ・・・ 【 0 】 カードから読み込む ・・・ 【 1 】 終了 ・・・ 【 2 】 : "))
        if mode == 0:
            block = int(input("ブロックを選択【0 ~ 14】: "))
            if write_Card(tag,block):
                print("Data successfully written to Felica.\n")
            else:
                print("Failed to write data to Felica.\n")
        elif mode == 1:
            block = int(input("ブロックを選択【0 ~ 14】: "))
            read_Card(tag,block)
        else:
            clf.close()
            file.close()
            print("Finished")
            break
        
if __name__ == "__main__":
    main()

