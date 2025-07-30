import sys
import re
import math
from functools import lru_cache
from typing import List, Callable, Optional, Union
from loguru import logger
from langid.langid import LanguageIdentifier, model
from sentence_splitter import SentenceSplitter
from sentsplit.segment import SentSplit
from mpire import WorkerPool

# Setup Loguru logger: remove default, add filtered stderr sink
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    filter=lambda record: "sentsplit" not in record["name"],  # exclude sentsplit logs
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{name}</cyan> | <level>{message}</level>"
)

LANGS_SENT_SPLIT = {
    "en", "fr", "de", "it", "pl", "pt", "lt", "ja", "ko", "ru", "zh", "tr"
}

LANGS_MOSES = {
    "ca", "cs", "da", "el", "es", "fi", "hu", "is", "lv",
    "nl", "no", "ro", "sk", "sl", "sv"
}

SENTENCE_END_REGEX = r".!?…。！？؟؛।"
CLAUSE_END_TRIGGERS = r";,)\]\”\’'\"`：—"

class Chunklet:
    """
    A robust and intelligent text chunker designed for large language models (LLMs),
    Retrieval-Augmented Generation (RAG) pipelines, and general text processing.
    Chunklet supports various chunking modes (sentence, token, hybrid) and applies
    overlap at the clause level to maintain semantic coherence.

    Key Features:
    - **Multilingual Support:** Utilizes `sentsplit` (CRF-based), `sentence-splitter` (Moses-based),
      and a robust regex fallback for accurate sentence segmentation across many languages.
    - **Hybrid Chunking:** Combines token and sentence limits with guaranteed, semantically-aware overlap.
    - **Clause-Level Overlap:** Overlap is applied at natural clause boundaries (e.g., commas, semicolons)
      to preserve the flow of meaning between chunks.
    - **Parallel Processing:** Efficiently chunks multiple texts using `mpire` for batch operations.
    - **Caching:** Optional LRU caching for `chunk` method to improve performance on repeated inputs.
    - **Pluggable Token Counters:** Allows users to define custom token counting logic (e.g., for GPT-2, BPE).
    """

    def __init__(
        self,
        verbose: bool = True,
        use_cache: bool = False,
        token_counter: Optional[Callable[[str], int]] = None,
    ):
        self.verbose = verbose
        self.use_cache = use_cache
        self.token_counter = token_counter
        self._language_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        self.sentence_end_regex = re.compile(r"\n|(?<=[" + SENTENCE_END_REGEX + r"])\s*")
        self.acronym_regex = re.compile(r"(\w|\d).\s?")
        self.abbreviation_regex = re.compile(r"\b[A-Z][a-z]{0,3}\.$")
        self.non_sentence_end_regex = re.compile(r"[^" + SENTENCE_END_REGEX + r"]*[a-z].*")
        self.clause_end_regex = re.compile(r"(?<=[" + CLAUSE_END_TRIGGERS + r"])\s")

    @staticmethod
    def _static_chunk_helper(
        text, lang, mode, max_tokens, max_sentences, token_counter, overlap_percent, offset
    ) -> List[str]:
        """
        Helper method for parallel processing in `batch_chunk`. Instantiates a temporary
        Chunklet and calls its internal `_chunk` method.

        Args:
            text (str): The text to chunk.
            lang (str): The language of the text (e.g., "en", "auto").
            mode (str): The chunking mode ("sentence", "token", "hybrid").
            max_tokens (int): Maximum number of tokens per chunk.
            max_sentences (int): Maximum number of sentences per chunk.
            token_counter (Callable[[str], int]): Function to count tokens.
            overlap_percent (Union[int, float]): Percentage of overlap between chunks.
            offset (int): Starting sentence offset for chunking.

        Returns:
            List[str]: A list of text chunks.
        """

    def _fallback_regex_splitter(self, text: str) -> List[str]:
        """
        A fallback sentence splitter using regular expressions. This is used when
        language-specific splitters are not available or language detection confidence is low.

        Args:
            text (str): The input text to split into sentences.

        Returns:
            List[str]: A list of sentences extracted using regex.
        """

    def _split_by_sentence(self, text: str, lang: str) -> List[str]:
        if lang == "auto":
            lang_detected, confidence = self._language_identifier.classify(text)
            if confidence < 0.7 and self.verbose:
                logger.warning(
                    f"Low confidence in language detection: '{lang_detected}' ({confidence:.2f})."
                )
            lang = lang_detected if confidence > 0.7 else lang

        if lang in LANGS_SENT_SPLIT:
            raw_sentences = SentSplit(lang).segment(text)
            return [s.rstrip("\n") for s in raw_sentences if s.strip()]

        if lang in LANGS_MOSES:
            return SentenceSplitter(language=lang).split(text)       
           
        if self.verbose:
            logger.warning(
                "Language not supported or detected with low confidence. Falling back to regex splitter."
            )
        return self._fallback_regex_splitter(text)      

    def _get_overlap_clauses(
        self, prev_chunk: List,  overlap_num: int,
    ) -> List[str]:
        all_clauses = []
        for sent in prev_chunk:
            clauses = self.clause_end_regex.split(sent)
            all_clauses.extend(c.rstrip() for c in clauses if c.strip())

        overlapped_clauses = all_clauses[-overlap_num:]
        if overlapped_clauses and overlapped_clauses[0][0].islower():
            overlapped_clauses[0] = "... " + overlapped_clauses[0]
        return overlapped_clauses

    def group_by_chunk(
        self,
        sentences: List[str],
        mode: str,
        max_tokens: int,
        max_sentences: int,
        overlap_percent: Union[int, float],
    ) -> List[List[str]]:
        chunks = []   
             
        if mode == "sentence":
            overlap_num = round(max_sentences * overlap_percent / 100)
            stride = max(1, max_sentences - overlap_num)   
            
            chunks.append(sentences[:max_sentences]) # first chunk has no prev chunk for overlapping                            
            for idx in range(max_sentences, len(sentences), stride):
                curr_chunk = sentences[idx : idx + stride]
                overlap_clauses = []  # To prevent unbound local error.
                if overlap_num > 0:
                    overlap_clauses = self._get_overlap_clauses(chunks[-1], overlap_num)
                chunks.append(overlap_clauses + curr_chunk)
        else:
            curr_chunk = []            
            token_count = 0
            sentence_count = 0
            for sentence in sentences:
                sentence_tokens = self.token_counter(sentence)
                if curr_chunk and (
                    token_count + sentence_tokens > max_tokens
                    or sentence_count + 1 > max_sentences
                ):
                    chunks.append(curr_chunk)  # chunk considered complete
                    
                    # prepare data for next chunk                                                                               
                    overlap_num = round(len(curr_chunk) * overlap_percent / 100)
                    curr_chunk = self._get_overlap_clauses(curr_chunk, overlap_num) 
                     
                    # treat them as sentence                                                                                                                          
                    token_count = sum(self.token_counter(s) for s in curr_chunk)
                    sentence_count = len(curr_chunk)
                curr_chunk.append(sentence)
                token_count += sentence_tokens
                sentence_count += 1
            if curr_chunk:
                chunks.append(curr_chunk)
        return ["\n".join(chunk) for chunk in chunks]
 
    def _chunk(
        self,
        text: str,
        lang: str,
        mode: str,
        max_tokens: int,
        max_sentences: int,
        overlap_percent: Union[int, float],
        offset: int,
    ) -> List[str]:
        if not text:
            return []
        if not (0 <= overlap_percent <= 85):
            raise ValueError("overlap_percent must be between 0 and 85")
        if max_sentences < 1:
            raise ValueError("max_sentences must be at least 1")
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if mode not in {"sentence", "token", "hybrid"}:
            raise ValueError("Invalid mode. Choose from 'sentence', 'token', or 'hybrid'.")
        if mode in {"token", "hybrid"} and self.token_counter is None:
            raise ValueError("A token_counter is required for token-based chunking.")
        if mode == "sentence":
            max_tokens = math.inf
        elif mode == "token":
            max_sentences = math.inf
            
        sentences  = self._split_by_sentence(text, lang)                
        if not sentences:
            return []
        if max_sentences == 1 and mode == "sentence":
            return sentences
            
        offset = round(offset)
        if offset >= len(sentences):
            if self.verbose:
                logger.warning(
                    f"Offset {offset} >= total sentences {len(sentences)}. Returning empty list."
                )
            return []
            
        sentences = sentences[offset:]        
        chunks = self.group_by_chunk(sentences, mode, max_tokens, max_sentences, overlap_percent)
        return chunks
        
    @lru_cache(maxsize=25)
    def _chunk_cached(
        self,
        text: str,
        lang: str,
        mode: str,
        max_tokens: int,
        max_sentences: int,
        overlap_percent: Union[int, float],
        offset: int,
    ) -> List[str]:
        return self._chunk(
            text=text,
            lang=lang,
            mode=mode,
            max_tokens=max_tokens,
            max_sentences=max_sentences,
            overlap_percent=overlap_percent,
            offset=offset,
        )

    def chunk(
        self,
        text: str,
        *,
        lang: str = "auto",
        mode: str = "hybrid",
        max_tokens: int = 512,
        max_sentences: int = 100,
        overlap_percent: Union[int, float] = 10,
        offset: int = 0,
    ) -> List[str]:
        if self.use_cache:
            return self._chunk_cached(
                text=text,
                lang=lang,
                mode=mode,
                max_tokens=max_tokens,
                max_sentences=max_sentences,
                overlap_percent=overlap_percent,
                offset=offset,
            )
        return self._chunk(
            text=text,
            lang=lang,
            mode=mode,
            max_tokens=max_tokens,
            max_sentences=max_sentences,
            overlap_percent=overlap_percent,
            offset=offset,
        )

    def batch_chunk(
        self,
        texts: List[str],
        *,
        lang: str = "auto",
        mode: str = "hybrid",
        max_tokens: int = 512,
        max_sentences: int = 100,
        overlap_percent: Union[int, float] = 20,
        offset: int = 0,
        n_jobs: Optional[int] = None,
    ) -> List[List[str]]:
        if not texts:
            return []

        args = [
            (
                text,
                lang,
                mode,
                max_tokens,
                max_sentences,
                self.token_counter,
                overlap_percent,
                offset,
            )
            for text in texts
        ]

        with WorkerPool(n_jobs=n_jobs) as pool:
            results = pool.map(self._static_chunk_helper, args)
        return results

    def preview_sentences(self, text: str, lang: str = "auto") -> List[str]:
        return self._split_by_sentence(text, lang)(text)


