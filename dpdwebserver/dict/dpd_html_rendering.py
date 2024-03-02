import re
from .models import Pali_Word, Pali_Root, Inflection_To_Headwords, Sandhi, Construction_Element, Construction_Element_Set



def make_meaning_html(i: Pali_Word) -> str:
    """Compile html of meaning_1 and literal meaning, or return meaning_2.
    Meaning_1 in <b>bold</b>"""

    if i.meaning_1:
        meaning: str = f"<b>{i.meaning_1}</b>"
        if i.meaning_lit:
            meaning += f"; lit. {i.meaning_lit}"
        return meaning
    else:
        # add bold to meaning_2, keep lit. plain
        if "; lit." in i.meaning_2:
            return re.sub("(.+)(; lit.+)", "<b>\\1</b>\\2", i.meaning_2)
        elif i.meaning_lit:
            return f"<b>{i.meaning_2}</b>; lit. {i.meaning_lit}"
        else:
            return f"<b>{i.meaning_2}</b>"


def render_headword_entry_html(w : Pali_Word) -> str:
    return w.pali_1 + "\r" + make_meaning_html(w)
