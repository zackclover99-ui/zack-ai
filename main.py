from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import requests
import threading

# Mengatur warna background utama (Gelap, agar efek kaca terlihat)
Window.clearcolor = get_color_from_hex('#0F172A')

# Kelas untuk membuat Kotak Kaca (Glassmorphism)
class GlassBox(BoxLayout):
    def __init__(self, bg_color=[1, 1, 1, 0.1], **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ZackAIChat(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 15

        # 1. Header Aplikasi (Efek Kaca)
        self.header = GlassBox(bg_color=[0, 1, 0, 0.2], size_hint_y=None, height=60, padding=10)
        header_label = Label(
            text="[b]ZACK AI[/b]",
            markup=True,
            font_size='24sp',
            color=get_color_from_hex('#00FF00'),
        )
        self.header.add_widget(header_label)
        self.add_widget(self.header)

        # 2. Area Chat (Bisa di-scroll)
        self.scroll_view = ScrollView()
        self.chat_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=15,
            padding=10
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll_view.add_widget(self.chat_layout)
        self.add_widget(self.scroll_view)

        # 3. Area Input (Efek Kaca)
        self.input_box = GlassBox(bg_color=[1, 1, 1, 0.15], size_hint_y=None, height=60, spacing=10, padding=5)
        
        self.user_input = TextInput(
            hint_text='Ketik pesan...',
            multiline=False,
            background_color=[0, 0, 0, 0],
            foreground_color=get_color_from_hex('#FFFFFF'),
            cursor_color=get_color_from_hex('#00FF00')
        )
        self.user_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text='Kirim',
            size_hint_x=None,
            width=80,
            background_color=[0, 1, 0, 0.5],
            background_normal='',
            color=get_color_from_hex('#FFFFFF')
        )
        send_btn.bind(on_press=self.send_message)

        self.input_box.add_widget(self.user_input)
        self.input_box.add_widget(send_btn)
        self.add_widget(self.input_box)

    def add_message(self, text, is_user=True):
        if is_user:
            bubble_color = [1, 1, 1, 0.2] 
        else:
            bubble_color = [0, 0.5, 1, 0.2]

        msg_label = Label(
            text=text,
            markup=True,
            size_hint_y=None,
            color=get_color_from_hex('#FFFFFF'),
            halign='right' if is_user else 'left',
            valign='middle',
            padding=(10, 10)
        )
        msg_label.bind(width=lambda *x: msg_label.setter('text_size')(msg_label, (msg_label.width, None)))
        msg_label.bind(texture_size=lambda *x: msg_label.setter('height')(msg_label, msg_label.texture_size[1]))
        
        bubble = GlassBox(
            bg_color=bubble_color,
            size_hint=(None, None),
            size=(Window.width * 0.75, msg_label.height + 20)
        )
        bubble.add_widget(msg_label)

        row = BoxLayout(size_hint_y=None, height=bubble.height)
        if is_user:
            row.add_widget(Label())
            row.add_widget(bubble)
        else:
            row.add_widget(bubble)
            row.add_widget(Label())

        self.chat_layout.add_widget(row)
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0), 0.1)

    def send_message(self, instance):
        text = self.user_input.text.strip()
        if not text:
            return
        
        self.add_message(f"[b]Kamu:[/b] {text}", is_user=True)
        self.user_input.text = ''
        
        threading.Thread(target=self.get_ai_response, args=(text,)).start()

    def get_ai_response(self, prompt):
        self.add_message("[i]Zack AI sedang berpikir...[/i]", is_user=False)
        
        # === GANTI DENGAN API KEY GROQ KAMU ===
        API_KEY = " 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"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            jawaban = response.json()['choices'][0]['message']['content']
            Clock.schedule_once(lambda dt: self.update_ai_response(jawaban))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ai_response(f"[b]Error:[/b] Gagal terhubung. {e}"))

    def update_ai_response(self, jawaban):
        self.chat_layout.remove_widget(self.chat_layout.children[0])
        self.add_message(f"[b]Zack AI:[/b] {jawaban}", is_user=False)

class ZackAIApp(App):
    def build(self):
        return ZackAIChat()

if __name__ == '__main__':
    ZackAIApp().run()
