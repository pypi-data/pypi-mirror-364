from orionis.container.container import Container
from orionis.container.facades.facade import Facade
from orionis.foundation.application import Application
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.container.mocks.mock_simple_classes import Car, ICar

class TestContainer(AsyncTestCase):
    """Test suite for the Container class functionality."""

    async def testTransientRegistration(self) -> None:
        """
        Tests the transient registration of a service in the container.
        It verifies that:
        1. The container.transient() method correctly registers a type (ICar) to be resolved as another type (Car)
        2. The resolved instances are of the correct type (Car)
        3. Each resolution returns a new instance (instance1 is not the same object as instance2)
        """
        container = Container()
        container.transient(ICar, Car)
        instance1 = container.make(ICar)
        instance2 = container.make(ICar)

        self.assertIsInstance(instance1, Car)
        self.assertIsInstance(instance2, Car)
        self.assertIsNot(instance1, instance2)

        container.drop(abstract=ICar)

    async def testSingletonRegistration(self) -> None:
        """
        Test that verifies singleton registration and resolution from the container.
        This test ensures that:
        1. A class can be registered as a singleton implementation of an interface
        2. The container correctly returns an instance of the registered implementation
        3. Multiple requests for the same interface return the same instance
        The test binds the ICar interface to the Car implementation as a singleton,
        then verifies that two requests for ICar:
        - Both return instances of Car
        - Return the exact same instance (object identity)
        """
        container = Container()
        container.singleton(ICar, Car)
        instance1 = container.make(ICar)
        instance2 = container.make(ICar)

        self.assertIsInstance(instance1, Car)
        self.assertIsInstance(instance2, Car)
        self.assertIs(instance1, instance2)

        container.drop(abstract=ICar)

    async def testScopedRegistration(self) -> None:
        """
        Tests the scoped registration functionality of the container.
        This test verifies that:
        1. Within a single context, scoped registrations return the same instance
            when the same interface is requested multiple times
        2. Different contexts produce different instances of the same registration
        The test creates two separate contexts and confirms that instances obtained
        within a single context are identical, but instances from different contexts
        are distinct.
        """

        container = Container()
        with container.createContext():
            container.scoped(ICar, Car)
            instance1 = container.make(ICar)
            instance2 = container.make(ICar)

            self.assertIsInstance(instance1, Car)
            self.assertIsInstance(instance2, Car)
            self.assertIs(instance1, instance2)

        with container.createContext():
            container.scoped(ICar, Car)
            instance3 = container.make(ICar)
            self.assertIsNot(instance1, instance3)

        container.drop(abstract=ICar)

    async def testInstanceRegistration(self) -> None:
        """
        Test case for instance registration in the container.
        This test ensures that when an instance is registered to a service in the container,
        the container returns exactly the same instance when resolving that service.
        The test:
        1. Creates an instance of Car
        2. Registers this instance to the ICar interface in the container
        3. Resolves the ICar interface from the container
        4. Asserts that the resolved instance is exactly the same object as the one registered
        """
        car_instance = Car()
        container = Container()
        container.instance(ICar, car_instance)
        resolved = container.make(ICar)

        self.assertIs(resolved, car_instance)

        container.drop(abstract=ICar)

    async def testCallableRegistration(self) -> None:
        """
        Test that callables can be registered and resolved from the container.
        This test verifies that:
        1. Functions can be registered in the container using the callable() method
        2. Registered functions can be resolved and executed using the make() method
        3. Arguments can be passed to the resolved functions as positional arguments
        4. Arguments can be passed to the resolved functions as keyword arguments
        The test registers two simple functions (add and multiply) and verifies
        they can be correctly resolved and executed with the expected results.
        """
        def add(a: int, b: int) -> int:
            return a + b

        def multiply(a: int, b: int) -> int:
            return a * b

        container = Container()
        container.callable('add', add)
        container.callable('multiply', multiply)

        self.assertEqual(container.make('add', 1, 2), 3)
        self.assertEqual(container.make('multiply', 3, 4), 12)
        self.assertEqual(container.make('add', a=5, b=7), 12)

        container.drop(alias='add')
        container.drop(alias='multiply')

    async def testTransientFacade(self) -> None:
        """
        Test case for transient instance resolution using a Facade pattern.
        This test validates that:
        1. The container can register a transient binding between an interface and a class
        2. The Facade pattern correctly resolves instances of the registered interface
        3. Multiple calls to the Facade's resolve() method return different instances
            when the binding is transient
        The test creates a CarFacade that accesses ICar interface which is bound to the Car
        implementation in a transient manner, ensuring each resolution yields a new instance.
        """
        container = Application()
        container.transient(ICar, Car)

        class CarFacade(Facade):
            @classmethod
            def getFacadeAccessor(cls):
                return ICar

        instance1 = CarFacade.resolve()
        instance2 = CarFacade.resolve()

        self.assertIsInstance(instance1, Car)
        self.assertIsInstance(instance2, Car)
        self.assertIsNot(instance1, instance2)

        container.drop(abstract=ICar)

    async def testSingletonFacade(self) -> None:
        """
        Tests if the Facade pattern correctly resolves singleton instances.
        This test verifies that:
        1. A singleton binding can be registered in the container
        2. A Facade class can be created to access this binding
        3. Multiple resolutions through the Facade return the same instance
        4. The resolved instances are of the correct type (Car)
        The test demonstrates how Facades act as static proxies to container bindings,
        maintaining the singleton behavior defined in the container.
        """
        container = Application()
        container.singleton(ICar, Car)

        class CarFacade(Facade):
            @classmethod
            def getFacadeAccessor(cls):
                return ICar

        instance1 = CarFacade.resolve()
        instance2 = CarFacade.resolve()

        self.assertIsInstance(instance1, Car)
        self.assertIsInstance(instance2, Car)
        self.assertIs(instance1, instance2)

        container.drop(abstract=ICar)

    async def testScopedFacade(self) -> None:
        """
        Tests the functionality of a Facade accessing a scoped service within a container context.
        This test verifies that:
        1. The Facade can properly resolve a scoped service
        2. Multiple resolves within the same scope return the same instance
        3. The resolved instance is of the correct type
        The test creates a scoped registration for ICar interface to Car implementation,
        defines a CarFacade class that accesses ICar, and then confirms that:
        - Resolved instances are of Car type
        - Multiple resolutions return the same instance (scoped behavior)
        """
        container = Application()
        with container.createContext():
            container.scoped(ICar, Car)

            class CarFacade(Facade):
                @classmethod
                def getFacadeAccessor(cls):
                    return ICar

            instance1 = CarFacade.resolve()
            instance2 = CarFacade.resolve()

            self.assertIsInstance(instance1, Car)
            self.assertIsInstance(instance2, Car)
            self.assertIs(instance1, instance2)

        container.drop(abstract=ICar)

    async def testResolvingUnregisteredType(self) -> None:
        """
        Tests that attempting to resolve an unregistered type from the container raises an exception.
        This test ensures that the container correctly validates that a type is registered before attempting to resolve it.

        Raises:
            Exception: Expected to be raised when attempting to resolve an unregistered type.
        """
        container = Container()
        with self.assertRaises(Exception):
            container.make('ICar')

    async def testOverridingRegistration(self) -> None:
        """
        Tests the ability of the container to override existing registrations.
        This test verifies that:
        1. When a class is registered as a singleton for an interface
        2. And later a different class is registered for the same interface
        3. The container returns the new class when resolving the interface
        4. The new instance is different from the previous instance
        This demonstrates the container's support for overriding service implementations.
        """
        class SportsCar(Car):
            def start(self):
                return f"{self.brand} {self.model} is starting."
            def stop(self):
                return f"{self.brand} {self.model} is stopping."

        container = Container()
        container.singleton(ICar, Car)
        first = container.make(ICar)
        self.assertIsInstance(first, Car)
        self.assertNotIsInstance(first, SportsCar)

        container.singleton(ICar, SportsCar)
        second = container.make(ICar)
        self.assertIsInstance(second, SportsCar)
        self.assertIsNot(first, second)

        container.drop(abstract=ICar)