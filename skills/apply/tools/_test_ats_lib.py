"""Сетка для ats_lib.upload_resume — класс «заявка ушла без резюме» (замер 04.09, волна 22).

На новых формах Ashby ПЕРВЫЙ input[type=file] на странице — виджет «Autofill from resume».
Старый код при отсутствии именованного поля брал именно его: файл уезжал в автозаполнение,
поле резюме оставалось пустым, и форма МОЛЧА отправлялась без CV (PermitFlow, первый прогон).

A1 именованное поле _systemfield_resume используется, когда оно есть
A2 нет именованного → берём поле, чей лейбл говорит «Resume», а не первый на странице
A3 на странице ТОЛЬКО автофилл-виджет → отказ RESUME-FIELD-NOT-FOUND, ФАЙЛ НЕ ОТПРАВЛЕН
A4 после загрузки имя файла ищется в самом поле резюме → нет чипа = CHIP-MISSING, не «OK»

Прогон: python3 _test_ats_lib.py  (0 сети, 0 браузера — драйвер подменён заглушкой)
Мутант, на котором сетка обязана краснеть: возврат слепого фолбэка
`or d.find_elements(By.CSS_SELECTOR, "input[type=file]")`.
Updated: 2026-09-04.
"""
import os, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# selenium может быть не установлен на узле — подменяем ровно то, что импортирует ats_lib
if "selenium" not in sys.modules:
    sel = types.ModuleType("selenium")
    wd = types.ModuleType("selenium.webdriver")
    common = types.ModuleType("selenium.webdriver.common")
    by = types.ModuleType("selenium.webdriver.common.by")
    keys = types.ModuleType("selenium.webdriver.common.keys")
    action_chains = types.ModuleType("selenium.webdriver.common.action_chains")
    ff = types.ModuleType("selenium.webdriver.firefox")
    ffopt = types.ModuleType("selenium.webdriver.firefox.options")
    ffsvc = types.ModuleType("selenium.webdriver.firefox.service")
    support = types.ModuleType("selenium.webdriver.support")
    ui = types.ModuleType("selenium.webdriver.support.ui")
    ec = types.ModuleType("selenium.webdriver.support.expected_conditions")
    exc = types.ModuleType("selenium.common.exceptions")
    common_mod = types.ModuleType("selenium.common")

    class By:
        CSS_SELECTOR = "css"; XPATH = "xpath"; TAG_NAME = "tag"; ID = "id"; NAME = "name"
    by.By = By
    keys.Keys = type("Keys", (), {"ESCAPE": "esc", "ENTER": "enter", "TAB": "tab", "DELETE": "del", "COMMAND": "cmd"})
    action_chains.ActionChains = object
    ffopt.Options = object
    ffsvc.Service = object
    ui.WebDriverWait = object
    ec.presence_of_element_located = lambda *a, **k: None
    for name in ("WebDriverException", "TimeoutException", "NoSuchElementException",
                 "StaleElementReferenceException", "ElementClickInterceptedException",
                 "ElementNotInteractableException", "SessionNotCreatedException"):
        setattr(exc, name, type(name, (Exception,), {}))
    wd.Firefox = object
    for mod, path in ((sel, "selenium"), (wd, "selenium.webdriver"), (common, "selenium.webdriver.common"),
                      (by, "selenium.webdriver.common.by"), (keys, "selenium.webdriver.common.keys"),
                      (action_chains, "selenium.webdriver.common.action_chains"),
                      (ff, "selenium.webdriver.firefox"), (ffopt, "selenium.webdriver.firefox.options"),
                      (ffsvc, "selenium.webdriver.firefox.service"), (support, "selenium.webdriver.support"),
                      (ui, "selenium.webdriver.support.ui"), (support, "selenium.webdriver.support"),
                      (ec, "selenium.webdriver.support.expected_conditions"),
                      (common_mod, "selenium.common"), (exc, "selenium.common.exceptions")):
        sys.modules[path] = mod

import ats_lib

fails = []
SENT = []


def check(name, cond, detail=""):
    print(("  ✅ " if cond else "  ❌ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        fails.append(name)


class FakeInput:
    def __init__(self, tag):
        self.tag = tag

    def send_keys(self, path):
        SENT.append((self.tag, path))


class FakeDriver:
    """named=есть ли input[name=_systemfield_resume]; labelled=есть ли поле с лейблом Resume;
    chip=появится ли имя файла в поле резюме после загрузки."""

    def __init__(self, named=False, labelled=False, chip=True):
        self.named, self.labelled, self.chip = named, labelled, chip

    def find_elements(self, how, sel):
        if "_systemfield_resume" in sel:
            return [FakeInput("named")] if self.named else []
        if sel == "input[type=file]":
            return [FakeInput("autofill-widget")]      # на странице он ВСЕГДА первый
        return []

    def execute_script(self, script, *a):
        if "bad = /autofill" in script:                # поиск поля по лейблу
            return [FakeInput("labelled-resume")] if self.labelled else []
        return "Anton-CV.pdf attached" if self.chip else "Resume\nUpload"


def main():
    path = "/tmp/Anton-CV.pdf"

    SENT.clear()
    r = ats_lib.upload_resume(FakeDriver(named=True), path, settle=0)
    check("A1 именованное поле используется", r == "OK", r)
    check("A1b файл ушёл именно в него", SENT == [("named", path)], SENT)

    SENT.clear()
    r = ats_lib.upload_resume(FakeDriver(named=False, labelled=True), path, settle=0)
    check("A2 без именованного берём поле с лейблом Resume", r == "OK", r)
    check("A2b файл НЕ ушёл в автофилл-виджет",
          SENT == [("labelled-resume", path)], SENT)

    SENT.clear()
    r = ats_lib.upload_resume(FakeDriver(named=False, labelled=False), path, settle=0)
    check("A3 только автофилл на странице → честный отказ",
          isinstance(r, str) and r.startswith("RESUME-FIELD-NOT-FOUND"), r)
    check("A3b при отказе файл НЕ отправлен никуда (иначе заявка уйдёт без CV)", SENT == [], SENT)

    SENT.clear()
    r = ats_lib.upload_resume(FakeDriver(named=True, chip=False), path, settle=0)
    check("A4 нет чипа в поле резюме → CHIP-MISSING, а не OK",
          isinstance(r, str) and r.startswith("CHIP-MISSING"), r)

    print(f"\n{'ВСЁ ЗЕЛЁНОЕ' if not fails else 'КРАСНОЕ: ' + ', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
