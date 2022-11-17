#
# Copyright (c) 2020 Saarland University.
#
# This file is part of AM Parser
# (see https://github.com/coli-saar/am-parser/).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import List, Dict, Tuple, Iterable, Union, Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    token: str
    replacement: str
    lemma: str
    pos_tag: str
    ner_tag: str
    fragment: str
    lexlabel: str
    typ: str
    head: int
    label: str
    aligned: bool
    range: Union[str, None]

    def __iter__(self):
        return iter([self.token, self.replacement, self.lemma, self.pos_tag, self.ner_tag, self.fragment, self.lexlabel,
                     self.typ, self.head, self.label, self.aligned, self.range])


@dataclass
class AMSentence:
    """Represents a sentence"""
    words: List[Entry]
    attributes: Dict[str, str]

    def __iter__(self):
        return iter(self.words)

    def __index__(self, i):
        """Zero-based indexing."""
        return self.words[i]

    def __eq__(self, other):
        if not isinstance(other, AMSentence):
            return False
        if len(self.words) != len(other.words):
            return False
        if self.attributes != other.attributes:
            return False

        return all(w == o for w, o in zip(self.words, other.words))

    def get_tokens(self, shadow_art_root) -> List[str]:
        r = [word.token for word in self.words]
        if shadow_art_root and r[-1] == "ART-ROOT":
            r[-1] = "."
        return r

    def get_replacements(self) -> List[str]:
        return [word.replacement for word in self.words]

    def get_pos(self) -> List[str]:
        return [word.pos_tag for word in self.words]

    def get_lemmas(self) -> List[str]:
        return [word.lemma for word in self.words]

    def get_ner(self) -> List[str]:
        return [word.ner_tag for word in self.words]

    def get_supertags(self) -> List[str]:
        return [word.fragment + "--TYPE--" + word.typ for word in self.words]

    def get_lexlabels(self) -> List[str]:
        return [word.lexlabel for word in self.words]

    def get_ranges(self) -> List[str]:
        return [word.range for word in self.words]

    def get_heads(self) -> List[int]:
        return [word.head for word in self.words]

    def get_edge_labels(self) -> List[str]:
        return [word.label if word.label != "_" else "IGNORE" for word in
                self.words]  # this is a hack :(, which we need because the dev data contains _

    def fix_dev_edge_labels(self) -> "AMSentence":
        """
        Return a copy of this sentence where edge labels that are "_" are replaced by "IGNORE".
        :return:
        """
        labels = self.get_edge_labels()
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, word.lexlabel,
                   word.typ, word.head, labels[i], word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_lexlabels(self, labels: List[str]) -> "AMSentence":
        assert len(labels) == len(
            self.words), f"number of lexical labels must agree with number of words but got {len(labels)} and {len(self.words)}"
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, labels[i],
                   word.typ, word.head, word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_labels(self, labels: List[str]) -> "AMSentence":
        assert len(labels) == len(
            self.words), f"number of lexical labels must agree with number of words but got {len(labels)} and {len(self.words)}"
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, word.lexlabel,
                   word.typ, word.head, labels[i], word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_supertags(self, supertags: List[str]):
        assert len(supertags) == len(
            self.words), f"number of supertags must agree with number of words but got {len(supertags)} and {len(self.words)}"
        split = [tag.split("--TYPE--") for tag in supertags]
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, split[i][0], word.lexlabel,
                   split[i][1], word.head, word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_supertag_tuples(self, supertags: List[Tuple[str, str]]):
        assert len(supertags) == len(
            self.words), f"number of supertags must agree with number of words but got {len(supertags)} and {len(self.words)}"
        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, supertags[i][0], word.lexlabel,
                   supertags[i][1], word.head, word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    def set_heads(self, heads: List[int]) -> "AMSentence":
        assert len(heads) == len(
            self.words), f"number of heads must agree with number of words but got {len(heads)} and {len(self.words)}"
        assert all(0 <= h <= len(self.words) for h in
                   heads), f"heads must be in range 0 to {len(self.words)} but got heads {heads}"

        return AMSentence(
            [Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, word.fragment, word.lexlabel,
                   word.typ, heads[i], word.label, word.aligned, word.range)
             for i, word in enumerate(self.words)], self.attributes)

    @staticmethod
    def get_bottom_supertag() -> str:
        return "_--TYPE--_"

    @staticmethod
    def split_supertag(supertag: str) -> Tuple[str, str]:
        return tuple(supertag.split("--TYPE--", maxsplit=1))

    def attributes_to_list(self) -> List[str]:
        return [f"#{key}:{val}" for key, val in self.attributes.items()]

    def check_validity(self):
        """Checks if representation makes sense, doesn't do AM algebra type checking"""
        assert len(self.words) > 0, "Sentence is empty"
        for entry in self.words:
            assert entry.head in range(len(self.words) + 1), f"head of {entry} is not in sentence range"
        has_root = any(w.label == "ROOT" and w.head == 0 for w in self.words)
        if not has_root:
            assert all((w.label == "IGNORE" or w.label == "_") and w.head == 0 for w in
                       self.words), f"Sentence doesn't have a root but seems annotated with trees:\n {self}"

    def strip_annotation(self) -> "AMSentence":
        return AMSentence([Entry(word.token, word.replacement, word.lemma, word.pos_tag, word.ner_tag, "_", "_",
                                 "_", 0, "IGNORE", word.aligned, word.range)
                           for word in self.words], self.attributes)

    def children_dict(self) -> Dict[int, List[int]]:
        """
        Return dictionary of children, 1-based.
        :return:
        """
        r = dict()
        for i in range(len(self.words)):
            head = self.words[i].head  # head is 1-based
            if self.words[i].label != "IGNORE":
                if head not in r:
                    r[head] = []
                r[head].append(i + 1)  # make current position 1-based
        return r

    def get_root(self) -> Optional[int]:
        """
        Returns the index of the root, 0-based.
        :return:
        """
        for i, e in enumerate(self.words):
            if e.head == 0 and e.label == "ROOT":
                return i

    def __str__(self):
        r = []
        if self.attributes:
            r.append("\n".join(f"#{attr}:{val}" for attr, val in self.attributes.items()))
        for i, w in enumerate(self.words, 1):
            fields = list(w)
            if fields[-1] is None:
                fields = fields[:-1]  # when token range not present -> remove it
            r.append("\t".join([str(x) for x in [i] + fields]))
        return "\n".join(r)

    def is_annotated(self):
        return not all((w.label == "_" or w.label == "IGNORE") and w.head == 0 for w in self.words)

    def __len__(self):
        return len(self.words)


def parse_amconll(fil, validate: bool = True) -> Iterable[AMSentence]:
    """
    Reads a file and returns a generator over AM sentences.
    :param validate:
    :param fil:
    :return:
    """
    expect_header = True
    new_sentence = True
    entries = []
    attributes = dict()
    for line in fil:
        line = line.rstrip("\n")
        if line.strip() == "":
            # sentence finished
            if len(entries) > 0:
                sent = AMSentence(entries, attributes)
                if validate:
                    sent.check_validity()
                yield sent
            new_sentence = True

        if new_sentence:
            expect_header = True
            attributes = dict()
            entries = []
            new_sentence = False
            if line.strip() == "":
                continue

        if expect_header:
            if line.startswith("#"):
                key, val = line[1:].split(":", maxsplit=1)
                attributes[key] = val
            else:
                expect_header = False

        if not expect_header:
            fields = line.split("\t")
            assert len(fields) == 12 or len(fields) == 13
            if len(fields) == 12:  # id + entry but no token ranges
                entries.append(
                    Entry(fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8],
                          int(fields[9]), fields[10], bool(fields[11]), None))
            elif len(fields) == 13:
                entries.append(
                    Entry(fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8],
                          int(fields[9]), fields[10], bool(fields[11]), fields[12]))