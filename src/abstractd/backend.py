import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
import os
import tomllib
import dearpygui.dearpygui as dpg

from abstractd.abstracts import AbstractProcessor


class Backend:
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.toml'), 'rb') as f:
            self.config = tomllib.load(f)

        self.abstracts = AbstractProcessor(self.config)
        self.abstracts.synchronize_forms()
        self.server = smtplib.SMTP_SSL(self.config['email']['smtp'], context=ssl.create_default_context())
        self.server.login(self.config['email']['sender'], self.config['email']['password'])

        # states
        self.status = 'todo'
        self.fix_checkboxes = {k: False for k in self.config['fix']}
        self.fix_checkboxes['custom_msg'] = False
        del self.fix_checkboxes['msg']
        self.current_abstract = -1  # cause we start with +=1 in next_abstract, which is used to get first abstract as well
        self.any_abstracts = True
        self.loaded_txt = ""

    def cleanup(self):
        self.server.quit()

    def check_job(self):
        if not self.abstracts.any_to_assess():
            dpg.set_value('abstract', "Nie ma nic do rozpatrzenia!")
            dpg.disable_item('send')
            dpg.disable_item('version')
            self.any_abstracts = False

    def next_abstract(self):
        self.checkboxes_enable(False)
        self.current_abstract += 1
        if not self.any_abstracts:
            return None

        if self.current_abstract == self.abstracts.n_abstracts():
            dpg.set_value('abstract', "To był ostatni abstrakt do rozpatrzenia!")
            dpg.set_value('status', '')
            dpg.disable_item('send')
            dpg.disable_item('version')
            return None
        elif self.abstracts.get_abstract_status(self.current_abstract) in [self.config['assessed']['status']['todo'], self.config['assessed']['status']['fix']]:
            dpg.set_value('abstract', self.abstracts.get_abstract(self.current_abstract))
            dpg.set_value('status', self.abstracts.get_abstract_status(self.current_abstract))
            self.status = self.abstracts.get_abstract_status(self.current_abstract)
            self.load_abstract_from_txt()
        else:
            self.next_abstract()

    def send_email(self, message: str):
        msg = EmailMessage()
        receipent = self.abstracts.get_email(self.current_abstract)
        msg["Subject"] = self.config['email']['title']
        msg["From"] = formataddr((self.config['email']['name'], self.config['email']['sender']))
        msg["To"] = receipent
        msg['reply-to'] = self.config['email']['sender']
        msg.set_content(message)
        self.server.sendmail(self.config['email']['sender'], receipent, msg.as_string())
        print(f"Sent mail to: {receipent}")

    def mail_message(self) -> str:
        decision = self.config[self.status]['msg']
        if self.status == 'fix':
            for e in self.fix_checkboxes:
                if self.fix_checkboxes[e]:
                    try:
                        decision += f"\n{self.config['fix'][e]['msg']}"
                    except KeyError:
                        decision += f"\n{dpg.get_value('custom_msg')}"
        return f"{self.config['generic_msg']['start']}{decision}\n\nPoniżej zgłoszony abstrakt:\n\n{self.abstracts.get_abstract(self.current_abstract)}\n\n{self.config['generic_msg']['end']}"

    def load_abstract_from_txt(self):
        try:
            self.loaded_txt = '\n'.join(self.abstracts.load_from_txt(self.current_abstract).split('\n')[2:])
        except FileNotFoundError:
            self.loaded_txt = "Nie znaleziono abstraktu do wczytania!"


    # CALLBACKS


    def checkboxes_enable(self, enable):
        for ch_name in self.fix_checkboxes:
            if enable:
                dpg.enable_item(f"ch_{ch_name}")
            else:
                dpg.disable_item(f"ch_{ch_name}")
                dpg.set_value(f"ch_{ch_name}", False)

        if enable:
            dpg.enable_item("ch_custom_msg")
        else:
            dpg.disable_item("ch_custom_msg")
            dpg.set_value("ch_custom_msg", False)

        self.fix_checkboxes = {k: False for k in self.fix_checkboxes.keys()}
        dpg.set_value('custom_msg', '')

    def radio_callback(self, sender, app_data):
        if app_data == 'Przyjmij':
            self.status = 'ok'
            self.checkboxes_enable(False)
        elif app_data == 'Odrzuć':
            self.status = 'rejected'
            self.checkboxes_enable(False)
        elif app_data == 'Do poprawy':
            self.status = 'fix'
            self.checkboxes_enable(True)
        else:
            raise RuntimeError("DO NOT CHANGE RADIO NAMES!!!")

    def checkbox_callback(self, sender, app_data):
        self.fix_checkboxes['_'.join(sender.split('_')[1:])] = app_data
        if sender == 'ch_custom_msg':
            dpg.enable_item('custom_msg') if app_data else dpg.disable_item('custom_msg')
            dpg.set_value('custom_msg', '')

    def send_callback(self, sender, app_data):
        if self.status == 'todo':
            raise RuntimeError("Select one of the options!")

        message = self.mail_message()
        self.abstracts.set_abstract_status(self.current_abstract, self.status)
        if self.status in ['ok', 'fix']:
            self.abstracts.export_abstract(self.current_abstract)

        self.send_email(message)
        self.next_abstract()

    def skip_callback(self, sender, app_data):
        self.next_abstract()

    def switch_callback(self, sender, app_data):
        if dpg.get_item_label(sender) == 'Forms':
            dpg.set_value('abstract', self.loaded_txt)
            dpg.set_item_label(sender, 'Txt')
        else:
            dpg.set_value('abstract', self.abstracts.get_abstract(self.current_abstract))
            dpg.set_item_label(sender, 'Forms')
