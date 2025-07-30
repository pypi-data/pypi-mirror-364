from devremind1.remind import remind_every

def test_remind_exists():
    assert callable(remind_every)
