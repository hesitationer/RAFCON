from future import standard_library
standard_library.install_aliases()
from builtins import str
import threading
import testing_utils
from testing_utils import call_gui_callback

from rafcon.utils import log

logger = log.get_logger(__name__)


def xor(_list):
    result = 0
    for element in _list:
        result = element ^ result
    return result


def trigger_dialog_tests():
    test_text = "test_text"
    from gi.repository import Gtk
    from rafcon.gui.utils import dialog

    def on_ok_clicked(widget, response_id):
        # Default response by the "ok" button is -5
        assert response_id == -5

    def on_button_clicked(widget, response_id):
        # Last button in the order gets the response 4 ((index=3) + 1)
        assert response_id == 4

    def on_entry_activated(widget, response_id):
        # The entry gets the same response as the first button
        assert response_id == 1
        assert widget.entry.get_text() == test_text
        assert widget.checkbox.get_label() == test_text
        # As Gtk.CheckButton is a ToggleButton, get_active()=True represents the "checked" state
        assert widget.checkbox.get_active()

    def on_checkbox_dialog_approval(widget, response_id):
        # Check if all checkboxes appeared and the modulo operation worked
        assert not widget.get_checkbox_state_by_index(0)
        assert widget.get_checkbox_state_by_index(3)
        # Check if the checkbutton labels are correct
        assert len(widget.get_checkbox_state_by_name(test_text)) == 4

        assert not xor(widget.get_checkbox_states())

    dialog_window = call_gui_callback(dialog.RAFCONMessageDialog, test_text, on_ok_clicked)
    # First button of the dialog, in this case the standard "Ok" button
    button = dialog_window.get_action_area().get_children()[0]
    call_gui_callback(button.clicked)
    call_gui_callback(dialog_window.destroy)
    button_texts = ["First", "Second", "Third", "Fourth"]

    dialog_window = call_gui_callback(dialog.RAFCONButtonDialog, test_text, button_texts, on_button_clicked)

    for index, button_text in enumerate(button_texts):
        # Check if the button order is the same as requested by the button_texts list
        button = dialog_window.get_action_area().get_children()[index]
        assert str(button.get_label()) == button_texts[index]

    call_gui_callback(button.clicked)
    call_gui_callback(dialog_window.destroy)

    dialog_window = call_gui_callback(dialog.RAFCONInputDialog, test_text, button_texts, test_text, on_entry_activated)
    call_gui_callback(dialog_window.entry.set_text, test_text)
    call_gui_callback(dialog_window.checkbox.set_active, True)
    # Represents hitting the enter button
    call_gui_callback(dialog_window.entry.activate)
    call_gui_callback(dialog_window.destroy)

    dialog_window = call_gui_callback(dialog.RAFCONColumnCheckboxDialog,
                                      test_text, button_texts, [test_text, test_text, test_text, test_text],
                                      on_checkbox_dialog_approval, (), Gtk.MessageType.QUESTION)

    for index, checkbox in enumerate(dialog_window.checkboxes):
        # Check the checkboxes in an alternating order
        call_gui_callback(checkbox.set_active, index % 2)

    button = dialog_window.get_action_area().get_children()[0]
    call_gui_callback(button.clicked)

    call_gui_callback(dialog_window.destroy)


# def test_dialog_test(caplog):
#     testing_utils.dummy_gui(None)
#
#     testing_utils.initialize_environment(gui_already_started=False)
#
#     logger.debug("Dialog test started.")
#
#     thread = threading.Thread(target=trigger_dialog_tests)
#     thread.start()
#     testing_utils.shutdown_environment(caplog=caplog, expected_warnings=0, expected_errors=0, unpatch_threading=False)


def test_dialog_test(caplog):
    testing_utils.run_gui(gui_config={'HISTORY_ENABLED': False, 'AUTO_BACKUP_ENABLED': False})
    logger.debug("Dialog test started.")
    try:
        trigger_dialog_tests()
    except Exception:
        raise
    finally:
        testing_utils.close_gui()
        testing_utils.shutdown_environment(caplog=caplog, expected_warnings=0, expected_errors=0)


#TODO dialog tests in rafcon by mouse click and callback or only by callback and respective dialog objects response call

# Following tests are useful to preserve functionality
# RAFCONButtonDialog, RAFCONInputDialog and RAFCONCheckBoxTableDialog
# - trigger of LibraryTreeController.delete_button_clicked and check of button responses (results in state machines e.g)
# - trigger of MenuBarController.
#   -> check_sm_modified and check of button responses (results in state machines e.g)
#   -> check_sm_running and check of button responses (results in state machines e.g)
#   -> stopped_state_machine_to_proceed and check of button responses (results in state machines e.g)
# - trigger of StateMachinesEditorController
#   -> on_close_clicked and check of button responses (results in state machines e.g)
#   -> push_sm_running_dialog (in on_close_clicked) and check of button responses (results in state machines e.g)
# - trigger of StateSubstituteChooseLibraryDialog and check of button responses (results in state machines e.g)
# - trigger of SourceEditorController and check of button responses (results in state machines e.g)
#   -> and in open_text_window RAFCONInputDialog think about a check
# - trigger respective functions in gui helper state and state_machine (4 time ButtonDialog used)
# - trigger auto_backup and test RAFCONCheckBoxTableDialog response and results
#   -> 3 options as checkboxes and
#   -> 3 options as buttons
# RAFCONMessageDialog, and RAFCONColumnCheckboxDialog is not directly used in the RAFCON GUI but if there are
# library states those maybe should be tested, too

if __name__ == '__main__':
    # test_dialog_test(None)
    import pytest
    pytest.main([__file__, '-xs'])
