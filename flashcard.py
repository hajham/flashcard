import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import json
import csv
import arabic_reshaper
from bidi.algorithm import get_display
import os

# ثبت فونت فارسی
LabelBase.register(name='Vazir', fn_regular='Vazir.ttf')

# تابع برای اصلاح متن فارسی
def fix_text(text):
    return get_display(arabic_reshaper.reshape(text))


class FlashcardApp(App):
    def build(self):
        self.cards = []
        self.current_index = 0
        self.is_flipped = False

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.card_label = Label(
            text=fix_text("هیچ کارتی وجود ندارد"),
            font_name='Vazir',
            font_size=28,
            halign="center",
            valign="middle"
        )
        self.layout.add_widget(self.card_label)

        nav_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.prev_btn = Button(text=fix_text("قبلی"), font_name='Vazir', on_press=self.prev_card)
        self.flip_btn = Button(text=fix_text("برگردان"), font_name='Vazir', on_press=self.flip_card)
        self.next_btn = Button(text=fix_text("بعدی"), font_name='Vazir', on_press=self.next_card)
        nav_layout.add_widget(self.prev_btn)
        nav_layout.add_widget(self.flip_btn)
        nav_layout.add_widget(self.next_btn)
        self.layout.add_widget(nav_layout)

        action_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        add_btn = Button(text=fix_text("اضافه‌کردن کارت"), font_name='Vazir', on_press=self.show_add_card_popup)
        load_btn = Button(text=fix_text("بارگذاری فایل"), font_name='Vazir', on_press=self.show_file_chooser)
        action_layout.add_widget(add_btn)
        action_layout.add_widget(load_btn)
        self.layout.add_widget(action_layout)

        return self.layout

    def update_card_display(self):
        if self.cards:
            card = self.cards[self.current_index]
            text = card['answer'] if self.is_flipped else card['question']
            self.card_label.text = fix_text(text)
        else:
            self.card_label.text = fix_text("هیچ کارتی وجود ندارد")

    def flip_card(self, _):
        self.is_flipped = not self.is_flipped
        self.update_card_display()

    def next_card(self, _):
        if self.cards:
            self.current_index = (self.current_index + 1) % len(self.cards)
            self.is_flipped = False
            self.update_card_display()

    def prev_card(self, _):
        if self.cards:
            self.current_index = (self.current_index - 1) % len(self.cards)
            self.is_flipped = False
            self.update_card_display()

    def show_add_card_popup(self, _):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        q_input = TextInput(hint_text="سوال", font_name='Vazir', multiline=True)
        a_input = TextInput(hint_text="پاسخ", font_name='Vazir', multiline=True)

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_btn = Button(text=fix_text("ذخیره"), font_name='Vazir')
        cancel_btn = Button(text=fix_text("لغو"), font_name='Vazir')

        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(q_input)
        content.add_widget(a_input)
        content.add_widget(btns)

        popup = Popup(title=fix_text("افزودن کارت جدید"), content=content, size_hint=(0.8, 0.6))

        save_btn.bind(on_press=lambda x: self.save_new_card(q_input.text, a_input.text, popup))
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def save_new_card(self, question, answer, popup):
        if question.strip() and answer.strip():
            self.cards.append({"question": question, "answer": answer})
            self.current_index = len(self.cards) - 1
            self.is_flipped = False
            self.update_card_display()
        popup.dismiss()

    def show_file_chooser(self, _):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(filters=['*.json', '*.csv'])
        btn = Button(text=fix_text("بارگذاری"), font_name='Vazir', size_hint_y=None, height=40)

        content.add_widget(file_chooser)
        content.add_widget(btn)

        popup = Popup(title=fix_text("انتخاب فایل JSON یا CSV"), content=content, size_hint=(0.9, 0.9))

        def load_file(_):
            file_path = file_chooser.selection[0] if file_chooser.selection else None
            if file_path:
                self.load_cards(file_path)
                popup.dismiss()

        btn.bind(on_press=load_file)
        popup.open()

    def load_cards(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext == '.json':
                    data = json.load(f)
                    for item in data:
                        if 'question' in item and 'answer' in item:
                            self.cards.append(item)
                elif ext == '.csv':
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'question' in row and 'answer' in row:
                            self.cards.append(row)
            self.current_index = 0
            self.is_flipped = False
            self.update_card_display()
        except Exception as e:
            print("Error loading file:", e)

if __name__ == '__main__':
    FlashcardApp().run()
