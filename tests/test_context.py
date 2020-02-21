from queue import Queue

import sparcli.context


def test_that_context_emits_data_produced_event(mocker):
    queue = mocker.MagicMock(Queue)()
    context = sparcli.context.SparcliContext(queue)

    context.record(x=1)

    queue.put.assert_called_with(("data_produced", context, {"x": 1}))
