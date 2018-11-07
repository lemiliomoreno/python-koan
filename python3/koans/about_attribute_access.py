#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Partially based on AboutMessagePassing in the Ruby Koans
#

from runner.koan import *

class AboutAttributeAccess(Koan):

    class TypicalObject:
        pass

    def test_calling_undefined_functions_normally_results_in_errors(self):
        typical = self.TypicalObject()

        with self.assertRaises(AttributeError): typical.foobar()

    def test_calling_getattribute_causes_an_attribute_error(self):
        typical = self.TypicalObject()

        with self.assertRaises(AttributeError): typical.__getattribute__('foobar')

        # THINK ABOUT IT:
        #
        # If the method __getattribute__() causes the AttributeError, then
        # what would happen if we redefine __getattribute__()?
        #
        # Every time an attribute is called by the class, will enter
        # in the '__getattribute__' method
        #
        # Very well explained in the below exercises

    # ------------------------------------------------------------------

    class CatchAllAttributeReads:
        def __getattribute__(self, attr_name):
            return "Someone called '" + attr_name + "' and it could not be found"

    def test_all_attribute_reads_are_caught(self):
        catcher = self.CatchAllAttributeReads()

        self.assertRegex(catcher.foobar, "Someone called 'foobar' and it could not be found")

    def test_intercepting_return_values_can_disrupt_the_call_chain(self):
        catcher = self.CatchAllAttributeReads()

        self.assertRegex(catcher.foobaz, "Someone called 'foobaz' and it could not be found") # This is fine

        try:
            catcher.foobaz(1)
        except TypeError as ex:
            err_msg = ex.args[0]

        self.assertRegex(err_msg, "'str' object is not callable")

        # foobaz returns a string. What happens to the '(1)' part?
        # Try entering this into a python console to reproduce the issue:
        #
        #     "foobaz"(1)
        #
        # It will raise a 'TypeError: 'str' object is not callable'

    def test_changes_to_the_getattribute_implementation_affects_getattr_function(self):
        catcher = self.CatchAllAttributeReads()

        self.assertRegex(getattr(catcher, 'any_attribute'), "Someone called 'any_attribute' and it could not be found")

    # ------------------------------------------------------------------

    class WellBehavedFooCatcher:
        def __getattribute__(self, attr_name):
            if attr_name[:3] == "foo":
                return "Foo to you too"
            else:
                return super().__getattribute__(attr_name)
                
                # In this '__getattribute__', if the first 3 characters are 'foo'
                # it will return a string, but if not, it will call the father class
                # and return the attribute that they are looking for

    def test_foo_attributes_are_caught(self):
        catcher = self.WellBehavedFooCatcher()

        self.assertEqual("Foo to you too", catcher.foo_bar)
        self.assertEqual("Foo to you too", catcher.foo_baz)

    def test_non_foo_messages_are_treated_normally(self):
        catcher = self.WellBehavedFooCatcher()

        with self.assertRaises(AttributeError): catcher.normal_undefined_attribute

    # ------------------------------------------------------------------

    global stack_depth
    stack_depth = 0

    class RecursiveCatcher:
        def __init__(self):
            global stack_depth
            stack_depth = 0
            self.no_of_getattribute_calls = 0

        def __getattribute__(self, attr_name):
            # We need something that is outside the scope of this class:
            global stack_depth
            stack_depth += 1

            if stack_depth<=10: # to prevent a stack overflow
                self.no_of_getattribute_calls += 1
                # Oops! We just accessed an attribute (no_of_getattribute_calls)
                # Guess what happens when self.no_of_getattribute_calls is
                # accessed?
                # It will access to '__getattribute__'

            # Using 'object' directly because using super() here will also
            # trigger a __getattribute__() call and cause non-end recursion
            return object.__getattribute__(self, attr_name)
            
            # It will access to '__getattribute__', then it will go to 'if stack_depth <= 10',
            # but 'stack_depth = 1', so it will enter the if and 'no_of_getattribute_calls = 1',
            # it will repeat until 'stack_depth = 11', it won't enter the if and return the 
            # attribute required when calling the object with 'object.__getattribute__( attr_name)'

        def my_method(self):
            pass

    def test_getattribute_is_a_bit_overzealous_sometimes(self):
        catcher = self.RecursiveCatcher()
        catcher.my_method()
        global stack_depth
        self.assertEqual(11, stack_depth)

    # ------------------------------------------------------------------

    class MinimalCatcher:
        class DuffObject: pass

        def __init__(self):
            self.no_of_getattr_calls = 0

        def __getattr__(self, attr_name):
            self.no_of_getattr_calls += 1
            return self.DuffObject

        def my_method(self):
            pass

    def test_getattr_ignores_known_attributes(self):
        catcher = self.MinimalCatcher()
        catcher.my_method()

        self.assertEqual(0, catcher.no_of_getattr_calls)

    def test_getattr_only_catches_unknown_attributes(self):
        catcher = self.MinimalCatcher()
        catcher.purple_flamingos()
        catcher.free_pie()

        self.assertEqual("DuffObject",
            type(catcher.give_me_duff_or_give_me_death()).__name__)
            
            # In this case you are naming the type of data from catcher.give_me_duff_or_give_me_death

        self.assertEqual(3, catcher.no_of_getattr_calls)

        # So the difference between '__getattribute__' and '__getattr__':
        # __getattribute__ : catches all attributes asked
        # __getattr__ : ignores known attributes and only catches unknown attributes
        
    # ------------------------------------------------------------------

    class PossessiveSetter(object):
        def __setattr__(self, attr_name, value):
            new_attr_name =  attr_name

            if attr_name[-5:] == 'comic':
                new_attr_name = "my_" + new_attr_name
            elif attr_name[-3:] == 'pie':
                new_attr_name = "a_" + new_attr_name

                # This is changing the value of the attribute with
                # '__setattr__'
                # setattr(object, name, value)
                
            object.__setattr__(self, new_attr_name, value)

    def test_setattr_intercepts_attribute_assignments(self):
        fanboy = self.PossessiveSetter()

        fanboy.comic = 'The Laminator, issue #1'
        fanboy.pie = 'blueberry'

        self.assertEqual('blueberry', fanboy.a_pie)

        #
        # NOTE: Change the prefix to make this next assert pass
        #

        prefix = 'my'
        self.assertEqual("The Laminator, issue #1", getattr(fanboy, prefix + '_comic'))

    # ------------------------------------------------------------------

    class ScarySetter:
        def __init__(self):
            self.num_of_coconuts = 9
            self._num_of_private_coconuts = 2

        def __setattr__(self, attr_name, value):
            new_attr_name =  attr_name

            if attr_name[0] != '_':
                new_attr_name = "altered_" + new_attr_name

            object.__setattr__(self, new_attr_name, value)

    def test_it_modifies_external_attribute_as_expected(self):
        setter = self.ScarySetter()
        setter.e = "mc hammer" # Here we are calling setattr because no attr 'e' is defined
        
        # When assigning values to an object with __init__ and altering the name with
        # setattr, it will modifie all the values, not only the one created apart from 
        # the class, in this case will be 'altered_num_of_coconuts' and 'altered_e'
        # __init__ will call __setattr__

        # In this case we could use the 'setattr()' method, like this:
        # setattr(object, 'attribute', 'value')
        # In this particular example will be:
        # setattr(setter, 'e', "mc hammer") is equal to setter.e = "mc hammer"
        
        self.assertEqual("mc hammer", setter.altered_e)
        
    def test_it_mangles_some_internal_attributes(self):
        setter = self.ScarySetter()

        try:
            coconuts = setter.num_of_coconuts
            
            # This won't happen because we changed the value in the class with
            # __setattr__
            
        except AttributeError:
            self.assertEqual(9, setter.altered_num_of_coconuts)

    def test_in_this_case_private_attributes_remain_unmangled(self):
        setter = self.ScarySetter()

        self.assertEqual(2, setter._num_of_private_coconuts)

        # The private ones won't change because of 'if attr_name[0] != '_':'
        # in '__setattr__'
        