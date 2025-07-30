#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import functools
import pathlib
import typing

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.page_layout import PageLayoutSettings
    from mtg_proxy_printer.model.document import Document

from mtg_proxy_printer.model.card import CardList
from ._interface import DocumentAction, IllegalStateError, ActionList, Self
from .page_actions import ActionNewPage
from .card_actions import ActionAddCard
from .new_document import ActionNewDocument
from .edit_document_settings import ActionEditDocumentSettings

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "ActionLoadDocument",
]


class ActionLoadDocument(DocumentAction):
    COMPARISON_ATTRIBUTES = ["save_path", "loaded_cards", "page_layout"]

    def __init__(self, save_path: pathlib.Path, loaded_cards: typing.List[CardList], page_layout: "PageLayoutSettings"):
        self.save_path = save_path
        self.page_layout = page_layout
        self.actions: ActionList = []
        self.loaded_cards = loaded_cards

    def apply(self, document: "Document") -> Self:
        if self.actions:
            raise IllegalStateError("Cannot apply action twice")
        self.actions.append(ActionNewDocument().apply(document))
        self.actions.append(ActionEditDocumentSettings(self.page_layout).apply(document))
        document.set_currently_edited_page(document.pages[0])
        if self.loaded_cards:
            for copies, card in self._batch_page_content(self.loaded_cards[0]):
                self.actions.append(ActionAddCard(card, copies).apply(document))
            if page_count := len(self.loaded_cards)-1:
                self.actions.append(ActionNewPage(count=page_count, content=self.loaded_cards[1:]).apply(document))
        return super().apply(document)

    @staticmethod
    def _batch_page_content(cards: CardList):
        if not cards:
            return
        cards.append(object())  # sentinel, will not be returned
        count, last = 0, cards[0]
        for card in cards:
            if card == last:
                count += 1
            else:
                yield count, last
                count, last = 0, card
        if count:
            yield count, last



    def undo(self, document: "Document") -> Self:
        for action in reversed(self.actions):
            action.undo(document)
        self.actions.clear()
        return self

    @functools.cached_property
    def as_str(self):
        page_count = len(self.loaded_cards)
        card_count = sum(map(len, self.loaded_cards))
        cards_total = self.translate(
            "ActionLoadDocument. Card total", "with %n card(s) total",
            "Undo/redo tooltip text. Will be inserted as {cards_total}", card_count
        )
        return self.translate(
            "ActionLoadDocument",
            "Load document from '{save_path}',\ncontaining %n page(s) {cards_total}",
            "Undo/redo tooltip text.", page_count
        ).format(save_path=self.save_path, cards_total=cards_total)
