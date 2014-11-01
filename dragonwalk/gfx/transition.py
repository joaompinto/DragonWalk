import pygame
import time

class TimedTransition(object):
    TRANSITIONS_TIMER = pygame.USEREVENT+1
    transition_list = []
    min_interval = 0

    def __init__(self, end_function,
                 target_object=None, target_property=None, update_interval=None, target_value=None, max_time=None):
        self.target_object = target_object()
        TimedTransition.transition_list.append(lambda: self.update)
        self.last_check = 0
        self.start_time = time.time()
        self.next_check = self.start_time + update_interval
        self.update_interval = update_interval

        current_value = getattr(self.target_object, 'target_property')
        self.sign = target_value - current_value
        if TimedTransition.min_interval > self.update_interval:
            TimedTransition.min_interval = self.update_interval
            pygame.time.set_timer(self.TRANSITIONS_TIMER, self.update_interval)


    def update(self):
        current_time = time.time()
        if self.next_check >= current_time:
            current_value = getattr(self.target_object, 'target_property')
            diff = current_value - self.target_value
            current_value += max_time/update_interval


    @staticmethod
    def on_transation_timer( event):

        if event.type != TimedTransition.TRANSITIONS_TIMER:
            return
        to_remove = []
        for event in TimedTransition.transition_list:
            if not event.update():
                to_remove.append(event)

        for event in to_remove:
            TimedTransition.transition_list.remove(event)
