import copy
import random
import time
from collections import Counter


class CryptArithmeticBTSolver:
    """
    CSP solver for cryptarithmetic problems.
    Implements backtrack and forward-checking algorithms
    """

    NO_LOGGING = 0  # Don't show logs
    SHOW_LOGS = 1  # Show logs

    def __init__(self, words: [str], answer: str, base: int = 10):
        """
        Init the solver
        Params:
            words: List of words composing the operands
            answer: Result of the operation
            base: arithmetic base. 10 by default (decimal numbers)
        Attributes:
            variables: list of variables
            domains: dictionary of the domains
            logging_level: show logs or not
            __solving_time: solving time
        """
        self.words = words
        self.answer = answer
        self.base = base
        # self.variables_dict = {}
        self.variables = []
        self.domains = {}
        self.__reset_model()
        self.logging_level = self.NO_LOGGING
        self.__solving_time = 0

    def __build_variables(self):
        """
        Build variables with their domains
        :return:
        """
        letters_set = set()
        for w in self.words + [self.answer]:
            letters_set.update(list(w))
        self.variables = letters_set
        self.domains = {v: list(range(10)) for v in self.variables}

    def __reset_model(self):
        """
        Reset variables with their domains
        :return:
        """
        self.__build_variables()

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

    def __get_num_value(self, word: str, assignment: dict):
        """
        Get numerical value of an instantion
        :param word: string of variables
        :param assignment: instantiation
        :return: Numerical value or None
        """
        ln = len(word)
        out = None
        for i, ch in enumerate(word):
            if i == 0:
                out = assignment[ch] * (self.base ** (ln - 1))
            else:
                out = out + assignment[ch] * (self.base ** (ln - (1 + i)))
        return out

    def __make_sum(self, words_list: list[str], assignment: dict):
        """
        Helper function. Get numerical value of all operands and sum them
        :param words_list: list of words
        :param assignment: instantiation
        :return: numerical sum of the operands
        """
        out = None
        for i, w in enumerate(words_list):
            if i == 0:
                out = self.__get_num_value(w, assignment)
            else:
                out = out + self.__get_num_value(w, assignment)
        return out

    def __check_constraints(self, assignment: dict):
        """
        Check that instantiation is valid
        :param assignment: instantiation
        :return: True if verified. False otherwise
        """
        # values = assignment.values()
        # if len(values) != len(set(values)):
        #     return False
        return self.__check_all_diff(assignment) and self.__make_sum(words_list=self.words, assignment=assignment) \
               == self.__get_num_value(self.answer, assignment)

    @staticmethod
    def __check_all_diff(assignment: dict, exclude_nones=True):
        """
        Check all diff constraint
        :param assignment: instantiation
        :param exclude_nones: exclude variables None values (not instantiated)
        :return: True if verified. False otherwise
        """
        values = assignment.values()
        if exclude_nones:
            values = [v for v in values if v is not None]
        if len(values) != len(set(values)):
            return False
        return True

    @staticmethod
    def __pick_variable(vars_, local_assignment: dict):
        """
        Helper function to pick a non-instantiated variable
        :param vars_: list of variables
        :param local_assignment: current instantiation
        :return: Selected variable or None if all variable have been instantiated
        """
        instantiated_vars = [v for v, d in local_assignment.items() if d is not None]
        for v in vars_:
            if v not in instantiated_vars:
                return v
        return None

    @staticmethod
    def __rank_variables(words: [str], answer: str):
        """
        Helper function to rank variables with respect to occurrences
        :param words: list of operands
        :param answer: result of operation
        :return: ordered list of variables
        """
        counter_dict = Counter(''.join(words + [answer]))
        return [v[0] for v in counter_dict.most_common()]

    def backtrack(self, variables_ordering='deg'):
        """
        Backtrack algorithm
        :param variables_ordering: Ordering to use for vriables. {deg, random}
        :return: Solution if found, False otherwise
        """

        if variables_ordering.lower() == 'deg':
            vars_ = self.__rank_variables(self.words, self.answer)
        else:
            vars_ = list(copy.deepcopy(self.variables))
            random.shuffle(vars_)
        # print(vars_)

        def backtrack_util(local_assignment: dict, i=0):
            if self.logging_level == self.SHOW_LOGS:
                print(i, '-', local_assignment)
            v = self.__pick_variable(vars_, local_assignment)
            if not v:
                # return True
                return self.__check_constraints(local_assignment)

            for d in self.domains[v]:
                local_assignment[v] = d
                if self.__check_all_diff(local_assignment):
                    if backtrack_util(local_assignment, i + 1):
                        return True
            local_assignment[v] = None

        I = {}
        if len(self.variables) > 10:
            return False
        for i, ch in enumerate(self.variables):
            I[ch] = None
        # print(variables)
        # print(I)
        if backtrack_util(I):
            return I
        return False

    def forward_checking(self, variables_ordering='deg'):
        """
        Forward-Checking algorithm
        :param variables_ordering: Ordering to use for vriables. {deg, random}
        :return: Solution if found, False otherwise
        """
        if variables_ordering.lower() == 'deg':
            vars_ = self.__rank_variables(self.words, self.answer)
        else:
            vars_ = list(copy.deepcopy(self.variables))
            random.shuffle(vars_)
        # print(vars_)

        def fc_util(local_assignment: dict, domains_: dict, i=0):
            if self.logging_level == self.SHOW_LOGS:
                print(i, '-', local_assignment)
            i += 1
            v = self.__pick_variable(vars_, local_assignment)
            if not v:
                # return True
                return self.__check_constraints(local_assignment)

            domain_v = domains_[v]
            for d in domain_v:
                domains_[v] = [d]
                local_assignment[v] = d
                domains_before_pruning = copy.deepcopy(domains_)
                # Remove inconsistent values from other variables
                empty_domain_detected = False
                for vj in vars_:
                    if vj != v:
                        try:
                            domains_[vj].remove(d)
                        except ValueError:
                            # print()
                            ...
                        empty_domain_detected = not domains_[vj]
                if not empty_domain_detected:
                    if self.__check_all_diff(local_assignment):
                        if fc_util(local_assignment, domains_, i):
                            return True
                domains_ = copy.deepcopy(domains_before_pruning)  # Restoring domains
            local_assignment[v] = None

        I = {}
        if len(self.variables) > 10:
            return False
        for i, ch in enumerate(self.variables):
            I[ch] = None
        # print(variables)
        # print(I)
        if fc_util(I, copy.deepcopy(self.domains), 0):
            return I
        return False

    def solve(self, solver='bt', variables_ordering='deg'):
        """
        Solve the problem.
        :param solver: Algorithm to use. {bt for Backtrack, fc for Forward checking}
        :param variable_ordering: 'deg' for deg (the number of constraints), 'random' for random ordering
        :return: solution as dict or None if no solution
        """
        start = time.time()
        if solver.lower() == 'fc':
            algo = self.forward_checking
        else:
            # BT by default
            algo = self.backtrack
        sol = algo(variables_ordering=variables_ordering)
        self.solving_time = time.time() - start
        return sol

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
        # sol = self.solve()
        print('\nStats')
        # print('  - Conflicts: %i' % self.solver.NumConflicts())
        # print('  - Branches : %i' % self.solver.NumBranches())
        print('  - Time: %f s' % self.solving_time)

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
