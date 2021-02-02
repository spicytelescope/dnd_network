from __future__ import division
from __future__ import print_function

import sys
from collections import defaultdict

import pygame

from .transitions import AnimationTransition

__all__ = ('Task', 'Animation', 'remove_animations_of')

ANIMATION_NOT_STARTED = 0
ANIMATION_RUNNING = 1
ANIMATION_DELAYED = 2
ANIMATION_FINISHED = 3

PY2 = sys.version_info[0] == 2
string_types = None
text_type = None
if PY2:
    string_types = basestring
    text_type = unicode
else:
    string_types = text_type = str


def is_number(value):
    """Test if an object is a number.
    :param value: some object
    :returns: True
    :raises: ValueError
    """
    try:
        float(value)
    except (ValueError, TypeError):
        raise ValueError

    return True


def remove_animations_of(target, group):
    """ Find animations that target objects and remove those animations

    :param target: any
    :param group: pygame.sprite.Group
    :returns: list of animations that were removed
    """
    animations = [ani for ani in group.sprites() if isinstance(ani, Animation)]
    to_remove = [ani for ani in animations
                 if target in [i[0] for i in ani.targets]]
    group.remove(*to_remove)
    return to_remove


class AnimBase(pygame.sprite.Sprite):
    _valid_schedules = []

    def __init__(self):
        super(AnimBase, self).__init__()
        self._callbacks = defaultdict(list)

    def schedule(self, func, when=None):
        """ Schedule a callback during operation of Task or Animation

        The callback is any callable object.  You can specify different
        times for the callback to be executed, according to the following:

        * "on update": called each time the Task/Animation is updated
        * "on finish": called when the Task/Animation completes normally
        * "on abort": called if the Task/Animation is aborted

        If when is not passed, it will be "on finish":

        :type func: callable
        :type when: basestring
        :return:
        """
        if when is None:
            when = self._valid_schedules[0]

        if when not in self._valid_schedules:
            print('invalid time to schedule a callback')
            print('valid:', self._valid_schedules)
            raise ValueError
        self._callbacks[when].append(func)

    def _execute_callbacks(self, when):
        try:
            callbacks = self._callbacks[when]
        except KeyError:
            return
        else:
            [cb() for cb in callbacks]


class Task(AnimBase):
    """ Execute functions at a later time and optionally loop it

    This is a silly little class meant to make it easy to create
    delayed or looping events without any complicated hooks into
    pygame's clock or event loop.

    Tasks are created and must be added to a normal pygame group
    in order to function.  This group must be updated, but not
    drawn.

    Setting the interval to 0 cause the callback to be called
    on the next update.

    Because the pygame clock returns milliseconds, the examples
    below use milliseconds.  However, you are free to use what-
    ever time unit you wish, as long as it is used consistently

        task_group = pygame.sprite.Group()

        # like a delay
        def call_later():
            pass
        task = Task(call_later, 1000)
        task_group.add(task)

        # do something 24 times at 1 second intervals
        task = Task(call_later, 1000, 24)

        # do something every 2.5 seconds forever
        task = Task(call_later, 2500, -1)

        # pass arguments using functools.partial
        from functools import partial
        task = Task(partial(call_later(1,2,3, key=value)), 1000)

        # a task must have at lease on callback, but others can be added
        task = Task(call_later, 2500, -1)
        task.schedule(some_thing_else)

        # chain tasks: when one task finishes, start another one
        task = Task(call_later, 2500)
        task.chain(Task(something_else))

        When chaining tasks, do not add the chained tasks to a group.
    """
    _valid_schedules = ('on interval', 'on finish', 'on abort')

    def __init__(self, callback, interval=0, times=1):
        if not callable(callback):
            raise ValueError

        if times == 0:
            raise ValueError

        super(Task, self).__init__()
        self._interval = interval
        self._loops = times
        self._duration = 0
        self._chain = list()
        self._state = ANIMATION_RUNNING
        self.schedule(callback)

    def chain(self, *others):
        """ Schedule Task(s) to execute when this one is finished

        If you attempt to chain a task that will never end (loops=-1),
        then ValueError will be raised.

        :param others: Task instances
        :returns: None
        """
        if self._loops <= -1:
            raise ValueError
        for task in others:
            if not isinstance(task, Task):
                raise TypeError
            self._chain.append(task)
        return others

    def update(self, dt):
        """ Update the Task

        The unit of time passed must match the one used in the
        constructor.

        Task will not 'make up for lost time'.  If an interval
        was skipped because of a lagging clock, then callbacks
        will not be made to account for the missed ones.

        :param dt: Time passed since last update.
        """
        if self._state is not ANIMATION_RUNNING:
            # raise RuntimeError
            return

        self._duration += dt
        if self._duration >= self._interval:
            self._duration -= self._interval
            if self._loops >= 0:
                self._loops -= 1
                if self._loops == 0:
                    self.finish()
                else:    # not finished, but still are iterations left
                    self._execute_callbacks("on interval")
            else:   # loops == -1, run forever
                self._execute_callbacks("on interval")

    def finish(self):
        """ Force task to finish, while executing callbacks
        """
        if self._state is ANIMATION_RUNNING:
            self._state = ANIMATION_FINISHED
            self._execute_callbacks("on interval")
            self._execute_callbacks("on finish")
            self._execute_chain()
            self._cleanup()

    def abort(self):
        """Force task to finish, without executing callbacks
        """
        self._state = ANIMATION_FINISHED
        self.kill()

    def _cleanup(self):
        self._chain = None

    def _execute_chain(self):
        groups = self.groups()
        for task in self._chain:
            task.add(*groups)


