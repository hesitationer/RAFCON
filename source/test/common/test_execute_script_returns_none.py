import pytest
import signal

from rafcon.statemachine.storage import storage
from rafcon.statemachine.states.hierarchy_state import HierarchyState
from rafcon.statemachine.states.execution_state import ExecutionState
import rafcon.mvc.singleton
import testing_utils


def test_execute_script_returns_none(caplog):
    testing_utils.remove_all_libraries()

    testing_utils.test_multithrading_lock.acquire()
    rafcon.statemachine.singleton.state_machine_manager.delete_all_state_machines()
    signal.signal(signal.SIGINT, rafcon.statemachine.singleton.signal_handler)

    rafcon.statemachine.singleton.library_manager.initialize()

    state_machine = storage.load_state_machine_from_path(testing_utils.get_test_sm_path("unit_test_state_machines/return_none_test_sm"))

    rafcon.statemachine.singleton.state_machine_manager.add_state_machine(state_machine)
    if testing_utils.sm_manager_model is None:
        testing_utils.sm_manager_model = rafcon.mvc.singleton.state_machine_manager_model

    # load the meta data for the state machine
    testing_utils.sm_manager_model.get_selected_state_machine_model().root_state.load_meta_data()

    rafcon.statemachine.singleton.state_machine_execution_engine.start()
    rafcon.statemachine.singleton.state_machine_execution_engine.join()

    assert state_machine.root_state.final_outcome.outcome_id == 0

    testing_utils.reload_config()
    testing_utils.test_multithrading_lock.release()
    testing_utils.assert_logger_warnings_and_errors(caplog, 0, 1)


if __name__ == '__main__':
    pytest.main([__file__])