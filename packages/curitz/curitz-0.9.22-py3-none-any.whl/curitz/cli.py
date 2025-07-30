#!/usr/bin/env python3
import curses
import curses.textpad
import logging
import datetime
import argparse
import sys
import textwrap
import re
import time
import locale
import os
import traceback
import importlib

from curitz import __version__
from curitz.timed_cache import timed_cache
import curitz.textpad as utf8textpad
from curitz.culistbox import listbox, BoxSize, BoxElement
from zinolib.ritz import (
    ritz,
    parse_tcl_config,
    notifier as ritz_notifier,
    caseType,
    caseState,
    NotConnectedError,
    ProtocolError,
)


DEFAULT_PROFILE = "default"


# Hotfix to fix OSX reporting only "UTF-8" on LC_CTYPE
try:
    loc = locale.getlocale()
except ValueError:
    loc = None, None
if loc == (None, None) and os.environ["LC_CTYPE"] == "UTF-8":
    locale.setlocale(locale.LC_CTYPE, "en_US.UTF-8")
# End UTF-8 Hotfix

table_structure_no_id = (
    "{selected:1} "
    "{opstate:11} "
    "{admstate:8} "
    "{age:9} "
    "{downtime:3} "
    "{router:16} "
    "{port:14} "
    "{description}"
)
table_structure_id = (
    "{selected:1}{id:5} "
    "{opstate:11} "
    "{admstate:8} "
    "{age:9} "
    "{downtime:3} "
    "{router:16} "
    "{port:14} "
    "{description}"
)
table_structure = table_structure_no_id

cases = {}  # type: ignore
visible_cases = []
cases_selected = []
cases_selected_last = []  # type: ignore

screen_size = None
lb = None
session = None
notifier = None
casefilter = None

log = logging.getLogger("cuRitz")

# Try to import DNSpython
try:
    import dns.resolver
    import dns.reversename

    resolver = dns.resolver.Resolver()
    resolver.lifetime = 1
    resolver.timeout = 1
except ImportError as E:
    log.error("Failed to load DNSPython {}".format(E))


class Config:
    def __init__(self, dict_=None, **kwargs):
        if dict_:
            self.__dict__.update(dict_)
        self.__dict__.update(kwargs)


@timed_cache(minutes=60)
def dns_reverse_resolver(address):
    try:
        return str(resolver.query(dns.reversename.from_address(str(address)), "PTR")[0])
    except Exception:
        return str(address)


def updateStatus(screen, text):
    try:
        global screen_size
        screen.addnstr(0, screen_size.length - 16, "{:<16}".format(text[:16]), 100)
        screen.noutrefresh()
        screen.refresh()
        curses.doupdate()
    except curses.error:
        # This matches when the display size is quite small
        pass


def interfaceRenamer(s):
    s = s.replace("HundredGigE", "Hu")
    s = s.replace("GigabitEthernet", "Gi")
    s = s.replace("TenGigiabitEthernet", "Te")
    s = s.replace("TenGigE", "Te")
    s = s.replace("FastEthernet", "Fa")
    s = s.replace("Port-channel", "Po")
    s = s.replace("Loopback", "Lo")
    s = s.replace("Tunnel", "Tu")
    s = s.replace("Ethernet", "Eth")
    s = s.replace("Vlan", "Vl")
    return s


def uiShowLogWindow(screen, heading, lines, config):
    (screen_y, screen_x) = screen.getmaxyx()

    if screen_y < 30:
        box_h = screen_y - 10
    else:
        box_h = 30
    box = listbox(
        box_h, screen_x, 4, 0, current_selected_arrow=config.arrow, lr_border=False
    )

    # Display box on the midle of screen
    box.heading = heading
    box.clear()
    for _line in lines:
        box.add(_line)

    box.draw()
    screen.noutrefresh()
    curses.doupdate()

    while True:
        x = screen.getch()
        if x == -1:
            pass
        elif x == curses.KEY_UP:
            # Move up one element in list
            if box.active_element > 0:
                box.active_element -= 1

        elif x == curses.KEY_DOWN:
            # Move down one element in list
            if box.active_element < len(lines) - 1:
                box.active_element += 1

        elif x == curses.KEY_NPAGE:
            a = box.active_element + box.pagesize
            if a < len(box) - 1:
                box.active_element = a
            else:
                box.active_element = len(lines) - 1

        elif x == curses.KEY_PPAGE:
            a = box.active_element - box.pagesize
            if a > 0:
                box.active_element = a
            else:
                box.active_element = 0
        else:
            return
        box.draw()
        screen.noutrefresh()
        curses.doupdate()


