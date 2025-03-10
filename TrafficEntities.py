import math
import random
from collections import deque
import numpy as np
import pandas as pd


class Car:
    """
    Represents a car in the simulation.
    """
    def __init__(self, length, acceleration, reaction_time, keeping_distance, initial_time):
        self.length = length  # Length of the car
        self.acceleration = acceleration  # Acceleration of the car
        self.reaction_time = reaction_time  # Reaction time of the car
        self.keeping_distance = keeping_distance  # Minimum distance to keep from the car ahead
        self.time = initial_time  # Time at which the car arrived at the junction

    def time_in_the_system(self, current_time):
        """Calculate the time the car has spent in the system."""
        return  current_time - self.time

class Counter:
    """
    Represents a counter to track how many cars have passed a specific point.
    """
    def __init__(self):
        self.cars_passed = 0

    def increment(self):
        """Increment the count of cars passed."""
        self.cars_passed += 1

    def reset(self):
        """Reset the counter to zero."""
        self.cars_passed = 0

    def get_counter(self):
        """Return the count of cars passed."""
        return self.cars_passed

class Road:
    """
    Represents a road in the simulation.
    """
    def __init__(self, length, name):
        self.length = length  # Length of the road
        self.queue = deque()  # FIFO queue of cars waiting at the junction
        self.name = name # Name of the road
        self.counter = Counter()  # Counter for cars passing this road

    def add_to_queue(self, car):
        """Add a car to the queue."""
        self.queue.append(car)

    def remove_from_queue(self):
        """Remove a car from the queue."""
        if self.queue:
            return self.queue.popleft()

    def queue_length(self):
        """Calculate the total physical length of the queue."""
        total_length = 0
        for car in self.queue:
            total_length += car.length + car.keeping_distance
        return total_length

    def get_queue_size(self):
        """Return the total number of cars in the queue."""
        return len(self.queue)

    def reset_road(self):
        """Reset the road to its initial state."""
        self.queue.clear()
        self.counter.reset()

class TrafficLight:
    """
    Represents a traffic light at a junction.
    """
    def __init__(self, green_duration):
        self.state = "red"  # Initial state is red
        self.green_duration = green_duration  # Duration of the green light

    def set_state(self, state):
        """Set the state of the traffic light."""
        self.state = state

    def change_state(self):
        """Toggle the state between green and red."""
        self.state = "green" if self.state == "red" else "red"

    def is_green(self):
        """Check if the light is green."""
        return self.state == "green"

class Junction:
    """
    Represents a junction in the simulation.
    """
    def __init__(self, id, junction_length, green_light_duration):
        self.id = id  # Unique identifier for the junction
        self.junction_length = junction_length  # Length of the junction
        self.queues = {}  # Dictionary mapping roads to their queues
        self.counters = {}  # Dictionary mapping roads to their counters
        self.traffic_lights = []  # List of traffic lights at the junction
        self.green_light_duration = green_light_duration  # Duration for which each light stays green

    def add_road(self, road, counter):  # not sure about that but maybe its good
        """Add a road and its corresponding counter to the junction."""
        self.queues[road] = road.queue
        self.counters[road] = counter
        road.counter = counter

    def add_traffic_light(self, traffic_light):
        """Add a traffic light to the junction."""
        self.traffic_lights.append(traffic_light)

    def process_queue(self, road, current_time):
        """
        Process the queue for a given road during the green light duration.
        """
        count = 0
        x = {}
        t = {}
        time_in_the_system = 0

        for idx, car in enumerate(road.queue):
            if idx == 0:
                x[car] = self.junction_length + car.keeping_distance
                t[car] = car.reaction_time + math.sqrt(2 * x[car] / car.acceleration)
            else:
                prev_car = road.queue[idx - 1]
                x[car] = x[prev_car] + prev_car.length + car.keeping_distance
                t[car] = max(car.reaction_time + math.sqrt(2 * x[car] / car.acceleration),
                             t[prev_car] + car.reaction_time)

        for car in list(road.queue):
            t_i = t[car]
            if t_i <= self.green_light_duration:
                time_in_the_system = time_in_the_system + car.time_in_the_system(t_i+current_time)
                road.remove_from_queue()
                road.counter.increment()
                count += 1
            else:
                return time_in_the_system
        return time_in_the_system

    def generate_cars_poisson(self, road, rate, current_time):
        """
        Generate cars for a road based data on a Poisson distribution.
        """
        num_new_cars = np.random.poisson(rate)
        for _ in range(num_new_cars):
            # Generate random car parameters
            car = Car(
                length=max(random.normalvariate(3.5, 2.5),1),  # Avg car length 4.5m, std 0.5m
                acceleration=max(random.normalvariate(2.5, 1.0),0.5),  # Distributed acceleration
                reaction_time=max(random.normalvariate(1.0, 0.25),0.1),  # Distributed reaction time
                keeping_distance=max(random.normalvariate(1.5, 1.0),0.1),  # Distributed keeping distance
                initial_time=current_time
            )
            road.add_to_queue(car)

def sync_traffic_lights(*traffic_light_groups):
    """
    Synchronize multiple groups of traffic lights by toggling between them in order.

    Args:
        *traffic_light_groups: Variable number of lists, where each list contains traffic lights
                               that are allowed to be green together.

    """
    current_group = 0  # Start with the first group

    def toggle_lights():
        nonlocal current_group
        # Turn all lights red
        for group in traffic_light_groups:
            for traffic_light in group:
                traffic_light.set_state("red")

        # Turn the next group green
        for traffic_light in traffic_light_groups[current_group]:
            traffic_light.set_state("green")


        # Move to the next group, wrap around if at the last group
        current_group = (current_group + 1) % len(traffic_light_groups)

    return toggle_lights







