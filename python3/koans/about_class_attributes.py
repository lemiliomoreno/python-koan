#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Based on AboutClassMethods in the Ruby Koans
#

from runner.koan import *

class AboutClassAttributes(Koan):
    class Dog:
        pass

    def test_objects_are_objects(self):
        fido = self.Dog()
        self.assertEqual(True, isinstance(fido, object))

    def test_classes_are_types(self):
        self.assertEqual(True, self.Dog.__class__ == type)

    def test_classes_are_objects_too(self):
        self.assertEqual(True, issubclass(self.Dog, object))

    def test_objects_have_methods(self):
        fido = self.Dog()
        self.assertEqual(26, len(dir(fido)))

    def test_classes_have_methods(self):
        self.assertEqual(26, len(dir(self.Dog)))

    def test_creating_objects_without_defining_a_class(self):
        singularity = object()
        self.assertEqual(23, len(dir(singularity)))

    def test_defining_attributes_on_individual_objects(self):
        fido = self.Dog()
        fido.legs = 4

        self.assertEqual(4, fido.legs)

    def test_defining_functions_on_individual_objects(self):
        fido = self.Dog()
        fido.wag = lambda : 'fidos wag'

        self.assertEqual("fidos wag", fido.wag())

    def test_other_objects_are_not_affected_by_these_singleton_functions(self):
        fido = self.Dog()
        rover = self.Dog()

        def wag():
            return 'fidos wag'
        fido.wag = wag

        with self.assertRaises(AttributeError): rover.wag()

    # ------------------------------------------------------------------

    class Dog2:
        def wag(self):
            return 'instance wag'

        def bark(self):
            return "instance bark"

        def growl(self):
            return "instance growl"

        @staticmethod
        def bark():
            return "staticmethod bark, arg: None"

        @classmethod
        def growl(cls):
            return "classmethod growl, arg: cls=" + cls.__name__
            
            # The distinction between "self" and "cls" is defined in PEP 8. PEP 8 says:
            # Function and method arguments:
            # Always use self for the first argument to instance methods.
            # Always use cls for the first argument to class methods.

    def test_since_classes_are_objects_you_can_define_singleton_methods_on_them_too(self):
        self.assertRegex(self.Dog2.growl(), "classmethod growl, arg: cls=Dog2")

    def test_classmethods_are_not_independent_of_instance_methods(self):
        fido = self.Dog2()
        self.assertRegex(fido.growl(), "classmethod growl, arg: cls=Dog2")
        self.assertRegex(self.Dog2.growl(), "classmethod growl, arg: cls=Dog2")

        # Class and instance methods live in the same namespace and you cannot reuse names 
        # like that; the last definition will win in that case.
        # This is documented in https://docs.python.org/3.3/library/functions.html#classmethod :
        # It can be called either on the class (such as C.f()) or on an instance 
        # (such as C().f()). The instance is ignored except for its class.
        # More?: https://stackoverflow.com/questions/28237955/same-name-for-classmethod-and-instancemethod
        # Even more?: https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner

        # Example:

        # class MyClass():
        #   def method():
        #       print("instance method")
        #   @classmethod
        #   def method():
        #       print("class method")
        #
        # MyClass.method()  # "class method"
        # var = MyClass()
        # var.method()      # "class method"

        # But if we declare the instance method after the class method:

        # class MyClass():
        #   @classmethod
        #   def method():
        #       print("class method")
        #   def method():
        #       print("instance method")
        #
        # MyClass.method()  # "instance method"
        # var = MyClass()
        # var.method()      # "instance method"

    def test_staticmethods_are_unbound_functions_housed_in_a_class(self):
        self.assertRegex(self.Dog2.bark(), "staticmethod bark, arg: None")

    def test_staticmethods_also_overshadow_instance_methods(self):
        fido = self.Dog2()
        self.assertRegex(fido.bark(), "staticmethod bark, arg: None")

    # ------------------------------------------------------------------

    class Dog3:
        def __init__(self):
            self._name = None

        def get_name_from_instance(self):
            return self._name

        def set_name_from_instance(self, name):
            self._name = name

        @classmethod
        def get_name(cls):
            return cls._name

        @classmethod
        def set_name(cls, name):
            cls._name = name

        name = property(get_name, set_name)
        name_from_instance = property(get_name_from_instance, set_name_from_instance)
        
        # About 'property'? https://docs.python.org/3.3/library/functions.html#property
        # The property method, got 3 values, 'getter', 'setter' and 'deleter'
        # property(fget=None, fset=None, fdel=None, doc=None)
        # 'c.x' will invoke the getter, 'c.x = value' will invoke the setter and del c.x will invoke the deleter
        # Example:
        # class C:
        #   def __init__(self):
        #       self._x = None
        #   @property
        #   def x(self):
        #       """I'm the 'x' property."""
        #       return self._x
        #   @x.setter
        #   def x(self, value):
        #        self._x = value
        #   @x.deleter
        #   def x(self):
        #        del self._x

    def test_classmethods_can_not_be_used_as_properties(self):
        fido = self.Dog3()
        with self.assertRaises(TypeError): fido.name = "Fido"
        
        # The class methods cannot be used as properties

    def test_classes_and_instances_do_not_share_instance_attributes(self):
        fido = self.Dog3()
        fido.set_name_from_instance("Fido")
        fido.set_name("Rover")
        self.assertEqual("Fido", fido.get_name_from_instance())
        self.assertEqual("Rover", self.Dog3.get_name())

    def test_classes_and_instances_do_share_class_attributes(self):
        fido = self.Dog3()
        fido.set_name("Fido")
        self.assertEqual("Fido", fido.get_name())
        self.assertEqual("Fido", self.Dog3.get_name())

    # ------------------------------------------------------------------

    class Dog4:
        def a_class_method(cls):
            return 'dogs class method'

        def a_static_method():
            return 'dogs static method'

        a_class_method = classmethod(a_class_method)
        a_static_method = staticmethod(a_static_method)

    def test_you_can_define_class_methods_without_using_a_decorator(self):
        self.assertEqual('dogs class method', self.Dog4.a_class_method())

    def test_you_can_define_static_methods_without_using_a_decorator(self):
        self.assertEqual('dogs static method', self.Dog4.a_static_method())

    # ------------------------------------------------------------------

    def test_heres_an_easy_way_to_explicitly_call_class_methods_from_instance_methods(self):
        fido = self.Dog4()
        self.assertEqual('dogs class method', fido.__class__.a_class_method())