def plugin_loader(plugin_name, filename):
    """Loads a plugin class from a external file"""
    try:
        log.info("Loading plugin from: {}".format(filename))
        spec = importlib.util.spec_from_file_location("plugin", filename)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        mod = getattr(foo, plugin_name)
        return mod
    except Exception:
        log.error(traceback.format_exc())
        return None


def import_plugins(dir):
    """Imports all plugins from a directory"""
    plugins = {}
    try:
        for _ in os.listdir(dir):
            if _.endswith(".py"):
                pl_name = _[0:-3]
                pl = plugin_loader(pl_name, dir + "/" + _)
                if pl:
                    try:
                        plugins[pl_name] = pl()
                    except Exception:
                        log.error(traceback.format_exc())
    except FileNotFoundError:
        pass
    return plugins


def actionPlugin(screen, caseid):
    plugins = {}
    plugins.update(
        import_plugins(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            + "/action_plugin"
        )
    )
    plugins.update(
        import_plugins(os.path.expanduser("/usr/share/curitz/action_plugin"))
    )
    plugins.update(import_plugins(os.path.expanduser("~/.curitz/action_plugin")))

    pkeys = list(plugins.keys())
    try:
        box = listbox(9, 62, 4, 9)
        for k in pkeys:
            box.add(plugins[k].description or "UNKNOWN PLUGIN")
        box.heading = "Select plugin"

        box.draw()
        screen.noutrefresh()
        curses.doupdate()

        while True:
            x = screen.getch()
            if x == -1:
                pass
            elif x == curses.KEY_UP:
                # Move up one element in list
                if box.active_element > 0:
                    box.active_element -= 1

            elif x == curses.KEY_DOWN:
                # Move down one element in list
                if box.active_element < len(box) - 1:
                    box.active_element += 1

            elif x == curses.KEY_ENTER or x == 13 or x == 10:
                if not pkeys:
                    log.debug("No plugin in list, exiting plugin manager")
                    return
                log.debug(pkeys)
                log.debug(box.active_element)
                try:
                    plugins[pkeys[box.active_element]].action(screen, cases[caseid])
                    return
                except Exception:
                    log.error("traceback while executing actionplugin:")
                    log.error(traceback.format_exc())
                    return

            elif x == 27 or x == ord("q") or x == ord("Q"):  # ESC and Q
                raise KeyboardInterrupt("ESC pressed")

            box.draw()
            curses.doupdate()
    except KeyboardInterrupt:
        box.clear()


def uiShowHistory(screen, caseid, config):
    global cases
    lines = []
    updateStatus(screen, "Waiting...")
    for line in cases[caseid].history:
        lines.append("{} {}".format(line["date"], line["header"]))
        for _line in line["log"]:
            for wrapped_line in textwrap.wrap(_line, 76, break_long_words=False):
                lines.append("  {}".format(wrapped_line))
    updateStatus(screen, "")
    uiShowLogWindow(
        screen,
        "History Case {} - {}".format(caseid, cases[caseid].get("descr", "")),
        lines,
        config,
    )


def uiShowLog(screen, caseid, config):
    global cases
    screen_x = screen.getmaxyx()[1]

    lines = []
    updateStatus(screen, "Waiting...")
    for line in cases[caseid].log:
        for _line in textwrap.wrap(
            "{} {}".format(line["date"], line["header"]),
            screen_x - 4,
            break_long_words=False,
        ):
            lines.append("{}".format(_line))
    updateStatus(screen, "")
    uiShowLogWindow(
        screen,
        "System Log Case {} - {}".format(caseid, cases[caseid].get("descr", "")),
        lines,
        config,
    )