if __name__ == "__main__":
    import textwrap

    def simple_token_counter(sentence: str) -> int:
        return len(sentence.split())

    chunker = Chunklet(verbose=True, use_cache=True, token_counter=simple_token_counter)

    sample_text = textwrap.dedent(
        """
        CHAPTER I
        # Down the Rabbit-Hole
        
        Alice was very tired of sitting by her sister on the bank. She peeped into the book, but it had no pictures or conversations.
        Suddenly, a White Rabbit with pink eyes ran close by her. Alice heard it say, "Oh dear! I shall be late!"
        Curious, Alice followed it and saw it take a watch out of its waistcoat-pocket.
        The rabbit-hole went straight like a tunnel and Alice fell down a very deep well.
        As she fell, she noticed cupboards, book-shelves, maps, and Mr. Smith's Ipod.
        The Playlist contains:
            - two videos
            - one music
        Then she took down a jar labelled "ORANGE MARMALADE" but it was empty.
        Thinking of the fall, Alice wondered about the distance she had fallen and imagined strange places.
        She wished Dinah, her cat, was there with her.
        Suddenly, she landed on a heap of sticks and dry leaves, and the fall was over.
        """
    )

    print("=== Hybrid Mode (token and sentence limits with GUARANTEED overlap) ===")
    chunks = chunker.chunk(
        sample_text,
        lang="auto",
        mode="hybrid",
        max_tokens=50,
        max_sentences=7,
        overlap_percent=20,
    )    
    for i, c in enumerate(chunks):
        print(f"Chunk {i+1} (Tokens: {simple_token_counter(c)}, Sentences: {len(c.splitlines())}):\n{c}\n")