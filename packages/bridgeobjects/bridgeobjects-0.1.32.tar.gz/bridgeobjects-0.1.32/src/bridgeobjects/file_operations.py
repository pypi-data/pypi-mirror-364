"""Provide file load and save functionality for PBN, RBN and lin formats."""


__all__ = ['load_pbn', 'save_pbn', 'pbn_as_text', 'load_lin', 'load_rbn',
           'parse_pbn', 'parse_lin', 'save_rbn', 'create_pbn_board']

from .event import Event
from . _parse_pbn_string import parse_pbn
from . _create_pbn_string import (create_pbn_event_list, create_pbn_board,
                                  create_rbn_list, _write_file)
from . _parse_rbn_string import parse_rbn
from ._parse_lin_string import parse_lin


def load_pbn(path: str) -> list[Event]:
    """Return a list of events from a  pbn file."""
    events = []
    file_text = _get_file_text(path)
    if file_text:
        events = parse_pbn(file_text)
    return events


def save_pbn(events: list[Event], path: str, append: bool = False) -> bool:
    """Save a list of events in pbn format."""
    success = False
    output = create_pbn_event_list(events, path)
    if output:
        success = bool(_write_file(output, path, append))
    return success


def pbn_as_text(events: list[Event]) -> list[str]:
    """Return an event in pbn format as a \n  delimited string."""
    output = create_pbn_event_list(events)
    return output


def load_rbn(path: str) -> list[Event]:
    """Load a rbn file to a list of events."""
    events = []
    file_text = _get_file_text(path)
    if file_text:
        events = parse_rbn(file_text)
    return events


def save_rbn(events: list[Event], path: str, append: bool = False) -> bool:
    """Save a list of events in rbn format."""
    success = False
    output = create_rbn_list(events)
    if output:
        success = bool(_write_file(output, path, append))
    return success


def load_lin(path: str) -> list[Event]:
    """Load a lin file to a list of events."""
    events = []
    file_text = _get_file_text(path)
    if file_text:
        events = parse_lin(file_text)
    return events


def _get_file_text(path: str) -> list[str]:
    """Return the file text lines as a list."""
    file_text = []
    try:
        with open(path, "r") as pbn_file:
            raw_text = pbn_file.read()
            raw_text = raw_text.replace(chr(13), '')
            raw_text = raw_text.replace('\r', '')
            file_text = raw_text.split('\n')
    except FileNotFoundError as error:
        raise FileNotFoundError(f'{path} is not a file') from error
    return file_text
