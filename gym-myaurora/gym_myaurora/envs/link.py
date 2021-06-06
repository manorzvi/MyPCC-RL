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
from loguru import logger

from .common import log_msg


class Link:

    _next_id = 0

    def __init__(self, bw: float, latency: float, queue_size: int, loss_rate: float):
        self.bw = bw
        self.lat = latency
        self.q_size = queue_size
        self.lr = loss_rate
        self.id = self._get_next_id()

        self.queue_delay = 0.0
        self.queue_delay_update_time = 0.0
        self.max_queue_delay = queue_size / self.bw

        # logger.info(log_msg(f' bw={self.bw} '
        #                     f'| latency={self.lat} '
        #                     f'| queue_size={self.q_size} '
        #                     f'| loss_rate={self.lr} '
        #                     f'| link_id={self.id} '))

    @staticmethod
    def _get_next_id():
        result = Link._next_id
        Link._next_id += 1
        return result

    def __str__(self):
        return f' bw={self.bw} ' \
               f'| latency={self.lat} ' \
               f'| queue_size={self.q_size} ' \
               f'| loss_rate={self.lr} ' \
               f'| link_id={self.id} '

    def reset(self, bw: float, latency: float, queue_size: int, loss_rate: float):
        self.bw = bw
        self.lat = latency
        self.q_size = queue_size
        self.lr = loss_rate
        self.queue_delay = 0.0
        self.queue_delay_update_time = 0.0
        self.max_queue_delay = queue_size / self.bw

    # def get_cur_queue_delay(self, event_time):
    #     return max(0.0, self.queue_delay - (event_time - self.queue_delay_update_time))
    #
    # def get_cur_latency(self, event_time):
    #     return self.dl + self.get_cur_queue_delay(event_time)
    #
    # def packet_enters_link(self, event_time):
    #     if (random.random() < self.lr):
    #         return False
    #     self.queue_delay = self.get_cur_queue_delay(event_time)
    #     self.queue_delay_update_time = event_time
    #     extra_delay = 1.0 / self.bw
    #     # print("Extra delay: %f, Current delay: %f, Max delay: %f" % (extra_delay, self.queue_delay, self.max_queue_delay))
    #     if extra_delay + self.queue_delay > self.max_queue_delay:
    #         # print("\tDrop!")
    #         return False
    #     self.queue_delay += extra_delay
    #     # print("\tNew delay = %f" % self.queue_delay)
    #     return True
    #
    # def print_debug(self):
    #     print("Link:")
    #     print("Bandwidth: %f" % self.bw)
    #     print("Delay: %f" % self.dl)
    #     print("Queue Delay: %f" % self.queue_delay)
    #     print("Max Queue Delay: %f" % self.max_queue_delay)
    #     print("One Packet Queue Delay: %f" % (1.0 / self.bw))
    #
    # def reset(self):
    #     self.queue_delay = 0.0
    #     self.queue_delay_update_time = 0.0
