from pathlib import Path

from CommonSpell.encoder import Encoder
from CommonSpell.bo.tokenizer_bo import TibetanTokenizer, TibetanNormalizer
from CommonSpell.aligners.fdmp import FDMPaligner
from CommonSpell.input_filters.pattern_filter import PatternInputFilter
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher
from CommonSpell.serializers.hfml import HFMLSerializer
from CommonSpell.serializers.plain_text import PlainTextSerializer
from CommonSpell.commonspeller import CommonSpeller