def uiShowAttr(screen, caseid, config):
    global cases
    lines = []
    for line in cases[caseid].keys():
        lines.append("{:<15} : {:>}".format(line, repr(cases[caseid][line])))

    uiShowLogWindow(
        screen,
        "Case {} - {}".format(caseid, cases[caseid].get("descr", "")),
        lines,
        config,
    )


def strfdelta(tdelta, fmt):
    """
    Snipped from: https://stackoverflow.com/questions/8906926/formatting-python-timedelta-objects/17847006
    """
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def downtimeShortner(td):
    log.debug(td)
    if td.days > 0:
        return "{:2d}d".format(td.days)
    if td.seconds < 60:
        return "{:2d}s".format(td.seconds)
    if td.seconds / 60 < 60:
        return "{:2.0f}m".format(td.seconds / 60)
    if td.seconds / 60 / 60 < 60:
        return "{:2.0f}h".format(td.seconds / 60 / 60)


def uiloop(screen, config):
    global lb, session, notifier, cases, table_structure, screen_size, casefilter
    casefilter = ""

    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    screen.timeout(1 * 1000)  # mSec timeout
    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(13, curses.COLOR_GREEN, curses.COLOR_BLACK)
    except curses.error:
        sys.stderr.write("You need a color terminal to run cuRitz\n")
        return

    try:
        curses.curs_set(0)
    except Exception:
        pass
    screen_size = BoxSize(*screen.getmaxyx())
    if config.kiosk:
        lb = listbox(
            screen_size.height - 1,
            screen_size.length,
            1,
            0,
            current_selected_arrow=config.arrow,
        )
    else:
        lb = listbox(
            screen_size.height - 4,
            screen_size.length,
            1,
            0,
            current_selected_arrow=config.arrow,
        )

    screen.clear()
    screen.refresh()

    with ritz(
        config.Server, username=config.User, password=config.Secret, timeout=30
    ) as session:
        with ritz_notifier(session) as notifier:
            try:
                runner(screen, config)
            except KeyboardInterrupt:
                pass


def sortCases(casedict, field="lasttrans", filter=""):
    cases_sorted = []
    for key in sorted(
        cases,
        key=lambda k: (
            0 if cases[k].get("state") == caseState.IGNORED else 1,
            cases[k]._attrs[field],
        ),
    ):
        show = False
        if "type" in cases[key]._attrs:
            if re.match(
                ".*{}".format(filter), str(cases[key].get("type")), re.IGNORECASE
            ):
                show = True
        if "state" in cases[key]._attrs:
            if re.match(
                ".*{}".format(filter), str(cases[key].get("state")), re.IGNORECASE
            ):
                show = True
        if "router" in cases[key]._attrs:
            if re.match(
                ".*{}".format(filter), str(cases[key].get("router")), re.IGNORECASE
            ):
                show = True
        if "descr" in cases[key]._attrs:
            if re.match(
                ".*{}".format(filter), str(cases[key].get("descr")), re.IGNORECASE
            ):
                show = True
        if "port" in cases[key]._attrs:
            if re.match(
                ".*{}".format(filter), str(cases[key].get("port")), re.IGNORECASE
            ):
                show = True

        if show:
            cases_sorted.append(key)

    return reversed(cases_sorted)


