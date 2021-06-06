import numpy as np
import gym

from abc import ABC
from loguru import logger

from .common import log_msg


class Sender(gym.Env, ABC):

    _next_id = 0

    def __init__(self, send_rate, send_rate_scale, max_send_rate, min_send_rate, path):
        self.id                     = Sender._get_next_id()

        self.start_send_rate        = send_rate
        self.send_rate_scale        = send_rate_scale
        self.max_send_rate          = max_send_rate
        self.min_send_rate          = min_send_rate
        self.path                   = path

        self.curr_send_rate         = send_rate

        self.sent               = 0
        self.acked              = 0
        self.lost               = 0
        self.bytes_in_flight    = 0

    @staticmethod
    def _get_next_id():
        result = Sender._next_id
        Sender._next_id += 1
        return result

    def __str__(self):
        string = log_msg(f' curr_send_rate={self.curr_send_rate} '
                         f'| sender_id={self.id} ')
        for link in self.path:
            string += log_msg(str(link))
        return  string

    def reset(self):
        self.curr_send_rate     = self.start_send_rate
        self.sent               = 0
        self.acked              = 0
        self.lost               = 0
        self.bytes_in_flight    = 0

    def apply_rate_delta(self, send_rate_delta):
        send_rate_delta *= self.send_rate_scale
        if send_rate_delta >= 0.0:
            logger.debug(f'sender={self.id}: Increase send_rate: curr_send_rate={self.curr_send_rate}->{self.curr_send_rate * (1.0 + send_rate_delta)}')
            self.curr_send_rate = self.curr_send_rate * (1.0 + send_rate_delta)
        else:
            logger.debug(f'sender={self.id}: Decrease send_rate: curr_send_rate={self.curr_send_rate}->{self.curr_send_rate / (1.0 - send_rate_delta)}')
            self.curr_send_rate = self.curr_send_rate / (1.0 - send_rate_delta)

        if self.curr_send_rate > self.max_send_rate:
            logger.debug(f'curr_send_rate ({self.curr_send_rate}) > max_send_rate ({self.max_send_rate})')
            self.curr_send_rate = self.max_send_rate
        if self.curr_send_rate < self.min_send_rate:
            logger.debug(f'curr_send_rate ({self.curr_send_rate}) > min_send_rate ({self.min_send_rate})')
            self.curr_send_rate = self.min_send_rate

    def step(self, action):
        pass
