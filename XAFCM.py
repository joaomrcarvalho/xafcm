from math import log2, pow
from ContextLine import ContextLine
from pympler import asizeof


class XAFCM(object):

    def __init__(self, alphab_size, k, d, word_size=None, alpha="auto", p=0.9):
        self.word_size = word_size
        self.number_of_bits = 0.0
        self.d = d
        self.k = k

        if alpha == "auto" or alpha is None:
            self.alpha = 1.1
            prob = 0

            # while prob < p:
            while prob < pow(p, self.d):
                self.alpha /= 1.1
                prob = (1 + self.alpha) / (1 + self.alpha * pow(alphab_size, self.d))
            print("auto alpha = %e" % self.alpha)
        # if alpha is provided
        else:
            self.alpha = alpha

        self.alphabet_size = alphab_size
        self.model_learned = dict()
        self.list_of_bits_per_symbol = []
        self._default_lidstone = self.alpha / (self.alpha * pow(self.alphabet_size, self.d))
        self._default_lidstone_part1 = self.alpha
        self._default_lidstone_part2 = self.alpha * pow(self.alphabet_size, self.d)

    def _reset_model(self):
        self.model_learned = dict()

    def _reset_number_of_bits(self):
        self.number_of_bits = 0

    def learn_model_from_text_files(self, list_of_path_text_files):
        self._reset_model()

        data = ""
        for path_text_file in list_of_path_text_files:
            with open(path_text_file, "r") as my_file:
                data += my_file.read()

        self.learn_models_from_string(data.upper())

    def learn_model_from_text_file(self, path_text_file):
        self._reset_model()

        data = ""
        with open(path_text_file, "r") as my_file:
            data += my_file.read()
        self.learn_models_from_string(data.upper())

    def learn_models_from_string(self, np_string):
        tmp_word_size = self.word_size
        if self.word_size is None:
            tmp_word_size = len(np_string)

        assert(len(np_string) % tmp_word_size == 0)

        self._reset_model()
        # print(np_string)

        aux_list_k = list(reversed(range(1, self.d + 1)))
        aux_list_l = list(reversed(range(self.d + 1, self.d + self.k + 1)))

        for curr_word_start_index in range(0, len(np_string), tmp_word_size):
            word = np_string[curr_word_start_index:curr_word_start_index+tmp_word_size]

            # print("word = %s" % word)
            for i in range(0, len(word)):

                curr_string_for_l = ""
                for curr_l in aux_list_l:
                    curr_string_for_l += word[(i-curr_l) % len(word)]

                curr_string_for_k = ""
                for curr_k in aux_list_k:
                    curr_string_for_k += word[(i-curr_k) % len(word)]

                if not ContextLine.check_key_in_dict(curr_string_for_l, self.model_learned):
                    default_context_line = ContextLine(context_word=curr_string_for_l)
                    self.model_learned[curr_string_for_l] = default_context_line

                self.model_learned[curr_string_for_l].increment_symbol(curr_string_for_k)

    def print_models_learned(self):
        print("Model learned:")
        from operator import itemgetter
        for item in sorted(self.model_learned.items(), key=itemgetter(1)):
            print(item[1])

    def get_memory_size_used_mbytes(self):
        mem_used_bytes = asizeof.asizeof(self.model_learned)
        mem_used_mbytes = mem_used_bytes / (1024 * 1024)
        return mem_used_mbytes

    def print_memory_size_used_mbytes(self):
        print("RAM used: %.2fMB" % self.get_memory_size_used_mbytes())

    def print_details_of_models_learned(self):
        different_contexts_found = self.model_learned.keys()
        number_of_different_contexts_found = len(different_contexts_found)
        print("Found %s different combinations of contexts for k = %s." % (number_of_different_contexts_found, self.k))

    def lidstone_probability_part1(self, current_context_word, symbol):
        try:
            model_line = self.model_learned[current_context_word]
        # in case this word never appeared in the reference model
        except KeyError as e:
            return self._default_lidstone_part1

        try:
            tmp = model_line.cols[symbol]
        # in case this symbol never appeared for this specific word
        except KeyError as e:
            tmp = 0

        return tmp + self.alpha

    def lidstone_probability_part2(self, current_context_word, symbol):
        try:
            model_line = self.model_learned[current_context_word]
        # in case this word never appeared in the reference model
        except KeyError as e:
            return self._default_lidstone_part2

        return model_line.cols['total'] + pow(self.alphabet_size, self.d) * self.alpha

    def lidstone_estimate_probability_for_symbol(self, current_context_word, symbol):
        try:
            model_line = self.model_learned[current_context_word]
        # in case this word never appeared in the reference model
        except KeyError as e:
            return self._default_lidstone

        try:
            tmp = model_line.cols[symbol]
        # in case this symbol never appeared for this specific word
        except KeyError as e:
            tmp = 0

        return (tmp + self.alpha) / \
               (model_line.cols['total'] + pow(self.alphabet_size, self.d) * self.alpha)

    def compress_text_file(self, path_text_file, based_on_model=True):
        self._reset_number_of_bits()

        data = ""
        with open(path_text_file, "r") as my_file:
            data += my_file.read()
        if based_on_model:
            return self.compress_string_based_on_models(data.upper())
        # compress itself
        else:
            return self.compress_string_based_on_counts_so_far(data.upper())

    def compress_string_based_on_models(self, string_to_compress):

        # compress based on self.model_learned
        self._reset_number_of_bits()
        self.list_of_bits_per_symbol = []

        tmp_word_size = self.word_size
        if self.word_size is None:
            tmp_word_size = len(string_to_compress)

        assert(len(string_to_compress) % tmp_word_size == 0)
        assert(self.model_learned != dict())

        aux_list_next_seq = list(reversed(range(0, self.d)))
        aux_list_current_context_k = list(reversed(range(self.d, self.d + self.k)))

        for curr_word_start_index in range(0, len(string_to_compress), tmp_word_size):
            word_to_process = string_to_compress[curr_word_start_index:curr_word_start_index+tmp_word_size]

            # init curr_string
            for i in range(0, len(word_to_process), self.d):
                next_sequence = ""
                current_context_k = ""

                for i_tmp in aux_list_next_seq:
                    next_sequence += word_to_process[(i - i_tmp) % len(word_to_process)]

                for i_tmp in aux_list_current_context_k:
                    current_context_k += word_to_process[(i - i_tmp) % len(word_to_process)]

                prob = self.lidstone_estimate_probability_for_symbol(current_context_k, next_sequence)
                tmp_bits_needed = - log2(prob)
                self.list_of_bits_per_symbol.append(tmp_bits_needed)
                self.number_of_bits += tmp_bits_needed

        return self.list_of_bits_per_symbol, self.number_of_bits