def create_case_list(config):
    global cases, visible_cases, lb, cases_selected, casefilter
    visible_cases = cases.keys()
    sorted_cases = sortCases(cases, field="updated", filter=casefilter)

    lb.clear()
    lb.heading = table_structure.format(
        id="  ID",
        selected="S",
        opstate="OpState",
        admstate="AdmState",
        router="Router",
        port="Port",
        description="Description",
        age=" Age",
        downtime="Dt",
    )
    for c in sorted_cases:
        if c in visible_cases:
            case = cases[c]
            try:
                age = datetime.datetime.now() - case.opened
                common = {}
                common["id"] = case.id
                common["selected"] = "*" if case.id in cases_selected else " "
                common["router"] = case.router
                common["admstate"] = case.state.value[:7]
                common["age"] = strfdelta(age, "{days:2d}d {hours:02}:{minutes:02}")
                common["priority"] = case.priority
                if "downtime" in case.keys():
                    common["downtime"] = downtimeShortner(case.downtime)
                else:
                    common["downtime"] = ""
                color = []
                if config.nocolor:
                    cRed = [curses.A_BOLD]
                    cYellow = []
                    cBlue = []
                    cGreen = []
                else:
                    cRed = [curses.color_pair(10)]
                    cYellow = [curses.color_pair(11)]
                    cBlue = [curses.color_pair(12)]
                    cGreen = [curses.color_pair(13)]

                if case.type == caseType.PORTSTATE:
                    if case.state in [caseState.IGNORED]:
                        color = cBlue
                    elif case.state in [caseState.CLOSED]:
                        color = cGreen
                    elif (
                        case.portstate in ["down", "lowerLayerDown"]
                        and case.state == caseState.OPEN
                    ):
                        color = cRed
                    elif case.portstate in [
                        "down",
                        "lowerLayerDown",
                    ] and case.state in [caseState.WORKING, caseState.WAITING]:
                        color = cYellow
                    lb.add(
                        BoxElement(
                            case.id,
                            table_structure.format(
                                **common,
                                opstate="PORT %s" % case.portstate[0:5],
                                port=interfaceRenamer(case.port),
                                description=case.get("descr", ""),
                            ),
                            color,
                        )
                    )
                elif case.type == caseType.BGP:
                    if case.state in [caseState.IGNORED]:
                        color = cBlue
                    elif case.state in [caseState.CLOSED]:
                        color = cGreen
                    elif case.bgpos == "down" and case.state == caseState.OPEN:
                        color = cRed
                    elif case.bgpos == "down" and case.state in [
                        caseState.WORKING,
                        caseState.WAITING,
                    ]:
                        color = cYellow
                    lb.add(
                        BoxElement(
                            case.id,
                            table_structure.format(
                                **common,
                                opstate="BGP  %s" % case.bgpos[0:5],
                                port="AS{}".format(case.remote_as),
                                description="%s %s"
                                % (
                                    dns_reverse_resolver(str(case.remote_addr)),
                                    case.get("lastevent", ""),
                                ),
                            ),
                            color,
                        )
                    )
                elif case.type == caseType.BFD:
                    if case.state in [caseState.IGNORED]:
                        color = cBlue
                    elif case.state in [caseState.CLOSED]:
                        color = cGreen
                    elif case.bfdstate == "down" and case.state == caseState.OPEN:
                        color = cRed
                    elif case.bfdstate == "down" and case.state in [
                        caseState.WORKING,
                        caseState.WAITING,
                    ]:
                        color = cYellow

                    try:
                        port = case.bfdaddr
                    except Exception:
                        port = "ix {}".format(case.bfdix)
                    lb.add(
                        BoxElement(
                            case.id,
                            table_structure.format(
                                **common,
                                opstate="BFD  %s" % case.bfdstate[0:5],
                                port=str(port),
                                description="{}, {}".format(
                                    case.get("neigh_rdns"), case.get("lastevent")
                                ),
                            ),
                            color,
                        )
                    )
                elif case.type == caseType.REACHABILITY:
                    if case.state in [caseState.IGNORED]:
                        color = cBlue
                    elif case.state in [caseState.CLOSED]:
                        color = cGreen
                    elif (
                        case.reachability == "no-response"
                        and case.state == caseState.OPEN
                    ):
                        color = cRed
                    elif case.reachability == "no-response" and case.state in [
                        caseState.WORKING,
                        caseState.WAITING,
                    ]:
                        color = cYellow
                    lb.add(
                        BoxElement(
                            case.id,
                            table_structure.format(
                                **common,
                                opstate=case.reachability,
                                port="",
                                description="",
                            ),
                            color,
                        )
                    )
                elif case.type == caseType.ALARM:
                    if case.state in [caseState.IGNORED]:
                        color = cBlue
                    elif case.state in [caseState.CLOSED]:
                        color = cGreen
                    elif case.alarm_count > 0 and case.state == caseState.OPEN:
                        color = cRed
                    elif case.alarm_count > 0 and case.state in [
                        caseState.WORKING,
                        caseState.WAITING,
                    ]:
                        color = cYellow
                    lb.add(
                        BoxElement(
                            case.id,
                            table_structure.format(
                                **common,
                                opstate="ALRM {}".format(case.alarm_type),
                                port="",
                                description=case.lastevent,
                            ),
                            color,
                        )
                    )
                else:
                    log.error("Unable to create table for case {}".format(case.id))
                    log.error(repr(case._attrs))
            except Exception:
                log.exception(
                    "Exception while createing table entry for case {}".format(case.id)
                )
                log.fatal(repr(case._attrs))
                raise


