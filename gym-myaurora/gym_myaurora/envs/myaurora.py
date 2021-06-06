# Copyright 2021 Manor Zvi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import  random
import  heapq
import  gym
import numpy as np

from abc            import ABC
from typing         import Tuple
from gym            import spaces
from loguru         import logger
from collections    import namedtuple

from .common    import log_msg
from .link      import Link
from .sender    import Sender

MIN_BW = 100.0
MAX_BW = 500.0

MIN_LATENCY = 0.05
MAX_LATENCY = 0.5

MIN_QUEUE = 2
MAX_QUEUE = 2981

MIN_LOSS = 0.0
MAX_LOSS = 0.05

SEND_RATE_SCALE = 0.025
MIN_SEND_RATE = -1e3
MAX_SEND_RATE = 1e3

EVENT_TYPE_SEND = 'S'
EVENT_TYPE_ACK = 'A'


# class Event:
#     def __init__(self, event_time, sender, event_type, next_hop, curr_latency, dropped):
#         self.event_time     = event_time
#         self.sender         = sender
#         self.event_type     = event_type
#         self.next_hop       = next_hop
#         self.curr_latency   = curr_latency
#         self.dropped        = dropped
#
#     def __str__(self):
#         return f' event_time={self.event_time} ' \
#                f'| sender_id={self.sender.id} ' \
#                f'| event_type={self.event_type} ' \
#                f'| next_hop_id={self.next_hop.id} ' \
#                f'| curr_latency={self.curr_latency} ' \
#                f'| dropped={self.dropped} '


class MyAuroraEnv(gym.Env, ABC):
    def __init__(self, range_bw: Tuple[float] = (MIN_BW, MAX_BW),
                 range_latency: Tuple[float] = (MIN_LATENCY, MAX_LATENCY),
                 range_queue: Tuple[float] = (MIN_QUEUE, MAX_QUEUE),
                 range_loss: Tuple[float] = (MIN_LOSS, MAX_LOSS),
                 num_senders: int = 2,
                 senders_starting_rate: Tuple[float] = (MIN_BW, MIN_BW),
                 range_send_rate: Tuple[float] = (MIN_SEND_RATE, MAX_SEND_RATE),
                 send_rate_scale: float = SEND_RATE_SCALE):
        super(MyAuroraEnv, self).__init__()

        assert num_senders == len(senders_starting_rate)

        self.range_bw               = range_bw
        self.range_latency          = range_latency
        self.range_queue            = range_queue
        self.range_loss             = range_loss
        self.num_senders            = num_senders
        self.num_links              = self.num_senders + 1
        self.senders_starting_rate  = senders_starting_rate
        self.range_send_rate        = range_send_rate
        self.send_rate_scale        = send_rate_scale

        logger.info(log_msg(f'| range_bw={self.range_bw} '
                            f'| range_latency={self.range_latency} '
                            f'| range_queue={self.range_queue} '
                            f'| range_loss={self.range_loss} '
                            f'| num_senders={self.num_senders} '
                            f'| senders_starting_rate={self.senders_starting_rate} '
                            f'| num_links={self.num_links} '
                            f'| send_rate_scale={self.send_rate_scale} '
                            f'| range_send_rate={self.range_send_rate} '))

        self.action_space = spaces.Box(np.tile(np.array([self.range_send_rate[0]]), self.num_senders),
                                       np.tile(np.array([self.range_send_rate[1]]), self.num_senders), dtype=np.float32)
        self.observation_space = spaces.Box(np.tile(np.array([-1.0, 1.0, 0.0]), self.num_senders),
                                            np.tile(np.array([10.0, 10000.0, 1000.0]), self.num_senders),
                                            dtype=np.float32)

        logger.info(log_msg(f'action_space: {str(self.action_space)}'))
        logger.info(log_msg(f'observation_space: {str(self.observation_space)}'))

        self.links      = []
        self.senders    = []
        self.q          = []

        self.cur_time   = 0.0

        max_link_latency = 0.0
        for i in range(self.num_links):
            link_bw         = random.uniform(*self.range_bw)
            link_latency    = random.uniform(*self.range_latency)
            if link_latency > max_link_latency:
                max_link_latency = link_latency
            link_queue      = int(random.uniform(*self.range_queue))
            link_loss       = random.uniform(*self.range_loss)
            self.links.append(Link(link_bw, link_latency, link_queue, link_loss))

        self.len_mi = 3 * max_link_latency
        logger.debug(f'MI length: {self.len_mi}[s]')

        for i in range(self.num_senders):
            self.senders.append(Sender(send_rate=self.senders_starting_rate[i],
                                       send_rate_scale=self.send_rate_scale,
                                       max_send_rate=self.range_send_rate[1],
                                       min_send_rate=self.range_send_rate[0],
                                       path=[self._get_link_with_id(id=i), self.links[-1]]))
        for sender in self.senders:
            logger.info(sender)

        # for sender in self.senders:
        #     self.q.append(Event(event_time=(1.0 / sender.curr_send_rate),
        #                         sender=sender,
        #                         event_type=EVENT_TYPE_SEND,
        #                         next_hop=sender.path[0],
        #                         curr_latency=0.0,
        #                         dropped=False))
        # for item in self.q:
        #     logger.info(log_msg(str(item)))

    def _get_link_with_id(self, id):
        for link in self.links:
            if link.id == id:
                return link

    def reset(self):

        max_link_latency = 0.0
        for link in self.links:
            link_bw         = random.uniform(*self.range_bw)
            link_latency    = random.uniform(*self.range_latency)
            if link_latency > max_link_latency:
                max_link_latency = link_latency
            link_queue      = int(random.uniform(*self.range_queue))
            link_loss       = random.uniform(*self.range_loss)
            link.reset(link_bw, link_latency, link_queue, link_loss)

        self.len_mi = 3 * max_link_latency
        logger.debug(f'MI length: {self.len_mi}[s]')

        for sender in self.senders:
            sender.reset()
        for sender in self.senders:
            logger.info(sender)

        self.cur_time = 0.0

    def step(self, action):

        for i, sender in enumerate(self.senders):
            sender.apply_rate_delta(action[i])
        for sender in self.senders:
            logger.info(sender)

        end_time = self.cur_time + self.len_mi
        while self.cur_time < end_time:




