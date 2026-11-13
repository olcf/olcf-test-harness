import os

os.environ["OTHCTL_MACHINE"] = "minimal_machine"

from oth.libraries.output_hub import OutputHub


def test_log_and_print(capsys):

    logger = OutputHub(
        name="test_log_and_print",
        log_level="INFO",
        log_file=None,
        console_log_level="INFO",
        file_log_level="INFO",
    )

    logger.print("Print standard")
    captured = capsys.readouterr()
    assert captured.out == "Print standard\n"

    logger.log_error("Log error")
    captured = capsys.readouterr()
    assert captured.out == "Log error\n"

    logger.log_error("Log debug")
    captured = capsys.readouterr()
    assert captured.out == "Log debug\n"