def doKeepalive():
    try:
        session.case(0)
    except ProtocolError:
        pass


def runner(screen, config):
    global cases, cases_selected, screen_size, table_structure
    # Get all data for the first time
    cases = {}
    cases_selected = []

    draw(screen, config.Server)
    caselist = session.get_caseids()
    for c in caselist:
        try:
            case = session.case(c)
        except Exception:
            continue
        cases[case.id] = case
        elements = int((len(cases) / len(caselist)) * 20)
        screen.addstr(
            9,
            10,
            "[{:-<20}] Loaded {} of {} cases".format(
                "=" * elements, len(cases), len(caselist)
            ),
        )
        screen.refresh()

    screen.clear()
    screen.refresh()

    create_case_list(config)
    lb.draw()
    draw(screen, config.Server)

    update_ui = time.time()
    keepalive = time.time()
    selection_time = time.time()

    while True:
        x = screen.getch()

        if curses.is_term_resized(*screen_size):
            # Screen is resized
            update_ui = 999
            screen_size = BoxSize(*screen.getmaxyx())
            if config.kiosk:
                lb.resize(screen_size.height - 1, screen_size.length)
            else:
                lb.resize(screen_size.height - 4, screen_size.length)
            updateStatus(screen, "refreshed")

        while poll(config):
            update_ui = 999
            updateStatus(screen, "Polling")

        updateStatus(screen, "ch:{:3}".format(x))

        if x == -1:
            # Nothing happened, check for changes
            pass

        elif x == ord("q"):
            # Q pressed, Exit application
            return

        elif x == curses.KEY_UP:
            update_ui = 999
            # Move up one element in list
            if lb.active_element > 0:
                lb.active_element -= 1

        elif x == curses.KEY_DOWN:
            update_ui = 999
            # Move down one element in list
            if lb.active_element < len(lb) - 1:
                lb.active_element += 1

        elif x == curses.KEY_NPAGE:
            update_ui = 999
            a = lb.active_element + lb.pagesize
            if a < len(lb) - 1:
                lb.active_element = a
            else:
                lb.active_element = len(lb) - 1

        elif x == curses.KEY_PPAGE:
            update_ui = 999
            a = lb.active_element - lb.pagesize
            if a > 0:
                lb.active_element = a
            else:
                lb.active_element = 0

        elif x == ord("p"):
            if cases_selected:
                uiPollCases(cases_selected)
            else:
                uiPollCases([lb.active.id])

        elif x == ord("f"):
            # Change Filter
            uiSimpleFilterWindow(screen, config.UTF8)
            update_ui = 999
            lb.active_element = 0

        elif x == ord("m"):
            # Clear flapping
            if cases_selected:
                uiCFlapCases(cases_selected)
            else:
                uiCFlapCases([lb.active.id])

        elif x == ord("x"):
            update_ui = 999
            selection_time = time.time()

            # (de)select a element
            if lb.active.id in cases_selected:
                cases_selected.remove(lb.active.id)
            else:
                cases_selected.append(lb.active.id)

        elif x == ord("X"):
            update_ui = 999
            cases_tmp = list(cases_selected)
            cases_selected.clear()
            for case in cases_selected_last:
                if case in cases:
                    # Only add cases that still exists
                    cases_selected.append(case)
            cases_selected_last.clear()
            cases_selected_last.extend(cases_tmp)

        elif x == ord("c"):
            update_ui = 999
            # Clear selection
            cases_selected.clear()

        elif x == ord("u"):
            update_ui = 999
            # Update selected cases
            if cases_selected:
                uiUpdateCases(screen, cases_selected, config.UTF8)
            else:
                uiUpdateCases(screen, [lb.active.id], config.UTF8)

        elif x == ord("U"):
            update_ui = 999
            # Update selected cases
            if cases_selected:
                uiUpdateCases(screen, cases_selected, config.UTF8)
                uiSetState(screen, cases_selected, config)
            else:
                uiUpdateCases(screen, [lb.active.id], config.UTF8)
                uiSetState(screen, [lb.active.id], config)

        elif x == ord("i"):
            update_ui = 999
            # Update selected cases
            if "{id" in table_structure:
                table_structure = table_structure_no_id
            else:
                table_structure = table_structure_id

        elif x == ord("s"):
            update_ui = 999
            # Update selected cases
            if cases_selected:
                uiSetState(screen, cases_selected, config)
            else:
                uiSetState(screen, [lb.active.id], config)

        elif x == ord("y"):
            update_ui = 999
            cases_to_delete = []
            for id in cases:
                if cases[id].state == caseState.CLOSED:
                    cases_to_delete.append(id)
            for id in cases_to_delete:
                cases.pop(id, None)
                if id in cases_selected:
                    cases_selected.remove(id)
            if lb.active_element >= len(visible_cases):
                # If the current active element is beyond the item list end
                # then move it to the last visible element
                lb.active_element = len(visible_cases) - 1

        elif x == ord("1"):
            update_ui = 999
            actionPlugin(screen, lb.active.id)

        elif x == ord("="):
            update_ui = 999
            uiShowAttr(screen, lb.active.id, config)

        elif x == curses.KEY_ENTER or x == 10 or x == 13:  # [ENTER], CR or LF
            update_ui = 999
            uiShowHistory(screen, lb.active.id, config)

        elif x == ord("l"):
            # [ENTER], CR or LF
            update_ui = 999
            uiShowLog(screen, lb.active.id, config)

        elif x == 12:
            # CTRL + L
            update_ui = 999

        if cases_selected:
            if time.time() - selection_time > 300:
                cases_selected_last.clear()
                cases_selected_last.extend(cases_selected)
                cases_selected.clear()
                update_ui = 999

        if time.time() - update_ui > 10:
            update_ui = time.time()
            create_case_list(config)
            lb.draw()
            draw(screen, config.Server)

        if time.time() - keepalive > 60:
            keepalive = time.time()
            updateStatus(screen, "Sending keepalive")
            doKeepalive()
            updateStatus(screen, "")