class Animation(AnimBase):
    """ Change numeric values over time

    To animate a target sprite/object's position, simply specify
    the target x/y values where you want the widget positioned at
    the end of the animation.  Then call start while passing the
    target as the only parameter.
        ani = Animation(x=100, y=100, duration=1000)
        ani.start(sprite)

    The shorthand method of starting animations is to pass the
    targets as positional arguments in the constructor.
        ani = Animation(sprite.rect, x=100, y=0)

    If you would rather specify relative values, then pass the
    relative keyword and the values will be adjusted for you:
        ani = Animation(x=100, y=100, duration=1000, relative=True)
        ani.start(sprite)

    You can also specify a callback that will be executed when the
    animation finishes:
        ani.schedule(my_function, 'on finish')

    Another optional callback is available that is called after
    each update:
        ani.schedule(update_function, 'on update')

    Animations must be added to a sprite group in order for them
    to be updated.  If the sprite group that contains them is
    drawn then an exception will be raised, so you should create
    a sprite group only for containing Animations.

    You can cancel the animation by calling Animation.abort().

    When the Animation has finished, then it will remove itself
    from the sprite group that contains it.

    You can optionally delay the start of the animation using the
    delay keyword.


    Callable Attributes
    ===================

    Target values can also be callable.  In this case, there is
    no way to determine the initial value unless it is specified
    in the constructor.  If no initial value is specified, it will
    default to 0.

    Like target arguments, the initial value can also refer to a
    callable.

    NOTE: Specifying an initial value will set the initial value
          for all target names in the constructor.  This
          limitation won't be resolved for a while.


    Pygame Rects
    ============

    The 'round_values' parameter will be set to True automatically
    if pygame rects are used as an animation target.
    """
    _valid_schedules = ('on finish', 'on update')
    default_duration = 1000.
    default_transition = 'linear'

    def __init__(self, *targets, **kwargs):
        super(Animation, self).__init__()
        self._targets = list()
        self._pre_targets = list()      #  used when there is a delay
        self._delay = kwargs.get('delay', 0)
        self._state = ANIMATION_NOT_STARTED
        self._round_values = kwargs.get('round_values', False)
        self._duration = float(kwargs.get('duration', self.default_duration))
        self._transition = kwargs.get('transition', self.default_transition)
        self._initial = kwargs.get('initial', None)
        self._relative = kwargs.get('relative', False)
        if isinstance(self._transition, string_types):
            self._transition = getattr(AnimationTransition, self._transition)
        self._elapsed = 0.
        for key in ('duration', 'transition', 'round_values', 'delay',
                    'initial', 'relative'):
            kwargs.pop(key, None)
        if not kwargs:
            raise ValueError
        self.props = kwargs

        if targets:
            self.start(*targets)

    @property
    def targets(self):
        return list(self._targets)

    def _get_value(self, target, name):
        """ Get value of an attribute, even if it is callable

        :param target: object than contains attribute
        :param name: name of attribute to get value from
        :returns: Any
        """
        if self._initial is None:
            value = getattr(target, name)
        else:
            value = self._initial

        if callable(value):
            value = value()

        return value

    def _set_value(self, target, name, value):
        """ Set a value on some other object

        If the name references a callable type, then
        the object of that name will be called with 'value'
        as the first and only argument.

        Because callables are 'write only', there is no way
        to determine the initial value.  you can supply
        an initial value in the constructor as a value or
        reference to a callable object.

        :param target: object to be modified
        :param name: name of attribute to be modified
        :param value: value
        :returns: None
        """
        if self._round_values:
            value = int(round(value, 0))

        attr = getattr(target, name)
        if callable(attr):
            attr(value)
        else:
            setattr(target, name, value)

    def _gather_initial_values(self):
        self._targets = list()
        for target in self._pre_targets:
            props = dict()
            if isinstance(target, pygame.Rect):
                self._round_values = True
            for name, value in self.props.items():
                initial = self._get_value(target, name)
                is_number(initial)
                is_number(value)
                if self._relative:
                    value += initial
                props[name] = initial, value
            self._targets.append((target, props))

        self.update(0)  # required to 'prime' initial values of callable targets

    def update(self, dt):
        """ Update the animation

        The unit of time passed must match the one used in the
        constructor.

        Make sure that you start the animation, otherwise your
        animation will not be changed during update().

        Will raise RuntimeError if animation is updated after
        it has finished.

        :param dt: Time passed since last update.
        :raises: RuntimeError
        """
        if self._state is ANIMATION_FINISHED:
            # raise RuntimeError
            return

        if self._state is not ANIMATION_RUNNING:
            return

        self._elapsed += dt
        if self._delay > 0:
            if self._elapsed > self._delay:
                self._elapsed -= self._delay
                self._gather_initial_values()
                self._delay = 0
            return

        p = min(1., self._elapsed / self._duration)
        t = self._transition(p)
        for target, props in self._targets:
            for name, values in props.items():
                a, b = values
                value = (a * (1. - t)) + (b * t)
                self._set_value(target, name, value)

        # update will be called with 0 it init the delay, but we
        # don't want to call the update callback in that case
        if dt:
            self._execute_callbacks("on update")

        if p >= 1:
            self.finish()

    def finish(self):
        """ Force animation to finish, apply transforms, and execute callbacks

        Update callback will be called because the value is changed
        Final callback ('callback') will be called
        Final values will be applied
        Animation will be removed from group

        Will raise RuntimeError if animation has not been started

        :returns: None
        :raises: RuntimeError
        """
        # if self._state is not ANIMATION_RUNNING:
        #     raise RuntimeError

        if self._targets is not None:
            for target, props in self._targets:
                for name, values in props.items():
                    a, b = values
                    self._set_value(target, name, b)

        self._execute_callbacks("on update")
        self.abort()

    def abort(self):
        """ Force animation to finish, without any cleanup

        Update callback will not be executed
        Final callback will be executed
        Values will not change
        Animation will be removed from group

        Will raise RuntimeError if animation has not been started

        :returns: None
        :raises: RuntimeError
        """
        # if self._state is not ANIMATION_RUNNING:
        #     raise RuntimeError

        self._state = ANIMATION_FINISHED
        self._targets = None
        self.kill()
        self._execute_callbacks("on finish")

    def start(self, *targets):
        """ Start the animation on a target sprite/object

        Targets must have the attributes that were set when
        this animation was created.

        :param targets: Any valid python object
        :raises: RuntimeError
        """
        # TODO: weakref the targets
        if self._state is not ANIMATION_NOT_STARTED:
            raise RuntimeError

        self._state = ANIMATION_RUNNING
        self._pre_targets = targets

        if self._delay == 0:
            self._gather_initial_values()

