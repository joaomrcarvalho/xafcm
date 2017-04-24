class ContextLine(object):

    def __init__(self, context_word):
        self.context_word = context_word
        self.cols = dict()
        self.cols['total'] = 0

    def increment_symbol(self, symbol):
        # if symbol in self.cols.keys():
        if self.check_key_in_dict(symbol, self.cols):
            self.cols[symbol] += 1
        else:
            self.cols[symbol] = 1

        self.cols["total"] += 1

    def __str__(self):
        res = ""
        res += str("%s   ---- " % self.context_word)
        for key in sorted(self.cols.keys()):
            res += str("   %s ->%5s  " % (key, self.cols[key]))
        return res

    def __lt__(self, other):
        return self.cols['total'] < other.cols['total']

    @staticmethod
    def check_key_in_dict(key, some_dict):
        try:
            tmp = some_dict[key]
            return True
        except KeyError as e:
            return False