def draw(screen, server):

    screen_size = BoxSize(*screen.getmaxyx())
    screen.erase()
    screen.addstr(
        0, 0, "cuRitz version {}  -  {}".format(__version__, server), curses.A_BOLD
    )
    screen.addstr(
        screen_size.height - 3,
        0,
        "<=>=Display attributes  m=Clear Flapping   i=Show/Hide ID   X=Restore last selection"[
            : screen_size.length - 1
        ],
    )  # noqa
    screen.addstr(
        screen_size.height - 2,
        0,
        "s=Set Stats u=Update History U=Update History and Set State f=Filter y=Remove Closed p=poll"[
            : screen_size.length - 1
        ],
    )  # noqa
    screen.addstr(
        screen_size.height - 1,
        0,
        "<ENTER>=Show history  <UP/DOWN>=Navigate q=Quit  l=Show Logs   x=(de)select  c=Clear selection"[
            : screen_size.length - 1
        ],
    )  # noqa
    screen.noutrefresh()
    lb.draw()
    curses.doupdate()


def uiPollCases(caseids):
    for case in caseids:
        cases[case].poll()


def uiCFlapCases(caseids):
    for case in caseids:
        if cases[case].type == caseType.PORTSTATE:
            cases[case].clear_flapping()


def uiUpdateCases(screen, caseids, utf8=False):
    update = uiUpdateCaseWindow(screen, len(caseids), utf8)
    if update:
        for case in caseids:
            cases[case].add_history(update)


