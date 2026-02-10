import dearpygui.dearpygui as dpg
import os

from abstractd.backend import Backend


ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')

MAIN_H = 800
MAIN_W = 700
TEXT_H = 600
INPUT_TEXT_W = 380


dpg.create_context()
dpg.create_viewport(title='Abstractd', width=MAIN_W, height=MAIN_H, resizable=False)


with dpg.font_registry():
    with dpg.font(os.path.join(ASSETS, "Roboto-Regular.ttf"), 18) as default_font:
        dpg.add_font_range(0x0020, 0x017F)
        dpg.add_font_range(0x2013, 0x204A)


def setup_window(backend: Backend):
    with dpg.window(tag='main', width=MAIN_W, height=MAIN_H, no_resize=True, no_scrollbar=True, no_scroll_with_mouse=True):
        with dpg.child_window(width=MAIN_W, height=TEXT_H, pos=(0, 0)):
            with dpg.group(horizontal=True):
                dpg.add_button(tag='version', label='Forms', width=100, callback=backend.switch_callback)
                dpg.add_text(tag='status_desc', default_value="Status:")
                dpg.add_text(tag='status')
            dpg.add_text(tag='abstract', wrap=MAIN_W - 5)
        with dpg.child_window(width=MAIN_W, height=MAIN_H - TEXT_H, pos=(0, TEXT_H), no_scrollbar=True, no_scroll_with_mouse=True):
            with dpg.group(horizontal=True):
                with dpg.group(tag='gr1'):
                    dpg.add_radio_button(tag='decision', items=['Przyjmij', 'Odrzuć', 'Do poprawy'], callback=backend.radio_callback)
                    dpg.add_spacer(height=25)
                    with dpg.group(horizontal=True):
                        dpg.add_button(tag='skip', label='Pomiń', callback=backend.skip_callback)
                        dpg.add_button(tag='send', label='Wyślij', callback=backend.send_callback)
                with dpg.group(tag='gr2'):
                    for e in backend.config['fix']:
                        if e != 'msg':
                            dpg.add_checkbox(label=backend.config['fix'][e]['label'], tag=f'ch_{e}', enabled=False, callback=backend.checkbox_callback)
                    dpg.add_checkbox(label='Wiadomość', tag='ch_custom_msg', enabled=False, callback=backend.checkbox_callback)

                dpg.add_input_text(multiline=True, width=INPUT_TEXT_W, tag='custom_msg', enabled=False)


def main():
    backend = Backend()
    try:
        setup_window(backend)
        dpg.set_primary_window('main', True)
        dpg.setup_dearpygui()
        dpg.bind_font(default_font)
        dpg.show_viewport()
        backend.check_job()
        backend.next_abstract()
        dpg.start_dearpygui()
        dpg.destroy_context()
    finally:
        backend.abstracts.save_synced()
        backend.cleanup()


if __name__ == '__main__':
    main()
