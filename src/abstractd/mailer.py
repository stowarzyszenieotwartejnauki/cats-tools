import pandas as pd
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
import tomllib
import dearpygui.dearpygui as dpg


class Backend:
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.toml'), 'rb') as f:
            self.config = tomllib.load(f)

        try:
            self.data = pd.read_excel(self.config['participants']['path'], sheet_name=0, skiprows=self.config['forms']['skip'], names=self.config['forms']['col_names'] + [self.config['participants']['col_name']])
            self.paid = self.data[self.data[self.config['participants']['col_name']] == self.config['participants']['paid']]['email'].to_list()
            self.not_paid = self.data[self.data[self.config['participants']['col_name']].isna()]['email'].to_list()
            self.all = pd.read_excel(self.config['participants']['path'], sheet_name=0, skiprows=self.config['forms']['skip'], names=self.config['forms']['col_names'] + [self.config['participants']['col_name']])['email'].to_list()
        except FileNotFoundError:
            self.data = pd.read_excel(self.config['forms']['path'], sheet_name=0, skiprows=self.config['forms']['skip'], names=self.config['forms']['col_names'])
            self.all = self.data['email'].to_list()
            self.paid = []
            self.not_paid = []
        assert len(self.paid) + len(self.not_paid) == len(self.data), "Invalid characters in paid column!"

        self.server = smtplib.SMTP_SSL(self.config['email']['smtp'], context=ssl.create_default_context())
        self.server.login(self.config['email']['sender'], self.config['email']['password'])

        self.message = ''
        self.subject = ''
        self.copy = True
        self.receipents = self.all
        self.attachments = None


    def cleanup(self):
        self.server.quit()


    def send_email(self):
        assert self.message and self.subject, "Content must not be empty!"
        assert self.receipents, "No receipents selected!"

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = formataddr((self.config['email']['name'], self.config['email']['sender']))
        msg['reply-to'] = self.config['email']['sender']
        body = MIMEText(self.message)
        msg.attach(body)
        if self.attachments is not None:
            for name, attachment in self.attachments.items():
                with open(attachment, 'rb') as f:
                   msg.attach(MIMEApplication(f.read(), name=name))

        for receipent in self.receipents:
            if "To" in msg:
                msg.replace_header('To', receipent)
            else:
                msg['To'] = receipent

            self.server.sendmail(self.config['email']['sender'], receipent, msg.as_string())
            print(f"Sent mail to: {receipent}")

        if self.copy:
            msg.replace_header('To', self.config['email']['sender'])
            self.server.sendmail(self.config['email']['sender'], self.config['email']['sender'], msg.as_string())
            print(f"Sent mail to: {self.config['email']['sender']}")


    def send_certificates(self):
        pass


    def text_callback(self, sender, app_data):
        match sender:
            case 'title': self.subject = app_data
            case 'custom_msg': self.message = app_data


    def radio_callback(self, sender, app_data):
        match app_data:
            case "Wszyscy": self.receipents = self.all
            case "Opłaceni": self.receipents = self.paid
            case "Nieopłaceni": self.receipents = self.not_paid

        print(self.receipents)


    def copy_callback(self, sender, app_data):
        self.copy = app_data


    def input_selector_callback(self, sender, app_data):
        match sender:
            case 'input_dialog':
                self.attachments = app_data['selections'] | self.attachments if self.attachments is not None else app_data['selections']
                dpg.set_value('attachment_selected', ', '.join([e for e in self.attachments.keys()]))
            case 'attachment_clear':
                self.attachments = None
                dpg.set_value('attachment_selected', '')
            case 'input_dir':
                pass


### FRONTEND


ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')

MAIN_H = 800
MAIN_W = 700
TEXT_H = 600
INPUT_TEXT_H = 380


dpg.create_context()
dpg.create_viewport(title='Abstractd Mailer', width=MAIN_W, height=MAIN_H, resizable=True)


with dpg.font_registry():
    with dpg.font(os.path.join(ASSETS, "Roboto-Regular.ttf"), 18) as default_font:
        dpg.add_font_range(0x0020, 0x017F)
        dpg.add_font_range(0x2013, 0x204A)


def setup_file_selectors(backend: Backend):
    with dpg.file_dialog(label="Wybierz pliki", show=False, callback=backend.input_selector_callback, tag="input_dialog", width=500, height=400, modal=True):
        dpg.add_file_extension(".*")

    with dpg.file_dialog(label="Wybierz folder z certyfikatami", show=False, tag="input_dir", width=500, height=400, modal=True, directory_selector=True, callback=backend.input_selector_callback):
        pass


def setup_window(backend: Backend):
    with dpg.window(tag='main', width=MAIN_W, height=MAIN_H, no_resize=True, no_scrollbar=True, no_scroll_with_mouse=True):
        dpg.add_text("Tytuł mejla:")
        dpg.add_input_text(tag='title', callback=backend.text_callback)
        dpg.add_text("Treść mejla:")
        dpg.add_input_text(multiline=True, height=INPUT_TEXT_H, tag='custom_msg', callback=backend.text_callback)

        dpg.add_text("Uczestnicy:")
        with dpg.group(horizontal=True):
            dpg.add_radio_button(["Wszyscy", "Opłaceni", "Nieopłaceni"], horizontal=True, label="Odbiorcy", tag='receipents', callback=backend.radio_callback)
            dpg.add_checkbox(label="Kopia do nadawcy", tag='copy', default_value=backend.copy, callback=backend.copy_callback)

        dpg.add_text("Załączniki:")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Dodaj", tag='attachment', callback=lambda: dpg.show_item('input_dialog'))
            dpg.add_button(label="Wyczyść", tag='attachment_clear', callback=backend.input_selector_callback)
            dpg.add_button(label="Folder z certyfikatami", tag='certificates', callback=lambda: print("NOT DONE YET"))

        with dpg.group(horizontal=True):
            dpg.add_text("Wybrane załączniki:")
            dpg.add_text('', tag='attachment_selected')

        dpg.add_spacer()
        dpg.add_separator()
        dpg.add_button(label="WYŚLIJ MEJLE", tag='send', callback=backend.send_email)  # TODO certificates will change that shit as well I guess



def main():
    backend = Backend()
    try:
        setup_file_selectors(backend)
        setup_window(backend)
        dpg.set_primary_window('main', True)
        dpg.setup_dearpygui()
        dpg.bind_font(default_font)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
    finally:
        backend.cleanup()


if __name__ == '__main__':
    main()