def uiSetState(screen, caseids, config):
    new_state = uiSetStateWindow(screen, len(caseids), config)
    if new_state:
        for case in caseids:
            cases[case].set_state(new_state)
        # Remove selection when case is closed
        # It's not posilbe to change the case when it's closed on the server
        cases_selected_last.clear()
        cases_selected_last.extend(cases_selected)
        cases_selected.clear()
        create_case_list(config)


def uiSetStateWindow(screen, number, config):
    try:
        box = listbox(9, 62, 4, 9, current_selected_arrow=config.arrow)
        box.heading = "Set state on {} cases".format(number)
        box.add("DON'T CHANGE")
        box.add("Open")
        box.add("Working")
        box.add("wAiting")
        box.add("coNfirm-wait")
        box.add("Ignored")
        box.add("Closed")
        box.draw()
        screen.noutrefresh()
        curses.doupdate()

        while True:
            x = screen.getch()
            if x == -1:
                pass
            elif x == curses.KEY_UP:
                # Move up one element in list
                if box.active_element > 0:
                    box.active_element -= 1

            elif x == curses.KEY_DOWN:
                # Move down one element in list
                if box.active_element < len(box) - 1:
                    box.active_element += 1

            elif x == ord("o") or x == ord("O"):
                box.active_element = 1
            elif x == ord("w") or x == ord("W"):
                box.active_element = 2
            elif x == ord("a") or x == ord("A"):
                box.active_element = 3
            elif x == ord("n") or x == ord("N"):
                box.active_element = 4
            elif x == ord("i") or x == ord("I"):
                box.active_element = 5
            elif x == ord("c") or x == ord("C"):
                box.active_element = 6
            elif x == curses.KEY_ENTER or x == 13 or x == 10:
                if box.active_element == 0:
                    raise KeyboardInterrupt("No Change pressed")
                else:
                    return box.active.lower()
            elif x == 27 or x == ord("q") or x == ord("Q"):  # ESC and Q
                raise KeyboardInterrupt("ESC pressed")

            box.draw()
            curses.doupdate()

    except KeyboardInterrupt:
        box.clear()
    return ""


def uiUpdateCaseWindow(screen, number, utf8=False):
    (screen_y, screen_x) = screen.getmaxyx()

    border = curses.newwin(9, screen_x, 4, 0)
    textbox = curses.newwin(5, screen_x - 2, 6, 1)
    border.box()
    border.addstr(0, 1, "Add new history line")
    border.addstr(8, 1, "Ctrl+C to Abort    Ctrl+G to send    Ctrl+H = Backspace")
    border.addstr(1, 1, "{} case(s) selected for update".format(number))
    border.refresh()
    if utf8:
        p = utf8textpad.Textbox(textbox)
    else:
        p = curses.textpad.Textbox(textbox)

    try:
        curses.curs_set(1)
    except Exception:
        pass
    try:
        text = p.edit()
    except KeyboardInterrupt:
        return ""
    try:
        curses.curs_set(0)
    except Exception:
        pass

    return text


def uiSimpleFilterWindow(screen, utf8=False):
    global casefilter
    border = curses.newwin(9, 62, 4, 9)
    textbox = curses.newwin(1, 60, 6, 10)
    textbox.addstr(0, 0, casefilter)
    border.box()
    border.addstr(0, 1, "Really Simple Filter Generator")
    border.addstr(8, 1, "Ctrl+C to Abort    [ENTER] OK    Ctrl+H = Backspace")
    border.refresh()
    if utf8:
        p = utf8textpad.Textbox(textbox)
    else:
        p = curses.textpad.Textbox(textbox)

    try:
        curses.curs_set(1)
    except Exception:
        pass
    try:
        text = p.edit()
    except KeyboardInterrupt:
        return ""
    try:
        curses.curs_set(0)
    except Exception:
        pass

    casefilter = text.strip()
    log.debug(repr(casefilter))
    return True


