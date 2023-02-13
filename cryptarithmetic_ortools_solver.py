from ortools.sat.python import cp_model


class CryptArithmeticOrtoolsSolver:
    """
    CSP solver for cryptarithmetic problems.
    Uses OR-Tools CP-SAT solver
    """

    def __init__(self, words: [str], answer: str, base: int = 10):
        """
        Init the solver
        Params:
            words: List of words composing the operands
            answer: Result of the operation
            base: arithmetic base. 10 by default (decimal numbers)
        Attributes:
            variables: list of variables
            variables_dict: variables as a dictionnary of letter, Variable instance key pairs
            model: CpModel instance
            model: CpSolver instance
        """
        self.words = words
        self.answer = answer
        self.base = base
        self.variables_dict = {}
        self.variables = []
        self.model = None
        self.__reset_model()
        self.solver = cp_model.CpSolver()

    def __build_variables(self):
        """
        Build variables with their domains
        :return:
        """
        letters_set = set()

        for w in self.words + [self.answer]:
            letters_set.update(list(w))

        self.variables = [None for _ in letters_set]

        for i, letter in enumerate(letters_set):
            self.variables[i] = self.model.NewIntVar(0, self.base-1, letter)
            self.variables_dict[letter] = self.variables[i]

    def __build_constraints(self):
        """
        Build variables constraints
        :return:
        """
        self.model.Add(self.__make_sum(self.words) == self.__get_num_value(self.answer))
        self.model.AddAllDifferent(self.variables)

    def __reset_model(self):
        """
        Reset variables with their domains
        :return:
        """
        self.model = cp_model.CpModel()
        self.__build_variables()
        self.__build_constraints()

    def set_words(self, words: [str]):
        """
        Set words of the operands
        :param words: list of strings representing the operands
        :return:
        """
        self.words = words
        self.__reset_model()

    def set_answer(self, answer: str):
        """
        Set result of the operation
        :param answer: string representing the result of the operation
        :return:
        """
        self.answer = answer
        self.__reset_model()

    def __get_num_value(self, word: str):
        """
        Get numerical value of an instantion
        :param word: string of variables
        :return: Numerical value or None
        """
        ln = len(word)
        out = None
        for i, ch in enumerate(word):
            if i == 0:
                out = self.variables_dict[ch] * (self.base ** (ln - 1))
            else:
                out = out + self.variables_dict[ch] * (self.base ** (ln - (1 + i)))
        return out

    def __make_sum(self, words_list: list[str]):
        """
        Helper function. Get numerical value of all operands and sum them
        :param words_list: list of words
        :return: numerical sum of the operands
        """
        out = None
        for i, w in enumerate(words_list):
            if i == 0:
                out = self.__get_num_value(w)
            else:
                out = out + self.__get_num_value(w)
        return out

    def solve(self):
        """
        Solve the problem.
        :return: solution or empty dict if no solution
        """
        status = self.solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            out = {}
            for k, v in self.variables_dict.items():
                out[k] = self.solver.Value(v)
            return out
        return {}

    @staticmethod
    def word_to_number(word: str, solution: dict):
        """
        Utility function. Prints words as number using the solution
        :param word: str
        :param solution: dict
        :return: str
        """
        out = ''
        for ch in word:
            out += str(solution[ch])
        return out

    def print_solution(self):
        """
        Print solution in a convenient way
        :return:
        """
        sol = self.solve()
        print('sol', sol)
        if not sol:
            print("No solution")
        else:
            nums = []
            for i, w in enumerate(self.words):
                nums.append(self.word_to_number(w, sol))

            print(' + '.join(nums), '=', self.word_to_number(self.answer, sol))

    def print_stats(self):
        """
        Print stats: solving time
        :return:
        """
        sol = self.solve()
        print('\nStats')
        print('  - Conflicts: %i' % self.solver.NumConflicts())
        print('  - Branches : %i' % self.solver.NumBranches())
        print('  - Wall time: %f s' % self.solver.WallTime())
