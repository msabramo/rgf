from rgf import Example, ExampleGroup, describe, it, before

class MockExampleGroup(object):
    def run_before_each(self, example):
        def before(eg):
            eg.before_was_run = True
        before(example)

# Example can be run
def first_test_function(self):
    self.has_been_run = True

first_example = Example("can be run", first_test_function, MockExampleGroup())
first_example.run()
assert first_example.has_been_run

# Example is run with before func from context
second_example = Example("runs before method from context", first_test_function, MockExampleGroup())
second_example.run()
assert second_example.before_was_run

# Successful example reports its success
third_example = Example("reports success", first_test_function, MockExampleGroup())
assert (1, None) == third_example.run()

# Exploded example reports its error
an_error = StandardError("An Error")
def bad_test_function(self):
    raise an_error

third_example = Example("reports error", bad_test_function, MockExampleGroup())
assert (3, an_error) == third_example.run()

# Failed example reports its error
def failed_test_function(self):
    assert False

fourth_example = Example("reports failure", failed_test_function, MockExampleGroup())
result = fourth_example.run()
assert result[0] == 2
assert type(result[-1]) == AssertionError

# ExampleGroups can be created and described
eg = ExampleGroup("A group of Examples")
assert eg.description == "A group of Examples"

# Examples can be grouped and run together
eg = ExampleGroup("")
eg.add_example(Example('All good', first_test_function, eg))
eg.add_example(Example('Still good', first_test_function, eg))
eg.run()

assert eg.examples[0].has_been_run
assert eg.examples[1].has_been_run

# ExampleGroups can have setup code to be run before examples added
def before_func(world):
    world.before_was_run = True

eg = ExampleGroup("")
eg.add_example(Example('All good', first_test_function, eg))
eg.add_example(Example('Still good', first_test_function, eg))
eg.add_before(before_func)
eg.run()

assert eg.examples[0].before_was_run
assert eg.examples[1].before_was_run

# ExampleGroup class provides a naive way to register an ExampleGroup instance as the 'current' example group
eg = ExampleGroup("")
ExampleGroup.set_current_example_group(eg)

assert ExampleGroup.get_current_example_group() is eg

# provide describe helper context to create and set current ExampleGroup
eg = describe('This Example Group')
assert ExampleGroup.get_current_example_group() is eg

# provide it() decorator creator. The decorator creates Examples on the current ExampleGroup
eg = describe('Example Group with examples added by it()')
decorator = it('Example description created by it()')
example = decorator(first_test_function)
assert example.description == 'Example description created by it()'
assert eg.examples == [example]

# provide before() decorator creator. The decorator adds a function to the current ExampleGroup's before runner
eg = describe('Example Group with before function')
decorator = before()
decorator(before_func)
assert eg.before_function is before_func
