import sparcli


def test_that_it_can_be_used_as_a_context_manager(mocker):
    controller = mocker.patch("sparcli.get_controller", autospec=True).return_value
    SparcliContext = mocker.patch("sparcli.context.SparcliContext", autospec=True)

    with sparcli.ctx() as ctx:
        ctx.record({})

    assert SparcliContext.return_value.__exit__.called


def test_that_it_can_wrap_an_iterable(mocker):
    ctx = mocker.patch("sparcli.ctx", autospec=True).return_value
    ctx = ctx.__enter__.return_value
    numbers = [1, 2, 3]

    output = list(sparcli.gen(numbers, "x"))

    assert numbers == output
    ctx.record.assert_any_call(x=1)
    ctx.record.assert_any_call(x=2)
    ctx.record.assert_any_call(x=3)