def poll(config):
    global cases, cases_selected, notifier
    update = notifier.poll()
    if update:
        log.debug("Updating case: {}  {}".format(update.id, update.info))
        if update.id not in cases:
            if update.type != "state":
                # Update on unknown case thats not a state update
                # We just exit and wait for a state on that object
                return
        if update.type == "state":
            states = update.info.split(" ")
            if states[1] == "closed" and config.autoremove:
                log.debug(
                    "Automatically removing {} because of autoremove argument".format(
                        update.id
                    )
                )
                cases.pop(update.id, None)
                log.debug("List after remove: {}".format(cases.keys()))
                if update.id in cases_selected:
                    cases_selected.remove(update.id)
            else:
                cases[update.id] = session.case(update.id)
        elif update.type == "attr":
            cases[update.id] = session.case(update.id)
        elif update.type == "history":
            pass
        elif update.type == "log":
            pass
        elif update.type == "scavenged":
            cases.pop(update.id, None)
            if update.id in cases_selected:
                cases_selected.remove(update.id)
        else:
            log.debug("unknown notify entry: %s for id %s" % (update.type, update.id))
            return False
        return True
    return False


def parse_args(args_list=None):
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "-p", "--profile", default=DEFAULT_PROFILE, help="use Zino profile"
    )
    parser.add_argument("--profiles", action="store_true", help="List Zino profiles")
    parser.add_argument(
        "-c", "--config", default="~/.ritz.tcl", help="zino config file"
    )
    parser.add_argument(
        "--nocolor", action="store_true", help="Show client in black-n-white mode"
    )
    parser.add_argument("--debug", action="store_true", help="write debug logfile")
    parser.add_argument(
        "--kiosk", action="store_true", help="Hides all keybinding fields"
    )
    parser.add_argument(
        "--autoremove", action="store_true", help="Automatically remove closed cases"
    )
    parser.add_argument(
        "--arrow", action="store_true", help="Use arrow for current element marker"
    )
    encoding_parser = parser.add_mutually_exclusive_group()
    encoding_parser.add_argument(
        "--utf8",
        action="store_true",
        default=False,
        help="Force usage of UTF8 encoding",
    )
    encoding_parser.add_argument(
        "--ascii",
        action="store_false",
        dest="utf8",
        help="Force usage of ASCII encoding",
    )
    args = parser.parse_args(args_list)
    return args


def build_config(conf, args):
    profile = getattr(args, "profile", DEFAULT_PROFILE)
    config = Config(conf.get(profile, {}))
    config.UTF8 = getattr(args, "utf8", False)
    bool_config_args = ("kiosk", "autoremove", "nocolor")
    for arg in bool_config_args:
        setattr(config, arg, getattr(args, arg, False))
    config.arrow = ">" if getattr(args, "arrow", False) else ""
    return config


def main():
    args = parse_args()

    try:
        if args.config:
            conf = parse_tcl_config(args.config)
        else:
            conf = parse_tcl_config("~/.ritz.tcl")
    except FileNotFoundError as E:
        sys.stderr.write("Unable to load configuration for curitz:\n")
        sys.exit("{}".format(E))

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.FileHandler("curitz.log"))

    if args.profile:
        if args.profile not in conf.keys():
            print("List of zino profiles:")
            for profile in conf.keys():
                print("  {}".format(profile))
            sys.exit("Unable to find profile {}".format(args.profile))

    if args.profiles:
        print("List of zino profiles:")
        for profile in conf.keys():
            print("  {}".format(profile))
        sys.exit(0)

    config = build_config(conf, args)
    try:
        curses.wrapper(uiloop, config)
    except TimeoutError:
        sys.exit("Connection lost with the zino server...")

    except NotConnectedError as E:
        sys.exit("Unable to contact Zino: {}".format(E))


if __name__ == "__main__":
    main()
