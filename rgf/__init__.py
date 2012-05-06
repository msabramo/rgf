class Example(object):
    def __init__(self, description, spec_function):
        self.spec_function = spec_function
        self.description = description

    def run(self, example_group):
        example_group.run_before_each(self)
        try:
            self.spec_function(self)
            return (1, None)
        except AssertionError as e:
            return (2, e)
        except Exception as e:
            return (3, e)

class ExampleGroup(object):
    def __init__(self, parent, description):
        self.parent = parent
        self.examples = []
        self.description = description
        self.before_function = None

    def add_example(self, example):
        self.examples.append(example)

    def add_before(self, before_function):
        self.before_function = before_function

    def run(self):
        [example.run(self) for example in self.examples]

    def run_before_each(self, example):
        if self.before_function:
            self.before_function(example)

    def __enter__(self):
        self.parent.set_current_example_group(self)
        return self

    def __exit__(self, cls, value, traceback):
        self.parent.pop_current_example_group()

class ExampleSuite(object):
    @classmethod
    def get_suite(cls):
        if hasattr(cls, 'example_suite'): return cls.example_suite
        cls.example_suite = ExampleSuite()
        return cls.example_suite

    def __init__(self):
        self.example_groups = []
        self.current_example_group_stack = [self]

    def add_example_group(self, description):
        example_group = ExampleGroup(self, description)
        self.example_groups.append(example_group)
        return example_group

    def set_current_example_group(self, example_group):
        self.current_example_group_stack.append(example_group)

    def get_current_example_group(self):
        return self.current_example_group_stack[-1]

    def pop_current_example_group(self):
        self.current_example_group_stack.pop()

def _get_current_example_group():
    return ExampleSuite.get_suite().get_current_example_group()

def describe(description):
    new_example_group = _get_current_example_group().add_example_group(description)
    return new_example_group

def it(description):
    def example_creator(spec_function):
        example_group = _get_current_example_group()
        example = Example(description, spec_function)
        example_group.add_example(example)
        return example
    return example_creator

def before():
    def before_wrapper(before_function):
        example_group = _get_current_example_group()
        example_group.add_before(before_function)
    return before_wrapper
