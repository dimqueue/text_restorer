from collections import defaultdict
from typing import Dict, List, Tuple
import heapq
import math


class TextRestorer:
    def __init__(self):
        self.dictionary = set()
        self.word_frequencies = {}
        self.candidate_store = CandidateStore()

    def load_dictionary(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word and word.isalpha():
                    self.dictionary.add(word)

    def load_frequencies(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        frequency = int(parts[0])
                        word = parts[1].lower()
                        if word and word.isalpha():
                            self.word_frequencies[word] = frequency
                    except ValueError:
                        continue

    def get_frequency_coefficient(self, word):
        frequency = self.word_frequencies.get(word, 1)
        coefficient = math.log(frequency + 1)
        return coefficient

    def match_pattern(self, pattern, word) -> bool:
        if len(pattern) != len(word):
            return False

        pattern_chars = []
        word_chars = []

        for i in range(len(pattern)):
            if pattern[i] != '*':
                pattern_chars.append(pattern[i])
                word_chars.append(word[i])

        pattern_chars.sort()
        word_chars.sort()

        return pattern_chars == word_chars

    def cost(self, pattern, word):
        base_weight = 0

        for i in range(len(word)):
            if pattern[i] == '*':
                continue
            elif word[i] == pattern[i]:
                base_weight += 10
            else:
                base_weight += 1

        pattern_weight = base_weight * len(pattern) ** 2
        frequency_coeff = self.get_frequency_coefficient(word)
        final_weight = pattern_weight * frequency_coeff

        return final_weight

    def get_all_words_for_position(self, damaged_text):
        for i in range(len(damaged_text)):
            max_length = min(10, len(damaged_text) - i)

            for j in range(1, max_length + 1):
                if i + j > len(damaged_text):
                    break
                pattern = damaged_text[i:i + j]
                self.find_words_for_pattern(i, pattern)

    def find_words_for_pattern(self, i, pattern):
        pattern_length = len(pattern)

        for word in self.dictionary:
            if len(word) == pattern_length:
                if self.match_pattern(pattern, word):
                    weight = self.cost(pattern, word)
                    self.candidate_store.add_candidate(i, word, weight)

    def restore_text_dp(self, damaged_text) -> Tuple[float, List[str]]:
        n = len(damaged_text)

        dp = [(-float('inf'), [])] * (n + 1)
        dp[n] = (0, [])

        for i in range(n - 1, -1, -1):
            candidates_at_position = self.candidate_store.get_candidates_at_position(i)

            for word, weight in candidates_at_position:
                word_length = len(word)
                if i + word_length <= n:
                    total_weight = weight + dp[i + word_length][0]

                    if total_weight > dp[i][0]:
                        new_words = [word] + dp[i + word_length][1]
                        dp[i] = (total_weight, new_words)

        return dp[0]

    def start(self, damaged_text):
        damaged_text = damaged_text.lower()

        self.get_all_words_for_position(damaged_text)

        max_weight, restored_words = self.restore_text_dp(damaged_text)

        print(f"Original text: {damaged_text}")
        print(f"Restored text: {' '.join(restored_words)}")

        return restored_words, max_weight

    def debug_positions(self, damaged_text):
        damaged_text = damaged_text.lower()
        self.get_all_words_for_position(damaged_text)

        for i in range(len(damaged_text)):
            candidates = self.candidate_store.get_candidates_at_position(i)
            if candidates:
                print(f"Position {i}: {candidates[:5]}")


class CandidateStore:
    def __init__(self, max_words_per_position: int = 30):
        self.positions: Dict[int, List[Tuple[float, str]]] = defaultdict(list)
        self.max_words = max_words_per_position

    def add_candidate(self, position: int, word: str, weight: float):
        heap = self.positions[position]

        if len(heap) < self.max_words:
            heapq.heappush(heap, (weight, word))
        elif weight > heap[0][0]:
            heapq.heapreplace(heap, (weight, word))

    def get_candidates_at_position(self, position: int) -> List[Tuple[str, float]]:
        heap = self.positions[position]
        return [(word, weight) for weight, word in sorted(heap, reverse=True)]


def main():
    text_restorer = TextRestorer()

    text_restorer.load_dictionary("popular.txt")
    text_restorer.load_frequencies("frequencies.txt")

    test_cases = [
        "Al*cew*sbegninnigtoegtver*triedofsitt*ngbyh*rsitsreonhtebnakandofh*vingnothi*gtodoonc*ortw*cesh*hdapee*edintoth*boo*h*rsiste*wasr*adnigbuti*hadnopictu*esorc*nve*sati*nsinitandwhatisth*useofab**kth*ughtAlic*withou*pic*u*esorco*versa*ions",
        "H*ll*Wrodl"
    ]

    for test_text in test_cases:
        print(f"\n{'=' * 50}")
        print(f"Testing: {test_text}")
        print(f"{'=' * 50}")

        text_restorer.start(test_text)


if __name__ == "__main__":
    main()
