import matplotlib.pyplot as plt


# Load data from file into an array
def load_file(filename):
    data_file = open(filename, 'r')
    data = data_file.read().split('\n')
    m_time = 0
    for i in range(len(data) - 1):
        split = data[i].split(" mm, ")
        data[i] = [int(split[0]), float(split[1])]
        m_time += data[i][1]
    t_time = float(data.pop())
    multi = t_time / m_time
    for item in data:
        item[1] = item[1] * multi
    return data


def convert_data_format(data):
    result = [[], []]
    for item in data:
        result[0].append(item[0])
        result[1].append(item[1])
    return result


def convert_t(data):
    for i in range(1, len(data[1])):
        data[1][i] = data[1][i - 1] + data[1][i]
    return data


class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def init(self, size):
        self.head = Node()
        current_node = self.head
        for i in range(2, size + 1):
            new_node = Node()
            current_node.next = new_node
            current_node = new_node
        self.tail = current_node

    def insert(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        current_node = self.head
        while current_node.next.next is not None:
            current_node = current_node.next
        current_node.next = None
        self.tail = current_node

    def print_list(self):
        current_node = self.head
        while current_node:
            print(current_node.data, "\n")
            current_node = current_node.next

    def clear(self):
        current_node = self.head
        while current_node is not None:
            current_node.data = None
            current_node = current_node.next


GRAD_FILTER = 2.5
GRAD_BUFFER_SIZE = 3
GRAD_BUFFER = LinkedList()
GRAD_BUFFER.init(GRAD_BUFFER_SIZE)
GRAD_MIN = 10
DEAD_ZONE = 5
CONSECUTIVE_FILTERS = 0

BUFFER_INDEX = 1
PREV_ENTRY = 0
BUFFER_SIZE = 25
BUFFER = [0] * BUFFER_SIZE
ABS_FILTER = 40


def apply_min(val, minimum):
    if val < minimum:
        result = minimum
    else:
        result = val
    return result


def moving_grad_filter(val):
    global GRAD_BUFFER
    global CONSECUTIVE_FILTERS

    if CONSECUTIVE_FILTERS >= DEAD_ZONE:
        GRAD_BUFFER.clear()
        CONSECUTIVE_FILTERS = 0

    if GRAD_BUFFER.tail.data is not None:
        head = GRAD_BUFFER.head.data
        tail = GRAD_BUFFER.tail.data
        ref_gradient = apply_min(abs(head - tail), GRAD_MIN)
        cur_gradient = apply_min(abs(val - head), GRAD_MIN)
        if (cur_gradient / ref_gradient) < GRAD_FILTER:
            GRAD_BUFFER.insert(val)
            CONSECUTIVE_FILTERS = 0
            return True
        else:
            CONSECUTIVE_FILTERS += 1
            return False
    else:
        GRAD_BUFFER.insert(val)
        return True


def moving_avg(val, filter_f):
    global BUFFER
    global BUFFER_INDEX
    global BUFFER_SIZE

    if filter_f(val):
        BUFFER[BUFFER_INDEX] = val
        BUFFER_INDEX += 1
        if BUFFER_INDEX >= BUFFER_SIZE:
            BUFFER_INDEX = 0

    average = sum(BUFFER) / BUFFER_SIZE
    return average


def apply_ma_filter(data, filter_f):
    global PREV_ENTRY
    PREV_ENTRY = data[0][0]
    result = [[], data[1]]
    for i in range(len(data[0])):
        result[0].append(moving_avg(data[0][i], filter_f))
    return result


pump_x = [750, 750, 800, 800, 850, 850, 900, 900]
pump_t = [0, 65, 65.1, 190, 190.1, 310, 310.1, 350]

raw_data = convert_data_format(load_file("2024-05-13 15_48_35.txt"))
convert_t(raw_data)


grad_data = apply_ma_filter(raw_data, moving_grad_filter)

plt.plot(raw_data[1], raw_data[0])
plt.plot(grad_data[1], grad_data[0])
plt.plot(pump_t, pump_x)

plt.show()
