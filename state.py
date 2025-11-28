class state:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(state, cls).__new__(cls)
            cls._instance._attacker_llm = None
            cls._instance._taacker_tokenizer = None
            cls._instance._target_llm = None
            cls._instance._target_tokenizer = None
            cls.current_conversation = []
        return cls._instance
    def init_base(self, target_tokenizer, 
                    attacker_tokenizer, 
                    target_llm, 
                    attacker_llm):
        self._target_tokenizer = target_tokenizer
        self._attacker_tokenizer = attacker_tokenizer
        self._target_llm = target_llm
        self._attacker_llm = attacker_llm
    @property
    def target_tokenizer(self):
        return self._target_tokenizer
    @target_tokenizer.setter
    def target_tokenizer(self, value):
        self._target_tokenizer = value
    @property
    def attacker_tokenizer(self):
        return self._attacker_tokenizer
    @attacker_tokenizer.setter
    def attacker_tokenizer(self, value):
        self._attacker_tokenizer = value
    @property
    def target_llm(self):
        return self._target_llm
    @target_llm.setter
    def target_llm(self, value):
        self._target_llm = value
    @property
    def attacker_llm(self):
        return self._attacker_llm
    @attacker_llm.setter
    def attacker_llm(self, value):
        self._attacker_llm = value