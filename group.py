import itertools
import random
from bs4 import BeautifulSoup
import lxml
import os
from mathtools import *

class Group:
    def __init__(self):
        self.content = []
        self.order = 0
        self.name, self.short_description = "", ""
        self.unit = None
        self.is_abelian = None
        self.inverse = {}
        self.centralizer_of = {}
        self.order_of = {}
        self.conjugates_of = {}

    def __getitem__(self, pos):
        if isinstance(pos, tuple):
            return self[list(pos)]
        if len(pos) > 2:
            return self[[self[pos[:2]]] + pos[2:]]
        if pos[0] >= self.order or pos[1] >= self.order:
            raise Exception("Element doesn't exist.")
        return self.content[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        if min(pos) < 0:
            raise Exception("Negative position error.")
        self.order = max([self.order, pos[0]+1, pos[1]+1, value+1])
        more_elements = self.order - len(self.content)
        if more_elements > 0:
            for i in range(more_elements):
                self.content.append([])
            for row in self.content:
                while len(row) < self.order:
                    row.append(-1)
        self.content[pos[0]][pos[1]] = value

    def __str__(self):
        table_string = ""
        for row in self.content:
            line = ''
            for element in row:
                line += str(element) + ' ' * (5 - len(str(element)))
            table_string += line + "\n"
        return table_string[:-1]

    def is_group(self):
        # associativity
        for i, j, k in itertools.product(range(self.order), range(self.order), range(self.order)):
            if self[i, j, k] != self[i, self[j, k]]:
                return False
        # each element appears in each row and column
        for i in range(self.order):
            for row, column in zip(self.rows(), self.columns()):
                if not (set(row) == set(column) == set(range(self.order))):
                    return False
        return True

    def rows(self):
        return self.content

    def columns(self):
        return [[self.content[i][j] for i in range(self.order)] for j in range(self.order)]

    def __swap_row(self, row1, row2):
        temp = self.content[row1][:]
        self.content[row1] = self.content[row2][:]
        self.content[row2] = temp

    def __swap_column(self, column1, column2):
        temp = self.columns()[column1]
        for i, row in enumerate(self.content):
            row[column1] = row[column2]
            row[column2] = temp[i]

    def swap_element(self, element1, element2):
        self.__swap_row(element1, element2)
        self.__swap_column(element1, element2)
        for row in self.content:
            for j in range(len(row)):
                if row[j] == element1:
                    row[j] = element2
                elif row[j] == element2:
                    row[j] = element1

    def shuffle(self):
        template = list(range(self.order))
        seed = random.sample(range(self.order), self.order)
        for i in range(self.order):
            self.swap_element(i, template.index(seed[i]))
            template[template.index(seed[i])] = template[i]
            template[i] = seed[i]
        self.complete_info()

    def complete_info(self): # do remember to use this method from time to time
        self.unit = None
        for i, j in itertools.product(self.elements(), self.elements()):
            if self[i, j] == j or self[j, i] == j:
                self.unit = i
                break
        self.centralizer_of = {i: [i] for i in self.elements()}
        for x in self.elements():
            self.centralizer_of[x] = self.centralizer(x)
            self.centralizer_of[x].sort()
        self.inverse = {}
        self.order_of = {}
        self.conjugates_of = {i: [i] for i in self.elements()}
        if self.unit is not None:
            for x in self.elements():
                for y in self.elements():
                    if self[x, y] == self.unit:
                        self.inverse[x] = y
                        self.inverse[y] = x
                        break
            for x in self.elements():
                self.order_of[x] = self.calculate_order(x)
            for x in self.elements():
                for y in self.elements():
                    y_inverse = self.inverse.get(y)
                    if y_inverse is not None:
                        cal = -1
                        if self[y, x] > -1 and self[y, x, y_inverse] > -1:
                            cal = self[y, x, y_inverse]
                        elif self[x, y_inverse] > -1 and self[y, self[x, y_inverse]] > -1:
                            cal = self[y, self[x, y_inverse]]
                        if cal > -1 and cal not in self.conjugates_of[x]:
                            self.conjugates_of[x].append(cal)
                self.conjugates_of[x].sort()
        self.is_abelian = True
        for (i, j) in itertools.product(range(self.order), range(self.order)):
            if self[i, j] != self[j, i]:
                self.is_abelian = False
                break

    def calculate_order(self, element: int):
        if self.unit is None:
            return
        if element == self.unit:
            return 1
        else:
            for i in range(2, self.order+1):
                if self.order % i != 0:
                    continue
                elif self[[element]*i] == self.unit:
                    return i

    def element_of_order(self, order: int):
        for i in range(self.order):
            if self.calculate_order(i) == order:
                return i
        return None

    def is_cyclic(self):
        for i in range(self.order):
            if self.calculate_order(i) == self.order:
                return True
        return False

    def cycle_generated_by(self, element):
        cycle = [element]
        for i in range(2, self.calculate_order(element) + 1):
            cycle.append(self[[element]*i])
        return cycle

    def elements_not_in(self, lst):
        return [x for x in range(self.order) if x not in lst]

    def elements(self):
        return range(self.order)

    def quotient(self, subgroup: list):
        quotient = Group()
        cosets = []
        for element in self.elements():
            coset = set(self[element, x] for x in subgroup)
            is_new = True
            for other_coset in cosets:
                if coset == other_coset:
                    is_new = False
                    break
            if is_new:
                cosets.append(coset)
        quotient_order = len(cosets)
        for (i, j) in itertools.product(range(quotient_order), range(quotient_order)):
            representative1 = cosets[i].__iter__().__next__()
            representative2 = cosets[j].__iter__().__next__()
            product = self[representative1, representative2]
            quotient[i, j] = sum(int(product in cosets[k]) * k for k in range(quotient_order))
        if not quotient.is_group():
            return None
        quotient.complete_info()
        return quotient

    def count_elements_of_order(self, order):
        if order == 1:
            return 1
        return sum(self.calculate_order(x) == order for x in self.elements())

    def center(self) -> list:
        result = []
        for x in self.elements():
            in_center = True
            for y in self.elements():
                if self[x, y] != self[y, x]:
                    in_center = False
                    break
            if in_center:
                result.append(x)
        return result

    def centralizer(self,  element) -> list:
        centralizers = [element]
        for other_element in self.elements():
            if other_element == element:
                continue
            if self[element, other_element] > -1 and self[element, other_element] == self[other_element, element]:
                centralizers.append(other_element)
        return centralizers

    def commutator(self) -> list: # this does not return a subgroup
        result = []
        for x, y in itertools.product(self.elements(), self.elements()):
            commu = self[x, y, self.inverse[x], self.inverse[y]]
            if commu not in result:
                result.append(commu)
        return result

    def sum_of(self, lst1, lst2) -> list:
        if not isinstance(lst1, list):
            lst1 = [lst1]
        if not isinstance(lst2, list):
            lst2 = [lst2]
        return list(set(self[x, y] for (x, y) in itertools.product(lst1, lst2)))

    def is_normal(self, sub_group: list) -> bool:
        for element in self.elements():
            left_coset = self.sum_of(element, sub_group)
            right_coset = self.sum_of(sub_group, element)
            if set(left_coset) != set(right_coset):
                return False
        return True

    def slice_of_elements(self, elements: list):
        sliced = empty_group_of_order(len(elements))
        for i, j in itertools.product(range(len(elements)), range(len(elements))):
            sliced[i, j] = self[elements[i], elements[j]]
        if sliced.is_group():
            sliced.complete_info()
        return sliced

    def normal_series(self) -> (str, str):
        series = "{e} ->"
        groups_in_series = []
        for order in range(2, int(self.order / 2) + 1):
            if self.order % order == 0:
                sliced = self.slice_of_elements(list(range(order)))
                if sliced.is_group() and self.is_normal(list(range(order))):
                    group_name = group_identify(sliced)
                    series += f" {group_name} ->"
                    groups_in_series.append(group_name)
        self.name = group_identify(self)
        series += f" {self.name}"
        return series, groups_in_series + [self.name]

class empty_group_of_order(Group):
    def __init__(self, order: int):
        super().__init__()
        self[order - 1, order - 1] = -1

"""
load groups from group files
"""
groups_by_name = {}
groups_by_order = {}
for file in os.listdir("groups"):
    new_group = Group()
    with open(os.path.join("groups", file), 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    table_data = soup.findAll("row")
    for index, row_data in enumerate(table_data):
        row_strings = row_data.string.split(" ")[1:-1]
        for column_index in range(len(table_data)):
            new_group[index, column_index] = int(row_strings[column_index])
    new_group.name = soup.gapname.string
    new_group.complete_info()
    if soup.phrase:
        new_group.short_description = soup.phrase.string
    groups_by_name[new_group.name] = new_group
    if new_group.order not in groups_by_order:
        groups_by_order[new_group.order] = [new_group]
    else:
        groups_by_order[new_group.order].append(new_group)

def group_identify(g: Group) -> str:
    result = ""
    if not g.is_group():
        return "Not a group."
    else:
        g.complete_info()
    if g.order == 1:
        result = "1"
    elif isprime(g.order):
        result = f"C{g.order}"
    elif g.order == 4:
        result = "C4" if g.is_cyclic() else "C2 x C2"
    elif g.order == 6:
        result = "C6" if g.is_cyclic() else "S3"
    elif g.order == 8:
        if g.is_abelian:
            if g.is_cyclic():
                result = "C8"
            else:
                result = "C4 x C2" if g.element_of_order(4) is not None else "C2 x C2 x C2"
        else:
            a = g.element_of_order(4)
            cycle = g.cycle_generated_by(a)
            b = g.elements_not_in(cycle)[0]
            if g[a, b, a, b] == g.unit:
                result = "D8"
            else:
                result = "Q8"
    elif g.order == 9:
        if g.is_cyclic():
            result = "C9"
        else:
            result = "C3 x C3"
    elif g.order == 10:
        if g.is_cyclic():
            result = "C10"
        else:
            result = "D10"
    elif g.order == 12:
        if g.is_abelian:
            if g.is_cyclic():
                result = "C12"
            else:
                result = "C6 x C2"
        else:
            a = g.element_of_order(6)
            b = g.element_of_order(4)
            if a is None and b is None:
                result = "A4"
            elif a is not None and b is not None:
                result = "C3 : C4"
            elif a is not None and b is None:
                result = "D12"
    elif g.order == 14:
        if g.is_cyclic():
            result = "C14"
        else:
            result = "D14"
    elif g.order == 15:
        result = "C15"
    elif g.order == 16:
        a = g.element_of_order(8)
        b = g.element_of_order(4)
        if g.is_abelian:
            if g.is_cyclic():
                result = "C16"
            elif a is not None:
                result = "C8 x C2"
            elif g.count_elements_of_order(2) == 15:
                result = "C2 x C2 x C2 x C2"
            else:
                cycle4 = g.cycle_generated_by(b)
                quotient1 = g.quotient(cycle4)
                c = quotient1.element_of_order(4)
                if c is None:
                    result = "C4 x C2 x C2"
                else:
                    result = "C4 x C4"
        else:
            if a is not None:
                a_cycle = g.cycle_generated_by(a)
                order_2_out_side_of_cycle = -1
                for element in g.elements_not_in(a_cycle):
                    if g.calculate_order(element) == 2:
                        order_2_out_side_of_cycle = element
                        break
                d = order_2_out_side_of_cycle
                if g.count_elements_of_order(2) == 1:
                    result = "Q16"
                elif g[a, d, a, d] == g.unit:
                    result = "D16"
                elif g[d, a, d, a, a, a, a, a] == g.unit:
                    result = "QD16"
                else:
                    result = "C8 : C2"
            else:
                quotients = [] # names of quotient groups
                for element in g.elements():
                    cycle_of_length_2 = g.cycle_generated_by(element)
                    if len(cycle_of_length_2) == 2 and g.is_normal(cycle_of_length_2):
                        quotients.append(group_identify(g.quotient(cycle_of_length_2)))
                if g.count_elements_of_order(2) == 11:
                    result = "C2 x D8"
                elif g.count_elements_of_order(2) == 3:
                    if "D8" in quotients:
                        result = "C4 : C4"
                    else:
                        result = "C2 x Q8"
                elif g.count_elements_of_order(2) == 7:
                    if "D8" in quotients:
                        result = "G4,4"
                    else:
                        result = "(C4 x C2) : C2"
    elif g.order == 18:
        if g.is_abelian:
            if g.is_cyclic():
                result = "C18"
            else:
                result = "C6 x C3"
        else:
            a = g.element_of_order(9)
            if a is not None:
                result = "D18"
            else:
                b = g.element_of_order(6)
                if b is None:
                    result = "(C3 x C3) : C2"
                else:
                    result = "C3 x S3"
    elif g.order == 20:
        if g.is_abelian:
            if g.is_cyclic():
                result = "C20"
            else:
                result = "C10 x C2"
        else:
            a = g.element_of_order(10)
            b = g.element_of_order(4)
            if a is not None:
                if b is None:
                    result = "D20"
                else:
                    result = "C5 ⋊ C4"
            else:
                result = "Fr20"
    else:
        result = "I don't know."
    g.name = result
    return result

def test_by_order(order: int):
    for group in groups_by_order[order]:
        group.shuffle()
        result = group_identify(group)
        if result == group.name:
            # print(f"Successfully identified {group.name}.")
            print(".")
        else:
            print(f"Failed to identify {group.name} as {result}")
            # print(group)

if __name__ == "__main__":
    for i in range(100):
        for j in range(1, 21):
            test_by_order(j)
        print("---------------------------------------------------------------")

