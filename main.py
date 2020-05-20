from typing import List
import operator
import itertools
from bs4 import BeautifulSoup as BS, Tag
import click
import spacy
from dataclasses import dataclass
import warnings

warnings.filterwarnings("ignore")  # nlp is too noisy


def get_xpath_from_soup_element(element):
    """a helper method I needed but didn't find in BS :)"""
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


@dataclass
class ElementProperties:
    title: str = None
    xpath: str = None
    tag: str = None
    classes: str = None
    href: str = None
    onclick: str = None
    text: str = None
    id: str = None

    def action_type(self):
        if any(word in self.classes for word in ['dander', 'warning', 'error']):
            return 'bad'
        elif any(word in self.classes for word in ['ok', 'success']):
            return 'good'
        elif any(word in self.classes for word in ['info', 'alert', 'default']):
            return 'neutral'
        return None

    @classmethod
    def from_bs_element(cls, el: Tag):
        return cls(
            text=el.get_text(),
            classes=el.get('class'),
            onclick=el.get('onclick'),
            href=el.get('href'),
            tag=el.name,
            title=el.get('title'),
            id=el.get('id'),
            xpath=get_xpath_from_soup_element(el)
        )


def jakarta_similarity(prop):
    def feature(origin: ElementProperties, target: ElementProperties):
        origin_prop = getattr(origin, prop) or []
        target_prop = getattr(target, prop) or []
        return len(set(origin_prop) & set(target_prop)) / len(origin_prop)

    return feature


def nlp_similarity(prop):
    def feature(origin: ElementProperties, target: ElementProperties):
        getattr(origin, prop) or ""
        nlp_origin_text = nlp(getattr(origin, prop) or "")
        nlp_target_text = nlp(getattr(target, prop) or "")
        return nlp_origin_text.similarity(nlp_target_text)

    return feature


def equality(prop):
    def feature(origin: ElementProperties, target: ElementProperties):
        return float(getattr(origin, prop) == getattr(target, prop))

    return feature


nlp = spacy.load('en')
tag_matching = {'a': ['a'], 'div': ['div'], 'span': ['span']}

# I called this human learning :) those scores ideally should be adjusted
features = [
    (nlp_similarity('title'), 1.0),
    (nlp_similarity('text'), 1.0),
    (nlp_similarity('xpath'), 1.0),
    (jakarta_similarity('classes'), 1.0),
    (nlp_similarity('onclick'), 1.0),
    (equality('tag'), 1.0),
    (equality('action_type'), 1.0)
]


def find_candidates(page: BS, origin: ElementProperties) -> List[ElementProperties]:
    tags = tag_matching.get(origin.tag, '*')
    return [
        ElementProperties.from_bs_element(el)
        for el in itertools.chain(*[page.find_all(tag) for tag in tags])
    ]


def get_origin_element_properties(el):
    ElementProperties.from_bs_element(el)


def get_element_features_score(origin: ElementProperties, target: ElementProperties):
    sum = 0
    for feature, coef in features:
        sum += feature(origin, target) * coef

    return sum


def find_that_guy(origin_id, origin_path, target_path):
    # don't worry, file with be automatically closed :)
    origin_page = BS(open(origin_path).read())
    target_page = BS(open(target_path).read())
    origin_el = ElementProperties.from_bs_element(origin_page.find(id=origin_id))
    candidates = find_candidates(target_page, origin_el)
    candidates_with_features = [
        (el, get_element_features_score(origin_el, el))
        for el in candidates
    ]
    best, _ = max(candidates_with_features, key=operator.itemgetter(1))

    return best


@click.command()
@click.argument('origin_id')
@click.argument('origin_path')
@click.argument('target_path')
def command(origin_id, origin_path, target_path):
    print(find_that_guy(origin_id, origin_path, target_path))


if __name__ == '__main__':
    command()
