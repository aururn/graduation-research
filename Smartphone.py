from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import nfc
import sqlite3
import matplotlib.pyplot as plt

class FelicaApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10)

        # データ表示用のラベル
        self.data_label = Label(text="Felicaデータ: ")
        self.layout.add_widget(self.data_label)

        # データ読み込みボタン
        read_button = Button(text="Felicaデータ読み込み", on_press=self.read_felica_data)
        self.layout.add_widget(read_button)

        # データ保存ボタン
        save_button = Button(text="データ保存", on_press=self.save_data)
        self.layout.add_widget(save_button)

        # グラフ表示ボタン
        graph_button = Button(text="グラフ表示", on_press=self.show_graph)
        self.layout.add_widget(graph_button)

        return self.layout

    def read_felica_data(self, instance):
        service_code_9 = 0x0009
        block = 1
        with nfc.ContactlessFrontend('usb') as clf:
            tag = clf.connect(rdwr={'on-connect': lambda tag: False})
            if isinstance(tag, nfc.tag.tt3.Type3Tag):
                sc_9 = nfc.tag.tt3.ServiceCode(service_code_9 >> 6, service_code_9 & 0x3f)        # サービス指定
                bc = nfc.tag.tt3.BlockCode(block, service=0)         # ブロック指定
                data = tag.read_without_encryption([sc_9], [bc])        # Felicaから読み込み
                data = tag.identifier.hex()  # ここでFelicaから取得したデータを処理する
            # データ表示
            self.data_label.text = f"Felicaデータ: {data}"

            # アプリケーション内で使用するデータとして保存
            self.felica_data = data

    def save_data(self, instance):
        if hasattr(self, 'felica_data'):
            conn = sqlite3.connect('felica_data.db')
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS felica_data (id INTEGER PRIMARY KEY, value TEXT)')
            cursor.execute('INSERT INTO felica_data (value) VALUES (?)', (self.felica_data,))
            conn.commit()
            conn.close()

    def show_graph(self, instance):
        conn = sqlite3.connect('felica_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM felica_data')
        data = cursor.fetchall()
        conn.close()

        # グラフ表示
        x_values = list(range(1, len(data) + 1))
        y_values = [int(row[1], 16) for row in data]

        plt.plot(x_values, y_values)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('')
        plt.show()

if __name__ == '__main__':
    FelicaApp().run()
