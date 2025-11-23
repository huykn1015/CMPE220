class MemoryManaagmentUnit:
    def __init__(self, size_words):
        self._memory = [0] * size_words

    def get_word(self, address):
        index = self.translate_address(address)
        return self._memory[value]

    def write_word(self, address, value):
        index = self.translate_address(address)
        self._memory[index] = value

    def translate_address(self, address) -> int:
        return address
