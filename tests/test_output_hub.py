from oth.libraries.output_hub import OutputHub


def test_print(capsys):

    logger = OutputHub(
        name="test_print",
        log_level="INFO",
        log_file=None,
        console_log_level="INFO",
        file_log_level="INFO",
    )

    logger.print("Print standard")
    captured = capsys.readouterr()
    assert captured.out == "Print standard\n"

    logger.print_vvv("Print very very very debug")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_log(caplog):

    logger = OutputHub(
        name="test_log",
        log_level="INFO",
        log_file=None,
        console_log_level="INFO",
        file_log_level="INFO",
    )

    logger.log_error("My log error")
    captured = caplog.text
    assert "My log error\n" in captured

    logger.log_error("My log debug")
    captured = caplog.text
    assert "My log debug\n" in captured
